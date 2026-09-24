"""The solve_* / sync_solve_* shortcuts must stay in step with the task models."""

from __future__ import annotations

import dataclasses
import inspect
from typing import Any, get_type_hints

import pytest

import ezcapsolver
from ezcapsolver import AsyncEzCapSolverClient, EzCapSolverClient, ReCaptchaV2Task, TaskType
from ezcapsolver._async_shortcuts import AsyncSolveShortcuts
from ezcapsolver._shortcuts import SolveShortcuts
from ezcapsolver.tasks import Task

from .conftest import (
    CLIENT_KEY,
    CREATE_TASK_URL,
    READY_RECAPTCHA,
    SYNC_TASK_URL,
    TASK_RESULT_URL,
)

# Map shortcut names to wire-format task types, keeping them consistent with the Rust SDK.
SHORTCUTS = {
    "solve_recaptcha_v2_task_proxyless": "ReCaptchaV2TaskProxyless",
    "solve_recaptcha_v2_task_proxyless_s9": "ReCaptchaV2TaskProxylessS9",
    "solve_recaptcha_v2_s_task_proxyless": "ReCaptchaV2STaskProxyless",
    "solve_recaptcha_v2_enterprise_task_proxyless": "ReCaptchaV2EnterpriseTaskProxyless",
    "solve_recaptcha_v2_s_enterprise_task_proxyless": "ReCaptchaV2SEnterpriseTaskProxyless",
    "solve_recaptcha_v2_classification": "ReCaptchaV2Classification",
    "solve_recaptcha_v3_task_proxyless": "ReCaptchaV3TaskProxyless",
    "solve_recaptcha_v3_task_proxyless_s9": "ReCaptchaV3TaskProxylessS9",
    "solve_recaptcha_v3_enterprise_task_proxyless": "ReCaptchaV3EnterpriseTaskProxyless",
    "solve_recaptcha_v3_enterprise_task_proxyless_s9": "ReCaptchaV3EnterpriseTaskProxylessS9",
    "solve_funcaptcha_task_proxyless": "FuncaptchaTaskProxyless",
    "solve_funcaptcha_classification": "FunCaptchaClassification",
    "solve_hcaptcha": "HCaptcha",
    "solve_hcaptcha_classification": "HCaptchaClassification",
    "solve_cloudflare_5s_task": "CloudFlare5STask",
    "solve_cloudflare_turnstile_task": "CloudFlareTurnstileTask",
    "solve_akamai_web_task_proxyless": "AkamaiWEBTaskProxyless",
    "solve_akamai_sbsd_task_proxyless": "AkamaiSBSDTaskProxyless",
    "solve_data_dome_task_proxyless": "DataDomeTaskProxyless",
    "solve_data_dome_tags_task_proxyless": "DataDomeTagsTaskProxyless",
    "solve_perimeter_x": "PerimeterX",
    "solve_incapsula_task_proxyless": "IncapsulaTaskProxyless",
    "solve_tls_task": "TlsTask",
}

# The same 23 types again, on the synchronous endpoint. Same arguments, same return type,
# so every check below runs against both halves.
SYNC_SHORTCUTS = {f"sync_{name}": wire for name, wire in SHORTCUTS.items()}
ALL_SHORTCUTS = SHORTCUTS | SYNC_SHORTCUTS

MIXINS = (SolveShortcuts, AsyncSolveShortcuts)


def _task_class(wire_type: str) -> type[Task[Any]]:
    """Find the task class whose task_type matches a wire type name."""
    for name in ezcapsolver.__all__:
        obj = getattr(ezcapsolver, name)
        if (
            isinstance(obj, type)
            and issubclass(obj, Task)
            and obj is not Task
            and obj.task_type.value == wire_type
        ):
            return obj
    raise AssertionError(f"no task class for {wire_type}")


def _parameters(mixin: type, method_name: str) -> dict[str, inspect.Parameter]:
    """The method's own parameters, minus self and the **extra catch-all."""
    signature = inspect.signature(getattr(mixin, method_name))
    return {
        name: parameter
        for name, parameter in signature.parameters.items()
        if name != "self" and parameter.kind is not inspect.Parameter.VAR_KEYWORD
    }


def test_there_is_one_shortcut_per_task_type():
    # A missing entry leaves a task type without a shortcut; an extra entry indicates a wrong name.
    assert set(SHORTCUTS.values()) == {kind.value for kind in TaskType}


@pytest.mark.parametrize("mixin", MIXINS, ids=lambda m: m.__name__)
@pytest.mark.parametrize("method_name", ALL_SHORTCUTS, ids=str)
def test_every_shortcut_exists_on_both_clients(mixin, method_name):
    assert callable(getattr(mixin, method_name))


@pytest.mark.parametrize("mixin", MIXINS, ids=lambda m: m.__name__)
@pytest.mark.parametrize("method_name,wire_type", ALL_SHORTCUTS.items(), ids=lambda v: str(v))
def test_shortcut_parameters_match_the_task_fields(mixin, method_name, wire_type):
    # If a task model gains a field but its shortcut does not, callers cannot use it through
    # the shortcut. Requests still go through without an error, but omit the new field.
    task = _task_class(wire_type)
    fields = {f.name for f in dataclasses.fields(task) if f.name != "extra"}
    assert set(_parameters(mixin, method_name)) == fields


@pytest.mark.parametrize("mixin", MIXINS, ids=lambda m: m.__name__)
@pytest.mark.parametrize("method_name,wire_type", ALL_SHORTCUTS.items(), ids=lambda v: str(v))
def test_shortcut_defaults_match_the_task_defaults(mixin, method_name, wire_type):
    # Default mismatches are subtler than missing fields: is_invisible differs between V2 and V3.
    task = _task_class(wire_type)
    parameters = _parameters(mixin, method_name)

    for field in dataclasses.fields(task):
        if field.name == "extra":
            continue
        parameter = parameters[field.name]
        if field.default is not dataclasses.MISSING:
            assert parameter.default == field.default, field.name
        elif field.default_factory is not dataclasses.MISSING:  # type: ignore[misc]
            # Shortcuts use None for mutable defaults, creating empty containers on construction.
            assert parameter.default is None, field.name
        else:
            # Required task fields must also be required shortcut parameters.
            assert parameter.default is inspect.Parameter.empty, field.name


@pytest.mark.parametrize("mixin", MIXINS, ids=lambda m: m.__name__)
@pytest.mark.parametrize("method_name,wire_type", ALL_SHORTCUTS.items(), ids=lambda v: str(v))
def test_shortcut_returns_the_tasks_solution_type(mixin, method_name, wire_type):
    # Incorrect return annotations break callers' type inference without a visible runtime error.
    task = _task_class(wire_type)
    hints = get_type_hints(getattr(mixin, method_name))
    expected = task.solution_type if task.solution_type is not None else Any
    assert hints["return"] == ezcapsolver.Solved[expected]  # type: ignore[index]


def test_a_shortcut_sends_what_the_task_object_would(respx_mock, fast_polling):
    # A shortcut is only a wrapper; both paths must produce identical requests.
    create = respx_mock.post(CREATE_TASK_URL).respond(json={"errorId": 0, "taskId": "task-1"})
    respx_mock.post(TASK_RESULT_URL).respond(json=READY_RECAPTCHA)

    with EzCapSolverClient(CLIENT_KEY, polling=fast_polling) as client:
        shortcut = client.solve_recaptcha_v2_task_proxyless("https://example.com", "sitekey")
        with_task = client.solve(
            ReCaptchaV2Task(website_url="https://example.com", website_key="sitekey")
        )

    assert create.calls[0].request.content == create.calls[1].request.content
    assert shortcut == with_task


def test_a_shortcut_forwards_unknown_keywords_as_extra(respx_mock, fast_polling):
    # **extra passes unmodelled parameters into the request body under their original names.
    create = respx_mock.post(CREATE_TASK_URL).respond(json={"errorId": 0, "taskId": "task-1"})
    respx_mock.post(TASK_RESULT_URL).respond(json=READY_RECAPTCHA)

    with EzCapSolverClient(CLIENT_KEY, polling=fast_polling) as client:
        client.solve_recaptcha_v2_task_proxyless("https://example.com", "sitekey", brandNewField=42)

    assert create.calls[0].request.read().count(b'"brandNewField":42') == 1


@pytest.mark.parametrize("mixin", MIXINS, ids=lambda m: m.__name__)
@pytest.mark.parametrize("method_name", SHORTCUTS, ids=str)
def test_both_modes_of_a_type_take_the_same_arguments(mixin, method_name):
    # Switching endpoints must never mean rewriting the call site.
    assert inspect.signature(getattr(mixin, method_name)) == inspect.signature(
        getattr(mixin, f"sync_{method_name}")
    )


def test_a_sync_shortcut_uses_the_synchronous_endpoint(respx_mock, fast_polling):
    # The sync_ prefix is the whole difference: same task, other endpoint, no polling.
    sync = respx_mock.post(SYNC_TASK_URL).respond(json=READY_RECAPTCHA)
    create = respx_mock.post(CREATE_TASK_URL)

    with EzCapSolverClient(CLIENT_KEY, polling=fast_polling) as client:
        solved = client.sync_solve_recaptcha_v2_task_proxyless("https://example.com", "sitekey")

    assert (sync.call_count, create.call_count) == (1, 0)
    # The synchronous endpoint answers on the creating request and assigns no identifier.
    assert solved.task_id is None
    assert solved.solution.token == READY_RECAPTCHA["solution"]["gRecaptchaResponse"]


def test_a_polling_shortcut_polls_a_type_documented_as_synchronous(respx_mock, fast_polling):
    # mode is informational: an unprefixed shortcut always polls, whatever the type is meant for.
    assert ezcapsolver.ReCaptchaV2ClassificationTask.mode is ezcapsolver.TaskMode.SYNC
    create = respx_mock.post(CREATE_TASK_URL).respond(json={"errorId": 0, "taskId": "task-1"})
    respx_mock.post(TASK_RESULT_URL).respond(
        json={"errorId": 0, "status": "ready", "solution": {"type": "multi", "objects": [1]}}
    )

    with EzCapSolverClient(CLIENT_KEY, polling=fast_polling) as client:
        solved = client.solve_recaptcha_v2_classification("image", "question")

    assert create.call_count == 1
    assert solved.task_id == "task-1"


def test_the_clients_expose_the_shortcuts():
    for client in (EzCapSolverClient, AsyncEzCapSolverClient):
        missing = [name for name in ALL_SHORTCUTS if not hasattr(client, name)]
        assert not missing, (client, missing)
