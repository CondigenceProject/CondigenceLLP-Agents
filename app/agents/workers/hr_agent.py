import logging
import uuid
from typing import Any, Dict
from app.agents.state import AgentState
from app.agents.workers.base import BaseWorkerAgent

logger = logging.getLogger("condigence.workers.hr")


class HRAgent(BaseWorkerAgent):
    def __init__(self):
        super().__init__(
            name="HRAgent",
            description="Manages employee leave balances, onboarding checklists, and draft payrolls."
        )

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        goal = state.get("goal", "")
        logger.info(f"HRAgent processing request: '{goal}'")
        
        payroll_draft = {
            "month": "August 2026",
            "employee_count": 8,
            "total_gross_disbursement": 480000.0,
            "statutory_deductions_tds": 24000.0,
            "net_payable": 456000.0,
            "status": "DRAFT_REQUIRES_OWNER_AUTHORIZATION"
        }

        step_record = await self.log_action(
            action="PREPARE_PAYROLL_DRAFT",
            input_data={"goal": goal},
            output_data={"payroll": payroll_draft}
        )

        approval_id = str(uuid.uuid4())[:8]

        return {
            "completed_steps": [step_record],
            "artifacts": {"payroll_draft": payroll_draft},
            "requires_approval": True,
            "pending_approval_id": approval_id,
            "approval_type": "PAYROLL",
            "approval_payload": payroll_draft,
            "current_agent": "AI_Supervisor",
            "next_step": None,
            "status": "AWAITING_APPROVAL",
            "summary": f"Payroll summary drafted for owner authorization (Approval ID: {approval_id})"
        }


hr_agent = HRAgent()
