import io
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import api.summary.summary_service as mod
from api.summary.summary_service import (
    SummaryService,
    generate_hash,
    get_daily_limit_for_role,
)


@pytest.fixture
def session() -> MagicMock:
    s = MagicMock(name="SessionMock")
    # Default: any session.exec(...).first() returns None
    s.exec.return_value.first.return_value = None
    # Default: any session.exec(...).all() returns []
    s.exec.return_value.all.return_value = []
    return s


@pytest.fixture
def auth_service() -> MagicMock:
    svc = MagicMock(name="AuthServiceMock")

    async def _get_current_user(token: str):
        return SimpleNamespace(
            id=7,
            username="alice",
            role_id=None,
            counter_last_update=None,
            summary_count=0,
        )

    svc.get_current_user.side_effect = _get_current_user
    return svc


@pytest.fixture
def gemini(monkeypatch) -> MagicMock:
    models = MagicMock()
    models.generate_content.return_value = SimpleNamespace(text="SUMMARY_TEXT")
    gc = SimpleNamespace(models=models)
    monkeypatch.setattr(mod, "gemini_client", gc)
    return models


@pytest.fixture
def gcs(monkeypatch) -> MagicMock:
    storage_client = MagicMock()
    storage_client.list_buckets.return_value = []
    monkeypatch.setattr(mod, "storage_client", storage_client)

    blob = MagicMock()
    blob.public_url = "https://files.example/summaries/abc.txt"
    bucket = MagicMock()
    bucket.blob.return_value = blob
    monkeypatch.setattr(mod, "bucket", bucket)
    return SimpleNamespace(bucket=bucket, blob=blob)


@pytest.fixture
def pdf(monkeypatch):
    class Page:
        def __init__(self, text): self._t = text

        def get_text(self): return self._t

    class Doc:
        def __init__(self, pages): self._pages = pages

        def __iter__(self): return iter(self._pages)

        def __enter__(self): return self

        def __exit__(self, exc_type, exc, tb): return False

    def fake_open(*args, **kwargs):
        return Doc([Page("Hello"), Page("World")])

    monkeypatch.setattr(mod.fitz, "open", fake_open)


@pytest.fixture
def upload_file():
    class DummyFile:
        def __init__(self, filename="doc.pdf", content=b"%PDF..."):
            self.filename = filename
            self.file = io.BytesIO(content)

    return DummyFile


@pytest.fixture
def svc(session, auth_service) -> SummaryService:
    return SummaryService(session=session, auth_service=auth_service)


class FakeDatetime(datetime):
    @classmethod
    def now(cls, tz=None):
        fixed = datetime(2025, 1, 1, 12, 0, 0)
        if tz:
            return fixed.replace(tzinfo=tz)
        return fixed


def test_generate_hash_is_deterministic_and_length():
    h1 = generate_hash("report.pdf")
    h2 = generate_hash("report.pdf")
    h3 = generate_hash("other.pdf")
    assert h1 == h2
    assert h1 != h3
    assert len(h1) == 10


@pytest.mark.parametrize(
    "role_id,expected",
    [(2, 5), (3, 50), (4, 200), (None, 5), (999, 5)],
)
def test_get_daily_limit_for_role(role_id, expected):
    assert get_daily_limit_for_role(role_id) == expected


def test_get_by_id(session, svc: SummaryService):
    target = object()
    session.exec.return_value.first.return_value = target
    got = svc.get_by_id(123)
    assert got is target
    session.exec.assert_called_once()


def test_get_all_user_summaries(session, svc: SummaryService):
    items = [object(), object()]
    session.exec.return_value.all.return_value = items
    got = svc.get_all_user_summaries(7)
    assert got == items
    session.exec.assert_called_once()
