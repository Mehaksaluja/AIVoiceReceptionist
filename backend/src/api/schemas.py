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


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(min_length=1, max_length=2000)


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
    reply: str | None = None
    activity: list[ActivityOut] = Field(default_factory=list)
