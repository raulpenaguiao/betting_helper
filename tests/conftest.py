import pytest
import database as db
from fastapi.testclient import TestClient
from app import app


@pytest.fixture()
def tmp_db(tmp_path, monkeypatch):
    """Redirect all DB operations to a fresh temp file for each test."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init_db()
    return tmp_path / "test.db"


@pytest.fixture()
def client(tmp_db):
    """TestClient backed by a fresh temp database."""
    with TestClient(app) as c:
        yield c
