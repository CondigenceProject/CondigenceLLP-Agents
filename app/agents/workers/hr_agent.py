import json
import logging
import uuid
from typing import Any, Dict
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState
from app.agents.workers.base import BaseWorkerAgent
from app.core.llm import get_llm

logger = logging.getLogger("condigence.workers.hr")

HR_SYSTEM_PROMPT = """You are the Human Resources & Payroll Specialist Agent (HRAgent) of Condigence LLP.
Your job is to process employee management requests, calculate payroll disbursements, manage leave requests, and onboarding.
Output valid JSON:
{
  "month": "Month and Year e.g. August 2026",
  "employee_count": 8,
  "total_gross_disbursement": 480000.0,
  "statutory_deductions_tds": 24000.0,
  "net_payable": 456000.0,
  "department_breakdown": {"Engineering": "3 members", "Operations": "3 members", "Design": "2 members"},
  "summary": "Short HR summary of the payroll or employee action"
}
"""


class HRAgent(BaseWorkerAgent):
    def __init__(self):
        super().__init__(
            name="HRAgent",
            description="Manages employee leave balances, onboarding checklists, and draft payrolls."
        )

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        goal = state.get("goal", "")
        artifacts = state.get("artifacts", {})
        logger.info(f"HRAgent processing request: '{goal}'")
        
        payroll_draft = {
            "month": "August 2026",
            "employee_count": 8,
            "total_gross_disbursement": 480000.0,
            "statutory_deductions_tds": 24000.0,
            "net_payable": 456000.0,
            "department_breakdown": {"Engineering": "3", "Operations": "3", "Design": "2"},
            "summary": f"Prepared payroll for: {goal}",
            "status": "DRAFT_REQUIRES_OWNER_AUTHORIZATION"
        }

        try:
            llm = get_llm(temperature=0.1)
            if llm:
                resp = await llm.ainvoke([
                    SystemMessage(content=HR_SYSTEM_PROMPT),
                    HumanMessage(content=f"Directive: {goal}\nContext: {json.dumps(artifacts)}")
                ])
                content = resp.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                parsed = json.loads(content)
                payroll_draft.update(parsed)
                payroll_draft["status"] = "DRAFT_REQUIRES_OWNER_AUTHORIZATION"
        except Exception as e:
            logger.warning(f"HRAgent LLM fallback: {e}")

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
            "summary": f"Payroll for {payroll_draft.get('month', 'current period')} (INR {payroll_draft.get('net_payable', 0):,.2f}) drafted for approval (Approval ID: {approval_id})"
        }


hr_agent = HRAgent()

