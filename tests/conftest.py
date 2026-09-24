"""Test fixtures and shared constants."""

from __future__ import annotations

import pytest

from ezcapsolver import PollingConfig
from ezcapsolver.config import DEFAULT_ASYNC_BASE_URL, DEFAULT_SYNC_BASE_URL

CLIENT_KEY = "test-client-key"

CREATE_TASK_URL = f"{DEFAULT_ASYNC_BASE_URL}/createTask"
TASK_RESULT_URL = f"{DEFAULT_ASYNC_BASE_URL}/getTaskResult"
BALANCE_URL = f"{DEFAULT_ASYNC_BASE_URL}/getBalance"
SYNC_TASK_URL = f"{DEFAULT_SYNC_BASE_URL}/createSyncTask"

#: A ready ReCaptcha response, reused across several tests.
READY_RECAPTCHA = {
    "errorId": 0,
    "status": "ready",
    "solution": {"gRecaptchaResponse": "the-token", "sec_ch_ua": "ua", "user_agent": "UA"},
}


@pytest.fixture
def fast_polling() -> PollingConfig:
    """Squeeze the polling interval so tests do not actually sleep."""
    return PollingConfig(interval=0.001, max_attempts=5)


@pytest.fixture(autouse=True)
def _no_ambient_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clear the environment variable so a real key cannot leak into tests."""
    monkeypatch.delenv("EZCAPTCHA_API_KEY", raising=False)
