"""
WhatsApp Cloud API integration client.
"""
import logging
from typing import Any, Dict
from app.config import settings

logger = logging.getLogger("condigence.integrations.whatsapp")


class WhatsAppClient:
    def __init__(self):
        self.api_token = settings.WHATSAPP_API_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID

    async def send_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        logger.info(f"[APPROVED ACTION] Sending WhatsApp message to {phone_number}: '{message[:30]}...'")
        return {"status": "DELIVERED", "wa_id": "mock_wa_123", "to": phone_number}


whatsapp_client = WhatsAppClient()
