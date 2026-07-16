"""Vapi webhooks — tool calls + call lifecycle events."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Request

from src.agent.booking_logic import run_book_appointment, run_check_availability
from src.services.session_store import store

router = APIRouter(prefix="/api/vapi", tags=["vapi"])


def _extract_args(tool_call: dict[str, Any]) -> dict[str, Any]:
    """Normalize Vapi tool-call argument shapes."""
    if "arguments" in tool_call and isinstance(tool_call["arguments"], dict):
        return tool_call["arguments"]
    if "parameters" in tool_call and isinstance(tool_call["parameters"], dict):
        return tool_call["parameters"]
    fn = tool_call.get("function") or {}
    params = fn.get("arguments") or fn.get("parameters") or {}
    if isinstance(params, str):
        try:
            return json.loads(params)
        except json.JSONDecodeError:
            return {}
    return params if isinstance(params, dict) else {}


def _session_id_from_message(message: dict[str, Any], args: dict[str, Any]) -> str | None:
    if args.get("session_id"):
        return str(args["session_id"])
    call = message.get("call") or {}
    metadata = call.get("metadata") or {}
    if metadata.get("session_id"):
        return str(metadata["session_id"])
    return None


def _execute_tool(name: str, args: dict[str, Any], session_id: str | None) -> Any:
    if name == "check_availability":
        return run_check_availability(
            preferred_date=args.get("preferred_date"),
            preferred_time=args.get("preferred_time"),
            session_id=session_id or args.get("session_id"),
        )

    if name == "book_appointment":
        sid = args.get("session_id") or session_id
        if not sid:
            return {"success": False, "error": "session_id is required"}
        return run_book_appointment(
            session_id=str(sid),
            datetime_iso=str(args.get("datetime_iso", "")),
            duration_minutes=int(args.get("duration_minutes") or 30),
        )

    return {"error": f"Unknown tool: {name}"}


def _handle_tool_calls(message: dict[str, Any]) -> dict[str, Any]:
    tool_list = message.get("toolCallList") or []
    results = []

    for tool_call in tool_list:
        tool_call_id = tool_call.get("id") or tool_call.get("toolCallId")
        name = tool_call.get("name") or (tool_call.get("function") or {}).get("name")
        args = _extract_args(tool_call)
        session_id = _session_id_from_message(message, args)

        print(f"[Vapi] tool-call {name} args={args}")
        result = _execute_tool(str(name), args, session_id)
        results.append(
            {
                "toolCallId": tool_call_id,
                "result": json.dumps(result) if not isinstance(result, str) else result,
            }
        )

    return {"results": results}


@router.post("/webhook")
async def vapi_webhook(request: Request) -> dict[str, Any]:
    """
    Single webhook for:
    - tool-calls (must return results)
    - status-update / end-of-call-report (ack only)
    """
    body = await request.json()
    message = body.get("message") or body
    msg_type = message.get("type")

    if msg_type == "tool-calls":
        return _handle_tool_calls(message)

    call = message.get("call") or {}
    call_id = call.get("id")
    metadata = call.get("metadata") or {}
    session_id = metadata.get("session_id")

    if msg_type == "status-update":
        status = message.get("status") or call.get("status")
        print(f"[Vapi] status-update call={call_id} status={status}")
        if session_id:
            store.log(str(session_id), "call_status", f"Call status: {status}", call_id=call_id)
        return {"ok": True}

    if msg_type == "end-of-call-report":
        print(f"[Vapi] end-of-call call={call_id}")
        if session_id:
            store.log(str(session_id), "call_ended", "Outbound call ended", call_id=call_id)
        return {"ok": True}

    # Ignore other event types
    return {"ok": True}
