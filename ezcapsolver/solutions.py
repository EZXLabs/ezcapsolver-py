"""Solution models.

Each task family has its own field shape, so nothing has to guess at a token.
Every model carries an ``extra`` mapping that catches unmodelled keys, which
makes typed decoding lossless: a worker that adds a field does not lose it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._wire import Model, extra, wire

__all__ = [
    "AkamaiSBSDSolution",
    "AkamaiWebSolution",
    "Cloudflare5sSolution",
    "CloudflareTurnstileSolution",
    "DataDomeSolution",
    "FunCaptchaClassificationSolution",
    "FunCaptchaSolution",
    "HCaptchaClassificationSolution",
    "HCaptchaSolution",
    "IncapsulaSolution",
    "PerimeterXSolution",
    "ReCaptchaSolution",
    "ReClassificationSolution",
    "TlsForwardSolution",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class ReCaptchaSolution(Model):
    """Token solution returned by ReCaptcha V2 and V3 workers.

    Attributes:
        token: Token to submit to the protected site.
        sec_ch_ua: Matching ``Sec-CH-UA`` request header.
        user_agent: Matching User-Agent.
        extra: Worker fields this release does not model.
    """

    token: str = wire("gRecaptchaResponse")
    sec_ch_ua: str = wire("sec_ch_ua", default="")
    user_agent: str = wire("user_agent", default="")
    extra: dict[str, Any] = extra()


@dataclass(frozen=True, slots=True, kw_only=True)
class FunCaptchaSolution(Model):
    """FunCaptcha (Arkose Labs) token solution.

    Attributes:
        token: Token to submit to the protected site.
        extra: Worker fields this release does not model.
    """

    token: str = wire()
    extra: dict[str, Any] = extra()


@dataclass(frozen=True, slots=True, kw_only=True)
class FunCaptchaClassificationSolution(Model):
    """FunCaptcha classification result, shape not yet confirmed.

    No reliable sample exists yet, so this declares no fields of its own —
    everything the worker returns lands in :attr:`extra`, and ``Solved.raw``
    keeps the untouched JSON. Add fields here as samples confirm them.

    Attributes:
        extra: Every field the worker returned.
    """

    extra: dict[str, Any] = extra()


@dataclass(frozen=True, slots=True, kw_only=True)
class HCaptchaClassificationSolution(Model):
    """HCaptcha classification result, shape not yet confirmed.

    No reliable sample exists yet, so this declares no fields of its own —
    everything the worker returns lands in :attr:`extra`, and ``Solved.raw``
    keeps the untouched JSON. Add fields here as samples confirm them.

    Attributes:
        extra: Every field the worker returned.
    """

    extra: dict[str, Any] = extra()


@dataclass(frozen=True, slots=True, kw_only=True)
class CloudflareTurnstileSolution(Model):
    """Cloudflare Turnstile solution.

    Attributes:
        token: Token to submit to the protected site.
        header: Request headers to replay alongside the token.
        extra: Worker fields this release does not model.
    """

    token: str = wire()
    header: dict[str, str] = wire(default_factory=dict)
    extra: dict[str, Any] = extra()


@dataclass(frozen=True, slots=True, kw_only=True)
class Cloudflare5sSolution(Model):
    """Cloudflare five-second challenge solution.

    Every field describes one part of the browser state the worker ended up
    with; replaying these headers and cookies against the protected site is
    what actually clears the challenge.

    Attributes:
        header: Request headers to replay.
        cookies: Clearance cookies the worker obtained.
        tls_version: Browser fingerprint the worker used, such as ``chrome149``.
        body: Challenge page content, empty when the worker captured none.
        s_token: Turnstile token embedded in the challenge, empty when the flow
            did not produce one.
        extra: Worker fields this release does not model.
    """

    header: dict[str, str] = wire(default_factory=dict)
    cookies: dict[str, str] = wire(default_factory=dict)
    tls_version: str = wire("tlsVersion", default="")
    body: str = wire(default="")
    s_token: str = wire("sToken", default="")
    extra: dict[str, Any] = extra()


@dataclass(frozen=True, slots=True, kw_only=True)
class HCaptchaSolution(Model):
    """HCaptcha solution.

    Attributes:
        generated_pass_uuid: Generated HCaptcha pass identifier.
        ua: Matching User-Agent.
        lang: Matching language.
        extra: Worker fields this release does not model.
    """

    generated_pass_uuid: str = wire("generated_pass_UUID")
    ua: str | None = wire(default=None)
    lang: str | None = wire(default=None)
    extra: dict[str, Any] = extra()


@dataclass(frozen=True, slots=True, kw_only=True)
class PerimeterXSolution(Model):
    """PerimeterX solution.

    The worker returns the clearance cookies as top-level fields rather than
    nested under a ``cookies`` object. The wire names carry a leading
    underscore; the Python fields drop it, because a leading underscore means
    "private" in Python, which is the opposite of what these fields are for.

    Attributes:
        px3: ``_px3`` clearance cookie, the value that actually passes the check.
        pxvid: ``_pxvid`` visitor identifier.
        pxde: ``_pxde`` data-enrichment cookie.
        extra: Worker fields this release does not model.
    """

    px3: str = wire("_px3")
    pxvid: str = wire("_pxvid", default="")
    pxde: str = wire("_pxde", default="")
    extra: dict[str, Any] = extra()


@dataclass(frozen=True, slots=True, kw_only=True)
class AkamaiWebSolution(Model):
    """Akamai Web solution, used in the multi-round flow.

    Attributes:
        payload: Sensor payload for the current round.
        encodedata: Encoded state for the next round, fed back in as its
            ``encode_data``. The round that ends the flow carries none, so its
            absence is not a decoding failure.
        extra: Worker fields this release does not model.
    """

    payload: str = wire()
    encodedata: str = wire(default="")
    extra: dict[str, Any] = extra()


@dataclass(frozen=True, slots=True, kw_only=True)
class AkamaiSBSDSolution(Model):
    """Akamai SBSD solution.

    Attributes:
        payload: Base64-encoded payload.
        bm_lso_time: ``bm_lso_time`` produced alongside the payload; not every
            response carries one.
        extra: Worker fields this release does not model.
    """

    payload: str = wire()
    bm_lso_time: str | None = wire("bm_lso_time", default=None)
    extra: dict[str, Any] = extra()


@dataclass(frozen=True, slots=True, kw_only=True)
class TlsForwardSolution(Model):
    """TLS forwarding solution.

    Attributes:
        status: The worker's own response status.
        code: Upstream HTTP status code.
        headers: Upstream response headers.
        cookies: Upstream response cookies.
        body: Upstream response body.
        extra: Worker fields this release does not model.
    """

    status: int = wire(default=0)
    code: int = wire(default=0)
    headers: dict[str, Any] = wire(default_factory=dict)
    cookies: dict[str, Any] = wire(default_factory=dict)
    body: str = wire(default="")
    extra: dict[str, Any] = extra()


@dataclass(frozen=True, slots=True, kw_only=True)
class DataDomeSolution(Model):
    """DataDome solution, shared by both challenge steps.

    Step one carries the challenge address in ``url``; step two carries the
    validation instructions. Earlier workers returned step one as a bare
    string — it is an object now, so both steps decode into this one type.
    ``DataDomeTask`` and ``DataDomeTagsTask`` share it as well.

    Attributes:
        kind: Challenge kind, such as ``slider`` or ``interstitial``.
        url: Challenge URL on step one, validation endpoint on step two.
        body: Optional validation request body.
        extra: Worker fields this release does not model.
    """

    kind: str | None = wire(default=None)
    url: str | None = wire(default=None)
    body: str | None = wire(default=None)
    extra: dict[str, Any] = extra()


@dataclass(frozen=True, slots=True, kw_only=True)
class IncapsulaSolution(Model):
    """Incapsula worker response envelope.

    Attributes:
        status: Inner worker status code.
        data: JSON string to post to the Incapsula sensor endpoint. It is
            stringified JSON and must be submitted verbatim — unwrapping it
            here would change what the caller has to send.
        extra: Worker fields this release does not model.
    """

    status: int | None = wire(default=None)
    data: str = wire()
    extra: dict[str, Any] = extra()


@dataclass(frozen=True, slots=True, kw_only=True)
class ReClassificationSolution(Model):
    """ReCaptcha V2 image classification result.

    Attributes:
        type: Worker result type, usually ``multi`` or ``single``. Unknown
            values are preserved for the caller to interpret.
        has_object: Whether a single image contains the requested object.
        objects: Zero-based indexes of the cells to select.
        extra: Worker fields this release does not model.
    """

    type: str = wire(default="")
    has_object: bool = wire("hasObject", default=False)
    objects: list[int] = wire(default_factory=list)
    extra: dict[str, Any] = extra()

    @property
    def is_multi(self) -> bool:
        """Whether the worker reported a multi-cell grid result."""
        return self.type == "multi"

    @property
    def is_single(self) -> bool:
        """Whether the worker reported a single-image result."""
        return self.type == "single"
