from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Single source of truth for configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_env: str = "development"
    clinic_name: str = "XYZ Clinic"

    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = "gpt-4o"

    vapi_api_key: str = ""
    vapi_assistant_id: str = ""
    vapi_phone_number_id: str = ""

    google_service_account_path: str = "./credentials/google-service-account.json"
    google_calendar_id: str = "primary"
    google_sheet_id: str = ""

    sendgrid_api_key: str = ""
    sendgrid_from_email: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""

    @property
    def is_dev(self) -> bool:
        return self.app_env == "development"

    @property
    def has_openai(self) -> bool:
        return bool(self.openai_api_key.strip())

    @property
    def has_vapi(self) -> bool:
        return bool(
            self.vapi_api_key and self.vapi_assistant_id and self.vapi_phone_number_id
        )


@lru_cache
def get_settings() -> Settings:
    """Cached singleton — load .env once, reuse everywhere."""
    return Settings()

settings = get_settings()
