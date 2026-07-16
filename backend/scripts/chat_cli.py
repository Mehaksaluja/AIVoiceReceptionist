"""
Interactive terminal chat with the agent (no frontend).

Usage (venv activated, from backend/):
  python -m scripts.chat_cli
"""

import asyncio
import json
import sys

import httpx

BASE = "http://127.0.0.1:8000"


async def main() -> None:
    print("=== AI Receptionist (text mode) ===\n")
    name = input("Patient name: ").strip() or "Mehak"
    phone = input("Phone (+91...): ").strip() or "+919876543210"
    reason = input("Reason: ").strip() or "Dental checkup"

    async with httpx.AsyncClient(timeout=60.0) as client:
        health = await client.get(f"{BASE}/health")
        health.raise_for_status()
        data = health.json()
        if not data.get("openai_configured"):
            print("\nERROR: Set OPENAI_API_KEY in backend/.env and restart the server.")
            sys.exit(1)

        print("\nStarting session...")
        res = await client.post(
            f"{BASE}/api/sessions",
            json={"name": name, "phone": phone, "reason": reason},
        )
        if res.status_code >= 400:
            print(res.text)
            sys.exit(1)

        body = res.json()
        session_id = body["session_id"]
        print(f"\nSession: {session_id}")
        print(f"Agent: {body.get('reply')}\n")

        while True:
            if body.get("is_booked"):
                print(f"\n✓ BOOKED → {body.get('confirmed_slot')}")
                print("\nActivity log:")
                print(json.dumps(body.get("activity", []), indent=2, default=str))
                break

            user = input("You: ").strip()
            if not user or user.lower() in {"quit", "exit", "q"}:
                print("Bye.")
                break

            res = await client.post(
                f"{BASE}/api/chat",
                json={"session_id": session_id, "message": user},
            )
            if res.status_code >= 400:
                print(res.text)
                continue

            body = res.json()
            print(f"Agent: {body.get('reply')}\n")


if __name__ == "__main__":
    asyncio.run(main())
