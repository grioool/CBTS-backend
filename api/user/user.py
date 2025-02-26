from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str | None = Field(index=True)
    email: str = Field(index=True)
    password: str
    role_id: int = Field(foreign_key="user_role.id")
