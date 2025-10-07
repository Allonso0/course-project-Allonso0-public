import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app


class TestNFRValidation:

    @pytest.fixture
    def client(self):
        with TestClient(app) as test_client:
            yield test_client

    def test_nfr_04_kind_validation_metric(self, client):
        valid_kinds = ["book", "article"]
        invalid_kinds = ["movie", "podcast", "invalid_type", ""]

        valid_count = 0
        invalid_count = 0

        for kind in valid_kinds:
            response = client.post(
                "/api/v1/entries",
                json={
                    "title": f"Test {kind}",
                    "link": "https://example.com",
                    "kind": kind,
                    "status": "planned",
                },
            )
            if response.status_code == 201:
                valid_count += 1

        for kind in invalid_kinds:
            response = client.post(
                "/api/v1/entries",
                json={
                    "title": "Test Invalid Kind",
                    "link": "https://example.com",
                    "kind": kind,
                    "status": "planned",
                },
            )
            if response.status_code == 422:
                invalid_count += 1

        assert valid_count == len(
            valid_kinds
        ), f"Not all valid kinds accepted: {valid_count}/{len(valid_kinds)}"
        assert invalid_count == len(
            invalid_kinds
        ), f"Not all invalid kinds rejected: {invalid_count}/{len(invalid_kinds)}"

    def test_nfr_04_status_validation_metric(self, client):
        valid_statuses = ["planned", "reading", "completed"]
        invalid_statuses = ["done", "in-progress", "unknown", ""]

        valid_count = 0
        invalid_count = 0

        for status in valid_statuses:
            response = client.post(
                "/api/v1/entries",
                json={
                    "title": f"Test Status {status}",
                    "link": "https://example.com",
                    "kind": "book",
                    "status": status,
                },
            )
            if response.status_code == 201:
                valid_count += 1

        for status in invalid_statuses:
            response = client.post(
                "/api/v1/entries",
                json={
                    "title": "Test Status Validation",
                    "link": "https://example.com",
                    "kind": "book",
                    "status": status,
                },
            )
            if response.status_code == 422:
                invalid_count += 1

        assert valid_count == len(
            valid_statuses
        ), f"Valid status failure: {valid_count}/{len(valid_statuses)}"
        assert invalid_count == len(
            invalid_statuses
        ), f"Invalid status not rejected: {invalid_count}/{len(invalid_statuses)}"
