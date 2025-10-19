from app.core.secrets import SecretsManager


class TestSecretsManager:

    def test_secret_registration(self, monkeypatch):
        monkeypatch.setenv("TEST_DB_PASSWORD", "secret123")
        manager = SecretsManager(prefix="TEST_")

        manager.register_secret("DB_PASSWORD")

        assert "DB_PASSWORD" in manager.secrets
        assert manager.get("DB_PASSWORD") == "secret123"

    def test_secret_masking(self, monkeypatch):
        monkeypatch.setenv("TEST_API_KEY", "sk-123456789")
        manager = SecretsManager(prefix="TEST_")
        manager.register_secret("API_KEY")

        masked = manager.mask_secrets("API key is sk-123456789")
        assert "sk-123456789" not in masked
        assert "***API_KEY_MASKED***" in masked

    def test_missing_required_secret(self):
        manager = SecretsManager(prefix="TEST_")
        manager.register_secret("MISSING_SECRET", required=True)

        assert manager.validate() is False
