import logging
from typing import Any, Dict
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AgentState
from app.core.audit import audit_service

logger = logging.getLogger("condigence.agents.ceo")

CEO_SYSTEM_PROMPT = """You are the AI CEO of Condigence LLP.
Your role:
1. Act as the strategic visionary and executive liaison between the Human Owners (Vishal Aryan / K.S. Tiwary) and the Agentic Layer.
2. Analyze high-level executive requests across Operations, Finance, Compliance, Projects, HR, and Analytics.
3. Formulate clear tactical directives for the AI Supervisor to execute with specialized worker agents.
4. Ensure company compliance, risk mitigation, and Human-in-the-Loop safeguards (never approve financial/legal actions autonomously).
"""


class AICEOAgent:
    def __init__(self):
        self.name = "AI_CEO"

    async def analyze_and_plan(self, state: AgentState) -> Dict[str, Any]:
        goal = state.get("goal", "")
        requester_role = state.get("requester_role", "OWNER")
        
        logger.info(f"AI CEO processing strategic goal: '{goal}' from {requester_role}")

        # Determine departments involved based on intent
        goal_lower = goal.lower()
        plan_steps = []
        
        if any(w in goal_lower for w in ["invoice", "gst", "bill", "expense", "payment", "p&l", "accounts"]):
            plan_steps.append("FinanceAgent")
        if any(w in goal_lower for w in ["email", "reply", "client", "whatsapp", "lead", "message"]):
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
            # Default to Operations / Comms
            plan_steps = ["CommsAgent"]

        step_record = {
            "agent": self.name,
            "action": "STRATEGIC_PLANNING",
            "input_data": {"goal": goal, "requester_role": requester_role},
            "output_data": {"identified_agents": plan_steps, "directive": f"Execute plan across: {', '.join(plan_steps)}"}
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
            "status": "PROCESSING"
        }


ai_ceo = AICEOAgent()
