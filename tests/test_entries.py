class TestCreateEntry:

    def test_create_entry_success(self, test_client, sample_entry_data):
        response = test_client.post("/api/v1/entries", json=sample_entry_data)

        assert response.status_code == 201
        data = response.json()

        assert data["id"] == 1
        assert data["title"] == sample_entry_data["title"]
        assert data["kind"] == sample_entry_data["kind"]
        assert data["link"] == sample_entry_data["link"]
        assert data["status"] == sample_entry_data["status"]
        assert data["owner_id"] == 1


class TestGetEntries:

    def test_get_entries_empty(self, test_client):
        response = test_client.get("/api/v1/entries")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_entries_with_data(self, test_client, created_entry):
        response = test_client.get("/api/v1/entries")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Test Book Title"


class TestGetEntry:

    def test_get_entry_success(self, test_client, created_entry):
        entry_id = created_entry["id"]
        response = test_client.get(f"/api/v1/entries/{entry_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entry_id
        assert data["title"] == created_entry["title"]

    def test_get_entry_not_found(self, test_client):
        response = test_client.get("/api/v1/entries/999")

        assert response.status_code == 404
        error_data = response.json()
        assert error_data["error"]["code"] == "not_found"
        assert "Entry with id 999 not found" in error_data["error"]["message"]


class TestUpdateEntry:

    def test_update_entry_success(self, test_client, created_entry):

        entry_id = created_entry["id"]
        update_data = {"title": "Updated Title", "status": "completed"}

        response = test_client.put(f"/api/v1/entries/{entry_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entry_id
        assert data["title"] == "Updated Title"
        assert data["status"] == "completed"
        assert data["kind"] == created_entry["kind"]
        assert data["link"] == created_entry["link"]

    def test_update_entry_partial(self, test_client, created_entry):
        entry_id = created_entry["id"]
        update_data = {"status": "reading"}

        response = test_client.put(f"/api/v1/entries/{entry_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "reading"
        assert data["title"] == created_entry["title"]
        assert data["kind"] == created_entry["kind"]


class TestDeleteEntry:

    def test_delete_entry_success(self, test_client, created_entry):
        entry_id = created_entry["id"]

        response = test_client.delete(f"/api/v1/entries/{entry_id}")
        assert response.status_code == 204

        get_response = test_client.get(f"/api/v1/entries/{entry_id}")
        assert get_response.status_code == 404
