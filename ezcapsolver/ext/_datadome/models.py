"""Input and result of the DataDome challenge workflow."""

from __future__ import annotations

from dataclasses import dataclass, field

#: ``Accept-Language`` sent when the caller does not choose one.
DEFAULT_ACCEPT_LANGUAGE = "en-US,en;q=0.9"


@dataclass(frozen=True, slots=True, kw_only=True)
class DataDomeChallenge:
    """A page behind DataDome, and the browser identity to clear its challenge with.

    Every browser-side request of one run goes out through ``proxy`` with
    ``user_agent``. Keep using both for the requests that carry the cookie the
    run returns.

    Attributes:
        target_url: Page on the protected site. It is fetched first, and the
            workflow only continues when DataDome intercepts it.
        user_agent: Browser ``User-Agent`` sent with every browser-side request.
            Its ``Chrome/<major>`` version also selects the TLS fingerprint, so
            it must name a Chrome release with a fingerprint preset: 131, or 144
            to 158.
        proxy: Proxy for every browser-side request, such as
            ``http://user:pass@host:port``. ``None`` means a direct connection.
            Calls to the EzCaptchaSolver API do not use it; they follow the
            client's own ``proxy``. Left out of ``repr`` to keep credentials out
            of logs.
        accept_language: ``Accept-Language`` sent with every browser-side request.
    """

    target_url: str
    user_agent: str
    proxy: str | None = field(default=None, repr=False)
    accept_language: str = DEFAULT_ACCEPT_LANGUAGE


@dataclass(frozen=True, slots=True, kw_only=True)
class DataDomeCookie:
    """The cookie DataDome issues once its challenge is cleared.

    Attributes:
        name: Cookie name, normally ``datadome``.
        value: Cookie value.
        domain: Domain the cookie applies to. Taken from the ``Domain``
            attribute, or built from the last two labels of the target host,
            such as ``.example.com``, when DataDome omits it.
        raw: The cookie exactly as DataDome returned it, attributes included.
    """

    name: str
    value: str
    domain: str
    raw: str
