from unittest.mock import MagicMock

import pytest

from api.note.dto.note_create import NoteCreate
from api.note.entity.note import Note
from api.note.note_service import NoteService


@pytest.fixture
def session() -> MagicMock:
    s = MagicMock(name="SessionMock")
    s.exec.return_value.all.return_value = []
    return s


@pytest.fixture
def svc(session) -> NoteService:
    return NoteService(session=session)


def _set_all(session: MagicMock, items):
    session.exec.return_value.all.return_value = items


def test_get_by_user_id_returns_notes(session, svc: NoteService):
    notes = [Note(id=1, content="a", user_id=7), Note(id=2, content="b", user_id=7)]
    _set_all(session, notes)

    got = svc.get_by_user_id(7)

    assert got == notes
    session.exec.assert_called_once()
    session.exec.return_value.all.assert_called_once()


def test_get_by_user_id_empty(session, svc: NoteService):
    _set_all(session, [])
    assert svc.get_by_user_id(99) == []


def test_create_persists_and_returns_note(session, svc: NoteService):
    note_in = NoteCreate(content="hello world")
    user_id = 42

    created = svc.create(user_id, note_in)

    assert isinstance(created, Note)
    assert created.content == "hello world"
    assert created.user_id == user_id

    session.add.assert_called_once_with(created)
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(created)


def test_create_multiple_calls_independent(session, svc: NoteService):
    a = svc.create(1, NoteCreate(content="A"))
    b = svc.create(2, NoteCreate(content="B"))

    assert a is not b
    assert a.user_id == 1 and a.content == "A"
    assert b.user_id == 2 and b.content == "B"
    assert session.add.call_count == 2
    assert session.commit.call_count == 2
    assert session.refresh.call_count == 2
