"""LangChain tool wrappers around shared booking logic."""

from langchain_core.tools import tool

from src.agent.booking_logic import run_book_appointment, run_check_availability


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
    return run_check_availability(preferred_date, preferred_time)


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
    return run_book_appointment(session_id, datetime_iso, duration_minutes)


TOOLS = [check_availability, book_appointment]
