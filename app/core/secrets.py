import logging
import os
import re
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Secret:
    name: str
    value: str
    required: bool = True
    masked: bool = True


class SecretsManager:

    def __init__(self, prefix: str = "APP_"):
        self.prefix = prefix
        self.secrets: Dict[str, Secret] = {}
        self.logger = logging.getLogger(__name__)
        self._mask_patterns = []
        self.is_test_env = os.getenv("TESTING") == "true" or os.getenv(
            "PYTEST_CURRENT_TEST"
        )

    def register_secret(self, name: str, required: bool = True, masked: bool = True):
        env_name = f"{self.prefix}{name.upper()}"
        value = os.getenv(env_name)

        if self.is_test_env and required and not value:
            value = f"test_{name.lower()}_value"

        secret = Secret(name=name, value=value, required=required, masked=masked)

        self.secrets[name] = secret

        if masked and value and not self.is_test_env:
            pattern = re.escape(value)
            self._mask_patterns.append((pattern, f"***{name.upper()}_MASKED***"))

    def validate(self) -> bool:
        if self.is_test_env:
            self.logger.info("Test environment - skipping secrets validation")
            return True

        missing = []

        for name, secret in self.secrets.items():
            if secret.required and not secret.value:
                missing.append(f"{self.prefix}{name.upper()}")

        if missing:
            self.logger.error(f"Missing required secrets: {', '.join(missing)}")
            return False

        self.logger.info(f"Successfully validated {len(self.secrets)} secrets")
        return True

    def get(self, name: str, default: Optional[str] = None) -> Optional[str]:
        secret = self.secrets.get(name)
        if secret and secret.value:
            return secret.value
        return default

    def mask_secrets(self, text: str) -> str:
        if not text or self.is_test_env:
            return text

        masked_text = text
        for pattern, replacement in self._mask_patterns:
            masked_text = re.sub(pattern, replacement, masked_text)

        return masked_text


class SecretsMaskingFilter(logging.Filter):

    def __init__(self, secrets_manager: SecretsManager):
        super().__init__()
        self.secrets_manager = secrets_manager

    def filter(self, record: logging.LogRecord) -> bool:
        if self.secrets_manager.is_test_env:
            return True

        if hasattr(record, "msg") and record.msg:
            record.msg = self.secrets_manager.mask_secrets(str(record.msg))

        if hasattr(record, "args") and record.args:
            new_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    new_args.append(self.secrets_manager.mask_secrets(arg))
                else:
                    new_args.append(arg)
            record.args = tuple(new_args)

        return True


secrets_manager = SecretsManager(prefix="APP_")


def setup_secrets() -> bool:
    secrets_manager.register_secret("JWT_SECRET", required=True)
    secrets_manager.register_secret("DATABASE_URL", required=True)
    secrets_manager.register_secret("API_KEY", required=True)

    secrets_manager.register_secret("VAULT_ADDR", required=False)
    secrets_manager.register_secret("VAULT_TOKEN", required=False)

    if not secrets_manager.validate():
        return False

    if not secrets_manager.is_test_env:
        for handler in logging.getLogger().handlers:
            handler.addFilter(SecretsMaskingFilter(secrets_manager))

    return True
