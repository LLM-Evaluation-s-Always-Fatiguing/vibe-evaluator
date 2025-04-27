from typing import Any, Dict, Protocol

from pydantic import BaseModel, Field
from smolagents import OpenAIServerModel, ToolCollection


# Shared Capability Model
class Capability(BaseModel):
    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="Detailed capability description")


# Evaluation Mode Protocol
class EvaluationMode(Protocol):
    """Protocol defining the interface for an evaluation mode."""
    def run(self, model: OpenAIServerModel, tool_collection: ToolCollection) -> Dict[str, Any]:
        """Runs the evaluation process and returns the result."""
        ... 