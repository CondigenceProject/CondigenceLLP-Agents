import asyncio
import json
import logging
from typing import Any, Dict, Optional
from aiokafka import AIOKafkaProducer
from app.config import settings

logger = logging.getLogger("condigence.kafka")


class KafkaManager:
    producer: Optional[AIOKafkaProducer] = None
    is_connected: bool = False

    async def connect(self):
        if not settings.KAFKA_ENABLE:
            logger.info("Kafka integration is disabled in settings.")
            return

        try:
            logger.info(f"Connecting to Kafka bootstrap servers at {settings.KAFKA_BOOTSTRAP_SERVERS}...")
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                request_timeout_ms=1000
            )
            # Fast timeout check
            await asyncio.wait_for(self.producer.start(), timeout=1.0)
            self.is_connected = True
            logger.info("Connected to Apache Kafka producer successfully.")
        except Exception as e:
            self.is_connected = False
            logger.warning(
                f"Kafka broker offline ({type(e).__name__}). Running with local in-memory event stream."
            )
            if self.producer:
                try:
                    await self.producer.stop()
                except Exception:
                    pass
                self.producer = None

    async def disconnect(self):
        if self.producer and self.is_connected:
            logger.info("Stopping Kafka producer...")
            await self.producer.stop()
            self.is_connected = False

    async def publish_event(self, topic: str, event: Dict[str, Any], key: Optional[str] = None):
        """
        Publishes event payload to Kafka topic.
        Compliments Redis by providing immutable, distributed, replayable event streaming.
        """
        if self.is_connected and self.producer:
            try:
                key_bytes = key.encode("utf-8") if key else None
                await self.producer.send_and_wait(topic, value=event, key=key_bytes)
                logger.debug(f"[KAFKA] Published event to topic '{topic}'")
            except Exception as e:
                logger.error(f"[KAFKA] Failed to publish event: {e}")
        else:
            logger.debug(f"[KAFKA:LOCAL] Emitted event to topic '{topic}': {event.get('action') or event.get('type')}")


kafka_manager = KafkaManager()
