import os
from unittest.mock import MagicMock, patch

import pytest

from app.core.secrets import (
    Secret,
    SecretsManager,
    SecretsMaskingFilter,
    secrets_manager,
    setup_secrets,
)


class TestSecretsManager:

    def test_secret_registration(self, monkeypatch):
        monkeypatch.setenv("APP_TEST_SECRET", "test_secret_value")

        manager = SecretsManager(prefix="APP_")
        manager.register_secret("TEST_SECRET")

        assert "TEST_SECRET" in manager.secrets
        assert manager.get("TEST_SECRET") == "test_secret_value"
        assert manager.secrets["TEST_SECRET"].masked is True

    def test_secret_masking(self, monkeypatch):
        monkeypatch.setenv("APP_API_KEY", "sk-1234567890abcdef")

        manager = SecretsManager(prefix="APP_")
        manager.register_secret("API_KEY")

        original_text = (
            "API key is sk-1234567890abcdef and token is sk-1234567890abcdef"
        )
        masked_text = manager.mask_secrets(original_text)

        assert "sk-1234567890abcdef" not in masked_text
        assert "***API_KEY_MASKED***" in masked_text
        assert masked_text.count("***API_KEY_MASKED***") == 2

    def test_missing_required_secret(self):
        manager = SecretsManager(prefix="APP_")
        manager.register_secret("MISSING_SECRET", required=True)

        with patch.object(manager, "is_test_env", False):
            assert manager.validate() is False

    def test_optional_secret_handling(self):
        manager = SecretsManager(prefix="APP_")
        manager.register_secret("OPTIONAL_SECRET", required=False)

        assert manager.validate() is True

    def test_test_environment_behavior(self, monkeypatch):
        monkeypatch.setenv("TESTING", "true")

        manager = SecretsManager(prefix="APP_")
        manager.register_secret("TEST_SECRET", required=True)

        assert manager.get("TEST_SECRET") == "test_test_secret_value"
        assert manager.validate() is True

    def test_secret_access_with_default(self):
        manager = SecretsManager(prefix="APP_")
        manager.register_secret("NONEXISTENT_SECRET")

        assert manager.get("NONEXISTENT_SECRET", "default_value") == "default_value"
        assert manager.get("NONEXISTENT_SECRET") is None

    def test_multiple_secrets_masking(self, monkeypatch):
        monkeypatch.setenv("APP_DB_PASSWORD", "secret_db_pass")
        monkeypatch.setenv("APP_API_KEY", "secret_api_key")

        manager = SecretsManager(prefix="APP_")
        manager.register_secret("DB_PASSWORD")
        manager.register_secret("API_KEY")

        text = "DB: secret_db_pass, API: secret_api_key, DB again: secret_db_pass"
        masked = manager.mask_secrets(text)

        assert "secret_db_pass" not in masked
        assert "secret_api_key" not in masked
        assert "***DB_PASSWORD_MASKED***" in masked
        assert "***API_KEY_MASKED***" in masked

    def test_secret_object_creation(self):
        secret = Secret(name="TEST", value="test_value", required=True, masked=True)

        assert secret.name == "TEST"
        assert secret.value == "test_value"
        assert secret.required is True
        assert secret.masked is True


class TestSecretsMaskingFilter:

    def test_log_filter_masking(self, monkeypatch):
        monkeypatch.setenv("APP_JWT_SECRET", "very_secret_jwt_token")

        manager = SecretsManager(prefix="APP_")
        manager.register_secret("JWT_SECRET")

        log_filter = SecretsMaskingFilter(manager)
        record = MagicMock()

        record.msg = "JWT token: very_secret_jwt_token"
        log_filter.filter(record)

        assert "very_secret_jwt_token" not in record.msg
        assert "***JWT_SECRET_MASKED***" in record.msg

    def test_log_filter_with_args(self, monkeypatch):
        monkeypatch.setenv("APP_API_KEY", "sk-12345")

        manager = SecretsManager(prefix="APP_")
        manager.register_secret("API_KEY")

        log_filter = SecretsMaskingFilter(manager)
        record = MagicMock()

        record.msg = "API call with key: %s"
        record.args = ("sk-12345",)

        log_filter.filter(record)

        assert record.args[0] == "***API_KEY_MASKED***"

    def test_log_filter_skip_test_env(self, monkeypatch):
        monkeypatch.setenv("TESTING", "true")

        manager = SecretsManager(prefix="APP_")
        manager.register_secret("TEST_SECRET")
        manager.is_test_env = True

        log_filter = SecretsMaskingFilter(manager)
        record = MagicMock()
        record.msg = "Secret: test_secret_value"

        result = log_filter.filter(record)
        assert result is True
        assert record.msg == "Secret: test_secret_value"


class TestSecretsIntegration:

    def test_global_secrets_manager(self):
        assert isinstance(secrets_manager, SecretsManager)
        assert secrets_manager.prefix == "APP_"

    def test_setup_secrets_function(self, monkeypatch):
        monkeypatch.setenv("APP_JWT_SECRET", "test_jwt")
        monkeypatch.setenv("APP_DATABASE_URL", "sqlite:///test.db")
        monkeypatch.setenv("APP_API_KEY", "test_key")

        with patch.object(secrets_manager, "is_test_env", False):
            result = setup_secrets()
            assert result is True

    def test_required_secrets_validation(self, monkeypatch):
        monkeypatch.delenv("APP_JWT_SECRET", raising=False)
        monkeypatch.delenv("APP_DATABASE_URL", raising=False)
        monkeypatch.delenv("APP_API_KEY", raising=False)

        with patch.object(secrets_manager, "is_test_env", False):
            result = setup_secrets()
            assert result is False

    def test_secrets_in_test_environment(self):
        with patch.object(secrets_manager, "is_test_env", True):
            result = setup_secrets()
            assert result is True


def test_secrets_security_practices():
    manager = SecretsManager(prefix="APP_")

    manager.register_secret("PASSWORD", masked=True)
    manager.register_secret("TOKEN", masked=True)

    for secret_name, secret in manager.secrets.items():
        if secret.masked:
            assert secret.value not in manager.mask_secrets(f"Secret: {secret.value}")


@pytest.mark.parametrize(
    "secret_name,expected_env_name",
    [
        ("JWT_SECRET", "APP_JWT_SECRET"),
        ("DATABASE_URL", "APP_DATABASE_URL"),
        ("API_KEY", "APP_API_KEY"),
    ],
)
def test_environment_variable_names(secret_name, expected_env_name):
    manager = SecretsManager(prefix="APP_")

    with patch.dict(os.environ, {expected_env_name: "test_value"}):
        manager.register_secret(secret_name)
        assert manager.get(secret_name) == "test_value"
