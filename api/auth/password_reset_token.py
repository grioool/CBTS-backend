import uuid
from datetime import datetime

from sqlmodel import SQLModel, Field


class PasswordResetToken(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    token: uuid.UUID = Field(index=True, nullable=False)
    expires_at: datetime = Field(default=None, nullable=False)
    used: bool = Field(default=False, nullable=False)
    user_id: int = Field(foreign_key="user.id")
