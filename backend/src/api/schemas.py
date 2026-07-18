"""API request / response schemas."""

from pydantic import BaseModel, Field


class StartSessionRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100, examples=["Mehak"])
    phone: str = Field(
        pattern=r"^\+[1-9]\d{6,14}$",
        examples=["+919876543210"],
        description="E.164 phone number",
    )
    reason: str = Field(min_length=3, max_length=500, examples=["Dental checkup"])
    # If true, skip text greeting and place a Vapi outbound call instead
    trigger_call: bool = False


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(min_length=1, max_length=2000)


class CallRequest(BaseModel):
    """Create session + place outbound call in one step."""

    name: str = Field(min_length=2, max_length=100)
    phone: str = Field(pattern=r"^\+[1-9]\d{6,14}$")
    reason: str = Field(min_length=3, max_length=500)


class WebCallRequest(BaseModel):
    """Browser voice — details collected by the assistant during the call."""

    pass


class WebCallResponse(BaseModel):
    session_id: str
    booking_id: str
    public_key: str
    assistant: dict
    caller_display_name: str
    caller_subtitle: str


class ActivityOut(BaseModel):
    step: str
    message: str
    metadata: dict = Field(default_factory=dict)
    at: str


class SessionResponse(BaseModel):
    session_id: str
    booking_id: str
    status: str
    is_booked: bool
    confirmed_slot: str | None = None
    vapi_call_id: str | None = None
    reply: str | None = None
    activity: list[ActivityOut] = Field(default_factory=list)
