"""
Workflow bridge for n8n cron schedules and deterministic workflows.
"""
import logging
from typing import Any, Dict
import httpx
from app.config import settings

logger = logging.getLogger("condigence.workflows.n8n")


class N8NBridge:
    def __init__(self):
        self.webhook_base = settings.N8N_WEBHOOK_URL

    async def trigger_workflow(self, workflow_name: str, payload: Dict[str, Any]) -> bool:
        url = f"{self.webhook_base}{workflow_name}"
        logger.info(f"Triggering n8n workflow at {url}")
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.post(url, json=payload)
                return res.status_code in [200, 201, 202]
        except Exception as e:
            logger.warning(f"Could not reach n8n instance: {e}. Non-blocking.")
            return False


n8n_bridge = N8NBridge()
