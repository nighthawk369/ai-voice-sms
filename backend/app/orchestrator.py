"""AI Orchestrator for conversation management and intent detection"""

import logging
import json
from typing import List, Optional, Dict, Any, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID
import re

from app.llm.router import get_llm_router
from app.llm.cache import get_llm_cache
from app.llm.usage import get_usage_tracker, TokenUsage

logger = logging.getLogger(__name__)


class ConversationState(str, Enum):
    """Conversation state machine states"""
    INITIAL = "INITIAL"
    GATHERING_INFO = "GATHERING_INFO"
    PROCESSING = "PROCESSING"
    WAITING_USER = "WAITING_USER"
    READY_TO_ACT = "READY_TO_ACT"
    EXECUTING = "EXECUTING"
    ESCALATING = "ESCALATING"
    ENDED = "ENDED"


class Intent(str, Enum):
    """Detected conversation intents"""
    BOOKING = "BOOKING"
    SUPPORT = "SUPPORT"
    INFO_REQUEST = "INFO_REQUEST"
    COMPLAINT = "COMPLAINT"
    SALES = "SALES"
    RESCHEDULE = "RESCHEDULE"
    CANCEL = "CANCEL"
    UNKNOWN = "UNKNOWN"


class Sentiment(str, Enum):
    """Sentiment analysis results"""
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"


@dataclass
class ConversationMessage:
    """Single message in conversation"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class ConversationContext:
    """Context for current conversation"""
    org_id: UUID
    conversation_id: UUID
    contact_id: Optional[UUID] = None
    state: ConversationState = ConversationState.INITIAL
    intent: Intent = Intent.UNKNOWN
    sentiment: Sentiment = Sentiment.NEUTRAL
    messages: List[ConversationMessage] = field(default_factory=list)
    extracted_info: Dict[str, Any] = field(default_factory=dict)
    pending_actions: List[Dict[str, Any]] = field(default_factory=list)
    escalation_reason: Optional[str] = None
    transfer_to: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add message to conversation"""
        msg = ConversationMessage(role=role, content=content, metadata=metadata or {})
        self.messages.append(msg)
        self.last_activity = datetime.utcnow()

    def get_recent_messages(self, count: int = 10) -> List[ConversationMessage]:
        """Get recent messages"""
        return self.messages[-count:]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "org_id": str(self.org_id),
            "conversation_id": str(self.conversation_id),
            "contact_id": str(self.contact_id) if self.contact_id else None,
            "state": self.state.value,
            "intent": self.intent.value,
            "sentiment": self.sentiment.value,
            "message_count": len(self.messages),
            "extracted_info": self.extracted_info,
            "pending_actions": self.pending_actions,
            "created_at": self.created_at.isoformat(),
        }


class IntentDetector:
    """Detect user intent from conversation messages"""

    # Intent keywords mapping
    INTENT_KEYWORDS = {
        Intent.BOOKING: ["book", "appointment", "schedule", "reserve", "availability", "time", "date"],
        Intent.SUPPORT: ["help", "issue", "problem", "fix", "broken", "error", "support", "assist"],
        Intent.INFO_REQUEST: ["tell me", "what is", "how to", "information", "details", "explain", "know"],
        Intent.COMPLAINT: ["complaint", "unhappy", "disappointed", "poor", "bad", "angry", "frustrated"],
        Intent.SALES: ["price", "cost", "buy", "purchase", "upgrade", "plan", "subscription"],
        Intent.RESCHEDULE: ["change", "reschedule", "move", "postpone", "delay", "different time"],
        Intent.CANCEL: ["cancel", "remove", "delete", "stop", "unsubscribe", "terminate"],
    }

    def detect_intent(self, text: str) -> Intent:
        """Detect intent from text using keyword matching"""
        text_lower = text.lower()
        intent_scores = {intent: 0 for intent in Intent}

        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    intent_scores[intent] += 1

        # Return intent with highest score, or UNKNOWN
        max_intent = max(intent_scores, key=intent_scores.get)
        if intent_scores[max_intent] == 0:
            return Intent.UNKNOWN

        return max_intent

    def detect_sentiment(self, text: str) -> Sentiment:
        """Detect sentiment from text using keyword analysis"""
        text_lower = text.lower()

        positive_words = [
            "good", "great", "excellent", "amazing", "wonderful", "happy", "satisfied",
            "thank", "thanks", "appreciate", "love", "perfect", "awesome"
        ]
        negative_words = [
            "bad", "terrible", "awful", "horrible", "angry", "frustrated", "sad",
            "disappointed", "hate", "worst", "poor", "issue", "problem", "error"
        ]

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            return Sentiment.POSITIVE
        elif negative_count > positive_count:
            return Sentiment.NEGATIVE
        else:
            return Sentiment.NEUTRAL


class AIOrchestrator:
    """Main orchestrator for AI conversations"""

    SYSTEM_PROMPT = """You are a helpful AI assistant for a service business. Your role is to:
1. Understand customer needs and intents
2. Extract relevant information from conversations
3. Provide clear, helpful responses
4. Guide customers through their requests
5. Escalate to human agents when necessary

Be professional, empathetic, and concise. Ask clarifying questions when needed."""

    EXTRACTION_PROMPT = """Based on the conversation history, extract the following information:
- Contact name (if mentioned)
- Contact email (if mentioned)
- Contact phone (if mentioned)
- Service type or product of interest
- Specific requests or problems
- Any constraints or preferences

Format as JSON with these fields:
{{
  "name": "...",
  "email": "...",
  "phone": "...",
  "service": "...",
  "request": "...",
  "constraints": "..."
}}

Conversation:
{conversation}

Return only valid JSON."""

    def __init__(self):
        self.llm_router = get_llm_router()
        self.cache = get_llm_cache()
        self.usage_tracker = get_usage_tracker()
        self.intent_detector = IntentDetector()

    async def start_conversation(
        self,
        org_id: UUID,
        conversation_id: UUID,
        contact_id: Optional[UUID] = None,
    ) -> ConversationContext:
        """Initialize a new conversation"""
        context = ConversationContext(
            org_id=org_id,
            conversation_id=conversation_id,
            contact_id=contact_id,
        )
        context.state = ConversationState.INITIAL
        logger.info(f"Started conversation {conversation_id} for org {org_id}")
        return context

    async def process_user_message(
        self,
        context: ConversationContext,
        user_message: str,
        provider: Optional[str] = None,
    ) -> str:
        """Process user message and generate response"""
        # Add user message to context
        context.add_message("user", user_message)

        # Update state machine
        context.state = ConversationState.PROCESSING

        # Detect intent and sentiment
        context.intent = self.intent_detector.detect_intent(user_message)
        context.sentiment = self.intent_detector.detect_sentiment(user_message)

        logger.info(f"Detected intent: {context.intent}, sentiment: {context.sentiment}")

        # Check cache
        cached = self.cache.get(user_message, None, provider or "openai", "default")
        if cached:
            response = cached.content
            context.add_message("assistant", response, {"from_cache": True})
            self.usage_tracker.record_usage(
                provider=cached.provider,
                model=cached.model,
                tokens_in=cached.tokens_in,
                tokens_out=cached.tokens_out,
                response_time=0.0,
                org_id=context.org_id,
                is_cache_hit=True,
            )
            context.state = ConversationState.WAITING_USER
            return response

        # Prepare messages for LLM
        messages = []
        for msg in context.get_recent_messages(5):
            messages.append({"role": msg.role, "content": msg.content})

        # Generate response
        try:
            start_time = datetime.utcnow()
            response_obj = await self.llm_router.generate(
                prompt=user_message,
                system_prompt=self.SYSTEM_PROMPT,
                provider_name=provider,
            )
            elapsed = (datetime.utcnow() - start_time).total_seconds()

            # Cache response
            self.cache.set(
                user_message,
                self.SYSTEM_PROMPT,
                response_obj.provider,
                response_obj.model,
                response_obj.content,
                response_obj.tokens_in,
                response_obj.tokens_out,
            )

            # Track usage
            self.usage_tracker.record_usage(
                provider=response_obj.provider,
                model=response_obj.model,
                tokens_in=response_obj.tokens_in,
                tokens_out=response_obj.tokens_out,
                response_time=elapsed,
                org_id=context.org_id,
                is_cache_hit=False,
            )

            # Add response to context
            context.add_message("assistant", response_obj.content)

            # Update state
            if context.intent == Intent.BOOKING or context.intent == Intent.SALES:
                context.state = ConversationState.READY_TO_ACT
            else:
                context.state = ConversationState.WAITING_USER

            return response_obj.content

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            error_response = "I apologize, but I encountered an error. Please try again."
            context.add_message("assistant", error_response, {"error": str(e)})
            return error_response

    async def stream_response(
        self,
        context: ConversationContext,
        user_message: str,
        provider: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """Stream response for user message"""
        context.add_message("user", user_message)
        context.state = ConversationState.PROCESSING

        # Detect intent and sentiment
        context.intent = self.intent_detector.detect_intent(user_message)
        context.sentiment = self.intent_detector.detect_sentiment(user_message)

        try:
            provider_obj = await self.llm_router.get_provider(provider)
            full_response = ""

            async for chunk in provider_obj.stream(
                prompt=user_message,
                system_prompt=self.SYSTEM_PROMPT,
            ):
                full_response += chunk
                yield chunk

            # Track usage
            tokens_out = await provider_obj.count_tokens(full_response)
            tokens_in = await provider_obj.count_tokens(user_message)

            self.usage_tracker.record_usage(
                provider=provider_obj.__class__.__name__.replace("Provider", "").lower(),
                model="unknown",
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                response_time=0.0,
                org_id=context.org_id,
                is_cache_hit=False,
            )

            context.add_message("assistant", full_response)
            context.state = ConversationState.WAITING_USER

        except Exception as e:
            logger.error(f"Error streaming response: {e}")
            yield f"Error: {str(e)}"

    async def extract_information(self, context: ConversationContext) -> Dict[str, Any]:
        """Extract structured information from conversation"""
        conversation_text = "\n".join([
            f"{msg.role}: {msg.content}" for msg in context.get_recent_messages()
        ])

        prompt = self.EXTRACTION_PROMPT.format(conversation=conversation_text)

        try:
            response_obj = await self.llm_router.generate(prompt=prompt)
            content = response_obj.content

            # Try to extract JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                info = json.loads(json_match.group())
                context.extracted_info = info
                return info
            else:
                logger.warning("Could not extract JSON from response")
                return {}
        except Exception as e:
            logger.error(f"Error extracting information: {e}")
            return {}

    async def should_escalate(self, context: ConversationContext) -> bool:
        """Determine if conversation should be escalated to human agent"""
        # Escalate if negative sentiment
        if context.sentiment == Sentiment.NEGATIVE:
            context.escalation_reason = "Negative sentiment detected"
            return True

        # Escalate if too many unresolved exchanges
        if len(context.messages) > 20:
            context.escalation_reason = "Conversation too long without resolution"
            return True

        # Escalate if user requests it (keywords)
        if context.messages:
            last_message = context.messages[-1].content.lower()
            escalation_keywords = ["speak to agent", "human", "manager", "supervisor", "escalate"]
            if any(keyword in last_message for keyword in escalation_keywords):
                context.escalation_reason = "User requested escalation"
                return True

        return False

    async def end_conversation(self, context: ConversationContext) -> None:
        """End conversation and prepare for storage"""
        context.state = ConversationState.ENDED
        logger.info(f"Ended conversation {context.conversation_id}")
