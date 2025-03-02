from sqlmodel import Field, SQLModel


class UserRole(SQLModel, table=True):
    __tablename__ = "user_role"
    id: int | None = Field(default=None, primary_key=True)
    role: str
    summaries_count: int | None = Field(index=True)


class UserTier(SQLModel, table=True):
    __tablename__ = "user_tier"
    id: int | None = Field(default=None, primary_key=True)
    tier: str


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str | None = Field(index=True)
    email: str = Field(index=True)
    password: str
    role_id: int = Field(default=2, foreign_key="user_role.id")
