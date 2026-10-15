import json
import logging
import uuid
from typing import Any, Dict, List
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState
from app.agents.workers.base import BaseWorkerAgent
from app.core.llm import get_llm
from app.core.json_util import extract_json_from_llm

logger = logging.getLogger("condigence.workers.finance")

FINANCE_QUOTATION_SYSTEM_PROMPT = """You are the Senior Commercial & Finance Specialist (FinanceAgent) of Condigence LLP.
Your job is to analyze an approved client MVP scope and generate an itemized, market-standard commercial quotation.

Market Benchmark Rates (India & Global IT benchmark):
- Senior AI & Backend Architect: ₹2,500/hr ($35/hr)
- Fullstack & Integration Engineer: ₹1,800/hr ($25/hr)
- UI/UX & Solution Designer: ₹2,000/hr ($28/hr)
- QA, DevOps & Security Engineer: ₹1,200/hr ($18/hr)

Instructions:
1. Extract client_name, project_name, and timeline_weeks from the MVP data.
2. Structure the quotation breakdown:
   - "line_items": list of roles with hours, hourly_rate, subtotal
   - "dev_subtotal": sum of line items
   - "contingency_percentage": 10
   - "contingency_amount": 10% of dev_subtotal
   - "cloud_infra_allowance": reasonable API/token & hosting budget (e.g. ₹10,000 - ₹15,000)
   - "net_amount": dev_subtotal + contingency_amount + cloud_infra_allowance
   - "gst_rate": "18%"
   - "gst_amount": 18% of net_amount
   - "grand_total": net_amount + gst_amount
   - "milestones":
     - Milestone 1 (40%): Project Kickoff & Architecture Setup
     - Milestone 2 (40%): Working Beta MVP Demo & UAT Delivery
     - Milestone 3 (20%): Final Production Handover & Sign-off

Respond ONLY in valid JSON matching this structure:
{
  "client_name": "...",
  "project_name": "...",
  "currency": "INR",
  "line_items": [
    {"role": "Senior AI & Backend Architect", "hours": 48, "hourly_rate": 2500.0, "amount": 120000.0},
    {"role": "Fullstack Integration Engineer", "hours": 36, "hourly_rate": 1800.0, "amount": 64800.0},
    {"role": "UI/UX & Solution Designer", "hours": 18, "hourly_rate": 2000.0, "amount": 36000.0},
    {"role": "QA, DevOps & Security Engineer", "hours": 18, "hourly_rate": 1200.0, "amount": 21600.0}
  ],
  "dev_subtotal": 242400.0,
  "contingency_amount": 24240.0,
  "cloud_infra_allowance": 12000.0,
  "net_amount": 278640.0,
  "gst_rate": "18%",
  "gst_amount": 50155.20,
  "grand_total": 328795.20,
  "milestones": [
    {"phase": "Milestone 1: Project Kickoff & Architecture Setup", "percentage": 40, "amount": 131518.08},
    {"phase": "Milestone 2: Working Beta MVP Demo & UAT Delivery", "percentage": 40, "amount": 131518.08},
    {"phase": "Milestone 3: Final Production Handover & Sign-off", "percentage": 20, "amount": 65759.04}
  ],
  "validity_days": 30,
  "payment_terms": "40% Advance, 40% on Beta Delivery, 20% upon Final Sign-off"
}
"""

FINANCE_INVOICE_SYSTEM_PROMPT = """You are the Finance & Tax Specialist Agent (FinanceAgent) of Condigence LLP.
Your job is to analyze billing, invoice requests, and financial directives to prepare structured invoice drafts.
Output valid JSON:
{
  "client_name": "Extracted or inferred client name (e.g. Acme Corp)",
  "base_amount": 50000.0,
  "currency": "INR",
  "items": [{"description": "Service description", "amount": 50000.0}],
  "hand_off_to_comms": false
}
"""


class FinanceAgent(BaseWorkerAgent):
    def __init__(self):
        super().__init__(
            name="FinanceAgent",
            description="Prepares market-standard commercial quotations, Zoho Books invoicing, and GST calculations."
        )

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        goal = state.get("goal", "")
        artifacts = state.get("artifacts", {})
        logger.info(f"FinanceAgent executing task for goal: '{goal}'")

        mvp_proposal = artifacts.get("mvp_proposal")
        goal_lower = goal.lower()
        is_quotation_task = bool(mvp_proposal) or any(k in goal_lower for k in ["quotation", "quote", "cost", "pricing", "commercial", "market standard"])

        if is_quotation_task:
            return await self._handle_quotation(goal, artifacts, mvp_proposal)
        else:
            return await self._handle_invoice(goal, artifacts)

    async def _handle_quotation(self, goal: str, artifacts: Dict[str, Any], mvp_proposal: Dict[str, Any] = None) -> Dict[str, Any]:
        mvp = mvp_proposal or {}
        client_name = mvp.get("client_name", "Valued Client")
        project_name = mvp.get("project_name", "AI System MVP")
        timeline_weeks = int(mvp.get("timeline_weeks", 3))

        # Calculate estimated engineering hours based on MVP features
        p0_features = mvp.get("p0_features", [])
        if p0_features:
            total_days = sum(int(f.get("effort_days", 3)) for f in p0_features)
        else:
            total_days = timeline_weeks * 5  # 5 business days per week

        total_hours = total_days * 8  # 8 hours/day

        # Market-standard role allocation
        ai_hours = round(total_hours * 0.40)
        fullstack_hours = round(total_hours * 0.30)
        design_hours = round(total_hours * 0.15)
        qa_hours = total_hours - (ai_hours + fullstack_hours + design_hours)

        rate_ai = 2500.0
        rate_fullstack = 1800.0
        rate_design = 2000.0
        rate_qa = 1200.0

        line_items = [
            {"role": "Senior AI & Backend Architect", "hours": ai_hours, "hourly_rate": rate_ai, "amount": round(ai_hours * rate_ai, 2)},
            {"role": "Fullstack Integration Engineer", "hours": fullstack_hours, "hourly_rate": rate_fullstack, "amount": round(fullstack_hours * rate_fullstack, 2)},
            {"role": "UI/UX & Solution Designer", "hours": design_hours, "hourly_rate": rate_design, "amount": round(design_hours * rate_design, 2)},
            {"role": "QA, DevOps & Security Engineer", "hours": qa_hours, "hourly_rate": rate_qa, "amount": round(qa_hours * rate_qa, 2)}
        ]

        dev_subtotal = sum(item["amount"] for item in line_items)
        contingency_amount = round(dev_subtotal * 0.10, 2)
        cloud_infra_allowance = 12000.0
        net_amount = round(dev_subtotal + contingency_amount + cloud_infra_allowance, 2)
        gst_rate = 0.18
        gst_amount = round(net_amount * gst_rate, 2)
        grand_total = round(net_amount + gst_amount, 2)

        milestones = [
            {"phase": "Milestone 1: Project Kickoff & Architecture Setup", "percentage": 40, "amount": round(grand_total * 0.40, 2)},
            {"phase": "Milestone 2: Working Beta MVP Demo & UAT Delivery", "percentage": 40, "amount": round(grand_total * 0.40, 2)},
            {"phase": "Milestone 3: Final Production Handover & Sign-off", "percentage": 20, "amount": round(grand_total * 0.20, 2)}
        ]

        quotation_data = {
            "quotation_number": f"QUO-2026-{str(uuid.uuid4())[:4].upper()}",
            "client_name": client_name,
            "project_name": project_name,
            "currency": "INR",
            "timeline_weeks": timeline_weeks,
            "line_items": line_items,
            "dev_subtotal": dev_subtotal,
            "contingency_percentage": 10,
            "contingency_amount": contingency_amount,
            "cloud_infra_allowance": cloud_infra_allowance,
            "net_amount": net_amount,
            "gst_rate": "18%",
            "gst_amount": gst_amount,
            "grand_total": grand_total,
            "milestones": milestones,
            "validity_days": 30,
            "payment_terms": "40% Advance, 40% upon Beta Delivery, 20% upon Final Sign-off",
            "status": "DRAFT_PENDING_APPROVAL"
        }

        # Try to refine with LLM
        try:
            llm = get_llm(temperature=0.1)
            if llm:
                prompt_text = (
                    f"Directive: {goal}\n"
                    f"Approved MVP Specification: {json.dumps(mvp)}\n"
                    f"Baseline Math: {json.dumps(quotation_data)}"
                )
                resp = await llm.ainvoke([
                    SystemMessage(content=FINANCE_QUOTATION_SYSTEM_PROMPT),
                    HumanMessage(content=prompt_text)
                ])
                parsed = extract_json_from_llm(resp.content)
                if parsed and isinstance(parsed, dict) and "grand_total" in parsed:
                    # Update fields while preserving quotation number
                    q_num = quotation_data["quotation_number"]
                    quotation_data.update(parsed)
                    quotation_data["quotation_number"] = q_num
                    quotation_data["currency"] = "INR"
        except Exception as e:
            logger.warning(f"FinanceAgent quotation LLM fallback: {e}")

        step_record = await self.log_action(
            action="GENERATE_MARKET_QUOTATION",
            input_data={"goal": goal, "client": client_name},
            output_data={"quotation": quotation_data}
        )

        approval_id = str(uuid.uuid4())[:8]

        return {
            "completed_steps": [step_record],
            "artifacts": {
                "quotation": quotation_data,
                "invoice_draft": {
                    "invoice_number": quotation_data.get("quotation_number"),
                    "client_name": client_name,
                    "total_amount": quotation_data.get("grand_total"),
                    "currency": "INR"
                }
            },
            "current_agent": "AI_Supervisor",
            "next_step": None,
            "requires_approval": True,
            "pending_approval_id": approval_id,
            "approval_type": "QUOTATION",
            "approval_payload": quotation_data,
            "status": "AWAITING_APPROVAL",
            "summary": f"Market-standard quotation {quotation_data.get('quotation_number')} for {client_name} (Total: ₹{quotation_data.get('grand_total', 0):,.2f} incl. 18% GST). Approval required."
        }

    async def _handle_invoice(self, goal: str, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        client_name = "Acme Global Corp"
        base_amount = 50000.0
        currency = "INR"

        try:
            llm = get_llm(temperature=0.1)
            if llm:
                resp = await llm.ainvoke([
                    SystemMessage(content=FINANCE_INVOICE_SYSTEM_PROMPT),
                    HumanMessage(content=f"Directive: {goal}\nContext: {json.dumps(artifacts)}")
                ])
                parsed = extract_json_from_llm(resp.content)
                if parsed:
                    client_name = parsed.get("client_name", client_name)
                    base_amount = float(parsed.get("base_amount", base_amount))
                    currency = parsed.get("currency", "INR")
        except Exception as e:
            logger.warning(f"FinanceAgent LLM invoice fallback: {e}")

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

        return {
            "completed_steps": [step_record],
            "artifacts": {"invoice_draft": invoice_draft},
            "current_agent": "AI_Supervisor",
            "next_step": None,
            "requires_approval": True,
            "pending_approval_id": approval_id,
            "approval_type": "INVOICE",
            "approval_payload": invoice_draft,
            "status": "AWAITING_APPROVAL",
            "summary": f"Invoice {invoice_number} ({currency} {total_amount:,.2f}) drafted for {client_name}."
        }


finance_agent = FinanceAgent()
