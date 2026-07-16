from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from langchain_core.tools import tool

from src.models.booking import TimeSlot
from src.services.session_store import store

IST = ZoneInfo("Asia/Kolkata")


def _format_display(dt: datetime) -> str:
    return dt.strftime("%A, %B %d at %I:%M %p")


def _parse_preference(preferred_date: str | None, preferred_time: str | None) -> datetime:
    """Best-effort parse of natural preferences into a concrete datetime (IST)."""
    now = datetime.now(IST)

    if preferred_date:
        lowered = preferred_date.strip().lower()
        if "tomorrow" in lowered:
            base = now + timedelta(days=1)
        elif "friday" in lowered:
            days_ahead = (4 - now.weekday()) % 7 or 7
            base = now + timedelta(days=days_ahead)
        elif "monday" in lowered:
            days_ahead = (0 - now.weekday()) % 7 or 7
            base = now + timedelta(days=days_ahead)
        else:
            try:
                base = datetime.fromisoformat(preferred_date).replace(tzinfo=IST)
            except ValueError:
                base = now + timedelta(days=1)
    else:
        base = now + timedelta(days=1)

    hour, minute = 16, 0
    if preferred_time:
        cleaned = preferred_time.strip().lower().replace(" ", "")
        try:
            if "pm" in cleaned or "am" in cleaned:
                is_pm = "pm" in cleaned
                cleaned = cleaned.replace("pm", "").replace("am", "")
                if ":" in cleaned:
                    h, m = cleaned.split(":", 1)
                    hour, minute = int(h), int(m[:2])
                else:
                    hour, minute = int(cleaned), 0
                if is_pm and hour < 12:
                    hour += 12
                if not is_pm and hour == 12:
                    hour = 0
            elif ":" in cleaned:
                h, m = cleaned.split(":", 1)
                hour, minute = int(h), int(m[:2])
            else:
                hour = int(cleaned)
        except ValueError:
            hour, minute = 17, 0

    return base.replace(hour=hour, minute=minute, second=0, microsecond=0)


@tool
def check_availability(
    preferred_date: str | None = None,
    preferred_time: str | None = None,
) -> dict:
    """Check open appointment slots.

    Args:
        preferred_date: Date preference like "tomorrow", "Friday", or ISO date.
        preferred_time: Time preference like "5pm", "17:00".
    """
    store_log_all = True

    primary = _parse_preference(preferred_date, preferred_time)
    alt = primary + timedelta(hours=1)

    slots = [
        TimeSlot(
            datetime_iso=primary.isoformat(),
            display=_format_display(primary),
            available=True,
        ),
        TimeSlot(
            datetime_iso=alt.isoformat(),
            display=_format_display(alt),
            available=True,
        ),
    ]

    result = {
        "available": True,
        "slots": [s.model_dump() for s in slots],
        "suggestion": slots[0].display,
        "suggestion_iso": slots[0].datetime_iso,
    }

    if store_log_all:
        print(f"[tool] check_availability → {result['suggestion']}")

    return result


@tool
def book_appointment(
    session_id: str,
    datetime_iso: str,
    duration_minutes: int = 30,
) -> dict:
    """Confirm and book an appointment after the patient agrees.

    Args:
        session_id: The current session id from the system prompt.
        datetime_iso: Confirmed slot ISO datetime from check_availability.
        duration_minutes: Appointment length (default 30).
    """
    session = store.get(session_id)
    if not session:
        return {"success": False, "error": "Session not found. Ask the user to restart."}

    if session.is_booked:
        return {
            "success": True,
            "message": f"Already booked for {session.booking.confirmed_slot}",
            "confirmed_slot": session.booking.confirmed_slot,
        }

    try:
        dt = datetime.fromisoformat(datetime_iso)
        display = _format_display(dt.astimezone(IST) if dt.tzinfo else dt.replace(tzinfo=IST))
    except ValueError:
        display = datetime_iso

    store.log(
        session_id,
        "tool_called",
        "book_appointment",
        datetime_iso=datetime_iso,
        duration_minutes=duration_minutes,
    )

    print(f"[Calendar] MOCK create event: {display} for {session.booking.name}")
    print(f"[Sheets] MOCK append row: {session.booking.name} | {display}")
    print(f"[Email] MOCK confirmation to {session.booking.phone}")

    store.log(session_id, "calendar_updated", "Mock calendar event created")
    store.log(session_id, "sheet_updated", "Mock sheet row appended")
    store.log(session_id, "email_sent", "Mock confirmation email sent")

    confirmed = store.mark_confirmed(session_id, display)
    assert confirmed is not None

    return {
        "success": True,
        "message": f"Appointment confirmed for {display}",
        "confirmed_slot": display,
        "patient": confirmed.booking.name,
        "reason": confirmed.booking.reason,
        "duration_minutes": duration_minutes,
    }


TOOLS = [check_availability, book_appointment]
