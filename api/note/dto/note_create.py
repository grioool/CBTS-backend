from sqlmodel import SQLModel


class NoteCreate(SQLModel):
    content: str
