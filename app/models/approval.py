from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ApprovalType(str, Enum):
    INVOICE = "INVOICE"
    PAYMENT = "PAYMENT"
    CLIENT_EMAIL = "CLIENT_EMAIL"
    WHATSAPP_MESSAGE = "WHATSAPP_MESSAGE"
    COMPLIANCE_FILING = "COMPLIANCE_FILING"
    PAYROLL = "PAYROLL"
    GENERAL = "GENERAL"


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"


class ApprovalTicket(BaseModel):
    id: str
    task_id: str
    agent_name: str
    approval_type: ApprovalType
    title: str
    description: str
    payload: Dict[str, Any] = Field(..., description="Draft payload e.g. invoice items, email body")
    status: ApprovalStatus = ApprovalStatus.PENDING
    required_role: str = "OWNER"
    reviewer_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None


class ApprovalActionRequest(BaseModel):
    action: str = Field(..., description="'APPROVE', 'REJECT', or 'MODIFY'")
    modified_payload: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
