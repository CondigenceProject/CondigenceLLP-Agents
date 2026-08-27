import json
import logging
import uuid
from typing import Any, Dict
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState
from app.agents.workers.base import BaseWorkerAgent
from app.core.llm import get_llm

logger = logging.getLogger("condigence.workers.compliance")

COMPLIANCE_SYSTEM_PROMPT = """You are the Legal & Statutory Compliance Specialist Agent (ComplianceAgent) of Condigence LLP.
Your job is to evaluate MCA/ROC statutory deadlines, LLP Agreement terms, GST filings, and regulatory compliance.
Output valid JSON:
{
  "statutory_body": "MCA / ROC / GSTN / Income Tax",
  "entity": "Condigence LLP",
  "form": "e.g. Form 11, Form 8, DIR-3 KYC, GSTR-3B",
  "upcoming_deadline": "YYYY-MM-DD",
  "summary_findings": "Detailed assessment based on the user directive.",
  "status": "DOCUMENTS_PREPARED_FOR_SIGN_OFF"
}
"""


class ComplianceAgent(BaseWorkerAgent):
    def __init__(self):
        super().__init__(
            name="ComplianceAgent",
            description="Monitors statutory deadlines, MCA/ROC filings, and compliance checklists."
        )

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        goal = state.get("goal", "")
        artifacts = state.get("artifacts", {})
        logger.info(f"ComplianceAgent checking filings for: '{goal}'")
        
        filing_checklist = {
            "statutory_body": "Ministry of Corporate Affairs (MCA) / ROC",
            "entity": "Condigence LLP",
            "form": "Form 11 (Annual Return) & Form 8 (Statement of Account & Solvency)",
            "upcoming_deadline": "2026-09-30",
            "designated_partners_notified": ["Designated Partner 1", "Designated Partner 2"],
            "summary_findings": f"Reviewed compliance requirements for: {goal}",
            "status": "DOCUMENTS_PREPARED_FOR_SIGN_OFF"
        }

        try:
            llm = get_llm(temperature=0.1)
            if llm:
                resp = await llm.ainvoke([
                    SystemMessage(content=COMPLIANCE_SYSTEM_PROMPT),
                    HumanMessage(content=f"Directive: {goal}\nContext: {json.dumps(artifacts)}")
                ])
                content = resp.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                parsed = json.loads(content)
                filing_checklist.update(parsed)
        except Exception as e:
            logger.warning(f"ComplianceAgent LLM fallback: {e}")

        step_record = await self.log_action(
            action="CHECK_COMPLIANCE_STATUS",
            input_data={"goal": goal},
            output_data={"filing_checklist": filing_checklist}
        )

        approval_id = str(uuid.uuid4())[:8]

        return {
            "completed_steps": [step_record],
            "artifacts": {"compliance_filing": filing_checklist},
            "requires_approval": True,
            "pending_approval_id": approval_id,
            "approval_type": "COMPLIANCE_FILING",
            "approval_payload": filing_checklist,
            "current_agent": "AI_Supervisor",
            "next_step": None,
            "status": "AWAITING_APPROVAL",
            "summary": f"Compliance dossier prepared for {filing_checklist.get('form', 'statutory filing')} (Approval ID: {approval_id})"
        }


compliance_agent = ComplianceAgent()

