def test_rfc7807_error_format(test_client):
    response = test_client.get("/api/v1/entries/9999")

    assert response.status_code == 404
    data = response.json()

    assert "type" in data
    assert "title" in data
    assert "status" in data
    assert "detail" in data
    assert "correlation_id" in data
    assert data["status"] == 404
    assert data["title"] == "Not Found"


def test_validation_error_rfc7807(test_client):
    response = test_client.post(
        "/api/v1/entries",
        json={"title": "", "kind": "invalid_kind", "status": "planned"},
    )

    assert response.status_code == 422
    data = response.json()

    assert data["type"] == "/errors/validation"
    assert data["title"] == "Validation Error"
    assert "correlation_id" in data


def test_content_type_problem_json(test_client):
    response = test_client.get("/api/v1/nonexistent-endpoint")

    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
    data = response.json()
    assert "type" in data
    assert "title" in data
    assert data["type"] == "/errors/not-found"
    assert data["title"] == "Not Found"


def test_method_not_allowed_rfc7807(test_client):
    response = test_client.patch("/api/v1/entries")

    assert response.status_code == 405
    data = response.json()

    assert data["type"] == "/errors/method-not-allowed"
    assert data["title"] == "Method Not Allowed"
    assert "correlation_id" in data
    assert response.headers["content-type"] == "application/problem+json"
