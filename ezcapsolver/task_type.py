"""Task types declared by the service."""

from __future__ import annotations

from enum import StrEnum

__all__ = ["TaskMode", "TaskType"]


class TaskMode(StrEnum):
    """Execution mode the service documents for a task type.

    This is **informational**. Every task type can be run either way: each has a
    ``solve_*`` method that polls and a ``sync_solve_*`` method that uses the
    synchronous endpoint, and nothing in the SDK reads this value to choose
    between them.

    It matters because the service may reject a type on the endpoint it does not
    serve — so this is the mode to follow when there is no reason to prefer the
    other. Such a rejection is refused before billing, so it costs a round trip
    rather than a task.
    """

    #: Created through ``createTask``, then polled until it completes.
    POLLING = "polling"
    #: Runs through ``createSyncTask`` and answers on the creating request.
    SYNC = "sync"


class TaskType(StrEnum):
    """Task types declared by the current EzCaptchaSolver service contract.

    Members **are** their wire strings, so they serialise to JSON and compare
    against plain strings directly::

        >>> TaskType.HCAPTCHA == "HCaptcha"
        True

    To call a task type this release does not know about yet, pass the bare
    string to :meth:`~ezcapsolver.client.EzCapSolverClient.solve_raw`.
    """

    RECAPTCHA_V2_TASK_PROXYLESS = "ReCaptchaV2TaskProxyless"
    RECAPTCHA_V2_TASK_PROXYLESS_S9 = "ReCaptchaV2TaskProxylessS9"
    RECAPTCHA_V2_S_TASK_PROXYLESS = "ReCaptchaV2STaskProxyless"
    RECAPTCHA_V2_ENTERPRISE_TASK_PROXYLESS = "ReCaptchaV2EnterpriseTaskProxyless"
    RECAPTCHA_V2_S_ENTERPRISE_TASK_PROXYLESS = "ReCaptchaV2SEnterpriseTaskProxyless"
    RECAPTCHA_V2_CLASSIFICATION = "ReCaptchaV2Classification"
    RECAPTCHA_V3_TASK_PROXYLESS = "ReCaptchaV3TaskProxyless"
    RECAPTCHA_V3_TASK_PROXYLESS_S9 = "ReCaptchaV3TaskProxylessS9"
    RECAPTCHA_V3_ENTERPRISE_TASK_PROXYLESS = "ReCaptchaV3EnterpriseTaskProxyless"
    # The task catalog writes this one as "RecaptchaV3EnterpriseTaskProxylessS9", with a
    # lowercase c unlike the rest of the family. Every language SDK normalises it so one
    # capitalisation runs through the whole ReCaptcha family; the service matches task
    # types case-insensitively, so it reaches the same worker. Do not "fix" it back.
    RECAPTCHA_V3_ENTERPRISE_TASK_PROXYLESS_S9 = "ReCaptchaV3EnterpriseTaskProxylessS9"
    FUNCAPTCHA_TASK_PROXYLESS = "FuncaptchaTaskProxyless"
    FUNCAPTCHA_CLASSIFICATION = "FunCaptchaClassification"
    PERIMETERX = "PerimeterX"
    HCAPTCHA = "HCaptcha"
    HCAPTCHA_CLASSIFICATION = "HCaptchaClassification"
    AKAMAI_WEB_TASK_PROXYLESS = "AkamaiWEBTaskProxyless"
    AKAMAI_SBSD_TASK_PROXYLESS = "AkamaiSBSDTaskProxyless"
    TLS_TASK = "TlsTask"
    CLOUDFLARE_5S_TASK = "CloudFlare5STask"
    CLOUDFLARE_TURNSTILE_TASK = "CloudFlareTurnstileTask"
    DATADOME_TASK_PROXYLESS = "DataDomeTaskProxyless"
    DATADOME_TAGS_TASK_PROXYLESS = "DataDomeTagsTaskProxyless"
    INCAPSULA_TASK_PROXYLESS = "IncapsulaTaskProxyless"
