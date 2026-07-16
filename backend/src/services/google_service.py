"""Google Calendar + Sheets integrations (service account)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from src.config import settings

IST = ZoneInfo("Asia/Kolkata")
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/spreadsheets",
]


def _credentials_path() -> Path:
    path = Path(settings.google_service_account_path)
    if not path.is_absolute():
        # Relative to backend/ (where uvicorn is run)
        path = Path.cwd() / path
    return path


def _has_credentials_file() -> bool:
    return _credentials_path().is_file()


def google_ready() -> bool:
    """True when service account JSON exists and at least calendar or sheet is configured."""
    return _has_credentials_file() and bool(
        settings.google_calendar_id or settings.google_sheet_id
    )


def _build_credentials():
    from google.oauth2 import service_account

    path = _credentials_path()
    if not path.is_file():
        raise FileNotFoundError(f"Google credentials not found: {path}")
    return service_account.Credentials.from_service_account_file(str(path), scopes=SCOPES)


def create_calendar_event(
    *,
    title: str,
    start: datetime,
    duration_minutes: int = 30,
    description: str = "",
) -> dict[str, Any]:
    """
    Create a Calendar event.
    Falls back to mock if credentials / calendar id missing.
    """
    if not _has_credentials_file() or not settings.google_calendar_id:
        print(f"[Calendar] MOCK create event: {title} @ {start.isoformat()}")
        return {"event_id": f"mock-event-{int(start.timestamp())}", "mock": True}

    from googleapiclient.discovery import build

    if start.tzinfo is None:
        start = start.replace(tzinfo=IST)
    end = start + timedelta(minutes=duration_minutes)

    body = {
        "summary": title,
        "description": description,
        "start": {
            "dateTime": start.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
    }

    creds = _build_credentials()
    service = build("calendar", "v3", credentials=creds, cache_discovery=False)
    event = (
        service.events()
        .insert(calendarId=settings.google_calendar_id, body=body)
        .execute()
    )

    event_id = event.get("id", "")
    html_link = event.get("htmlLink", "")
    print(f"[Calendar] Created event {event_id} → {html_link}")
    return {"event_id": event_id, "html_link": html_link, "mock": False}


def append_sheet_row(row: list[Any]) -> dict[str, Any]:
    """
    Append one row to the configured Google Sheet.
    Falls back to mock if credentials / sheet id missing.
    """
    if not _has_credentials_file() or not settings.google_sheet_id.strip():
        print(f"[Sheets] MOCK append row: {row}")
        return {"updated": False, "mock": True}

    from googleapiclient.discovery import build

    creds = _build_credentials()
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)
    result = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=settings.google_sheet_id.strip(),
            range="Sheet1!A:F",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": [row]},
        )
        .execute()
    )

    updated = result.get("updates", {}).get("updatedCells", 0)
    print(f"[Sheets] Appended row ({updated} cells)")
    return {"updated": True, "mock": False, "result": result}


def ensure_sheet_header() -> None:
    """Write header row if the sheet is empty (best-effort)."""
    if not _has_credentials_file() or not settings.google_sheet_id.strip():
        return

    from googleapiclient.discovery import build

    creds = _build_credentials()
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)
    existing = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=settings.google_sheet_id.strip(),
            range="Sheet1!A1:F1",
        )
        .execute()
    )
    if existing.get("values"):
        return

    headers = [["Timestamp", "Name", "Phone", "Reason", "Confirmed Slot", "Booking ID"]]
    service.spreadsheets().values().update(
        spreadsheetId=settings.google_sheet_id.strip(),
        range="Sheet1!A1:F1",
        valueInputOption="USER_ENTERED",
        body={"values": headers},
    ).execute()
    print("[Sheets] Wrote header row")


def service_account_email() -> str | None:
    """Read client_email from the JSON (for sharing calendar/sheet)."""
    path = _credentials_path()
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("client_email")
    except (OSError, json.JSONDecodeError):
        return None
