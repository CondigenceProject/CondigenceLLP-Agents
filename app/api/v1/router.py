from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.agents import router as agents_router
from app.api.v1.approvals import router as approvals_router
from app.api.v1.audit import router as audit_router
from app.api.v1.webhooks import router as webhooks_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(agents_router)
api_v1_router.include_router(approvals_router)
api_v1_router.include_router(audit_router)
api_v1_router.include_router(webhooks_router)
