from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Identidade
    SYSTEM_NAME: str = "PMAS"
    LOG_LEVEL: str = "INFO"

    # Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # Taiga
    TAIGA_URL: str
    TAIGA_API_TOKEN: str
    TAIGA_PROJECT_ID: int
    TAIGA_USER_ID: int

    # Storage
    STORAGE_PATH: str = "storage"

    class Config:
        env_file = ".env"

settings = Settings()