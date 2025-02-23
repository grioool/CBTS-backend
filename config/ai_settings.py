from pydantic_settings import BaseSettings, SettingsConfigDict

class AISettings(BaseSettings):
    GEMINI_KEY: str

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

ai_settings = AISettings()
