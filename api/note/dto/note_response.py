from sqlmodel import SQLModel


class NoteResponse(SQLModel):
    id: int
    user_id: int
    content: str