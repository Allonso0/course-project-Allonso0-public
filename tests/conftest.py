import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["TESTING"] = "true"

os.environ["APP_JWT_SECRET"] = "test_jwt_secret"
os.environ["APP_DATABASE_URL"] = "sqlite:///:memory:"
os.environ["APP_API_KEY"] = "test_api_key"


from app.domain.database_models import Base
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    from app.core.database import engine

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_database():
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
    finally:
        db.close()
    yield


@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def sample_entry_data():
    return {
        "title": "Test Book Title",
        "kind": "book",
        "link": "https://example.com/book",
        "status": "planned",
    }


@pytest.fixture
def created_entry(test_client, sample_entry_data):
    response = test_client.post("/api/v1/entries", json=sample_entry_data)
    return response.json()
