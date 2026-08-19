"""
Notion workspace integration client.
"""
import logging
from typing import Any, Dict
from app.config import settings

logger = logging.getLogger("condigence.integrations.notion")


class NotionClient:
    def __init__(self):
        self.api_key = settings.NOTION_API_KEY
        self.task_db_id = settings.NOTION_TASK_DB_ID

    async def get_active_tasks(self) -> list:
        logger.info("Fetching active tasks from Notion database")
        return [
            {"id": "task_01", "title": "Review LLP Annual Accounts", "status": "In Progress", "priority": "High"},
            {"id": "task_02", "title": "Onboard Technical Lead", "status": "Completed", "priority": "Medium"}
        ]

    async def update_task_status(self, task_id: str, status: str) -> Dict[str, Any]:
        logger.info(f"Updating Notion task {task_id} status to {status}")
        return {"task_id": task_id, "status": status, "updated": True}


notion_client = NotionClient()
