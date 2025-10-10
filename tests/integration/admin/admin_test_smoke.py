from datetime import timedelta
import jwt

from api.auth.auth_service import AuthService
from config import auth_settings


class _DummyUserService:
    def get_by_username(self, username): return None


class _DummySession:
    def exec(self, *a, **k): return None


def test_hash_and_verify():
    svc = AuthService(session=_DummySession(), user_service=_DummyUserService())
    pwd = "P@ssw0rd!"
    hashed = svc.get_password_hash(pwd)
    assert hashed != pwd
    assert svc.verify_password(pwd, hashed) is True


def test_create_access_token_roundtrip(monkeypatch):
    # isolate key/alg so decode works here
    monkeypatch.setattr(auth_settings, "SECRET_KEY", "covkey")
    monkeypatch.setattr(auth_settings, "ALGORITHM", "HS256")

    svc = AuthService(session=_DummySession(), user_service=_DummyUserService())
    token = svc.create_access_token({"sub": "someone"}, expires_delta=timedelta(minutes=1))
    payload = jwt.decode(token, "covkey", algorithms=["HS256"])
    # Just assert payload is a dict and exp exists — keep it basic
    assert isinstance(payload, dict)
    assert "exp" in payload
