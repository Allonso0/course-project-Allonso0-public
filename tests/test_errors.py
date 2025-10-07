def test_404_endpoint(test_client):
    response = test_client.get("/api/v1/nonexistent")

    assert response.status_code == 404


def test_validation_error_response_format(test_client):
    response = test_client.post(
        "/api/v1/entries",
        json={"title": "", "kind": "invalid_kind", "status": "planned"},
    )

    assert response.status_code == 422
    error_data = response.json()
    assert "error" in error_data
    assert error_data["error"]["code"] == "validation_error"


def test_404_nonexistent_entry(test_client):
    response = test_client.get("/api/v1/entries/9999")

    assert response.status_code == 404
    error_data = response.json()
    assert error_data["error"]["code"] == "not_found"
    assert "Entry with id 9999" in error_data["error"]["message"]
