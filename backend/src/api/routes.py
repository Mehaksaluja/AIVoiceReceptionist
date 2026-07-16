"""HTTP routes for the text agent (voice/UI come later)."""

from fastapi import APIRouter, HTTPException

from src.agent.graph import run_turn, start_conversation
from src.api.schemas import (
    ActivityOut,
    ChatRequest,
    SessionResponse,
    StartSessionRequest,
)
from src.config import settings
from src.services.session_store import store

router = APIRouter(prefix="/api")


def _session_response(session, reply: str | None = None) -> SessionResponse:
    return SessionResponse(
        session_id=session.session_id,
        booking_id=session.booking.id,
        status=session.booking.status.value,
        is_booked=session.is_booked,
        confirmed_slot=session.booking.confirmed_slot,
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


@router.post("/sessions", response_model=SessionResponse)
async def create_session(body: StartSessionRequest) -> SessionResponse:
    """Start a booking session. Agent greets and offers first slot."""
    if not settings.has_openai:
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY not set in backend/.env",
        )

    session = store.create(name=body.name, phone=body.phone, reason=body.reason)
    try:
        reply = await start_conversation(session)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    session = store.get(session.session_id)
    assert session is not None
    return _session_response(session, reply=reply)


@router.post("/chat", response_model=SessionResponse)
async def chat(body: ChatRequest) -> SessionResponse:
    """Continue the booking conversation."""
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
            }
            for s in sessions
        ],
    }
