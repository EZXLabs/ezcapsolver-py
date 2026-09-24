"""Response models."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Final, Self

from .errors import UnexpectedResponseError

__all__ = ["MISSING", "Solved", "TaskResult", "TaskStatus"]


class _Missing:
    """Sentinel type meaning "the response had no such field at all"."""

    __slots__ = ()

    def __repr__(self) -> str:
        """Keep debug output readable."""
        return "MISSING"

    def __bool__(self) -> bool:
        """Always falsy, so ``if not result.solution`` reads naturally."""
        return False


#: Distinguishes "field absent" from "field is JSON null". The former means the
#: task has not finished; the latter means the worker returned an empty result.
#: These two must stay tellable apart.
MISSING: Final[Any] = _Missing()


class TaskStatus(StrEnum):
    """Task status. The service reports exactly these three, so it is closed."""

    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskResult:
    """Response of ``getTaskResult`` and ``createSyncTask``.

    Attributes:
        status: Current task status.
        solution: Raw solution value, or :data:`MISSING` when the response
            carried no such field, which is different from a ``None`` value.
        task_id: Identifier the synchronous endpoint assigns. ``createSyncTask``
            returns one on both the success and the failure path;
            ``getTaskResult`` does not echo it back, so it is ``None`` there.
        request_id: Server-side request tracking identifier.
        error_code: Task-level error code.
        error_description: Task-level error description.
    """

    status: TaskStatus
    solution: Any = MISSING
    task_id: str | None = None
    request_id: str | None = None
    error_code: str | None = None
    error_description: str | None = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Self:
        """Build from a response dictionary.

        Raises:
            UnexpectedResponseError: ``status`` is missing, or its value is not
                one of the three the contract declares.
        """
        raw_status = data.get("status")
        if raw_status is None:
            # Request-level failures (invalid key, unknown task ID) may omit status,
            # but their error envelopes are handled before reaching this code.
            # A missing status here therefore violates the API contract.
            raise UnexpectedResponseError(
                "successful task response does not contain a status field",
                body=repr(dict(data)),
            )
        try:
            status = TaskStatus(raw_status)
        except ValueError as exc:
            raise UnexpectedResponseError(
                f"unknown task status {raw_status!r}", body=repr(dict(data))
            ) from exc

        return cls(
            status=status,
            solution=data.get("solution", MISSING),
            task_id=data.get("taskId"),
            request_id=data.get("requestId"),
            error_code=data.get("errorCode"),
            error_description=data.get("errorDescription"),
        )

    @property
    def has_solution(self) -> bool:
        """Whether the response carried a solution field, ``None`` included."""
        return self.solution is not MISSING

    @property
    def is_processing(self) -> bool:
        """Whether the task is still being processed."""
        return self.status is TaskStatus.PROCESSING

    @property
    def is_ready(self) -> bool:
        """Whether the task completed successfully."""
        return self.status is TaskStatus.READY

    @property
    def is_error(self) -> bool:
        """Whether the task failed."""
        return self.status is TaskStatus.ERROR


@dataclass(frozen=True, slots=True, kw_only=True)
class Solved[S]:
    """A solved task.

    :attr:`raw` always keeps the JSON the worker returned, regardless of whether
    :attr:`solution` decoded — anything the typed model omits is recoverable
    from there.

    Attributes:
        solution: The decoded result. For task types whose shape is unconfirmed
            this is the raw value itself.
        raw: The untouched solution JSON the worker returned.
        task_id: Identifier the service assigned. Both endpoints supply one:
            the asynchronous path from task creation, the synchronous path
            alongside the result.
        request_id: Server-side request tracking identifier.
    """

    solution: S
    raw: Any = None
    task_id: str | None = None
    request_id: str | None = None
