from datetime import datetime

from sqlmodel import Field, SQLModel


class UserRole(SQLModel, table=True):
    __tablename__ = "user_role"
    id: int | None = Field(default=None, primary_key=True)
    role: str


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str | None = Field(index=True)
    email: str = Field(index=True)
    password: str
    summary_count: int = Field(default=5)
    counter_last_update: datetime = Field(default=datetime.date())
    role_id: int = Field(default=2, foreign_key="user_role.id")
