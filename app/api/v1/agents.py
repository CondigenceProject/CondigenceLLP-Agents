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

    # Stage approvals for all generated sensitive artifacts
    artifacts = final_state.get("artifacts", {})
    if "invoice_draft" in artifacts:
        inv = artifacts["invoice_draft"]
        inv_id = str(uuid.uuid4())[:8]
        ticket = ApprovalTicket(
            id=inv_id,
            task_id=task_id,
            agent_name="FinanceAgent",
            approval_type=ApprovalType.INVOICE,
            title=f"Authorize Invoice {inv.get('invoice_number')} for {inv.get('client_name', 'Client')}",
            description=f"Draft invoice of {inv.get('currency', 'INR')} {inv.get('total_amount', 0):,.2f} prepared for {inv.get('client_name')}.",
            payload=inv,
            status=ApprovalStatus.PENDING,
            required_role="OWNER"
        )
        register_approval_ticket(ticket)

    if "comms_draft" in artifacts:
        comms = artifacts["comms_draft"]
        comms_id = final_state.get("pending_approval_id") or str(uuid.uuid4())[:8]
        ticket = ApprovalTicket(
            id=comms_id,
            task_id=task_id,
            agent_name="CommsAgent",
            approval_type=ApprovalType.CLIENT_EMAIL,
            title=f"Approve Email: {comms.get('subject', 'Client Communication')[:45]}",
            description=f"Email drafted to {comms.get('recipient', 'client@example.com')}.",
            payload=comms,
            status=ApprovalStatus.PENDING,
            required_role="OWNER"
        )
        register_approval_ticket(ticket)

    if "compliance_filing" in artifacts:
        comp = artifacts["compliance_filing"]
        comp_id = str(uuid.uuid4())[:8]
        ticket = ApprovalTicket(
            id=comp_id,
            task_id=task_id,
            agent_name="ComplianceAgent",
            approval_type=ApprovalType.COMPLIANCE_FILING,
            title=f"Sign-off on Statutory Filing: {comp.get('form', 'Compliance Form')}",
            description=f"Statutory filing for {comp.get('statutory_body', 'MCA/ROC')}.",
            payload=comp,
            status=ApprovalStatus.PENDING,
            required_role="OWNER"
        )
        register_approval_ticket(ticket)

    if "payroll_draft" in artifacts:
        pay = artifacts["payroll_draft"]
        pay_id = str(uuid.uuid4())[:8]
        ticket = ApprovalTicket(
            id=pay_id,
            task_id=task_id,
            agent_name="HRAgent",
            approval_type=ApprovalType.PAYROLL,
            title=f"Disbursement Approval: Payroll {pay.get('month', '')}",
            description=f"Payroll disbursement of INR {pay.get('net_payable', 0):,.2f}.",
            payload=pay,
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
    return sorted(_TASKS_DB.values(), key=lambda x: x.created_at, reverse=True)



@router.get("/tasks/{task_id}", response_model=AgentTaskResponse)
async def get_task(task_id: str):
    if task_id not in _TASKS_DB:
        raise HTTPException(status_code=404, detail="Task not found")
    return _TASKS_DB[task_id]
