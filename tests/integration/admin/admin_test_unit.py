from types import SimpleNamespace
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from api.admin import admin_service as admin_service_mod, admin_router
from api.auth.auth_service import AuthService


class _AuthAdmin(AuthService):
    async def get_current_user(self, token: str):
        return SimpleNamespace(role_id=1, username="admin")

class _AuthUser(AuthService):
    async def get_current_user(self, token: str):
        return SimpleNamespace(role_id=2, username="user")

class _Auth401(AuthService):
    async def get_current_user(self, token: str):
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="bad token")


def _make_app(auth_impl):
    app = FastAPI()
    app.include_router(admin_router)
    app.dependency_overrides[AuthService] = lambda: auth_impl
    return app


def test_admin_ok(monkeypatch):
    async def fake_sum(session): return 10
    async def fake_users(session): return 3
    monkeypatch.setattr(admin_service_mod, "count_summaries", fake_sum)
    monkeypatch.setattr(admin_service_mod, "count_users", fake_users)

    app = _make_app(_AuthAdmin())
    client = TestClient(app)
    r = client.get("/admin/analytics", headers={"Authorization": "Bearer x"})
    assert r.status_code == status.HTTP_200_OK
    assert r.json() == {"total_summaries": 10, "total_users": 3, "is_admin": True}


def test_admin_forbidden(monkeypatch):
    async def fake_sum(session): return 1
    async def fake_users(session): return 1
    monkeypatch.setattr(admin_service_mod, "count_summaries", fake_sum)
    monkeypatch.setattr(admin_service_mod, "count_users", fake_users)

    app = _make_app(_AuthUser())
    client = TestClient(app)
    r = client.get("/admin/analytics", headers={"Authorization": "Bearer x"})
    assert r.status_code == status.HTTP_403_FORBIDDEN


def test_admin_not_found(monkeypatch):
    async def fake_sum(session): return None
    async def fake_users(session): return 5
    monkeypatch.setattr(admin_service_mod, "count_summaries", fake_sum)
    monkeypatch.setattr(admin_service_mod, "count_users", fake_users)

    app = _make_app(_AuthAdmin())
    client = TestClient(app)
    r = client.get("/admin/analytics", headers={"Authorization": "Bearer x"})
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_missing_bearer():
    app = _make_app(_AuthAdmin())
    client = TestClient(app)
    r = client.get("/admin/analytics")  # no Authorization header
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_invalid_token(monkeypatch):
    async def fake_sum(session): return 1
    async def fake_users(session): return 1
    monkeypatch.setattr(admin_service_mod, "count_summaries", fake_sum)
    monkeypatch.setattr(admin_service_mod, "count_users", fake_users)

    app = _make_app(_Auth401())
    client = TestClient(app)
    r = client.get("/admin/analytics", headers={"Authorization": "Bearer bad"})
    assert r.status_code == status.HTTP_401_UNAUTHORIZED
