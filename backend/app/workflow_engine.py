"""Workflow Engine - Triggers, Conditions, and Actions"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from uuid import uuid4, UUID
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models import (
    Workflow, WorkflowExecution, Contact, Deal, Activity,
    Conversation, Organization, Task, Integration
)

logger = logging.getLogger(__name__)


class TriggerType(str, Enum):
    """Supported workflow triggers"""
    CALL_RECEIVED = "call_received"
    CALL_ENDED = "call_ended"
    CONTACT_CREATED = "contact_created"
    CONTACT_UPDATED = "contact_updated"
    DEAL_CREATED = "deal_created"
    DEAL_WON = "deal_won"
    DEAL_LOST = "deal_lost"
    ACTIVITY_CREATED = "activity_created"
    MESSAGE_RECEIVED = "message_received"
    FORM_SUBMITTED = "form_submitted"


class ActionType(str, Enum):
    """Supported workflow actions"""
    SEND_SMS = "send_sms"
    SEND_EMAIL = "send_email"
    CREATE_TASK = "create_task"
    UPDATE_CONTACT = "update_contact"
    CREATE_ACTIVITY = "create_activity"
    UPDATE_DEAL = "update_deal"
    ESCALATE = "escalate"
    WEBHOOK = "webhook"
    SYNC_CRM = "sync_crm"


class ConditionOperator(str, Enum):
    """Condition operators"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"


class WorkflowCondition:
    """Condition evaluator"""

    @staticmethod
    def evaluate(value: Any, operator: str, compare_to: Any) -> bool:
        """Evaluate a condition"""
        if operator == ConditionOperator.EQUALS:
            return value == compare_to
        elif operator == ConditionOperator.NOT_EQUALS:
            return value != compare_to
        elif operator == ConditionOperator.GREATER_THAN:
            return float(value) > float(compare_to)
        elif operator == ConditionOperator.LESS_THAN:
            return float(value) < float(compare_to)
        elif operator == ConditionOperator.CONTAINS:
            return str(compare_to).lower() in str(value).lower()
        elif operator == ConditionOperator.NOT_CONTAINS:
            return str(compare_to).lower() not in str(value).lower()
        elif operator == ConditionOperator.IN:
            return value in (compare_to if isinstance(compare_to, list) else [compare_to])
        elif operator == ConditionOperator.NOT_IN:
            return value not in (compare_to if isinstance(compare_to, list) else [compare_to])
        return False

    @staticmethod
    def evaluate_conditions(data: Dict[str, Any], conditions: List[Dict[str, Any]]) -> bool:
        """Evaluate multiple conditions (AND logic)"""
        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")

            if field not in data:
                return False

            if not WorkflowCondition.evaluate(data[field], operator, value):
                return False

        return True


class WorkflowAction:
    """Base workflow action executor"""

    @staticmethod
    async def execute_send_sms(
        db: Session,
        config: Dict[str, Any],
        trigger_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute send SMS action"""
        try:
            phone_number = config.get("phone_number") or trigger_data.get("phone")
            message = config.get("message", "")

            if not phone_number:
                return {"success": False, "error": "No phone number provided"}

            # TODO: Integrate with SMS service
            logger.info(f"Sending SMS to {phone_number}: {message}")

            return {
                "success": True,
                "sms_id": str(uuid4()),
                "phone": phone_number
            }
        except Exception as e:
            logger.error(f"SMS action failed: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    async def execute_send_email(
        db: Session,
        config: Dict[str, Any],
        trigger_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute send email action"""
        try:
            email = config.get("email") or trigger_data.get("email")
            subject = config.get("subject", "")
            body = config.get("body", "")

            if not email:
                return {"success": False, "error": "No email provided"}

            # TODO: Integrate with email service
            logger.info(f"Sending email to {email}: {subject}")

            return {
                "success": True,
                "email_id": str(uuid4()),
                "email": email
            }
        except Exception as e:
            logger.error(f"Email action failed: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    async def execute_create_task(
        db: Session,
        config: Dict[str, Any],
        trigger_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute create task action"""
        try:
            contact_id = trigger_data.get("contact_id")
            organization_id = trigger_data.get("organization_id")

            if not contact_id:
                return {"success": False, "error": "No contact_id in trigger data"}

            task = Task(
                id=uuid4(),
                organization_id=organization_id,
                contact_id=contact_id,
                title=config.get("title", "Workflow Task"),
                description=config.get("description", ""),
                priority=config.get("priority", "MEDIUM"),
                due_date=datetime.utcnow() + timedelta(days=config.get("due_days", 1))
            )

            db.add(task)
            db.commit()

            logger.info(f"Created task {task.id}")

            return {
                "success": True,
                "task_id": str(task.id)
            }
        except Exception as e:
            logger.error(f"Create task action failed: {str(e)}")
            db.rollback()
            return {"success": False, "error": str(e)}

    @staticmethod
    async def execute_update_contact(
        db: Session,
        config: Dict[str, Any],
        trigger_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute update contact action"""
        try:
            contact_id = trigger_data.get("contact_id")

            if not contact_id:
                return {"success": False, "error": "No contact_id in trigger data"}

            contact = db.query(Contact).filter(Contact.id == UUID(contact_id)).first()
            if not contact:
                return {"success": False, "error": "Contact not found"}

            # Update contact fields
            if "status" in config:
                contact.status = config["status"]
            if "notes" in config:
                contact.notes = config["notes"]
            if "custom_fields" in config:
                contact.custom_fields.update(config["custom_fields"])

            contact.updated_at = datetime.utcnow()
            db.commit()

            logger.info(f"Updated contact {contact_id}")

            return {
                "success": True,
                "contact_id": str(contact.id)
            }
        except Exception as e:
            logger.error(f"Update contact action failed: {str(e)}")
            db.rollback()
            return {"success": False, "error": str(e)}

    @staticmethod
    async def execute_create_activity(
        db: Session,
        config: Dict[str, Any],
        trigger_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute create activity action"""
        try:
            contact_id = trigger_data.get("contact_id")
            organization_id = trigger_data.get("organization_id")

            if not contact_id:
                return {"success": False, "error": "No contact_id in trigger data"}

            activity = Activity(
                id=uuid4(),
                organization_id=organization_id,
                contact_id=contact_id,
                activity_type=config.get("activity_type", "NOTE"),
                title=config.get("title", "Workflow Activity"),
                description=config.get("description", ""),
                metadata=config.get("metadata", {})
            )

            db.add(activity)
            db.commit()

            logger.info(f"Created activity {activity.id}")

            return {
                "success": True,
                "activity_id": str(activity.id)
            }
        except Exception as e:
            logger.error(f"Create activity action failed: {str(e)}")
            db.rollback()
            return {"success": False, "error": str(e)}

    @staticmethod
    async def execute_update_deal(
        db: Session,
        config: Dict[str, Any],
        trigger_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute update deal action"""
        try:
            deal_id = trigger_data.get("deal_id")

            if not deal_id:
                return {"success": False, "error": "No deal_id in trigger data"}

            deal = db.query(Deal).filter(Deal.id == UUID(deal_id)).first()
            if not deal:
                return {"success": False, "error": "Deal not found"}

            # Update deal fields
            if "stage" in config:
                deal.stage = config["stage"]
            if "status" in config:
                deal.deal_status = config["status"]
            if "probability" in config:
                deal.probability = config["probability"]

            deal.updated_at = datetime.utcnow()
            db.commit()

            logger.info(f"Updated deal {deal_id}")

            return {
                "success": True,
                "deal_id": str(deal.id)
            }
        except Exception as e:
            logger.error(f"Update deal action failed: {str(e)}")
            db.rollback()
            return {"success": False, "error": str(e)}

    @staticmethod
    async def execute(
        db: Session,
        action_type: str,
        config: Dict[str, Any],
        trigger_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an action"""
        if action_type == ActionType.SEND_SMS:
            return await WorkflowAction.execute_send_sms(db, config, trigger_data)
        elif action_type == ActionType.SEND_EMAIL:
            return await WorkflowAction.execute_send_email(db, config, trigger_data)
        elif action_type == ActionType.CREATE_TASK:
            return await WorkflowAction.execute_create_task(db, config, trigger_data)
        elif action_type == ActionType.UPDATE_CONTACT:
            return await WorkflowAction.execute_update_contact(db, config, trigger_data)
        elif action_type == ActionType.CREATE_ACTIVITY:
            return await WorkflowAction.execute_create_activity(db, config, trigger_data)
        elif action_type == ActionType.UPDATE_DEAL:
            return await WorkflowAction.execute_update_deal(db, config, trigger_data)
        else:
            return {"success": False, "error": f"Unknown action type: {action_type}"}


class WorkflowExecutor:
    """Executes workflows"""

    def __init__(self, db: Session):
        self.db = db

    async def execute_workflow(
        self,
        workflow: Workflow,
        trigger_data: Dict[str, Any]
    ) -> WorkflowExecution:
        """Execute a workflow with trigger data"""
        try:
            execution = WorkflowExecution(
                id=uuid4(),
                workflow_id=workflow.id,
                organization_id=workflow.organization_id,
                trigger_data=trigger_data,
                status="RUNNING",
                execution_logs=[]
            )

            self.db.add(execution)
            self.db.flush()

            # Evaluate conditions
            conditions = workflow.conditions or []
            if conditions and not WorkflowCondition.evaluate_conditions(trigger_data, conditions):
                execution.status = "SKIPPED"
                self.db.commit()
                logger.info(f"Workflow {workflow.id} skipped due to conditions")
                return execution

            # Execute actions
            actions = workflow.actions or []
            for idx, action in enumerate(actions):
                try:
                    action_type = action.get("type")
                    action_config = action.get("config", {})

                    result = await WorkflowAction.execute(
                        self.db,
                        action_type,
                        action_config,
                        trigger_data
                    )

                    execution.execution_logs.append({
                        "action_index": idx,
                        "action_type": action_type,
                        "status": "SUCCESS" if result.get("success") else "FAILED",
                        "result": result,
                        "timestamp": datetime.utcnow().isoformat()
                    })

                    if result.get("success"):
                        execution.actions_executed += 1
                    else:
                        execution.actions_failed += 1

                except Exception as e:
                    logger.error(f"Action {idx} failed: {str(e)}")
                    execution.actions_failed += 1
                    execution.execution_logs.append({
                        "action_index": idx,
                        "action_type": action.get("type"),
                        "status": "FAILED",
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    })

            # Update workflow execution status and workflow stats
            execution.status = "SUCCESS" if execution.actions_failed == 0 else "FAILED"
            execution.started_at = datetime.utcnow()
            execution.completed_at = datetime.utcnow()

            workflow.execution_count += 1
            workflow.last_execution_at = datetime.utcnow()

            self.db.commit()
            logger.info(f"Workflow {workflow.id} execution completed with status {execution.status}")

            return execution

        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            execution.status = "FAILED"
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            self.db.commit()
            return execution

    async def trigger_workflow(
        self,
        organization_id: UUID,
        trigger_type: str,
        trigger_data: Dict[str, Any]
    ) -> List[WorkflowExecution]:
        """Trigger workflows by type"""
        try:
            # Find all active workflows matching this trigger
            workflows = self.db.query(Workflow).filter(
                and_(
                    Workflow.organization_id == organization_id,
                    Workflow.trigger_type == trigger_type,
                    Workflow.is_active == True
                )
            ).all()

            executions = []
            for workflow in workflows:
                execution = await self.execute_workflow(workflow, trigger_data)
                executions.append(execution)

            return executions

        except Exception as e:
            logger.error(f"Failed to trigger workflows: {str(e)}")
            return []
