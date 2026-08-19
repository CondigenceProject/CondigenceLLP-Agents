import logging
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.models.task import AgentTaskRequest, AgentTaskResponse, TaskStatus, TaskStep
from app.models.approval import ApprovalTicket, ApprovalType, ApprovalStatus
from app.agents.supervisor.orchestrator import agent_orchestrator
from app.api.v1.approvals import register_approval_ticket
from app.core.security import get_current_user_optional

logger = logging.getLogger("condigence.api.agents")

router = APIRouter(prefix="/agents", tags=["Agent Execution"])

# In-memory tasks store
_TASKS_DB = {}


@router.post("/run", response_model=AgentTaskResponse)
async def run_agent_task(
    req: AgentTaskRequest,
    current_user: dict = Depends(get_current_user_optional)
):
    task_id = str(uuid.uuid4())
    logger.info(f"Triggering multi-agent execution for task {task_id}: '{req.goal}'")

    initial_state = {
        "messages": [],
        "task_id": task_id,
        "goal": req.goal,
        "requester_role": req.requester_role,
        "next_step": None,
        "current_agent": "AI_CEO",
        "completed_steps": [],
        "artifacts": {},
        "requires_approval": False,
        "pending_approval_id": None,
        "approval_type": None,
        "approval_payload": None,
        "summary": None,
        "status": "PROCESSING"
    }

    try:
        final_state = await agent_orchestrator.ainvoke(initial_state)
    except Exception as e:
        logger.error(f"Execution error in LangGraph: {e}")
        raise HTTPException(status_code=500, detail=f"Agent execution error: {str(e)}")

    # Check if an approval was requested and stage it
    if final_state.get("requires_approval") and final_state.get("approval_payload"):
        app_id = final_state.get("pending_approval_id") or str(uuid.uuid4())[:8]
        ticket = ApprovalTicket(
            id=app_id,
            task_id=task_id,
            agent_name=final_state.get("current_agent") or "WorkerAgent",
            approval_type=final_state.get("approval_type", ApprovalType.GENERAL),
            title=f"Review requested for task: {req.goal[:40]}...",
            description=final_state.get("summary") or "Action staged for human approval.",
            payload=final_state.get("approval_payload", {}),
            status=ApprovalStatus.PENDING,
            required_role="OWNER"
        )
        register_approval_ticket(ticket)

    steps = [
        TaskStep(
            agent=s.get("agent", "Unknown"),
            action=s.get("action", "Unknown"),
            input_data=s.get("input_data"),
            output_data=s.get("output_data"),
            status=s.get("status", "COMPLETED")
        )
        for s in final_state.get("completed_steps", [])
    ]

    task_status = TaskStatus.AWAITING_APPROVAL if final_state.get("requires_approval") else TaskStatus.COMPLETED

    task_resp = AgentTaskResponse(
        task_id=task_id,
        goal=req.goal,
        status=task_status,
        current_agent=final_state.get("current_agent"),
        steps=steps,
        artifacts=final_state.get("artifacts", {}),
        summary=final_state.get("summary", "Task processed successfully.")
    )

    _TASKS_DB[task_id] = task_resp
    return task_resp


@router.get("/tasks", response_model=List[AgentTaskResponse])
async def list_tasks():
    return list(_TASKS_DB.values())


@router.get("/tasks/{task_id}", response_model=AgentTaskResponse)
async def get_task(task_id: str):
    if task_id not in _TASKS_DB:
        raise HTTPException(status_code=404, detail="Task not found")
    return _TASKS_DB[task_id]
