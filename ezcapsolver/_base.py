"""Parts shared by the synchronous and asynchronous clients.

The two clients differ only in how they send a request and how they wait.
Configuration merging, payload construction and result decoding live here so
they are not written twice.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from typing import Any, NoReturn, cast

from . import _http
from .config import ClientConfig, PollingConfig
from .errors import (
    ApiError,
    EzCaptchaError,
    PollingExhaustedError,
    UnexpectedResponseError,
    WaitInterruptedError,
)
from .responses import Solved, TaskResult
from .tasks import Task


class BaseClient:
    """Configuration handling plus the pure request/response logic."""

    __slots__ = ("_client_key", "_config", "_http", "_key_headers", "_owns_http")

    def __init__(
        self,
        client_key: str | None,
        *,
        config: ClientConfig | None,
        async_base_url: str | None,
        sync_base_url: str | None,
        timeout: float | None,
        sync_timeout: float | None,
        polling: PollingConfig | None,
        app_id: int | None,
        proxy: str | None,
        user_agent: str | None,
    ) -> None:
        """Merge the configuration, resolve the client key and build its header."""
        changes: dict[str, Any] = {
            "client_key": client_key,
            "async_base_url": async_base_url,
            "sync_base_url": sync_base_url,
            "timeout": timeout,
            "sync_timeout": sync_timeout,
            "polling": polling,
            "app_id": app_id,
            "proxy": proxy,
            "user_agent": user_agent,
        }
        # None preserves the existing value rather than clearing it.
        given = {key: value for key, value in changes.items() if value is not None}
        base = config or ClientConfig()
        self._config = replace(base, **given) if given else base
        self._client_key = self._config.resolve_client_key()
        self._key_headers = _http.client_key_headers(self._client_key)

    @property
    def config(self) -> ClientConfig:
        """Return this client's configuration."""
        return self._config

    # -- Request construction ---------------------------------------------

    def _create_task_request(self, task: Task[Any]) -> tuple[str, dict[str, Any]]:
        """Build the creation request for an asynchronous task."""
        return (
            _http.endpoint(self._config.async_base_url, _http.CREATE_TASK),
            self._task_payload(task.task_type, task.to_dict()),
        )

    def _sync_task_request(self, task: Task[Any]) -> tuple[str, dict[str, Any]]:
        """Build the execution request for a synchronous task."""
        return (
            _http.endpoint(self._config.sync_base_url, _http.CREATE_SYNC_TASK),
            self._task_payload(task.task_type, task.to_dict()),
        )

    def _raw_request(
        self, task_type: str, params: Mapping[str, Any], *, sync: bool
    ) -> tuple[str, dict[str, Any]]:
        """Escape hatch: any task type with any parameter dictionary."""
        base = self._config.sync_base_url if sync else self._config.async_base_url
        path = _http.CREATE_SYNC_TASK if sync else _http.CREATE_TASK
        return _http.endpoint(base, path), self._task_payload(task_type, dict(params))

    def _result_request(self, task_id: str) -> tuple[str, dict[str, Any]]:
        """Build a task result query."""
        return (
            _http.endpoint(self._config.async_base_url, _http.GET_TASK_RESULT),
            {"clientKey": self._client_key, "taskId": task_id},
        )

    def _balance_request(self) -> tuple[str, dict[str, Any]]:
        """Build a balance query."""
        return (
            _http.endpoint(self._config.async_base_url, _http.GET_BALANCE),
            {"clientKey": self._client_key},
        )

    def _task_payload(self, task_type: str, params: dict[str, Any]) -> dict[str, Any]:
        """Wrap a task type and its parameters in the envelope the API wants."""
        return _http.task_payload(
            client_key=self._client_key,
            task_type=task_type,
            params=params,
            app_id=self._config.app_id,
        )

    # -- Response handling ------------------------------------------------

    @staticmethod
    def _task_id_of(data: dict[str, Any]) -> str:
        """Extract the task identifier from a creation response."""
        task_id = data.get("taskId")
        if not isinstance(task_id, str) or not task_id:
            raise UnexpectedResponseError(
                "successful create-task response does not contain a task ID",
                body=repr(data),
            )
        return task_id

    @classmethod
    def _created_of(cls, data: dict[str, Any]) -> tuple[str, str | None]:
        """Extract the task identifier and the creating request's tracking id."""
        request_id = data.get("requestId")
        return cls._task_id_of(data), request_id if isinstance(request_id, str) else None

    @staticmethod
    def _require_terminal(result: TaskResult) -> TaskResult:
        """Reject a result that is not a finished, successful task.

        A failed task normally arrives with ``errorId`` 1 and has already become
        an :class:`~ezcapsolver.errors.ApiError`, so reaching here means the
        envelope contradicted itself. Returning it as a solution would hand the
        caller a ``Solved`` with nothing in it.
        """
        if not result.is_ready:
            detail = "still processing" if result.is_processing else "reported status `error`"
            raise UnexpectedResponseError(f"task result {detail} without an API error")
        return result

    @staticmethod
    def _balance_of(data: dict[str, Any]) -> float:
        """Extract the balance from a balance response.

        A missing or non-numeric ``balance`` is a contract break, not a zero
        balance — and the two call for opposite reactions, so they must not look
        alike. The service always sends a JSON number here.
        """
        balance = data.get("balance")
        if not isinstance(balance, (int, float)) or isinstance(balance, bool):
            raise UnexpectedResponseError(
                "balance response does not contain a numeric balance", body=repr(data)
            )
        return float(balance)

    def _solved[S](
        self,
        task: Task[S],
        result: TaskResult,
        task_id: str | None = None,
        request_id: str | None = None,
    ) -> Solved[S]:
        """Decode a task result into its target model.

        Raises:
            UnexpectedResponseError: The result is not in the ready state, or it
                is ready but carried no solution field.
            SolutionDecodeError: The raw value does not fit the model.
        """
        self._require_terminal(result)
        if not result.has_solution:
            raise UnexpectedResponseError("ready task result does not contain a solution")

        raw = result.solution
        model = task.solution_type
        # Task types with unconfirmed solution shapes have no model; return raw data (S is Any).
        # The relationship between the ClassVar and S is defined by each task class.
        # Type checkers cannot infer that relationship, so an explicit cast is needed here.
        solution = cast("S", model.from_dict(raw) if model is not None else raw)
        return Solved(
            solution=solution,
            raw=raw,
            # On the asynchronous path the caller passes in the id from creation.
            # The synchronous path has none, so the response supplies it.
            task_id=task_id or result.task_id,
            # The service assigns every HTTP request its own correlation id. The one
            # from the result query describes the response the caller is holding, so it
            # wins; creation's id is the fallback that keeps this field populated.
            request_id=result.request_id or request_id,
        )

    @staticmethod
    def _tag_with_task(error: ApiError, task_id: str) -> ApiError:
        """Attach task context to an API error raised while polling."""
        error.task_id = task_id
        return error

    @staticmethod
    def _raise_wait_failure(
        error: EzCaptchaError, task_id: str, request_id: str | None
    ) -> NoReturn:
        """Re-raise a failure from waiting, attaching the task id when it has none.

        ``solve`` creates the task internally, so an error that drops the
        identifier strands a result the caller already paid for. Errors that
        carry it themselves are re-raised untouched, since wrapping them would
        only make existing ``except`` clauses miss.
        """
        if isinstance(error, ApiError | PollingExhaustedError):
            raise error
        raise WaitInterruptedError(task_id=task_id, request_id=request_id, cause=error) from error
