import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.approval import ApprovalTicket, ApprovalActionRequest, ApprovalStatus
from app.core.security import get_current_user_optional
from app.core.audit import audit_service
from app.integrations.communication.gmail_client import gmail_client
from app.integrations.communication.whatsapp_client import whatsapp_client
from app.core.db import db_manager

logger = logging.getLogger("condigence.api.approvals")

router = APIRouter(prefix="/approvals", tags=["Human-in-the-Loop Approvals"])

# In-memory store for pending approvals
_APPROVAL_TICKETS: Dict[str, ApprovalTicket] = {}


def register_approval_ticket(ticket: ApprovalTicket):
    _APPROVAL_TICKETS[ticket.id] = ticket


@router.get("", response_model=List[ApprovalTicket])
async def list_approvals(status_filter: Optional[ApprovalStatus] = None):
    tickets = list(_APPROVAL_TICKETS.values())
    if status_filter:
        tickets = [t for t in tickets if t.status == status_filter]
    return sorted(tickets, key=lambda x: x.created_at, reverse=True)


@router.get("/{ticket_id}", response_model=ApprovalTicket)
async def get_approval(ticket_id: str):
    if ticket_id not in _APPROVAL_TICKETS:
        raise HTTPException(status_code=404, detail="Approval ticket not found")
    return _APPROVAL_TICKETS[ticket_id]


@router.post("/{ticket_id}/action", response_model=ApprovalTicket)
async def handle_approval_action(
    ticket_id: str,
    action_req: ApprovalActionRequest,
    current_user: dict = Depends(get_current_user_optional)
):
    if ticket_id not in _APPROVAL_TICKETS:
        raise HTTPException(status_code=404, detail="Approval ticket not found")

    ticket = _APPROVAL_TICKETS[ticket_id]
    action = action_req.action.upper()
    user_id = current_user.get("username", "admin")

    if action == "APPROVE":
        ticket.status = ApprovalStatus.APPROVED
        ticket.resolved_at = datetime.now(timezone.utc)
        ticket.resolved_by = user_id
        ticket.reviewer_notes = action_req.notes
        
        # Execute the staged action safely now that human has approved
        if ticket.approval_type == "CLIENT_EMAIL":
            payload = ticket.payload
            await gmail_client.send_draft_email(
                to_email=payload.get("recipient", "client@example.com"),
                subject=payload.get("subject", "Update from Condigence LLP"),
                body=payload.get("body", "")
            )
        elif ticket.approval_type == "WHATSAPP_MESSAGE":
            payload = ticket.payload
            await whatsapp_client.send_message(
                phone_number=payload.get("phone", "+910000000000"),
                message=payload.get("message", "")
            )

        await audit_service.log_event(
            actor_id=user_id,
            actor_type="HUMAN",
            action="APPROVE_TICKET",
            details={"ticket_id": ticket_id, "type": ticket.approval_type, "payload": ticket.payload}
        )

    elif action == "REJECT":
        ticket.status = ApprovalStatus.REJECTED
        ticket.resolved_at = datetime.now(timezone.utc)
        ticket.resolved_by = user_id
        ticket.reviewer_notes = action_req.notes

        await audit_service.log_event(
            actor_id=user_id,
            actor_type="HUMAN",
            action="REJECT_TICKET",
            details={"ticket_id": ticket_id, "notes": action_req.notes}
        )

    elif action == "MODIFY":
        ticket.status = ApprovalStatus.MODIFIED
        if action_req.modified_payload:
            ticket.payload = action_req.modified_payload
        ticket.resolved_at = datetime.now(timezone.utc)
        ticket.resolved_by = user_id
        ticket.reviewer_notes = action_req.notes

        await audit_service.log_event(
            actor_id=user_id,
            actor_type="HUMAN",
            action="MODIFY_TICKET",
            details={"ticket_id": ticket_id, "modified_payload": action_req.modified_payload}
        )

    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use APPROVE, REJECT, or MODIFY.")

    return ticket
