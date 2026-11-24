"""Errors raised by the workflows in :mod:`ezcapsolver.ext`.

They all derive from :class:`~ezcapsolver.errors.EzCaptchaError`, so catching
that one base class still covers every failure a workflow can raise.
"""

from __future__ import annotations

from ..errors import EzCaptchaError


class BrowserRequestError(EzCaptchaError):
    """A browser-side request of a workflow failed.

    These requests go to the protected site and to the anti-bot vendor, not to
    the EzCaptchaSolver API. The transport failure is chained as ``__cause__``.
    """


class DataDomeError(EzCaptchaError):
    """The DataDome challenge workflow could not be completed.

    The message names the stage that failed: an unusable input, a challenge
    without a script, or a submission DataDome did not accept.
    """


class DataDomeBlockedError(DataDomeError):
    """DataDome banned the visitor outright, which no challenge clears.

    The ban follows the IP, so retry through a different proxy.
    """
