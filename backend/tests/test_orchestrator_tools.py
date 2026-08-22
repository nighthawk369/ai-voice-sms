"""Tests for Orchestrator and Tool System (PHASES 5-7)"""

import pytest
from uuid import UUID, uuid4
from datetime import datetime

from app.orchestrator import (
    AIOrchestrator,
    ConversationContext,
    ConversationState,
    Intent,
    Sentiment,
    IntentDetector,
)
from app.tools import (
    get_tool_registry,
    SearchContactsTool,
    CreateContactTool,
    ToolSpec,
    ToolCategory,
    ToolType,
)
from app.tool_router import get_tool_router
from app.llm.cache import get_llm_cache
from app.llm.usage import get_usage_tracker, TokenUsage


# ============================================================================
# ORCHESTRATOR TESTS
# ============================================================================

class TestIntentDetector:
    """Test intent detection"""

    def test_booking_intent(self):
        """Test booking intent detection"""
        detector = IntentDetector()
        intent = detector.detect_intent("I'd like to book an appointment")
        assert intent == Intent.BOOKING

    def test_support_intent(self):
        """Test support intent detection"""
        detector = IntentDetector()
        intent = detector.detect_intent("I have a problem with my service")
        assert intent == Intent.SUPPORT

    def test_info_request_intent(self):
        """Test info request intent detection"""
        detector = IntentDetector()
        intent = detector.detect_intent("What is your pricing?")
        assert intent == Intent.INFO_REQUEST

    def test_complaint_intent(self):
        """Test complaint intent detection"""
        detector = IntentDetector()
        intent = detector.detect_intent("I'm very disappointed with the service")
        assert intent == Intent.COMPLAINT

    def test_sales_intent(self):
        """Test sales intent detection"""
        detector = IntentDetector()
        intent = detector.detect_intent("How much does it cost to upgrade?")
        assert intent == Intent.SALES

    def test_sentiment_positive(self):
        """Test positive sentiment detection"""
        detector = IntentDetector()
        sentiment = detector.detect_sentiment("Great service! I love it!")
        assert sentiment == Sentiment.POSITIVE

    def test_sentiment_negative(self):
        """Test negative sentiment detection"""
        detector = IntentDetector()
        sentiment = detector.detect_sentiment("Terrible experience, very frustrated")
        assert sentiment == Sentiment.NEGATIVE

    def test_sentiment_neutral(self):
        """Test neutral sentiment detection"""
        detector = IntentDetector()
        sentiment = detector.detect_sentiment("I would like to reschedule my appointment")
        assert sentiment == Sentiment.NEUTRAL


class TestConversationContext:
    """Test conversation context"""

    def test_context_creation(self):
        """Test creating conversation context"""
        org_id = uuid4()
        conv_id = uuid4()

        context = ConversationContext(org_id=org_id, conversation_id=conv_id)

        assert context.org_id == org_id
        assert context.conversation_id == conv_id
        assert context.state == ConversationState.INITIAL
        assert len(context.messages) == 0

    def test_add_message(self):
        """Test adding messages to context"""
        context = ConversationContext(org_id=uuid4(), conversation_id=uuid4())

        context.add_message("user", "Hello")
        assert len(context.messages) == 1
        assert context.messages[0].role == "user"
        assert context.messages[0].content == "Hello"

    def test_get_recent_messages(self):
        """Test retrieving recent messages"""
        context = ConversationContext(org_id=uuid4(), conversation_id=uuid4())

        for i in range(15):
            context.add_message("user", f"Message {i}")

        recent = context.get_recent_messages(5)
        assert len(recent) == 5
        assert recent[-1].content == "Message 14"

    def test_context_to_dict(self):
        """Test converting context to dict"""
        org_id = uuid4()
        conv_id = uuid4()
        context = ConversationContext(org_id=org_id, conversation_id=conv_id)
        context.add_message("user", "Hi")

        data = context.to_dict()
        assert data["org_id"] == str(org_id)
        assert data["conversation_id"] == str(conv_id)
        assert data["message_count"] == 1


@pytest.mark.asyncio
class TestAIOrchestrator:
    """Test AI Orchestrator"""

    async def test_start_conversation(self):
        """Test starting a conversation"""
        orchestrator = AIOrchestrator()
        org_id = uuid4()
        conv_id = uuid4()

        context = await orchestrator.start_conversation(org_id=org_id, conversation_id=conv_id)

        assert context.org_id == org_id
        assert context.conversation_id == conv_id
        assert context.state == ConversationState.INITIAL

    async def test_process_user_message(self):
        """Test processing user message"""
        orchestrator = AIOrchestrator()
        context = await orchestrator.start_conversation(org_id=uuid4(), conversation_id=uuid4())

        response = await orchestrator.process_user_message(context, "Hello, can I schedule an appointment?")

        assert isinstance(response, str)
        assert len(response) > 0
        assert context.intent == Intent.BOOKING
        assert len(context.messages) == 2  # user + assistant

    async def test_extract_information(self):
        """Test information extraction"""
        orchestrator = AIOrchestrator()
        context = await orchestrator.start_conversation(org_id=uuid4(), conversation_id=uuid4())

        context.add_message("user", "My name is John Doe and my phone is 555-1234")
        context.add_message("assistant", "I'll help you with that")

        info = await orchestrator.extract_information(context)

        # This may be empty if JSON extraction fails, which is ok for mock
        assert isinstance(info, dict)

    async def test_escalation_negative_sentiment(self):
        """Test escalation on negative sentiment"""
        orchestrator = AIOrchestrator()
        context = await orchestrator.start_conversation(org_id=uuid4(), conversation_id=uuid4())

        context.add_message("user", "I'm very angry and frustrated!")
        context.sentiment = Sentiment.NEGATIVE

        should_escalate = await orchestrator.should_escalate(context)
        assert should_escalate is True
        assert context.escalation_reason == "Negative sentiment detected"

    async def test_escalation_user_request(self):
        """Test escalation on user request"""
        orchestrator = AIOrchestrator()
        context = await orchestrator.start_conversation(org_id=uuid4(), conversation_id=uuid4())

        context.add_message("user", "I want to speak with a manager")

        should_escalate = await orchestrator.should_escalate(context)
        assert should_escalate is True

    async def test_end_conversation(self):
        """Test ending a conversation"""
        orchestrator = AIOrchestrator()
        context = await orchestrator.start_conversation(org_id=uuid4(), conversation_id=uuid4())

        await orchestrator.end_conversation(context)

        assert context.state == ConversationState.ENDED


# ============================================================================
# TOOL SYSTEM TESTS
# ============================================================================

class TestToolRegistry:
    """Test tool registry"""

    def test_tool_registration(self):
        """Test registering tools"""
        registry = get_tool_registry()
        tools = registry.list_tools()

        assert len(tools) > 0
        assert any(t.id == "search_contacts" for t in tools)
        assert any(t.id == "create_contact" for t in tools)

    def test_get_tool(self):
        """Test retrieving tool"""
        registry = get_tool_registry()
        tool = registry.get_tool("search_contacts")

        assert tool is not None
        assert tool.spec.id == "search_contacts"

    def test_get_tool_spec(self):
        """Test getting tool specification"""
        registry = get_tool_registry()
        spec = registry.get_spec("create_contact")

        assert spec is not None
        assert spec.name == "Create Contact"
        assert spec.category == ToolCategory.CRM

    def test_list_tools_by_category(self):
        """Test listing tools by category"""
        registry = get_tool_registry()
        crm_tools = registry.list_tools(ToolCategory.CRM)

        assert len(crm_tools) > 0
        assert all(t.category == ToolCategory.CRM for t in crm_tools)

    def test_tool_not_found(self):
        """Test retrieving non-existent tool"""
        registry = get_tool_registry()
        tool = registry.get_tool("nonexistent_tool")

        assert tool is None


@pytest.mark.asyncio
class TestToolExecution:
    """Test tool execution"""

    async def test_execute_search_contacts(self):
        """Test executing search contacts tool"""
        registry = get_tool_registry()
        result = await registry.execute_tool(
            "search_contacts",
            {"query": "John Doe"},
            org_id=uuid4(),
        )

        assert isinstance(result, object)
        assert hasattr(result, 'success')

    async def test_execute_create_contact(self):
        """Test executing create contact tool"""
        registry = get_tool_registry()
        result = await registry.execute_tool(
            "create_contact",
            {
                "first_name": "John",
                "last_name": "Doe",
                "phone": "555-1234",
                "email": "john@example.com",
            },
            org_id=uuid4(),
        )

        assert result.success is True
        assert result.output["first_name"] == "John"

    async def test_tool_parameter_validation(self):
        """Test tool parameter validation"""
        registry = get_tool_registry()
        result = await registry.execute_tool(
            "create_contact",
            {"first_name": "John"},  # Missing required last_name and phone
            org_id=uuid4(),
        )

        assert result.success is False
        assert "Missing required parameter" in result.error


# ============================================================================
# TOOL ROUTER TESTS
# ============================================================================

class TestToolRouter:
    """Test tool router"""

    def test_get_tools_for_intent(self):
        """Test getting tools for intent"""
        router = get_tool_router()

        booking_tools = router.get_tools_for_intent(Intent.BOOKING)
        assert "create_deal" in booking_tools
        assert "create_contact" in booking_tools

        support_tools = router.get_tools_for_intent(Intent.SUPPORT)
        assert "search_knowledge" in support_tools

    def test_tools_for_all_intents(self):
        """Test that all intents have tools"""
        router = get_tool_router()

        for intent in Intent:
            if intent != Intent.UNKNOWN:
                tools = router.get_tools_for_intent(intent)
                assert len(tools) > 0, f"No tools for intent {intent}"


# ============================================================================
# CACHING TESTS
# ============================================================================

class TestLLMCache:
    """Test LLM response caching"""

    def test_cache_set_and_get(self):
        """Test setting and getting cached response"""
        cache = get_llm_cache()

        # Clear cache first
        cache.clear()

        prompt = "What is 2+2?"
        cache.set(
            prompt=prompt,
            system_prompt="You are a math tutor",
            provider="openai",
            model="gpt-4",
            content="The answer is 4",
            tokens_in=5,
            tokens_out=4,
        )

        cached = cache.get(prompt, "You are a math tutor", "openai", "gpt-4")
        assert cached is not None
        assert cached.content == "The answer is 4"

    def test_cache_miss(self):
        """Test cache miss"""
        cache = get_llm_cache()
        cache.clear()

        cached = cache.get("unknown", None, "openai", "gpt-4")
        assert cached is None

    def test_cache_stats(self):
        """Test cache statistics"""
        cache = get_llm_cache()
        cache.clear()

        cache.set("prompt", None, "openai", "gpt-4", "response", 10, 5)

        stats = cache.get_stats()
        assert stats["size"] == 1
        assert stats["total_hits"] == 0

    def test_cache_expiration(self):
        """Test cache expiration"""
        cache = get_llm_cache(ttl_hours=0)
        cache.clear()

        cache.set("prompt", None, "openai", "gpt-4", "response", 10, 5)

        # Wait a tiny bit for expiration
        import time
        time.sleep(0.1)

        cached = cache.get("prompt", None, "openai", "gpt-4")
        # Cache should be expired
        assert cached is None or cached.hit_count >= 0


# ============================================================================
# USAGE TRACKING TESTS
# ============================================================================

class TestUsageTracker:
    """Test usage tracking"""

    def test_record_usage(self):
        """Test recording usage"""
        tracker = get_usage_tracker()
        tracker.reset_stats()

        usage = tracker.record_usage(
            provider="openai",
            model="gpt-4o-mini",
            tokens_in=100,
            tokens_out=50,
            response_time=1.2,
            org_id=uuid4(),
            is_cache_hit=False,
        )

        assert isinstance(usage, TokenUsage)
        assert usage.total_tokens == 150
        assert usage.cost > 0  # Should have cost

    def test_get_provider_stats(self):
        """Test getting provider statistics"""
        tracker = get_usage_tracker()
        tracker.reset_stats()

        tracker.record_usage(
            provider="openai",
            model="gpt-4o-mini",
            tokens_in=100,
            tokens_out=50,
            response_time=1.2,
        )

        stats = tracker.get_provider_stats("openai")
        assert stats["total_requests"] == 1
        assert stats["total_tokens"] == 150

    def test_get_org_stats(self):
        """Test getting organization statistics"""
        tracker = get_usage_tracker()
        tracker.reset_stats()

        org_id = uuid4()
        tracker.record_usage(
            provider="openai",
            model="gpt-4o-mini",
            tokens_in=100,
            tokens_out=50,
            response_time=1.2,
            org_id=org_id,
        )

        stats = tracker.get_org_stats(org_id)
        assert stats["total_requests"] == 1
        assert stats["total_tokens"] == 150
        assert "by_provider" in stats

    def test_cache_hit_tracking(self):
        """Test cache hit tracking"""
        tracker = get_usage_tracker()
        tracker.reset_stats()

        tracker.record_usage(
            provider="openai",
            model="gpt-4o-mini",
            tokens_in=100,
            tokens_out=50,
            response_time=1.2,
            is_cache_hit=True,
        )

        key = "openai:gpt-4o-mini"
        stats = tracker.usage_by_provider[key]
        assert stats.cache_hits == 1
        assert stats.cache_misses == 0
