# Contributing

Thanks for your interest. This is a small research-support package; issues and PRs are
welcome.

## Setup

```bash
pip install -e ".[dev]"
pre-commit install     # optional: runs ruff + black on changed files at commit time
```

## Before you push

Local checks must match CI (tool versions are pinned in `pyproject.toml`):

```bash
ruff check .
black --check .
mypy -p som_multimodal     # advisory
pytest -m "not slow" --cov
```

Add a note under `[Unreleased]` in `CHANGELOG.md` for anything user-facing.

## Scope of the style gates

`ruff`, `black`, and `mypy` are applied to the **original-authored** code
(`som_multimodal/*.py` and `tests/`) only. The vendored SOMPY
(`som_multimodal/_vendor/`) and the modified visualization engine
(`som_multimodal/engine/`) are **excluded**: they are upstream / upstream-derived code
kept close to their original form for fidelity and attribution. Please don't reformat
them wholesale; if you must change them, keep the change minimal and update the header
note + `NOTICE`/`ACKNOWLEDGMENTS.md` if attribution is affected.

## Tests

Tests live in `tests/`, run on CPU against tiny synthetic data, and should stay fast.
Mark anything that trains a full-size SOM on the real dataset with `@pytest.mark.slow`
so it is skipped in the default CI run.
