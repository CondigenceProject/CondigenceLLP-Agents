from typing import List, Optional
from fastapi import APIRouter, Query
from app.core.audit import audit_service
from app.models.audit_log import AuditLogEntry

router = APIRouter(prefix="/audit", tags=["Audit Trail"])


@router.get("/logs", response_model=List[AuditLogEntry])
async def get_audit_logs(
    limit: int = Query(default=50, ge=1, le=200),
    agent_name: Optional[str] = Query(default=None)
):
    raw_logs = await audit_service.get_logs(limit=limit, agent_name=agent_name)
    return [
        AuditLogEntry(
            id=log.get("_id") or log.get("id"),
            timestamp=log.get("timestamp"),
            actor_id=log.get("actor_id"),
            actor_type=log.get("actor_type"),
            agent_name=log.get("agent_name"),
            action=log.get("action"),
            status=log.get("status", "SUCCESS"),
            details=log.get("details", {})
        )
        for log in raw_logs
    ]
