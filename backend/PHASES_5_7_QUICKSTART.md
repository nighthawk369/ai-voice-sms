# PHASES 5-7 Quick Start Guide

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file with:
```bash
# LLM Configuration
LLM_PROVIDER=openai
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Anthropic (Optional)
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Google (Optional)
GOOGLE_API_KEY=your-key-here
GOOGLE_MODEL=gemini-2.0-flash-exp

# Local LLM (Optional, for testing)
LOCAL_LLM_ENDPOINT=http://localhost:8000/v1
LOCAL_LLM_MODEL=mistral
```

### 3. Start Application
```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs for API documentation.

## Quick Examples

### Example 1: Basic Conversation

```python
from app.orchestrator import AIOrchestrator
from uuid import uuid4

# Initialize orchestrator
orchestrator = AIOrchestrator()

# Start conversation
context = await orchestrator.start_conversation(
    org_id=uuid4(),
    conversation_id=uuid4(),
)

# Process user message
response = await orchestrator.process_user_message(
    context,
    "I'd like to book an appointment for next Tuesday"
)

print(f"AI: {response}")
print(f"Detected Intent: {context.intent}")
print(f"Sentiment: {context.sentiment}")
```

### Example 2: Using Tools

```python
from app.tools import get_tool_registry
from uuid import uuid4

registry = get_tool_registry()

# Create a contact
result = await registry.execute_tool(
    tool_id="create_contact",
    params={
        "first_name": "John",
        "last_name": "Doe",
        "phone": "555-1234",
        "email": "john@example.com",
    },
    org_id=uuid4(),
)

if result.success:
    print(f"Contact created: {result.output}")
else:
    print(f"Error: {result.error}")
```

### Example 3: Streaming Responses

```python
from app.orchestrator import AIOrchestrator
from uuid import uuid4

orchestrator = AIOrchestrator()

context = await orchestrator.start_conversation(
    org_id=uuid4(),
    conversation_id=uuid4(),
)

# Stream response in real-time
async for chunk in orchestrator.stream_response(
    context,
    "Tell me about your services"
):
    print(chunk, end="", flush=True)
print()
```

### Example 4: Intent-Based Tool Routing

```python
from app.tool_router import get_tool_router
from app.orchestrator import AIOrchestrator, Intent
from uuid import uuid4

orchestrator = AIOrchestrator()
tool_router = get_tool_router()

# Start conversation
context = await orchestrator.start_conversation(
    org_id=uuid4(),
    conversation_id=uuid4(),
)

# Process message (automatically detects booking intent)
await orchestrator.process_user_message(
    context,
    "I want to book an appointment"
)

# Route to appropriate tools
if context.intent == Intent.BOOKING:
    success, result = await tool_router.route_and_execute(context)
    if success:
        print(f"Created deal: {result}")
```

### Example 5: Usage Analytics

```python
from app.llm.usage import get_usage_tracker
from uuid import uuid4

tracker = get_usage_tracker()

# Get organization statistics
org_id = uuid4()
stats = tracker.get_org_stats(org_id)

print(f"Total requests: {stats['total_requests']}")
print(f"Total tokens: {stats['total_tokens']}")
print(f"Total cost: ${stats['total_cost']}")

# Get provider stats
provider_stats = tracker.get_provider_stats("openai")
print(f"OpenAI requests: {provider_stats['total_requests']}")
```

### Example 6: Response Caching

```python
from app.llm.cache import get_llm_cache

cache = get_llm_cache()

# Check cache stats
stats = cache.get_stats()
print(f"Cache size: {stats['size']}")
print(f"Cache hits: {stats['total_hits']}")

# Clear cache if needed
cache.clear()
```

## REST API Examples

### Start Conversation
```bash
curl -X POST http://localhost:8000/api/v1/orchestrator/conversations/start \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_id": "123e4567-e89b-12d3-a456-426614174000"
  }'
```

### Send Message
```bash
curl -X POST http://localhost:8000/api/v1/orchestrator/conversations/conv-id/messages \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv-id",
    "message": "I want to book an appointment",
    "provider": "openai"
  }'
```

### Get Conversation Status
```bash
curl -X GET http://localhost:8000/api/v1/orchestrator/conversations/conv-id \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### List Available Tools
```bash
curl -X GET http://localhost:8000/api/v1/orchestrator/tools \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Execute Tool
```bash
curl -X POST http://localhost:8000/api/v1/orchestrator/tools/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_id": "create_contact",
    "params": {
      "first_name": "John",
      "last_name": "Doe",
      "phone": "555-1234"
    },
    "conversation_id": "conv-id"
  }'
```

### Get Usage Stats
```bash
curl -X GET http://localhost:8000/api/v1/orchestrator/usage/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### WebSocket Streaming
```bash
# Using websocat or similar tool
websocat ws://localhost:8000/api/v1/orchestrator/ws/conversations/conv-id

# Send message
{"message": "What services do you offer?"}

# Receive chunks in real-time
{"chunk": "We offer..."}
```

## Common Workflows

### Workflow 1: Customer Booking Request

```
1. User says: "I want to book an appointment"
   - Intent detected: BOOKING
   - Sentiment: NEUTRAL

2. AI responds: "I'd be happy to help you book. When would you like to come in?"

3. User says: "Next Tuesday at 2pm"
   - Extracted info: date=next Tuesday, time=2pm

4. Tool Router: Execute create_deal tool
   - Create deal with scheduling info
   - Link to contact

5. AI response: "Great! Your appointment is confirmed for Tuesday at 2pm."
```

### Workflow 2: Customer Support Issue

```
1. User says: "My service is not working!"
   - Intent detected: SUPPORT
   - Sentiment: NEGATIVE

2. AI responds: "I'm sorry to hear that. Let me help troubleshoot."

3. Tool Router: Execute search_knowledge tool
   - Find relevant troubleshooting articles

4. User still frustrated after 5 exchanges
   - Escalation triggered due to negative sentiment

5. Route to human agent
```

### Workflow 3: Information Request

```
1. User says: "What is your pricing?"
   - Intent detected: INFO_REQUEST
   - Sentiment: NEUTRAL

2. Tool Router: Execute search_knowledge tool
   - Find pricing information

3. AI response: "Our pricing plans start at..."

4. Response cached for similar future queries
```

## Debugging

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Cache Hit Rate
```python
from app.llm.cache import get_llm_cache

cache = get_llm_cache()
stats = cache.get_stats()
hit_rate = stats['total_hits'] / (stats['total_hits'] + stats['total_misses'])
print(f"Cache hit rate: {hit_rate:.2%}")
```

### Monitor Token Usage
```python
from app.llm.usage import get_usage_tracker

tracker = get_usage_tracker()
stats = tracker.get_provider_stats("openai")
print(f"Average tokens/request: {stats['average_tokens_per_request']}")
```

### View Conversation Messages
```python
context = await orchestrator.start_conversation(...)
await orchestrator.process_user_message(context, "Hello")

for msg in context.messages:
    print(f"{msg.role}: {msg.content}")
```

## Testing

### Run Unit Tests
```bash
pytest tests/test_orchestrator_tools.py -v
```

### Run Integration Tests
```bash
pytest tests/ -v -k "orchestrator"
```

### Test with Mock Provider
```python
from app.llm.router import get_llm_router

router = get_llm_router()
response = await router.generate(
    prompt="Hello",
    provider_name="mock"
)
print(response.content)
```

## Performance Tips

### 1. Enable Caching
```python
from app.llm.cache import get_llm_cache

cache = get_llm_cache(ttl_hours=24)
```

### 2. Use Local Model for Testing
```python
# In .env
LLM_PROVIDER=local
LOCAL_LLM_ENDPOINT=http://localhost:8000/v1
```

### 3. Monitor Token Usage
```python
tracker = get_usage_tracker()
stats = tracker.get_org_stats(org_id)
print(f"Cost so far: ${stats['total_cost']}")
```

### 4. Batch Tool Operations
Instead of single tool calls, batch them when possible.

### 5. Use Streaming for Long Responses
```python
async for chunk in orchestrator.stream_response(context, message):
    # Process chunks as they arrive
    pass
```

## Troubleshooting

### Issue: "OPENAI_API_KEY not set"
**Solution**: Add to `.env`:
```
OPENAI_API_KEY=sk-your-actual-key
```

### Issue: Slow responses
**Solution**: 
1. Check cache hit rate
2. Use cheaper model (gpt-4o-mini instead of gpt-4o)
3. Reduce max_tokens
4. Use local LLM for testing

### Issue: High costs
**Solution**:
1. Enable caching
2. Use Anthropic Claude (cheaper)
3. Use Google Gemini (very cheap)
4. Implement usage quotas

### Issue: Tool execution fails
**Solution**:
1. Check tool parameters
2. View audit logs
3. Ensure database is configured
4. Check authorization

## Advanced Configuration

### Custom Intent Mapping
```python
from app.tool_router import ToolRouter

router = ToolRouter()
# Modify INTENT_TOOL_MAP
router.INTENT_TOOL_MAP[Intent.CUSTOM] = ["custom_tool"]
```

### Custom Tool Creation
```python
from app.tools import CRMTool, ToolSpec, ToolParameter

class CustomTool(CRMTool):
    SPEC = ToolSpec(...)
    
    async def _execute_crm_operation(self, params):
        # Implement your logic
        pass

registry.register_tool(CustomTool())
```

### Provider Switching
```python
# Switch providers at runtime
response = await orchestrator.process_user_message(
    context,
    "Tell me a joke",
    provider="anthropic"  # Use Claude instead of OpenAI
)
```

## Resources

- Full Documentation: `PHASES_5_7_IMPLEMENTATION.md`
- API Reference: http://localhost:8000/docs
- Test Examples: `tests/test_orchestrator_tools.py`

