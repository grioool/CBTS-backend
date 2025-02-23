from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    gemini_key: str

    model_config = SettingsConfigDict(env_file=".env")


app_settings = AppSettings()
