from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from services.ai.errors import format_ai_error


class AgentResult(BaseModel):
    success: bool
    data: dict[str, Any] = {}
    error: str | None = None
    tokens_used: int = 0


class BaseAgent(ABC):
    """Base class for all AI agents."""

    name: str = "base_agent"
    description: str = ""

    @abstractmethod
    async def run(self, context: dict[str, Any]) -> AgentResult:
        """Execute the agent with the given context."""
        ...

    def _build_prompt_context(self, context: dict[str, Any], keys: list[str]) -> str:
        parts = []
        for key in keys:
            if key in context and context[key]:
                value = context[key]
                if isinstance(value, (dict, list)):
                    import json
                    value = json.dumps(value, indent=2)
                parts.append(f"### {key.replace('_', ' ').title()}\n{value}")
        return "\n\n".join(parts)

    def _agent_error(self, exc: Exception) -> str:
        return format_ai_error(exc)
