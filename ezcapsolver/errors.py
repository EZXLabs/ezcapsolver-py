"""Exception hierarchy.

Catching :class:`EzCaptchaError` alone covers every failure path in the SDK,
including model parsing. A bare ``ValueError``, ``KeyError`` or built-in
``TimeoutError`` must never escape the SDK boundary.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "ApiError",
    "EzCaptchaError",
    "PollingExhaustedError",
    "SolutionDecodeError",
    "TransportError",
    "UnexpectedResponseError",
    "WaitInterruptedError",
    "task_id_of",
]

# Limit raw-value previews in decode error messages so long worker responses do not obscure
# the remaining details. The full raw value is still available on the exception.
_PREVIEW_CHARS = 512


def _preview(text: str, limit: int = _PREVIEW_CHARS) -> str:
    """Truncate overlong text, marking the cut with an ellipsis."""
    if len(text) <= limit:
        return text
    return f"{text[:limit]}..."


class EzCaptchaError(Exception):
    """Base class for every exception raised by this SDK.

    It is also raised directly for a failure whose only useful detail is its
    message, an invalid client configuration being the one case today. Anything
    a caller would react to programmatically gets a subclass of its own.
    """


def _config_error(detail: str) -> EzCaptchaError:
    """Build the plain SDK error reporting an invalid client configuration.

    The prefix lives here rather than at each call site so every configuration
    failure reads the same way. These are raised while a client is being built,
    never once one is in use, so nothing has been billed when one surfaces.
    """
    return EzCaptchaError(f"invalid client configuration: {detail}")


class TransportError(EzCaptchaError):
    """An HTTP transport failure: connection error, timeout, TLS failure.

    Attributes:
        cause: The underlying httpx exception, for classifying the failure
            further.
    """

    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        """Record the message and the underlying exception."""
        super().__init__(message)
        self.cause = cause


class UnexpectedResponseError(EzCaptchaError):
    """The response is unusable: it did not decode, or it violated the contract.

    A ready result carrying no solution field lands here too: the task was
    billed and the answer is gone, which is a broken contract rather than a
    category of its own. ``TaskResult.has_solution`` still tells that case apart
    from a solution that was present and null.

    Attributes:
        body: A slice of the raw response body, the only thing available for
            diagnosis.
    """

    def __init__(self, message: str, *, body: str | None = None) -> None:
        """Record the message and a slice of the raw body."""
        super().__init__(message)
        self.body = body


class ApiError(EzCaptchaError):
    """The service returned a structured business error, or any non-2xx status.

    ``errorId != 0`` is the sole discriminator. A non-2xx response without an
    error envelope lands here too, so :attr:`http_status` is always readable.

    Attributes:
        error_code: Stable machine-readable code, such as ``ERROR_ZERO_BALANCE``.
        error_description: Human-readable description.
        request_id: Server-side request tracking identifier.
        task_id: Set for errors that happen after a task was created.
        errors: Field-level validation errors, keyed by field path.
        http_status: The HTTP status that carried the error.
    """

    def __init__(
        self,
        message: str = "",
        *,
        error_code: str | None = None,
        error_description: str | None = None,
        request_id: str | None = None,
        task_id: str | None = None,
        errors: dict[str, str] | None = None,
        http_status: int = 0,
    ) -> None:
        """Assemble the error, synthesising a message when none is given."""
        self.error_code = error_code
        self.error_description = error_description
        self.request_id = request_id
        self.task_id = task_id
        self.errors = errors or {}
        self.http_status = http_status
        super().__init__(message or self._build_message())

    def _build_message(self) -> str:
        """Render as ``CODE: description (HTTP nnn); field: reason``."""
        code = self.error_code or "UNKNOWN_API_ERROR"
        description = self.error_description or "The API returned an unspecified error"
        message = f"{code}: {description} (HTTP {self.http_status})"
        # Include field names in the message so validation failures are actionable at a glance.
        if self.errors:
            details = ", ".join(f"{field}: {reason}" for field, reason in self.errors.items())
            message = f"{message}; {details}"
        return message

    def is_authentication_error(self) -> bool:
        """Whether this is a credential or balance problem.

        Thirty of these within a minute trigger a three-minute server-side ban,
        so a caller should stop retrying rather than back off and try again.
        """
        return self.error_code in _AUTH_ERROR_CODES

    def is_terminal(self) -> bool:
        """Whether resending the identical request would fail identically.

        An unrecognised code returns ``False``, because a code this release has
        not seen may well be transient and the SDK should not talk a caller out
        of a retry that would have worked. ``False`` is not a promise that
        retrying is safe — the retry policy stays with the caller.
        """
        return self.error_code in _TERMINAL_ERROR_CODES

    def is_rate_limited(self) -> bool:
        """Whether the service refused the request for throttling alone.

        Both codes are transient by construction: a rate limit resets with its
        window and a ban expires on its own. Neither says anything about a task
        -- the query is refused before the service looks it up -- so
        :meth:`~ezcapsolver.EzCapSolverClient.wait_for_result` treats one as a
        skipped attempt instead of a failed task, and a caller polling by hand
        with :meth:`~ezcapsolver.EzCapSolverClient.get_result` should do the same.

        This is narrower than ``not is_terminal()``, which is also true of every
        unrecognised code -- including the worker codes that report a task that
        genuinely failed.
        """
        return self.error_code in _RATE_LIMITED_ERROR_CODES


class PollingExhaustedError(EzCaptchaError):
    """Polling ran out before the task reached a terminal state.

    Attributes:
        task_id: The unfinished task, usable to fetch the result manually later.
        attempts: Number of completed result queries.
        interval: Delay between queries, in seconds.
    """

    def __init__(self, *, task_id: str, attempts: int, interval: float) -> None:
        """Record the task identifier and the polling budget."""
        super().__init__(
            f"task {task_id!r} did not complete after {attempts} polling attempts "
            f"at {interval}s intervals"
        )
        self.task_id = task_id
        self.attempts = attempts
        self.interval = interval


class WaitInterruptedError(EzCaptchaError):
    """The task was created and billed, but waiting for its result failed.

    :meth:`~ezcapsolver.EzCapSolverClient.solve` creates the task internally, so
    this exception is the only place its identifier appears. Recover by waiting
    on the same task again with
    :meth:`~ezcapsolver.EzCapSolverClient.wait_for_result` rather than creating a
    second one: the service holds a result for five minutes after creation, and
    a new task is billed again.

    The failure that interrupted the wait stays reachable as ``__cause__``.

    Errors that carry the identifier themselves are not wrapped: a business
    failure still arrives as :class:`ApiError` with ``task_id`` set, and an
    exhausted budget as :class:`PollingExhaustedError`.

    Attributes:
        task_id: Identifier of the task that was created and billed.
        request_id: Correlation id of the creating request, when the service
            supplied one.
    """

    def __init__(self, *, task_id: str, request_id: str | None, cause: Exception) -> None:
        """Record the identifiers and the failure that interrupted the wait."""
        super().__init__(f"task {task_id!r} was created but waiting for its result failed: {cause}")
        self.task_id = task_id
        self.request_id = request_id


def task_id_of(error: BaseException) -> str | None:
    """Return the id of a task that was created and billed, if ``error`` left one.

    Creating a task is what costs money, so a failure after that point leaves a
    result worth recovering: wait on this id again with
    :meth:`~ezcapsolver.EzCapSolverClient.wait_for_result` instead of creating a
    second task. The service holds a result for five minutes after creation.

    ``None`` means nothing was billed — the failure happened before or during
    task creation, so there is nothing to recover.

    Which exception carries the id is an implementation detail; this is the one
    place to ask.

    Example:
        >>> from ezcapsolver import task_id_of
        >>> task_id = task_id_of(error)  # doctest: +SKIP
        >>> if task_id:  # doctest: +SKIP
        ...     solved = client.wait_for_result(task_id)
    """
    if isinstance(error, WaitInterruptedError | PollingExhaustedError | ApiError):
        return error.task_id
    return None


class SolutionDecodeError(EzCaptchaError):
    """The raw solution could not be decoded into the target model.

    The raw value travels with the error: a decode failure means the worker
    returned a shape this release does not model, and that shape is exactly
    what is needed to diagnose it.

    Attributes:
        raw: The complete raw solution value, untruncated.
        cause: The underlying parsing exception.
    """

    def __init__(self, *, raw: Any, cause: Exception) -> None:
        """Keep the full raw value; put a truncated preview in the message."""
        preview = _preview(repr(raw))
        super().__init__(f"failed to decode task solution: {cause}; raw solution: {preview}")
        self.raw = raw
        self.cause = cause


# The three codes @ApiDefenses lists on the service's AsyncTaskController: thirty of
# them against /createTask within a minute earn a three-minute ban. Retrying them
# does not waste a call so much as cause the ban.
_AUTH_ERROR_CODES = frozenset(
    {
        "ERROR_KEY_DOES_NOT_EXIST",
        "ERROR_KEY_NOT_AVAILABLE",
        "ERROR_ZERO_BALANCE",
    }
)

# The remaining codes are left out on purpose: internal errors, rate limits, bans,
# and the two synchronous-worker faults ERROR_SERVICE_UNAVAILABLE and
# ERROR_SERVICE_TIMEOUT can all clear on their own.
_TERMINAL_ERROR_CODES = frozenset(
    {
        "ERROR_CONTENT_TYPE_ERROR",
        "ERROR_KEY_DOES_NOT_EXIST",
        "ERROR_KEY_NOT_AVAILABLE",
        "ERROR_NOT_FOUND",
        "ERROR_PACKAGE_NOT_EXIST",
        "ERROR_PACKAGE_TASK_TYPE_NOT_SUPPORTED",
        "ERROR_REQUEST_METHOD",
        "ERROR_REQUEST_PARAMETERS",
        "ERROR_REQUEST_PROXY_MISSING",
        "ERROR_SUBSCRIPTION_EXPIRED",
        "ERROR_TASK_NOT_EXIST",
        "ERROR_TASK_TYPE_NOT_ALLOWED",
        "ERROR_TASK_TYPE_NOT_AVAILABLE",
        "ERROR_TASK_TYPE_NOT_SUPPORTED",
        "ERROR_WEBSITE_NOT_ALLOWED",
        "ERROR_ZERO_BALANCE",
    }
)

# The service's two throttling codes, both HTTP 429. /getTaskResult counts only the
# first two authentication codes towards its ban counter, so polling through a
# refusal does not dig the hole deeper.
_RATE_LIMITED_ERROR_CODES = frozenset({"ERROR_REQUEST_LIMIT", "ERROR_REQUEST_BANNED"})
