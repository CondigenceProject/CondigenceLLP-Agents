from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class AuditLogEntry(BaseModel):
    id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actor_id: str
    actor_type: str  # "AGENT" | "HUMAN"
    agent_name: Optional[str] = None
    action: str
    status: str = "SUCCESS"
    details: Dict[str, Any] = Field(default_factory=dict)
