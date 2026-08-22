"""Routes for orchestrator and AI conversation endpoints"""

import logging
from typing import Optional
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, WebSocket
from pydantic import BaseModel

from app.dependencies import get_current_user, get_current_org
from app.orchestrator import AIOrchestrator, ConversationContext, Intent, Sentiment
from app.tool_router import get_tool_router
from app.models import User, Organization

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/orchestrator", tags=["orchestrator"])

# Initialize orchestrator
orchestrator = AIOrchestrator()
tool_router = get_tool_router()


# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================

class ConversationStartRequest(BaseModel):
    """Start new conversation"""
    contact_id: Optional[UUID] = None


class ConversationStartResponse(BaseModel):
    """Conversation started"""
    conversation_id: UUID
    status: str


class MessageRequest(BaseModel):
    """User message to process"""
    conversation_id: UUID
    message: str
    provider: Optional[str] = None


class MessageResponse(BaseModel):
    """AI response"""
    message: str
    intent: str
    sentiment: str
    extracted_info: dict


class ConversationStatusResponse(BaseModel):
    """Conversation status"""
    conversation_id: UUID
    state: str
    intent: str
    sentiment: str
    message_count: int
    extracted_info: dict
    should_escalate: bool


class ToolExecutionRequest(BaseModel):
    """Request to execute tool"""
    tool_id: str
    params: dict
    conversation_id: Optional[UUID] = None


class ToolExecutionResponse(BaseModel):
    """Tool execution result"""
    success: bool
    tool_id: str
    output: dict
    error: Optional[str] = None


# ============================================================================
# CONVERSATION ENDPOINTS
# ============================================================================

# In-memory conversation storage (use database in production)
_conversations: dict[UUID, ConversationContext] = {}


@router.post("/conversations/start", response_model=ConversationStartResponse)
async def start_conversation(
    request: ConversationStartRequest,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_org),
) -> ConversationStartResponse:
    """Start a new conversation"""
    conversation_id = uuid4()

    context = await orchestrator.start_conversation(
        org_id=current_org.id,
        conversation_id=conversation_id,
        contact_id=request.contact_id,
    )

    _conversations[conversation_id] = context

    logger.info(f"Started conversation {conversation_id}")

    return ConversationStartResponse(
        conversation_id=conversation_id,
        status="started",
    )


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: UUID,
    request: MessageRequest,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_org),
) -> MessageResponse:
    """Send message in conversation and get AI response"""
    context = _conversations.get(conversation_id)
    if not context:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if context.org_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Process message
    response = await orchestrator.process_user_message(
        context,
        request.message,
        provider=request.provider,
    )

    logger.info(f"Processed message in conversation {conversation_id}")

    return MessageResponse(
        message=response,
        intent=context.intent.value,
        sentiment=context.sentiment.value,
        extracted_info=context.extracted_info,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationStatusResponse)
async def get_conversation_status(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_org),
) -> ConversationStatusResponse:
    """Get conversation status"""
    context = _conversations.get(conversation_id)
    if not context:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if context.org_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if should escalate
    should_escalate = await orchestrator.should_escalate(context)

    return ConversationStatusResponse(
        conversation_id=conversation_id,
        state=context.state.value,
        intent=context.intent.value,
        sentiment=context.sentiment.value,
        message_count=len(context.messages),
        extracted_info=context.extracted_info,
        should_escalate=should_escalate,
    )


@router.post("/conversations/{conversation_id}/extract", response_model=dict)
async def extract_information(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_org),
) -> dict:
    """Extract structured information from conversation"""
    context = _conversations.get(conversation_id)
    if not context:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if context.org_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    info = await orchestrator.extract_information(context)

    logger.info(f"Extracted information from conversation {conversation_id}")

    return info


@router.post("/conversations/{conversation_id}/close")
async def close_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_org),
) -> dict:
    """Close conversation"""
    context = _conversations.get(conversation_id)
    if not context:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if context.org_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await orchestrator.end_conversation(context)

    # TODO: Save conversation to database

    logger.info(f"Closed conversation {conversation_id}")

    return {"status": "closed"}


# ============================================================================
# TOOL ENDPOINTS
# ============================================================================

@router.post("/tools/execute", response_model=ToolExecutionResponse)
async def execute_tool(
    request: ToolExecutionRequest,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_org),
) -> ToolExecutionResponse:
    """Execute a tool directly"""
    success, result = await tool_router.route_and_execute(
        context=_conversations.get(request.conversation_id),
        tool_id=request.tool_id,
        params=request.params,
        user_id=current_user.id,
    ) if request.conversation_id in _conversations else (False, {"error": "Conversation not found"})

    logger.info(f"Executed tool {request.tool_id} for org {current_org.id}")

    return ToolExecutionResponse(
        success=success,
        tool_id=request.tool_id,
        output=result,
        error=result.get("error") if not success else None,
    )


@router.get("/tools")
async def list_tools(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_org),
) -> list:
    """List available tools"""
    registry = tool_router.registry
    specs = registry.list_tools()

    return [spec.to_dict() for spec in specs]


@router.get("/tools/{tool_id}")
async def get_tool_spec(
    tool_id: str,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_org),
) -> dict:
    """Get tool specification"""
    registry = tool_router.registry
    spec = registry.get_spec(tool_id)

    if not spec:
        raise HTTPException(status_code=404, detail="Tool not found")

    return spec.to_dict()


# ============================================================================
# STREAMING ENDPOINTS
# ============================================================================

@router.websocket("/ws/conversations/{conversation_id}")
async def websocket_conversation(websocket):
    """WebSocket endpoint for streaming conversations"""
    await websocket.accept()

    conversation_id = websocket.path_params.get("conversation_id")
    context = _conversations.get(UUID(conversation_id))

    if not context:
        await websocket.close(code=4004, reason="Conversation not found")
        return

    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message")

            if not message:
                continue

            # Stream response
            async for chunk in orchestrator.stream_response(context, message):
                await websocket.send_json({"chunk": chunk})

            # Send completion signal
            await websocket.send_json({
                "done": True,
                "intent": context.intent.value,
                "sentiment": context.sentiment.value,
            })

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=1011, reason=str(e))


# ============================================================================
# USAGE & ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/usage/stats")
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_org),
) -> dict:
    """Get organization usage statistics"""
    from app.llm.usage import get_usage_tracker

    tracker = get_usage_tracker()
    stats = tracker.get_org_stats(current_org.id)

    return stats


@router.get("/usage/provider/{provider}")
async def get_provider_usage(
    provider: str,
    model: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_org),
) -> dict:
    """Get provider usage statistics"""
    from app.llm.usage import get_usage_tracker

    tracker = get_usage_tracker()
    stats = tracker.get_provider_stats(provider, model)

    return stats


@router.get("/cache/stats")
async def get_cache_stats(
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_org),
) -> dict:
    """Get cache statistics"""
    from app.llm.cache import get_llm_cache

    cache = get_llm_cache()
    return cache.get_stats()


@router.post("/cache/clear")
async def clear_cache(
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_org),
) -> dict:
    """Clear response cache"""
    from app.llm.cache import get_llm_cache

    cache = get_llm_cache()
    cache.clear()

    return {"status": "cleared"}
