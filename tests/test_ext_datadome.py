"""The DataDome challenge workflow in ezcapsolver.ext.

The pure parts — page reading, headers, the submission verdict — are tested on
their own. The workflow runs end to end against a fake browser session and a
respx-mocked API, so nothing touches the network.
"""

from __future__ import annotations

import base64
import hashlib
import json
import sys
from typing import Any

import httpx
import pytest

from ezcapsolver import AsyncEzCapSolverClient, DataDomeSolution, EzCaptchaError
from ezcapsolver.ext import (
    BrowserRequestError,
    DataDomeBlockedError,
    DataDomeChallenge,
    DataDomeCookie,
    DataDomeError,
)
from ezcapsolver.ext._datadome import workflow
from ezcapsolver.ext._datadome.browser import (
    CHALLENGE_ORIGIN,
    FORM_CONTENT_TYPE,
    BrowserProfile,
)
from ezcapsolver.ext._datadome.page import (
    external_script_url,
    inline_script,
    is_challenged,
    is_hard_blocked,
    is_slider,
    script_hash,
    strip_banner,
)
from ezcapsolver.ext._datadome.verdict import (
    DEFAULT_GET_DELAY,
    Submission,
    read_verdict,
    submit_delay,
)

from .conftest import CLIENT_KEY, SYNC_TASK_URL

BANNER = (
    "/* DataDome is a cyberfraud solution to detect bot activity "
    "@license https://datadome.co v1.33.1 d5110df */"
)
INTERSTITIAL_BODY = ";(function(){var A={};})();"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36"
)
TARGET_URL = "https://shop.example.com/signup"
INTERCEPTED_PAGE = "<html><script>var dd={'rt':'c','cid':'abc'}</script></html>"
SLIDER_SCRIPT = "/** DataDome v1.34.0 96eb15b */\n!function A(){}();\nvar g=1;"
RAW_COOKIE = "datadome=abc123; Max-Age=31536000; Domain=.example.com; Path=/; Secure"


def b64(text: str) -> str:
    """Base64 of UTF-8 text, as the service receives pages and scripts."""
    return base64.b64encode(text.encode()).decode()


def headers_of(headers: list[tuple[str, str]]) -> dict[str, str]:
    """Header pairs as a dict, for lookups."""
    return dict(headers)


# --------------------------------------------------------------------------
# Page reading
# --------------------------------------------------------------------------


class TestPage:
    def test_only_a_closed_first_line_comment_is_a_banner(self):
        assert strip_banner(f"{BANNER}\n{INTERSTITIAL_BODY}") == INTERSTITIAL_BODY
        assert strip_banner(INTERSTITIAL_BODY) == INTERSTITIAL_BODY
        assert strip_banner(f"var x=1;\n{INTERSTITIAL_BODY}") == f"var x=1;\n{INTERSTITIAL_BODY}"
        assert strip_banner("/* unclosed\nvar x=1;") == "/* unclosed\nvar x=1;"
        assert strip_banner(BANNER) == ""

    def test_the_hash_is_the_md5_of_the_script_without_its_banner(self):
        # RFC 1321 test vector.
        assert script_hash("") == "d41d8cd98f00b204e9800998ecf8427e"
        expected = hashlib.md5(INTERSTITIAL_BODY.encode(), usedforsecurity=False).hexdigest()
        assert script_hash(f"{BANNER}\n{INTERSTITIAL_BODY}") == expected

    def test_an_interstitial_bundle_ends_before_the_session_glue(self):
        html = (
            "<html><head>"
            '<script src="https://ct.captcha-delivery.com/interstitial.1.33.0.x.js"></script>'
            "<script>var small=1;</script>"
            f"<script>var ddm={{cid:'session-unique'}};\n{BANNER}\n{INTERSTITIAL_BODY}\n"
            "var glue='initialCid=session-unique';</script>"
            "</head></html>"
        )
        assert inline_script(html) == f"{BANNER}\n{INTERSTITIAL_BODY}".rstrip(";")
        assert (
            external_script_url(html) == "https://ct.captcha-delivery.com/interstitial.1.33.0.x.js"
        )

    def test_a_slider_bundle_keeps_its_static_glue(self):
        html = f"<script>var ddm={{}};\n{SLIDER_SCRIPT}</script>"
        assert inline_script(html) == SLIDER_SCRIPT

    def test_a_bundle_without_a_banner_starts_where_its_code_does(self):
        assert inline_script("<script>var a=1;</script>") == "var a=1;"
        assert inline_script("<script>var a=1;\n!function B(){}();</script>") == (
            "!function B(){}();"
        )
        assert inline_script('<script src="x.js"></script>') is None
        assert inline_script("<p>no scripts</p>") is None

    def test_a_hash_named_external_script_is_found_past_the_loaders(self):
        html = (
            '<script src="https://ct.captcha-delivery.com/i.js"></script>'
            '<script src="//ct.captcha-delivery.com/5d512141a346e3bf.js"></script>'
        )
        assert external_script_url(html) == "https://ct.captcha-delivery.com/5d512141a346e3bf.js"
        loader_only = '<script src="https://ct.captcha-delivery.com/c.js"></script>'
        assert external_script_url(loader_only) is None

    def test_pages_are_classified_by_their_markers(self):
        assert is_hard_blocked("<p>hardblock</p>")
        assert is_challenged(INTERCEPTED_PAGE)
        assert not is_challenged("<html>welcome</html>")
        assert is_slider("https://geo.captcha-delivery.com/captcha/?initialCid=x")
        assert not is_slider("https://geo.captcha-delivery.com/interstitial/?initialCid=x")


# --------------------------------------------------------------------------
# Browser identity
# --------------------------------------------------------------------------


class TestBrowserProfile:
    def test_the_chrome_version_comes_from_the_user_agent(self):
        assert BrowserProfile.create(USER_AGENT, "en").chrome_major == 153
        with pytest.raises(DataDomeError):
            BrowserProfile.create("Mozilla/5.0 Firefox/133.0", "en")

    def test_client_hints_follow_the_user_agent(self):
        headers = headers_of(BrowserProfile.create(USER_AGENT, "en-US").navigation())
        assert headers["sec-ch-ua"] == (
            '"Chromium";v="153", "Google Chrome";v="153", "Not/A)Brand";v="99"'
        )
        assert headers["sec-ch-ua-platform"] == '"Windows"'
        assert headers["user-agent"] == USER_AGENT
        assert headers["accept-language"] == "en-US"

        mac = BrowserProfile.create("Mozilla/5.0 (Macintosh) Chrome/153.0.0.0", "en")
        assert headers_of(mac.navigation())["sec-ch-ua-platform"] == '"macOS"'

    def test_each_request_carries_the_referer_a_browser_would(self):
        profile = BrowserProfile.create(USER_AGENT, "en")
        target = "https://shop.example.com/signup?next=1"
        challenge = "https://geo.captcha-delivery.com/captcha/?initialCid=x"

        slider = headers_of(profile.challenge_frame(target, slider=True))
        assert slider["referer"] == target
        interstitial = headers_of(profile.challenge_frame(target, slider=False))
        assert interstitial["referer"] == "https://shop.example.com"
        assert headers_of(profile.script(challenge))["referer"] == (
            "https://geo.captcha-delivery.com/"
        )

    def test_only_a_post_submission_carries_a_form_content_type(self):
        profile = BrowserProfile.create(USER_AGENT, "en")
        challenge = "https://geo.captcha-delivery.com/interstitial/?x=1"

        post = headers_of(profile.submission(challenge, post=True))
        assert post["content-type"] == FORM_CONTENT_TYPE
        assert post["origin"] == CHALLENGE_ORIGIN
        assert post["referer"] == challenge

        get = headers_of(profile.submission(challenge, post=False))
        assert "content-type" not in get
        assert "origin" not in get


# --------------------------------------------------------------------------
# Submission and verdict
# --------------------------------------------------------------------------


def answer(**fields: Any) -> DataDomeSolution:
    """A step-three answer with the given fields."""
    return DataDomeSolution.from_dict(fields)


class TestVerdict:
    def test_a_slider_or_bodyless_answer_is_submitted_as_a_get(self):
        slider = Submission.from_answer(answer(url="https://dd/check", kind="slider", body="x=1"))
        assert slider == Submission("https://dd/check", None)
        assert not Submission.from_answer(answer(url="https://dd/check", body="")).is_post

        interstitial = Submission.from_answer(answer(url="https://dd/i", body="x=1"))
        assert interstitial == Submission("https://dd/i", "x=1")
        assert interstitial.is_post

        with pytest.raises(DataDomeError):
            Submission.from_answer(answer())

    def test_the_answer_decides_the_delay_with_a_default_for_gets(self):
        timed = answer(url="u", kind="slider", submit_after_ms=1500)
        assert submit_delay(timed, Submission.from_answer(timed)) == 1.5

        untimed_get = answer(url="u", kind="slider", submit_after_ms=0)
        assert submit_delay(untimed_get, Submission.from_answer(untimed_get)) == DEFAULT_GET_DELAY

        untimed_post = answer(url="u", body="x=1")
        assert submit_delay(untimed_post, Submission.from_answer(untimed_post)) == 0.0

    def test_the_cookie_is_split_into_its_parts(self):
        verdict = json.dumps({"view": "redirect", "cookie": RAW_COOKIE})
        assert read_verdict(verdict, TARGET_URL) == DataDomeCookie(
            name="datadome", value="abc123", domain=".example.com", raw=RAW_COOKIE
        )
        without_domain = read_verdict('{"cookie": "datadome=v; Path=/"}', TARGET_URL)
        assert without_domain.domain == ".example.com"

    def test_a_response_without_a_cookie_says_why(self):
        banned = json.dumps({"view": "captcha", "url": "https://geo/captcha/?t=bv&cid=x"})
        with pytest.raises(DataDomeBlockedError):
            read_verdict(banned, TARGET_URL)
        rejected = json.dumps({"view": "captcha", "url": "https://geo/captcha/?t=fe"})
        with pytest.raises(DataDomeError) as excinfo:
            read_verdict(rejected, TARGET_URL)
        assert not isinstance(excinfo.value, DataDomeBlockedError)
        with pytest.raises(DataDomeError):
            read_verdict("<html>oops</html>", TARGET_URL)


# --------------------------------------------------------------------------
# The workflow end to end
# --------------------------------------------------------------------------


class FakeResponse:
    """The part of an lkrequest response the workflow reads."""

    def __init__(self, body: str) -> None:
        self.content = body.encode()


class FakeSession:
    """Serves canned pages by method and URL, and records every request."""

    def __init__(self, pages: dict[tuple[str, str], str]) -> None:
        self.pages = pages
        self.requests: list[tuple[str, str, dict[str, str], bytes | None]] = []
        self.closed = False

    async def get(self, url: str, *, headers: list[tuple[str, str]], **options: Any) -> Any:
        self.requests.append(("GET", url, dict(headers), None))
        return FakeResponse(self.pages[("GET", url)])

    async def post(
        self, url: str, *, headers: list[tuple[str, str]], body: bytes, **options: Any
    ) -> Any:
        self.requests.append(("POST", url, dict(headers), body))
        return FakeResponse(self.pages[("POST", url)])

    def close(self) -> None:
        self.closed = True


@pytest.fixture
def browser(monkeypatch: pytest.MonkeyPatch) -> FakeSession:
    """Replace the lkrequest session with a fake the test fills in."""
    session = FakeSession({})
    monkeypatch.setattr(workflow, "open_session", lambda profile, proxy: session)
    return session


def mock_api(respx_mock: Any, solutions: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Answer each DataDome step on the synchronous endpoint; return the tasks sent."""
    sent: list[dict[str, Any]] = []

    def respond(request: httpx.Request) -> httpx.Response:
        task = json.loads(request.content)["task"]
        sent.append(task)
        solution = solutions[task["step"]]
        return httpx.Response(200, json={"errorId": 0, "status": "ready", "solution": solution})

    respx_mock.post(SYNC_TASK_URL).mock(side_effect=respond)
    return sent


def challenge(**overrides: Any) -> DataDomeChallenge:
    """A challenge run against the target page."""
    return DataDomeChallenge(**{"target_url": TARGET_URL, "user_agent": USER_AGENT} | overrides)


async def test_a_slider_run_sends_an_uncached_script_in_full(respx_mock, browser):
    challenge_url = "https://geo.captcha-delivery.com/captcha/?initialCid=abc"
    submit_url = "https://geo.captcha-delivery.com/captcha/check?cid=abc"
    challenge_page = f"<html><script>var ddm={{}};\n{SLIDER_SCRIPT}</script></html>"
    browser.pages.update(
        {
            ("GET", TARGET_URL): INTERCEPTED_PAGE,
            ("GET", challenge_url): challenge_page,
            ("GET", submit_url): json.dumps({"view": "redirect", "cookie": RAW_COOKIE}),
        }
    )
    sent = mock_api(
        respx_mock,
        {
            "1": {"url": challenge_url},
            "2": {"status": False},
            "3": {"url": submit_url, "kind": "slider", "submit_after_ms": 1},
        },
    )

    async with AsyncEzCapSolverClient(CLIENT_KEY) as client:
        cookie = await client.solve_data_dome_workflow(challenge())

    assert cookie == DataDomeCookie(
        name="datadome", value="abc123", domain=".example.com", raw=RAW_COOKIE
    )
    assert sent == [
        {
            "type": "DataDomeTaskProxyless",
            "step": "1",
            "html_b64": b64(INTERCEPTED_PAGE),
            "image": "",
            "referer": TARGET_URL,
            "user_agent": USER_AGENT,
        },
        {
            "type": "DataDomeTaskProxyless",
            "step": "2",
            "image": "",
            "hash": script_hash(SLIDER_SCRIPT),
        },
        {
            "type": "DataDomeTaskProxyless",
            "step": "3",
            "html_b64": b64(challenge_page),
            "image": "",
            "referer": challenge_url,
            "user_agent": USER_AGENT,
            "external_js_base64": b64(SLIDER_SCRIPT),
        },
    ]
    assert [(method, url) for method, url, _, _ in browser.requests] == [
        ("GET", TARGET_URL),
        ("GET", challenge_url),
        ("GET", submit_url),
    ]
    # The slider frame carries the full page address as its referer.
    assert browser.requests[1][2]["referer"] == TARGET_URL
    assert browser.closed


async def test_an_interstitial_run_sends_only_the_hash_of_a_cached_script(respx_mock, browser):
    challenge_url = "https://geo.captcha-delivery.com/interstitial/?initialCid=abc"
    submit_url = "https://geo.captcha-delivery.com/interstitial/"
    script = f"{BANNER}\n{INTERSTITIAL_BODY}".rstrip(";")
    challenge_page = f"<html><script>var ddm={{}};\n{script};\nvar glue='cid=abc';</script></html>"
    browser.pages.update(
        {
            ("GET", TARGET_URL): INTERCEPTED_PAGE,
            ("GET", challenge_url): challenge_page,
            ("POST", submit_url): json.dumps({"view": "redirect", "cookie": RAW_COOKIE}),
        }
    )
    sent = mock_api(
        respx_mock,
        {
            "1": {"url": challenge_url},
            "2": {"status": True},
            "3": {"url": submit_url, "body": "p=1"},
        },
    )

    async with AsyncEzCapSolverClient(CLIENT_KEY) as client:
        cookie = await client.solve_data_dome_workflow(challenge())

    assert cookie is not None
    assert cookie.value == "abc123"
    step_three = sent[2]
    assert step_three["external_js_hash"] == script_hash(script)
    assert "external_js_base64" not in step_three
    method, url, headers, body = browser.requests[-1]
    assert (method, url, body) == ("POST", submit_url, b"p=1")
    assert headers["content-type"] == FORM_CONTENT_TYPE
    # The interstitial frame only gets the origin of the page.
    assert browser.requests[1][2]["referer"] == "https://shop.example.com"


async def test_a_page_datadome_lets_through_costs_no_task(respx_mock, browser):
    browser.pages[("GET", TARGET_URL)] = "<html>welcome</html>"
    sent = mock_api(respx_mock, {})

    async with AsyncEzCapSolverClient(CLIENT_KEY) as client:
        assert await client.solve_data_dome_workflow(challenge()) is None

    assert sent == []
    assert browser.closed


async def test_a_block_page_is_reported_as_a_ban(respx_mock, browser):
    browser.pages[("GET", TARGET_URL)] = "<html><script>var dd={}</script>hardblock</html>"
    sent = mock_api(respx_mock, {})

    async with AsyncEzCapSolverClient(CLIENT_KEY) as client:
        with pytest.raises(DataDomeBlockedError):
            await client.solve_data_dome_workflow(challenge())

    assert sent == []
    assert browser.closed


async def test_unusable_inputs_fail_before_any_request(respx_mock):
    # No fake session here: these must fail before a session would be used.
    sent = mock_api(respx_mock, {})
    async with AsyncEzCapSolverClient(CLIENT_KEY) as client:
        for bad in (
            challenge(target_url="shop.example.com/signup"),
            challenge(user_agent="Mozilla/5.0 Firefox/133.0"),
            challenge(user_agent="Mozilla/5.0 Chrome/120.0.0.0"),
            challenge(proxy="not a url"),
        ):
            with pytest.raises(DataDomeError):
                await client.solve_data_dome_workflow(bad)
    assert sent == []


async def test_a_failed_browser_request_is_wrapped(monkeypatch):
    import lkrequest

    class FailingSession(FakeSession):
        async def get(self, url: str, *, headers: list[tuple[str, str]], **options: Any) -> Any:
            raise lkrequest.LkTimeoutError("timed out")

    monkeypatch.setattr(workflow, "open_session", lambda profile, proxy: FailingSession({}))
    async with AsyncEzCapSolverClient(CLIENT_KEY) as client:
        with pytest.raises(BrowserRequestError) as excinfo:
            await client.solve_data_dome_workflow(challenge())
    assert isinstance(excinfo.value.__cause__, lkrequest.RequestError)


async def test_a_missing_extra_names_what_to_install(monkeypatch):
    monkeypatch.delitem(sys.modules, "ezcapsolver.ext._datadome.workflow")
    monkeypatch.setitem(sys.modules, "lkrequest", None)
    async with AsyncEzCapSolverClient(CLIENT_KEY) as client:
        with pytest.raises(EzCaptchaError, match=r"ezcapsolver-py\[datadome\]"):
            await client.solve_data_dome_workflow(challenge())


def test_the_proxy_stays_out_of_repr():
    rendered = repr(challenge(proxy="http://user:secret@proxy.example.com:8080"))
    assert "secret" not in rendered
