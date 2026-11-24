"""Reading the pages of a DataDome challenge.

The script hash is the key the service caches challenge scripts under, so the
extraction and hashing rules here have to match the service's exactly. The
tests pin them to fixed vectors.
"""

from __future__ import annotations

import base64
import hashlib
import re
from urllib.parse import urlsplit

#: Text DataDome puts on the page of a visitor it has banned outright.
HARD_BLOCK_MARKER = "hardblock"
#: Text every page DataDome intercepted carries.
CHALLENGE_MARKER = "var dd"
#: Path segment of a slider captcha address; the interstitial uses another.
SLIDER_PATH = "/captcha/"
#: What closes the invisible interstitial bundle.
BUNDLE_CLOSE = "})()"
#: CDN scripts that bootstrap a challenge but are not its bundle.
LOADER_SCRIPTS = frozenset({"i.js", "c.js"})

# Every <script> element: its opening tag, then its body.
_SCRIPT_ELEMENT = re.compile(r"(<script\b[^>]*>)(.*?)</script>", re.IGNORECASE | re.DOTALL)
# A src attribute, which marks an opening tag as an external script.
_SRC_ATTRIBUTE = re.compile(r"\bsrc\s*=")
# The version banner, /* DataDome ... */ or /** DataDome ... */.
_BANNER = re.compile(r"/\*+\s*DataDome[^*]*\*/")
# How the interstitial bundle opens, right after its banner.
_INTERSTITIAL_OPENING = re.compile(r"\s*;\s*\(function\s*\(\)\s*\{")
# Where a bundle starts when it carries no banner: the slider or the interstitial form.
_BUNDLE_START = re.compile(r"!\s*function\s+[A-Za-z_$][\w$]*\s*\(|;\s*\(function\s*\(\)\s*\{")
# An external challenge script with a descriptive name.
_NAMED_EXTERNAL_SCRIPT = re.compile(
    r"""<script\b[^>]*?\bsrc\s*=\s*["']((?:https:)?//ct\.captcha-delivery\.com/"""
    r"""(?:interstitial|captcha)\.[^"']+?\.js)["']""",
    re.IGNORECASE,
)
# An external challenge script named by its content hash, which DataDome
# switched to in November 2026.
_HASHED_EXTERNAL_SCRIPT = re.compile(
    r"""<script\b[^>]*?\bsrc\s*=\s*["']((?:https:)?//ct\.captcha-delivery\.com/"""
    r"""[A-Za-z0-9][A-Za-z0-9._-]*?\.js)["']""",
    re.IGNORECASE,
)


def is_hard_blocked(html: str) -> bool:
    """Return whether DataDome banned the visitor outright; only a new IP helps."""
    return HARD_BLOCK_MARKER in html


def is_challenged(html: str) -> bool:
    """Return whether DataDome intercepted the page with a challenge."""
    return CHALLENGE_MARKER in html


def is_slider(challenge_url: str) -> bool:
    """Return whether a challenge address leads to the slider rather than the interstitial."""
    return SLIDER_PATH in urlsplit(challenge_url).path


def encode_text(text: str) -> str:
    """Base64-encode page or script text the way the service expects it."""
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def strip_banner(script: str) -> str:
    """Strip the version banner DataDome puts on the first line of its script.

    The banner changes with every release while the code under it may not, so it
    stays out of the hash. Only a first line that opens and closes a comment
    counts as a banner; anything else is returned unchanged.
    """
    if not script.startswith("/*"):
        return script
    newline = script.find("\n")
    first_line_end = newline + 1 if newline != -1 else len(script)
    return script[first_line_end:] if "*/" in script[:first_line_end] else script


def script_hash(script: str) -> str:
    """Return the content-addressed identifier of a challenge script.

    It is the lower-case hex MD5 of the script without its banner, and the
    service caches scripts under it.
    """
    content = strip_banner(script).encode("utf-8")
    # A content identifier, not a security control.
    return hashlib.md5(content, usedforsecurity=False).hexdigest()


def external_script_url(html: str) -> str | None:
    """Return the address of the challenge script when the page loads it from the CDN.

    A descriptively named script wins; otherwise the first hash-named one that
    is not a loader. A protocol-relative address is completed with ``https:``.
    """
    named = _NAMED_EXTERNAL_SCRIPT.search(html)
    if named:
        return _absolute_src(named.group(1))
    for hashed in _HASHED_EXTERNAL_SCRIPT.finditer(html):
        src = hashed.group(1)
        if src.rsplit("/", 1)[-1].lower() not in LOADER_SCRIPTS:
            return _absolute_src(src)
    return None


def inline_script(html: str) -> str | None:
    """Return the challenge script embedded in the page, cut to its session-independent part.

    The bundle is the longest inline script by far, and it is cut from its
    version banner on. An interstitial bundle also ends at its closing ``})()``:
    what follows is page glue that carries session-unique identifiers, and
    hashing those would never hit the cache. A slider bundle keeps everything to
    the end of its script. Without a banner, the bundle runs from where its code
    starts.
    """
    script = _longest_inline_script(html)
    if script is None:
        return None
    banner = _BANNER.search(script)
    if banner is None:
        start = _BUNDLE_START.search(script)
        return script[start.start() :] if start else script
    bundle = script[banner.start() :]
    if _INTERSTITIAL_OPENING.match(bundle, len(banner.group(0))):
        close = bundle.rfind(BUNDLE_CLOSE)
        if close != -1:
            return bundle[: close + len(BUNDLE_CLOSE)]
    return bundle


def _longest_inline_script(html: str) -> str | None:
    """Return the longest non-empty script without a ``src``; the first one wins a tie."""
    longest = ""
    for element in _SCRIPT_ELEMENT.finditer(html):
        if _SRC_ATTRIBUTE.search(element.group(1)):
            continue
        if len(element.group(2)) > len(longest):
            longest = element.group(2)
    return longest or None


def _absolute_src(src: str) -> str:
    """Complete a protocol-relative script address with ``https:``."""
    return f"https:{src}" if src.startswith("//") else src
