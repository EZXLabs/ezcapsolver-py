"""Packaging metadata that is easy to break silently."""

from __future__ import annotations

import tomllib
from pathlib import Path

import ezcapsolver
from ezcapsolver import ClientConfig

PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"


def _pyproject() -> dict:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))


def test_version_is_read_from_the_installed_distribution():
    # __init__ reads the version with importlib.metadata.version(<distribution name>).
    # Renaming the distribution without updating that lookup silently falls back to 0.0.0-dev,
    # which also makes the default User-Agent incorrect without raising an error.
    assert ezcapsolver.__version__ != "0.0.0-dev"
    assert ezcapsolver.__version__ == _pyproject()["project"]["version"]


def test_the_default_user_agent_names_the_sdk_and_its_version():
    assert ClientConfig(client_key="k").user_agent == f"ezcapsolver-py/{ezcapsolver.__version__}"


def test_every_public_name_is_importable():
    # Catch names listed in __all__ but not exported before a caller's
    # from ezcapsolver import X statement fails.
    missing = [name for name in ezcapsolver.__all__ if not hasattr(ezcapsolver, name)]
    assert not missing
