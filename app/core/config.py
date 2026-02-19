from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Identidade e Log
    SYSTEM_NAME: str = "PMAS"
    LOG_LEVEL: str = "INFO"
    STORAGE_PATH: str = "storage"

    # API Keys
    GEMINI_API_KEY: str

    # Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # Taiga
    TAIGA_URL: str
    TAIGA_API_TOKEN: str
    TAIGA_PROJECT_ID: int
    TAIGA_USER_ID: int

    # Frontend/CORS
    FRONTEND_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("FRONTEND_ORIGINS", mode="before")
    @classmethod
    def parse_frontend_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
