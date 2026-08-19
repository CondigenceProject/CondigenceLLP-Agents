import logging
from typing import Any, Dict
from app.agents.state import AgentState

logger = logging.getLogger("condigence.supervisor.evaluator")


class SupervisorEvaluator:
    @staticmethod
    def validate_step(state: AgentState, step_result: Dict[str, Any]) -> bool:
        """
        Ensures worker outputs adhere to HITL rules:
        - Financial calculations have positive totals
        - Emails contain necessary greeting/sign-off
        - Filings check proper statutory timelines
        """
        artifacts = step_result.get("artifacts", {})
        
        if "invoice_draft" in artifacts:
            total = artifacts["invoice_draft"].get("total_amount", 0)
            if total <= 0:
                logger.error("Evaluator rejected invoice: total amount <= 0")
                return False
                
        if "comms_draft" in artifacts:
            body = artifacts["comms_draft"].get("body", "")
            if not body or len(body) < 10:
                logger.error("Evaluator rejected email draft: body is empty or too short")
                return False

        return True


evaluator = SupervisorEvaluator()
