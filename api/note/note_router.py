from typing import Annotated

from fastapi import APIRouter, Depends

from api.auth.auth_service import oauth2_scheme, AuthServiceDep
from api.note import note_service
from api.note.dto.note_create import NoteCreate
from api.note.dto.note_response import NoteResponse
from api.note.note_service import NoteServiceDep

router = APIRouter(prefix='/note', tags=['Note'])

@router.post('/', response_model=NoteResponse)
async def create_note(token: Annotated[str, Depends(oauth2_scheme)], auth_service: AuthServiceDep, note_create: NoteCreate, note_service: NoteServiceDep) -> NoteResponse:
    user = await auth_service.get_current_user(token)
    note = note_service.create(user.id, note_create)
    return note

@router.get('/', response_model=list[NoteResponse])
async def get_history(token: Annotated[str, Depends(oauth2_scheme)], auth_service: AuthServiceDep,
                      note_service: NoteServiceDep):
    user = await auth_service.get_current_user(token)
    notes = note_service.get_by_user_id(user.id)
    return notes