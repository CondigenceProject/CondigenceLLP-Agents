from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    ROUTED = "ROUTED"
    PROCESSING = "PROCESSING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AgentTaskRequest(BaseModel):
    goal: str = Field(..., description="High-level goal or instruction from the user/owner")
    requester_role: str = Field(default="OWNER", description="Role initiating the request")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context parameters")


class TaskStep(BaseModel):
    agent: str
    action: str
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    status: str = "COMPLETED"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentTaskResponse(BaseModel):
    task_id: str
    goal: str
    status: TaskStatus
    current_agent: Optional[str] = None
    steps: List[TaskStep] = Field(default_factory=list)
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    summary: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
