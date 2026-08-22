"""Tool system for AI-driven actions"""

import logging
import json
from typing import Dict, Any, List, Optional, Callable, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID
from datetime import datetime
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ToolCategory(str, Enum):
    """Tool categories"""
    CRM = "CRM"
    CALENDAR = "CALENDAR"
    COMMUNICATION = "COMMUNICATION"
    KNOWLEDGE = "KNOWLEDGE"
    WORKFLOW = "WORKFLOW"


class ToolType(str, Enum):
    """Tool types"""
    ACTION = "ACTION"
    QUERY = "QUERY"
    SEARCH = "SEARCH"


@dataclass
class ToolParameter:
    """Tool parameter specification"""
    name: str
    type: str  # "string", "number", "boolean", "array", "object"
    description: str
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None


@dataclass
class ToolSpec:
    """Tool specification"""
    id: str
    name: str
    description: str
    category: ToolCategory
    tool_type: ToolType
    parameters: List[ToolParameter]
    output_schema: Dict[str, Any]
    rate_limit: Optional[int] = None  # requests per minute
    requires_auth: bool = False
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "type": self.tool_type.value,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type,
                    "description": p.description,
                    "required": p.required,
                    "default": p.default,
                    "enum": p.enum,
                } for p in self.parameters
            ],
            "output_schema": self.output_schema,
            "rate_limit": self.rate_limit,
            "requires_auth": self.requires_auth,
            "tags": self.tags,
        }


@dataclass
class ToolResult:
    """Result from tool execution"""
    tool_id: str
    success: bool
    output: Dict[str, Any]
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ToolAuditLog:
    """Audit log entry for tool execution"""
    tool_id: str
    org_id: UUID
    user_id: Optional[UUID]
    input_params: Dict[str, Any]
    output: Dict[str, Any]
    status: str  # "success", "failed", "denied"
    reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "org_id": str(self.org_id),
            "user_id": str(self.user_id) if self.user_id else None,
            "input_params": self.input_params,
            "output": self.output,
            "status": self.status,
            "reason": self.reason,
            "created_at": self.created_at.isoformat(),
        }


class Tool(ABC):
    """Abstract base class for tools"""

    def __init__(self, spec: ToolSpec):
        self.spec = spec
        self.last_executed = None

    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Execute the tool with given parameters"""
        pass

    def validate_parameters(self, params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate parameters against spec"""
        for param in self.spec.parameters:
            if param.required and param.name not in params:
                return False, f"Missing required parameter: {param.name}"

        return True, None


class CRMTool(Tool):
    """Base class for CRM tools"""

    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Execute CRM operation"""
        is_valid, error = self.validate_parameters(params)
        if not is_valid:
            return ToolResult(
                tool_id=self.spec.id,
                success=False,
                output={},
                error=error,
            )

        try:
            start_time = datetime.utcnow()
            output = await self._execute_crm_operation(params)
            execution_time = (datetime.utcnow() - start_time).total_seconds()

            return ToolResult(
                tool_id=self.spec.id,
                success=True,
                output=output,
                execution_time=execution_time,
            )
        except Exception as e:
            logger.error(f"CRM tool execution failed: {e}")
            return ToolResult(
                tool_id=self.spec.id,
                success=False,
                output={},
                error=str(e),
            )

    @abstractmethod
    async def _execute_crm_operation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Implement CRM-specific operation"""
        pass


# ============================================================================
# CONCRETE TOOL IMPLEMENTATIONS
# ============================================================================

class SearchContactsTool(CRMTool):
    """Search for contacts by name or phone"""

    SPEC = ToolSpec(
        id="search_contacts",
        name="Search Contacts",
        description="Search for contacts by name, email, or phone",
        category=ToolCategory.CRM,
        tool_type=ToolType.SEARCH,
        parameters=[
            ToolParameter("query", "string", "Search query (name, email, or phone)", required=True),
            ToolParameter("limit", "number", "Maximum results to return", required=False, default=10),
        ],
        output_schema={
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "email": {"type": "string"},
                            "phone": {"type": "string"},
                        }
                    }
                },
                "total": {"type": "number"},
            }
        },
        tags=["contacts", "search"],
    )

    def __init__(self):
        super().__init__(self.SPEC)

    async def _execute_crm_operation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search contacts in database"""
        # This would be implemented with actual database query
        return {
            "results": [],
            "total": 0,
        }


class CreateContactTool(CRMTool):
    """Create a new contact"""

    SPEC = ToolSpec(
        id="create_contact",
        name="Create Contact",
        description="Create a new contact in CRM",
        category=ToolCategory.CRM,
        tool_type=ToolType.ACTION,
        parameters=[
            ToolParameter("first_name", "string", "Contact first name", required=True),
            ToolParameter("last_name", "string", "Contact last name", required=True),
            ToolParameter("phone", "string", "Contact phone number", required=True),
            ToolParameter("email", "string", "Contact email", required=False),
            ToolParameter("notes", "string", "Additional notes", required=False),
        ],
        output_schema={
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "phone": {"type": "string"},
                "email": {"type": "string"},
                "created_at": {"type": "string"},
            }
        },
        tags=["contacts", "create"],
    )

    def __init__(self):
        super().__init__(self.SPEC)

    async def _execute_crm_operation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create contact in database"""
        # This would be implemented with actual database operation
        return {
            "id": "contact_123",
            "first_name": params.get("first_name"),
            "last_name": params.get("last_name"),
            "phone": params.get("phone"),
            "email": params.get("email"),
            "created_at": datetime.utcnow().isoformat(),
        }


class UpdateContactTool(CRMTool):
    """Update contact information"""

    SPEC = ToolSpec(
        id="update_contact",
        name="Update Contact",
        description="Update existing contact information",
        category=ToolCategory.CRM,
        tool_type=ToolType.ACTION,
        parameters=[
            ToolParameter("contact_id", "string", "Contact ID to update", required=True),
            ToolParameter("first_name", "string", "Updated first name", required=False),
            ToolParameter("last_name", "string", "Updated last name", required=False),
            ToolParameter("phone", "string", "Updated phone number", required=False),
            ToolParameter("email", "string", "Updated email", required=False),
            ToolParameter("notes", "string", "Updated notes", required=False),
        ],
        output_schema={
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "updated_at": {"type": "string"},
            }
        },
        tags=["contacts", "update"],
    )

    def __init__(self):
        super().__init__(self.SPEC)

    async def _execute_crm_operation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update contact in database"""
        return {
            "id": params.get("contact_id"),
            "updated_at": datetime.utcnow().isoformat(),
        }


class CreateDealTool(CRMTool):
    """Create a new sales deal"""

    SPEC = ToolSpec(
        id="create_deal",
        name="Create Deal",
        description="Create a new sales deal/opportunity",
        category=ToolCategory.CRM,
        tool_type=ToolType.ACTION,
        parameters=[
            ToolParameter("contact_id", "string", "Contact ID", required=True),
            ToolParameter("name", "string", "Deal name", required=True),
            ToolParameter("amount", "number", "Deal amount", required=False),
            ToolParameter("stage", "string", "Sales stage", required=True),
            ToolParameter("description", "string", "Deal description", required=False),
        ],
        output_schema={
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "amount": {"type": "number"},
                "stage": {"type": "string"},
                "created_at": {"type": "string"},
            }
        },
        tags=["deals", "create"],
    )

    def __init__(self):
        super().__init__(self.SPEC)

    async def _execute_crm_operation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create deal in database"""
        return {
            "id": "deal_123",
            "name": params.get("name"),
            "amount": params.get("amount"),
            "stage": params.get("stage"),
            "created_at": datetime.utcnow().isoformat(),
        }


class SearchKnowledgeTool(Tool):
    """Search knowledge base for information"""

    SPEC = ToolSpec(
        id="search_knowledge",
        name="Search Knowledge Base",
        description="Search knowledge base articles and FAQs",
        category=ToolCategory.KNOWLEDGE,
        tool_type=ToolType.SEARCH,
        parameters=[
            ToolParameter("query", "string", "Search query", required=True),
            ToolParameter("limit", "number", "Maximum results", required=False, default=5),
        ],
        output_schema={
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "title": {"type": "string"},
                            "content": {"type": "string"},
                            "relevance": {"type": "number"},
                        }
                    }
                },
                "total": {"type": "number"},
            }
        },
        tags=["knowledge", "search"],
    )

    def __init__(self):
        super().__init__(self.SPEC)

    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Execute knowledge search"""
        is_valid, error = self.validate_parameters(params)
        if not is_valid:
            return ToolResult(
                tool_id=self.spec.id,
                success=False,
                output={},
                error=error,
            )

        try:
            start_time = datetime.utcnow()
            # This would be implemented with actual knowledge base search
            output = {"results": [], "total": 0}
            execution_time = (datetime.utcnow() - start_time).total_seconds()

            return ToolResult(
                tool_id=self.spec.id,
                success=True,
                output=output,
                execution_time=execution_time,
            )
        except Exception as e:
            logger.error(f"Knowledge search failed: {e}")
            return ToolResult(
                tool_id=self.spec.id,
                success=False,
                output={},
                error=str(e),
            )


class ToolRegistry:
    """Registry of available tools"""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.specs: Dict[str, ToolSpec] = {}
        self.rate_limits: Dict[str, int] = {}  # tool_id -> calls in current minute
        self._initialize_default_tools()

    def _initialize_default_tools(self) -> None:
        """Initialize default tools"""
        tools = [
            SearchContactsTool(),
            CreateContactTool(),
            UpdateContactTool(),
            CreateDealTool(),
            SearchKnowledgeTool(),
        ]

        for tool in tools:
            self.register_tool(tool)

    def register_tool(self, tool: Tool) -> None:
        """Register a tool"""
        self.tools[tool.spec.id] = tool
        self.specs[tool.spec.id] = tool.spec
        self.rate_limits[tool.spec.id] = 0

    def get_tool(self, tool_id: str) -> Optional[Tool]:
        """Get tool by ID"""
        return self.tools.get(tool_id)

    def get_spec(self, tool_id: str) -> Optional[ToolSpec]:
        """Get tool specification"""
        return self.specs.get(tool_id)

    def list_tools(self, category: Optional[ToolCategory] = None) -> List[ToolSpec]:
        """List available tools"""
        specs = list(self.specs.values())
        if category:
            specs = [s for s in specs if s.category == category]
        return specs

    async def execute_tool(
        self,
        tool_id: str,
        params: Dict[str, Any],
        org_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
    ) -> ToolResult:
        """Execute a tool"""
        tool = self.get_tool(tool_id)
        if not tool:
            return ToolResult(
                tool_id=tool_id,
                success=False,
                output={},
                error=f"Tool not found: {tool_id}",
            )

        # Check rate limits
        if tool.spec.rate_limit:
            if self.rate_limits.get(tool_id, 0) >= tool.spec.rate_limit:
                return ToolResult(
                    tool_id=tool_id,
                    success=False,
                    output={},
                    error=f"Rate limit exceeded for tool {tool_id}",
                )
            self.rate_limits[tool_id] += 1

        # Execute tool
        result = await tool.execute(params)

        # Log execution
        audit_log = ToolAuditLog(
            tool_id=tool_id,
            org_id=org_id or UUID("00000000-0000-0000-0000-000000000000"),
            user_id=user_id,
            input_params=params,
            output=result.output,
            status="success" if result.success else "failed",
            reason=result.error,
        )
        logger.info(f"Tool execution audit: {audit_log.tool_id} - {audit_log.status}")

        return result


# Global tool registry
_registry = None


def get_tool_registry() -> ToolRegistry:
    """Get or create global tool registry"""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry
