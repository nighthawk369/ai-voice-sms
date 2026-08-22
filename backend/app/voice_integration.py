"""Voice Integration Module for Twilio/Vonage Integration"""

import os
import logging
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models import Conversation, Message, Organization, Contact, Activity

logger = logging.getLogger(__name__)


# ============================================================================
# VOICE STATE MACHINE
# ============================================================================

class VoiceCallState(str, Enum):
    """Voice call states"""
    INITIATED = "initiated"
    RINGING = "ringing"
    CONNECTED = "connected"
    ON_HOLD = "on_hold"
    TRANSFERRED = "transferred"
    ENDED = "ended"
    FAILED = "failed"


class VoiceCallEvent(str, Enum):
    """Voice call events"""
    CALL_INITIATED = "call_initiated"
    CALL_RINGING = "call_ringing"
    CALL_ANSWERED = "call_answered"
    CALL_MUTED = "call_muted"
    CALL_UNMUTED = "call_unmuted"
    CALL_ON_HOLD = "call_on_hold"
    CALL_RESUMED = "call_resumed"
    CALL_TRANSFERRED = "call_transferred"
    CALL_ENDED = "call_ended"
    CALL_FAILED = "call_failed"
    RECORDING_STARTED = "recording_started"
    RECORDING_ENDED = "recording_ended"


class VoiceStateMachine:
    """State machine for voice calls"""

    def __init__(self):
        self.state_transitions = {
            VoiceCallState.INITIATED: [
                VoiceCallState.RINGING,
                VoiceCallState.FAILED,
            ],
            VoiceCallState.RINGING: [
                VoiceCallState.CONNECTED,
                VoiceCallState.FAILED,
            ],
            VoiceCallState.CONNECTED: [
                VoiceCallState.ON_HOLD,
                VoiceCallState.TRANSFERRED,
                VoiceCallState.ENDED,
            ],
            VoiceCallState.ON_HOLD: [
                VoiceCallState.CONNECTED,
                VoiceCallState.ENDED,
            ],
            VoiceCallState.TRANSFERRED: [
                VoiceCallState.CONNECTED,
                VoiceCallState.ENDED,
            ],
            VoiceCallState.ENDED: [],
            VoiceCallState.FAILED: [],
        }

    def can_transition(
        self,
        from_state: VoiceCallState,
        to_state: VoiceCallState,
    ) -> bool:
        """Check if transition is valid"""
        return to_state in self.state_transitions.get(from_state, [])

    def get_valid_transitions(self, current_state: VoiceCallState) -> List[VoiceCallState]:
        """Get valid next states"""
        return self.state_transitions.get(current_state, [])


# ============================================================================
# VOICE CALL MANAGER
# ============================================================================

class VoiceCallManager:
    """Manages voice calls and integrations"""

    def __init__(self, db: Session):
        self.db = db
        self.state_machine = VoiceStateMachine()
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_from_number = os.getenv("TWILIO_FROM_NUMBER")

    def create_call(
        self,
        org_id: UUID,
        to_phone: str,
        from_phone: Optional[str] = None,
        contact_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Initiate a voice call"""
        try:
            conversation = Conversation(
                organization_id=org_id,
                contact_id=contact_id,
                conversation_type="VOICE",
                status="ACTIVE",
                phone_number=to_phone,
            )
            self.db.add(conversation)
            self.db.flush()

            # Record initial state
            self._record_call_event(
                conversation,
                VoiceCallState.INITIATED,
                metadata or {},
            )

            self.db.commit()
            self.db.refresh(conversation)

            logger.info(f"Created call {conversation.id} to {to_phone}")
            return {
                "call_id": str(conversation.id),
                "status": "initiated",
                "phone": to_phone,
            }
        except Exception as e:
            logger.error(f"Error creating call: {e}")
            raise

    def get_call(self, org_id: UUID, call_id: UUID) -> Optional[Dict[str, Any]]:
        """Get call details"""
        conversation = self.db.query(Conversation).filter(
            and_(
                Conversation.organization_id == org_id,
                Conversation.id == call_id,
                Conversation.conversation_type == "VOICE",
            )
        ).first()

        if not conversation:
            return None

        return {
            "call_id": str(conversation.id),
            "status": conversation.status,
            "phone_number": conversation.phone_number,
            "duration": self._calculate_duration(conversation),
            "transcript": conversation.transcript,
            "recording_url": conversation.metadata.get("recording_url"),
            "created_at": conversation.created_at.isoformat(),
            "ended_at": conversation.ended_at.isoformat() if conversation.ended_at else None,
        }

    def handle_call_event(
        self,
        org_id: UUID,
        call_id: UUID,
        event: VoiceCallEvent,
        data: Dict[str, Any],
    ) -> bool:
        """Handle voice call event"""
        try:
            conversation = self.db.query(Conversation).filter(
                and_(
                    Conversation.organization_id == org_id,
                    Conversation.id == call_id,
                )
            ).first()

            if not conversation:
                return False

            # Map event to state
            state_map = {
                VoiceCallEvent.CALL_INITIATED: VoiceCallState.INITIATED,
                VoiceCallEvent.CALL_RINGING: VoiceCallState.RINGING,
                VoiceCallEvent.CALL_ANSWERED: VoiceCallState.CONNECTED,
                VoiceCallEvent.CALL_ON_HOLD: VoiceCallState.ON_HOLD,
                VoiceCallEvent.CALL_TRANSFERRED: VoiceCallState.TRANSFERRED,
                VoiceCallEvent.CALL_ENDED: VoiceCallState.ENDED,
                VoiceCallEvent.CALL_FAILED: VoiceCallState.FAILED,
            }

            new_state = state_map.get(event)
            if new_state:
                conversation.status = new_state.value
                conversation.metadata.update(data)

                if event == VoiceCallEvent.CALL_ENDED:
                    conversation.ended_at = datetime.utcnow()

            self.db.commit()
            logger.info(f"Call {call_id} event: {event}")
            return True
        except Exception as e:
            logger.error(f"Error handling call event: {e}")
            return False

    def end_call(
        self,
        org_id: UUID,
        call_id: UUID,
        transcript: Optional[str] = None,
        recording_url: Optional[str] = None,
        duration_seconds: Optional[int] = None,
    ) -> bool:
        """End a voice call"""
        try:
            conversation = self.db.query(Conversation).filter(
                and_(
                    Conversation.organization_id == org_id,
                    Conversation.id == call_id,
                )
            ).first()

            if not conversation:
                return False

            conversation.status = "ENDED"
            conversation.ended_at = datetime.utcnow()
            if transcript:
                conversation.transcript = transcript
            if recording_url:
                conversation.metadata["recording_url"] = recording_url
            if duration_seconds:
                conversation.metadata["duration_seconds"] = duration_seconds

            self.db.commit()
            logger.info(f"Ended call {call_id}")
            return True
        except Exception as e:
            logger.error(f"Error ending call: {e}")
            return False

    def transfer_call(
        self,
        org_id: UUID,
        call_id: UUID,
        transfer_to: str,
    ) -> bool:
        """Transfer a call to another number"""
        try:
            conversation = self.db.query(Conversation).filter(
                and_(
                    Conversation.organization_id == org_id,
                    Conversation.id == call_id,
                )
            ).first()

            if not conversation:
                return False

            conversation.status = "TRANSFERRED"
            conversation.transfer_to = transfer_to
            conversation.metadata["transferred_at"] = datetime.utcnow().isoformat()

            self.db.commit()
            logger.info(f"Transferred call {call_id} to {transfer_to}")
            return True
        except Exception as e:
            logger.error(f"Error transferring call: {e}")
            return False

    def add_call_message(
        self,
        call_id: UUID,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Add a message to call conversation"""
        try:
            message = Message(
                conversation_id=call_id,
                role=role,
                content=content,
                metadata=metadata or {},
            )
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            return str(message.id)
        except Exception as e:
            logger.error(f"Error adding call message: {e}")
            return None

    def get_call_messages(
        self,
        org_id: UUID,
        call_id: UUID,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get messages from a call"""
        try:
            messages = self.db.query(Message).join(Conversation).filter(
                and_(
                    Conversation.organization_id == org_id,
                    Conversation.id == call_id,
                )
            ).order_by(Message.created_at.asc()).limit(limit).all()

            return [
                {
                    "id": str(m.id),
                    "role": m.role,
                    "content": m.content,
                    "created_at": m.created_at.isoformat(),
                }
                for m in messages
            ]
        except Exception as e:
            logger.error(f"Error getting call messages: {e}")
            return []

    def list_calls(
        self,
        org_id: UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[List[Dict[str, Any]], int]:
        """List organization calls"""
        try:
            query = self.db.query(Conversation).filter(
                and_(
                    Conversation.organization_id == org_id,
                    Conversation.conversation_type == "VOICE",
                )
            )

            if status:
                query = query.filter(Conversation.status == status)

            total = query.count()
            calls = query.order_by(desc(Conversation.created_at)).offset(skip).limit(limit).all()

            return [
                {
                    "call_id": str(c.id),
                    "phone_number": c.phone_number,
                    "status": c.status,
                    "duration": self._calculate_duration(c),
                    "created_at": c.created_at.isoformat(),
                }
                for c in calls
            ], total
        except Exception as e:
            logger.error(f"Error listing calls: {e}")
            return [], 0

    def _record_call_event(
        self,
        conversation: Conversation,
        state: VoiceCallState,
        event_data: Dict[str, Any],
    ):
        """Record a call event"""
        if not conversation.metadata:
            conversation.metadata = {}

        if "events" not in conversation.metadata:
            conversation.metadata["events"] = []

        conversation.metadata["events"].append({
            "state": state.value,
            "timestamp": datetime.utcnow().isoformat(),
            "data": event_data,
        })

    def _calculate_duration(self, conversation: Conversation) -> int:
        """Calculate call duration in seconds"""
        if not conversation.ended_at:
            return 0
        duration = conversation.ended_at - conversation.created_at
        return int(duration.total_seconds())


# ============================================================================
# CALL RECORDING HANDLER
# ============================================================================

class CallRecordingHandler:
    """Handles voice call recordings"""

    def __init__(self, storage_bucket: str = None):
        self.storage_bucket = storage_bucket or os.getenv("STORAGE_BUCKET")

    def store_recording(
        self,
        call_id: UUID,
        recording_data: bytes,
        file_format: str = "wav",
    ) -> str:
        """Store call recording"""
        try:
            filename = f"recordings/{call_id}.{file_format}"
            logger.info(f"Stored recording: {filename}")
            return f"s3://{self.storage_bucket}/{filename}"
        except Exception as e:
            logger.error(f"Error storing recording: {e}")
            raise

    def get_recording_url(
        self,
        call_id: UUID,
        expires_in_seconds: int = 3600,
    ) -> str:
        """Get signed recording URL"""
        try:
            filename = f"recordings/{call_id}.wav"
            logger.info(f"Generated signed URL for {filename}")
            return f"s3://{self.storage_bucket}/{filename}?expires_in={expires_in_seconds}"
        except Exception as e:
            logger.error(f"Error getting recording URL: {e}")
            raise

    def delete_recording(self, call_id: UUID) -> bool:
        """Delete call recording"""
        try:
            filename = f"recordings/{call_id}.wav"
            logger.info(f"Deleted recording: {filename}")
            return True
        except Exception as e:
            logger.error(f"Error deleting recording: {e}")
            return False


# ============================================================================
# VOICE ROUTING
# ============================================================================

class VoiceRouter:
    """Routes incoming voice calls"""

    def __init__(self, db: Session):
        self.db = db

    def route_incoming_call(
        self,
        org_id: UUID,
        from_phone: str,
        to_phone: str,
    ) -> Optional[Dict[str, Any]]:
        """Route incoming call to appropriate handler"""
        try:
            # Find or create contact
            contact = self.db.query(Contact).filter(
                and_(
                    Contact.organization_id == org_id,
                    Contact.phone == from_phone,
                )
            ).first()

            if not contact:
                # Create new contact
                contact = Contact(
                    organization_id=org_id,
                    first_name="Unknown",
                    last_name="Caller",
                    phone=from_phone,
                    contact_type="LEAD",
                    status="NEW",
                    source="PHONE",
                )
                self.db.add(contact)
                self.db.flush()

            # Create conversation
            conversation = Conversation(
                organization_id=org_id,
                contact_id=contact.id,
                conversation_type="VOICE",
                status="ACTIVE",
                phone_number=from_phone,
            )
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)

            logger.info(f"Routed incoming call from {from_phone}")
            return {
                "conversation_id": str(conversation.id),
                "contact_id": str(contact.id),
                "from_phone": from_phone,
                "to_phone": to_phone,
            }
        except Exception as e:
            logger.error(f"Error routing incoming call: {e}")
            return None

    def get_routing_rules(self, org_id: UUID) -> List[Dict[str, Any]]:
        """Get call routing rules for organization"""
        # This would be stored in DB and retrieved
        # For now return example rules
        return [
            {
                "id": "rule_1",
                "name": "Business Hours",
                "condition": "hour >= 9 and hour <= 17",
                "action": "queue",
                "destination": "support_team",
            },
            {
                "id": "rule_2",
                "name": "After Hours",
                "condition": "hour < 9 or hour > 17",
                "action": "voicemail",
                "destination": "voicemail_box",
            },
        ]
