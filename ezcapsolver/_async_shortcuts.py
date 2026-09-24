"""Keyword-argument shortcuts for the asynchronous client, two per task type.

The blocking versions live in :mod:`ezcapsolver._shortcuts`; these are the same
signatures with ``await`` added. See that module for the details — in particular
that every type has both a ``solve_*`` and a ``sync_solve_*`` method, and that
``**extra`` forwards unmodelled parameters verbatim, so a misspelled keyword is
forwarded rather than rejected.

Note that ``sync_`` here refers to the service's synchronous endpoint, not to
blocking I/O: these methods are all coroutines.
"""

from __future__ import annotations

from typing import Any

from ._base import BaseClient
from .responses import Solved
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

__all__ = ["AsyncSolveShortcuts"]


class AsyncSolveShortcuts(BaseClient):
    """One ``solve_*`` and one ``sync_solve_*`` per task type, taking fields."""

    __slots__ = ()

    async def solve[S](self, task: Task[S]) -> Solved[S]:
        """Create a task and poll it. Implemented by the concrete client."""
        raise NotImplementedError

    async def sync_solve[S](self, task: Task[S]) -> Solved[S]:
        """Run a task synchronously. Implemented by the concrete client."""
        raise NotImplementedError

    # -- ReCaptcha V2 -----------------------------------------------------

    async def solve_recaptcha_v2_task_proxyless(
        self,
        website_url: str,
        website_key: str,
        *,
        is_invisible: bool = False,
        sa: str | None = None,
        s: str | None = None,
        website_title: str | None = None,
        proxy: str | None = None,
        **extra: Any,
    ) -> Solved[ReCaptchaSolution]:
        """Solve ``ReCaptchaV2TaskProxyless``. See :class:`ReCaptchaV2Task`."""
        return await self.solve(
            ReCaptchaV2Task(
                website_url=website_url,
                website_key=website_key,
                is_invisible=is_invisible,
                sa=sa,
                s=s,
                website_title=website_title,
                proxy=proxy,
                extra=extra,
            )
        )

    async def sync_solve_recaptcha_v2_task_proxyless(
        self,
        website_url: str,
        website_key: str,
        *,
        is_invisible: bool = False,
        sa: str | None = None,
        s: str | None = None,
        website_title: str | None = None,
        proxy: str | None = None,
        **extra: Any,
    ) -> Solved[ReCaptchaSolution]:
        """Solve ``ReCaptchaV2TaskProxyless`` on the synchronous endpoint.

        See :class:`ReCaptchaV2Task`.
        """
        return await self.sync_solve(
            ReCaptchaV2Task(
                website_url=website_url,
                website_key=website_key,
                is_invisible=is_invisible,
                sa=sa,
                s=s,
                website_title=website_title,
                proxy=proxy,
                extra=extra,
            )
        )

    async def solve_recaptcha_v2_task_proxyless_s9(
        self,
        website_url: str,
        website_key: str,
        *,
        is_invisible: bool = False,
        sa: str | None = None,
        s: str | None = None,
        website_title: str | None = None,
        proxy: str | None = None,
        **extra: Any,
    ) -> Solved[ReCaptchaSolution]:
        """Solve ``ReCaptchaV2TaskProxylessS9``. See :class:`ReCaptchaV2S9Task`."""
        return await self.solve(
            ReCaptchaV2S9Task(
                website_url=website_url,
                website_key=website_key,
                is_invisible=is_invisible,
                sa=sa,
                s=s,
                website_title=website_title,
                proxy=proxy,
                extra=extra,
            )
        )

    async def sync_solve_recaptcha_v2_task_proxyless_s9(
        self,
        website_url: str,
        website_key: str,
        *,
        is_invisible: bool = False,
        sa: str | None = None,
        s: str | None = None,
        website_title: str | None = None,
        proxy: str | None = None,
        **extra: Any,
    ) -> Solved[ReCaptchaSolution]:
        """Solve ``ReCaptchaV2TaskProxylessS9`` on the synchronous endpoint.

        See :class:`ReCaptchaV2S9Task`.
        """
        return await self.sync_solve(
            ReCaptchaV2S9Task(
                website_url=website_url,
                website_key=website_key,
                is_invisible=is_invisible,
                sa=sa,
                s=s,
                website_title=website_title,
                proxy=proxy,
                extra=extra,
            )
        )

    async def solve_recaptcha_v2_s_task_proxyless(
        self,
        website_url: str,
        website_key: str,
        *,
        is_invisible: bool = False,
        sa: str | None = None,
        s: str | None = None,
        website_title: str | None = None,
        proxy: str | None = None,
        **extra: Any,
    ) -> Solved[ReCaptchaSolution]:
        """Solve ``ReCaptchaV2STaskProxyless``. See :class:`ReCaptchaV2STask`."""
        return await self.solve(
            ReCaptchaV2STask(
                website_url=website_url,
                website_key=website_key,
                is_invisible=is_invisible,
                sa=sa,
                s=s,
                website_title=website_title,
                proxy=proxy,
                extra=extra,
            )
        )

    async def sync_solve_recaptcha_v2_s_task_proxyless(
        self,
        website_url: str,
        website_key: str,
        *,
        is_invisible: bool = False,
        sa: str | None = None,
        s: str | None = None,
        website_title: str | None = None,
        proxy: str | None = None,
        **extra: Any,
    ) -> Solved[ReCaptchaSolution]:
        """Solve ``ReCaptchaV2STaskProxyless`` on the synchronous endpoint.

        See :class:`ReCaptchaV2STask`.
        """
        return await self.sync_solve(
            ReCaptchaV2STask(
                website_url=website_url,
                website_key=website_key,
                is_invisible=is_invisible,
                sa=sa,
                s=s,
                website_title=website_title,
                proxy=proxy,
                extra=extra,
            )
        )

    async def solve_recaptcha_v2_enterprise_task_proxyless(
        self,
        website_url: str,
        website_key: str,
        *,
        is_invisible: bool = False,
        sa: str | None = None,
        s: str | None = None,
        website_title: str | None = None,
        proxy: str | None = None,
        **extra: Any,
    ) -> Solved[ReCaptchaSolution]:
        """Solve ``ReCaptchaV2EnterpriseTaskProxyless``.

        See :class:`ReCaptchaV2EnterpriseTask`.
        """
        return await self.solve(
            ReCaptchaV2EnterpriseTask(
                website_url=website_url,
                website_key=website_key,
                is_invisible=is_invisible,
                sa=sa,
                s=s,
                website_title=website_title,
                proxy=proxy,
                extra=extra,
            )
        )

    async def sync_solve_recaptcha_v2_enterprise_task_proxyless(
        self,
        website_url: str,
        website_key: str,
        *,
        is_invisible: bool = False,
        sa: str | None = None,
        s: str | None = None,
        website_title: str | None = None,
        proxy: str | None = None,
        **extra: Any,
    ) -> Solved[ReCaptchaSolution]:
        """Solve ``ReCaptchaV2EnterpriseTaskProxyless`` on the synchronous endpoint.

        See :class:`ReCaptchaV2EnterpriseTask`.
        """
        return await self.sync_solve(
            ReCaptchaV2EnterpriseTask(
                website_url=website_url,
                website_key=website_key,
                is_invisible=is_invisible,
                sa=sa,
                s=s,
                website_title=website_title,
                proxy=proxy,
                extra=extra,
            )
        )

    async def solve_recaptcha_v2_s_enterprise_task_proxyless(
        self,
        website_url: str,
        website_key: str,
        *,
        is_invisible: bool = False,
        sa: str | None = None,
        s: str | None = None,
        website_title: str | None = None,
        proxy: str | None = None,
        **extra: Any,
    ) -> Solved[ReCaptchaSolution]:
        """Solve ``ReCaptchaV2SEnterpriseTaskProxyless``.

        See :class:`ReCaptchaV2SEnterpriseTask`.
        """
        return await self.solve(
            ReCaptchaV2SEnterpriseTask(
                website_url=website_url,
                website_key=website_key,
                is_invisible=is_invisible,
                sa=sa,
                s=s,
                website_title=website_title,
                proxy=proxy,
                extra=extra,
            )
        )

    async def sync_solve_recaptcha_v2_s_enterprise_task_proxyless(
        self,
        website_url: str,
        website_key: str,
        *,
        is_invisible: bool = False,
        sa: str | None = None,
        s: str | None = None,
        website_title: str | None = None,
        proxy: str | None = None,
        **extra: Any,
    ) -> Solved[ReCaptchaSolution]:
        """Solve ``ReCaptchaV2SEnterpriseTaskProxyless`` on the synchronous endpoint.

        See :class:`ReCaptchaV2SEnterpriseTask`.
        """
        return await self.sync_solve(
            ReCaptchaV2SEnterpriseTask(
                website_url=website_url,
                website_key=website_key,
                is_invisible=is_invisible,
                sa=sa,
                s=s,
                website_title=website_title,
                proxy=proxy,
                extra=extra,
            )
        )

    async def solve_recaptcha_v2_classification(
        self,
        image: str,
        question: str,
        *,
        size: int = 4,
        **extra: Any,
    ) -> Solved[ReClassificationSolution]:
        """Solve ``ReCaptchaV2Classification``.

        See :class:`ReCaptchaV2ClassificationTask`.
        """
        return await self.solve(
            ReCaptchaV2ClassificationTask(
                image=image,
                question=question,
                size=size,
                extra=extra,
            )
        )

    async def sync_solve_recaptcha_v2_classification(
        self,
        image: str,
        question: str,
        *,
        size: int = 4,
        **extra: Any,
    ) -> Solved[ReClassificationSolution]:
        """Solve ``ReCaptchaV2Classification`` on the synchronous endpoint.

        See :class:`ReCaptchaV2ClassificationTask`.
        """
        return await self.sync_solve(
            ReCaptchaV2ClassificationTask(
                image=image,
                question=question,
                size=size,
                extra=extra,
            )
        )

    # -- ReCaptcha V3 -----------------------------------------------------

    async def solve_recaptcha_v3_task_proxyless(
        self,
        website_url: str,
        website_key: str,
        *,
        is_invisible: bool = True,
        page_action: str | None = None,
        website_title: str | None = None,
        check_field: str | None = None,
        proxy: str | None = None,
        **extra: Any,
    ) -> Solved[ReCaptchaSolution]:
        """Solve ``ReCaptchaV3TaskProxyless``. See :class:`ReCaptchaV3Task`."""
        return await self.solve(
            ReCaptchaV3Task(
                website_url=website_url,
                website_key=website_key,
                is_invisible=is_invisible,
                page_action=page_action,
                website_title=website_title,
                check_field=check_field,
                proxy=proxy,
                extra=extra,
            )
        )

    async def sync_solve_recaptcha_v3_task_proxyless(
        self,
        website_url: str,
        website_key: str,
        *,
        is_invisible: bool = True,
        page_action: str | None = None,
        website_title: str | None = None,
        check_field: str | None = None,
        proxy: str | None = None,
        **extra: Any,
    ) -> Solved[ReCaptchaSolution]:
        """Solve ``ReCaptchaV3TaskProxyless`` on the synchronous endpoint.

        See :class:`ReCaptchaV3Task`.
        """
        return await self.sync_solve(
            ReCaptchaV3Task(
                website_url=website_url,
                website_key=website_key,
                is_invisible=is_invisible,
                page_action=page_action,
                website_title=website_title,
                check_field=check_field,
                proxy=proxy,
                extra=extra,
            )
        )

    async def solve_recaptcha_v3_task_proxyless_s9(
        self,
        website_url: str,
        website_key: str,
        *,
        is_invisible: bool = True,
        page_action: str | None = None,
        website_title: str | None = None,
        check_field: str | None = None,
        proxy: str | None = None,
        **extra: Any,
    ) -> Solved[ReCaptchaSolution]:
        """Solve ``ReCaptchaV3TaskProxylessS9``. See :class:`ReCaptchaV3S9Task`."""
        return await self.solve(
            ReCaptchaV3S9Task(
                website_url=website_url,
                website_key=website_key,
                is_invisible=is_invisible,
                page_action=page_action,
                website_title=website_title,
                check_field=check_field,
                proxy=proxy,
                extra=extra,
            )
        )

    async def sync_solve_recaptcha_v3_task_proxyless_s9(
        self,
        website_url: str,
        website_key: str,
        *,
        is_invisible: bool = True,
        page_action: str | None = None,
        website_title: str | None = None,
        check_field: str | None = None,
        proxy: str | None = None,
        **extra: Any,
    ) -> Solved[ReCaptchaSolution]:
        """Solve ``ReCaptchaV3TaskProxylessS9`` on the synchronous endpoint.

        See :class:`ReCaptchaV3S9Task`.
        """
        return await self.sync_solve(
            ReCaptchaV3S9Task(
                website_url=website_url,
                website_key=website_key,
                is_invisible=is_invisible,
                page_action=page_action,
                website_title=website_title,
                check_field=check_field,
                proxy=proxy,
                extra=extra,
            )
        )

    async def solve_recaptcha_v3_enterprise_task_proxyless(
        self,
        website_url: str,
        website_key: str,
        *,
        is_invisible: bool = True,
        page_action: str | None = None,
        website_title: str | None = None,
        check_field: str | None = None,
        proxy: str | None = None,
        **extra: Any,
    ) -> Solved[ReCaptchaSolution]:
        """Solve ``ReCaptchaV3EnterpriseTaskProxyless``.

        See :class:`ReCaptchaV3EnterpriseTask`.
        """
        return await self.solve(
            ReCaptchaV3EnterpriseTask(
                website_url=website_url,
                website_key=website_key,
                is_invisible=is_invisible,
                page_action=page_action,
                website_title=website_title,
                check_field=check_field,
                proxy=proxy,
                extra=extra,
            )
        )

    async def sync_solve_recaptcha_v3_enterprise_task_proxyless(
        self,
        website_url: str,
        website_key: str,
        *,
        is_invisible: bool = True,
        page_action: str | None = None,
        website_title: str | None = None,
        check_field: str | None = None,
        proxy: str | None = None,
        **extra: Any,
    ) -> Solved[ReCaptchaSolution]:
        """Solve ``ReCaptchaV3EnterpriseTaskProxyless`` on the synchronous endpoint.

        See :class:`ReCaptchaV3EnterpriseTask`.
        """
        return await self.sync_solve(
            ReCaptchaV3EnterpriseTask(
                website_url=website_url,
                website_key=website_key,
                is_invisible=is_invisible,
                page_action=page_action,
                website_title=website_title,
                check_field=check_field,
                proxy=proxy,
                extra=extra,
            )
        )

    async def solve_recaptcha_v3_enterprise_task_proxyless_s9(
        self,
        website_url: str,
        website_key: str,
        *,
        is_invisible: bool = True,
        page_action: str | None = None,
        website_title: str | None = None,
        check_field: str | None = None,
        proxy: str | None = None,
        **extra: Any,
    ) -> Solved[ReCaptchaSolution]:
        """Solve ``ReCaptchaV3EnterpriseTaskProxylessS9``.

        See :class:`ReCaptchaV3EnterpriseS9Task`.
        """
        return await self.solve(
            ReCaptchaV3EnterpriseS9Task(
                website_url=website_url,
                website_key=website_key,
                is_invisible=is_invisible,
                page_action=page_action,
                website_title=website_title,
                check_field=check_field,
                proxy=proxy,
                extra=extra,
            )
        )

    async def sync_solve_recaptcha_v3_enterprise_task_proxyless_s9(
        self,
        website_url: str,
        website_key: str,
        *,
        is_invisible: bool = True,
        page_action: str | None = None,
        website_title: str | None = None,
        check_field: str | None = None,
        proxy: str | None = None,
        **extra: Any,
    ) -> Solved[ReCaptchaSolution]:
        """Solve ``ReCaptchaV3EnterpriseTaskProxylessS9`` on the synchronous endpoint.

        See :class:`ReCaptchaV3EnterpriseS9Task`.
        """
        return await self.sync_solve(
            ReCaptchaV3EnterpriseS9Task(
                website_url=website_url,
                website_key=website_key,
                is_invisible=is_invisible,
                page_action=page_action,
                website_title=website_title,
                check_field=check_field,
                proxy=proxy,
                extra=extra,
            )
        )

    # -- FunCaptcha -------------------------------------------------------

    async def solve_funcaptcha_task_proxyless(
        self,
        website_url: str,
        website_key: str,
        *,
        data: str | None = None,
        api_js_subdomain: str | None = None,
        proxy: str | None = None,
        cn: bool = False,
        **extra: Any,
    ) -> Solved[FunCaptchaSolution]:
        """Solve ``FuncaptchaTaskProxyless``. See :class:`FunCaptchaTask`."""
        return await self.solve(
            FunCaptchaTask(
                website_url=website_url,
                website_key=website_key,
                data=data,
                api_js_subdomain=api_js_subdomain,
                proxy=proxy,
                cn=cn,
                extra=extra,
            )
        )

    async def sync_solve_funcaptcha_task_proxyless(
        self,
        website_url: str,
        website_key: str,
        *,
        data: str | None = None,
        api_js_subdomain: str | None = None,
        proxy: str | None = None,
        cn: bool = False,
        **extra: Any,
    ) -> Solved[FunCaptchaSolution]:
        """Solve ``FuncaptchaTaskProxyless`` on the synchronous endpoint.

        See :class:`FunCaptchaTask`.
        """
        return await self.sync_solve(
            FunCaptchaTask(
                website_url=website_url,
                website_key=website_key,
                data=data,
                api_js_subdomain=api_js_subdomain,
                proxy=proxy,
                cn=cn,
                extra=extra,
            )
        )

    async def solve_funcaptcha_classification(
        self,
        image: str,
        question: str,
        **extra: Any,
    ) -> Solved[FunCaptchaClassificationSolution]:
        """Solve ``FunCaptchaClassification``.

        See :class:`FunCaptchaClassificationTask`. The solution shape is
        unconfirmed, so the raw JSON value is returned.
        """
        return await self.solve(
            FunCaptchaClassificationTask(
                image=image,
                question=question,
                extra=extra,
            )
        )

    async def sync_solve_funcaptcha_classification(
        self,
        image: str,
        question: str,
        **extra: Any,
    ) -> Solved[FunCaptchaClassificationSolution]:
        """Solve ``FunCaptchaClassification`` on the synchronous endpoint.

        See :class:`FunCaptchaClassificationTask`. The solution shape is
        unconfirmed, so the raw JSON value is returned.
        """
        return await self.sync_solve(
            FunCaptchaClassificationTask(
                image=image,
                question=question,
                extra=extra,
            )
        )

    # -- HCaptcha ---------------------------------------------------------

    async def solve_hcaptcha(
        self,
        website_url: str,
        website_key: str,
        lang: str,
        *,
        invisible: bool,
        proxy: str | None = None,
        rq_data: str | None = None,
        **extra: Any,
    ) -> Solved[HCaptchaSolution]:
        """Solve ``HCaptcha``. See :class:`HCaptchaTask`."""
        return await self.solve(
            HCaptchaTask(
                website_url=website_url,
                website_key=website_key,
                lang=lang,
                proxy=proxy,
                invisible=invisible,
                rq_data=rq_data,
                extra=extra,
            )
        )

    async def sync_solve_hcaptcha(
        self,
        website_url: str,
        website_key: str,
        lang: str,
        *,
        invisible: bool,
        proxy: str | None = None,
        rq_data: str | None = None,
        **extra: Any,
    ) -> Solved[HCaptchaSolution]:
        """Solve ``HCaptcha`` on the synchronous endpoint. See :class:`HCaptchaTask`."""
        return await self.sync_solve(
            HCaptchaTask(
                website_url=website_url,
                website_key=website_key,
                lang=lang,
                proxy=proxy,
                invisible=invisible,
                rq_data=rq_data,
                extra=extra,
            )
        )

    async def solve_hcaptcha_classification(
        self,
        *,
        image: str | None = None,
        images: list[str] | None = None,
        anchors: list[str] | None = None,
        question: str | None = None,
        module: str | None = None,
        **extra: Any,
    ) -> Solved[HCaptchaClassificationSolution]:
        """Solve ``HCaptchaClassification``.

        See :class:`HCaptchaClassificationTask`. Every field is optional
        because different modules take different inputs, and the solution shape
        is unconfirmed, so the raw JSON value is returned.
        """
        return await self.solve(
            HCaptchaClassificationTask(
                image=image,
                images=images,
                anchors=anchors,
                question=question,
                module=module,
                extra=extra,
            )
        )

    async def sync_solve_hcaptcha_classification(
        self,
        *,
        image: str | None = None,
        images: list[str] | None = None,
        anchors: list[str] | None = None,
        question: str | None = None,
        module: str | None = None,
        **extra: Any,
    ) -> Solved[HCaptchaClassificationSolution]:
        """Solve ``HCaptchaClassification`` on the synchronous endpoint.

        See :class:`HCaptchaClassificationTask`. Every field is optional
        because different modules take different inputs, and the solution shape
        is unconfirmed, so the raw JSON value is returned.
        """
        return await self.sync_solve(
            HCaptchaClassificationTask(
                image=image,
                images=images,
                anchors=anchors,
                question=question,
                module=module,
                extra=extra,
            )
        )

    # -- Cloudflare -------------------------------------------------------

    async def solve_cloudflare_5s_task(
        self,
        website_url: str,
        proxy: str,
        *,
        rq_data: dict[str, Any] | None = None,
        **extra: Any,
    ) -> Solved[Cloudflare5sSolution]:
        """Solve ``CloudFlare5STask``.

        See :class:`Cloudflare5sTask`. A proxy is required for this type.
        """
        return await self.solve(
            Cloudflare5sTask(
                website_url=website_url,
                proxy=proxy,
                rq_data=rq_data,
                extra=extra,
            )
        )

    async def sync_solve_cloudflare_5s_task(
        self,
        website_url: str,
        proxy: str,
        *,
        rq_data: dict[str, Any] | None = None,
        **extra: Any,
    ) -> Solved[Cloudflare5sSolution]:
        """Solve ``CloudFlare5STask`` on the synchronous endpoint.

        See :class:`Cloudflare5sTask`. A proxy is required for this type.
        """
        return await self.sync_solve(
            Cloudflare5sTask(
                website_url=website_url,
                proxy=proxy,
                rq_data=rq_data,
                extra=extra,
            )
        )

    async def solve_cloudflare_turnstile_task(
        self,
        website_url: str,
        website_key: str,
        *,
        proxy: str | None = None,
        rq_data: dict[str, Any] | None = None,
        **extra: Any,
    ) -> Solved[CloudflareTurnstileSolution]:
        """Solve ``CloudFlareTurnstileTask``. See :class:`CloudflareTurnstileTask`."""
        return await self.solve(
            CloudflareTurnstileTask(
                website_url=website_url,
                website_key=website_key,
                proxy=proxy,
                rq_data=rq_data,
                extra=extra,
            )
        )

    async def sync_solve_cloudflare_turnstile_task(
        self,
        website_url: str,
        website_key: str,
        *,
        proxy: str | None = None,
        rq_data: dict[str, Any] | None = None,
        **extra: Any,
    ) -> Solved[CloudflareTurnstileSolution]:
        """Solve ``CloudFlareTurnstileTask`` on the synchronous endpoint.

        See :class:`CloudflareTurnstileTask`.
        """
        return await self.sync_solve(
            CloudflareTurnstileTask(
                website_url=website_url,
                website_key=website_key,
                proxy=proxy,
                rq_data=rq_data,
                extra=extra,
            )
        )

    # -- Akamai -----------------------------------------------------------

    async def solve_akamai_web_task_proxyless(
        self,
        page_url: str,
        v3_url: str,
        ua: str,
        lang: str,
        *,
        index: int = 0,
        abck: str = "",
        bmsz: str = "",
        script_base64: str = "",
        encode_data: str = "",
        **extra: Any,
    ) -> Solved[AkamaiWebSolution]:
        """Solve ``AkamaiWEBTaskProxyless``.

        See :class:`AkamaiWebTask`. This is a multi-round flow: feed the
        previous round's ``encodedata`` back in as ``encode_data``.
        """
        return await self.solve(
            AkamaiWebTask(
                page_url=page_url,
                v3_url=v3_url,
                ua=ua,
                lang=lang,
                index=index,
                abck=abck,
                bmsz=bmsz,
                script_base64=script_base64,
                encode_data=encode_data,
                extra=extra,
            )
        )

    async def sync_solve_akamai_web_task_proxyless(
        self,
        page_url: str,
        v3_url: str,
        ua: str,
        lang: str,
        *,
        index: int = 0,
        abck: str = "",
        bmsz: str = "",
        script_base64: str = "",
        encode_data: str = "",
        **extra: Any,
    ) -> Solved[AkamaiWebSolution]:
        """Solve ``AkamaiWEBTaskProxyless`` on the synchronous endpoint.

        See :class:`AkamaiWebTask`. This is a multi-round flow: feed the
        previous round's ``encodedata`` back in as ``encode_data``.
        """
        return await self.sync_solve(
            AkamaiWebTask(
                page_url=page_url,
                v3_url=v3_url,
                ua=ua,
                lang=lang,
                index=index,
                abck=abck,
                bmsz=bmsz,
                script_base64=script_base64,
                encode_data=encode_data,
                extra=extra,
            )
        )

    async def solve_akamai_sbsd_task_proxyless(
        self,
        page_url: str,
        sbsd_url: str,
        bm_so: str,
        ua: str,
        lang: str,
        script_base64: str,
        **extra: Any,
    ) -> Solved[AkamaiSBSDSolution]:
        """Solve ``AkamaiSBSDTaskProxyless``. See :class:`AkamaiSBSDTask`."""
        return await self.solve(
            AkamaiSBSDTask(
                page_url=page_url,
                sbsd_url=sbsd_url,
                bm_so=bm_so,
                ua=ua,
                lang=lang,
                script_base64=script_base64,
                extra=extra,
            )
        )

    async def sync_solve_akamai_sbsd_task_proxyless(
        self,
        page_url: str,
        sbsd_url: str,
        bm_so: str,
        ua: str,
        lang: str,
        script_base64: str,
        **extra: Any,
    ) -> Solved[AkamaiSBSDSolution]:
        """Solve ``AkamaiSBSDTaskProxyless`` on the synchronous endpoint.

        See :class:`AkamaiSBSDTask`.
        """
        return await self.sync_solve(
            AkamaiSBSDTask(
                page_url=page_url,
                sbsd_url=sbsd_url,
                bm_so=bm_so,
                ua=ua,
                lang=lang,
                script_base64=script_base64,
                extra=extra,
            )
        )

    # -- DataDome ---------------------------------------------------------

    async def solve_data_dome_task_proxyless(
        self,
        html_b64: str,
        *,
        step: DataDomeStep = DataDomeStep.ONE,
        image: str = "",
        referer: str | None = None,
        parent_url: str | None = None,
        equipment: str | None = None,
        **extra: Any,
    ) -> Solved[DataDomeSolution]:
        """Solve ``DataDomeTaskProxyless``.

        See :class:`DataDomeTask`. Step one returns the challenge URL, step two
        the validation instructions.
        """
        return await self.solve(
            DataDomeTask(
                html_b64=html_b64,
                step=step,
                image=image,
                referer=referer,
                parent_url=parent_url,
                equipment=equipment,
                extra=extra,
            )
        )

    async def sync_solve_data_dome_task_proxyless(
        self,
        html_b64: str,
        *,
        step: DataDomeStep = DataDomeStep.ONE,
        image: str = "",
        referer: str | None = None,
        parent_url: str | None = None,
        equipment: str | None = None,
        **extra: Any,
    ) -> Solved[DataDomeSolution]:
        """Solve ``DataDomeTaskProxyless`` on the synchronous endpoint.

        See :class:`DataDomeTask`. Step one returns the challenge URL, step two
        the validation instructions.
        """
        return await self.sync_solve(
            DataDomeTask(
                html_b64=html_b64,
                step=step,
                image=image,
                referer=referer,
                parent_url=parent_url,
                equipment=equipment,
                extra=extra,
            )
        )

    async def solve_data_dome_tags_task_proxyless(
        self,
        ddk: str,
        referer: str,
        ua: str,
        *,
        jstype: DataDomeJsType = DataDomeJsType.CH,
        cid: str = "",
        bpc: int = 1,
        fields: dict[str, Any] | None = None,
        **extra: Any,
    ) -> Solved[DataDomeSolution]:
        """Solve ``DataDomeTagsTaskProxyless``. See :class:`DataDomeTagsTask`."""
        return await self.solve(
            DataDomeTagsTask(
                ddk=ddk,
                jstype=jstype,
                cid=cid,
                bpc=bpc,
                referer=referer,
                ua=ua,
                fields=fields if fields is not None else {},
                extra=extra,
            )
        )

    async def sync_solve_data_dome_tags_task_proxyless(
        self,
        ddk: str,
        referer: str,
        ua: str,
        *,
        jstype: DataDomeJsType = DataDomeJsType.CH,
        cid: str = "",
        bpc: int = 1,
        fields: dict[str, Any] | None = None,
        **extra: Any,
    ) -> Solved[DataDomeSolution]:
        """Solve ``DataDomeTagsTaskProxyless`` on the synchronous endpoint.

        See :class:`DataDomeTagsTask`.
        """
        return await self.sync_solve(
            DataDomeTagsTask(
                ddk=ddk,
                jstype=jstype,
                cid=cid,
                bpc=bpc,
                referer=referer,
                ua=ua,
                fields=fields if fields is not None else {},
                extra=extra,
            )
        )

    # -- Other protection systems -----------------------------------------

    async def solve_perimeter_x(
        self,
        website_key: str,
        *,
        invisible: bool = False,
        **extra: Any,
    ) -> Solved[PerimeterXSolution]:
        """Solve ``PerimeterX``. See :class:`PerimeterXTask`."""
        return await self.solve(
            PerimeterXTask(
                website_key=website_key,
                invisible=invisible,
                extra=extra,
            )
        )

    async def sync_solve_perimeter_x(
        self,
        website_key: str,
        *,
        invisible: bool = False,
        **extra: Any,
    ) -> Solved[PerimeterXSolution]:
        """Solve ``PerimeterX`` on the synchronous endpoint. See :class:`PerimeterXTask`."""
        return await self.sync_solve(
            PerimeterXTask(
                website_key=website_key,
                invisible=invisible,
                extra=extra,
            )
        )

    async def solve_incapsula_task_proxyless(
        self,
        script: str,
        script_url: str,
        page_url: str,
        ua: str,
        *,
        accept_language: str | None = None,
        proxy: str | None = None,
        # The parameter name has to match the task field, which test_shortcuts.py
        # enforces, and that field follows the wire name `pow`.
        pow: str | None = None,  # noqa: A002
        **extra: Any,
    ) -> Solved[IncapsulaSolution]:
        """Solve ``IncapsulaTaskProxyless``. See :class:`IncapsulaTask`."""
        return await self.solve(
            IncapsulaTask(
                script=script,
                script_url=script_url,
                page_url=page_url,
                accept_language=accept_language,
                ua=ua,
                proxy=proxy,
                pow=pow,
                extra=extra,
            )
        )

    async def sync_solve_incapsula_task_proxyless(
        self,
        script: str,
        script_url: str,
        page_url: str,
        ua: str,
        *,
        accept_language: str | None = None,
        proxy: str | None = None,
        # The parameter name has to match the task field, which test_shortcuts.py
        # enforces, and that field follows the wire name `pow`.
        pow: str | None = None,  # noqa: A002
        **extra: Any,
    ) -> Solved[IncapsulaSolution]:
        """Solve ``IncapsulaTaskProxyless`` on the synchronous endpoint.

        See :class:`IncapsulaTask`.
        """
        return await self.sync_solve(
            IncapsulaTask(
                script=script,
                script_url=script_url,
                page_url=page_url,
                accept_language=accept_language,
                ua=ua,
                proxy=proxy,
                pow=pow,
                extra=extra,
            )
        )

    async def solve_tls_task(
        self,
        tls_type: str,
        proxy: str,
        url: str,
        *,
        method: TlsHttpMethod = TlsHttpMethod.GET,
        headers: dict[str, Any] | None = None,
        headers_order: str | None = None,
        cookies: dict[str, Any] | None = None,
        body: Any = None,
        body_raw: bool = False,
        **extra: Any,
    ) -> Solved[TlsForwardSolution]:
        """Solve ``TlsTask``. See :class:`TlsForwardTask`."""
        return await self.solve(
            TlsForwardTask(
                tls_type=tls_type,
                proxy=proxy,
                method=method,
                url=url,
                headers=headers,
                headers_order=headers_order,
                cookies=cookies,
                body=body,
                body_raw=body_raw,
                extra=extra,
            )
        )

    async def sync_solve_tls_task(
        self,
        tls_type: str,
        proxy: str,
        url: str,
        *,
        method: TlsHttpMethod = TlsHttpMethod.GET,
        headers: dict[str, Any] | None = None,
        headers_order: str | None = None,
        cookies: dict[str, Any] | None = None,
        body: Any = None,
        body_raw: bool = False,
        **extra: Any,
    ) -> Solved[TlsForwardSolution]:
        """Solve ``TlsTask`` on the synchronous endpoint. See :class:`TlsForwardTask`."""
        return await self.sync_solve(
            TlsForwardTask(
                tls_type=tls_type,
                proxy=proxy,
                method=method,
                url=url,
                headers=headers,
                headers_order=headers_order,
                cookies=cookies,
                body=body,
                body_raw=body_raw,
                extra=extra,
            )
        )
