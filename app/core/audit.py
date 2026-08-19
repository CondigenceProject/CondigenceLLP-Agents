import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from app.core.db import db_manager
from app.core.kafka_client import kafka_manager
from app.config import settings

logger = logging.getLogger("condigence.audit")

_IN_MEMORY_AUDIT_LOGS = []


class AuditService:
    @staticmethod
    async def log_event(
        actor_id: str,
        actor_type: str,  # "AGENT" or "HUMAN"
        action: str,      # e.g., "DRAFT_INVOICE", "ROUTE_TASK", "APPROVE_EMAIL"
        details: Dict[str, Any],
        status: str = "SUCCESS",
        agent_name: Optional[str] = None
    ) -> Dict[str, Any]:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor_id": actor_id,
            "actor_type": actor_type,
            "agent_name": agent_name,
            "action": action,
            "status": status,
            "details": details,
        }

        # 1. Stream to Kafka topic for durable analytics & real-time telemetry
        await kafka_manager.publish_event(
            topic=settings.KAFKA_TOPIC_AUDIT_LOGS,
            event=record,
            key=agent_name or actor_id
        )

        # 2. Persist to MongoDB
        if db_manager.is_connected and db_manager.db is not None:
            try:
                result = await db_manager.db["audit_logs"].insert_one(record)
                record["_id"] = str(result.inserted_id)
            except Exception as e:
                logger.error(f"Failed to write audit log to MongoDB: {e}")
                _IN_MEMORY_AUDIT_LOGS.append(record)
        else:
            _IN_MEMORY_AUDIT_LOGS.append(record)

        logger.info(f"[AUDIT] [{actor_type}:{agent_name or actor_id}] -> {action} ({status})")
        return record

    @staticmethod
    async def get_logs(limit: int = 50, agent_name: Optional[str] = None) -> list:
        if db_manager.is_connected and db_manager.db is not None:
            try:
                query = {"agent_name": agent_name} if agent_name else {}
                cursor = db_manager.db["audit_logs"].find(query).sort("timestamp", -1).limit(limit)
                docs = await cursor.to_list(length=limit)
                for doc in docs:
                    doc["_id"] = str(doc["_id"])
                return docs
            except Exception as e:
                logger.error(f"Error fetching audit logs from DB: {e}")
        
        # In-memory fallback
        logs = _IN_MEMORY_AUDIT_LOGS
        if agent_name:
            logs = [l for l in logs if l.get("agent_name") == agent_name]
        return list(reversed(logs[-limit:]))


audit_service = AuditService()
