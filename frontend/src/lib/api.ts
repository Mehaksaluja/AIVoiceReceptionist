export type WebCallResponse = {
  session_id: string;
  booking_id: string;
  public_key: string;
  assistant: Record<string, unknown>;
  caller_display_name: string;
  caller_subtitle: string;
};

export type SessionResponse = {
  session_id: string;
  booking_id: string;
  status: string;
  is_booked: boolean;
  confirmed_slot: string | null;
  reply: string | null;
};

export type HealthResponse = {
  vapi_web_configured: boolean;
  public_base_url: string | null;
};

async function parseError(res: Response): Promise<string> {
  try {
    const data = await res.json();
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) return data.detail.map((d: { msg?: string }) => d.msg).join(", ");
    return res.statusText || "Request failed";
  } catch {
    return res.statusText || "Request failed";
  }
}

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch("/health");
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function startWebCall(): Promise<WebCallResponse> {
  const res = await fetch("/api/web-call", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: "{}",
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function getSession(sessionId: string): Promise<SessionResponse> {
  const res = await fetch(`/api/sessions/${sessionId}`);
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}
