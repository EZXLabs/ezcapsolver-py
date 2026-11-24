"""Workflow methods of the async client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .._base import BaseClient
from ..errors import EzCaptchaError

if TYPE_CHECKING:
    from ..responses import Solved
    from ..tasks import Task
    from ._datadome import DataDomeChallenge, DataDomeCookie

#: The extra that installs what the DataDome workflow needs.
_DATADOME_EXTRA = "ezcapsolver-py[datadome]"


class AsyncWorkflows(BaseClient):
    """One ``solve_*_workflow`` per extension; see :mod:`ezcapsolver.ext`."""

    __slots__ = ()

    async def sync_solve[S](self, task: Task[S]) -> Solved[S]:
        """Run a task synchronously. Implemented by the concrete client."""
        raise NotImplementedError

    async def solve_data_dome_workflow(self, challenge: DataDomeChallenge) -> DataDomeCookie | None:
        """Clear the DataDome challenge in front of a page and return its cookie.

        Only the page address and a browser identity are needed; the whole flow
        runs inside this call:

        1. Fetch the target page. A page DataDome did not intercept ends the run
           and returns ``None``.
        2. Step one finds the challenge address, and the challenge page is
           fetched.
        3. The challenge script is read from that page, or fetched from
           DataDome's CDN when the page links it.
        4. Step two asks whether the service already caches the script.
        5. Step three computes the answer, sending the whole script only when it
           is not cached.
        6. The answer is submitted after the delay it asks for, and the cookie
           in DataDome's response is returned.

        Steps one to three are ``DataDomeTaskProxyless`` tasks on the synchronous
        endpoint, so a challenged page costs three tasks. Browser-side requests
        go through ``challenge.proxy`` with the Chrome TLS fingerprint of
        ``challenge.user_agent``. Needs the ``datadome`` extra.

        Args:
            challenge: The page, and the browser identity to clear it with.

        Returns:
            The cookie DataDome issued, or ``None`` when it let the page through.

        Raises:
            DataDomeBlockedError: DataDome banned the IP; retry through a
                different proxy.
            DataDomeError: The flow cannot go on: an unusable ``target_url``,
                ``user_agent`` or ``proxy``, a challenge without a script, or a
                submission DataDome did not accept.
            BrowserRequestError: A request to the protected site or to DataDome
                failed.
            EzCaptchaError: The ``datadome`` extra is not installed, or an API
                call failed as it would from ``sync_solve``.
        """
        try:
            from ._datadome.workflow import solve_data_dome
        except ModuleNotFoundError as error:
            if error.name != "lkrequest":
                raise
            raise EzCaptchaError(
                f"the DataDome workflow needs lkrequest; install {_DATADOME_EXTRA}"
            ) from error
        return await solve_data_dome(self, challenge)
