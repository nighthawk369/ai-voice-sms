"""Billing Engine - Stripe Integration and Subscription Management"""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from uuid import UUID, uuid4
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models import (
    BillingAccount, Invoice, InvoiceLineItem, Organization,
    UsageMetric, Deal
)

logger = logging.getLogger(__name__)

# Stripe integration - import only if STRIPE_API_KEY is available
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
if STRIPE_API_KEY:
    import stripe
    stripe.api_key = STRIPE_API_KEY


class SubscriptionTier:
    """Subscription tier definitions"""

    TIERS = {
        "STARTER": {
            "name": "Starter",
            "price": 99,
            "currency": "USD",
            "billing_cycle": "MONTHLY",
            "features": {
                "max_contacts": 1000,
                "max_calls_per_month": 500,
                "max_users": 3,
                "workflows": True,
                "analytics": True,
                "crm_integrations": 2,
                "custom_fields": 5,
            },
            "stripe_product_id": "prod_starter"
        },
        "PROFESSIONAL": {
            "name": "Professional",
            "price": 299,
            "currency": "USD",
            "billing_cycle": "MONTHLY",
            "features": {
                "max_contacts": 10000,
                "max_calls_per_month": 5000,
                "max_users": 10,
                "workflows": True,
                "analytics": True,
                "crm_integrations": 10,
                "custom_fields": 50,
            },
            "stripe_product_id": "prod_professional"
        },
        "ENTERPRISE": {
            "name": "Enterprise",
            "price": None,  # Custom pricing
            "currency": "USD",
            "billing_cycle": "ANNUAL",
            "features": {
                "max_contacts": None,  # Unlimited
                "max_calls_per_month": None,  # Unlimited
                "max_users": None,  # Unlimited
                "workflows": True,
                "analytics": True,
                "crm_integrations": None,  # Unlimited
                "custom_fields": None,  # Unlimited
            },
            "stripe_product_id": "prod_enterprise"
        }
    }

    @staticmethod
    def get_tier(tier_name: str) -> Dict[str, Any]:
        """Get tier configuration"""
        return SubscriptionTier.TIERS.get(tier_name, SubscriptionTier.TIERS["STARTER"])


class BillingManager:
    """Manages billing and subscriptions"""

    @staticmethod
    def create_billing_account(
        db: Session,
        organization_id: UUID,
        billing_email: str,
        billing_name: str,
        tier: str = "STARTER"
    ) -> BillingAccount:
        """Create billing account"""
        try:
            now = datetime.utcnow()
            period_start = now
            period_end = now + timedelta(days=30)

            account = BillingAccount(
                id=uuid4(),
                organization_id=organization_id,
                billing_email=billing_email,
                billing_name=billing_name,
                subscription_tier=tier,
                current_period_start=period_start,
                current_period_end=period_end,
                next_billing_date=period_end,
                status="ACTIVE"
            )

            db.add(account)
            db.commit()

            logger.info(f"Created billing account for org {organization_id}")
            return account

        except Exception as e:
            logger.error(f"Failed to create billing account: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def create_stripe_customer(
        organization: Organization,
        billing_account: BillingAccount
    ) -> Optional[str]:
        """Create Stripe customer"""
        if not STRIPE_API_KEY:
            logger.warning("Stripe API key not configured")
            return None

        try:
            customer = stripe.Customer.create(
                email=billing_account.billing_email,
                name=billing_account.billing_name,
                metadata={
                    "organization_id": str(organization.id),
                    "organization_name": organization.name
                }
            )

            logger.info(f"Created Stripe customer {customer.id} for org {organization.id}")
            return customer.id

        except Exception as e:
            logger.error(f"Failed to create Stripe customer: {str(e)}")
            return None

    @staticmethod
    def create_subscription(
        db: Session,
        billing_account: BillingAccount,
        tier: str = "STARTER"
    ) -> Optional[str]:
        """Create subscription in Stripe"""
        if not billing_account.stripe_customer_id:
            logger.warning("No Stripe customer ID")
            return None

        if not STRIPE_API_KEY:
            logger.warning("Stripe API key not configured")
            return None

        try:
            tier_config = SubscriptionTier.get_tier(tier)

            if tier_config["price"] is None:
                logger.warning(f"Tier {tier} has custom pricing, cannot auto-create subscription")
                return None

            subscription = stripe.Subscription.create(
                customer=billing_account.stripe_customer_id,
                items=[{
                    "price_data": {
                        "currency": tier_config["currency"].lower(),
                        "product": tier_config["stripe_product_id"],
                        "unit_amount": int(tier_config["price"] * 100),  # Convert to cents
                        "recurring": {
                            "interval": "month",
                            "interval_count": 1
                        }
                    }
                }]
            )

            billing_account.stripe_subscription_id = subscription.id
            db.commit()

            logger.info(f"Created Stripe subscription {subscription.id}")
            return subscription.id

        except Exception as e:
            logger.error(f"Failed to create subscription: {str(e)}")
            return None

    @staticmethod
    def generate_invoice(
        db: Session,
        billing_account: BillingAccount,
        usage_items: List[Dict[str, Any]],
        subscription_amount: Optional[Decimal] = None
    ) -> Invoice:
        """Generate invoice from usage and subscription"""
        try:
            organization = billing_account.organization
            now = datetime.utcnow()
            period_end = now + timedelta(days=30)

            # Create invoice
            invoice = Invoice(
                id=uuid4(),
                billing_account_id=billing_account.id,
                organization_id=billing_account.organization_id,
                invoice_number=BillingManager._generate_invoice_number(db, organization.id),
                status="DRAFT",
                invoice_date=now,
                due_date=now + timedelta(days=30),
                period_start=billing_account.current_period_start,
                period_end=billing_account.current_period_end,
                currency="USD"
            )

            subtotal = Decimal(0)

            # Add subscription line item
            if subscription_amount:
                tier_config = SubscriptionTier.get_tier(billing_account.subscription_tier)
                line_item = InvoiceLineItem(
                    id=uuid4(),
                    invoice_id=invoice.id,
                    billing_account_id=billing_account.id,
                    description=f"{tier_config['name']} Plan - Monthly",
                    quantity=Decimal(1),
                    unit_price=Decimal(str(subscription_amount)),
                    amount=Decimal(str(subscription_amount)),
                    metadata={"type": "subscription"}
                )
                db.add(line_item)
                subtotal += Decimal(str(subscription_amount))

            # Add usage line items
            for item in usage_items:
                line_item = InvoiceLineItem(
                    id=uuid4(),
                    invoice_id=invoice.id,
                    billing_account_id=billing_account.id,
                    description=item.get("description", "Usage"),
                    quantity=Decimal(str(item.get("quantity", 0))),
                    unit_price=Decimal(str(item.get("unit_price", 0))),
                    amount=Decimal(str(item.get("amount", 0))),
                    metadata=item.get("metadata", {})
                )
                db.add(line_item)
                subtotal += Decimal(str(item.get("amount", 0)))

            # Calculate tax (10% for demo)
            tax_rate = Decimal("0.10")
            tax_amount = (subtotal * tax_rate).quantize(Decimal("0.01"))

            invoice.subtotal = subtotal
            invoice.tax_amount = tax_amount
            invoice.total_amount = subtotal + tax_amount

            db.add(invoice)
            db.commit()

            logger.info(f"Generated invoice {invoice.invoice_number}")
            return invoice

        except Exception as e:
            logger.error(f"Failed to generate invoice: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def send_invoice(
        invoice: Invoice
    ) -> bool:
        """Send invoice to customer"""
        try:
            # TODO: Integrate with email service
            logger.info(f"Sending invoice {invoice.invoice_number} to {invoice.billing_account.billing_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send invoice: {str(e)}")
            return False

    @staticmethod
    def process_payment(
        db: Session,
        invoice: Invoice,
        payment_method_id: Optional[str] = None
    ) -> bool:
        """Process payment for invoice"""
        if not STRIPE_API_KEY:
            logger.warning("Stripe API key not configured")
            return False

        try:
            if not invoice.billing_account.stripe_customer_id:
                logger.warning("No Stripe customer ID")
                return False

            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=int(float(invoice.total_amount) * 100),  # Convert to cents
                currency="usd",
                customer=invoice.billing_account.stripe_customer_id,
                off_session=True,
                confirm=True,
                payment_method=payment_method_id
            )

            if payment_intent.status == "succeeded":
                invoice.status = "PAID"
                invoice.paid_at = datetime.utcnow()
                db.commit()

                logger.info(f"Payment processed for invoice {invoice.invoice_number}")
                return True
            else:
                logger.warning(f"Payment failed: {payment_intent.status}")
                return False

        except Exception as e:
            logger.error(f"Failed to process payment: {str(e)}")
            return False

    @staticmethod
    def upgrade_subscription(
        db: Session,
        billing_account: BillingAccount,
        new_tier: str
    ) -> bool:
        """Upgrade subscription tier"""
        try:
            old_tier = billing_account.subscription_tier
            billing_account.subscription_tier = new_tier
            billing_account.updated_at = datetime.utcnow()

            # TODO: Handle prorated charges in Stripe if subscription exists

            db.commit()
            logger.info(f"Upgraded {billing_account.id} from {old_tier} to {new_tier}")
            return True

        except Exception as e:
            logger.error(f"Failed to upgrade subscription: {str(e)}")
            db.rollback()
            return False

    @staticmethod
    def cancel_subscription(
        db: Session,
        billing_account: BillingAccount
    ) -> bool:
        """Cancel subscription"""
        if not STRIPE_API_KEY or not billing_account.stripe_subscription_id:
            logger.warning("Cannot cancel subscription")
            return False

        try:
            stripe.Subscription.delete(billing_account.stripe_subscription_id)

            billing_account.status = "CANCELLED"
            billing_account.auto_renew = False
            billing_account.updated_at = datetime.utcnow()
            db.commit()

            logger.info(f"Cancelled subscription for {billing_account.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to cancel subscription: {str(e)}")
            return False

    @staticmethod
    def renew_subscription(
        db: Session,
        billing_account: BillingAccount
    ) -> bool:
        """Renew subscription at period end"""
        try:
            now = datetime.utcnow()
            period_start = billing_account.current_period_end
            period_end = period_start + timedelta(days=30)

            billing_account.current_period_start = period_start
            billing_account.current_period_end = period_end
            billing_account.next_billing_date = period_end
            billing_account.status = "ACTIVE"
            billing_account.updated_at = now

            db.commit()
            logger.info(f"Renewed subscription for {billing_account.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to renew subscription: {str(e)}")
            db.rollback()
            return False

    @staticmethod
    def _generate_invoice_number(db: Session, organization_id: UUID) -> str:
        """Generate unique invoice number"""
        today = datetime.utcnow().date()
        count = db.query(func.count(Invoice.id)).filter(
            and_(
                Invoice.organization_id == organization_id,
                Invoice.invoice_date >= datetime.combine(today, datetime.min.time())
            )
        ).scalar() or 0

        return f"INV-{today.strftime('%Y%m%d')}-{count + 1:04d}"


class UsageBillingCalculator:
    """Calculates usage-based billing"""

    @staticmethod
    def calculate_monthly_usage_charges(
        db: Session,
        billing_account: BillingAccount
    ) -> List[Dict[str, Any]]:
        """Calculate usage-based charges for the month"""
        try:
            usage_items = []

            # Get usage metrics for current period
            metrics = db.query(UsageMetric).filter(
                and_(
                    UsageMetric.organization_id == billing_account.organization_id,
                    UsageMetric.created_at.between(
                        billing_account.current_period_start,
                        billing_account.current_period_end
                    )
                )
            ).all()

            usage_by_type = {}
            for metric in metrics:
                if metric.metric_type not in usage_by_type:
                    usage_by_type[metric.metric_type] = {
                        "quantity": 0,
                        "cost": Decimal(0)
                    }
                usage_by_type[metric.metric_type]["quantity"] += metric.quantity
                usage_by_type[metric.metric_type]["cost"] += metric.total_cost

            # Convert to line items
            for metric_type, usage in usage_by_type.items():
                usage_items.append({
                    "description": f"{metric_type.replace('_', ' ').title()} ({usage['quantity']})",
                    "quantity": usage["quantity"],
                    "unit_price": Decimal("0"),
                    "amount": usage["cost"],
                    "metadata": {"metric_type": metric_type}
                })

            return usage_items

        except Exception as e:
            logger.error(f"Failed to calculate usage charges: {str(e)}")
            return []
