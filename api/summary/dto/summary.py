from sqlmodel import Field, SQLModel


class Summary(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    filename: str | None = Field(index=True)
    user_id: int = Field(foreign_key="user.id")
