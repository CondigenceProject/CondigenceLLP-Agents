import logging
import uuid
from typing import Any, Dict
from app.agents.state import AgentState
from app.agents.workers.base import BaseWorkerAgent

logger = logging.getLogger("condigence.workers.finance")


class FinanceAgent(BaseWorkerAgent):
    def __init__(self):
        super().__init__(
            name="FinanceAgent",
            description="Handles Zoho Books drafting, GST calculations, and expense reconciliation."
        )

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        goal = state.get("goal", "")
        logger.info(f"FinanceAgent executing task for goal: '{goal}'")
        
        # Calculate mock GST / Invoice numbers
        base_amount = 50000.0
        gst_rate = 0.18
        gst_amount = base_amount * gst_rate
        total_amount = base_amount + gst_amount
        
        invoice_number = f"INV-2026-{str(uuid.uuid4())[:4].upper()}"
        invoice_draft = {
            "invoice_number": invoice_number,
            "client_name": "Acme Global Corp",
            "base_amount": base_amount,
            "gst_rate": "18%",
            "gst_amount": gst_amount,
            "total_amount": total_amount,
            "currency": "INR",
            "status": "DRAFT_PENDING_APPROVAL"
        }

        step_record = await self.log_action(
            action="DRAFT_INVOICE",
            input_data={"goal": goal},
            output_data={"invoice": invoice_draft}
        )

        approval_id = str(uuid.uuid4())[:8]

        # Check if next step should be CommsAgent to prepare email
        return {
            "completed_steps": [step_record],
            "artifacts": {"invoice_draft": invoice_draft},
            "current_agent": "AI_Supervisor",
            "next_step": "CommsAgent",
            "requires_approval": True,
            "pending_approval_id": approval_id,
            "approval_type": "INVOICE",
            "approval_payload": invoice_draft,
            "status": "PROCESSING",
            "summary": f"Invoice {invoice_number} drafted. Handing off to CommsAgent for email preparation."
        }


finance_agent = FinanceAgent()
