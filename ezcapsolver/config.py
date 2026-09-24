"""Client configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass, field, replace
from typing import Self

from .errors import _config_error

__all__ = [
    "DEFAULT_ASYNC_BASE_URL",
    "DEFAULT_CLIENT_KEY_ENV",
    "DEFAULT_SYNC_BASE_URL",
    "ClientConfig",
    "PollingConfig",
]

#: Base URL for asynchronous tasks and balance queries.
DEFAULT_ASYNC_BASE_URL = "https://api.ez-captcha.com"

#: Base URL for synchronous tasks. The service hosts them on a separate domain.
DEFAULT_SYNC_BASE_URL = "https://sync.ez-captcha.com"

#: Environment variable read when no client key is passed explicitly.
DEFAULT_CLIENT_KEY_ENV = "EZCAPTCHA_API_KEY"


@dataclass(frozen=True, slots=True, kw_only=True)
class PollingConfig:
    """Polling settings used while waiting for an asynchronous task.

    Attributes:
        interval: Delay in seconds before every result query, including the
            first one.
        max_attempts: Maximum number of result queries before giving up.
    """

    #: Newly created tasks are still queued, so an immediate query almost always returns
    #: processing. Wait one interval before polling to avoid that unnecessary request.
    interval: float = 3.0
    max_attempts: int = 50

    def __post_init__(self) -> None:
        """Validate that the polling budget is positive."""
        if self.interval <= 0:
            raise _config_error("polling interval must be greater than zero")
        if self.max_attempts <= 0:
            raise _config_error("maximum polling attempts must be greater than zero")

    @property
    def budget_seconds(self) -> float:
        """Total polling budget in seconds, for logging and documentation."""
        return self.interval * self.max_attempts


@dataclass(frozen=True, slots=True, kw_only=True)
class ClientConfig:
    """Configuration shared by the synchronous and asynchronous clients.

    Attributes:
        client_key: API credential. Read from the environment when omitted.
        async_base_url: Base URL for asynchronous tasks and balance queries.
        sync_base_url: Base URL for synchronous tasks.
        timeout: Per-request timeout in seconds for asynchronous endpoints and
            balance queries.
        sync_timeout: Per-request timeout in seconds for the synchronous task
            endpoint.
        polling: Polling settings for asynchronous tasks.
        app_id: Optional developer application identifier.
        proxy: Proxy the SDK itself uses to reach the EzCaptchaSolver API.
        user_agent: User-Agent sent with every request.

    Note:
        Passing an ``httpx`` client with its own ``base_url`` does **not**
        redirect the SDK: it always builds absolute URLs, and ``httpx`` applies
        ``base_url`` only to relative ones. Set the two fields below instead.
    """

    client_key: str | None = None

    #: Base URL for asynchronous tasks and balance queries. Override it to reach a private
    #: gateway or a test server. The service splits the two deployments, so they cannot
    #: share one host.
    async_base_url: str = DEFAULT_ASYNC_BASE_URL

    #: Base URL for synchronous tasks.
    sync_base_url: str = DEFAULT_SYNC_BASE_URL

    #: Async endpoints enqueue tasks or query results in milliseconds. A shorter timeout
    #: helps distinguish network failures from slow server responses.
    timeout: float = 30.0

    #: Sync calls block until the worker returns a result; the slowest task types are
    #: granted a 180-second worker deadline. Reusing the async timeout would cut off a call
    #: that the server is still billing for, and a call that times out never receives the
    #: task ID it would take to recover the result. 240 leaves a minute of headroom.
    sync_timeout: float = 240.0

    polling: PollingConfig = field(default_factory=PollingConfig)
    app_id: int | None = None
    proxy: str | None = None
    user_agent: str = ""

    def __post_init__(self) -> None:
        """Validate the timeouts and fill in the default User-Agent."""
        if not self.async_base_url.strip() or not self.sync_base_url.strip():
            raise _config_error("base URLs must not be blank")
        if self.timeout <= 0:
            raise _config_error("timeout must be greater than zero")
        if self.sync_timeout <= 0:
            raise _config_error("sync timeout must be greater than zero")
        if not self.user_agent:
            # A frozen dataclass requires this assignment to set the default. Set it here
            # so the default User-Agent always reflects the currently installed version.
            object.__setattr__(self, "user_agent", _default_user_agent())

    def resolve_client_key(self) -> str:
        """Return a usable client key.

        Raises:
            EzCaptchaError: The key is missing or blank.
        """
        client_key = self.client_key
        if client_key is None:
            client_key = os.environ.get(DEFAULT_CLIENT_KEY_ENV)
        if client_key is None:
            raise _config_error(
                f"client key is unavailable: pass client_key= or set the "
                f"{DEFAULT_CLIENT_KEY_ENV} environment variable"
            )
        if not client_key.strip():
            raise _config_error("client key must not be blank")
        return client_key

    def evolve(self, **changes: object) -> Self:
        """Return a copy with only the named fields changed."""
        return replace(self, **changes)  # type: ignore[arg-type]

    def __repr__(self) -> str:
        """Hide the client key so printing the config cannot leak it."""
        redacted = "***" if self.client_key else None
        return (
            f"ClientConfig(client_key={redacted!r}, "
            f"async_base_url={self.async_base_url!r}, sync_base_url={self.sync_base_url!r}, "
            f"timeout={self.timeout!r}, sync_timeout={self.sync_timeout!r}, "
            f"polling={self.polling!r}, app_id={self.app_id!r}, proxy={self.proxy!r}, "
            f"user_agent={self.user_agent!r})"
        )


def _default_user_agent() -> str:
    """Build the User-Agent identifying this SDK and its version."""
    from . import __version__

    return f"ezcapsolver-py/{__version__}"
