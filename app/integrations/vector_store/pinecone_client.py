"""
Pinecone Vector Database client for Company SOP and Policy RAG.
"""
import logging
from typing import List, Dict, Any
from app.config import settings

logger = logging.getLogger("condigence.integrations.pinecone")


class PineconeRAGClient:
    def __init__(self):
        self.api_key = settings.PINECONE_API_KEY
        self.index_name = settings.PINECONE_INDEX_NAME

    async def query_sop(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        logger.info(f"Querying Pinecone SOP Index for: '{query}'")
        return [
            {
                "title": "LLP Statutory Compliance Policy 2026",
                "text": "All MCA Form 8 and Form 11 filings require prior sign-off by both designated partners before submission.",
                "score": 0.94
            },
            {
                "title": "Invoicing & Payment Policy",
                "text": "All outgoing invoices must include 18% GST calculation and bank transfer details.",
                "score": 0.89
            }
        ]


pinecone_client = PineconeRAGClient()
