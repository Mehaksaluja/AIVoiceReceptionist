"""
AI Receptionist — FastAPI entrypoint.

Run from backend/:
  uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router
from src.config import settings

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info(
        "startup",
        clinic=settings.clinic_name,
        env=settings.app_env,
        openai_configured=settings.has_openai,
        vapi_configured=settings.has_vapi,
    )
    yield
    logger.info("shutdown")


app = FastAPI(
    title="AI Receptionist Agent",
    description="Appointment booking agent with tool calling (text first, voice later).",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "clinic": settings.clinic_name,
        "openai_configured": settings.has_openai,
        "vapi_configured": settings.has_vapi,
    }
