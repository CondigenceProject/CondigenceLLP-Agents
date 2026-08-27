import json
import logging
from typing import Any, Dict
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState
from app.core.audit import audit_service
from app.core.llm import get_llm

from app.core.json_util import extract_json_from_llm

logger = logging.getLogger("condigence.agents.ceo")

CEO_SYSTEM_PROMPT = """You are the AI CEO of Condigence LLP.
Your role:
1. Act as the strategic visionary and executive liaison between the Human Owners (Admin) and the Agentic Layer.
2. Analyze high-level executive requests across Operations, Finance, Compliance, Projects, HR, and Analytics.
3. Formulate clear tactical directives for the AI Supervisor to execute with specialized worker agents.
4. Always output valid JSON with the following structure:
{
  "identified_agents": ["FinanceAgent" | "CommsAgent" | "ComplianceAgent" | "ProjectAgent" | "HRAgent" | "AnalyticsAgent"],
  "reasoning": "short explanation of strategy",
  "directive": "specific instruction for the worker agents",
  "extracted_entities": {"client_name": "...", "amount": "...", "topic": "..."}
}
"""


class AICEOAgent:
    def __init__(self):
        self.name = "AI_CEO"

    async def analyze_and_plan(self, state: AgentState) -> Dict[str, Any]:
        goal = state.get("goal", "")
        requester_role = state.get("requester_role", "OWNER")
        
        logger.info(f"AI CEO processing strategic goal: '{goal}' from {requester_role}")

        plan_steps = []
        directive = f"Execute requested task: {goal}"
        reasoning = "Strategic planning"
        entities = {}

        try:
            llm = get_llm(temperature=0.1)
            if llm:
                prompt_messages = [
                    SystemMessage(content=CEO_SYSTEM_PROMPT),
                    HumanMessage(content=f"Strategic Goal: {goal}\nRequester Role: {requester_role}")
                ]
                resp = await llm.ainvoke(prompt_messages)
                parsed = extract_json_from_llm(resp.content)
                if parsed:
                    plan_steps = parsed.get("identified_agents", [])
                    directive = parsed.get("directive", directive)
                    reasoning = parsed.get("reasoning", reasoning)
                    entities = parsed.get("extracted_entities", {})
        except Exception as e:
            logger.warning(f"AI CEO LLM analysis fallback: {e}")

        if not plan_steps:
            goal_lower = goal.lower()
            if any(w in goal_lower for w in ["invoice", "gst", "bill", "expense", "payment", "p&l", "accounts"]):
                plan_steps.append("FinanceAgent")
            if any(w in goal_lower for w in ["email", "reply", "client", "whatsapp", "lead", "message", "content", "draft", "write"]):
                plan_steps.append("CommsAgent")
            if any(w in goal_lower for w in ["mca", "roc", "compliance", "filing", "statutory", "legal"]):
                plan_steps.append("ComplianceAgent")
            if any(w in goal_lower for w in ["notion", "task", "project", "deadline", "milestone", "status report"]):
                plan_steps.append("ProjectAgent")
            if any(w in goal_lower for w in ["leave", "employee", "onboarding", "payroll", "salary", "hr"]):
                plan_steps.append("HRAgent")
            if any(w in goal_lower for w in ["revenue", "analytics", "cash flow", "metrics", "chart"]):
                plan_steps.append("AnalyticsAgent")

        if not plan_steps:
            plan_steps = ["CommsAgent"]

        step_record = {
            "agent": self.name,
            "action": "STRATEGIC_PLANNING",
            "input_data": {"goal": goal, "requester_role": requester_role},
            "output_data": {
                "identified_agents": plan_steps,
                "directive": directive,
                "reasoning": reasoning,
                "entities": entities
            }
        }

        await audit_service.log_event(
            actor_id=self.name,
            actor_type="AGENT",
            agent_name=self.name,
            action="STRATEGIC_PLAN_CREATED",
            details=step_record["output_data"]
        )

        return {
            "current_agent": "AI_Supervisor",
            "next_step": plan_steps[0],
            "completed_steps": [step_record],
            "artifacts": {"strategic_plan": step_record["output_data"]},
            "status": "PROCESSING"
        }


ai_ceo = AICEOAgent()

