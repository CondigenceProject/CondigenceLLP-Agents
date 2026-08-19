"""
Communication integrations: Gmail and WhatsApp.
"""
from app.integrations.communication.gmail_client import gmail_client
from app.integrations.communication.whatsapp_client import whatsapp_client

__all__ = ["gmail_client", "whatsapp_client"]
