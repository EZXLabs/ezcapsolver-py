"""The DataDome challenge workflow.

This is the only module that touches the network or imports ``lkrequest``; it is
imported on first use, so ``import ezcapsolver`` works without the extra.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Protocol
from urllib.parse import urlsplit

import lkrequest

from ...responses import Solved
from ...solutions import DataDomeSolution
from ...tasks import DataDomeStep, DataDomeTask, Task
from .._errors import BrowserRequestError, DataDomeBlockedError, DataDomeError
from .browser import BrowserProfile, Headers
from .models import DataDomeChallenge, DataDomeCookie
from .page import (
    encode_text,
    external_script_url,
    inline_script,
    is_challenged,
    is_hard_blocked,
    is_slider,
    script_hash,
)
from .verdict import Submission, read_verdict, submit_delay

logger = logging.getLogger("ezcapsolver")

#: Seconds each browser-side request may take.
BROWSER_REQUEST_TIMEOUT = 30.0


class SyncSolver(Protocol):
    """What the workflow needs from a client: the synchronous endpoint."""

    async def sync_solve[S](self, task: Task[S]) -> Solved[S]:
        """Run a task on the synchronous endpoint."""
        ...


async def solve_data_dome(
    solver: SyncSolver, challenge: DataDomeChallenge
) -> DataDomeCookie | None:
    """Clear the DataDome challenge in front of a page; ``None`` when there is none.

    See :meth:`ezcapsolver.AsyncEzCapSolverClient.solve_data_dome_workflow`.
    """
    target_url = _checked_url(challenge.target_url, "target_url")
    profile = BrowserProfile.create(challenge.user_agent, challenge.accept_language)
    session = open_session(profile, challenge.proxy)
    try:
        return await _run(solver, Browser(session, profile), target_url, challenge.user_agent)
    finally:
        session.close()


async def _run(
    solver: SyncSolver, browser: Browser, target_url: str, user_agent: str
) -> DataDomeCookie | None:
    """Run the flow in an open browser session."""
    page = await browser.get(target_url, browser.profile.navigation())
    if is_hard_blocked(page):
        raise DataDomeBlockedError("the target page is a block page")
    if not is_challenged(page):
        logger.info("datadome did not intercept the target page")
        return None

    challenge_url = await _challenge_url(solver, page, target_url, user_agent)
    slider = is_slider(challenge_url)
    logger.debug("datadome challenge located, slider=%s", slider)
    frame_headers = browser.profile.challenge_frame(target_url, slider=slider)
    challenge_page = await browser.get(challenge_url, frame_headers)
    if is_hard_blocked(challenge_page):
        raise DataDomeBlockedError("the challenge page is a block page")
    loaded_at = time.monotonic()

    script = await browser.challenge_script(challenge_page, challenge_url)
    answer = await _answer(solver, challenge_page, challenge_url, user_agent, script)
    submission = Submission.from_answer(answer)
    wait = max(submit_delay(answer, submission) - (time.monotonic() - loaded_at), 0.0)
    logger.debug("waiting %.3fs before submitting the datadome answer", wait)
    await asyncio.sleep(wait)

    verdict = await browser.submit(submission, challenge_url)
    cookie = read_verdict(verdict, target_url)
    logger.info("datadome challenge passed, cookie=%s", cookie.name)
    return cookie


async def _challenge_url(solver: SyncSolver, page: str, target_url: str, user_agent: str) -> str:
    """Step one: ask the service where the challenge of an intercepted page lives."""
    task = DataDomeTask(
        step=DataDomeStep.ONE,
        html_b64=encode_text(page),
        referer=target_url,
        user_agent=user_agent,
    )
    answer = (await solver.sync_solve(task)).solution
    if not answer.url:
        raise DataDomeError("step one returned no challenge url")
    return _checked_url(answer.url, "the step one challenge url")


async def _answer(
    solver: SyncSolver, challenge_page: str, challenge_url: str, user_agent: str, script: str
) -> DataDomeSolution:
    """Steps two and three: ask whether the script is cached, then for the answer.

    The script itself is sent only when the service does not cache it already.
    """
    hash_ = script_hash(script)
    cached = await _script_cached(solver, hash_)
    logger.debug("probed the datadome script cache, hash=%s cached=%s", hash_, cached)
    task = DataDomeTask(
        step=DataDomeStep.THREE,
        html_b64=encode_text(challenge_page),
        referer=challenge_url,
        user_agent=user_agent,
        external_js_hash=hash_ if cached else None,
        external_js_base64=None if cached else encode_text(script),
    )
    return (await solver.sync_solve(task)).solution


async def _script_cached(solver: SyncSolver, hash_: str) -> bool:
    """Step two: whether the service already caches the script with this hash.

    An answer without ``status`` counts as not cached, which only means the
    script is sent in full.
    """
    answer = (await solver.sync_solve(DataDomeTask(step=DataDomeStep.TWO, hash=hash_))).solution
    return bool(answer.status)


def open_session(profile: BrowserProfile, proxy: str | None) -> lkrequest.Session:
    """Open the cookie-keeping session with the Chrome fingerprint of the profile."""
    preset = getattr(lkrequest.Client, f"chrome_{profile.chrome_major}", None)
    if preset is None:
        raise DataDomeError(
            f"no TLS fingerprint for Chrome {profile.chrome_major}; use 131, or 144 to 158"
        )
    client: lkrequest.Client = preset()
    try:
        return client.session(proxy=proxy)
    except ValueError as error:
        raise DataDomeError(f"the proxy is not usable: {error}") from error


class Browser:
    """Browser side of a challenge run: one session and the identity it presents."""

    __slots__ = ("_session", "profile")

    def __init__(self, session: lkrequest.Session, profile: BrowserProfile) -> None:
        """Wrap an open session."""
        self._session = session
        self.profile = profile

    async def get(self, url: str, headers: Headers) -> str:
        """Send a GET and return the response body.

        The status is not checked: DataDome answers an intercepted page with an
        error status, and the body is what tells the cases apart.
        """
        try:
            response = await self._session.get(
                url, headers=headers, timeout=BROWSER_REQUEST_TIMEOUT
            )
        except lkrequest.RequestError as error:
            raise BrowserRequestError(f"GET {url} failed: {error}") from error
        return _body(response)

    async def post(self, url: str, headers: Headers, body: str) -> str:
        """Send a form POST and return the response body."""
        try:
            response = await self._session.post(
                url, headers=headers, body=body.encode("utf-8"), timeout=BROWSER_REQUEST_TIMEOUT
            )
        except lkrequest.RequestError as error:
            raise BrowserRequestError(f"POST {url} failed: {error}") from error
        return _body(response)

    async def challenge_script(self, page: str, challenge_url: str) -> str:
        """Return the challenge script, fetched from the CDN when the page links it."""
        src = external_script_url(page)
        if src is None:
            logger.debug("reading the inline datadome script")
            script = inline_script(page)
            if script is None:
                raise DataDomeError("the challenge page carries no challenge script")
            return script
        logger.debug("fetching the external datadome script %s", src)
        script = await self.get(src, self.profile.script(challenge_url))
        if not script.strip():
            raise DataDomeError("the external challenge script is empty")
        return script

    async def submit(self, submission: Submission, challenge_url: str) -> str:
        """Hand the answer to DataDome and return its response body."""
        headers = self.profile.submission(challenge_url, post=submission.is_post)
        if submission.body is None:
            return await self.get(submission.url, headers)
        return await self.post(submission.url, headers, submission.body)


def _body(response: lkrequest.Response) -> str:
    """Decode a response body leniently."""
    return response.content.decode("utf-8", errors="replace")


def _checked_url(url: str, what: str) -> str:
    """Reject an address the workflow could not request."""
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise DataDomeError(f"{what} {url!r} is not an http(s) URL")
    return url
