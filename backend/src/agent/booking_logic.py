"""Shared booking tool logic — used by LangChain tools and Vapi webhooks."""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from src.models.booking import TimeSlot
from src.services.google_service import (
    append_sheet_row,
    create_calendar_event,
    ensure_sheet_header,
)
from src.services.session_store import store

IST = ZoneInfo("Asia/Kolkata")


def format_display(dt: datetime) -> str:
    return dt.strftime("%A, %B %d at %I:%M %p")


def parse_preference(preferred_date: str | None, preferred_time: str | None) -> datetime:
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


def run_check_availability(
    preferred_date: str | None = None,
    preferred_time: str | None = None,
    session_id: str | None = None,
) -> dict:
    primary = parse_preference(preferred_date, preferred_time)
    alt = primary + timedelta(hours=1)

    slots = [
        TimeSlot(
            datetime_iso=primary.isoformat(),
            display=format_display(primary),
            available=True,
        ),
        TimeSlot(
            datetime_iso=alt.isoformat(),
            display=format_display(alt),
            available=True,
        ),
    ]

    result = {
        "available": True,
        "slots": [s.model_dump() for s in slots],
        "suggestion": slots[0].display,
        "suggestion_iso": slots[0].datetime_iso,
    }

    print(f"[tool] check_availability → {result['suggestion']}")
    if session_id:
        store.log(
            session_id,
            "tool_called",
            "check_availability",
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            suggestion=result["suggestion"],
        )

    return result


def run_book_appointment(
    session_id: str,
    datetime_iso: str,
    duration_minutes: int = 30,
) -> dict:
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
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=IST)
        display = format_display(dt.astimezone(IST))
    except ValueError:
        dt = datetime.now(IST) + timedelta(days=1)
        display = datetime_iso

    store.log(
        session_id,
        "tool_called",
        "book_appointment",
        datetime_iso=datetime_iso,
        duration_minutes=duration_minutes,
    )

    # ── Google Calendar ─────────────────────────────────────
    cal = create_calendar_event(
        title=f"{session.booking.reason} — {session.booking.name}",
        start=dt,
        duration_minutes=duration_minutes,
        description=(
            f"Phone: {session.booking.phone}\n"
            f"Reason: {session.booking.reason}\n"
            f"Booking ID: {session.booking.id}\n"
            f"Session ID: {session.session_id}"
        ),
    )
    store.log(
        session_id,
        "calendar_updated",
        "Calendar event created" if not cal.get("mock") else "Mock calendar event created",
        event_id=cal.get("event_id"),
        html_link=cal.get("html_link"),
        mock=cal.get("mock"),
    )

    # ── Google Sheets ───────────────────────────────────────
    try:
        ensure_sheet_header()
    except Exception as exc:  # noqa: BLE001
        print(f"[Sheets] Header check skipped: {exc}")

    sheet = append_sheet_row(
        [
            datetime.now(timezone.utc).isoformat(),
            session.booking.name,
            session.booking.phone,
            session.booking.reason,
            display,
            session.booking.id,
        ]
    )
    store.log(
        session_id,
        "sheet_updated",
        "Sheet row appended" if not sheet.get("mock") else "Mock sheet row appended",
        mock=sheet.get("mock"),
    )

    # Email still mock for now
    print(f"[Email] MOCK confirmation to {session.booking.phone}")
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
        "calendar": cal,
        "sheet": {"mock": sheet.get("mock"), "updated": sheet.get("updated")},
    }
