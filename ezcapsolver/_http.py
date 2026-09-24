"""Request construction, envelope parsing and redacted logging.

Everything here is a pure function; no I/O. The two clients only differ in how
they send the request — parsing shares this one implementation.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Final

from .errors import ApiError, UnexpectedResponseError, _config_error

logger = logging.getLogger("ezcapsolver")
# Follow library conventions: attach only a NullHandler and let the host configure output.
logger.addHandler(logging.NullHandler())

#: Level for full request and response bodies, one step below ``DEBUG``.
#:
#: Bodies sit below ``DEBUG`` on purpose. A DataDome ``html_b64`` or an Akamai
#: ``script_base64`` runs to megabytes, so mixing them into ``DEBUG`` would make the
#: level unusable for watching the task lifecycle, which is what it is for. The Go
#: SDK draws the same line with its own ``LevelTrace``.
TRACE: Final = 5
logging.addLevelName(TRACE, "TRACE")

#: JSON keys whose values contain credentials and must never be logged.
_REDACTED_KEYS: Final = frozenset({"clientKey", "proxy"})

#: Body characters retained in logs. Error envelopes fit; solved tokens and oversized
#: task parameters are truncated, which is the point.
_LOG_PREVIEW = 256

#: Response body characters retained in errors. Debugging context takes priority over brevity.
_ERROR_PREVIEW = 512

#: Header carrying the client key on every request, alongside the ``clientKey`` body field.
CLIENT_KEY_HEADER: Final = "X-API-Key"

CREATE_TASK = "/createTask"
GET_TASK_RESULT = "/getTaskResult"
CREATE_SYNC_TASK = "/createSyncTask"
GET_BALANCE = "/getBalance"


def client_key_headers(client_key: str) -> dict[str, str]:
    """Build the client-key header once, when a client is created.

    A key that cannot travel as a header value is rejected here as a configuration
    error, rather than failing every request later with an opaque transport error.

    Raises:
        EzCaptchaError: The key holds a character an HTTP header value cannot carry.
    """
    # httpx encodes header values as ASCII, and h11 rejects control characters and
    # surrounding whitespace, so the key has to be printable ASCII with no padding.
    if not (client_key.isascii() and client_key.isprintable()) or client_key != client_key.strip():
        raise _config_error("client key contains invalid characters")
    return {CLIENT_KEY_HEADER: client_key}


def endpoint(base_url: str, path: str) -> str:
    """Join a base URL and a path, tolerating slashes on either side."""
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def _preview(text: str, limit: int) -> str:
    """Truncate overlong text to ``limit`` characters."""
    return text if len(text) <= limit else f"{text[:limit]}..."


def redact(value: Any) -> Any:
    """Replace credential fields with a placeholder, at any depth."""
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if key in _REDACTED_KEYS else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def task_payload(
    *, client_key: str, task_type: str, params: dict[str, Any], app_id: int | None
) -> dict[str, Any]:
    """Build the body for ``createTask`` and ``createSyncTask``.

    The task type goes in as a ``type`` key *inside* the task object, which is
    the shape the service requires.

    It is written last so the SDK's choice always wins over a ``type`` carried
    in the parameters, whether that came from a model's ``extra``, a shortcut's
    ``**extra``, or the raw entry point. A caller who reached for one task type
    and sent another gets a task billed and executed as the second one, while
    the result is still decoded as the first.
    """
    payload: dict[str, Any] = {
        "clientKey": client_key,
        "task": {**params, "type": task_type},
    }
    if app_id is not None:
        payload["appId"] = app_id
    return payload


def parse_response(status: int, body: bytes) -> dict[str, Any]:
    """Parse the response envelope.

    Args:
        status: HTTP status code.
        body: Raw response body.

    Returns:
        The parsed response dictionary.

    Raises:
        ApiError: ``errorId`` is non-zero, or the status is not 2xx.
        UnexpectedResponseError: A 2xx response whose body is not a JSON object.
    """
    text = body.decode("utf-8", errors="replace")
    ok_status = 200 <= status < 300

    try:
        parsed = json.loads(text) if text else None
    except json.JSONDecodeError as exc:
        # A non-success status without JSON is still a server error. Report it in the same
        # form as an error envelope so callers can always read the status from one place.
        if not ok_status:
            raise _status_only(status, text) from exc
        raise UnexpectedResponseError(
            f"response body is not valid JSON: {exc}", body=_preview(text, _ERROR_PREVIEW)
        ) from exc

    if not isinstance(parsed, dict):
        if not ok_status:
            raise _status_only(status, text)
        raise UnexpectedResponseError(
            f"expected a JSON object, got {type(parsed).__name__}",
            body=_preview(text, _ERROR_PREVIEW),
        )

    # errorId is the sole criterion: the server sets it on every response, and 0 means success.
    # Treating a nonempty errorCode as another failure signal could reject a solved task if
    # success codes are added later. Every server-defined error already has a nonzero errorId.
    if int(parsed.get("errorId", 0) or 0) != 0:
        raise ApiError(
            error_code=parsed.get("errorCode"),
            error_description=parsed.get("errorDescription"),
            request_id=parsed.get("requestId"),
            errors=parsed.get("errors") or {},
            http_status=status,
        )

    if not ok_status:
        raise _status_only(status, text)

    return parsed


def _status_only(status: int, text: str) -> ApiError:
    """Build an error for a non-success response that carried no envelope."""
    return ApiError(error_description=_preview(text, _ERROR_PREVIEW), http_status=status)


def log_request(url: str, payload: dict[str, Any]) -> None:
    """Log an outgoing request with credentials redacted.

    The body is not rendered at all below TRACE, so this costs nothing at the
    default log level.
    """
    if logger.isEnabledFor(TRACE):
        logger.log(
            TRACE,
            "POST %s body=%s",
            url,
            _preview(str(redact(payload)), _LOG_PREVIEW),
        )


def log_response(url: str, status: int, elapsed_ms: float, body: bytes) -> None:
    """Log a response's status, duration, size and truncated body."""
    if logger.isEnabledFor(TRACE):
        logger.log(
            TRACE,
            "POST %s -> %s in %.1fms (%d bytes) body=%s",
            url,
            status,
            elapsed_ms,
            len(body),
            _preview(body.decode("utf-8", errors="replace"), _LOG_PREVIEW),
        )
