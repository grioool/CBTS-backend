from pydantic_settings import BaseSettings, SettingsConfigDict


class StorageSettings(BaseSettings):
    STORAGE_NAME:str

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


storage_settings = StorageSettings()
