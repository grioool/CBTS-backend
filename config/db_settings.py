from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_IP: str

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


db_settings = DatabaseSettings()
