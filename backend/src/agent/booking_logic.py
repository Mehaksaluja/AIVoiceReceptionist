"""Shared booking tool logic — used by LangChain tools and Vapi webhooks."""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import re

from src.agent.prompts import (
    INTAKE_PLACEHOLDER_NAME,
    INTAKE_PLACEHOLDER_PHONE,
    INTAKE_PLACEHOLDER_REASON,
)
from src.config import settings
from src.models.booking import TimeSlot
from src.services.google_service import (
    append_sheet_row,
    create_calendar_event,
    ensure_sheet_header,
    get_busy_intervals,
    is_slot_free,
)
from src.services.session_store import store

IST = ZoneInfo("Asia/Kolkata")


def format_display(dt: datetime) -> str:
    return dt.strftime("%A, %B %d at %I:%M %p")


def parse_preference(preferred_date: str | None, preferred_time: str | None) -> datetime:
    """Best-effort parse of natural preferences into a concrete datetime (IST)."""
    now = datetime.now(IST)
    weekday_names = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    if preferred_date:
        lowered = preferred_date.strip().lower()
        if "today" in lowered:
            base = now
        elif "tomorrow" in lowered:
            base = now + timedelta(days=1)
        else:
            matched_day = next((name for name in weekday_names if name in lowered), None)
            if matched_day is not None:
                target = weekday_names[matched_day]
                days_ahead = (target - now.weekday()) % 7
                if days_ahead == 0 and ("next" in lowered or now.hour >= settings.clinic_close_hour):
                    days_ahead = 7
                base = now + timedelta(days=days_ahead)
            else:
                try:
                    parsed = datetime.fromisoformat(preferred_date)
                    base = parsed.replace(tzinfo=IST) if parsed.tzinfo is None else parsed.astimezone(IST)
                except ValueError:
                    base = now + timedelta(days=1)
    else:
        base = now + timedelta(days=1)

    # No time given → start from clinic open (or next half-hour if today)
    hour, minute = settings.clinic_open_hour, 0
    if not preferred_time and preferred_date and "today" in preferred_date.strip().lower():
        bump_minutes = 30 - (now.minute % 30) if now.minute % 30 else 30
        bump = now + timedelta(minutes=bump_minutes)
        hour, minute = bump.hour, bump.minute
        if hour < settings.clinic_open_hour:
            hour, minute = settings.clinic_open_hour, 0

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
                minute = 0
        except ValueError:
            hour, minute = settings.clinic_open_hour, 0

    return base.replace(hour=hour, minute=minute, second=0, microsecond=0)


def _clinic_day_bounds(day: datetime) -> tuple[datetime, datetime]:
    """Clinic hours for the given calendar day (IST)."""
    day_local = day.astimezone(IST)
    open_at = day_local.replace(
        hour=settings.clinic_open_hour,
        minute=0,
        second=0,
        microsecond=0,
    )
    close_at = day_local.replace(
        hour=settings.clinic_close_hour,
        minute=0,
        second=0,
        microsecond=0,
    )
    return open_at, close_at


def _generate_day_slots(day: datetime, duration_minutes: int) -> list[datetime]:
    open_at, close_at = _clinic_day_bounds(day)
    slots: list[datetime] = []
    current = open_at
    while current + timedelta(minutes=duration_minutes) <= close_at:
        slots.append(current)
        current += timedelta(minutes=duration_minutes)
    return slots


def _find_available_slots(
    preferred: datetime,
    duration_minutes: int,
    *,
    max_results: int = 2,
) -> list[datetime]:
    open_at, close_at = _clinic_day_bounds(preferred)
    busy = get_busy_intervals(open_at, close_at)

    candidates = _generate_day_slots(preferred, duration_minutes)
    free = [slot for slot in candidates if is_slot_free(slot, duration_minutes, busy)]

    # Prefer slots at/after requested time, then closest alternatives
    def sort_key(slot: datetime) -> tuple[int, float]:
        after = 0 if slot >= preferred else 1
        return (after, abs((slot - preferred).total_seconds()))

    free.sort(key=sort_key)
    return free[:max_results]


_E164 = re.compile(r"^\+[1-9]\d{6,14}$")


def patient_is_ready(session) -> bool:
    b = session.booking
    return (
        b.name not in ("", INTAKE_PLACEHOLDER_NAME)
        and b.phone not in ("", INTAKE_PLACEHOLDER_PHONE)
        and b.reason not in ("", INTAKE_PLACEHOLDER_REASON)
    )


def run_save_patient_info(
    session_id: str,
    name: str,
    phone: str,
    reason: str,
) -> dict:
    session = store.get(session_id)
    if not session:
        return {"success": False, "error": "Session not found. Ask the user to refresh and try again."}

    clean_name = (name or "").strip()
    clean_phone = (phone or "").strip().replace(" ", "")
    clean_reason = (reason or "").strip()

    if len(clean_name) < 2:
        return {"success": False, "error": "Name is too short. Ask for their full name."}
    if not _E164.match(clean_phone):
        return {
            "success": False,
            "error": "Phone must be E.164 format, e.g. +919876543210. Ask again and confirm.",
        }
    if len(clean_reason) < 3:
        return {"success": False, "error": "Reason is too short. Ask why they need an appointment."}

    updated = store.update_patient(
        session_id,
        name=clean_name,
        phone=clean_phone,
        reason=clean_reason,
    )
    if not updated:
        return {"success": False, "error": "Could not save patient details."}

    print(f"[tool] save_patient_info → {clean_name} / {clean_phone} / {clean_reason}")
    return {
        "success": True,
        "message": "Patient details saved.",
        "name": clean_name,
        "phone": clean_phone,
        "reason": clean_reason,
    }


def run_check_availability(
    preferred_date: str | None = None,
    preferred_time: str | None = None,
    session_id: str | None = None,
) -> dict:
    duration = settings.appointment_duration_minutes
    preferred = parse_preference(preferred_date, preferred_time)
    # Return more options when only a day was given; fewer when they asked for a specific time
    max_results = 2 if preferred_time else 4
    available_times = _find_available_slots(preferred, duration, max_results=max_results)

    day_label = preferred.strftime("%A, %B %d")

    if not available_times:
        result = {
            "available": False,
            "slots": [],
            "suggestion": None,
            "suggestion_iso": None,
            "preferred_day": day_label,
            "message": (
                f"No open {duration}-minute slots on {day_label}. "
                "Ask the patient for another day."
            ),
        }
        print(f"[tool] check_availability → no slots on {preferred.date()}")
    else:
        slots = [
            TimeSlot(
                datetime_iso=dt.isoformat(),
                display=format_display(dt),
                available=True,
            )
            for dt in available_times
        ]
        spoken_times = ", ".join(dt.strftime("%I:%M %p").lstrip("0") for dt in available_times)
        result = {
            "available": True,
            "slots": [s.model_dump() for s in slots],
            "suggestion": slots[0].display,
            "suggestion_iso": slots[0].datetime_iso,
            "preferred_day": day_label,
            "spoken_options": spoken_times,
            "duration_minutes": duration,
            "message": (
                f"Open slots on {day_label}: {spoken_times}. "
                f"Offer these times to the patient and ask which they prefer. "
                f"Each appointment is {duration} minutes."
            ),
        }
        print(f"[tool] check_availability → {day_label}: {spoken_times}")

    if session_id:
        store.log(
            session_id,
            "tool_called",
            "check_availability",
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            suggestion=result.get("suggestion"),
            available=result.get("available"),
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

    if not patient_is_ready(session):
        return {
            "success": False,
            "error": "Patient name, phone, and reason are not saved yet. Call save_patient_info first.",
        }

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
        else:
            dt = dt.astimezone(IST)
        display = format_display(dt)
    except ValueError:
        return {
            "success": False,
            "error": "Invalid datetime. Call check_availability and use suggestion_iso.",
        }

    # Re-check calendar so we never double-book (e.g. existing 5:00–5:30 blocks another at 5:00)
    window_start = dt - timedelta(minutes=5)
    window_end = dt + timedelta(minutes=duration_minutes + 5)
    busy = get_busy_intervals(window_start, window_end)
    if not is_slot_free(dt, duration_minutes, busy):
        return {
            "success": False,
            "error": (
                f"That time ({display}) is no longer available — another appointment overlaps. "
                "Call check_availability again and offer a different slot."
            ),
        }

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
