from pydantic_settings import BaseSettings, SettingsConfigDict


class OriginsSettings(BaseSettings):
    ALLOWED_ORIGINS: str

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


origins_settings = OriginsSettings()
