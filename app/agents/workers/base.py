import logging
from typing import Any, Dict
from app.core.audit import audit_service

logger = logging.getLogger("condigence.workers.base")


class BaseWorkerAgent:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    async def log_action(
        self,
        action: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        status: str = "SUCCESS"
    ) -> Dict[str, Any]:
        record = {
            "agent": self.name,
            "action": action,
            "input_data": input_data,
            "output_data": output_data,
            "status": status,
        }
        await audit_service.log_event(
            actor_id=self.name,
            actor_type="AGENT",
            agent_name=self.name,
            action=action,
            details={"input": input_data, "output": output_data},
            status=status
        )
        return record
