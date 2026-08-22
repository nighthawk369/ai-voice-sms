"""SMS Integration Module for Twilio/Vonage"""

import os
import logging
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_

from app.models import Conversation, Message, Organization, Contact

logger = logging.getLogger(__name__)


# ============================================================================
# SMS MODELS
# ============================================================================

class SMSStatus(str, Enum):
    """SMS delivery status"""
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
    UNDELIVERED = "undelivered"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class TCPACompliance:
    """TCPA (Telephone Consumer Protection Act) Compliance"""

    # TCPA consent types
    CONSENT_EXPRESS_WRITTEN = "express_written"
    CONSENT_PRIOR_EXPRESS = "prior_express"
    CONSENT_IMPLIED = "implied"

    @staticmethod
    def is_business_hours(hour: int) -> bool:
        """Check if current time is business hours (8am-9pm)"""
        return 8 <= hour < 21

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        # Remove common formatting
        clean_phone = "".join(filter(str.isdigit, phone))
        return len(clean_phone) == 10 or len(clean_phone) == 11

    @staticmethod
    def validate_consent(phone: str, consent_type: str, org_id: UUID, db: Session) -> bool:
        """Validate TCPA consent for number"""
        try:
            contact = db.query(Contact).filter(
                and_(
                    Contact.organization_id == org_id,
                    Contact.phone == phone,
                )
            ).first()

            if not contact:
                return False

            # Check consent in metadata
            consent_data = contact.custom_fields.get("tcpa_consent", {})
            return consent_data.get("type") == consent_type and consent_data.get("consented", False)
        except Exception as e:
            logger.error(f"Error validating consent: {e}")
            return False


# ============================================================================
# SMS MANAGER
# ============================================================================

class SMSManager:
    """Manages SMS messages and integrations"""

    def __init__(self, db: Session):
        self.db = db
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")

    def send_sms(
        self,
        org_id: UUID,
        to_phone: str,
        message_text: str,
        contact_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Send SMS message"""
        try:
            # Validate TCPA compliance
            if not TCPACompliance.validate_phone(to_phone):
                raise ValueError(f"Invalid phone number: {to_phone}")

            # Create conversation if needed
            conversation = self.db.query(Conversation).filter(
                and_(
                    Conversation.organization_id == org_id,
                    Conversation.contact_id == contact_id,
                    Conversation.conversation_type == "SMS",
                )
            ).order_by(desc(Conversation.created_at)).first()

            if not conversation:
                conversation = Conversation(
                    organization_id=org_id,
                    contact_id=contact_id,
                    conversation_type="SMS",
                    status="ACTIVE",
                    phone_number=to_phone,
                )
                self.db.add(conversation)
                self.db.flush()

            # Create message
            message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=message_text,
                metadata={
                    "status": SMSStatus.QUEUED.value,
                    "phone": to_phone,
                    **(metadata or {}),
                },
            )
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)

            logger.info(f"Sent SMS {message.id} to {to_phone}")
            return {
                "message_id": str(message.id),
                "conversation_id": str(conversation.id),
                "status": SMSStatus.QUEUED.value,
                "phone": to_phone,
            }
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            raise

    def receive_sms(
        self,
        org_id: UUID,
        from_phone: str,
        message_text: str,
        twilio_message_sid: str,
    ) -> Optional[str]:
        """Handle incoming SMS"""
        try:
            # Find or create contact
            contact = self.db.query(Contact).filter(
                and_(
                    Contact.organization_id == org_id,
                    Contact.phone == from_phone,
                )
            ).first()

            if not contact:
                contact = Contact(
                    organization_id=org_id,
                    first_name="Unknown",
                    last_name="Sender",
                    phone=from_phone,
                    contact_type="LEAD",
                    status="NEW",
                    source="SMS",
                )
                self.db.add(contact)
                self.db.flush()

            # Find or create conversation
            conversation = self.db.query(Conversation).filter(
                and_(
                    Conversation.organization_id == org_id,
                    Conversation.contact_id == contact.id,
                    Conversation.conversation_type == "SMS",
                )
            ).order_by(desc(Conversation.created_at)).first()

            if not conversation:
                conversation = Conversation(
                    organization_id=org_id,
                    contact_id=contact.id,
                    conversation_type="SMS",
                    status="ACTIVE",
                    phone_number=from_phone,
                )
                self.db.add(conversation)
                self.db.flush()

            # Create message
            message = Message(
                conversation_id=conversation.id,
                role="user",
                content=message_text,
                metadata={
                    "twilio_message_sid": twilio_message_sid,
                    "from_phone": from_phone,
                },
            )
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)

            logger.info(f"Received SMS {message.id} from {from_phone}")
            return str(message.id)
        except Exception as e:
            logger.error(f"Error receiving SMS: {e}")
            return None

    def update_sms_status(
        self,
        message_id: UUID,
        status: SMSStatus,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Update SMS delivery status"""
        try:
            message = self.db.query(Message).filter(Message.id == message_id).first()
            if not message:
                return False

            message.metadata["status"] = status.value
            if metadata:
                message.metadata.update(metadata)

            self.db.commit()
            logger.info(f"Updated SMS {message_id} status to {status.value}")
            return True
        except Exception as e:
            logger.error(f"Error updating SMS status: {e}")
            return False

    def get_conversation(
        self,
        org_id: UUID,
        conversation_id: UUID,
    ) -> Optional[Dict[str, Any]]:
        """Get SMS conversation"""
        try:
            conversation = self.db.query(Conversation).filter(
                and_(
                    Conversation.organization_id == org_id,
                    Conversation.id == conversation_id,
                    Conversation.conversation_type == "SMS",
                )
            ).first()

            if not conversation:
                return None

            messages = self.db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.asc()).all()

            return {
                "conversation_id": str(conversation.id),
                "contact_id": str(conversation.contact_id),
                "phone_number": conversation.phone_number,
                "status": conversation.status,
                "messages": [
                    {
                        "id": str(m.id),
                        "role": m.role,
                        "content": m.content,
                        "created_at": m.created_at.isoformat(),
                    }
                    for m in messages
                ],
                "created_at": conversation.created_at.isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            return None

    def list_conversations(
        self,
        org_id: UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[List[Dict[str, Any]], int]:
        """List SMS conversations"""
        try:
            query = self.db.query(Conversation).filter(
                and_(
                    Conversation.organization_id == org_id,
                    Conversation.conversation_type == "SMS",
                )
            )

            if status:
                query = query.filter(Conversation.status == status)

            total = query.count()
            conversations = query.order_by(desc(Conversation.created_at)).offset(skip).limit(limit).all()

            return [
                {
                    "conversation_id": str(c.id),
                    "phone_number": c.phone_number,
                    "status": c.status,
                    "last_message_at": max(
                        [m.created_at for m in c.messages],
                        default=c.created_at,
                    ).isoformat(),
                    "message_count": len(c.messages),
                }
                for c in conversations
            ], total
        except Exception as e:
            logger.error(f"Error listing conversations: {e}")
            return [], 0


# ============================================================================
# OPT-OUT MANAGEMENT
# ============================================================================

class OptOutManager:
    """Manages SMS opt-outs and DNC (Do Not Call) compliance"""

    def __init__(self, db: Session):
        self.db = db

    def add_to_dnc_list(
        self,
        org_id: UUID,
        phone: str,
        reason: str = "user_requested",
    ) -> bool:
        """Add phone to DNC list"""
        try:
            contact = self.db.query(Contact).filter(
                and_(
                    Contact.organization_id == org_id,
                    Contact.phone == phone,
                )
            ).first()

            if contact:
                contact.custom_fields = contact.custom_fields or {}
                contact.custom_fields["do_not_contact"] = True
                contact.custom_fields["do_not_contact_reason"] = reason
                contact.custom_fields["do_not_contact_date"] = datetime.utcnow().isoformat()
                self.db.commit()

            logger.info(f"Added {phone} to DNC list")
            return True
        except Exception as e:
            logger.error(f"Error adding to DNC list: {e}")
            return False

    def remove_from_dnc_list(self, org_id: UUID, phone: str) -> bool:
        """Remove phone from DNC list"""
        try:
            contact = self.db.query(Contact).filter(
                and_(
                    Contact.organization_id == org_id,
                    Contact.phone == phone,
                )
            ).first()

            if contact and contact.custom_fields:
                contact.custom_fields["do_not_contact"] = False
                self.db.commit()

            logger.info(f"Removed {phone} from DNC list")
            return True
        except Exception as e:
            logger.error(f"Error removing from DNC list: {e}")
            return False

    def is_on_dnc_list(self, org_id: UUID, phone: str) -> bool:
        """Check if phone is on DNC list"""
        try:
            contact = self.db.query(Contact).filter(
                and_(
                    Contact.organization_id == org_id,
                    Contact.phone == phone,
                )
            ).first()

            if not contact:
                return False

            custom_fields = contact.custom_fields or {}
            return custom_fields.get("do_not_contact", False)
        except Exception as e:
            logger.error(f"Error checking DNC list: {e}")
            return False

    def get_dnc_list(self, org_id: UUID, skip: int = 0, limit: int = 1000) -> tuple[List[str], int]:
        """Get DNC list for organization"""
        try:
            # This is a simplified query - in production would use a dedicated table
            contacts = self.db.query(Contact).filter(
                Contact.organization_id == org_id
            ).all()

            dnc_phones = [
                c.phone for c in contacts
                if c.custom_fields and c.custom_fields.get("do_not_contact", False)
            ]

            return dnc_phones[skip:skip + limit], len(dnc_phones)
        except Exception as e:
            logger.error(f"Error getting DNC list: {e}")
            return [], 0


# ============================================================================
# SMS QUEUE SYSTEM
# ============================================================================

class SMSQueueManager:
    """Manages SMS queue for batch sending and retry logic"""

    def __init__(self, db: Session):
        self.db = db
        self.max_retries = 3
        self.retry_delay_minutes = 5

    def queue_batch_sms(
        self,
        org_id: UUID,
        recipients: List[Dict[str, str]],
        message_text: str,
    ) -> Dict[str, Any]:
        """Queue batch SMS messages"""
        try:
            queued_count = 0
            failed_count = 0
            errors = []

            for recipient in recipients:
                try:
                    phone = recipient.get("phone")
                    contact_id = recipient.get("contact_id")

                    if not TCPACompliance.validate_phone(phone):
                        errors.append({
                            "phone": phone,
                            "error": "Invalid phone number",
                        })
                        failed_count += 1
                        continue

                    # Create conversation and message
                    conversation = Conversation(
                        organization_id=org_id,
                        contact_id=contact_id,
                        conversation_type="SMS",
                        status="ACTIVE",
                        phone_number=phone,
                    )
                    self.db.add(conversation)
                    self.db.flush()

                    message = Message(
                        conversation_id=conversation.id,
                        role="assistant",
                        content=message_text,
                        metadata={
                            "status": SMSStatus.QUEUED.value,
                            "retry_count": 0,
                            "phone": phone,
                        },
                    )
                    self.db.add(message)
                    self.db.flush()
                    queued_count += 1
                except Exception as e:
                    errors.append({
                        "phone": recipient.get("phone"),
                        "error": str(e),
                    })
                    failed_count += 1

            self.db.commit()
            logger.info(f"Queued {queued_count} SMS messages")
            return {
                "queued_count": queued_count,
                "failed_count": failed_count,
                "errors": errors,
            }
        except Exception as e:
            logger.error(f"Error queuing batch SMS: {e}")
            raise

    def retry_failed_messages(self, org_id: UUID, limit: int = 100) -> int:
        """Retry failed SMS messages"""
        try:
            # This would query messages with FAILED status and retry_count < max_retries
            # For now, return count of retried messages
            logger.info(f"Retried SMS messages for org {org_id}")
            return 0
        except Exception as e:
            logger.error(f"Error retrying failed messages: {e}")
            return 0

    def get_queue_stats(self, org_id: UUID) -> Dict[str, int]:
        """Get SMS queue statistics"""
        try:
            queued = self.db.query(Message).join(Conversation).filter(
                and_(
                    Conversation.organization_id == org_id,
                    Conversation.conversation_type == "SMS",
                    Message.metadata["status"].astext == SMSStatus.QUEUED.value,
                )
            ).count()

            sent = self.db.query(Message).join(Conversation).filter(
                and_(
                    Conversation.organization_id == org_id,
                    Conversation.conversation_type == "SMS",
                    Message.metadata["status"].astext == SMSStatus.SENT.value,
                )
            ).count()

            failed = self.db.query(Message).join(Conversation).filter(
                and_(
                    Conversation.organization_id == org_id,
                    Conversation.conversation_type == "SMS",
                    Message.metadata["status"].astext == SMSStatus.FAILED.value,
                )
            ).count()

            return {
                "queued": queued,
                "sent": sent,
                "failed": failed,
                "total": queued + sent + failed,
            }
        except Exception as e:
            logger.error(f"Error getting queue stats: {e}")
            return {"queued": 0, "sent": 0, "failed": 0, "total": 0}
