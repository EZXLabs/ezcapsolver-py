"""EzCaptchaSolver Python SDK.

Python client library for the EzCaptchaSolver service. The synchronous and
asynchronous clients share models and error types, and all 23 task types go
through one ``solve()`` — the task object carries its own type and solution
shape. ``sync_solve()`` runs any of them on the service's synchronous endpoint
instead, returning the same thing without a task ID.

Example:
    >>> from ezcapsolver import EzCapSolverClient, ReCaptchaV2Task
    >>> with EzCapSolverClient("your-key") as client:  # doctest: +SKIP
    ...     solved = client.solve(
    ...         ReCaptchaV2Task(website_url="https://example.com", website_key="6Lc...")
    ...     )
    ...     print(solved.solution.token)
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("ezcapsolver-py")
except PackageNotFoundError:  # pragma: no cover - only in an uninstalled source tree
    __version__ = "0.0.0-dev"

from ._http import TRACE
from .async_client import AsyncEzCapSolverClient
from .client import EzCapSolverClient
from .config import (
    DEFAULT_ASYNC_BASE_URL,
    DEFAULT_CLIENT_KEY_ENV,
    DEFAULT_SYNC_BASE_URL,
    ClientConfig,
    PollingConfig,
)
from .errors import (
    ApiError,
    EzCaptchaError,
    PollingExhaustedError,
    SolutionDecodeError,
    TransportError,
    UnexpectedResponseError,
    WaitInterruptedError,
    task_id_of,
)
from .responses import MISSING, Solved, TaskResult, TaskStatus
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
from .tasks import (
    AkamaiSBSDTask,
    AkamaiWebTask,
    Cloudflare5sTask,
    CloudflareTurnstileTask,
    DataDomeJsType,
    DataDomeStep,
    DataDomeTagsTask,
    DataDomeTask,
    FunCaptchaClassificationTask,
    FunCaptchaTask,
    HCaptchaClassificationTask,
    HCaptchaTask,
    IncapsulaTask,
    PerimeterXTask,
    ReCaptchaV2ClassificationTask,
    ReCaptchaV2EnterpriseTask,
    ReCaptchaV2S9Task,
    ReCaptchaV2SEnterpriseTask,
    ReCaptchaV2STask,
    ReCaptchaV2Task,
    ReCaptchaV3EnterpriseS9Task,
    ReCaptchaV3EnterpriseTask,
    ReCaptchaV3S9Task,
    ReCaptchaV3Task,
    Task,
    TlsForwardTask,
    TlsHttpMethod,
)

__all__ = [
    "DEFAULT_ASYNC_BASE_URL",
    "DEFAULT_CLIENT_KEY_ENV",
    "DEFAULT_SYNC_BASE_URL",
    "MISSING",
    "TRACE",
    "AkamaiSBSDSolution",
    "AkamaiSBSDTask",
    "AkamaiWebSolution",
    "AkamaiWebTask",
    "ApiError",
    "AsyncEzCapSolverClient",
    "ClientConfig",
    "Cloudflare5sSolution",
    "Cloudflare5sTask",
    "CloudflareTurnstileSolution",
    "CloudflareTurnstileTask",
    "DataDomeJsType",
    "DataDomeSolution",
    "DataDomeStep",
    "DataDomeTagsTask",
    "DataDomeTask",
    "EzCapSolverClient",
    "EzCaptchaError",
    "FunCaptchaClassificationSolution",
    "FunCaptchaClassificationTask",
    "FunCaptchaSolution",
    "FunCaptchaTask",
    "HCaptchaClassificationSolution",
    "HCaptchaClassificationTask",
    "HCaptchaSolution",
    "HCaptchaTask",
    "IncapsulaSolution",
    "IncapsulaTask",
    "PerimeterXSolution",
    "PerimeterXTask",
    "PollingConfig",
    "PollingExhaustedError",
    "ReCaptchaSolution",
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
    "ReClassificationSolution",
    "SolutionDecodeError",
    "Solved",
    "Task",
    "TaskMode",
    "TaskResult",
    "TaskStatus",
    "TaskType",
    "TlsForwardSolution",
    "TlsForwardTask",
    "TlsHttpMethod",
    "TransportError",
    "UnexpectedResponseError",
    "WaitInterruptedError",
    "__version__",
    "task_id_of",
]
