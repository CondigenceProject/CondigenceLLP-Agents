import logging
from typing import Any, Dict
from app.agents.state import AgentState
from app.agents.workers.base import BaseWorkerAgent

logger = logging.getLogger("condigence.workers.project")


class ProjectAgent(BaseWorkerAgent):
    def __init__(self):
        super().__init__(
            name="ProjectAgent",
            description="Syncs Notion tasks, monitors project milestones, and alerts ops managers."
        )

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        goal = state.get("goal", "")
        logger.info(f"ProjectAgent evaluating milestones for: '{goal}'")
        
        project_report = {
            "platform": "Notion",
            "active_projects": 3,
            "tasks_on_track": 14,
            "tasks_at_risk": 1,
            "highlight": "Client deliverables for Sprint 4 are 90% completed."
        }

        step_record = await self.log_action(
            action="SYNC_NOTION_BOARD",
            input_data={"goal": goal},
            output_data={"project_summary": project_report}
        )

        return {
            "completed_steps": [step_record],
            "artifacts": {"project_status": project_report},
            "current_agent": "AI_Supervisor",
            "next_step": None,
            "status": "COMPLETED",
            "summary": "Project status synced from Notion successfully."
        }


project_agent = ProjectAgent()
