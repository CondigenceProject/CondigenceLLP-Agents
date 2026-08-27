import json
import logging
import uuid
from typing import Any, Dict
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState
from app.agents.workers.base import BaseWorkerAgent
from app.core.llm import get_llm

logger = logging.getLogger("condigence.workers.finance")

FINANCE_SYSTEM_PROMPT = """You are the Finance & Tax Specialist Agent (FinanceAgent) of Condigence LLP.
Your job is to analyze billing, invoice requests, and financial directives to prepare structured invoice drafts.
Output valid JSON:
{
  "client_name": "Extracted or inferred client name (e.g. Acme Corp)",
  "base_amount": 50000.0,
  "currency": "INR",
  "items": [{"description": "Service description", "amount": 50000.0}],
  "hand_off_to_comms": true
}
"""


class FinanceAgent(BaseWorkerAgent):
    def __init__(self):
        super().__init__(
            name="FinanceAgent",
            description="Handles Zoho Books drafting, GST calculations, and expense reconciliation."
        )

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        goal = state.get("goal", "")
        artifacts = state.get("artifacts", {})
        logger.info(f"FinanceAgent executing task for goal: '{goal}'")
        
        client_name = "Acme Global Corp"
        base_amount = 50000.0
        currency = "INR"
        hand_off_to_comms = True
        
        try:
            llm = get_llm(temperature=0.1)
            if llm:
                resp = await llm.ainvoke([
                    SystemMessage(content=FINANCE_SYSTEM_PROMPT),
                    HumanMessage(content=f"Directive: {goal}\nContext: {json.dumps(artifacts)}")
                ])
                content = resp.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                parsed = json.loads(content)
                client_name = parsed.get("client_name", client_name)
                base_amount = float(parsed.get("base_amount", base_amount))
                currency = parsed.get("currency", "INR")
                hand_off_to_comms = parsed.get("hand_off_to_comms", True)
        except Exception as e:
            logger.warning(f"FinanceAgent LLM fallback: {e}")

        gst_rate = 0.18
        gst_amount = round(base_amount * gst_rate, 2)
        total_amount = round(base_amount + gst_amount, 2)
        invoice_number = f"INV-2026-{str(uuid.uuid4())[:4].upper()}"

        invoice_draft = {
            "invoice_number": invoice_number,
            "client_name": client_name,
            "base_amount": base_amount,
            "gst_rate": "18%",
            "gst_amount": gst_amount,
            "total_amount": total_amount,
            "currency": currency,
            "status": "DRAFT_PENDING_APPROVAL"
        }

        step_record = await self.log_action(
            action="DRAFT_INVOICE",
            input_data={"goal": goal},
            output_data={"invoice": invoice_draft}
        )

        approval_id = str(uuid.uuid4())[:8]

        next_step = "CommsAgent" if hand_off_to_comms else None

        return {
            "completed_steps": [step_record],
            "artifacts": {"invoice_draft": invoice_draft},
            "current_agent": "AI_Supervisor",
            "next_step": next_step,
            "requires_approval": True,
            "pending_approval_id": approval_id,
            "approval_type": "INVOICE",
            "approval_payload": invoice_draft,
            "status": "PROCESSING" if next_step else "AWAITING_APPROVAL",
            "summary": f"Invoice {invoice_number} ({currency} {total_amount:,.2f}) drafted for {client_name}."
        }


finance_agent = FinanceAgent()

