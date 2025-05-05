# core/agent.py
from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

class AgentStatus(str, Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class AgentSpec(BaseModel):
    goal: str
    tools: List[str] = Field(default_factory=list)
    next_agent_instructions: Optional[str] = None
    continue_chain: bool = True

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AgentResult(BaseModel):
    execution_result: Dict[str, Any] = Field(default_factory=dict)
    next_agent_spec: Optional[AgentSpec] = None
    errors: List[str] = Field(default_factory=list)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
