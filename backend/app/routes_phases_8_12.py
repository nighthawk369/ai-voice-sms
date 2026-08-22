"""API Routes for PHASES 8-12: Knowledge Base, Voice, SMS, Calendar, and Integration Engine"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
import logging

from app.db import get_db
from app.security import get_current_user
from app.models import User, Organization
from app.knowledge_base import (
    KnowledgeBaseManager,
    EmbeddingManager,
    RAGRetriever,
    DocumentProcessor,
    KBBatchOperations,
)
from app.voice_integration import (
    VoiceCallManager,
    CallRecordingHandler,
    VoiceRouter,
)
from app.sms_integration import (
    SMSManager,
    OptOutManager,
    SMSQueueManager,
    TCPACompliance,
)
from app.calendar_integration import (
    UnifiedCalendarManager,
    CalendarProvider,
)
from app.integration_engine import (
    IntegrationManager,
    FieldMapper,
    SyncEngine,
    WebhookHandler,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Phase 8-12"])


# ============================================================================
# KNOWLEDGE BASE ROUTES (PHASE 8)
# ============================================================================

@router.post("/knowledge-base/items")
def create_kb_item(
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a knowledge base item"""
    try:
        kb_manager = KnowledgeBaseManager(db)
        item = kb_manager.create_item(
            current_user.organization_id,
            current_user.id,
            data,
        )
        return {
            "id": str(item.id),
            "title": item.title,
            "content": item.content,
            "category": item.category,
            "is_published": item.is_published,
        }
    except Exception as e:
        logger.error(f"Error creating KB item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-base/items")
def list_kb_items(
    category: Optional[str] = Query(None),
    is_published: Optional[bool] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List knowledge base items"""
    try:
        kb_manager = KnowledgeBaseManager(db)
        items, total = kb_manager.list_items(
            current_user.organization_id,
            category=category,
            is_published=is_published,
            skip=skip,
            limit=limit,
        )
        return {
            "items": [
                {
                    "id": str(item.id),
                    "title": item.title,
                    "category": item.category,
                    "is_published": item.is_published,
                }
                for item in items
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Error listing KB items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-base/items/{item_id}")
def get_kb_item(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a knowledge base item"""
    try:
        kb_manager = KnowledgeBaseManager(db)
        item = kb_manager.get_item(current_user.organization_id, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return {
            "id": str(item.id),
            "title": item.title,
            "content": item.content,
            "category": item.category,
            "tags": item.tags,
        }
    except Exception as e:
        logger.error(f"Error getting KB item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/knowledge-base/items/{item_id}")
def update_kb_item(
    item_id: UUID,
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a knowledge base item"""
    try:
        kb_manager = KnowledgeBaseManager(db)
        item = kb_manager.update_item(current_user.organization_id, item_id, data)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"status": "updated", "id": str(item.id)}
    except Exception as e:
        logger.error(f"Error updating KB item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/knowledge-base/items/{item_id}")
def delete_kb_item(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a knowledge base item"""
    try:
        kb_manager = KnowledgeBaseManager(db)
        success = kb_manager.delete_item(current_user.organization_id, item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"status": "deleted"}
    except Exception as e:
        logger.error(f"Error deleting KB item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge-base/search")
def search_kb(
    query: str = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search knowledge base (RAG)"""
    try:
        kb_manager = KnowledgeBaseManager(db)
        retriever = RAGRetriever(db, kb_manager)
        results = retriever.retrieve_context(current_user.organization_id, query)
        return {"query": query, "results": results}
    except Exception as e:
        logger.error(f"Error searching KB: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge-base/bulk-create")
def bulk_create_kb_items(
    items: List[dict] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bulk create knowledge base items"""
    try:
        kb_manager = KnowledgeBaseManager(db)
        batch_ops = KBBatchOperations(db, kb_manager)
        result = batch_ops.bulk_create_items(current_user.organization_id, current_user.id, items)
        return result
    except Exception as e:
        logger.error(f"Error bulk creating KB items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# VOICE INTEGRATION ROUTES (PHASE 9)
# ============================================================================

@router.post("/voice/calls")
def create_voice_call(
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a voice call"""
    try:
        call_manager = VoiceCallManager(db)
        result = call_manager.create_call(
            current_user.organization_id,
            data.get("to_phone"),
            contact_id=data.get("contact_id"),
        )
        return result
    except Exception as e:
        logger.error(f"Error creating voice call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voice/calls")
def list_voice_calls(
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List voice calls"""
    try:
        call_manager = VoiceCallManager(db)
        calls, total = call_manager.list_calls(
            current_user.organization_id,
            status=status,
            skip=skip,
            limit=limit,
        )
        return {
            "calls": calls,
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Error listing voice calls: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voice/calls/{call_id}")
def get_voice_call(
    call_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get voice call details"""
    try:
        call_manager = VoiceCallManager(db)
        call = call_manager.get_call(current_user.organization_id, call_id)
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        return call
    except Exception as e:
        logger.error(f"Error getting voice call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/calls/{call_id}/end")
def end_voice_call(
    call_id: UUID,
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """End a voice call"""
    try:
        call_manager = VoiceCallManager(db)
        success = call_manager.end_call(
            current_user.organization_id,
            call_id,
            transcript=data.get("transcript"),
            recording_url=data.get("recording_url"),
            duration_seconds=data.get("duration_seconds"),
        )
        if not success:
            raise HTTPException(status_code=404, detail="Call not found")
        return {"status": "ended"}
    except Exception as e:
        logger.error(f"Error ending voice call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/calls/{call_id}/transfer")
def transfer_voice_call(
    call_id: UUID,
    transfer_to: str = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Transfer a voice call"""
    try:
        call_manager = VoiceCallManager(db)
        success = call_manager.transfer_call(
            current_user.organization_id,
            call_id,
            transfer_to,
        )
        if not success:
            raise HTTPException(status_code=404, detail="Call not found")
        return {"status": "transferred", "transfer_to": transfer_to}
    except Exception as e:
        logger.error(f"Error transferring voice call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voice/calls/{call_id}/messages")
def get_call_messages(
    call_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get messages from a voice call"""
    try:
        call_manager = VoiceCallManager(db)
        messages = call_manager.get_call_messages(current_user.organization_id, call_id)
        return {"messages": messages}
    except Exception as e:
        logger.error(f"Error getting call messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SMS INTEGRATION ROUTES (PHASE 10)
# ============================================================================

@router.post("/sms/send")
def send_sms(
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send SMS message"""
    try:
        sms_manager = SMSManager(db)
        result = sms_manager.send_sms(
            current_user.organization_id,
            data.get("to_phone"),
            data.get("message_text"),
            contact_id=data.get("contact_id"),
        )
        return result
    except Exception as e:
        logger.error(f"Error sending SMS: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sms/conversations")
def list_sms_conversations(
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List SMS conversations"""
    try:
        sms_manager = SMSManager(db)
        conversations, total = sms_manager.list_conversations(
            current_user.organization_id,
            status=status,
            skip=skip,
            limit=limit,
        )
        return {
            "conversations": conversations,
            "total": total,
        }
    except Exception as e:
        logger.error(f"Error listing SMS conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sms/conversations/{conversation_id}")
def get_sms_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get SMS conversation"""
    try:
        sms_manager = SMSManager(db)
        conversation = sms_manager.get_conversation(
            current_user.organization_id,
            conversation_id,
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except Exception as e:
        logger.error(f"Error getting SMS conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sms/batch-send")
def batch_send_sms(
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Batch send SMS messages"""
    try:
        sms_queue = SMSQueueManager(db)
        result = sms_queue.queue_batch_sms(
            current_user.organization_id,
            data.get("recipients", []),
            data.get("message_text"),
        )
        return result
    except Exception as e:
        logger.error(f"Error batch sending SMS: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sms/dnc/add")
def add_to_dnc_list(
    phone: str = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add phone to DNC list"""
    try:
        dnc_manager = OptOutManager(db)
        success = dnc_manager.add_to_dnc_list(current_user.organization_id, phone)
        return {"status": "added" if success else "failed"}
    except Exception as e:
        logger.error(f"Error adding to DNC list: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sms/dnc/list")
def get_dnc_list(
    skip: int = Query(0),
    limit: int = Query(1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get DNC list"""
    try:
        dnc_manager = OptOutManager(db)
        phones, total = dnc_manager.get_dnc_list(
            current_user.organization_id,
            skip=skip,
            limit=limit,
        )
        return {"phones": phones, "total": total}
    except Exception as e:
        logger.error(f"Error getting DNC list: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sms/queue/stats")
def get_sms_queue_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get SMS queue statistics"""
    try:
        sms_queue = SMSQueueManager(db)
        stats = sms_queue.get_queue_stats(current_user.organization_id)
        return stats
    except Exception as e:
        logger.error(f"Error getting SMS queue stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CALENDAR INTEGRATION ROUTES (PHASE 11)
# ============================================================================

@router.get("/calendar/availability/{user_id}")
def get_user_availability(
    user_id: UUID,
    date: Optional[str] = Query(None),
    duration_minutes: int = Query(30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's available time slots"""
    try:
        calendar_manager = UnifiedCalendarManager(db, current_user.organization_id)
        if date:
            slots = calendar_manager.list_available_slots(user_id, date, duration_minutes)
            return {"date": date, "slots": slots}
        else:
            availability = calendar_manager.get_availability(user_id)
            return availability
    except Exception as e:
        logger.error(f"Error getting user availability: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calendar/appointments")
def book_appointment(
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Book a calendar appointment"""
    try:
        calendar_manager = UnifiedCalendarManager(db, current_user.organization_id)
        result = calendar_manager.book_appointment(
            data.get("provider", "google"),
            data.get("user_id"),
            data.get("contact_id"),
            data.get("start_time"),
            data.get("end_time"),
            data.get("title"),
            description=data.get("description"),
        )
        return result
    except Exception as e:
        logger.error(f"Error booking appointment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calendar/sync")
def sync_calendars(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sync all calendars"""
    try:
        calendar_manager = UnifiedCalendarManager(db, current_user.organization_id)
        results = calendar_manager.sync_all_calendars(current_user.id)
        return results
    except Exception as e:
        logger.error(f"Error syncing calendars: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# INTEGRATION ENGINE ROUTES (PHASE 12)
# ============================================================================

@router.post("/integrations")
def create_integration(
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new integration"""
    try:
        integration_manager = IntegrationManager(db)
        integration_id = integration_manager.create_integration(
            current_user.organization_id,
            data.get("integration_type"),
            data.get("name"),
            data.get("credentials", {}),
        )
        if not integration_id:
            raise HTTPException(status_code=400, detail="Failed to create integration")
        return {
            "id": integration_id,
            "status": "created",
        }
    except Exception as e:
        logger.error(f"Error creating integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/integrations")
def list_integrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all integrations"""
    try:
        integration_manager = IntegrationManager(db)
        integrations = integration_manager.list_integrations(current_user.organization_id)
        return {
            "integrations": [
                {
                    "id": str(i.id),
                    "type": i.integration_type,
                    "name": i.name,
                    "is_active": i.is_active,
                    "sync_status": i.sync_status,
                }
                for i in integrations
            ]
        }
    except Exception as e:
        logger.error(f"Error listing integrations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/integrations/{integration_id}/activate")
def activate_integration(
    integration_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Activate integration"""
    try:
        integration_manager = IntegrationManager(db)
        success = integration_manager.activate_integration(
            current_user.organization_id,
            integration_id,
        )
        if not success:
            raise HTTPException(status_code=404, detail="Integration not found")
        return {"status": "activated"}
    except Exception as e:
        logger.error(f"Error activating integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/integrations/{integration_id}/deactivate")
def deactivate_integration(
    integration_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deactivate integration"""
    try:
        integration_manager = IntegrationManager(db)
        success = integration_manager.deactivate_integration(
            current_user.organization_id,
            integration_id,
        )
        if not success:
            raise HTTPException(status_code=404, detail="Integration not found")
        return {"status": "deactivated"}
    except Exception as e:
        logger.error(f"Error deactivating integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/integrations/webhook")
def handle_integration_webhook(
    system: str = Body(...),
    event_type: str = Body(...),
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    """Handle incoming webhook from integrated system"""
    try:
        # Extract org_id from payload if available
        org_id = payload.get("organization_id")
        if not org_id:
            raise HTTPException(status_code=400, detail="organization_id required in payload")

        webhook_handler = WebhookHandler(db)
        success = webhook_handler.handle_webhook(
            UUID(org_id),
            system,
            event_type,
            payload,
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to process webhook")
        return {"status": "processed"}
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/integrations/sync")
def sync_integration(
    integration_id: UUID = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sync specific integration"""
    try:
        integration_manager = IntegrationManager(db)
        integration = integration_manager.get_integration(current_user.organization_id, integration_id)
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")

        # Get adapter and sync
        adapter = integration_manager.get_adapter(
            integration.integration_type,
            integration.config,
        )
        if not adapter:
            raise HTTPException(status_code=400, detail="Failed to initialize adapter")

        sync_engine = SyncEngine(db)
        result = sync_engine.sync_contacts(
            current_user.organization_id,
            integration.integration_type,
            "platform",
            adapter,
            FieldMapper(),
        )
        return result
    except Exception as e:
        logger.error(f"Error syncing integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))
