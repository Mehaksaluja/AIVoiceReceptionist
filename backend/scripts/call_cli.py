"""
Trigger an outbound Vapi call (phone will ring).

Prerequisites:
  1. uvicorn running
  2. ngrok http 8000  → set PUBLIC_BASE_URL in .env
  3. VAPI_API_KEY + VAPI_PHONE_NUMBER_ID in .env
  4. Restart uvicorn after editing .env

Usage:
  python -m scripts.call_cli
"""

import asyncio
import sys

import httpx

BASE = "http://127.0.0.1:8000"


async def main() -> None:
    print("=== AI Receptionist — Outbound Call ===\n")
    name = input("Patient name: ").strip() or "Mehak"
    phone = input("Your phone (+91...): ").strip()
    if not phone.startswith("+"):
        print("Phone must be E.164, e.g. +919876543210")
        sys.exit(1)
    reason = input("Reason: ").strip() or "Dental checkup"

    async with httpx.AsyncClient(timeout=60.0) as client:
        health = await client.get(f"{BASE}/health")
        health.raise_for_status()
        h = health.json()
        print(f"\nHealth: vapi={h.get('vapi_configured')} public_url={h.get('public_base_url')}")

        if not h.get("vapi_configured"):
            print("ERROR: Set VAPI_API_KEY and VAPI_PHONE_NUMBER_ID in .env")
            sys.exit(1)
        if not h.get("public_base_url"):
            print("ERROR: Set PUBLIC_BASE_URL (ngrok URL) in .env and restart server")
            sys.exit(1)

        print("\nPlacing outbound call...")
        res = await client.post(
            f"{BASE}/api/call",
            json={"name": name, "phone": phone, "reason": reason},
        )
        if res.status_code >= 400:
            print(res.text)
            sys.exit(1)

        body = res.json()
        print(f"\n{body.get('reply')}")
        print(f"Session: {body.get('session_id')}")
        print(f"Vapi call: {body.get('vapi_call_id')}")
        print("\nAnswer your phone. After the call, check activity:")
        print(f"  GET {BASE}/api/sessions/{body.get('session_id')}")


if __name__ == "__main__":
    asyncio.run(main())
