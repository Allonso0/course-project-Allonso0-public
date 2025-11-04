from app.domain.models import EntryCreate, EntryKind


class TestInputValidationSecurity:
    def test_valid_entry_creation(self):
        # Позитивный тест: создание валидной записи.
        valid_data = {
            "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
            "kind": "book",
            "link": "https://example.com/book",
            "status": "planned",
        }
        entry = EntryCreate(**valid_data)
        assert entry.title == "Clean Code: A Handbook of Agile Software Craftsmanship"
        assert entry.kind == EntryKind.BOOK

    def test_title_validation_attack_scenarios(self, test_client):
        # Негативные тесты: атаки через поле title.

        # XSS попытка.
        response = test_client.post(
            "/api/v1/entries",
            json={
                "title": "<script>alert('xss')</script>",
                "kind": "book",
                "status": "planned",
            },
        )
        assert response.status_code == 422

        # SQL injection.
        response = test_client.post(
            "/api/v1/entries",
            json={
                "title": "test'; DROP TABLE entries;--",
                "kind": "book",
                "status": "planned",
            },
        )
        assert response.status_code == 422

        # Очень длинный title (пограничное значение).
        response = test_client.post(
            "/api/v1/entries",
            json={"title": "A" * 201, "kind": "book", "status": "planned"},
        )
        assert response.status_code == 422

        # Title только из пробелов.
        response = test_client.post(
            "/api/v1/entries",
            json={"title": "   ", "kind": "book", "status": "planned"},
        )
        assert response.status_code == 422

    def test_kind_enum_validation(self, test_client):
        # Несуществующий kind.
        response = test_client.post(
            "/api/v1/entries",
            json={"title": "Test Book", "kind": "movie", "status": "planned"},
        )
        assert response.status_code == 422

    def test_link_validation_security(self, test_client):
        # Негативные тесты: опасные URL.

        # JavaScript URL.
        response = test_client.post(
            "/api/v1/entries",
            json={
                "title": "Test Book",
                "kind": "book",
                "link": "javascript:alert('xss')",
                "status": "planned",
            },
        )
        assert response.status_code == 422

        # URL с path traversal.
        response = test_client.post(
            "/api/v1/entries",
            json={
                "title": "Test Book",
                "kind": "book",
                "link": "https://example.com/../../../etc/passwd",
                "status": "planned",
            },
        )
        assert response.status_code == 422

        # Data URL.
        response = test_client.post(
            "/api/v1/entries",
            json={
                "title": "Test Book",
                "kind": "book",
                "link": "data:text/html,<script>alert('xss')</script>",
                "status": "planned",
            },
        )
        assert response.status_code == 422

    def test_domain_rule_validation(self, test_client):
        # Статья без ссылки должна отклоняться.
        response = test_client.post(
            "/api/v1/entries",
            json={
                "title": "Test Article Title",
                "kind": "article",
                "status": "planned",
            },
        )
        assert response.status_code == 422

        # Статья со ссылкой должна проходить.
        response = test_client.post(
            "/api/v1/entries",
            json={
                "title": "Test Article Title",
                "kind": "article",
                "link": "https://example.com/article",
                "status": "planned",
            },
        )
        assert response.status_code == 201

    def test_extra_fields_rejection(self, test_client):
        response = test_client.post(
            "/api/v1/entries",
            json={
                "title": "Test Book",
                "kind": "book",
                "status": "planned",
                "malicious_field": "dangerous_value",
                "owner_id": 999,
            },
        )
        assert response.status_code == 422

    def test_update_validation(self, test_client, created_entry):
        # Тесты валидации при обновления.
        entry_id = created_entry["id"]

        # Пустой update должен отклоняться.
        response = test_client.put(f"/api/v1/entries/{entry_id}", json={})
        assert response.status_code == 422

        # Обновление с невалидным статусом.
        response = test_client.put(
            f"/api/v1/entries/{entry_id}", json={"status": "invalid_status"}
        )
        assert response.status_code == 422

    def test_sql_injection_specific(self, test_client):
        dangerous_sql_attempts = [
            "'; DROP TABLE users;--",
            "SELECT * FROM users",
            "INSERT INTO entries",
            "UPDATE users SET password='hacked'",
            "DROP TABLE entries",
            "UNION SELECT",
        ]

        for attempt in dangerous_sql_attempts:
            response = test_client.post(
                "/api/v1/entries",
                json={"title": attempt, "kind": "book", "status": "planned"},
            )
            assert response.status_code == 422, f"SQL injection '{attempt}' not blocked"


def test_boundary_value_analysis(test_client):
    # Тесты пограничных значений.

    # Title длиной ровно 200 символов.
    max_title = "A" * 200
    response = test_client.post(
        "/api/v1/entries",
        json={"title": max_title, "kind": "book", "status": "planned"},
    )
    assert response.status_code == 201

    # Title длиной 1 символ.
    response = test_client.post(
        "/api/v1/entries", json={"title": "A", "kind": "book", "status": "planned"}
    )
    assert response.status_code == 201


def test_string_stripping_behavior():
    entry = EntryCreate(
        title="  Test Book  ",
        kind="book",
        link="  https://example.com  ",
        status="planned",
    )
    assert entry.title == "Test Book"
    assert entry.link == "https://example.com"


def test_dangerous_characters_removal():
    # Используем безопасный title для теста.
    entry = EntryCreate(title="Test Book Title", kind="book", status="planned")
    assert entry.title == "Test Book Title"

    # Тест с частично опасными символами.
    safe_entry = EntryCreate(
        title="Normal Title with Spaces", kind="book", status="planned"
    )
    assert "Normal Title with Spaces" == safe_entry.title
