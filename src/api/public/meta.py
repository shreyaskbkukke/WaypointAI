from __future__ import annotations

from dotenv import load_dotenv
from fastapi import APIRouter
from datetime import datetime, timezone
import os

load_dotenv()

router = APIRouter(prefix="/meta", tags=["Server Meta"])

STARTED_AT = datetime.now(timezone.utc)

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/live")
async def liveness():
    return {"live": True, "since": STARTED_AT.isoformat()}

@router.get("/version")
async def version():
    return {
        "version": os.getenv("APP_VERSION", "0.1.0"),
        "commit": os.getenv("GIT_COMMIT", "unknown"),
        "env": os.getenv("APP_ENV", "dev"),
    }

@router.get("/info")
async def info():
    return {
        "name": "Agent Builder API",
        "description": "Meta endpoints with no auth (health/live/version).",
        "uptime_seconds": int((datetime.now(timezone.utc) - STARTED_AT).total_seconds()),
    }
