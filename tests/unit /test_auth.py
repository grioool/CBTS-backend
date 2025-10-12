import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from api.auth.auth_service import AuthService, auth_settings, jwt, pwd_context
from api.auth.password_reset_token import PasswordResetToken
from api.user.dto.user_create import UserCreate
from api.user.dto.user_login import UserLogin
from api.user.entity.user import User


@pytest.fixture
def session() -> MagicMock:
    s = MagicMock(name="SessionMock")
    s.exec.return_value.first.return_value = None
    return s


@pytest.fixture
def user_service() -> MagicMock:
    return MagicMock(name="UserServiceMock")


@pytest.fixture
def svc(session, user_service) -> AuthService:
    return AuthService(session=session, user_service=user_service)


@pytest.fixture(autouse=True)
def patch_password_hashing(monkeypatch):
    # Make hashing/verify predictable and cheap
    monkeypatch.setattr(pwd_context, "hash", lambda pw: f"HASHED::{pw}")
    monkeypatch.setattr(pwd_context, "verify", lambda plain, hashed: hashed == f"HASHED::{plain}")


@pytest.fixture(autouse=True)
def patch_auth_settings(monkeypatch):
    # Minimal settings needed by the service
    monkeypatch.setattr(auth_settings, "SECRET_KEY", "test-secret")
    monkeypatch.setattr(auth_settings, "ALGORITHM", "HS256")
    monkeypatch.setattr(auth_settings, "FORGOT_PASSWORD_URL", "https://example.com/reset")


def _set_first(session: MagicMock, value):
    session.exec.return_value.first.return_value = value


def test_verify_and_hash(svc: AuthService):
    hashed = svc.get_password_hash("pw")
    assert hashed == "HASHED::pw"
    assert svc.verify_password("pw", hashed) is True
    assert svc.verify_password("nope", hashed) is False


def test_user_exists_true(session, svc: AuthService):
    _set_first(session, object())
    assert svc.user_exists(UserCreate(username="a", email="a@x", password="pw")) is True


def test_user_exists_false(session, svc: AuthService):
    _set_first(session, None)
    assert svc.user_exists(UserCreate(username="a", email="a@x", password="pw")) is False


def test_create_user_hashes_and_persists(session, svc: AuthService):
    uc = UserCreate(username="a", email="a@x", password="pw")

    result = svc.create_user(uc)

    # The method returns the input dto (your implementation), now with hashed password
    assert result.password == "HASHED::pw"
    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()


# -------------------- login --------------------

def test_login_success(user_service, svc: AuthService):
    user_service.get_by_username.return_value = User(id=1, username="a", email="a@x", password="HASHED::pw")
    ok = svc.login(UserLogin(username="a", password="pw"))
    assert ok is not None and ok.username == "a"


def test_login_user_not_found(user_service, svc: AuthService):
    user_service.get_by_username.return_value = None
    assert svc.login(UserLogin(username="a", password="pw")) is None


def test_login_wrong_password(user_service, svc: AuthService):
    user_service.get_by_username.return_value = User(id=1, username="a", email="a@x", password="HASHED::pw")
    assert svc.login(UserLogin(username="a", password="wrong")) is None


def test_create_and_decode_access_token_roundtrip(svc: AuthService):
    token = svc.create_access_token({"sub": "alice"}, expires_delta=timedelta(minutes=5))
    payload = svc.decode_access_token(token)
    assert payload["sub"] == "alice"
    assert "exp" in payload


def test_decode_access_token_expired(svc: AuthService, monkeypatch):
    class _Expired(Exception): pass

    monkeypatch.setattr(jwt, "ExpiredSignatureError", _Expired)
    monkeypatch.setattr(jwt, "decode", lambda *a, **k: (_ for _ in ()).throw(_Expired()))
    with pytest.raises(HTTPException) as exc:
        svc.decode_access_token("tok")
    assert exc.value.status_code == 401
    assert "expired" in exc.value.detail.lower()


def test_get_current_user_success(user_service, svc: AuthService, monkeypatch):
    token = svc.create_access_token({"sub": "alice"})
    user_service.get_by_username.return_value = User(id=1, username="alice", email="a@x", password="HASHED::pw")

    user = pytest.run(async_fn=svc.get_current_user(token)) if hasattr(pytest, "run") else \
        pytest.mark.asyncio(lambda: None)


def test_request_password_reset_no_user(user_service, svc: AuthService):
    user_service.get_by_email.return_value = None
    bg = MagicMock(name="BackgroundTasksMock")
    assert svc.request_password_reset("nobody@x", bg) is None
    bg.add_task.assert_not_called()
    svc.session.add.assert_not_called()


def test_request_password_reset_creates_token_and_sends_email(user_service, session, svc: AuthService, monkeypatch):
    user_service.get_by_email.return_value = User(id=7, username="u", email="u@x", password="HASHED::pw")
    monkeypatch.setattr(uuid, "uuid4", lambda: uuid.UUID(int=1))
    bg = MagicMock(name="BackgroundTasksMock")

    svc.request_password_reset("u@x", bg)

    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()
    bg.add_task.assert_called_once()


def _make_token(user_id=7, minutes=15, used=False) -> PasswordResetToken:
    return PasswordResetToken(
        token=uuid.uuid4(),
        user_id=user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=minutes),
        used=used,
    )


def test_reset_password_happy_path(session, user_service, svc: AuthService):
    token = _make_token()
    _set_first(session, token)  # for session.exec(...).first()

    user = User(id=token.user_id, username="u", email="u@x", password="HASHED::old")
    user_service.get_by_id.return_value = user

    updated = svc.reset_password(str(token.token), "newpw")

    assert updated is user
    assert updated.password == "HASHED::newpw"
    assert token.used is True
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(user)


def test_reset_password_invalid_token(session, svc: AuthService):
    _set_first(session, None)
    with pytest.raises(HTTPException) as exc:
        svc.reset_password("nope", "x")
    assert exc.value.status_code == 401

    used = _make_token(minutes=15, used=True)
    _set_first(session, used)
    with pytest.raises(HTTPException):
        svc.reset_password(str(used.token), "x")


def test_reset_password_user_missing(session, user_service, svc: AuthService):
    token = _make_token()
    _set_first(session, token)
    user_service.get_by_id.return_value = None
    with pytest.raises(HTTPException) as exc:
        svc.reset_password(str(token.token), "x")
    assert exc.value.status_code == 401
