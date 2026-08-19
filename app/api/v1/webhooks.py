import logging
from typing import Any, Dict
from fastapi import APIRouter, Request, BackgroundTasks
from app.agents.supervisor.orchestrator import agent_orchestrator

logger = logging.getLogger("condigence.api.webhooks")

router = APIRouter(prefix="/webhooks", tags=["External Webhooks"])


@router.post("/gmail")
async def gmail_inbound_webhook(payload: Dict[str, Any], background_tasks: BackgroundTasks):
    logger.info(f"Received Gmail inbound notification: {payload}")
    return {"status": "ACKNOWLEDGED", "source": "gmail"}


@router.post("/whatsapp")
async def whatsapp_inbound_webhook(payload: Dict[str, Any], background_tasks: BackgroundTasks):
    logger.info(f"Received WhatsApp webhook notification: {payload}")
    return {"status": "ACKNOWLEDGED", "source": "whatsapp"}


@router.post("/n8n")
async def n8n_trigger_webhook(payload: Dict[str, Any], background_tasks: BackgroundTasks):
    logger.info(f"Received n8n scheduled trigger: {payload}")
    return {"status": "ACKNOWLEDGED", "source": "n8n"}
