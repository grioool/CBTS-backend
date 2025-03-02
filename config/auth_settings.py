from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


auth_settings = AuthSettings()
