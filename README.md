# CronBark Python SDK

Python SDK and CLI for [CronBark](https://cronbark.com) — monitor any cron job
with a single decorator.

> **Preview / Alpha.** This SDK is in preview and the CronBark SaaS service is
> launching soon. The public API may change in backwards-incompatible ways
> before the 1.0 release.

## Install

```bash
pip install cronbark
```

Requires **Python 3.9+**.

## Quickstart

Get an API token from your CronBark dashboard, then pick whichever style fits
your job best.

### 1. Context manager

Wrap any block of code — `start` is sent on entry, and `success` or `fail`
(with the traceback) is sent on exit.

```python
import cronbark

cronbark.configure(token="YOUR_TOKEN")

with cronbark.monitor():
    run_backup()
```

### 2. Decorator

Instrument an existing function in one line.

```python
import cronbark

@cronbark.job("YOUR_TOKEN")
def generate_report():
    ...
```

### 3. CLI — wrap any command

The easiest way to monitor an existing cron entry without touching its source:

```bash
cronbark exec --token YOUR_TOKEN "python backup.py"
```

Use it directly in `crontab`:

```crontab
# Before
0 * * * * /usr/bin/python3 /opt/scripts/backup.py

# After
0 * * * * cronbark exec --token YOUR_TOKEN "/usr/bin/python3 /opt/scripts/backup.py"
```

The CLI captures stdout/stderr, forwards them to CronBark, and exits with the
same status code as the wrapped command.

## Configuration

The SDK reads configuration from environment variables by default:

| Variable | Purpose | Default |
|----------|---------|---------|
| `CRONBARK_TOKEN` | Your job's API token | _(none — required)_ |
| `CRONBARK_URL` | API base URL override (self-hosted, staging, etc.) | `https://api.cronbark.com` |

You can also configure the SDK programmatically:

```python
import cronbark

cronbark.configure(
    token="YOUR_TOKEN",
    base_url="https://api.cronbark.com",  # optional
    timeout=10,                            # seconds, optional
)
```

## Public API

Top-level functions exported from the `cronbark` package:

| Symbol | Description |
|--------|-------------|
| `configure(token, base_url, timeout)` | Set global SDK configuration. |
| `monitor(token=None)` | Context manager — auto `start` / `success` / `fail`. |
| `job(token=None)` | Decorator wrapping a function with `monitor`. |
| `ping(token=None)` | One-shot `start + success`. |
| `start(token=None)` | Report execution start. |
| `success(token=None, output=None, metrics=None)` | Report success. |
| `fail(token=None, error_message=None, output=None)` | Report failure. |
| `tick(token=None)` | Heartbeat — report success without a prior `start`. |

CLI commands (`cronbark --help`):

```
cronbark exec --token TOKEN "<command>"   # wrap and run a command
cronbark ping TOKEN                     # one-shot start+success
cronbark start TOKEN
cronbark success TOKEN
cronbark fail TOKEN --msg "..."
cronbark tick TOKEN
cronbark discover                       # scan local crontab
```

All HTTP calls are best-effort: network errors are swallowed and returned as
`{"status": "error", "message": "..."}` so an unreachable monitoring service
will never break your job.

## Links

- Website: [cronbark.com](https://cronbark.com)
- Documentation: [cronbark.com/docs](https://cronbark.com/docs) _(coming soon)_
- Issues: [github.com/wookja-0/cronbark-sdk/issues](https://github.com/wookja-0/cronbark-sdk/issues)

## License

MIT — see [LICENSE](./LICENSE).
