import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.approval import ApprovalTicket, ApprovalActionRequest, ApprovalStatus, ApprovalType
from app.core.security import get_current_user_optional
from app.core.audit import audit_service
from app.integrations.communication.gmail_client import gmail_client
from app.integrations.communication.whatsapp_client import whatsapp_client
from app.agents.workers.finance_agent import finance_agent
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
        if action_req.modified_payload:
            ticket.payload = action_req.modified_payload
        ticket.status = ApprovalStatus.APPROVED
        ticket.resolved_at = datetime.now(timezone.utc)
        ticket.resolved_by = user_id
        ticket.reviewer_notes = action_req.notes

        payload = ticket.payload

        # 1. Handling MVP Proposal Approval (Gate 1 -> Gate 2 Transition)
        if ticket.approval_type == ApprovalType.MVP_PROPOSAL or ticket.approval_type == "MVP_PROPOSAL":
            email_info = payload.get("draft_email", {})
            recipient = email_info.get("recipient") or payload.get("contact_email") or "client@example.com"
            subject = email_info.get("subject", f"MVP Proposal: {payload.get('project_name', 'Client Project')}")
            body = email_info.get("body", "")

            # Dispatch approved proposal email
            await gmail_client.send_draft_email(
                to_email=recipient,
                subject=subject,
                body=body
            )

            # Option A Handoff: Trigger FinanceAgent to prepare market-standard quotation based on approved MVP
            finance_state = {
                "goal": f"Prepare market-standard quotation for approved MVP: {payload.get('project_name', 'Client Project')}",
                "task_id": ticket.task_id,
                "requester_role": "OWNER",
                "completed_steps": [],
                "artifacts": {"mvp_proposal": payload},
                "requires_approval": True,
                "messages": []
            }

            try:
                finance_res = await finance_agent.execute(finance_state)
                quote_artifact = finance_res.get("artifacts", {}).get("quotation")
                if quote_artifact:
                    quote_ticket_id = finance_res.get("pending_approval_id") or str(uuid.uuid4())[:8]
                    quote_ticket = ApprovalTicket(
                        id=quote_ticket_id,
                        task_id=ticket.task_id,
                        agent_name="FinanceAgent",
                        approval_type=ApprovalType.QUOTATION,
                        title=f"Authorize Quotation: {quote_artifact.get('project_name', 'Client Quotation')}",
                        description=f"Market-standard commercial quotation of INR {quote_artifact.get('grand_total', 0):,.2f} (incl. 18% GST).",
                        payload=quote_artifact,
                        status=ApprovalStatus.PENDING,
                        required_role="OWNER"
                    )
                    register_approval_ticket(quote_ticket)
                    logger.info(f"Generated Gate 2 Quotation Ticket {quote_ticket_id} for task {ticket.task_id}")
            except Exception as e:
                logger.error(f"Error executing FinanceAgent after MVP approval: {e}")

        # 2. Handling Commercial Quotation Approval (Gate 2 Finalization)
        elif ticket.approval_type == ApprovalType.QUOTATION or ticket.approval_type == "QUOTATION":
            recipient = payload.get("contact_email") or "client@example.com"
            project_name = payload.get("project_name", "AI System MVP")
            grand_total = payload.get("grand_total", 0)
            currency = payload.get("currency", "INR")
            
            quote_email_body = (
                f"Dear {payload.get('client_name', 'Client')},\n\n"
                f"We are pleased to provide the official commercial quotation for {project_name}.\n\n"
                f"Quotation Summary:\n"
                f"- Project: {project_name}\n"
                f"- Total Cost: {currency} {grand_total:,.2f} (incl. 18% GST)\n"
                f"- Payment Milestones: {payload.get('payment_terms', '40% Kickoff, 40% Beta Demo, 20% Final Sign-off')}\n"
                f"- Quotation Validity: {payload.get('validity_days', 30)} days\n\n"
                f"Please find the itemized rate card and milestone schedule attached.\n\n"
                f"Best regards,\nCondigence LLP Commercial & Finance Operations"
            )

            await gmail_client.send_draft_email(
                to_email=recipient,
                subject=f"Commercial Quotation & Milestone Schedule: {project_name}",
                body=quote_email_body
            )

        # 3. Standard Email Approval
        elif ticket.approval_type == ApprovalType.CLIENT_EMAIL or ticket.approval_type == "CLIENT_EMAIL":
            await gmail_client.send_draft_email(
                to_email=payload.get("recipient", "client@example.com"),
                subject=payload.get("subject", "Update from Condigence LLP"),
                body=payload.get("body", "")
            )

        # 4. Standard WhatsApp Approval
        elif ticket.approval_type == ApprovalType.WHATSAPP_MESSAGE or ticket.approval_type == "WHATSAPP_MESSAGE":
            await whatsapp_client.send_message(
                phone_number=payload.get("phone", "+910000000000"),
                message=payload.get("message", "")
            )

        await audit_service.log_event(
            actor_id=user_id,
            actor_type="HUMAN",
            action="APPROVE_TICKET",
            details={"ticket_id": ticket_id, "type": str(ticket.approval_type), "payload": ticket.payload}
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
