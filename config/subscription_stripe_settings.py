from pydantic_settings import BaseSettings, SettingsConfigDict


class SubscriptionSettings(BaseSettings):
    STRIPE_ID:str
    PRICE_ID_PREMIUM:str
    PRICE_ID_ENTERPRISE:str

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


subscription_settings = SubscriptionSettings()
