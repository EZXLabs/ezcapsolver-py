"""Task models.

Every task class carries three pieces of metadata: which
:class:`~ezcapsolver.task_type.TaskType` it maps to, which model its result
decodes into, and which execution mode the service documents for it. The first
two are what let a single :meth:`~ezcapsolver.client.EzCapSolverClient.solve` cover
all 23 types instead of one method each; the third is informational only.

Variants within a family — ReCaptcha V2's high-score and enterprise flavours,
say — are subclasses that override only ``task_type``, so the field definitions
are never repeated.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, ClassVar

from ._wire import Model, extra, wire
from .solutions import (
    AkamaiSBSDSolution,
    AkamaiWebSolution,
    Cloudflare5sSolution,
    CloudflareTurnstileSolution,
    DataDomeSolution,
    FunCaptchaClassificationSolution,
    FunCaptchaSolution,
    HCaptchaClassificationSolution,
    HCaptchaSolution,
    IncapsulaSolution,
    PerimeterXSolution,
    ReCaptchaSolution,
    ReClassificationSolution,
    TlsForwardSolution,
)
from .task_type import TaskMode, TaskType

__all__ = [
    "AkamaiSBSDTask",
    "AkamaiWebTask",
    "Cloudflare5sTask",
    "CloudflareTurnstileTask",
    "DataDomeJsType",
    "DataDomeStep",
    "DataDomeTagsTask",
    "DataDomeTask",
    "FunCaptchaClassificationTask",
    "FunCaptchaTask",
    "HCaptchaClassificationTask",
    "HCaptchaTask",
    "IncapsulaTask",
    "PerimeterXTask",
    "ReCaptchaV2ClassificationTask",
    "ReCaptchaV2EnterpriseTask",
    "ReCaptchaV2S9Task",
    "ReCaptchaV2SEnterpriseTask",
    "ReCaptchaV2STask",
    "ReCaptchaV2Task",
    "ReCaptchaV3EnterpriseS9Task",
    "ReCaptchaV3EnterpriseTask",
    "ReCaptchaV3S9Task",
    "ReCaptchaV3Task",
    "Task",
    "TlsForwardTask",
    "TlsHttpMethod",
]


class Task[S](Model):
    """Base class for every task model.

    The type parameter ``S`` is the solution type this task resolves to, which
    is what lets a type checker infer the return value of ``client.solve(task)``.

    Attributes:
        task_type: The service-side task type this task maps to.
        solution_type: Model the result decodes into; ``None`` means the shape
            is unconfirmed and the raw value is returned.
        mode: Execution mode the service documents for this type. Informational
            only — every task can be run either way, through ``solve`` or
            through ``sync_solve``. See :class:`~ezcapsolver.task_type.TaskMode`.
    """

    __slots__ = ()

    task_type: ClassVar[TaskType]
    solution_type: ClassVar[type[Model] | None] = None
    mode: ClassVar[TaskMode] = TaskMode.POLLING


# --------------------------------------------------------------------------
# ReCaptcha
# --------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, kw_only=True)
class ReCaptchaV2Task(Task[ReCaptchaSolution]):
    """ReCaptcha V2, proxyless.

    Attributes:
        website_url: URL of the page containing the challenge.
        website_key: ReCaptcha site key.
        is_invisible: Whether the challenge uses invisible mode.
        sa: Optional security anchor parameter.
        s: Optional challenge-bound ``s`` parameter.
        website_title: Optional page title.
        proxy: Optional proxy forwarded to the worker.
        extra: Additional worker parameters.
    """

    task_type: ClassVar[TaskType] = TaskType.RECAPTCHA_V2_TASK_PROXYLESS
    solution_type: ClassVar[type[Model] | None] = ReCaptchaSolution

    website_url: str = wire("websiteURL")
    website_key: str = wire()
    is_invisible: bool = wire("isInvisible", default=False)
    sa: str | None = wire(default=None)
    s: str | None = wire(default=None)
    website_title: str | None = wire(default=None)
    proxy: str | None = wire(default=None)
    extra: dict[str, Any] = extra()


class ReCaptchaV2S9Task(ReCaptchaV2Task):
    """ReCaptcha V2 high-score S9, proxyless."""

    __slots__ = ()
    task_type: ClassVar[TaskType] = TaskType.RECAPTCHA_V2_TASK_PROXYLESS_S9


class ReCaptchaV2STask(ReCaptchaV2Task):
    """ReCaptcha V2 carrying the ``s`` parameter, proxyless."""

    __slots__ = ()
    task_type: ClassVar[TaskType] = TaskType.RECAPTCHA_V2_S_TASK_PROXYLESS


class ReCaptchaV2EnterpriseTask(ReCaptchaV2Task):
    """ReCaptcha V2 Enterprise, proxyless."""

    __slots__ = ()
    task_type: ClassVar[TaskType] = TaskType.RECAPTCHA_V2_ENTERPRISE_TASK_PROXYLESS


class ReCaptchaV2SEnterpriseTask(ReCaptchaV2Task):
    """ReCaptcha V2 Enterprise carrying the ``s`` parameter, proxyless."""

    __slots__ = ()
    task_type: ClassVar[TaskType] = TaskType.RECAPTCHA_V2_S_ENTERPRISE_TASK_PROXYLESS


@dataclass(frozen=True, slots=True, kw_only=True)
class ReCaptchaV3Task(Task[ReCaptchaSolution]):
    """ReCaptcha V3, proxyless.

    Attributes:
        website_url: URL of the page containing the challenge.
        website_key: ReCaptcha site key.
        is_invisible: Whether the challenge uses invisible mode; true by
            default for V3.
        page_action: Action configured by the protected page.
        website_title: Optional page title.
        check_field: Site-specific check field.
        proxy: Optional proxy forwarded to the worker.
        extra: Additional worker parameters.
    """

    task_type: ClassVar[TaskType] = TaskType.RECAPTCHA_V3_TASK_PROXYLESS
    solution_type: ClassVar[type[Model] | None] = ReCaptchaSolution

    website_url: str = wire("websiteURL")
    website_key: str = wire()
    is_invisible: bool = wire("isInvisible", default=True)
    page_action: str | None = wire(default=None)
    website_title: str | None = wire(default=None)
    check_field: str | None = wire(default=None)
    proxy: str | None = wire(default=None)
    extra: dict[str, Any] = extra()


class ReCaptchaV3S9Task(ReCaptchaV3Task):
    """ReCaptcha V3 high-score S9, proxyless."""

    __slots__ = ()
    task_type: ClassVar[TaskType] = TaskType.RECAPTCHA_V3_TASK_PROXYLESS_S9


class ReCaptchaV3EnterpriseTask(ReCaptchaV3Task):
    """ReCaptcha V3 Enterprise, proxyless."""

    __slots__ = ()
    task_type: ClassVar[TaskType] = TaskType.RECAPTCHA_V3_ENTERPRISE_TASK_PROXYLESS


class ReCaptchaV3EnterpriseS9Task(ReCaptchaV3Task):
    """ReCaptcha V3 Enterprise high-score S9, proxyless."""

    __slots__ = ()
    task_type: ClassVar[TaskType] = TaskType.RECAPTCHA_V3_ENTERPRISE_TASK_PROXYLESS_S9


@dataclass(frozen=True, slots=True, kw_only=True)
class ReCaptchaV2ClassificationTask(Task[ReClassificationSolution]):
    """ReCaptcha V2 image classification.

    Attributes:
        image: Base64-encoded challenge image.
        question: Object identifier or classification question.
        size: Grid size documented by the service.
        extra: Additional worker parameters.
    """

    task_type: ClassVar[TaskType] = TaskType.RECAPTCHA_V2_CLASSIFICATION
    solution_type: ClassVar[type[Model] | None] = ReClassificationSolution
    mode: ClassVar[TaskMode] = TaskMode.SYNC

    image: str = wire()
    question: str = wire()
    size: int = wire(default=4)
    extra: dict[str, Any] = extra()


# --------------------------------------------------------------------------
# FunCaptcha
# --------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, kw_only=True)
class FunCaptchaTask(Task[FunCaptchaSolution]):
    """FunCaptcha, proxyless.

    Attributes:
        website_url: URL of the page containing the challenge.
        website_key: FunCaptcha public key.
        data: Optional Arkose Labs blob data.
        api_js_subdomain: Optional Arkose Labs API subdomain.
        proxy: Optional worker proxy. FunCaptcha is the only task type using the
            ``FUN`` proxy format -- ``protocol://host:port:username:password``,
            with the credentials appended rather than placed before the host.
            Every other type takes ``protocol://username:password@host:port``.
            Either way the service requires both a username and a password: an
            unauthenticated proxy is rejected.
        cn: Whether the supplied proxy is in mainland China.
        extra: Additional worker parameters.
    """

    task_type: ClassVar[TaskType] = TaskType.FUNCAPTCHA_TASK_PROXYLESS
    solution_type: ClassVar[type[Model] | None] = FunCaptchaSolution

    website_url: str = wire("websiteURL")
    website_key: str = wire()
    data: str | None = wire(default=None)
    api_js_subdomain: str | None = wire("funcaptchaApiJSSubdomain", default=None)
    proxy: str | None = wire(default=None)
    cn: bool = wire(default=False)
    extra: dict[str, Any] = extra()


@dataclass(frozen=True, slots=True, kw_only=True)
class FunCaptchaClassificationTask(Task[FunCaptchaClassificationSolution]):
    """FunCaptcha image classification.

    Attributes:
        image: Base64-encoded challenge image.
        question: Classification question.
        extra: Additional worker parameters.

    Note:
        This type's solution shape is not confirmed yet, so
        :class:`~ezcapsolver.solutions.FunCaptchaClassificationSolution` declares
        no fields — everything lands in its ``extra`` mapping.
    """

    task_type: ClassVar[TaskType] = TaskType.FUNCAPTCHA_CLASSIFICATION
    solution_type: ClassVar[type[Model] | None] = FunCaptchaClassificationSolution
    mode: ClassVar[TaskMode] = TaskMode.SYNC

    image: str = wire()
    question: str = wire()
    extra: dict[str, Any] = extra()


# --------------------------------------------------------------------------
# HCaptcha
# --------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, kw_only=True)
class HCaptchaTask(Task[HCaptchaSolution]):
    """HCaptcha.

    Attributes:
        website_url: URL of the page containing the challenge.
        website_key: HCaptcha site key.
        lang: Browser language. Only ``en-US`` is supported at the moment.
        proxy: Optional proxy forwarded to the worker.
        invisible: Whether the challenge runs without a visible checkbox. True
            when the site shows no HCaptcha checkbox, false when it does.
        rq_data: Optional ``rqdata`` value, required by the sites that publish
            one. The wire name is all lowercase here, unlike
            :attr:`Cloudflare5sTask.rq_data`, whose wire name is ``rqData`` and
            which carries an object rather than a string.
        extra: Additional worker parameters.
    """

    task_type: ClassVar[TaskType] = TaskType.HCAPTCHA
    solution_type: ClassVar[type[Model] | None] = HCaptchaSolution

    website_url: str = wire("websiteURL")
    website_key: str = wire()
    lang: str = wire()
    proxy: str | None = wire(default=None)
    invisible: bool = wire()
    rq_data: str | None = wire("rqdata", default=None)
    extra: dict[str, Any] = extra()


@dataclass(frozen=True, slots=True, kw_only=True)
class HCaptchaClassificationTask(Task[HCaptchaClassificationSolution]):
    """HCaptcha image classification.

    Every field is optional: different classification modules need different
    input combinations, and the service contract does not yet state which are
    required.

    Attributes:
        image: Optional single image.
        images: Optional image collection.
        anchors: Optional anchor collection.
        question: Optional classification question.
        module: Optional classification module.
        extra: Additional worker parameters.

    Note:
        This type's solution shape is not confirmed yet, so
        :class:`~ezcapsolver.solutions.HCaptchaClassificationSolution` declares
        no fields.
    """

    task_type: ClassVar[TaskType] = TaskType.HCAPTCHA_CLASSIFICATION
    solution_type: ClassVar[type[Model] | None] = HCaptchaClassificationSolution
    mode: ClassVar[TaskMode] = TaskMode.SYNC

    image: str | None = wire(default=None)
    images: list[str] | None = wire(default=None)
    anchors: list[str] | None = wire(default=None)
    question: str | None = wire(default=None)
    module: str | None = wire(default=None)
    extra: dict[str, Any] = extra()


# --------------------------------------------------------------------------
# PerimeterX
# --------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, kw_only=True)
class PerimeterXTask(Task[PerimeterXSolution]):
    """PerimeterX.

    Attributes:
        website_key: PerimeterX application identifier.
        invisible: Whether the challenge uses invisible mode.
        extra: Additional worker parameters.
    """

    task_type: ClassVar[TaskType] = TaskType.PERIMETERX
    solution_type: ClassVar[type[Model] | None] = PerimeterXSolution

    website_key: str = wire()
    invisible: bool = wire(default=False)
    extra: dict[str, Any] = extra()


# --------------------------------------------------------------------------
# Akamai
# --------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, kw_only=True)
class AkamaiWebTask(Task[AkamaiWebSolution]):
    """Akamai Web, proxyless.

    This is a multi-round flow: each round feeds the previous round's
    ``encodedata`` into :attr:`encode_data` and increments :attr:`index`.

    Attributes:
        page_url: URL of the page the Akamai script belongs to.
        v3_url: URL of the Akamai v3 script. Most sites change it on every
            request, so it has to be read from the page rather than hard-coded.
            It is the URL itself, not the script the URL serves.
        ua: Browser User-Agent.
        lang: Browser language.
        index: Current interaction round.
        abck: Current ``_abck`` cookie value. Empty on the first round, which
            runs before the site has issued one.
        bmsz: Current ``bm_sz`` cookie value, empty on the first round.
        script_base64: Base64-encoded Akamai script. Only the first round sends
            it; later rounds leave it empty.
        encode_data: Encoded state returned by the previous round.
        extra: Additional worker parameters.
    """

    task_type: ClassVar[TaskType] = TaskType.AKAMAI_WEB_TASK_PROXYLESS
    solution_type: ClassVar[type[Model] | None] = AkamaiWebSolution
    mode: ClassVar[TaskMode] = TaskMode.SYNC

    page_url: str = wire()
    v3_url: str = wire()
    ua: str = wire()
    lang: str = wire()
    index: int = wire(default=0)
    # The contract marks these three optional with an empty-string default. Round 0
    # runs before _abck and bm_sz exist, and the script is only sent on that round,
    # so requiring them would make every caller write "" by hand.
    abck: str = wire(default="")
    bmsz: str = wire(default="")
    script_base64: str = wire("script_base64", default="")
    encode_data: str = wire(default="")
    extra: dict[str, Any] = extra()


@dataclass(frozen=True, slots=True, kw_only=True)
class AkamaiSBSDTask(Task[AkamaiSBSDSolution]):
    """Akamai SBSD, proxyless.

    Attributes:
        page_url: URL of the page the challenge belongs to.
        sbsd_url: URL of the SBSD script.
        bm_so: Existing ``bm_so`` or equivalent cookie value.
        ua: Browser User-Agent.
        lang: Browser language.
        script_base64: Base64-encoded SBSD script.
        extra: Additional worker parameters.
    """

    task_type: ClassVar[TaskType] = TaskType.AKAMAI_SBSD_TASK_PROXYLESS
    solution_type: ClassVar[type[Model] | None] = AkamaiSBSDSolution
    mode: ClassVar[TaskMode] = TaskMode.SYNC

    page_url: str = wire()
    sbsd_url: str = wire()
    bm_so: str = wire()
    ua: str = wire()
    lang: str = wire()
    script_base64: str = wire("script_base64")
    extra: dict[str, Any] = extra()


# --------------------------------------------------------------------------
# Cloudflare
# --------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, kw_only=True)
class Cloudflare5sTask(Task[Cloudflare5sSolution]):
    """Cloudflare five-second challenge.

    Attributes:
        website_url: URL protected by the challenge.
        proxy: Proxy the challenge worker uses; required for this type, unlike
            most others. Format is ``protocol://username:password@host:port``
            with protocol one of ``http``, ``https`` or ``socks5``. Both
            credentials are required -- the service rejects an unauthenticated
            proxy -- and the host may not be a private address.
        rq_data: Optional challenge request data.
        extra: Additional worker parameters.
    """

    task_type: ClassVar[TaskType] = TaskType.CLOUDFLARE_5S_TASK
    solution_type: ClassVar[type[Model] | None] = Cloudflare5sSolution

    website_url: str = wire("websiteURL")
    proxy: str = wire()
    rq_data: dict[str, Any] | None = wire("rqData", default=None)
    extra: dict[str, Any] = extra()


@dataclass(frozen=True, slots=True, kw_only=True)
class CloudflareTurnstileTask(Task[CloudflareTurnstileSolution]):
    """Cloudflare Turnstile.

    Attributes:
        website_url: URL of the page containing the Turnstile widget.
        website_key: Turnstile site key.
        proxy: Optional worker proxy.
        rq_data: Optional Turnstile metadata.
        extra: Additional worker parameters.
    """

    task_type: ClassVar[TaskType] = TaskType.CLOUDFLARE_TURNSTILE_TASK
    solution_type: ClassVar[type[Model] | None] = CloudflareTurnstileSolution

    website_url: str = wire("websiteURL")
    website_key: str = wire()
    proxy: str | None = wire(default=None)
    rq_data: dict[str, Any] | None = wire("rqData", default=None)
    extra: dict[str, Any] = extra()


# --------------------------------------------------------------------------
# DataDome
# --------------------------------------------------------------------------


class DataDomeStep(StrEnum):
    """DataDome challenge step."""

    #: Step one: fetch the challenge URL.
    ONE = "1"
    #: Step two: produce the validation instructions.
    TWO = "2"


class DataDomeJsType(StrEnum):
    """JavaScript mode for DataDome tags."""

    #: Challenge mode.
    CH = "ch"
    #: Legacy or external mode.
    LE = "le"


@dataclass(frozen=True, slots=True, kw_only=True)
class DataDomeTask(Task[DataDomeSolution]):
    """DataDome challenge, proxyless.

    Both steps return a :class:`~ezcapsolver.solutions.DataDomeSolution`: step one
    carries the challenge address in ``url``, step two the validation
    instructions.

    Attributes:
        html_b64: Base64-encoded challenge HTML.
        step: Step of the challenge workflow.
        image: Optional base64-encoded image.
        referer: Optional page or challenge URL.
        parent_url: Optional parent page URL.
        equipment: Optional equipment identifier.
        extra: Additional worker parameters.
    """

    task_type: ClassVar[TaskType] = TaskType.DATADOME_TASK_PROXYLESS
    solution_type: ClassVar[type[Model] | None] = DataDomeSolution
    mode: ClassVar[TaskMode] = TaskMode.SYNC

    html_b64: str = wire("html_b64")
    step: DataDomeStep = wire(default=DataDomeStep.ONE)
    image: str = wire(default="")
    referer: str | None = wire(default=None)
    parent_url: str | None = wire("parent_url", default=None)
    equipment: str | None = wire(default=None)
    extra: dict[str, Any] = extra()


@dataclass(frozen=True, slots=True, kw_only=True)
class DataDomeTagsTask(Task[DataDomeSolution]):
    """DataDome tags, proxyless.

    Attributes:
        ddk: DataDome JavaScript key.
        jstype: DataDome JavaScript mode.
        cid: Session identifier; an empty string is valid.
        bpc: One-based packet counter.
        referer: Current page URL.
        ua: Browser User-Agent.
        fields: External business fields forwarded to the worker.
        extra: Additional worker parameters.
    """

    task_type: ClassVar[TaskType] = TaskType.DATADOME_TAGS_TASK_PROXYLESS
    solution_type: ClassVar[type[Model] | None] = DataDomeSolution
    mode: ClassVar[TaskMode] = TaskMode.SYNC

    ddk: str = wire()
    jstype: DataDomeJsType = wire(default=DataDomeJsType.CH)
    cid: str = wire(default="")
    bpc: int = wire(default=1)
    referer: str = wire()
    ua: str = wire()
    fields: dict[str, Any] = wire(default_factory=dict)
    extra: dict[str, Any] = extra()


# --------------------------------------------------------------------------
# Incapsula
# --------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, kw_only=True)
class IncapsulaTask(Task[IncapsulaSolution]):
    """Incapsula Reese84, proxyless.

    Attributes:
        script: Full source of the Reese84 sensor script.
        script_url: URL of the sensor script.
        page_url: URL of the page executing the sensor script.
        accept_language: Optional Accept-Language header used by the browser
            flow.
        ua: Browser User-Agent.
        proxy: Optional proxy used by the worker.
        pow: Optional proof-of-work data, required by the sites that have PoW
            challenges enabled.
        extra: Additional worker parameters.
    """

    task_type: ClassVar[TaskType] = TaskType.INCAPSULA_TASK_PROXYLESS
    solution_type: ClassVar[type[Model] | None] = IncapsulaSolution
    mode: ClassVar[TaskMode] = TaskMode.SYNC

    script: str = wire()
    script_url: str = wire()
    page_url: str = wire()
    accept_language: str | None = wire(default=None)
    ua: str = wire()
    proxy: str | None = wire(default=None)
    pow: str | None = wire(default=None)
    extra: dict[str, Any] = extra()


# --------------------------------------------------------------------------
# TLS forwarding
# --------------------------------------------------------------------------


class TlsHttpMethod(StrEnum):
    """HTTP methods accepted by TLS forwarding tasks."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


@dataclass(frozen=True, slots=True, kw_only=True)
class TlsForwardTask(Task[TlsForwardSolution]):
    """Forward one HTTP request through the worker's TLS fingerprint.

    Attributes:
        tls_type: The worker's TLS fingerprint identifier.
        proxy: Proxy used for the upstream request.
        method: Upstream HTTP method.
        url: Upstream URL.
        headers: Optional upstream request headers.
        headers_order: Optional serialised header order.
        cookies: Optional upstream request cookies.
        body: Optional upstream request body.
        body_raw: Whether :attr:`body` is already base64-encoded. Always sent,
            so the default states plainly that it is not rather than leaving
            the worker to guess.
        extra: Additional worker parameters.
    """

    task_type: ClassVar[TaskType] = TaskType.TLS_TASK
    solution_type: ClassVar[type[Model] | None] = TlsForwardSolution
    mode: ClassVar[TaskMode] = TaskMode.SYNC

    tls_type: str = wire("tls_type")
    proxy: str = wire()
    method: TlsHttpMethod = wire(default=TlsHttpMethod.GET)
    url: str = wire()
    headers: dict[str, Any] | None = wire(default=None)
    headers_order: str | None = wire("headers_order", default=None)
    cookies: dict[str, Any] | None = wire(default=None)
    body: Any = wire(default=None)
    body_raw: bool = wire("body_raw", default=False)
    extra: dict[str, Any] = extra()
