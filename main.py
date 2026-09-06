import os
import uvicorn
from app.config import settings
from app.server import app

__all__ = ["app"]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", settings.PORT))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=settings.DEBUG
    )
