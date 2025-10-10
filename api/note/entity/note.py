from sqlmodel import SQLModel, Field, Relationship

from api.user.entity.user import User


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content: str
    user_id: int | None = Field(default=None, foreign_key="user.id")
    user: User = Relationship(back_populates="notes")