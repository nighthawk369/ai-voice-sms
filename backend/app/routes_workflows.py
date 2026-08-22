"""Workflow API Routes - Create, manage, and execute workflows"""

import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.db import get_db
from app.dependencies import get_current_user
from app.models import Workflow, WorkflowExecution, Organization, User
from app.schemas import WorkflowCreateSchema, WorkflowUpdateSchema, WorkflowResponseSchema
from app.workflow_engine import WorkflowExecutor, TriggerType, ActionType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])


# ============================================================================
# WORKFLOW MANAGEMENT ROUTES
# ============================================================================

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    schema: WorkflowCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new workflow"""
    try:
        org = db.query(Organization).filter(
            Organization.id == current_user.organization_id
        ).first()

        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        workflow = Workflow(
            id=None,  # Auto-generate
            organization_id=org.id,
            name=schema.name,
            description=schema.description,
            trigger_type=schema.trigger_type,
            trigger_config=schema.trigger_config or {},
            conditions=schema.conditions or [],
            actions=schema.actions or [],
            is_active=schema.is_active if schema.is_active is not None else True
        )

        db.add(workflow)
        db.commit()
        db.refresh(workflow)

        logger.info(f"Created workflow {workflow.id}")

        return {
            "id": str(workflow.id),
            "name": workflow.name,
            "trigger_type": workflow.trigger_type,
            "is_active": workflow.is_active,
            "created_at": workflow.created_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=dict)
async def list_workflows(
    skip: int = 0,
    limit: int = 50,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List workflows for organization"""
    try:
        query = db.query(Workflow).filter(
            Workflow.organization_id == current_user.organization_id
        )

        if active_only:
            query = query.filter(Workflow.is_active == True)

        workflows = query.offset(skip).limit(limit).all()
        total = query.count()

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "workflows": [
                {
                    "id": str(w.id),
                    "name": w.name,
                    "trigger_type": w.trigger_type,
                    "is_active": w.is_active,
                    "execution_count": w.execution_count,
                    "last_execution_at": w.last_execution_at.isoformat() if w.last_execution_at else None,
                    "created_at": w.created_at.isoformat()
                }
                for w in workflows
            ]
        }

    except Exception as e:
        logger.error(f"Failed to list workflows: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}", response_model=dict)
async def get_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get workflow details"""
    try:
        workflow = db.query(Workflow).filter(
            and_(
                Workflow.id == UUID(workflow_id),
                Workflow.organization_id == current_user.organization_id
            )
        ).first()

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        return {
            "id": str(workflow.id),
            "name": workflow.name,
            "description": workflow.description,
            "trigger_type": workflow.trigger_type,
            "trigger_config": workflow.trigger_config,
            "conditions": workflow.conditions,
            "actions": workflow.actions,
            "is_active": workflow.is_active,
            "execution_count": workflow.execution_count,
            "last_execution_at": workflow.last_execution_at.isoformat() if workflow.last_execution_at else None,
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{workflow_id}", response_model=dict)
async def update_workflow(
    workflow_id: str,
    schema: WorkflowUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update workflow"""
    try:
        workflow = db.query(Workflow).filter(
            and_(
                Workflow.id == UUID(workflow_id),
                Workflow.organization_id == current_user.organization_id
            )
        ).first()

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        if schema.name:
            workflow.name = schema.name
        if schema.description:
            workflow.description = schema.description
        if schema.conditions:
            workflow.conditions = schema.conditions
        if schema.actions:
            workflow.actions = schema.actions
        if schema.is_active is not None:
            workflow.is_active = schema.is_active

        db.commit()
        db.refresh(workflow)

        logger.info(f"Updated workflow {workflow.id}")

        return {
            "id": str(workflow.id),
            "name": workflow.name,
            "is_active": workflow.is_active,
            "updated_at": workflow.updated_at.isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to update workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete workflow"""
    try:
        workflow = db.query(Workflow).filter(
            and_(
                Workflow.id == UUID(workflow_id),
                Workflow.organization_id == current_user.organization_id
            )
        ).first()

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        db.delete(workflow)
        db.commit()

        logger.info(f"Deleted workflow {workflow.id}")

    except Exception as e:
        logger.error(f"Failed to delete workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WORKFLOW EXECUTION ROUTES
# ============================================================================

@router.post("/{workflow_id}/execute", response_model=dict)
async def execute_workflow(
    workflow_id: str,
    trigger_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually execute a workflow"""
    try:
        workflow = db.query(Workflow).filter(
            and_(
                Workflow.id == UUID(workflow_id),
                Workflow.organization_id == current_user.organization_id
            )
        ).first()

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        executor = WorkflowExecutor(db)
        execution = await executor.execute_workflow(workflow, trigger_data)

        return {
            "execution_id": str(execution.id),
            "status": execution.status,
            "actions_executed": execution.actions_executed,
            "actions_failed": execution.actions_failed,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None
        }

    except Exception as e:
        logger.error(f"Failed to execute workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}/executions", response_model=dict)
async def list_workflow_executions(
    workflow_id: str,
    skip: int = 0,
    limit: int = 50,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List workflow executions"""
    try:
        workflow = db.query(Workflow).filter(
            and_(
                Workflow.id == UUID(workflow_id),
                Workflow.organization_id == current_user.organization_id
            )
        ).first()

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        query = db.query(WorkflowExecution).filter(
            WorkflowExecution.workflow_id == UUID(workflow_id)
        )

        if status:
            query = query.filter(WorkflowExecution.status == status)

        executions = query.order_by(
            WorkflowExecution.created_at.desc()
        ).offset(skip).limit(limit).all()

        total = query.count()

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "executions": [
                {
                    "id": str(e.id),
                    "status": e.status,
                    "actions_executed": e.actions_executed,
                    "actions_failed": e.actions_failed,
                    "started_at": e.started_at.isoformat() if e.started_at else None,
                    "completed_at": e.completed_at.isoformat() if e.completed_at else None,
                    "created_at": e.created_at.isoformat()
                }
                for e in executions
            ]
        }

    except Exception as e:
        logger.error(f"Failed to list executions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}/executions/{execution_id}", response_model=dict)
async def get_workflow_execution(
    workflow_id: str,
    execution_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get workflow execution details"""
    try:
        workflow = db.query(Workflow).filter(
            and_(
                Workflow.id == UUID(workflow_id),
                Workflow.organization_id == current_user.organization_id
            )
        ).first()

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        execution = db.query(WorkflowExecution).filter(
            WorkflowExecution.id == UUID(execution_id)
        ).first()

        if not execution or execution.workflow_id != workflow.id:
            raise HTTPException(status_code=404, detail="Execution not found")

        return {
            "id": str(execution.id),
            "workflow_id": str(execution.workflow_id),
            "status": execution.status,
            "trigger_data": execution.trigger_data,
            "actions_executed": execution.actions_executed,
            "actions_failed": execution.actions_failed,
            "error_message": execution.error_message,
            "execution_logs": execution.execution_logs,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "created_at": execution.created_at.isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get execution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WORKFLOW TEMPLATES ROUTES
# ============================================================================

@router.get("/templates/available", response_model=dict)
async def get_available_templates():
    """Get available workflow templates"""
    return {
        "templates": [
            {
                "id": "welcome_sms",
                "name": "Welcome SMS",
                "description": "Send SMS when new contact is created",
                "trigger": "contact_created",
                "actions": [
                    {
                        "type": "send_sms",
                        "config": {
                            "message": "Welcome! Thanks for reaching out."
                        }
                    }
                ]
            },
            {
                "id": "deal_won_notification",
                "name": "Deal Won Notification",
                "description": "Create task when deal is won",
                "trigger": "deal_won",
                "actions": [
                    {
                        "type": "create_activity",
                        "config": {
                            "activity_type": "NOTE",
                            "title": "Deal Won",
                            "description": "Deal has been won"
                        }
                    }
                ]
            },
            {
                "id": "follow_up_task",
                "name": "Auto Follow-Up Task",
                "description": "Create follow-up task after call",
                "trigger": "call_ended",
                "actions": [
                    {
                        "type": "create_task",
                        "config": {
                            "title": "Follow-up Call",
                            "priority": "MEDIUM",
                            "due_days": 3
                        }
                    }
                ]
            }
        ]
    }
