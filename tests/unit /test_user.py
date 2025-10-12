from typing import Callable
from unittest.mock import MagicMock

import pytest

from api.user.entity.user import User
from api.user.user_service import UserService


@pytest.fixture
def session() -> MagicMock:
    s = MagicMock(name="SessionMock")
    s.exec.return_value.first.return_value = None
    return s


@pytest.fixture
def svc_factory(session: MagicMock) -> Callable[[], UserService]:
    return lambda: UserService(session=session)


def _set_first(session: MagicMock, value):
    session.exec.return_value.first.return_value = value


@pytest.mark.parametrize(
    "method,arg",
    [
        ("get_by_username", "alice"),
        ("get_by_email", "alice@example.com"),
        ("get_by_id", 42),
    ],
)
def test_service_methods_return_user(session, svc_factory, method, arg):
    svc = svc_factory()
    fake = User(id=1, username="alice", email="alice@example.com")
    _set_first(session, fake)

    got = getattr(svc, method)(arg)

    assert got is fake
    session.exec.assert_called_once()
    session.exec.return_value.first.assert_called_once()


@pytest.mark.parametrize(
    "method,arg",
    [
        ("get_by_username", "bob"),
        ("get_by_email", "bob@example.com"),
        ("get_by_id", 999),
    ],
)
def test_service_methods_return_none_when_absent(session, svc_factory, method, arg):
    svc = svc_factory()
    _set_first(session, None)

    assert getattr(svc, method)(arg) is None
    session.exec.assert_called_once()
    session.exec.return_value.first.assert_called_once()


def test_exec_errors_bubble_up(session, svc_factory):
    svc = svc_factory()
    session.exec.side_effect = RuntimeError("boom")

    with pytest.raises(RuntimeError):
        svc.get_by_username("alice")


def test_service_uses_injected_session_instance(session, svc_factory):
    svc = svc_factory()
    assert svc.session is session
