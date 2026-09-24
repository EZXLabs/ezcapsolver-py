"""Envelope parsing, redaction and configuration validation."""

from __future__ import annotations

import json

import pytest

from ezcapsolver import (
    MISSING,
    ApiError,
    ClientConfig,
    EzCaptchaError,
    PollingConfig,
    TaskResult,
    UnexpectedResponseError,
)
from ezcapsolver._http import endpoint, parse_response, redact


class TestEnvelopeParsing:
    def test_success_returns_the_parsed_body(self):
        assert parse_response(200, b'{"errorId":0,"taskId":"t-1"}')["taskId"] == "t-1"

    def test_a_non_zero_error_id_is_the_sole_discriminator(self):
        with pytest.raises(ApiError) as excinfo:
            parse_response(
                200,
                json.dumps(
                    {
                        "errorId": 1,
                        "errorCode": "ERROR_ZERO_BALANCE",
                        "errorDescription": "no balance",
                        "requestId": "r-1",
                    }
                ).encode(),
            )
        error = excinfo.value
        assert error.error_code == "ERROR_ZERO_BALANCE"
        assert error.request_id == "r-1"
        assert error.is_authentication_error() is True

    @pytest.mark.parametrize(
        "code",
        ["ERROR_KEY_DOES_NOT_EXIST", "ERROR_KEY_NOT_AVAILABLE", "ERROR_ZERO_BALANCE"],
    )
    def test_ban_triggering_codes_are_recognised(self, code):
        # These three come from @ApiDefenses on the service's AsyncTaskController.
        # Getting them wrong lets a caller retry its way into a ban. They are
        # terminal errors as well.
        error = ApiError(error_code=code, http_status=500)
        assert error.is_authentication_error() is True
        assert error.is_terminal() is True

    @pytest.mark.parametrize(
        "code",
        [
            "ERROR_SERVICE_UNAVAILABLE",
            "ERROR_SERVICE_TIMEOUT",
            "ERROR_REQUEST_LIMIT",
            "ERROR_REQUEST_BANNED",
            "ERROR_INTERNAL_SERVER_ERROR",
            "ERROR_MINTED_NEXT_RELEASE",
            None,
        ],
    )
    def test_recoverable_and_unknown_codes_are_not_terminal(self, code):
        # An unrecognised code is never terminal: it must not talk a caller out of
        # a retry that would have succeeded.
        error = ApiError(error_code=code, http_status=500)
        assert error.is_authentication_error() is False
        assert error.is_terminal() is False

    def test_a_website_rejection_is_terminal_but_not_a_credential_fault(self):
        error = ApiError(error_code="ERROR_WEBSITE_NOT_ALLOWED", http_status=500)
        assert error.is_authentication_error() is False
        assert error.is_terminal() is True

    @pytest.mark.parametrize("code", ["ERROR_REQUEST_LIMIT", "ERROR_REQUEST_BANNED"])
    def test_the_throttling_codes_are_recognised(self, code):
        assert ApiError(error_code=code, http_status=429).is_rate_limited() is True

    @pytest.mark.parametrize(
        "code",
        [
            "ERROR_SERVICE_UNAVAILABLE",
            "ERROR_SERVICE_TIMEOUT",
            "ERROR_INTERNAL_SERVER_ERROR",
            "ERROR_TASK_NOT_EXIST",
            "ERROR_ZERO_BALANCE",
            "ERROR_MINTED_NEXT_RELEASE",
            None,
        ],
    )
    def test_nothing_else_counts_as_throttling(self, code):
        # wait_for_result retries exactly the throttled set, so it has to stay
        # narrower than "everything that is not terminal". A code leaking in
        # would make the loop poll on past a task that has genuinely failed.
        assert ApiError(error_code=code, http_status=500).is_rate_limited() is False

    def test_field_level_errors_reach_the_message(self):
        with pytest.raises(ApiError, match=r"task\.websiteKey: Must not be blank"):
            parse_response(
                400,
                json.dumps(
                    {
                        "errorId": 1,
                        "errorCode": "ERROR_REQUEST_PARAMETERS",
                        "errors": {"task.websiteKey": "Must not be blank"},
                    }
                ).encode(),
            )

    def test_a_success_envelope_is_not_derailed_by_an_error_code(self):
        # errorId is the sole criterion. Treating a nonempty errorCode as another failure signal
        # could reject a solved task if the server introduces success codes later.
        assert (
            parse_response(200, b'{"errorId":0,"errorCode":"","taskId":"t-1"}')["taskId"] == "t-1"
        )

    def test_a_non_json_error_body_still_reports_the_status(self):
        # Gateways or CDNs may return HTML; callers must still find the status in the same place.
        with pytest.raises(ApiError) as excinfo:
            parse_response(503, b"<html>Service Unavailable</html>")
        assert excinfo.value.http_status == 503
        assert "Service Unavailable" in str(excinfo.value)

    def test_a_non_json_success_body_is_an_unexpected_response(self):
        with pytest.raises(UnexpectedResponseError) as excinfo:
            parse_response(200, b"not json at all")
        assert excinfo.value.body is not None

    def test_a_json_array_body_is_rejected(self):
        with pytest.raises(UnexpectedResponseError):
            parse_response(200, b"[1, 2, 3]")


class TestRedaction:
    def test_credentials_are_removed_at_every_depth(self):
        rendered = json.dumps(
            redact(
                {
                    "clientKey": "super-secret-key",
                    "task": {
                        "type": "TlsTask",
                        "proxy": "http://user:hunter2@127.0.0.1:8080",
                        "rounds": [{"proxy": "socks5://user:hunter2@host:1080"}],
                    },
                }
            )
        )
        assert "super-secret-key" not in rendered
        assert "hunter2" not in rendered
        assert "TlsTask" in rendered


class TestEndpoint:
    @pytest.mark.parametrize(
        ("base", "path"),
        [
            ("https://api.example.com", "/createTask"),
            ("https://api.example.com/", "createTask"),
            ("https://api.example.com/", "/createTask"),
        ],
    )
    def test_slashes_are_normalised(self, base, path):
        assert endpoint(base, path) == "https://api.example.com/createTask"


class TestTaskResult:
    def test_a_missing_solution_differs_from_a_json_null(self):
        # An absent solution means the task is unfinished; null means the worker returned no value.
        absent = TaskResult.from_dict({"errorId": 0, "status": "ready"})
        explicit_null = TaskResult.from_dict({"errorId": 0, "status": "ready", "solution": None})

        assert absent.solution is MISSING
        assert absent.has_solution is False
        assert explicit_null.solution is None
        assert explicit_null.has_solution is True

    @pytest.mark.parametrize("raw", [{"a": 1}, "text", [1, 2], 3, True, None])
    def test_all_six_json_shapes_survive(self, raw):
        assert TaskResult.from_dict({"status": "ready", "solution": raw}).solution == raw

    def test_a_response_without_status_violates_the_contract(self):
        with pytest.raises(UnexpectedResponseError):
            TaskResult.from_dict({"errorId": 0})

    def test_an_unknown_status_is_rejected(self):
        with pytest.raises(UnexpectedResponseError):
            TaskResult.from_dict({"errorId": 0, "status": "half-done"})


class TestConfig:
    @pytest.mark.parametrize("kwargs", [{"timeout": 0}, {"timeout": -1}, {"sync_timeout": 0}])
    def test_non_positive_timeouts_are_rejected(self, kwargs):
        with pytest.raises(EzCaptchaError, match="invalid client configuration"):
            ClientConfig(**kwargs)

    @pytest.mark.parametrize("kwargs", [{"interval": 0}, {"max_attempts": 0}])
    def test_non_positive_polling_budgets_are_rejected(self, kwargs):
        with pytest.raises(EzCaptchaError, match="invalid client configuration"):
            PollingConfig(**kwargs)

    def test_a_blank_client_key_is_rejected(self):
        with pytest.raises(EzCaptchaError, match="invalid client configuration"):
            ClientConfig(client_key="   ").resolve_client_key()

    def test_a_missing_client_key_names_the_environment_variable(self):
        with pytest.raises(EzCaptchaError, match="EZCAPTCHA_API_KEY"):
            ClientConfig().resolve_client_key()

    def test_the_key_is_read_from_the_environment(self, monkeypatch):
        monkeypatch.setenv("EZCAPTCHA_API_KEY", "from-env")
        assert ClientConfig().resolve_client_key() == "from-env"

    def test_repr_never_leaks_the_key(self):
        assert "hunter2" not in repr(ClientConfig(client_key="hunter2"))

    def test_synchronous_and_asynchronous_timeouts_differ_by_default(self):
        # Sync endpoints block until the worker finishes, with up to three minutes for some types.
        # The async timeout would cut off a billed call whose result cannot be retrieved later.
        config = ClientConfig()
        assert (config.timeout, config.sync_timeout) == (30.0, 240.0)
        # Strictly greater than the service's 180s worker deadline, or a worker
        # that uses its full budget gets cut off by the client.
        assert config.sync_timeout > 180.0

    def test_polling_defaults_match_the_specified_budget(self):
        polling = PollingConfig()
        assert (polling.interval, polling.max_attempts) == (3.0, 50)
        assert polling.budget_seconds == 150.0
