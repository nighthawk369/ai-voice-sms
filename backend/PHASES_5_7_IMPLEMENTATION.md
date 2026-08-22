# PHASES 5-7 Implementation Guide

## Overview

This document covers the implementation of PHASES 5, 6, and 7 of the AI Platform:
- **PHASE 5**: LLM Provider Abstraction & Token Management
- **PHASE 6**: AI Orchestrator with Conversation State Management
- **PHASE 7**: Tool System for AI-Driven Actions

## PHASE 5: LLM Provider Abstraction

### Completed Components

#### 1. Enhanced Provider Implementations
**File**: `app/llm/providers.py`

All providers now support:
- **OpenAI** (GPT-4o, GPT-4o-mini)
- **Anthropic** (Claude 3.5 Sonnet, Haiku)
- **Google** (Gemini 2.0 Flash)
- **Local** (vLLM, Ollama)

Features:
- Full HTTP API integration with streaming support
- Accurate token counting (OpenAI uses tiktoken)
- Health checks for API availability
- Error handling and fallback mechanisms

#### 2. Response Caching
**File**: `app/llm/cache.py`

- In-memory LLM response cache with TTL (default 24 hours)
- Cache key generation using SHA256 hashing
- Cache statistics and hit rate tracking
- LRU eviction when cache is full
- Configurable cache size and TTL

Usage:
```python
cache = get_llm_cache()
cached = cache.get(prompt, system_prompt, provider, model)
if cached:
    # Use cached response
    pass
else:
    # Generate and cache
    cache.set(prompt, system_prompt, provider, model, content, tokens_in, tokens_out)
```

#### 3. Usage Tracking & Analytics
**File**: `app/llm/usage.py`

Tracks:
- Token usage per request (input/output)
- Cost calculation based on current pricing
- Provider and model-specific metrics
- Organization-level usage aggregation
- Cache hit rates
- Average response times

Features:
- Real-time pricing calculation for all providers
- Organization isolation for multi-tenant support
- Aggregated statistics by provider and model
- Cache performance metrics

Usage:
```python
tracker = get_usage_tracker()
tracker.record_usage(
    provider="openai",
    model="gpt-4o",
    tokens_in=100,
    tokens_out=50,
    response_time=1.2,
    org_id=org_id,
    is_cache_hit=False
)
stats = tracker.get_provider_stats("openai")
org_stats = tracker.get_org_stats(org_id)
```

#### 4. Provider Router with Fallback
**File**: `app/llm/router.py` (enhanced)

- Automatic fallback to secondary providers
- Health checks before provider selection
- Graceful degradation to mock provider
- Provider selection by name or auto-selection

## PHASE 6: AI Orchestrator

### Completed Components

#### 1. Conversation State Machine
**File**: `app/orchestrator.py`

States:
- `INITIAL`: Conversation started
- `GATHERING_INFO`: Collecting customer information
- `PROCESSING`: Processing user input
- `WAITING_USER`: Awaiting next user message
- `READY_TO_ACT`: Ready to execute action
- `EXECUTING`: Performing action
- `ESCALATING`: Escalating to human agent
- `ENDED`: Conversation concluded

Features:
- Automatic state transitions based on intent and context
- Persistent conversation history
- Message metadata tracking

#### 2. Intent Detection
**File**: `app/orchestrator.py` - `IntentDetector` class

Detectable intents:
- `BOOKING`: Appointment/schedule requests
- `SUPPORT`: Technical support requests
- `INFO_REQUEST`: General information queries
- `COMPLAINT`: Customer complaints
- `SALES`: Purchase/upgrade inquiries
- `RESCHEDULE`: Rescheduling requests
- `CANCEL`: Cancellation requests

Features:
- Keyword-based intent matching
- Sentiment analysis (POSITIVE/NEUTRAL/NEGATIVE)
- Extensible for ML-based intent detection

#### 3. Conversation Context Management
**File**: `app/orchestrator.py` - `ConversationContext` class

Tracks:
- Complete message history
- Extracted information from conversation
- Current intent and sentiment
- Pending actions
- Escalation flags
- Conversation metadata

#### 4. Escalation Logic
**File**: `app/orchestrator.py` - `AIOrchestrator.should_escalate()`

Escalates to human agent when:
- Negative sentiment detected
- Conversation exceeds length threshold
- User explicitly requests human
- Intent is ambiguous or complex

#### 5. Response Generation with Caching
**File**: `app/orchestrator.py` - `AIOrchestrator.process_user_message()`

Features:
- Cache-aware response generation
- Streaming support for real-time responses
- Usage tracking integration
- Error handling and recovery

#### 6. Information Extraction
**File**: `app/orchestrator.py` - `AIOrchestrator.extract_information()`

Extracts structured data:
- Contact name, email, phone
- Service/product of interest
- Specific requests or problems
- Constraints or preferences

Returns JSON-formatted structured data.

## PHASE 7: Tool System

### Completed Components

#### 1. Tool Specifications
**File**: `app/tools.py`

Tool structure:
```python
@dataclass
class ToolSpec:
    id: str
    name: str
    description: str
    category: ToolCategory  # CRM, CALENDAR, COMMUNICATION, KNOWLEDGE, WORKFLOW
    tool_type: ToolType     # ACTION, QUERY, SEARCH
    parameters: List[ToolParameter]
    output_schema: Dict[str, Any]
    rate_limit: Optional[int]
    requires_auth: bool
    tags: List[str]
```

#### 2. Tool Execution Engine
**File**: `app/tools.py` - `Tool` abstract class and implementations

Base implementation with:
- Parameter validation
- Error handling
- Execution time tracking
- Result formatting

#### 3. CRM Tools
**File**: `app/tools.py`

Implemented tools:
- **SearchContactsTool**: Search contacts by name, email, or phone
- **CreateContactTool**: Create new contact in CRM
- **UpdateContactTool**: Update existing contact
- **CreateDealTool**: Create new sales opportunity

Example:
```python
result = await registry.execute_tool(
    "create_contact",
    {
        "first_name": "John",
        "last_name": "Doe",
        "phone": "555-1234",
        "email": "john@example.com"
    },
    org_id=org_id
)
```

#### 4. Knowledge Search Tool
**File**: `app/tools.py` - `SearchKnowledgeTool`

Features:
- Full-text search of knowledge base
- Relevance scoring
- Configurable result limits
- Category filtering (future enhancement)

#### 5. Tool Registry
**File**: `app/tools.py` - `ToolRegistry` class

Features:
- Tool registration and discovery
- Spec management
- Rate limit enforcement
- Tool lookup by ID or category

#### 6. Tool Router
**File**: `app/tool_router.py` - `ToolRouter` class

Features:
- Intent-based tool recommendation
- Automatic parameter extraction from conversation
- Tool execution orchestration
- Tool execution decision logic

Intent-to-Tool mapping:
```python
INTENT_TOOL_MAP = {
    Intent.BOOKING: ["create_deal", "create_contact", "search_contacts"],
    Intent.SUPPORT: ["search_knowledge", "create_contact"],
    Intent.INFO_REQUEST: ["search_knowledge"],
    Intent.COMPLAINT: ["create_contact", "create_deal"],
    Intent.SALES: ["create_deal", "search_contacts"],
    Intent.RESCHEDULE: ["create_deal", "search_contacts"],
    Intent.CANCEL: ["search_contacts"],
}
```

#### 7. Audit Logging
**File**: `app/tools.py` - `ToolAuditLog` class

Logs:
- Tool ID and execution timestamp
- Input parameters and output results
- Success/failure status
- Organization and user context
- Execution error details

#### 8. Rate Limiting
**File**: `app/tools.py` - `ToolRegistry.execute_tool()`

Features:
- Per-tool rate limit enforcement
- Configurable limits per tool
- Clear error messages on limit exceeded

Example configuration:
```python
SPEC = ToolSpec(
    id="search_contacts",
    # ... other fields ...
    rate_limit=10,  # 10 requests per minute
)
```

## Integration Points

### Orchestrator to Tool Router
```python
orchestrator = AIOrchestrator()
tool_router = get_tool_router()

# Process user message and detect intent
response = await orchestrator.process_user_message(context, user_input)

# Route to tools if action needed
if context.intent in [Intent.BOOKING, Intent.SALES]:
    success, result = await tool_router.route_and_execute(context)
```

### Database Integration (TODO)
- Store conversation histories in database
- Link conversations to contacts/deals
- Persist tool audit logs
- Track organization usage

## Configuration

### Environment Variables
```
# LLM Provider
LLM_PROVIDER=openai  # openai, anthropic, google, local
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Google
GOOGLE_API_KEY=...
GOOGLE_MODEL=gemini-2.0-flash-exp

# Local LLM
LOCAL_LLM_ENDPOINT=http://localhost:8000/v1
LOCAL_LLM_MODEL=mistral
```

## Usage Examples

### Basic Conversation Flow
```python
from app.orchestrator import AIOrchestrator
from app.tool_router import get_tool_router
from uuid import UUID

orchestrator = AIOrchestrator()
tool_router = get_tool_router()

# Start conversation
context = await orchestrator.start_conversation(
    org_id=UUID("..."),
    conversation_id=UUID("..."),
)

# Process user message
user_input = "I'd like to book an appointment"
response = await orchestrator.process_user_message(context, user_input)
print(response)  # AI response

# Intent detected: Intent.BOOKING
# Route to appropriate tools
if context.intent == Intent.BOOKING:
    success, result = await tool_router.route_and_execute(context)
    if success:
        print(f"Created deal: {result}")

# End conversation
await orchestrator.end_conversation(context)
```

### Streaming Responses
```python
# Stream response for real-time user experience
async for chunk in orchestrator.stream_response(context, user_input):
    print(chunk, end="", flush=True)
```

### Tool Direct Execution
```python
registry = get_tool_registry()

result = await registry.execute_tool(
    "search_contacts",
    {"query": "John Doe"},
    org_id=org_id,
    user_id=user_id,
)

if result.success:
    print(f"Found contacts: {result.output}")
else:
    print(f"Error: {result.error}")
```

### Usage Analytics
```python
tracker = get_usage_tracker()

# Get provider stats
stats = tracker.get_provider_stats("openai")
print(f"Total requests: {stats['total_requests']}")
print(f"Total cost: ${stats['total_cost']}")

# Get organization stats
org_stats = tracker.get_org_stats(org_id)
print(f"Org usage: {org_stats}")
```

## Testing

### Unit Tests
```bash
pytest tests/test_orchestrator.py
pytest tests/test_tools.py
pytest tests/test_llm_providers.py
```

### Integration Tests
```bash
pytest tests/test_orchestrator_integration.py
```

## Security Considerations

1. **API Key Management**: Use environment variables, never commit keys
2. **Rate Limiting**: Enforce rate limits on all tools
3. **Audit Logging**: Log all tool executions for compliance
4. **Input Validation**: Validate all tool parameters
5. **Escalation**: Route sensitive operations to human agents
6. **Data Privacy**: Ensure PII is handled securely

## Performance Optimization

1. **Response Caching**: Reduces API calls and latency
2. **Async Operations**: All I/O operations are async
3. **Streaming**: Support for streaming responses
4. **Token Counting**: Accurate token counting for cost control
5. **Provider Selection**: Intelligent fallback to lower-cost providers

## Future Enhancements

1. **Machine Learning Intent Detection**: Replace keyword matching with ML
2. **Custom Tools**: Allow organizations to create custom tools
3. **Tool Chaining**: Execute multiple tools in sequence
4. **Conditional Logic**: Complex decision trees based on context
5. **Workflow Automation**: Multi-step workflows with tools
6. **Real-time Analytics**: Dashboard for usage and performance metrics
7. **Cost Optimization**: Automatic provider switching based on cost/quality
8. **Fine-tuned Models**: Organization-specific model tuning

## Troubleshooting

### Provider Errors
- Check API keys in environment
- Verify API key permissions
- Check rate limits with provider
- Review error logs for details

### Cache Issues
- Clear cache if stale responses appear
- Check TTL configuration
- Monitor cache hit rates

### Tool Execution Failures
- Verify tool parameters are correct
- Check rate limits
- Review audit logs
- Validate database connectivity

## Dependencies

See `requirements.txt` for complete list. Key additions:
- `openai>=1.0.0`: OpenAI API
- `anthropic>=0.7.0`: Anthropic API
- `google-generativeai>=0.3.0`: Google Gemini API
- `tiktoken>=0.5.0`: Token counting
- `httpx>=0.24.0`: Async HTTP client

