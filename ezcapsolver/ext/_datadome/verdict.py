"""Handing the step-three answer to DataDome, and reading the cookie it answers with."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Self
from urllib.parse import parse_qs, urlsplit

from ...solutions import DataDomeSolution
from .._errors import DataDomeBlockedError, DataDomeError
from .models import DataDomeCookie

#: Seconds a GET submission waits when the answer names no delay.
DEFAULT_GET_DELAY = 20.0
#: Challenge kind whose answer always goes out as a GET.
SLIDER_KIND = "slider"
#: ``view`` of a submission response that shows the captcha again.
CAPTCHA_VIEW = "captcha"
#: Query value of ``t`` that marks a banned visitor.
BANNED_MARKER = "bv"
#: How much of an unreadable response an error message quotes.
PREVIEW_CHARS = 200


@dataclass(frozen=True, slots=True)
class Submission:
    """The request that hands the step-three answer to DataDome.

    Attributes:
        url: Submission address.
        body: Form body of a POST; ``None`` for a GET, which a slider answer or
            one without a body is sent as.
    """

    url: str
    body: str | None

    @classmethod
    def from_answer(cls, answer: DataDomeSolution) -> Self:
        """Read the submission out of a step-three answer."""
        if not answer.url:
            raise DataDomeError("step three returned no submission url")
        slider = SLIDER_KIND in (answer.kind or "")
        return cls(answer.url, None if slider or not answer.body else answer.body)

    @property
    def is_post(self) -> bool:
        """Whether the answer is posted as a form."""
        return self.body is not None


def submit_delay(answer: DataDomeSolution, submission: Submission) -> float:
    """Return how many seconds to wait, from when the challenge page loaded, before submitting.

    The answer's ``submit_after_ms`` decides; when it is absent or zero, a GET
    waits :data:`DEFAULT_GET_DELAY` and a POST goes out at once.
    """
    if answer.submit_after_ms:
        return answer.submit_after_ms / 1000
    return 0.0 if submission.is_post else DEFAULT_GET_DELAY


def read_verdict(body: str, target_url: str) -> DataDomeCookie:
    """Read DataDome's response to a submission and return the cookie it issued.

    A response without a cookie is a failed run: a ban when DataDome shows the
    captcha again with ``t=bv``, a rejected answer otherwise.
    """
    try:
        verdict: Any = json.loads(body)
    except ValueError:
        raise DataDomeError(
            f"the submission response is not JSON: {body[:PREVIEW_CHARS]}"
        ) from None
    if not isinstance(verdict, dict):
        raise DataDomeError(f"the submission response is not an object: {body[:PREVIEW_CHARS]}")
    cookie = _text(verdict, "cookie")
    if not cookie:
        raise _rejection(verdict)
    return _parse_cookie(cookie, target_url)


def _rejection(verdict: dict[str, Any]) -> DataDomeError:
    """Explain why a submission brought back no cookie."""
    view = _text(verdict, "view")
    marker = parse_qs(urlsplit(_text(verdict, "url")).query).get("t", [""])[0]
    if view == CAPTCHA_VIEW and marker == BANNED_MARKER:
        return DataDomeBlockedError("the submission was answered with a ban (t=bv)")
    return DataDomeError(f"the challenge was not passed (view {view!r})")


def _parse_cookie(raw: str, target_url: str) -> DataDomeCookie:
    """Split DataDome's cookie string into its parts.

    The domain falls back to the last two labels of the target host when the
    cookie carries no ``Domain`` attribute.
    """
    pair, *attributes = raw.split(";")
    name, _, value = pair.partition("=")
    domain = next(
        (
            attribute.split("=", 1)[1].strip()
            for attribute in map(str.strip, attributes)
            if attribute.startswith(("Domain=", "domain="))
        ),
        None,
    )
    if domain is None:
        host = urlsplit(target_url).hostname or ""
        domain = "." + ".".join(host.split(".")[-2:])
    return DataDomeCookie(name=name.strip(), value=value.strip(), domain=domain, raw=raw)


def _text(verdict: dict[str, Any], name: str) -> str:
    """Return a string field of the verdict, empty when absent or not a string."""
    value = verdict.get(name)
    return value if isinstance(value, str) else ""
