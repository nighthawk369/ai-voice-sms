"""Tool routing and execution orchestration"""

import logging
import json
import re
from typing import Optional, Dict, Any, List, Tuple
from uuid import UUID
from datetime import datetime

from app.tools import get_tool_registry, ToolResult, ToolCategory
from app.orchestrator import AIOrchestrator, Intent, ConversationContext

logger = logging.getLogger(__name__)


class ToolRouter:
    """Routes intents to appropriate tools and manages tool execution"""

    # Intent to tool mapping
    INTENT_TOOL_MAP = {
        Intent.BOOKING: ["create_deal", "create_contact", "search_contacts"],
        Intent.SUPPORT: ["search_knowledge", "create_contact"],
        Intent.INFO_REQUEST: ["search_knowledge"],
        Intent.COMPLAINT: ["create_contact", "create_deal"],
        Intent.SALES: ["create_deal", "search_contacts"],
        Intent.RESCHEDULE: ["create_deal", "search_contacts"],
        Intent.CANCEL: ["search_contacts"],
    }

    def __init__(self):
        self.registry = get_tool_registry()
        self.orchestrator = AIOrchestrator()

    def get_tools_for_intent(self, intent: Intent) -> List[str]:
        """Get recommended tools for detected intent"""
        return self.INTENT_TOOL_MAP.get(intent, [])

    async def route_and_execute(
        self,
        context: ConversationContext,
        tool_id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        user_id: Optional[UUID] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Route to tool and execute based on intent and parameters

        Returns:
            Tuple of (success, result)
        """
        # If tool not specified, recommend based on intent
        if not tool_id:
            recommended_tools = self.get_tools_for_intent(context.intent)
            if not recommended_tools:
                logger.warning(f"No tools recommended for intent {context.intent}")
                return False, {"error": "No suitable tools for this request"}

            tool_id = recommended_tools[0]
            logger.info(f"Recommended tool {tool_id} for intent {context.intent}")

        # Check if tool exists
        tool = self.registry.get_tool(tool_id)
        if not tool:
            logger.error(f"Tool not found: {tool_id}")
            return False, {"error": f"Tool '{tool_id}' not found"}

        # Extract parameters from conversation if not provided
        if not params:
            params = await self._extract_parameters_from_conversation(context, tool_id)

        # Execute tool
        try:
            result = await self.registry.execute_tool(
                tool_id=tool_id,
                params=params,
                org_id=context.org_id,
                user_id=user_id,
            )

            if result.success:
                logger.info(f"Tool {tool_id} executed successfully")
                context.add_message(
                    "system",
                    f"Tool executed: {tool_id}",
                    {"tool_result": result.output}
                )
                return True, result.output
            else:
                logger.error(f"Tool {tool_id} failed: {result.error}")
                return False, {"error": result.error}

        except Exception as e:
            logger.error(f"Error executing tool {tool_id}: {e}")
            return False, {"error": str(e)}

    async def _extract_parameters_from_conversation(
        self,
        context: ConversationContext,
        tool_id: str,
    ) -> Dict[str, Any]:
        """Extract tool parameters from conversation using LLM"""
        tool_spec = self.registry.get_spec(tool_id)
        if not tool_spec:
            return {}

        # Build parameter extraction prompt
        params_desc = "\n".join([
            f"- {p.name} ({p.type}): {p.description} (required: {p.required})"
            for p in tool_spec.parameters
        ])

        prompt = f"""Based on the conversation history, extract parameters for the tool '{tool_spec.name}'.

Tool: {tool_spec.name}
Description: {tool_spec.description}

Required parameters:
{params_desc}

Conversation:
{chr(10).join([f'{msg.role}: {msg.content}' for msg in context.get_recent_messages()])}

Extract parameters and return as JSON. Only include parameters mentioned in the conversation.
If a parameter is not found, omit it."""

        try:
            response_obj = await self.orchestrator.llm_router.generate(prompt=prompt)
            content = response_obj.content

            # Try to extract JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                params = json.loads(json_match.group())
                logger.info(f"Extracted parameters: {params}")
                return params
        except Exception as e:
            logger.warning(f"Could not extract parameters: {e}")

        return {}

    async def should_execute_tool(
        self,
        context: ConversationContext,
        tool_id: str,
    ) -> Tuple[bool, Optional[str]]:
        """Determine if tool should be executed automatically"""
        tool = self.registry.get_tool(tool_id)
        if not tool:
            return False, "Tool not found"

        # Don't auto-execute action tools without explicit parameters
        if tool.spec.tool_type.value == "ACTION":
            # For now, require explicit params for actions
            return False, "Action tools require explicit parameters"

        # Query and search tools can be auto-executed
        return True, None

    async def build_tool_context_prompt(self, context: ConversationContext) -> str:
        """Build system prompt with available tools"""
        tools = self.registry.list_tools()

        tool_descriptions = []
        for tool in tools:
            params_str = ", ".join([
                f"{p.name} ({p.type})" for p in tool.parameters
            ])
            tool_descriptions.append(
                f"- {tool.name} ({tool.id}): {tool.description}\n"
                f"  Parameters: {params_str}"
            )

        return f"""You are an AI assistant with access to the following tools:

{chr(10).join(tool_descriptions)}

When appropriate, suggest using relevant tools to help the customer.
Format tool suggestions as: [TOOL_SUGGESTION: tool_id with params]"""


# Global tool router instance
_router = None


def get_tool_router() -> ToolRouter:
    """Get or create global tool router"""
    global _router
    if _router is None:
        _router = ToolRouter()
    return _router
