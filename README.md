# pytest-no-retry

A pytest plugin that refuses to let your suite hide flakes behind retries.

```bash
pip install pytest-no-retry
```

Once installed, any of the following abort the test session before it
runs:

- `--reruns N` on the CLI
- `reruns = N` in `pytest.ini` / `pyproject.toml`
- `@pytest.mark.flaky(reruns=N)` on a test (works with both
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

A `--reruns=3` decorator is a one-line ROI: failing tests stop blocking
merges tomorrow. It's also how teams stop trusting their CI. A flaky
test is a test asserting on the wrong thing — the fix lives in the
assertion or in the wait, not in the runner.

This plugin makes that position **enforceable** in code review. Once
installed, "let's just add `@flaky` to unblock the release" becomes a
CI failure, not a Slack DM.

## opt-outs

Two intentional escape hatches:

**Per-test, with a reason:**

```python
@pytest.mark.flaky(reruns=2)
@pytest.mark.allow_retry("3rd-party rate-limited API, ticket QA-7421")
def test_payment_callback():
    ...
```

The reason string is **required**. A bare `@allow_retry` aborts the
session too — the design forces the author to name the trade-off.

**Soak tests** (deliberately repeated runs that report a rate, not
pass/fail):

```python
@pytest.mark.soak
@pytest.mark.flaky(reruns=100)
def test_soak_payment_flow_passes_99_percent():
    ...
```

**Whole session** (use sparingly, e.g. while investigating a real
flake):

```bash
pytest --allow-retry
```

## install

```bash
pip install pytest-no-retry
```

That's it. The plugin auto-registers via `pytest11` entry point.

## philosophy

Shipped alongside [ADR-006 — No retry-on-failure decorator](https://github.com/alexshabunin/qa-automation-portfolio/blob/main/docs/adr/0006-no-retry-on-failure.md)
in [qa-automation-portfolio](https://github.com/alexshabunin/qa-automation-portfolio).
The ADR argues the position; this plugin enforces it.

## license

MIT.
