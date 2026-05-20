"""Tests for the plugin itself."""
from __future__ import annotations

import textwrap

import pytest


pytest_plugins = ["pytester"]


def test_clean_session_runs_normally(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        """
        def test_ok():
            assert 1 + 1 == 2
        """
    )
    result = pytester.runpytest("-p", "pytest_no_retry.plugin")
    assert result.ret == 0


def test_reruns_cli_aborts_session(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        """
        def test_ok():
            assert True
        """
    )
    result = pytester.runpytest("-p", "pytest_no_retry.plugin", "--reruns=2")
    assert result.ret != 0
    # the plugin's banner is in stdout/stderr
    combined = "\n".join(result.outlines + result.errlines)
    assert "pytest-no-retry" in combined


def test_flaky_marker_with_reruns_aborts(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.flaky(reruns=3)
        def test_with_reruns():
            assert True
        """
    )
    result = pytester.runpytest("-p", "pytest_no_retry.plugin")
    assert result.ret != 0


def test_allow_retry_marker_with_reason_passes(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.flaky(reruns=2)
        @pytest.mark.allow_retry("3rd-party rate-limited API, ticket QA-7421")
        def test_with_explicit_opt_out():
            assert True
        """
    )
    result = pytester.runpytest("-p", "pytest_no_retry.plugin")
    assert result.ret == 0


def test_allow_retry_without_reason_aborts(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.flaky(reruns=2)
        @pytest.mark.allow_retry
        def test_lazy_opt_out():
            assert True
        """
    )
    result = pytester.runpytest("-p", "pytest_no_retry.plugin")
    assert result.ret != 0


def test_global_escape_hatch(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.flaky(reruns=2)
        def test_t():
            assert True
        """
    )
    result = pytester.runpytest("-p", "pytest_no_retry.plugin", "--allow-retry")
    assert result.ret == 0


def test_soak_marker_is_skipped(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.soak
        @pytest.mark.flaky(reruns=10)
        def test_soak_run():
            assert True
        """
    )
    result = pytester.runpytest("-p", "pytest_no_retry.plugin")
    assert result.ret == 0
