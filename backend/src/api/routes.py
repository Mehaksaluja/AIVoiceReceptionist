"""HTTP routes for text agent + voice call trigger."""

from fastapi import APIRouter, HTTPException

from src.agent.graph import run_turn, start_conversation
from src.api.schemas import (
    ActivityOut,
    CallRequest,
    ChatRequest,
    SessionResponse,
    StartSessionRequest,
    WebCallRequest,
    WebCallResponse,
)
from src.config import settings
from src.services.session_store import store
from src.services.vapi_service import VapiError, build_web_call_payload, create_outbound_call

router = APIRouter(prefix="/api")


def _session_response(session, reply: str | None = None) -> SessionResponse:
    return SessionResponse(
        session_id=session.session_id,
        booking_id=session.booking.id,
        status=session.booking.status.value,
        is_booked=session.is_booked,
        confirmed_slot=session.booking.confirmed_slot,
        vapi_call_id=session.booking.vapi_call_id,
        reply=reply,
        activity=[
            ActivityOut(
                step=e.step,
                message=e.message,
                metadata=e.metadata,
                at=e.at.isoformat(),
            )
            for e in session.activity
        ],
    )


async def _place_call(session) -> SessionResponse:
    try:
        call = await create_outbound_call(session)
    except VapiError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Failed to start call: {exc}") from exc

    call_id = call.get("id")
    if call_id:
        store.set_vapi_call(session.session_id, call_id)

    refreshed = store.get(session.session_id)
    assert refreshed is not None
    return _session_response(
        refreshed,
        reply="Calling your phone now. Answer to speak with the AI receptionist.",
    )


@router.post("/sessions", response_model=SessionResponse)
async def create_session(body: StartSessionRequest) -> SessionResponse:
    """Start a booking session (text agent, or outbound call if trigger_call=true)."""
    session = store.create(name=body.name, phone=body.phone, reason=body.reason)

    if body.trigger_call:
        if not settings.has_vapi:
            raise HTTPException(
                status_code=503,
                detail="Vapi not configured. Set VAPI_API_KEY and VAPI_PHONE_NUMBER_ID.",
            )
        return await _place_call(session)

    if not settings.has_openai:
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY not set in backend/.env",
        )

    try:
        reply = await start_conversation(session)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    session = store.get(session.session_id)
    assert session is not None
    return _session_response(session, reply=reply)


@router.post("/call", response_model=SessionResponse)
async def start_outbound_call(body: CallRequest) -> SessionResponse:
    """Create a session and immediately place a Vapi outbound call."""
    if not settings.has_vapi:
        raise HTTPException(
            status_code=503,
            detail="Vapi not configured. Set VAPI_API_KEY and VAPI_PHONE_NUMBER_ID in .env",
        )
    if not settings.public_base_url:
        raise HTTPException(
            status_code=503,
            detail="PUBLIC_BASE_URL missing. Run ngrok and set PUBLIC_BASE_URL in .env",
        )

    session = store.create(name=body.name, phone=body.phone, reason=body.reason)
    return await _place_call(session)


@router.post("/web-call", response_model=WebCallResponse)
async def start_web_call(body: WebCallRequest) -> WebCallResponse:
    """
    Start a browser voice session (mobile-style UI).
    Returns Vapi public key + transient assistant for @vapi-ai/web.
    """
    if not settings.has_vapi_web:
        raise HTTPException(
            status_code=503,
            detail=(
                "Web voice not configured. Set VAPI_PUBLIC_KEY and PUBLIC_BASE_URL in .env "
                "(ngrok required for tool webhooks)."
            ),
        )

    session = store.create(name=body.name, phone=body.phone, reason=body.reason)
    store.log(session.session_id, "web_call_ready", "Browser incoming-call UI ready")

    try:
        payload = build_web_call_payload(session)
    except VapiError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return WebCallResponse(
        session_id=payload["session_id"],
        booking_id=payload["booking_id"],
        public_key=payload["public_key"],
        assistant=payload["assistant"],
        caller_display_name=payload["caller_display_name"],
        caller_subtitle=payload["caller_subtitle"],
    )


@router.post("/sessions/{session_id}/call", response_model=SessionResponse)
async def call_existing_session(session_id: str) -> SessionResponse:
    """Trigger an outbound call for an existing session."""
    session = store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.is_booked:
        return _session_response(
            session,
            reply=f"Already booked for {session.booking.confirmed_slot}.",
        )
    return await _place_call(session)


@router.post("/chat", response_model=SessionResponse)
async def chat(body: ChatRequest) -> SessionResponse:
    """Continue the booking conversation (text mode)."""
    session = store.get(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.is_booked:
        return _session_response(
            session,
            reply=f"Your appointment is already booked for {session.booking.confirmed_slot}.",
        )

    try:
        reply = await run_turn(session, body.message)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    session = store.get(body.session_id)
    assert session is not None
    return _session_response(session, reply=reply)


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str) -> SessionResponse:
    session = store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return _session_response(session)


@router.get("/sessions")
async def list_sessions():
    sessions = store.list_sessions()
    return {
        "count": len(sessions),
        "sessions": [
            {
                "session_id": s.session_id,
                "name": s.booking.name,
                "status": s.booking.status.value,
                "is_booked": s.is_booked,
                "confirmed_slot": s.booking.confirmed_slot,
                "vapi_call_id": s.booking.vapi_call_id,
            }
            for s in sessions
        ],
    }
