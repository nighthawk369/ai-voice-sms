"""Twilio Voice Integration - Inbound/outbound call handling"""

import logging
from typing import Optional, Dict, Any
from uuid import UUID
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Conversation, Activity
from app.llm.orchestrator import AIOrchestrator
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TwilioVoiceHandler:
    """Handle Twilio voice calls"""

    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.phone_number = settings.TWILIO_PHONE_NUMBER

    async def handle_inbound_call(
        self,
        call_sid: str,
        from_number: str,
        to_number: str,
        db: AsyncSession,
        organization_id: UUID
    ) -> VoiceResponse:
        """Handle inbound call from customer"""
        try:
            # Create conversation record
            conversation = Conversation(
                organization_id=organization_id,
                conversation_type="VOICE",
                phone_number=from_number,
                twilio_call_sid=call_sid,
                status="ACTIVE"
            )
            db.add(conversation)
            await db.commit()

            # Initialize orchestrator
            orchestrator = AIOrchestrator(db, organization_id)

            # Generate greeting
            greeting = "Hello! Welcome to our service. How can we help you today?"

            # Create TwiML response with gather
            response = VoiceResponse()
            response.say(greeting)
            response.gather(
                num_digits=1,
                action=f"/api/v1/voice/gather?call_sid={call_sid}",
                method="POST",
                timeout=10
            )

            return response

        except Exception as e:
            logger.error(f"Inbound call error: {e}")
            response = VoiceResponse()
            response.say("Sorry, something went wrong. Please try again later.")
            return response

    async def handle_voice_input(
        self,
        call_sid: str,
        digits: str,
        db: AsyncSession,
        organization_id: UUID
    ) -> VoiceResponse:
        """Handle voice input/DTMF during call"""
        try:
            # Get conversation
            result = await db.execute(
                select(Conversation).where(
                    Conversation.twilio_call_sid == call_sid
                )
            )
            conversation = result.scalar_one_or_none()

            if not conversation:
                response = VoiceResponse()
                response.say("Call not found.")
                return response

            # Process based on digit input
            if digits == "1":
                # Book appointment
                message = "I'd like to book an appointment"
            elif digits == "2":
                # Check status
                message = "I want to check the status of my appointment"
            else:
                # Get speech instead
                response = VoiceResponse()
                response.record(
                    action=f"/api/v1/voice/transcribe?call_sid={call_sid}",
                    method="POST",
                    timeout=10,
                    play_beep=True
                )
                return response

            # Use orchestrator to process
            orchestrator = AIOrchestrator(db, organization_id)
            result = await orchestrator.process_message(
                conversation_id=conversation.id,
                user_message=message,
                contact_id=conversation.contact_id
            )

            # Convert response to voice
            response = VoiceResponse()
            response.say(result["response"])
            response.gather(
                action=f"/api/v1/voice/gather?call_sid={call_sid}",
                method="POST",
                timeout=10
            )

            return response

        except Exception as e:
            logger.error(f"Voice input error: {e}")
            response = VoiceResponse()
            response.say("Error processing your request.")
            return response

    async def transcribe_call(
        self,
        call_sid: str,
        recording_url: str,
        db: AsyncSession,
        organization_id: UUID
    ) -> VoiceResponse:
        """Transcribe voice recording and process"""
        try:
            # Get conversation
            result = await db.execute(
                select(Conversation).where(
                    Conversation.twilio_call_sid == call_sid
                )
            )
            conversation = result.scalar_one_or_none()

            if not conversation:
                response = VoiceResponse()
                response.say("Call not found.")
                return response

            # In production, use Twilio's transcription service or external API
            # For now, just note the recording
            conversation.metadata = conversation.metadata or {}
            conversation.metadata["recording_url"] = recording_url

            await db.commit()

            # Provide response
            response = VoiceResponse()
            response.say("Thank you for your message. We'll get back to you soon.")
            response.hangup()

            return response

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            response = VoiceResponse()
            response.say("Error processing recording.")
            response.hangup()
            return response

    async def end_call(
        self,
        call_sid: str,
        db: AsyncSession,
        organization_id: UUID
    ):
        """End call and save metadata"""
        try:
            result = await db.execute(
                select(Conversation).where(
                    Conversation.twilio_call_sid == call_sid
                )
            )
            conversation = result.scalar_one_or_none()

            if conversation:
                conversation.status = "ENDED"
                conversation.ended_at = __import__('datetime').datetime.utcnow()
                await db.commit()

                # Create activity record
                activity = Activity(
                    organization_id=organization_id,
                    contact_id=conversation.contact_id,
                    activity_type="CALL",
                    title=f"Inbound Call from {conversation.phone_number}",
                    completed_at=__import__('datetime').datetime.utcnow(),
                    metadata={
                        "twilio_call_sid": call_sid,
                        "conversation_id": str(conversation.id)
                    }
                )
                db.add(activity)
                await db.commit()

        except Exception as e:
            logger.error(f"End call error: {e}")

    async def make_outbound_call(
        self,
        phone_number: str,
        message: str,
        db: AsyncSession,
        organization_id: UUID
    ) -> Dict[str, Any]:
        """Initiate outbound call"""
        try:
            call = self.client.calls.create(
                to=phone_number,
                from_=self.phone_number,
                url=f"{settings.API_BASE_URL}/api/v1/voice/outbound",
                method="POST"
            )

            # Create conversation record
            conversation = Conversation(
                organization_id=organization_id,
                conversation_type="VOICE",
                phone_number=phone_number,
                twilio_call_sid=call.sid,
                status="ACTIVE",
                metadata={"message": message, "type": "outbound"}
            )
            db.add(conversation)
            await db.commit()

            return {
                "call_sid": call.sid,
                "status": call.status,
                "conversation_id": str(conversation.id)
            }

        except Exception as e:
            logger.error(f"Outbound call error: {e}")
            raise

    async def send_sms(
        self,
        phone_number: str,
        message: str,
        db: AsyncSession,
        organization_id: UUID
    ) -> Dict[str, Any]:
        """Send SMS message via Twilio"""
        try:
            sms = self.client.messages.create(
                to=phone_number,
                from_=self.phone_number,
                body=message
            )

            # Create conversation record for SMS
            conversation = Conversation(
                organization_id=organization_id,
                conversation_type="SMS",
                phone_number=phone_number,
                status="ENDED",
                metadata={"message": message, "twilio_sid": sms.sid}
            )
            db.add(conversation)
            await db.commit()

            return {
                "sid": sms.sid,
                "status": sms.status,
                "conversation_id": str(conversation.id)
            }

        except Exception as e:
            logger.error(f"SMS error: {e}")
            raise
