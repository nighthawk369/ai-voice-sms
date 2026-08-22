"""Billing API Routes - Subscription management and invoicing"""

import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.db import get_db
from app.dependencies import get_current_user
from app.models import User, Organization, BillingAccount, Invoice
from app.billing_engine import BillingManager, SubscriptionTier, UsageBillingCalculator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])


# ============================================================================
# BILLING ACCOUNT ROUTES
# ============================================================================

@router.post("/account", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_billing_account(
    billing_email: str,
    billing_name: str,
    tier: str = "STARTER",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create billing account"""
    try:
        # Check if account already exists
        existing = db.query(BillingAccount).filter(
            BillingAccount.organization_id == current_user.organization_id
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Billing account already exists")

        account = BillingManager.create_billing_account(
            db,
            current_user.organization_id,
            billing_email,
            billing_name,
            tier
        )

        # Attempt to create Stripe customer
        org = db.query(Organization).filter(
            Organization.id == current_user.organization_id
        ).first()

        if org:
            stripe_customer_id = BillingManager.create_stripe_customer(org, account)
            if stripe_customer_id:
                account.stripe_customer_id = stripe_customer_id
                db.commit()

        return {
            "id": str(account.id),
            "organization_id": str(account.organization_id),
            "billing_email": account.billing_email,
            "subscription_tier": account.subscription_tier,
            "status": account.status,
            "current_period_start": account.current_period_start.isoformat(),
            "current_period_end": account.current_period_end.isoformat(),
            "created_at": account.created_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create billing account: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/account", response_model=dict)
async def get_billing_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get billing account"""
    try:
        account = db.query(BillingAccount).filter(
            BillingAccount.organization_id == current_user.organization_id
        ).first()

        if not account:
            raise HTTPException(status_code=404, detail="Billing account not found")

        tier_config = SubscriptionTier.get_tier(account.subscription_tier)

        return {
            "id": str(account.id),
            "organization_id": str(account.organization_id),
            "billing_email": account.billing_email,
            "billing_name": account.billing_name,
            "subscription_tier": account.subscription_tier,
            "tier_details": tier_config,
            "billing_cycle": account.billing_cycle,
            "status": account.status,
            "current_period_start": account.current_period_start.isoformat(),
            "current_period_end": account.current_period_end.isoformat(),
            "next_billing_date": account.next_billing_date.isoformat(),
            "auto_renew": account.auto_renew,
            "created_at": account.created_at.isoformat(),
            "updated_at": account.updated_at.isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get billing account: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SUBSCRIPTION MANAGEMENT ROUTES
# ============================================================================

@router.get("/subscriptions/tiers", response_model=dict)
async def get_subscription_tiers():
    """Get available subscription tiers"""
    return {
        "tiers": [
            {
                "id": tier_name,
                "name": config["name"],
                "price": config["price"],
                "currency": config["currency"],
                "features": config["features"]
            }
            for tier_name, config in SubscriptionTier.TIERS.items()
        ]
    }


@router.post("/subscriptions/upgrade", response_model=dict)
async def upgrade_subscription(
    new_tier: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upgrade subscription"""
    try:
        account = db.query(BillingAccount).filter(
            BillingAccount.organization_id == current_user.organization_id
        ).first()

        if not account:
            raise HTTPException(status_code=404, detail="Billing account not found")

        if new_tier not in SubscriptionTier.TIERS:
            raise HTTPException(status_code=400, detail="Invalid tier")

        success = BillingManager.upgrade_subscription(db, account, new_tier)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to upgrade subscription")

        return {
            "id": str(account.id),
            "subscription_tier": account.subscription_tier,
            "status": account.status,
            "message": f"Upgraded to {new_tier}"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upgrade subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscriptions/cancel", response_model=dict)
async def cancel_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel subscription"""
    try:
        account = db.query(BillingAccount).filter(
            BillingAccount.organization_id == current_user.organization_id
        ).first()

        if not account:
            raise HTTPException(status_code=404, detail="Billing account not found")

        success = BillingManager.cancel_subscription(db, account)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to cancel subscription")

        return {
            "id": str(account.id),
            "status": account.status,
            "message": "Subscription cancelled"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# INVOICE ROUTES
# ============================================================================

@router.get("/invoices", response_model=dict)
async def list_invoices(
    skip: int = 0,
    limit: int = 50,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List invoices"""
    try:
        query = db.query(Invoice).filter(
            Invoice.organization_id == current_user.organization_id
        )

        if status:
            query = query.filter(Invoice.status == status)

        invoices = query.order_by(
            Invoice.invoice_date.desc()
        ).offset(skip).limit(limit).all()

        total = query.count()

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "invoices": [
                {
                    "id": str(i.id),
                    "invoice_number": i.invoice_number,
                    "status": i.status,
                    "total_amount": float(i.total_amount),
                    "currency": i.currency,
                    "invoice_date": i.invoice_date.isoformat(),
                    "due_date": i.due_date.isoformat(),
                    "paid_at": i.paid_at.isoformat() if i.paid_at else None
                }
                for i in invoices
            ]
        }

    except Exception as e:
        logger.error(f"Failed to list invoices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invoices/{invoice_id}", response_model=dict)
async def get_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get invoice details"""
    try:
        invoice = db.query(Invoice).filter(
            and_(
                Invoice.id == UUID(invoice_id),
                Invoice.organization_id == current_user.organization_id
            )
        ).first()

        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        return {
            "id": str(invoice.id),
            "invoice_number": invoice.invoice_number,
            "status": invoice.status,
            "invoice_date": invoice.invoice_date.isoformat(),
            "due_date": invoice.due_date.isoformat(),
            "period_start": invoice.period_start.isoformat(),
            "period_end": invoice.period_end.isoformat(),
            "subtotal": float(invoice.subtotal),
            "tax_amount": float(invoice.tax_amount),
            "discount_amount": float(invoice.discount_amount),
            "total_amount": float(invoice.total_amount),
            "currency": invoice.currency,
            "paid_at": invoice.paid_at.isoformat() if invoice.paid_at else None,
            "line_items": [
                {
                    "description": li.description,
                    "quantity": float(li.quantity),
                    "unit_price": float(li.unit_price),
                    "amount": float(li.amount)
                }
                for li in invoice.line_items
            ]
        }

    except Exception as e:
        logger.error(f"Failed to get invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invoices/{invoice_id}/send", response_model=dict)
async def send_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send invoice to customer"""
    try:
        invoice = db.query(Invoice).filter(
            and_(
                Invoice.id == UUID(invoice_id),
                Invoice.organization_id == current_user.organization_id
            )
        ).first()

        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        success = BillingManager.send_invoice(invoice)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to send invoice")

        return {
            "invoice_number": invoice.invoice_number,
            "message": "Invoice sent successfully"
        }

    except Exception as e:
        logger.error(f"Failed to send invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PAYMENT ROUTES
# ============================================================================

@router.post("/payments/process", response_model=dict)
async def process_payment(
    invoice_id: str,
    payment_method_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process payment for invoice"""
    try:
        invoice = db.query(Invoice).filter(
            and_(
                Invoice.id == UUID(invoice_id),
                Invoice.organization_id == current_user.organization_id
            )
        ).first()

        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        success = BillingManager.process_payment(db, invoice, payment_method_id)

        if not success:
            raise HTTPException(status_code=500, detail="Payment processing failed")

        return {
            "invoice_number": invoice.invoice_number,
            "status": invoice.status,
            "paid_at": invoice.paid_at.isoformat() if invoice.paid_at else None,
            "message": "Payment processed successfully"
        }

    except Exception as e:
        logger.error(f"Failed to process payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# USAGE-BASED BILLING ROUTES
# ============================================================================

@router.post("/generate-invoice", response_model=dict)
async def generate_invoice(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate invoice for current period"""
    try:
        account = db.query(BillingAccount).filter(
            BillingAccount.organization_id == current_user.organization_id
        ).first()

        if not account:
            raise HTTPException(status_code=404, detail="Billing account not found")

        # Calculate usage charges
        usage_items = UsageBillingCalculator.calculate_monthly_usage_charges(db, account)

        # Get subscription amount
        tier_config = SubscriptionTier.get_tier(account.subscription_tier)
        subscription_amount = tier_config.get("price")

        # Generate invoice
        invoice = BillingManager.generate_invoice(
            db,
            account,
            usage_items,
            subscription_amount
        )

        return {
            "id": str(invoice.id),
            "invoice_number": invoice.invoice_number,
            "status": invoice.status,
            "total_amount": float(invoice.total_amount),
            "created_at": invoice.created_at.isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to generate invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
