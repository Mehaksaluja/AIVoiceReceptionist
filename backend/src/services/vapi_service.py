"""Vapi outbound voice calls."""

from __future__ import annotations

import json
from typing import Any

import httpx

from src.agent.prompts import build_system_prompt
from src.config import settings
from src.models.booking import Session


class VapiError(Exception):
    pass


def _tool_definitions(webhook_url: str) -> list[dict[str, Any]]:
    """Transient tools that hit our public webhook."""
    return [
        {
            "type": "function",
            "function": {
                "name": "check_availability",
                "description": "Check open appointment slots for a date/time preference.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "preferred_date": {
                            "type": "string",
                            "description": 'Date preference e.g. "tomorrow", "Friday"',
                        },
                        "preferred_time": {
                            "type": "string",
                            "description": 'Time preference e.g. "5pm", "17:00"',
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session id from the system prompt",
                        },
                    },
                },
            },
            "server": {"url": webhook_url},
        },
        {
            "type": "function",
            "function": {
                "name": "book_appointment",
                "description": "Book the confirmed appointment after the patient agrees.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session id from the system prompt",
                        },
                        "datetime_iso": {
                            "type": "string",
                            "description": "ISO datetime from check_availability",
                        },
                        "duration_minutes": {
                            "type": "integer",
                            "description": "Length in minutes, default 30",
                        },
                    },
                    "required": ["session_id", "datetime_iso"],
                },
            },
            "server": {"url": webhook_url},
        },
    ]


def build_transient_assistant(session: Session, webhook_url: str) -> dict[str, Any]:
    """Inline assistant so tools always point at the current public URL (ngrok)."""
    prompt = build_system_prompt(
        patient_name=session.booking.name,
        patient_phone=session.booking.phone,
        appointment_reason=session.booking.reason,
        booking_id=session.booking.id,
        session_id=session.session_id,
    )

    first_name = session.booking.name.split()[0]
    first_message = (
        f"Hello {first_name}, I'm calling from {settings.clinic_name}. "
        f"I noticed you requested an appointment for {session.booking.reason}. "
        f"Would tomorrow at 4 PM work for you?"
    )

    return {
        "name": f"{settings.clinic_name} Receptionist",
        "firstMessage": first_message,
        "model": {
            "provider": "openai",
            "model": settings.openai_model,
            "temperature": 0.3,
            "messages": [{"role": "system", "content": prompt}],
            "tools": _tool_definitions(webhook_url),
        },
        "voice": {
            "provider": "vapi",
            "voiceId": "Elliot",
        },
        "server": {"url": webhook_url},
        "serverMessages": [
            "tool-calls",
            "status-update",
            "end-of-call-report",
        ],
    }


async def create_outbound_call(session: Session) -> dict[str, Any]:
    """Place an outbound AI call to the patient's phone."""
    if not settings.has_vapi:
        raise VapiError(
            "Vapi is not configured. Set VAPI_API_KEY, VAPI_PHONE_NUMBER_ID in .env. "
            "VAPI_ASSISTANT_ID is optional when using transient assistants."
        )

    if not settings.public_base_url:
        raise VapiError(
            "PUBLIC_BASE_URL is empty. Start ngrok and set PUBLIC_BASE_URL=https://xxxx.ngrok-free.app"
        )

    webhook_url = f"{settings.public_base_url.rstrip('/')}/api/vapi/webhook"

    payload: dict[str, Any] = {
        "phoneNumberId": settings.vapi_phone_number_id,
        "customer": {
            "number": session.booking.phone,
            "name": session.booking.name,
        },
        "metadata": {
            "session_id": session.session_id,
            "booking_id": session.booking.id,
        },
    }

    if settings.vapi_use_saved_assistant and settings.vapi_assistant_id:
        payload["assistantId"] = settings.vapi_assistant_id
        payload["assistantOverrides"] = {
            "variableValues": {
                "patientName": session.booking.name,
                "patientPhone": session.booking.phone,
                "appointmentReason": session.booking.reason,
                "bookingId": session.booking.id,
                "sessionId": session.session_id,
                "clinicName": settings.clinic_name,
            },
            "server": {"url": webhook_url},
        }
    else:
        payload["assistant"] = build_transient_assistant(session, webhook_url)

    headers = {
        "Authorization": f"Bearer {settings.vapi_api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post("https://api.vapi.ai/call", headers=headers, json=payload)

    if response.status_code >= 400:
        raise VapiError(f"Vapi call failed ({response.status_code}): {response.text}")

    data = response.json()
    print(
        f"[Vapi] Outbound call created: "
        f"{json.dumps({'id': data.get('id'), 'status': data.get('status')})}"
    )
    return data


def build_web_call_payload(session: Session) -> dict[str, Any]:
    """
    Payload for browser Web SDK (@vapi-ai/web).
    Frontend uses public key + assistant config — no PSTN / Twilio needed.
    """
    if not settings.vapi_public_key.strip():
        raise VapiError(
            "VAPI_PUBLIC_KEY missing. In Vapi Dashboard → API Keys, copy the Public Key."
        )
    if not settings.public_base_url.strip():
        raise VapiError(
            "PUBLIC_BASE_URL empty. Run ngrok http 8000 and set PUBLIC_BASE_URL in .env"
        )

    webhook_url = f"{settings.public_base_url.rstrip('/')}/api/vapi/webhook"
    assistant = build_transient_assistant(session, webhook_url)

    return {
        "public_key": settings.vapi_public_key.strip(),
        "assistant": assistant,
        "session_id": session.session_id,
        "booking_id": session.booking.id,
        "caller_display_name": settings.clinic_name,
        "caller_subtitle": "AI Receptionist",
    }
