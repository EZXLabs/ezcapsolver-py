"""The browser a challenge run presents itself as.

DataDome compares what each request claims against how it is sent, so every
header set here mirrors what Chrome sends for that kind of request, and the TLS
fingerprint follows the Chrome version the user agent names.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Self
from urllib.parse import urlsplit

from .._errors import DataDomeError

#: Request headers, in the order they are sent.
type Headers = list[tuple[str, str]]

#: ``Accept`` of a document or frame navigation.
DOCUMENT_ACCEPT = (
    "text/html,application/xhtml+xml,application/xml;q=0.9,"
    "image/avif,image/webp,image/apng,*/*;q=0.8"
)
#: ``Accept-Encoding`` Chrome sends.
ACCEPT_ENCODING = "gzip, deflate, br, zstd"
#: Origin of the page a POST submission comes from.
CHALLENGE_ORIGIN = "https://geo.captcha-delivery.com"
#: Content type of a POST submission.
FORM_CONTENT_TYPE = "application/x-www-form-urlencoded; charset=UTF-8"

_CHROME_VERSION = re.compile(r"Chrome/(\d+)")


@dataclass(frozen=True, slots=True)
class BrowserProfile:
    """Browser identity every request of one challenge run shares.

    Attributes:
        user_agent: The ``User-Agent`` every request carries.
        accept_language: The ``Accept-Language`` every request carries.
        chrome_major: Chrome major version named in the user agent.
    """

    user_agent: str
    accept_language: str
    chrome_major: int

    @classmethod
    def create(cls, user_agent: str, accept_language: str) -> Self:
        """Build the profile, rejecting a user agent that names no Chrome version."""
        match = _CHROME_VERSION.search(user_agent)
        if match is None:
            raise DataDomeError(f"user_agent must name a Chrome version, got {user_agent!r}")
        return cls(user_agent, accept_language, int(match.group(1)))

    def navigation(self) -> Headers:
        """Return the headers of the first visit to the protected page."""
        return [
            *self._device(),
            ("accept", DOCUMENT_ACCEPT),
            ("upgrade-insecure-requests", "1"),
            ("sec-fetch-site", "none"),
            ("sec-fetch-mode", "navigate"),
            ("sec-fetch-user", "?1"),
            ("sec-fetch-dest", "document"),
        ]

    def challenge_frame(self, target_url: str, *, slider: bool) -> Headers:
        """Return the headers of loading the challenge into its frame.

        The slider frame gets the full page address as its referer; the
        interstitial only its origin, as a real visitor's browser sends them.
        """
        return [
            *self._device(),
            ("accept", DOCUMENT_ACCEPT),
            ("upgrade-insecure-requests", "1"),
            ("sec-fetch-site", "cross-site"),
            ("sec-fetch-mode", "navigate"),
            ("sec-fetch-dest", "iframe"),
            ("referer", target_url if slider else origin(target_url)),
        ]

    def script(self, challenge_url: str) -> Headers:
        """Return the headers of fetching the external challenge script.

        It has to look like a script load: the CDN rejects navigation headers.
        """
        return [
            *self._device(),
            ("accept", "*/*"),
            ("sec-fetch-site", "same-site"),
            ("sec-fetch-mode", "no-cors"),
            ("sec-fetch-dest", "script"),
            ("referer", f"{origin(challenge_url)}/"),
        ]

    def submission(self, challenge_url: str, *, post: bool) -> Headers:
        """Return the headers of submitting the answer from the challenge frame."""
        form = [("content-type", FORM_CONTENT_TYPE), ("origin", CHALLENGE_ORIGIN)] if post else []
        return [
            *self._device(),
            *form,
            ("accept", "*/*"),
            ("sec-fetch-site", "same-origin"),
            ("sec-fetch-mode", "cors"),
            ("sec-fetch-dest", "empty"),
            ("referer", challenge_url),
        ]

    def _device(self) -> Headers:
        """Return the headers every request carries: the client hints and the identity."""
        return [
            ("sec-ch-ua", self._sec_ch_ua()),
            ("sec-ch-ua-mobile", "?0"),
            ("sec-ch-ua-platform", f'"{self._platform()}"'),
            ("user-agent", self.user_agent),
            ("accept-encoding", ACCEPT_ENCODING),
            ("accept-language", self.accept_language),
        ]

    def _sec_ch_ua(self) -> str:
        """Return the ``Sec-CH-UA`` brand list matching the Chrome version."""
        version = self.chrome_major
        return f'"Chromium";v="{version}", "Google Chrome";v="{version}", "Not/A)Brand";v="99"'

    def _platform(self) -> str:
        """Return the ``Sec-CH-UA-Platform`` value matching the user agent's system."""
        if "Macintosh" in self.user_agent:
            return "macOS"
        if "Linux" in self.user_agent:
            return "Linux"
        return "Windows"


def origin(url: str) -> str:
    """Return ``scheme://host[:port]`` of an address, the form an origin-only referer takes."""
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}"
