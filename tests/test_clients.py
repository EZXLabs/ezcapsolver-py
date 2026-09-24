"""Behaviour of both clients.

Synchronous and asynchronous cases come in pairs: a behaviour change on either
side must have a matching case on the other.
"""

from __future__ import annotations

import asyncio
import json
import logging

import httpx
import pytest

from ezcapsolver import (
    AkamaiWebTask,
    ApiError,
    AsyncEzCapSolverClient,
    ClientConfig,
    EzCapSolverClient,
    EzCaptchaError,
    PollingConfig,
    PollingExhaustedError,
    ReCaptchaV2ClassificationTask,
    ReCaptchaV2Task,
    ReClassificationSolution,
    TaskMode,
    TaskResult,
    TransportError,
    UnexpectedResponseError,
    WaitInterruptedError,
    task_id_of,
)
from ezcapsolver._http import TRACE

from .conftest import (
    BALANCE_URL,
    CLIENT_KEY,
    CREATE_TASK_URL,
    READY_RECAPTCHA,
    SYNC_TASK_URL,
    TASK_RESULT_URL,
)

CREATED = {"errorId": 0, "taskId": "t-1"}
PROCESSING = {"errorId": 0, "status": "processing"}


def recaptcha() -> ReCaptchaV2Task:
    """A minimal usable ReCaptcha task."""
    return ReCaptchaV2Task(website_url="https://example.com", website_key="key")


def akamai() -> AkamaiWebTask:
    """A minimal usable Akamai task, which uses the synchronous endpoint."""
    return AkamaiWebTask(
        page_url="https://example.com",
        v3_url="https://example.com/v3.js",
        ua="UA",
        lang="en",
        abck="abck",
        bmsz="bmsz",
        script_base64="script",
    )


@pytest.fixture
def client(fast_polling):
    with EzCapSolverClient(CLIENT_KEY, polling=fast_polling) as instance:
        yield instance


@pytest.fixture
async def aclient(fast_polling):
    async with AsyncEzCapSolverClient(CLIENT_KEY, polling=fast_polling) as instance:
        yield instance


@pytest.fixture(
    params=[
        {"type": "multi", "objects": [1, 4]},
        {"type": "single", "hasObject": False},
        {"type": "brand-new", "custom": [2]},
    ]
)
def classification_payload(request, respx_mock):
    payload = request.param
    respx_mock.post(SYNC_TASK_URL).respond(
        json={"errorId": 0, "status": "ready", "requestId": "r-1", "solution": payload}
    )
    return payload


class TestAsynchronousTasks:
    def test_sync_client_creates_polls_and_decodes(self, client, respx_mock):
        respx_mock.post(CREATE_TASK_URL).mock(return_value=httpx.Response(200, json=CREATED))
        route = respx_mock.post(TASK_RESULT_URL)
        route.side_effect = [
            httpx.Response(200, json=PROCESSING),
            httpx.Response(200, json=READY_RECAPTCHA),
        ]

        solved = client.solve(recaptcha())

        assert solved.task_id == "t-1"
        assert solved.solution.token == "the-token"
        assert route.call_count == 2

    async def test_async_client_creates_polls_and_decodes(self, aclient, respx_mock):
        respx_mock.post(CREATE_TASK_URL).mock(return_value=httpx.Response(200, json=CREATED))
        route = respx_mock.post(TASK_RESULT_URL)
        route.side_effect = [
            httpx.Response(200, json=PROCESSING),
            httpx.Response(200, json=READY_RECAPTCHA),
        ]

        solved = await aclient.solve(recaptcha())

        assert solved.task_id == "t-1"
        assert solved.solution.token == "the-token"
        assert route.call_count == 2

    def test_the_task_type_is_nested_inside_the_task_object(self, client, respx_mock):
        route = respx_mock.post(CREATE_TASK_URL).mock(
            return_value=httpx.Response(200, json=CREATED)
        )
        respx_mock.post(TASK_RESULT_URL).mock(
            return_value=httpx.Response(200, json=READY_RECAPTCHA)
        )

        client.solve(recaptcha())

        body = route.calls.last.request.read().decode().replace(" ", "")
        assert '"type":"ReCaptchaV2TaskProxyless"' in body
        assert '"clientKey"' in body

    def test_the_raw_solution_is_always_available(self, client, respx_mock):
        # Fields omitted from the typed model must remain accessible through raw.
        respx_mock.post(CREATE_TASK_URL).mock(return_value=httpx.Response(200, json=CREATED))
        respx_mock.post(TASK_RESULT_URL).mock(
            return_value=httpx.Response(200, json=READY_RECAPTCHA)
        )

        solved = client.solve(recaptcha())
        assert solved.raw == READY_RECAPTCHA["solution"]


class TestSynchronousTasks:
    """sync_solve() reaches the synchronous endpoint for any type, not just some."""

    def test_sync_client_returns_the_solution_without_polling(self, client, respx_mock):
        sync_route = respx_mock.post(SYNC_TASK_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "errorId": 0,
                    "status": "ready",
                    "solution": {"payload": "p", "encodedata": "e"},
                },
            )
        )
        poll_route = respx_mock.post(TASK_RESULT_URL)

        solved = client.sync_solve(akamai())

        assert (solved.solution.payload, solved.solution.encodedata) == ("p", "e")
        assert solved.task_id is None
        assert sync_route.call_count == 1
        assert poll_route.call_count == 0

    async def test_async_client_returns_the_solution_without_polling(self, aclient, respx_mock):
        respx_mock.post(SYNC_TASK_URL).mock(
            return_value=httpx.Response(
                200, json={"errorId": 0, "status": "ready", "solution": {"payload": "p"}}
            )
        )
        solved = await aclient.sync_solve(akamai())
        assert solved.solution.payload == "p"

    def test_the_assigned_task_id_survives(self, client, respx_mock):
        # The synchronous endpoint assigns and returns a taskId. Dropping it
        # discards the only handle on a billed task.
        respx_mock.post(SYNC_TASK_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "errorId": 0,
                    "taskId": "sync-task-1",
                    "status": "ready",
                    "solution": {"payload": "p"},
                },
            )
        )

        assert client.sync_solve(akamai()).task_id == "sync-task-1"

    def test_the_assigned_task_id_survives_the_raw_entry_point(self, client, respx_mock):
        # sync_solve_raw builds its own Solved, a second code path alongside
        # sync_solve.
        respx_mock.post(SYNC_TASK_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "errorId": 0,
                    "taskId": "sync-task-2",
                    "status": "ready",
                    "solution": {"token": "t"},
                },
            )
        )

        solved = client.sync_solve_raw("BrandNewTaskType", {"websiteURL": "https://example.com"})
        assert solved.task_id == "sync-task-2"


class TestExecutionModeIsTheCallersChoice:
    """mode records what the service documents; it never decides where a task goes."""

    def test_sync_client_polls_a_type_documented_as_synchronous(self, client, respx_mock):
        assert akamai().mode is TaskMode.SYNC
        create = respx_mock.post(CREATE_TASK_URL).mock(
            return_value=httpx.Response(200, json=CREATED)
        )
        respx_mock.post(TASK_RESULT_URL).mock(
            return_value=httpx.Response(
                200, json={"errorId": 0, "status": "ready", "solution": {"payload": "p"}}
            )
        )

        solved = client.solve(akamai())

        assert create.call_count == 1
        assert solved.task_id == "t-1"

    async def test_async_client_syncs_a_type_documented_as_polling(self, aclient, respx_mock):
        assert recaptcha().mode is TaskMode.POLLING
        sync_route = respx_mock.post(SYNC_TASK_URL).mock(
            return_value=httpx.Response(200, json=READY_RECAPTCHA)
        )
        poll_route = respx_mock.post(TASK_RESULT_URL)

        solved = await aclient.sync_solve(recaptcha())

        assert (sync_route.call_count, poll_route.call_count) == (1, 0)
        assert solved.solution.token == "the-token"
        assert solved.task_id is None


class TestClassificationResults:
    def test_sync_client_returns_the_model_and_raw_value(self, client, classification_payload):
        solved = client.sync_solve(
            ReCaptchaV2ClassificationTask(image="image", question="question")
        )

        assert isinstance(solved.solution, ReClassificationSolution)
        assert solved.solution.type == classification_payload["type"]
        assert solved.solution.objects == classification_payload.get("objects", [])
        assert solved.solution.has_object == classification_payload.get("hasObject", False)
        assert solved.raw == classification_payload
        assert solved.request_id == "r-1"
        assert solved.task_id is None

    async def test_async_client_returns_the_model_and_raw_value(
        self, aclient, classification_payload
    ):
        solved = await aclient.sync_solve(
            ReCaptchaV2ClassificationTask(image="image", question="question")
        )

        assert isinstance(solved.solution, ReClassificationSolution)
        assert solved.solution.type == classification_payload["type"]
        assert solved.solution.objects == classification_payload.get("objects", [])
        assert solved.solution.has_object == classification_payload.get("hasObject", False)
        assert solved.raw == classification_payload
        assert solved.request_id == "r-1"
        assert solved.task_id is None


class TestBalance:
    def test_sync(self, client, respx_mock):
        respx_mock.post(BALANCE_URL).mock(
            return_value=httpx.Response(200, json={"errorId": 0, "balance": 12.3456})
        )
        assert client.get_balance() == pytest.approx(12.3456)

    async def test_async(self, aclient, respx_mock):
        respx_mock.post(BALANCE_URL).mock(
            return_value=httpx.Response(200, json={"errorId": 0, "balance": 12.3456})
        )
        assert await aclient.get_balance() == pytest.approx(12.3456)


class TestEscapeHatch:
    def test_a_bare_task_type_goes_through_unchanged(self, client, respx_mock):
        # New server-side types must be usable without waiting for an SDK release.
        route = respx_mock.post(CREATE_TASK_URL).mock(
            return_value=httpx.Response(200, json=CREATED)
        )
        respx_mock.post(TASK_RESULT_URL).mock(
            return_value=httpx.Response(
                200, json={"errorId": 0, "status": "ready", "solution": {"anything": 1}}
            )
        )

        solved = client.solve_raw("BrandNewTaskType", {"someField": "value"})

        body = route.calls.last.request.read().decode().replace(" ", "")
        assert '"type":"BrandNewTaskType"' in body
        assert '"someField":"value"' in body
        assert solved.solution == {"anything": 1}

    def test_a_raw_synchronous_type_skips_polling(self, client, respx_mock):
        respx_mock.post(SYNC_TASK_URL).mock(
            return_value=httpx.Response(
                200, json={"errorId": 0, "status": "ready", "solution": "x"}
            )
        )
        assert client.sync_solve_raw("NewSyncType", {}).solution == "x"

    async def test_async_escape_hatch(self, aclient, respx_mock):
        respx_mock.post(CREATE_TASK_URL).mock(return_value=httpx.Response(200, json=CREATED))
        respx_mock.post(TASK_RESULT_URL).mock(
            return_value=httpx.Response(200, json={"errorId": 0, "status": "ready", "solution": 42})
        )
        solved = await aclient.solve_raw("BrandNewTaskType", {})
        assert solved.solution == 42


class TestTheSdkOwnsTheTaskType:
    """A caller-supplied ``type`` never displaces the one the SDK selected.

    Every entry point funnels through the same envelope builder, so each of the
    three ways a ``type`` can arrive is checked. Letting one through would bill
    and run the task as the caller's type while decoding it as the SDK's.
    """

    @staticmethod
    def _sent_type(route) -> str:
        payload = json.loads(route.calls.last.request.read())
        task: dict[str, object] = payload["task"]
        return str(task["type"])

    def test_a_raw_type_in_the_parameters_is_ignored(self, client, respx_mock):
        route = respx_mock.post(SYNC_TASK_URL).mock(
            return_value=httpx.Response(200, json={"errorId": 0, "status": "ready", "solution": 1})
        )

        client.sync_solve_raw("HCaptcha", {"type": "TlsTask", "websiteURL": "https://e.com"})

        assert self._sent_type(route) == "HCaptcha"

    def test_a_type_in_a_models_extra_is_ignored(self, client, respx_mock):
        route = respx_mock.post(SYNC_TASK_URL).mock(
            return_value=httpx.Response(200, json={"errorId": 0, "status": "ready", "solution": 1})
        )
        task = ReCaptchaV2Task(
            website_url="https://e.com", website_key="k", extra={"type": "TlsTask"}
        )

        client.sync_solve_raw(task.task_type, task.to_dict())

        assert self._sent_type(route) == "ReCaptchaV2TaskProxyless"

    def test_a_type_passed_to_a_shortcut_is_ignored(self, client, respx_mock):
        route = respx_mock.post(SYNC_TASK_URL).mock(
            return_value=httpx.Response(200, json=READY_RECAPTCHA)
        )

        client.sync_solve_recaptcha_v2_task_proxyless(
            website_url="https://e.com", website_key="k", type="TlsTask"
        )

        assert self._sent_type(route) == "ReCaptchaV2TaskProxyless"

    async def test_async_clients_own_the_task_type_too(self, aclient, respx_mock):
        route = respx_mock.post(SYNC_TASK_URL).mock(
            return_value=httpx.Response(200, json=READY_RECAPTCHA)
        )

        await aclient.sync_solve_recaptcha_v2_task_proxyless(
            website_url="https://e.com", website_key="k", type="TlsTask"
        )

        assert self._sent_type(route) == "ReCaptchaV2TaskProxyless"


class TestInvalidConfiguration:
    """A bad value from the caller surfaces as an SDK error, not an httpx one.

    The proxy comes from a config file or EZCAPTCHA_PROXY, so a typo in it is
    ordinary. Rust and Go both report it as a configuration error; letting
    httpx.InvalidURL escape here would be the one case a caller cannot catch
    with EzCaptchaError.
    """

    # Both exception types are covered: httpx raises InvalidURL for some bad
    # addresses and ValueError for others.
    @pytest.mark.parametrize(
        "proxy", ["::not a url::", "not-a-scheme://host", "http://host:notaport"]
    )
    def test_an_unusable_proxy_is_a_config_error(self, proxy):
        with pytest.raises(EzCaptchaError, match="invalid client configuration"):
            EzCapSolverClient(CLIENT_KEY, proxy=proxy)

    # Both exception types are covered: httpx raises InvalidURL for some bad
    # addresses and ValueError for others.
    @pytest.mark.parametrize(
        "proxy", ["::not a url::", "not-a-scheme://host", "http://host:notaport"]
    )
    async def test_an_unusable_proxy_is_a_config_error_for_the_async_client(self, proxy):
        with pytest.raises(EzCaptchaError, match="invalid client configuration"):
            AsyncEzCapSolverClient(CLIENT_KEY, proxy=proxy)


class TestFailurePaths:
    def test_an_api_error_while_polling_carries_the_task_id(self, client, respx_mock):
        respx_mock.post(CREATE_TASK_URL).mock(
            return_value=httpx.Response(200, json={"errorId": 0, "taskId": "t-42"})
        )
        respx_mock.post(TASK_RESULT_URL).mock(
            return_value=httpx.Response(
                200, json={"errorId": 1, "errorCode": "ERROR_TASKID_INVALID"}
            )
        )

        with pytest.raises(ApiError) as excinfo:
            client.solve(recaptcha())
        assert excinfo.value.task_id == "t-42"

    def test_polling_exhaustion_reports_the_task_id(self, client, respx_mock):
        respx_mock.post(CREATE_TASK_URL).mock(
            return_value=httpx.Response(200, json={"errorId": 0, "taskId": "t-9"})
        )
        respx_mock.post(TASK_RESULT_URL).mock(return_value=httpx.Response(200, json=PROCESSING))

        with pytest.raises(PollingExhaustedError) as excinfo:
            client.solve(recaptcha())
        # Preserve the task ID so callers can retrieve the result they have already paid for.
        assert excinfo.value.task_id == "t-9"
        assert excinfo.value.attempts == 5

    async def test_async_polling_exhaustion(self, aclient, respx_mock):
        respx_mock.post(CREATE_TASK_URL).mock(
            return_value=httpx.Response(200, json={"errorId": 0, "taskId": "t-9"})
        )
        respx_mock.post(TASK_RESULT_URL).mock(return_value=httpx.Response(200, json=PROCESSING))
        with pytest.raises(PollingExhaustedError):
            await aclient.solve(recaptcha())

    def test_a_throttled_poll_is_retried_instead_of_failing_the_task(self, client, respx_mock):
        # A throttled query is refused before the service ever looks the task up,
        # so the task is still queued -- and it has already been billed, which is
        # what makes giving up on it expensive.
        respx_mock.post(CREATE_TASK_URL).mock(
            return_value=httpx.Response(200, json={"errorId": 0, "taskId": "t-9"})
        )
        route = respx_mock.post(TASK_RESULT_URL).mock(
            side_effect=[
                httpx.Response(429, json={"errorId": 1, "errorCode": "ERROR_REQUEST_LIMIT"}),
                httpx.Response(429, json={"errorId": 1, "errorCode": "ERROR_REQUEST_BANNED"}),
                httpx.Response(200, json=READY_RECAPTCHA),
            ]
        )

        solved = client.solve(recaptcha())

        assert solved.task_id == "t-9"
        assert route.call_count == 3

    async def test_the_async_client_retries_a_throttled_poll(self, aclient, respx_mock):
        respx_mock.post(CREATE_TASK_URL).mock(
            return_value=httpx.Response(200, json={"errorId": 0, "taskId": "t-9"})
        )
        route = respx_mock.post(TASK_RESULT_URL).mock(
            side_effect=[
                httpx.Response(429, json={"errorId": 1, "errorCode": "ERROR_REQUEST_LIMIT"}),
                httpx.Response(200, json=READY_RECAPTCHA),
            ]
        )

        solved = await aclient.solve(recaptcha())

        assert solved.task_id == "t-9"
        assert route.call_count == 2

    def test_throttling_still_runs_out_the_polling_budget(self, client, respx_mock):
        # Retrying must not turn a five-attempt budget into an endless loop: the
        # result is held for only five minutes, so the wall clock the budget
        # stands for has to keep running.
        respx_mock.post(CREATE_TASK_URL).mock(
            return_value=httpx.Response(200, json={"errorId": 0, "taskId": "t-9"})
        )
        route = respx_mock.post(TASK_RESULT_URL).mock(
            return_value=httpx.Response(
                429, json={"errorId": 1, "errorCode": "ERROR_REQUEST_LIMIT"}
            )
        )

        with pytest.raises(PollingExhaustedError) as excinfo:
            client.solve(recaptcha())

        assert excinfo.value.task_id == "t-9"
        assert route.call_count == 5

    def test_any_other_api_error_ends_the_wait_at_once(self, client, respx_mock):
        # Only throttling is retried. Every other API error is the answer to the
        # poll, so the wait ends on it rather than burning the budget.
        respx_mock.post(CREATE_TASK_URL).mock(
            return_value=httpx.Response(200, json={"errorId": 0, "taskId": "t-9"})
        )
        route = respx_mock.post(TASK_RESULT_URL).mock(
            return_value=httpx.Response(
                500, json={"errorId": 1, "errorCode": "ERROR_INTERNAL_SERVER_ERROR"}
            )
        )

        with pytest.raises(ApiError):
            client.solve(recaptcha())

        assert route.call_count == 1

    @pytest.mark.parametrize(
        ("failure", "match"),
        [(httpx.ConnectError("boom"), "failed"), (httpx.ReadTimeout("slow"), "timed out")],
    )
    def test_network_failures_become_transport_errors(self, client, respx_mock, failure, match):
        respx_mock.post(CREATE_TASK_URL).mock(side_effect=failure)
        with pytest.raises(TransportError, match=match):
            client.create_task(recaptcha())

    def test_a_create_response_without_a_task_id_is_rejected(self, client, respx_mock):
        from ezcapsolver import UnexpectedResponseError

        respx_mock.post(CREATE_TASK_URL).mock(return_value=httpx.Response(200, json={"errorId": 0}))
        with pytest.raises(UnexpectedResponseError):
            client.create_task(recaptcha())

    def test_a_ready_result_without_a_solution_is_rejected(self, client, respx_mock):
        respx_mock.post(CREATE_TASK_URL).mock(return_value=httpx.Response(200, json=CREATED))
        respx_mock.post(TASK_RESULT_URL).mock(
            return_value=httpx.Response(200, json={"errorId": 0, "status": "ready"})
        )
        with pytest.raises(UnexpectedResponseError, match="does not contain a solution"):
            client.solve(recaptcha())


class TestTimeoutBudgets:
    """A sync timeout is billed and unrecoverable, so the budgets stay apart."""

    @staticmethod
    def _recorder(captured, payload):
        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(request.extensions.get("timeout", {}).get("read"))
            return httpx.Response(200, json=payload)

        return handler

    def test_synchronous_tasks_get_the_long_timeout(self, respx_mock):
        captured: list[float | None] = []
        respx_mock.post(SYNC_TASK_URL).mock(
            side_effect=self._recorder(
                captured, {"errorId": 0, "status": "ready", "solution": {"payload": "p"}}
            )
        )
        with EzCapSolverClient(CLIENT_KEY, timeout=7.0, sync_timeout=99.0) as client:
            client.sync_solve(akamai())
        assert captured == [99.0]

    def test_asynchronous_endpoints_get_the_short_timeout(self, respx_mock):
        captured: list[float | None] = []
        respx_mock.post(BALANCE_URL).mock(
            side_effect=self._recorder(captured, {"errorId": 0, "balance": 1.0})
        )
        with EzCapSolverClient(CLIENT_KEY, timeout=7.0, sync_timeout=99.0) as client:
            client.get_balance()
        assert captured == [7.0]


class TestConcurrency:
    async def test_one_client_serves_many_concurrent_callers(self, respx_mock, fast_polling):
        # Client state is read-only after construction, so any number of coroutines can share it.
        callers = 64
        respx_mock.post(CREATE_TASK_URL).mock(return_value=httpx.Response(200, json=CREATED))
        respx_mock.post(TASK_RESULT_URL).mock(
            return_value=httpx.Response(200, json=READY_RECAPTCHA)
        )

        async with AsyncEzCapSolverClient(CLIENT_KEY, polling=fast_polling) as client:
            results = await asyncio.gather(*(client.solve(recaptcha()) for _ in range(callers)))

        assert len(results) == callers
        assert all(r.solution.token == "the-token" for r in results)


class TestLifecycle:
    def test_a_supplied_http_client_is_not_closed(self):
        http = httpx.Client()
        with EzCapSolverClient(CLIENT_KEY, http_client=http):
            pass
        assert http.is_closed is False
        http.close()

    async def test_a_supplied_async_http_client_is_not_closed(self):
        http = httpx.AsyncClient()
        async with AsyncEzCapSolverClient(CLIENT_KEY, http_client=http):
            pass
        assert http.is_closed is False
        await http.aclose()

    def test_keyword_arguments_override_a_supplied_config(self):
        with EzCapSolverClient(
            config=ClientConfig(client_key="a", timeout=5.0), timeout=9.0
        ) as client:
            assert client.config.timeout == 9.0
            assert client.config.client_key == "a"


def _mock_every_endpoint(respx_mock) -> None:
    """Answer all four endpoints so one client can exercise each of them."""
    respx_mock.post(CREATE_TASK_URL).respond(json=CREATED)
    respx_mock.post(TASK_RESULT_URL).respond(json=READY_RECAPTCHA)
    respx_mock.post(SYNC_TASK_URL).respond(
        json={"errorId": 0, "status": "ready", "solution": {"payload": "p"}}
    )
    respx_mock.post(BALANCE_URL).respond(json={"errorId": 0, "balance": 1.5})


def _assert_every_endpoint_sent_the_key(respx_mock) -> None:
    """Check that each of the four endpoints was hit once, carrying the key header."""
    paths = sorted(call.request.url.path for call in respx_mock.calls)
    assert paths == ["/createSyncTask", "/createTask", "/getBalance", "/getTaskResult"]
    for call in respx_mock.calls:
        assert call.request.headers.get("X-API-Key") == CLIENT_KEY


class TestClientKeyHeader:
    """Every request carries the client key in ``X-API-Key``, on top of the body field."""

    def test_every_endpoint_sends_the_key_header(self, respx_mock, fast_polling):
        _mock_every_endpoint(respx_mock)

        with EzCapSolverClient(CLIENT_KEY, polling=fast_polling) as client:
            client.solve(recaptcha())
            client.sync_solve(akamai())
            client.get_balance()

        _assert_every_endpoint_sent_the_key(respx_mock)

    async def test_every_endpoint_sends_the_key_header_async(self, respx_mock, fast_polling):
        _mock_every_endpoint(respx_mock)

        async with AsyncEzCapSolverClient(CLIENT_KEY, polling=fast_polling) as client:
            await client.solve(recaptcha())
            await client.sync_solve(akamai())
            await client.get_balance()

        _assert_every_endpoint_sent_the_key(respx_mock)

    def test_a_supplied_http_client_still_sends_the_key(self, respx_mock):
        # A caller-supplied client has no default headers of ours, so the key has
        # to be added per request.
        respx_mock.post(BALANCE_URL).respond(json={"errorId": 0, "balance": 1.5})

        with httpx.Client() as http, EzCapSolverClient(CLIENT_KEY, http_client=http) as client:
            client.get_balance()

        assert respx_mock.calls.last.request.headers.get("X-API-Key") == CLIENT_KEY

    async def test_a_supplied_http_client_still_sends_the_key_async(self, respx_mock):
        respx_mock.post(BALANCE_URL).respond(json={"errorId": 0, "balance": 1.5})

        async with (
            httpx.AsyncClient() as http,
            AsyncEzCapSolverClient(CLIENT_KEY, http_client=http) as client,
        ):
            await client.get_balance()

        assert respx_mock.calls.last.request.headers.get("X-API-Key") == CLIENT_KEY

    # A key that cannot travel as a header value fails when the client is built,
    # not on every request afterwards.
    @pytest.mark.parametrize("key", ["key\nX-Injected: 1", " padded ", "kéy"])
    def test_a_key_that_is_not_a_valid_header_value_is_a_config_error(self, key):
        with pytest.raises(EzCaptchaError, match="contains invalid characters"):
            EzCapSolverClient(key)

    @pytest.mark.parametrize("key", ["key\nX-Injected: 1", " padded ", "kéy"])
    async def test_a_key_that_is_not_a_valid_header_value_is_a_config_error_async(self, key):
        with pytest.raises(EzCaptchaError, match="contains invalid characters"):
            AsyncEzCapSolverClient(key)


class TestObservability:
    """The SDK has to be debuggable without a packet capture."""

    def test_the_sdk_does_not_invent_a_correlation_id(self, respx_mock, fast_polling):
        # The gateway assigns the request id and propagates it downstream; the SDK
        # only reads it back off the response. Sending one from here would compete
        # with the id the rest of the platform is already tracing on.
        respx_mock.post(CREATE_TASK_URL).respond(json=CREATED)
        respx_mock.post(TASK_RESULT_URL).respond(json={**READY_RECAPTCHA, "requestId": "req-1"})

        with EzCapSolverClient(CLIENT_KEY, polling=fast_polling) as client:
            solved = client.solve(recaptcha())

        assert respx_mock.calls, "the requests must have been sent"
        for call in respx_mock.calls:
            assert "X-Request-Id" not in call.request.headers
        assert solved.request_id == "req-1", "the service's id is what gets kept"

    def test_the_task_lifecycle_is_logged(self, respx_mock, fast_polling, caplog):
        # Rust and Go both log this lifecycle. Without it there is no way to watch
        # progress short of capturing traffic.
        respx_mock.post(CREATE_TASK_URL).respond(json={"errorId": 0, "taskId": "t-1"})
        respx_mock.post(TASK_RESULT_URL).respond(json=READY_RECAPTCHA)

        with (
            caplog.at_level(logging.DEBUG, logger="ezcapsolver"),
            EzCapSolverClient(CLIENT_KEY, polling=fast_polling) as client,
        ):
            client.solve(ReCaptchaV2Task(website_url="https://example.com", website_key="k"))

        messages = [record.getMessage() for record in caplog.records]
        assert any("creating task" in m and "ReCaptchaV2TaskProxyless" in m for m in messages)
        assert any("task created" in m and "t-1" in m for m in messages)
        assert any("polling task result" in m and "attempt=1" in m for m in messages)
        assert any("task completed" in m for m in messages)

    def test_bodies_stay_out_of_debug(self, respx_mock, fast_polling, caplog):
        # Payloads appear at TRACE only: DataDome and Akamai bodies run to
        # megabytes, and mixing them into DEBUG would make that level useless for
        # following a task.
        respx_mock.post(CREATE_TASK_URL).respond(json={"errorId": 0, "taskId": "t-1"})
        respx_mock.post(TASK_RESULT_URL).respond(json=READY_RECAPTCHA)

        with (
            caplog.at_level(logging.DEBUG, logger="ezcapsolver"),
            EzCapSolverClient(CLIENT_KEY, polling=fast_polling) as client,
        ):
            client.solve(ReCaptchaV2Task(website_url="https://example.com", website_key="k"))
        assert not any("body=" in record.getMessage() for record in caplog.records)

        caplog.clear()
        with (
            caplog.at_level(TRACE, logger="ezcapsolver"),
            EzCapSolverClient(CLIENT_KEY, polling=fast_polling) as client,
        ):
            client.solve(ReCaptchaV2Task(website_url="https://example.com", website_key="k"))
        rendered = [record.getMessage() for record in caplog.records]
        assert any("body=" in m for m in rendered)
        # Credentials have to be redacted at any depth.
        assert not any(CLIENT_KEY in m for m in rendered)


class TestClientPrimitives:
    """create / wait / sync-create are separately reachable, as in Rust and Go."""

    def test_a_created_task_can_be_waited_on_separately(self, client, respx_mock):
        # PollingExhaustedError documents keeping the task_id to collect the result
        # later, and without this method a caller has to write the loop themselves.
        respx_mock.post(CREATE_TASK_URL).mock(return_value=httpx.Response(200, json=CREATED))
        route = respx_mock.post(TASK_RESULT_URL)
        route.side_effect = [
            httpx.Response(200, json=PROCESSING),
            httpx.Response(200, json=READY_RECAPTCHA),
        ]

        task_id = client.create_task(recaptcha())
        result = client.wait_for_result(task_id)

        assert task_id == "t-1"
        assert result.is_ready
        assert route.call_count == 2

    async def test_the_async_client_waits_separately_too(self, aclient, respx_mock):
        respx_mock.post(CREATE_TASK_URL).mock(return_value=httpx.Response(200, json=CREATED))
        respx_mock.post(TASK_RESULT_URL).mock(
            return_value=httpx.Response(200, json=READY_RECAPTCHA)
        )

        task_id = await aclient.create_task(recaptcha())
        assert (await aclient.wait_for_result(task_id)).is_ready

    def test_polling_can_be_overridden_per_call(self, client, respx_mock):
        # Task types differ widely in how long they take, so one client-wide budget
        # does not fit them all.
        respx_mock.post(CREATE_TASK_URL).mock(return_value=httpx.Response(200, json=CREATED))
        route = respx_mock.post(TASK_RESULT_URL).mock(
            return_value=httpx.Response(200, json=PROCESSING)
        )

        with pytest.raises(PollingExhaustedError) as excinfo:
            client.solve(recaptcha(), polling=PollingConfig(interval=0.001, max_attempts=2))

        assert excinfo.value.attempts == 2
        assert route.call_count == 2

    def test_create_sync_task_returns_the_undecoded_result(self, client, respx_mock):
        respx_mock.post(SYNC_TASK_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "errorId": 0,
                    "taskId": "s-1",
                    "status": "ready",
                    "solution": {"payload": "p"},
                },
            )
        )

        result = client.create_sync_task(akamai())

        assert isinstance(result, TaskResult)
        assert (result.task_id, result.solution) == ("s-1", {"payload": "p"})

    def test_a_contradictory_error_status_is_not_returned_as_a_solution(self, client, respx_mock):
        # status=error with errorId=0 is a self-contradicting envelope. Rust and Go
        # both raise; Python used to hand out an empty Solved in silence.
        respx_mock.post(CREATE_TASK_URL).mock(return_value=httpx.Response(200, json=CREATED))
        respx_mock.post(TASK_RESULT_URL).mock(
            return_value=httpx.Response(200, json={"errorId": 0, "status": "error"})
        )

        # The task has been created and billed by now, so the contract violation is
        # wrapped to carry the task id out. The original diagnosis stays reachable
        # through __cause__.
        with pytest.raises(WaitInterruptedError) as excinfo:
            client.solve_raw("BrandNewTaskType", {"websiteURL": "https://example.com"})
        assert isinstance(excinfo.value.__cause__, UnexpectedResponseError)

    def test_a_contradictory_sync_error_status_is_rejected(self, client, respx_mock):
        respx_mock.post(SYNC_TASK_URL).mock(
            return_value=httpx.Response(200, json={"errorId": 0, "status": "error"})
        )

        with pytest.raises(UnexpectedResponseError):
            client.sync_solve_raw("BrandNewTaskType", {"websiteURL": "https://example.com"})

    def test_the_request_id_falls_back_to_the_creating_call(self, client, respx_mock):
        # When the result response carries no requestId, creation's is the fallback:
        # this field should not come back empty.
        respx_mock.post(CREATE_TASK_URL).mock(
            return_value=httpx.Response(
                200, json={"errorId": 0, "taskId": "t-1", "requestId": "r-create"}
            )
        )
        respx_mock.post(TASK_RESULT_URL).mock(
            return_value=httpx.Response(200, json=READY_RECAPTCHA)
        )

        assert client.solve(recaptcha()).request_id == "r-create"


class TestEndpointOverride:
    """A private gateway, or a mock server in a downstream project's own tests."""

    def test_requests_follow_the_configured_base_urls(self, respx_mock, fast_polling):
        create = respx_mock.post("https://gateway.internal/createTask").respond(
            json={"errorId": 0, "taskId": "t-1"}
        )
        respx_mock.post("https://gateway.internal/getTaskResult").respond(json=READY_RECAPTCHA)
        sync = respx_mock.post("https://sync.internal/createSyncTask").respond(
            json={"errorId": 0, "status": "ready", "solution": {"payload": "p"}}
        )

        with EzCapSolverClient(
            CLIENT_KEY,
            async_base_url="https://gateway.internal",
            sync_base_url="https://sync.internal",
            polling=fast_polling,
        ) as client:
            client.solve(recaptcha())
            client.sync_solve(akamai())

        assert (create.call_count, sync.call_count) == (1, 1)

    def test_a_blank_base_url_is_rejected(self):
        with pytest.raises(EzCaptchaError, match="invalid client configuration"):
            ClientConfig(async_base_url="   ")

    def test_a_missing_balance_is_not_a_zero_balance(self, client, respx_mock):
        # A zero balance means stop; a response that breaks the contract means
        # raise. Opposite reactions, so they must not look alike.
        respx_mock.post(BALANCE_URL).mock(return_value=httpx.Response(200, json={"errorId": 0}))

        with pytest.raises(UnexpectedResponseError):
            client.get_balance()

    def test_a_real_zero_balance_is_returned(self, client, respx_mock):
        respx_mock.post(BALANCE_URL).mock(
            return_value=httpx.Response(200, json={"errorId": 0, "balance": 0})
        )

        assert client.get_balance() == 0.0


class TestBilledTaskStaysRecoverable:
    """A failure with nowhere of its own to put the task id still carries it out.

    ``solve`` creates the task internally, so the error is the only place the id
    appears. Losing it strands a result the caller already paid for: the service
    holds one for five minutes, but only for whoever still knows the id.
    """

    def test_a_transport_failure_while_waiting_keeps_the_task_id(self, client, respx_mock):
        respx_mock.post(CREATE_TASK_URL).mock(
            return_value=httpx.Response(
                200, json={"errorId": 0, "taskId": "t-7", "requestId": "r-7"}
            )
        )
        respx_mock.post(TASK_RESULT_URL).mock(side_effect=httpx.ConnectError("boom"))

        with pytest.raises(WaitInterruptedError) as excinfo:
            client.solve(recaptcha())
        assert excinfo.value.task_id == "t-7"
        assert excinfo.value.request_id == "r-7"
        # The underlying failure has to stay reachable, or diagnosing this leaves
        # nothing but the words "wait interrupted".
        assert isinstance(excinfo.value.__cause__, TransportError)

    def test_a_contract_break_while_waiting_keeps_the_task_id(self, client, respx_mock):
        respx_mock.post(CREATE_TASK_URL).mock(
            return_value=httpx.Response(200, json={"errorId": 0, "taskId": "t-7"})
        )
        # A success envelope with no status breaks the contract rather than being a
        # business error, so nothing else attaches the task id to it.
        respx_mock.post(TASK_RESULT_URL).mock(return_value=httpx.Response(200, json={"errorId": 0}))

        with pytest.raises(WaitInterruptedError) as excinfo:
            client.solve(recaptcha())
        assert excinfo.value.task_id == "t-7"

    async def test_the_async_client_behaves_the_same(self, aclient, respx_mock):
        respx_mock.post(CREATE_TASK_URL).mock(
            return_value=httpx.Response(200, json={"errorId": 0, "taskId": "t-7"})
        )
        respx_mock.post(TASK_RESULT_URL).mock(side_effect=httpx.ConnectError("boom"))

        with pytest.raises(WaitInterruptedError) as excinfo:
            await aclient.solve(recaptcha())
        assert excinfo.value.task_id == "t-7"

    def test_solve_raw_is_covered_too(self, client, respx_mock):
        respx_mock.post(CREATE_TASK_URL).mock(
            return_value=httpx.Response(200, json={"errorId": 0, "taskId": "t-7"})
        )
        respx_mock.post(TASK_RESULT_URL).mock(side_effect=httpx.ConnectError("boom"))

        with pytest.raises(WaitInterruptedError) as excinfo:
            client.solve_raw("BrandNewTaskType", {"websiteURL": "https://example.com"})
        assert excinfo.value.task_id == "t-7"

    def test_errors_that_already_carry_the_id_are_not_wrapped(self, client, respx_mock):
        """Wrapping these would only make existing except clauses miss."""
        respx_mock.post(CREATE_TASK_URL).mock(
            return_value=httpx.Response(200, json={"errorId": 0, "taskId": "t-9"})
        )
        respx_mock.post(TASK_RESULT_URL).mock(return_value=httpx.Response(200, json=PROCESSING))

        with pytest.raises(PollingExhaustedError) as excinfo:
            client.solve(recaptcha())
        assert excinfo.value.task_id == "t-9"

    def test_waiting_on_a_known_id_is_not_wrapped(self, client, respx_mock):
        """The caller passed the id in, so there is nothing to rescue."""
        respx_mock.post(TASK_RESULT_URL).mock(side_effect=httpx.ConnectError("boom"))

        with pytest.raises(TransportError):
            client.wait_for_result("t-7")


class TestTaskIDOfAsksOnce:
    """One question — "is there a billed task to rescue?" — regardless of type."""

    def test_it_reads_every_error_that_carries_one(self):
        interrupted = WaitInterruptedError(
            task_id="t-1", request_id=None, cause=RuntimeError("reset")
        )
        assert task_id_of(interrupted) == "t-1"
        assert task_id_of(PollingExhaustedError(task_id="t-2", attempts=1, interval=1.0)) == "t-2"
        assert task_id_of(ApiError(task_id="t-3")) == "t-3"

    def test_a_failure_before_creation_has_nothing_to_recover(self):
        # Failing before creation means no task and no charge.
        assert task_id_of(TransportError("connect failed")) is None
        assert task_id_of(ApiError(error_code="ERROR_ZERO_BALANCE")) is None

    def test_it_works_on_a_real_solve_failure(self, client, respx_mock):
        respx_mock.post(CREATE_TASK_URL).mock(
            return_value=httpx.Response(200, json={"errorId": 0, "taskId": "t-7"})
        )
        respx_mock.post(TASK_RESULT_URL).mock(side_effect=httpx.ConnectError("boom"))

        with pytest.raises(EzCaptchaError) as excinfo:
            client.solve(recaptcha())
        assert task_id_of(excinfo.value) == "t-7"


async def test_aclose_is_an_alias_that_contextlib_can_find():
    """contextlib.aclosing looks for this exact name, not close."""
    from contextlib import aclosing

    client = AsyncEzCapSolverClient(CLIENT_KEY)
    async with aclosing(client) as instance:
        assert instance is client
    assert client._http.is_closed
