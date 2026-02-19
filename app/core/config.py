from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Identidade e Log
    SYSTEM_NAME: str = "PMAS"
    LOG_LEVEL: str = "INFO"
    STORAGE_PATH: str = "storage" # Adicionado para resolver o erro do BPMNService
    
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
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()