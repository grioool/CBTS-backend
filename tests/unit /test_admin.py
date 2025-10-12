from unittest.mock import MagicMock

from api.admin.admin_service import count_users, count_summaries


def _set_scalar(session: MagicMock, value: int):
    session.execute.return_value.scalar.return_value = value


def make_session() -> MagicMock:
    s = MagicMock(name="SessionMock")
    res = MagicMock(name="ResultMock")
    res.scalar.return_value = 0
    s.execute.return_value = res
    return s


def test_count_users_returns_scalar():
    session = make_session()
    _set_scalar(session, 42)
    assert count_users(session) == 42
    session.execute.assert_called_once()
    session.execute.return_value.scalar.assert_called_once()


def test_count_users_zero():
    session = make_session()
    _set_scalar(session, 0)
    assert count_users(session) == 0


def test_count_summaries_returns_scalar():
    session = make_session()
    _set_scalar(session, 7)
    assert count_summaries(session) == 7


def test_count_summaries_zero():
    session = make_session()
    _set_scalar(session, 0)
    assert count_summaries(session) == 0
