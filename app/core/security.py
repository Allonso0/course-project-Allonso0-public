import os

from slowapi import Limiter
from slowapi.util import get_remote_address

IS_TEST_ENV = os.getenv("TESTING") == "true" or os.getenv("PYTEST_CURRENT_TEST")

if IS_TEST_ENV:
    limiter = Limiter(key_func=get_remote_address, default_limits=[])
else:
    limiter = Limiter(
        key_func=get_remote_address, default_limits=["10 per minute", "100 per hour"]
    )

ENDPOINT_LIMITS = {
    "create_entry": "3 per minute" if not IS_TEST_ENV else None,
    "get_entries": "5 per minute" if not IS_TEST_ENV else None,
    "get_entry": "5 per minute" if not IS_TEST_ENV else None,
    "update_entry": "3 per minute" if not IS_TEST_ENV else None,
    "delete_entry": "2 per minute" if not IS_TEST_ENV else None,
    "health_check": "10 per minute" if not IS_TEST_ENV else None,
}
