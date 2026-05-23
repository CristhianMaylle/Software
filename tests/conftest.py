"""
Patch the database engine to SQLite in-memory BEFORE app.main is imported.
This ensures no SQL Server connection is needed to run the test suite.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.database as _db

_test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_db.engine = _test_engine
_db.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

# Import app AFTER patching so main.py picks up the SQLite engine
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


def _override_get_db():
    db = _db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client() -> TestClient:
    Base.metadata.create_all(bind=_test_engine)
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=_test_engine)
    app.dependency_overrides.clear()
