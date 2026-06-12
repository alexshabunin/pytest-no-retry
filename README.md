# pytest-no-retry

[![ci](https://github.com/alexshabunin/pytest-no-retry/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/alexshabunin/pytest-no-retry/actions/workflows/ci.yml)
&nbsp;
[![python](https://img.shields.io/badge/python-3.10%2B-171717?style=flat-square&labelColor=171717)](https://github.com/alexshabunin/pytest-no-retry)
&nbsp;
[![license](https://img.shields.io/badge/license-MIT-171717?style=flat-square&labelColor=171717)](LICENSE)

Stops your pytest session if it's about to rerun failed tests.

```bash
pip install git+https://github.com/alexshabunin/pytest-no-retry
```

Aborts the session if it sees any of:

- `--reruns N` on the CLI
- `reruns = N` in `pytest.ini` / `pyproject.toml`
- `@pytest.mark.flaky(reruns=N)` on a test (covers both
  [pytest-rerunfailures](https://pypi.org/project/pytest-rerunfailures/)
  and the [flaky](https://pypi.org/project/flaky/) package)

```
$ pytest --reruns=3
  pytest-no-retry: this session asks for retry-on-failure.
  A flaky test is a test asserting on the wrong thing.
  Fix the assertion, not the runner.

  Offending source: --reruns=3 on the command line
```

## why

`--reruns=3` makes the red CI signal go away, but it doesn't fix
anything — the bug is still there, hidden behind a coin flip. After a
month nobody trusts the suite. This plugin makes "let's just slap
`@flaky`" a CI failure instead of a PR comment.

## opt-outs

Per-test, reason string required:

```python
@pytest.mark.flaky(reruns=2)
@pytest.mark.allow_retry("3rd-party rate-limited API, ticket QA-7421")
def test_payment_callback():
    ...
```

A bare `@allow_retry` without a reason fails too — by design.

Soak tests that intentionally repeat to measure a rate:

```python
@pytest.mark.soak
@pytest.mark.flaky(reruns=100)
def test_soak_payment_flow_passes_99_percent():
    ...
```

Whole session, for when you're actively debugging a flake:

```bash
pytest --allow-retry
```

## install

```bash
pip install git+https://github.com/alexshabunin/pytest-no-retry
```

Auto-registers via the `pytest11` entry point. (Not on PyPI yet — install
straight from the repo.)

## origin

Lives next to [qa-automation-portfolio](https://github.com/alexshabunin/qa-automation-portfolio)
where the same rule is written up as [ADR-006](https://github.com/alexshabunin/qa-automation-portfolio/blob/main/docs/adr/0006-no-retry-on-failure.md).

## license

MIT.
