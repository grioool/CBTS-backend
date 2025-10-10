from typing import Annotated

from fastapi import Depends
from sqlmodel import select

from api.note.dto.note_create import NoteCreate
from api.note.entity.note import Note
from db.config import SessionDep


class NoteService:
    def __init__(self, session: SessionDep):
        self.session = session

    def get_by_user_id(self, user_id: int) -> list[Note]:
        notes = self.session.exec(select(Note).where(Note.user_id == user_id)).all()
        return notes

    def create(self, user_id: int,  note: NoteCreate) -> Note:
        db_note = Note(content=note.content, user_id=user_id)
        self.session.add(db_note)
        self.session.commit()
        self.session.refresh(db_note)
        return db_note

NoteServiceDep = Annotated[NoteService, Depends(NoteService)]

