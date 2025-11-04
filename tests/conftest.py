import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["TESTING"] = "true"

from app.api.endpoints.entries import reset_database
from app.main import app


@pytest.fixture(autouse=True)
def clean_database():
    reset_database()
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
