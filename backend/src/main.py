"""
AI Receptionist — FastAPI entrypoint.

Run from backend/:
  uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

API docs: http://127.0.0.1:8000/docs
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router
from src.api.vapi_routes import router as vapi_router
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
        vapi_web_configured=settings.has_vapi_web,
    )
    yield
    logger.info("shutdown")


app = FastAPI(
    title="AI Receptionist Agent",
    description="Appointment booking API — agent, Vapi webhooks, Google Calendar/Sheets.",
    version="0.3.0",
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
app.include_router(vapi_router)


@app.get("/")
async def root():
    return {
        "service": "AI Receptionist API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health():
    from src.services.google_service import google_ready, service_account_email

    return {
        "status": "ok",
        "clinic": settings.clinic_name,
        "openai_configured": settings.has_openai,
        "vapi_configured": settings.has_vapi,
        "vapi_web_configured": settings.has_vapi_web,
        "google_configured": google_ready(),
        "google_service_account": service_account_email(),
        "public_base_url": settings.public_base_url or None,
    }
