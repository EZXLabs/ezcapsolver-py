# Contributing

Thanks for your interest in improving `ezcapsolver-py`.

## Development Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --all-groups
```

Optionally install the hooks, which run the gates below on every commit.
`pre-commit` is a standalone tool, not a project dependency:

```bash
uv tool install pre-commit
pre-commit install
```

## Local Checks

Run all four gates before opening a PR:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy ezcapsolver examples
uv run pytest -q
```

CI additionally runs a spell check (`typos`), a dependency audit
(`pip-audit`) and a packaging smoke test. To reproduce them locally:

```bash
uvx typos
uv run --with pip-audit pip-audit
uv build && uvx twine check dist/*
```

## Adding a Task Type

A new CAPTCHA type is one dataclass in `ezcapsolver/tasks.py` — declare
`task_type`, `solution_type` and `mode`, then export it from `__init__.py`.
`mode` is informational: it records the execution mode the service documents,
and nothing reads it to route a task.

Then add both shortcuts — `solve_*` and `sync_solve_*` — to `_shortcuts.py` and
`_async_shortcuts.py`. `tests/test_shortcuts.py` checks all four against the
task model, so a missing one fails the suite.

Variants of an existing family (high-score, enterprise) are subclasses that
override only `task_type`; do not repeat the field definitions.

If the solution shape has no confirmed sample yet, leave `solution_type = None`
so the raw JSON is returned. **A guessed model is worse than no model** — it
tells callers a contract exists when it does not.

## Conventions

- **Docstrings in English.** They are the public API reference — what editors
  show on hover, what `help()` prints, and what a reader of the source sees.
  `ruff` enforces this: `RUF002` fails on non-ASCII characters in a docstring.
- **Inline `#` comments may be Chinese.** They explain non-obvious decisions and
  never reach the published documentation.
- Every public name needs a type annotation; `mypy --strict` must stay clean.
- Line length 100.
- Tests never touch the network — use the `respx_mock` fixture. Note that
  `@respx.mock` applied to a *class* silently prevents pytest from collecting
  its tests.

## Pull Requests

- Keep changes focused and atomic.
- Add or update tests when behaviour changes. Sync and async cases come in pairs.
- Update `README.md` **and** `README.zh-CN.md` if public API usage changes; the two
  are kept in sync.

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/). Release
notes are generated from the commit history by `git-cliff`, so the prefix
decides which section a change lands in:

```
feat: add the DataDome tags task type
fix: keep the raw solution on a decode failure
docs: document the two timeout budgets
```

Breaking changes take a `!` (`feat!:`) or a `BREAKING CHANGE:` footer.

## Releasing

1. Bump `version` in `pyproject.toml`.
2. Tag `vX.Y.Z` and push it.

The release workflow verifies that the tag matches the project version, builds
the distributions, checks that the wheel installs and reports the right version,
then publishes to PyPI through trusted publishing.

## Questions

Open an issue if you are unsure about API behaviour or compatibility. For a new
task type, a real request/response sample is worth far more than a description.
