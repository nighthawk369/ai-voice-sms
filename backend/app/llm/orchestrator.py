"""AI Orchestrator - Conversation state machine and intent detection"""

import json
import logging
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Conversation, Message
from app.llm.providers import LLMProviderFactory, LLMProviderType
from app.llm.cache import LLMCache

logger = logging.getLogger(__name__)


class ConversationState(str, Enum):
    """Conversation states in the state machine"""
    GREETING = "greeting"
    GATHERING_INFO = "gathering_info"
    PROCESSING_REQUEST = "processing_request"
    EXECUTING_ACTION = "executing_action"
    PROVIDING_RESULT = "providing_result"
    OFFERING_FOLLOWUP = "offering_followup"
    ESCALATING = "escalating"
    CLOSED = "closed"


class Intent(str, Enum):
    """Detected user intents"""
    BOOKING_APPOINTMENT = "booking_appointment"
    CHECKING_AVAILABILITY = "checking_availability"
    GETTING_INFORMATION = "getting_information"
    UPDATING_CONTACT = "updating_contact"
    CHECKING_STATUS = "checking_status"
    SCHEDULING_CALLBACK = "scheduling_callback"
    COMPLAINT = "complaint"
    OTHER = "other"


class AIOrchestrator:
    """Main AI orchestrator for managing conversations"""

    SYSTEM_PROMPT = """You are an AI assistant for a field service business (HVAC, Plumbing, Electrical).
Your role is to:
1. Greet customers warmly
2. Understand their service needs
3. Check availability and schedule appointments
4. Gather necessary information (name, address, contact)
5. Confirm details before booking
6. Offer follow-up services when appropriate
7. Escalate to human agent if needed

Be professional, friendly, and efficient. Keep responses concise for voice calls.
Always confirm information before taking action.
If you're unsure about something, ask clarifying questions.
Never make up information - if you don't know something, say so."""

    def __init__(
        self,
        db: AsyncSession,
        organization_id: UUID,
        provider_type: LLMProviderType = LLMProviderType.OPENAI,
        cache: Optional[LLMCache] = None
    ):
        self.db = db
        self.organization_id = organization_id
        self.provider = LLMProviderFactory.create(provider_type)
        self.cache = cache or LLMCache()
        self.state = ConversationState.GREETING
        self.detected_intent = Intent.OTHER
        self.context = {}

    async def process_message(
        self,
        conversation_id: UUID,
        user_message: str,
        contact_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Process user message and generate AI response"""
        try:
            # Load conversation history
            messages = await self._load_conversation_history(conversation_id)

            # Detect intent from user message
            self.detected_intent = await self._detect_intent(user_message, messages)

            # Update conversation state
            self.state = await self._update_state(self.detected_intent)

            # Build context for LLM
            context = await self._build_context(conversation_id, contact_id)

            # Generate AI response
            response = await self._generate_response(
                user_message=user_message,
                messages=messages,
                context=context
            )

            # Save message to database
            await self._save_message(conversation_id, "user", user_message)
            await self._save_message(conversation_id, "assistant", response["content"])

            # Update conversation metadata
            await self._update_conversation(
                conversation_id,
                intent=self.detected_intent,
                state=self.state
            )

            return {
                "response": response["content"],
                "intent": self.detected_intent.value,
                "state": self.state.value,
                "tokens_used": response["tokens_used"],
                "actions": await self._extract_actions(response["content"])
            }
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            raise

    async def _load_conversation_history(
        self,
        conversation_id: UUID,
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """Load recent messages from conversation"""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = result.scalars().all()
        return [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages)
        ]

    async def _detect_intent(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]]
    ) -> Intent:
        """Detect user intent from message"""
        detection_prompt = f"""Analyze this message and determine the user's intent.
Return ONLY the intent name from this list:
- booking_appointment
- checking_availability
- getting_information
- updating_contact
- checking_status
- scheduling_callback
- complaint
- other

Message: {user_message}

Intent:"""

        try:
            response = await self.provider.complete(
                messages=[{"role": "user", "content": detection_prompt}],
                max_tokens=50,
                temperature=0.3
            )

            intent_text = response.content.strip().lower()
            for intent in Intent:
                if intent.value in intent_text:
                    return intent
            return Intent.OTHER
        except Exception as e:
            logger.warning(f"Intent detection failed: {e}, defaulting to OTHER")
            return Intent.OTHER

    async def _update_state(self, intent: Intent) -> ConversationState:
        """Update conversation state based on intent"""
        if self.state == ConversationState.GREETING:
            return ConversationState.GATHERING_INFO
        elif intent == Intent.BOOKING_APPOINTMENT:
            return ConversationState.PROCESSING_REQUEST
        elif intent == Intent.COMPLAINT:
            return ConversationState.ESCALATING
        return ConversationState.PROVIDING_RESULT

    async def _build_context(
        self,
        conversation_id: UUID,
        contact_id: Optional[UUID]
    ) -> Dict[str, Any]:
        """Build context for LLM from database"""
        context = {
            "conversation_id": str(conversation_id),
            "timestamp": datetime.utcnow().isoformat(),
            "current_state": self.state.value,
            "detected_intent": self.detected_intent.value
        }

        if contact_id:
            # Load contact information
            from app.models import Contact
            result = await self.db.execute(
                select(Contact).where(Contact.id == contact_id)
            )
            contact = result.scalar_one_or_none()
            if contact:
                context["contact"] = {
                    "name": f"{contact.first_name} {contact.last_name}",
                    "phone": contact.phone,
                    "type": contact.contact_type,
                    "status": contact.status
                }

        return context

    async def _generate_response(
        self,
        user_message: str,
        messages: List[Dict[str, str]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI response using LLM"""
        # Check cache first
        cache_key = f"{self.organization_id}:{user_message[:100]}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Build messages for LLM
        system_msg = self._build_system_prompt(context)
        full_messages = messages + [{"role": "user", "content": user_message}]

        # Generate response
        response = await self.provider.complete(
            messages=full_messages,
            system_prompt=system_msg,
            temperature=0.7,
            max_tokens=500
        )

        result = {
            "content": response.content,
            "tokens_used": response.tokens_used
        }

        # Cache result
        self.cache.set(cache_key, result)

        return result

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt with context"""
        prompt = self.SYSTEM_PROMPT

        if "contact" in context:
            prompt += f"\n\nCurrent Customer:\n"
            prompt += f"Name: {context['contact']['name']}\n"
            prompt += f"Type: {context['contact']['type']}\n"
            prompt += f"Status: {context['contact']['status']}\n"

        prompt += f"\nCurrent Intent: {context['detected_intent']}\n"
        prompt += f"Current State: {context['current_state']}\n"

        return prompt

    async def _extract_actions(self, response_text: str) -> List[Dict[str, Any]]:
        """Extract actionable items from response"""
        # TODO: Implement action extraction (booking, reminders, etc.)
        return []

    async def _save_message(
        self,
        conversation_id: UUID,
        role: str,
        content: str
    ):
        """Save message to database"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        self.db.add(message)
        await self.db.commit()

    async def _update_conversation(
        self,
        conversation_id: UUID,
        intent: Intent,
        state: ConversationState
    ):
        """Update conversation record"""
        from app.models import Conversation
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if conversation:
            conversation.intent = intent.value
            conversation.status = state.value
            await self.db.commit()
