from sqlmodel import SQLModel, Field


class UserRole(SQLModel, table=True):
    __tablename__ = "user_role"
    id: int | None = Field(default=None, primary_key=True)
    role: str
    summaries_count: int | None = Field(index=True)
