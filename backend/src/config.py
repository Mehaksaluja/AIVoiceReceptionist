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
    # Public HTTPS URL (ngrok) so Vapi can reach our webhooks/tools
    public_base_url: str = ""

    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = "gpt-4o"

    vapi_api_key: str = ""
    vapi_public_key: str = ""  # browser Web SDK (safe for frontend)
    vapi_assistant_id: str = ""
    vapi_phone_number_id: str = ""
    # False = transient assistant (recommended for local/ngrok)
    vapi_use_saved_assistant: bool = False

    google_service_account_path: str = "./credentials/google-service-account.json"
    google_calendar_id: str = "primary"
    google_sheet_id: str = ""

    clinic_open_hour: int = 9
    clinic_close_hour: int = 20
    appointment_duration_minutes: int = 30

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
        # Phone number required only for PSTN outbound
        return bool(self.vapi_api_key and self.vapi_phone_number_id)

    @property
    def has_vapi_web(self) -> bool:
        """Browser voice — needs public key + webhook URL (no phone number)."""
        return bool(self.vapi_public_key.strip() and self.public_base_url.strip())

    @property
    def has_google_credentials(self) -> bool:
        from pathlib import Path

        path = Path(self.google_service_account_path)
        if not path.is_absolute():
            path = Path.cwd() / path
        return path.is_file()


@lru_cache
def get_settings() -> Settings:
    """Cached singleton — load .env once, reuse everywhere."""
    return Settings()

settings = get_settings()
