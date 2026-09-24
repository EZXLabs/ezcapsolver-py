"""Synchronous client."""

from __future__ import annotations

import time
from collections.abc import Mapping
from types import TracebackType
from typing import Any, Self

import httpx

from . import _http
from ._shortcuts import SolveShortcuts
from .config import ClientConfig, PollingConfig
from .errors import ApiError, EzCaptchaError, PollingExhaustedError, TransportError, _config_error
from .responses import Solved, TaskResult
from .tasks import Task

__all__ = ["EzCapSolverClient"]


class EzCapSolverClient(SolveShortcuts):
    """Synchronous EzCaptchaSolver client.

    An instance is safe to share across threads: its state is read-only after
    construction, and the underlying ``httpx.Client`` is itself thread-safe.

    Every task type can be run either way: :meth:`solve` creates the task and
    polls for its result, :meth:`sync_solve` runs it through the synchronous
    endpoint. Each also has one shortcut per task type — ``solve_*`` and
    ``sync_solve_*`` — taking the task's fields directly instead of a task
    object.

    Example:
        >>> from ezcapsolver import EzCapSolverClient, ReCaptchaV2Task
        >>> with EzCapSolverClient("your-key") as client:  # doctest: +SKIP
        ...     solved = client.solve(
        ...         ReCaptchaV2Task(website_url="https://example.com", website_key="6Lc...")
        ...     )
        ...     print(solved.solution.token)
    """

    __slots__ = ()

    def __init__(
        self,
        client_key: str | None = None,
        *,
        config: ClientConfig | None = None,
        async_base_url: str | None = None,
        sync_base_url: str | None = None,
        timeout: float | None = None,
        sync_timeout: float | None = None,
        polling: PollingConfig | None = None,
        app_id: int | None = None,
        proxy: str | None = None,
        user_agent: str | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        """Construct the client.

        Args:
            client_key: API credential. Read from ``EZCAPTCHA_API_KEY`` when
                omitted.
            config: A full configuration object; the remaining keyword
                arguments override fields on top of it.
            async_base_url: Base URL for asynchronous tasks and balance queries,
                for a private gateway or a test server.
            sync_base_url: Base URL for synchronous tasks.
            timeout: Per-request timeout in seconds for asynchronous endpoints
                and balance queries.
            sync_timeout: Per-request timeout in seconds for the synchronous
                task endpoint.
            polling: Polling settings for asynchronous tasks.
            app_id: Optional developer application identifier.
            proxy: Proxy the SDK uses to reach the EzCaptchaSolver API.
            user_agent: Override the default User-Agent.
            http_client: Your own httpx client, for connection-pool reuse or to
                point at a private gateway. Closing it stays your job.
        """
        super().__init__(
            client_key,
            config=config,
            async_base_url=async_base_url,
            sync_base_url=sync_base_url,
            timeout=timeout,
            sync_timeout=sync_timeout,
            polling=polling,
            app_id=app_id,
            proxy=proxy,
            user_agent=user_agent,
        )
        self._owns_http = http_client is None
        if http_client is not None:
            self._http = http_client
        else:
            try:
                self._http = httpx.Client(
                    headers={"User-Agent": self._config.user_agent},
                    proxy=self._config.proxy,
                )
            except (httpx.InvalidURL, TypeError, ValueError) as exc:
                # httpx expresses one thing through several exceptions here: the
                # proxy address is unusable.
                raise _config_error(f"invalid SDK proxy: {exc}") from exc

    # -- Lifecycle --------------------------------------------------------

    def close(self) -> None:
        """Close the underlying pool. A supplied httpx client is left open."""
        if self._owns_http:
            self._http.close()

    def __enter__(self) -> Self:
        """Enter the context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Close the pool on exit."""
        self.close()

    # -- Public API -------------------------------------------------------

    def solve[S](self, task: Task[S], *, polling: PollingConfig | None = None) -> Solved[S]:
        """Create the task, poll until it finishes, and decode its result.

        Every task type can be run this way. :meth:`sync_solve` runs the same
        task through the synchronous endpoint instead, taking the same argument
        and returning the same type.

        Args:
            task: A task model, such as :class:`~ezcapsolver.tasks.ReCaptchaV2Task`.
            polling: Polling settings for this call only. Task types differ
                widely in how long they take, so one client-wide budget does not
                fit all of them. Defaults to the client's own settings.

        Returns:
            The solved task. The type of ``solution`` follows from the task type.

        Raises:
            ApiError: The service reported a business error.
            PollingExhaustedError: The polling budget ran out before completion.
            SolutionDecodeError: The worker returned a shape this release does
                not model.
        """
        task_id, request_id = self._create(task)
        try:
            result = self._wait(task_id, polling)
        except EzCaptchaError as exc:
            self._raise_wait_failure(exc, task_id, request_id)
        return self._solved(task, result, task_id, request_id)

    def sync_solve[S](self, task: Task[S]) -> Solved[S]:
        """Run the task through the synchronous endpoint and decode its result.

        The result comes back on the creating request, so nothing is polled;
        :attr:`~ezcapsolver.responses.Solved.task_id` carries the identifier this
        endpoint assigns and returns alongside the result.

        Whether a given type is accepted here is the service's decision. A type
        it does not serve is refused with ``ERROR_TASK_TYPE_NOT_ALLOWED`` before
        anything is billed. Check :attr:`~ezcapsolver.tasks.Task.mode` before
        switching a type over.

        Args:
            task: A task model, such as :class:`~ezcapsolver.tasks.ReCaptchaV2Task`.

        Returns:
            The solved task, with the same ``solution`` type :meth:`solve` gives.

        Raises:
            ApiError: The service reported a business error.
            SolutionDecodeError: The worker returned a shape this release does
                not model.
        """
        return self._solved(task, self.create_sync_task(task))

    def solve_raw(
        self,
        task_type: str,
        params: Mapping[str, Any],
        *,
        polling: PollingConfig | None = None,
    ) -> Solved[Any]:
        """Create a task by bare type name, poll it, and return the raw result.

        Use this when the service ships a type the installed release does not
        know about yet, instead of waiting for an SDK release.
        :meth:`sync_solve_raw` is the synchronous-endpoint counterpart.

        Args:
            task_type: Task type string, such as ``"BrandNewTaskType"``.
            params: Task parameters, keyed by **wire** names and sent verbatim.
            polling: Polling settings for this call only. Defaults to the
                client's own settings.

        Returns:
            A result whose ``solution`` is the raw JSON value.
        """
        url, payload = self._raw_request(task_type, params, sync=False)
        task_id, request_id = self._created_of(self._post(url, payload, self._config.timeout))
        try:
            result = self._wait(task_id, polling)
        except EzCaptchaError as exc:
            self._raise_wait_failure(exc, task_id, request_id)
        return Solved(
            solution=result.solution,
            raw=result.solution,
            task_id=task_id,
            request_id=result.request_id or request_id,
        )

    def sync_solve_raw(self, task_type: str, params: Mapping[str, Any]) -> Solved[Any]:
        """Run a task by bare type name through the synchronous endpoint.

        Args:
            task_type: Task type string, such as ``"BrandNewTaskType"``.
            params: Task parameters, keyed by **wire** names and sent verbatim.

        Returns:
            A result whose ``solution`` is the raw JSON value, with the
            ``task_id`` this endpoint assigned.
        """
        url, payload = self._raw_request(task_type, params, sync=True)
        result = self._require_terminal(
            TaskResult.from_dict(self._post(url, payload, self._config.sync_timeout))
        )
        return Solved(
            solution=result.solution,
            raw=result.solution,
            task_id=result.task_id,
            request_id=result.request_id,
        )

    def create_task(self, task: Task[Any]) -> str:
        """Create an asynchronous task and return its ID without waiting.

        Pair it with :meth:`wait_for_result` to create and wait separately —
        :meth:`solve` does both in one call.
        """
        return self._create(task)[0]

    def create_sync_task(self, task: Task[Any]) -> TaskResult:
        """Run a task on the synchronous endpoint and return its raw result.

        This is the low-level primitive :meth:`sync_solve` builds on, and the
        synchronous counterpart of :meth:`create_task`. Prefer ``sync_solve``
        unless you want the undecoded :class:`~ezcapsolver.responses.TaskResult`.
        """
        _http.logger.debug("creating sync task task_type=%s", task.task_type.value)
        url, payload = self._sync_task_request(task)
        result = TaskResult.from_dict(self._post(url, payload, self._config.sync_timeout))
        _http.logger.info(
            "sync task completed task_type=%s task_id=%s", task.task_type.value, result.task_id
        )
        return result

    def get_result(self, task_id: str) -> TaskResult:
        """Query the task result once, without waiting for completion."""
        url, payload = self._result_request(task_id)
        return TaskResult.from_dict(self._post(url, payload, self._config.timeout))

    def wait_for_result(self, task_id: str, *, polling: PollingConfig | None = None) -> TaskResult:
        """Poll an existing task until it finishes.

        This is what makes a :class:`~ezcapsolver.errors.PollingExhaustedError`
        recoverable: the task keeps running, so hold on to its id and wait for it
        again. The service keeps a result for **five minutes** after creation,
        after which the id is reported as ``ERROR_TASK_NOT_EXIST``.

        Args:
            task_id: Identifier returned by :meth:`create_task`.
            polling: Polling settings for this call only. Defaults to the
                client's own settings.

        Returns:
            The finished result, always in the ready state.

        Raises:
            ApiError: The service reported a business error.
            PollingExhaustedError: The budget ran out before completion.
            UnexpectedResponseError: The task reported ``error`` without an
                accompanying API error, which contradicts the envelope.
        """
        return self._wait(task_id, polling)

    def get_balance(self) -> float:
        """Query the account balance."""
        _http.logger.debug("querying account balance")
        url, payload = self._balance_request()
        return self._balance_of(self._post(url, payload, self._config.timeout))

    # -- Internals --------------------------------------------------------

    def _create(self, task: Task[Any]) -> tuple[str, str | None]:
        """Create a task, returning its id and the creating request's tracking id."""
        _http.logger.debug("creating task task_type=%s", task.task_type.value)
        url, payload = self._create_task_request(task)
        task_id, request_id = self._created_of(self._post(url, payload, self._config.timeout))
        _http.logger.info("task created task_id=%s task_type=%s", task_id, task.task_type.value)
        return task_id, request_id

    def _wait(self, task_id: str, polling: PollingConfig | None = None) -> TaskResult:
        """Poll at the configured interval until the task reaches a terminal state."""
        polling = polling or self._config.polling
        for attempt in range(1, polling.max_attempts + 1):
            # Newly created tasks are still queued. Wait one interval before polling
            # to skip the first request, which would only return processing.
            time.sleep(polling.interval)
            _http.logger.debug("polling task result task_id=%s attempt=%d", task_id, attempt)
            try:
                result = self.get_result(task_id)
            except ApiError as exc:
                # Throttling says nothing about the task, which is still queued.
                # Spend the attempt and poll again rather than failing a task that
                # has already been billed. The attempt is spent on purpose:
                # interval x max_attempts is what keeps the whole wait inside the
                # five-minute window the result is held for.
                if exc.is_rate_limited():
                    _http.logger.warning(
                        "polling throttled, retrying task_id=%s attempt=%d error_code=%s",
                        task_id,
                        attempt,
                        exc.error_code,
                    )
                    continue
                raise self._tag_with_task(exc, task_id) from None
            if not result.is_processing:
                _http.logger.info("task completed task_id=%s attempts=%d", task_id, attempt)
                # A failed task comes back with errorId 1 and became an ApiError in
                # parse_response already. Reaching here means the envelope
                # contradicts itself, so it cannot be handed out as a result.
                return self._require_terminal(result)
        raise PollingExhaustedError(
            task_id=task_id, attempts=polling.max_attempts, interval=polling.interval
        )

    def _post(self, url: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
        """Send one POST and parse the response envelope."""
        _http.log_request(url, payload)
        started = time.perf_counter()
        try:
            response = self._http.post(
                url,
                json=payload,
                timeout=timeout,
                headers=self._key_headers,
            )
        except httpx.TimeoutException as exc:
            raise TransportError(f"request to {url} timed out", cause=exc) from exc
        except httpx.HTTPError as exc:
            raise TransportError(f"request to {url} failed: {exc}", cause=exc) from exc
        _http.log_response(
            url,
            response.status_code,
            (time.perf_counter() - started) * 1000,
            response.content,
        )
        return _http.parse_response(response.status_code, response.content)
