"""
Gmail and WhatsApp Cloud API clients.
"""
import logging
from typing import Any, Dict
from app.config import settings

logger = logging.getLogger("condigence.integrations.comm")


class GmailClient:
    async def send_draft_email(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        logger.info(f"[APPROVED ACTION] Sending email via Gmail API to {to_email}: '{subject}'")
        return {"status": "SENT", "message_id": "mock_gmail_msg_987", "to": to_email}


class WhatsAppClient:
    async def send_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        logger.info(f"[APPROVED ACTION] Sending WhatsApp message to {phone_number}")
        return {"status": "DELIVERED", "wa_id": "mock_wa_123"}


gmail_client = GmailClient()
whatsapp_client = WhatsAppClient()
