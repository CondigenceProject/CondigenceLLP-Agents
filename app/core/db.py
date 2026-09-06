import asyncio
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

logger = logging.getLogger("condigence.db")


class MongoDBManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    is_connected: bool = False

    async def connect(self):
        try:
            logger.info(f"Connecting to MongoDB at {settings.MONGODB_URI}...")
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000
            )
            # Ping cloud cluster with 5s timeout
            await asyncio.wait_for(self.client.admin.command("ping"), timeout=5.0)
            self.db = self.client[settings.MONGODB_DB_NAME]
            self.is_connected = True
            logger.info(f"Connected to MongoDB database: {settings.MONGODB_DB_NAME}")
        except Exception as e:
            self.is_connected = False
            logger.warning(
                f"MongoDB connection offline ({type(e).__name__}). Running in development mode with in-memory persistence."
            )

    def get_database(self) -> Optional[AsyncIOMotorDatabase]:
        return self.db

    async def disconnect(self):
        if self.client:
            logger.info("Closing MongoDB connection...")
            self.client.close()
            self.is_connected = False


db_manager = MongoDBManager()


async def get_db() -> Optional[AsyncIOMotorDatabase]:
    return db_manager.get_database()
