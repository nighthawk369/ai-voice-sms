"""Utility functions for API operations"""

import logging
import json
from datetime import datetime, timezone
from typing import Optional, List, Any, Dict
from uuid import UUID
from enum import Enum
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.orm import InstrumentedAttribute

logger = logging.getLogger(__name__)


class SortOrder(str, Enum):
    """Sort order enumeration"""
    ASC = "asc"
    DESC = "desc"


class AuditAction(str, Enum):
    """Audit action types"""
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    IMPORT = "IMPORT"
    EXPORT = "EXPORT"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"


class AuditLog:
    """Audit logging utility"""

    @staticmethod
    def log_action(
        organization_id: UUID,
        user_id: UUID,
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[UUID] = None,
        changes: Optional[Dict[str, Any]] = None,
        status: str = "SUCCESS",
        details: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create audit log entry"""
        return {
            "organization_id": str(organization_id),
            "user_id": str(user_id),
            "action": action.value,
            "resource_type": resource_type,
            "resource_id": str(resource_id) if resource_id else None,
            "changes": changes or {},
            "status": status,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


class FilterBuilder:
    """Build SQL filters from query parameters"""

    @staticmethod
    def build_filters(
        model: type,
        filter_params: Dict[str, Any],
        allowed_fields: Optional[List[str]] = None
    ) -> Optional[Any]:
        """Build SQLAlchemy filter from parameters"""
        if not filter_params:
            return None

        filters = []

        for field_name, value in filter_params.items():
            if allowed_fields and field_name not in allowed_fields:
                continue

            if not hasattr(model, field_name):
                continue

            field = getattr(model, field_name)

            # Handle different filter types
            if isinstance(value, dict):
                op = value.get("op", "eq")
                val = value.get("value")

                if op == "eq":
                    filters.append(field == val)
                elif op == "neq":
                    filters.append(field != val)
                elif op == "gt":
                    filters.append(field > val)
                elif op == "gte":
                    filters.append(field >= val)
                elif op == "lt":
                    filters.append(field < val)
                elif op == "lte":
                    filters.append(field <= val)
                elif op == "like":
                    filters.append(field.ilike(f"%{val}%"))
                elif op == "in":
                    filters.append(field.in_(val))
            else:
                # Simple equality
                filters.append(field == value)

        return and_(*filters) if filters else None

    @staticmethod
    def build_search(
        model: type,
        search_term: str,
        search_fields: List[str]
    ) -> Optional[Any]:
        """Build search filter for multiple fields"""
        if not search_term or not search_fields:
            return None

        conditions = []
        for field_name in search_fields:
            if hasattr(model, field_name):
                field = getattr(model, field_name)
                conditions.append(field.ilike(f"%{search_term}%"))

        return or_(*conditions) if conditions else None


class SortBuilder:
    """Build SQL sorting from query parameters"""

    @staticmethod
    def build_sort(
        model: type,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        default_field: Optional[str] = None,
        allowed_fields: Optional[List[str]] = None
    ) -> Optional[Any]:
        """Build SQLAlchemy sort expression"""
        field_name = sort_by or default_field or "created_at"

        if allowed_fields and field_name not in allowed_fields:
            field_name = default_field or "created_at"

        if not hasattr(model, field_name):
            field_name = "created_at"

        field: InstrumentedAttribute = getattr(model, field_name)

        if sort_order.lower() == SortOrder.DESC.value:
            return desc(field)
        return asc(field)


class PaginationHelper:
    """Pagination helper utilities"""

    @staticmethod
    def calculate_offset(skip: int, limit: int) -> int:
        """Calculate offset from skip parameter"""
        return max(0, skip)

    @staticmethod
    def get_limit(limit: int, max_limit: int = 500) -> int:
        """Ensure limit is within bounds"""
        return min(max(1, limit), max_limit)

    @staticmethod
    def build_pagination_response(
        items: List[Any],
        total: int,
        skip: int,
        limit: int
    ) -> Dict[str, Any]:
        """Build paginated response"""
        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "pages": (total + limit - 1) // limit if limit > 0 else 1
        }


class ChangeTracker:
    """Track changes between old and new data"""

    @staticmethod
    def get_changes(
        old_data: Optional[Dict[str, Any]],
        new_data: Dict[str, Any],
        tracked_fields: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Get changes between two versions of data"""
        if not old_data:
            return {"created": new_data}

        changes = {}

        for key, new_value in new_data.items():
            if tracked_fields and key not in tracked_fields:
                continue

            old_value = old_data.get(key)
            if old_value != new_value:
                changes[key] = {
                    "old": old_value,
                    "new": new_value
                }

        return changes if changes else {}


class BulkOperationHelper:
    """Helper for bulk operations"""

    @staticmethod
    def validate_bulk_items(
        items: List[Dict[str, Any]],
        required_fields: List[str],
        max_items: int = 100
    ) -> tuple[bool, Optional[str]]:
        """Validate bulk operation items"""
        if not items:
            return False, "No items provided"

        if len(items) > max_items:
            return False, f"Maximum {max_items} items allowed per request"

        for idx, item in enumerate(items):
            for field in required_fields:
                if field not in item:
                    return False, f"Item {idx}: missing required field '{field}'"

        return True, None

    @staticmethod
    def chunk_items(items: List[Any], chunk_size: int = 100) -> List[List[Any]]:
        """Split items into chunks for batch processing"""
        return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def serialize_model(model_instance: Any, exclude_fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """Serialize SQLAlchemy model to dictionary"""
    if not hasattr(model_instance, '__table__'):
        return {}

    data = {}
    for column in model_instance.__table__.columns:
        value = getattr(model_instance, column.name)

        if exclude_fields and column.name in exclude_fields:
            continue

        # Handle special types
        if isinstance(value, UUID):
            value = str(value)
        elif isinstance(value, datetime):
            value = value.isoformat()
        elif isinstance(value, Enum):
            value = value.value

        data[column.name] = value

    return data
