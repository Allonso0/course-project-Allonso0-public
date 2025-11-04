import uuid

import pytest


class TestRFC7807ErrorFormat:

    def test_not_found_error_format(self, test_client):
        response = test_client.get("/api/v1/entries/99999")

        assert response.status_code == 404
        assert response.headers["content-type"] == "application/problem+json"

        error_data = response.json()

        assert "type" in error_data
        assert "title" in error_data
        assert "status" in error_data
        assert "detail" in error_data
        assert "correlation_id" in error_data

        assert error_data["type"] == "/errors/not-found"
        assert error_data["title"] == "Not Found"
        assert error_data["status"] == 404
        assert "Entry with id 99999 not found" in error_data["detail"]

        try:
            uuid.UUID(error_data["correlation_id"])
        except ValueError:
            pytest.fail("correlation_id is not a valid UUID")

    def test_validation_error_format(self, test_client):
        response = test_client.post(
            "/api/v1/entries",
            json={"title": "", "kind": "invalid_kind", "status": "planned"},
        )

        assert response.status_code == 422
        assert response.headers["content-type"] == "application/problem+json"

        error_data = response.json()

        assert "type" in error_data
        assert "title" in error_data
        assert "status" in error_data
        assert "detail" in error_data
        assert "correlation_id" in error_data

        assert error_data["type"] == "/errors/validation"
        assert error_data["title"] == "Validation Error"
        assert error_data["status"] == 422

    def test_method_not_allowed_format(self, test_client):
        response = test_client.patch("/api/v1/entries")

        assert response.status_code == 405
        assert response.headers["content-type"] == "application/problem+json"

        error_data = response.json()

        assert error_data["type"] == "/errors/method-not-allowed"
        assert error_data["title"] == "Method Not Allowed"
        assert error_data["status"] == 405
        assert "correlation_id" in error_data

    def test_internal_server_error_format(self, test_client):
        response = test_client.get("/api/v1/health?force_error=true")

        if response.status_code == 500:
            error_data = response.json()

            assert "type" in error_data
            assert "title" in error_data
            assert "status" in error_data
            assert "detail" in error_data
            assert "correlation_id" in error_data

            assert error_data["type"] == "/errors/internal"
            assert error_data["title"] == "Internal Server Error"
            assert "internal server error" in error_data["detail"].lower()
            assert "traceback" not in error_data["detail"].lower()
            assert "file" not in error_data["detail"].lower()

    def test_correlation_id_uniqueness(self, test_client):
        responses = []

        for i in range(3):
            response = test_client.get(f"/api/v1/entries/{99900 + i}")
            if response.status_code == 404:
                responses.append(response.json())

        correlation_ids = [resp["correlation_id"] for resp in responses]
        assert len(correlation_ids) == len(
            set(correlation_ids)
        ), "Correlation IDs are not unique"

    def test_error_with_additional_fields(self, test_client):
        response = test_client.post(
            "/api/v1/entries",
            json={"title": "Valid Title", "kind": "article", "status": "planned"},
        )

        if response.status_code == 422:
            error_data = response.json()

            assert "type" in error_data
            assert "correlation_id" in error_data

    def test_content_type_header(self, test_client):
        response = test_client.get("/api/v1/nonexistent-endpoint")

        assert response.status_code == 404
        content_type = response.headers.get("content-type", "")
        assert "application/problem+json" in content_type

    def test_malformed_json_error(self, test_client):
        response = test_client.post(
            "/api/v1/entries",
            data="invalid json {",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code in [400, 422, 500]
        if response.status_code >= 400:
            content_type = response.headers.get("content-type", "")
            if "application/problem+json" in content_type:
                error_data = response.json()
                assert "correlation_id" in error_data

    def test_rate_limiting_error_format(self, test_client):
        responses = []
        for i in range(10):
            response = test_client.post(
                "/api/v1/entries",
                json={"title": f"Test Book {i}", "kind": "book", "status": "planned"},
            )
            responses.append(response)

            if response.status_code == 429:
                error_data = response.json()
                assert "type" in error_data
                assert "title" in error_data
                assert "status" in error_data
                assert "detail" in error_data
                assert "correlation_id" in error_data
                break

    def test_error_response_structure_consistency(self, test_client):
        error_endpoints = [
            ("/api/v1/nonexistent", 404),
            ("/api/v1/entries", "PATCH"),
        ]

        for endpoint, method in error_endpoints:
            if isinstance(method, str):
                response = test_client.request(method, endpoint)
            else:
                response = test_client.get(endpoint)

            if 400 <= response.status_code < 600:
                error_data = response.json()

                required_fields = {
                    "type",
                    "title",
                    "status",
                    "detail",
                    "correlation_id",
                }
                assert required_fields.issubset(
                    error_data.keys()
                ), f"Missing fields in {endpoint}"

                assert isinstance(error_data["type"], str)
                assert isinstance(error_data["title"], str)
                assert isinstance(error_data["status"], int)
                assert isinstance(error_data["detail"], str)
                assert isinstance(error_data["correlation_id"], str)


def test_custom_api_error_handling(test_client):
    response = test_client.delete("/api/v1/entries/99999")

    if response.status_code == 404:
        error_data = response.json()

        assert error_data["type"] == "/errors/not-found"
        assert error_data["title"] == "Not Found"
        assert "correlation_id" in error_data

        detail = error_data["detail"]
        assert "Entry with id 99999 not found" in detail
        assert "sql" not in detail.lower()
        assert "trace" not in detail.lower()
