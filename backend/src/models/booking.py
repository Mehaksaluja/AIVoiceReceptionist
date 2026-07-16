"""Domain models for bookings and conversation sessions."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class BookingStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Booking(BaseModel):
    """One appointment request flowing through the agent."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    phone: str
    reason: str
    status: BookingStatus = BookingStatus.PENDING
    preferred_slot: str | None = None
    confirmed_slot: str | None = None
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class TimeSlot(BaseModel):
    datetime_iso: str
    display: str
    available: bool = True


class ActivityEvent(BaseModel):
    """Structured log entry for demo / debugging."""

    step: str
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    at: datetime = Field(default_factory=_utcnow)


class Session(BaseModel):
    """In-memory chat session tied to a booking."""

    session_id: str = Field(default_factory=lambda: str(uuid4()))
    booking: Booking
    activity: list[ActivityEvent] = Field(default_factory=list)
    is_booked: bool = False
    # Serialized LangChain-style turns: {"role": "user"|"assistant", "content": "..."}
    history: list[dict[str, str]] = Field(default_factory=list)
