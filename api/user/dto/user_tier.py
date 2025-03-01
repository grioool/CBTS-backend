from sqlmodel import SQLModel, Field


class UserTier(SQLModel, table=True):
    __tablename__ = "user_tier"
    id: int | None = Field(default=None, primary_key=True)
    tier: str
    user_id: int | None = Field(index=True)