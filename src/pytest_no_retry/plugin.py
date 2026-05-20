"""Refuse to run if anything in the test session is rerunning failed tests.

A flaky test is a test asserting on the wrong thing. The fix lives in the
assertion or in the wait, not in the runner. This plugin makes that
position enforceable: once installed, a CI run that depends on retries
fails at collection time with a message pointing at the offending marker
or option.

What it catches:
- pytest-rerunfailures: `--reruns N` (CLI), `reruns=N` in pytest.ini, or
  `@pytest.mark.flaky(reruns=N)` on a test.
- flaky (the package): `@pytest.mark.flaky` with `max_runs > 1`.

What it does not catch (by design):
- Soak tests that count failures across N iterations as a metric.
  Mark those `@pytest.mark.soak` and they're skipped.

Opt out for a specific test: `@pytest.mark.allow_retry("explain why")`.
The reason string is required and logged.
"""
from __future__ import annotations

import pytest


_BANNER = (
    "\n"
    "  pytest-no-retry: this session asks for retry-on-failure.\n"
    "  A flaky test is a test asserting on the wrong thing.\n"
    "  Fix the assertion, not the runner.\n"
    "\n"
    "  Offending source: {source}\n"
    "  See https://github.com/alexshabunin/pytest-no-retry for the policy.\n"
)


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("no-retry")
    group.addoption(
        "--allow-retry",
        action="store_true",
        default=False,
        help=(
            "Escape hatch. Allows reruns globally for this run. "
            "Use only when explicitly investigating a flake."
        ),
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "allow_retry(reason): permit retry-on-failure for this single test. "
        "Reason string is required.",
    )
    config.addinivalue_line(
        "markers",
        "soak: a deliberately repeated test that reports a rate, not pass/fail.",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--allow-retry"):
        return

    reruns_cli = config.getoption("--reruns", default=None)
    if reruns_cli not in (None, 0, "0"):
        _fail(config, f"--reruns={reruns_cli} on the command line")

    reruns_ini = config.getini("reruns") if "reruns" in config._parser._inicache else None
    if reruns_ini not in (None, "", 0, "0"):
        _fail(config, f"reruns={reruns_ini} in pytest.ini / pyproject.toml")

    for item in items:
        if item.get_closest_marker("allow_retry") is not None:
            marker = item.get_closest_marker("allow_retry")
            if not marker.args or not isinstance(marker.args[0], str):
                _fail(config, f"{item.nodeid}: @pytest.mark.allow_retry needs a reason string")
            continue
        if item.get_closest_marker("soak") is not None:
            continue

        flaky = item.get_closest_marker("flaky")
        if flaky is None:
            continue
        # pytest-rerunfailures uses reruns=, flaky package uses max_runs=
        reruns = flaky.kwargs.get("reruns")
        max_runs = flaky.kwargs.get("max_runs")
        if reruns not in (None, 0) or (max_runs is not None and int(max_runs) > 1):
            _fail(
                config,
                f"{item.nodeid}: @pytest.mark.flaky requests reruns",
            )


def _fail(config: pytest.Config, source: str) -> None:
    pytest.exit(_BANNER.format(source=source), returncode=2)
