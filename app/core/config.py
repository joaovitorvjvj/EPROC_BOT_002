from typing import List, Optional

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Identidade e Log
    SYSTEM_NAME: str = "PMAS"
    LOG_LEVEL: str = "INFO"
    STORAGE_PATH: str = "storage"

    # LLM (Groq atual + compatibilidade legado Gemini)
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GEMINI_API_KEY: Optional[str] = None

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

    @model_validator(mode="after")
    def validate_llm_keys(self):
        # Compatibilidade: se só GEMINI_API_KEY existir no ambiente, usa como fallback.
        if not self.GROQ_API_KEY and self.GEMINI_API_KEY:
            self.GROQ_API_KEY = self.GEMINI_API_KEY

        if not self.GROQ_API_KEY:
            raise ValueError("Defina GROQ_API_KEY (ou GEMINI_API_KEY legado) nas variáveis de ambiente.")
        return self

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
