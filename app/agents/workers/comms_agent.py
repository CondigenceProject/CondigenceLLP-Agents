import logging
import uuid
from typing import Any, Dict
from app.agents.state import AgentState
from app.agents.workers.base import BaseWorkerAgent

logger = logging.getLogger("condigence.workers.comms")


class CommsAgent(BaseWorkerAgent):
    def __init__(self):
        super().__init__(
            name="CommsAgent",
            description="Manages business communications across Gmail, WhatsApp, and CRM lead interactions."
        )

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        goal = state.get("goal", "")
        artifacts = state.get("artifacts", {})
        
        logger.info(f"CommsAgent processing task related to: '{goal}'")
        
        # Prepare draft communication based on context or invoice artifacts
        draft_subject = "Update regarding your request with Condigence LLP"
        draft_recipient = "client@example.com"
        draft_body = (
            "Dear Client,\n\n"
            "Thank you for contacting Condigence LLP. We have processed your request.\n"
        )
        
        if "invoice_draft" in artifacts:
            inv = artifacts["invoice_draft"]
            draft_subject = f"Invoice #{inv.get('invoice_number')} from Condigence LLP"
            draft_body += f"\nPlease find attached the draft invoice for {inv.get('currency', 'INR')} {inv.get('total_amount')}.\n"

        draft_body += "\nBest regards,\nCondigence LLP Operations Team"
        
        approval_id = str(uuid.uuid4())[:8]
        approval_payload = {
            "channel": "EMAIL",
            "recipient": draft_recipient,
            "subject": draft_subject,
            "body": draft_body,
        }

        step_record = await self.log_action(
            action="DRAFT_COMMUNICATION",
            input_data={"goal": goal, "context": artifacts},
            output_data={"draft_email": approval_payload, "requires_approval": True}
        )

        return {
            "completed_steps": [step_record],
            "artifacts": {"comms_draft": approval_payload},
            "requires_approval": True,
            "pending_approval_id": approval_id,
            "approval_type": "CLIENT_EMAIL",
            "approval_payload": approval_payload,
            "current_agent": "AI_Supervisor",
            "next_step": None,
            "status": "AWAITING_APPROVAL",
            "summary": f"Comms draft ready for review (Approval ID: {approval_id})"
        }


comms_agent = CommsAgent()
