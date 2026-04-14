# Changelog

All notable changes to the CronBark Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Pre-1.0 notice:** This SDK is currently in alpha (0.x). The public API may
> change in backwards-incompatible ways between minor versions until 1.0 is
> released.

## [Unreleased]

### Changed
- Renamed `api_key` parameter and `CRONBARK_API_KEY` env var to `token` and
  `CRONBARK_TOKEN` for terminology consistency with the backend (`api_tokens`
  table) and dashboard UI.

### Added
- Initial public preview of the CronBark Python SDK and `cronbark` CLI.
- `cronbark.configure()` for setting the API token, base URL, and request timeout.
- `cronbark.monitor()` context manager for automatic start/success/fail reporting.
- `cronbark.job()` decorator for instrumenting functions.
- Low-level helpers: `ping()`, `start()`, `success()`, `fail()`, `tick()`.
- CLI commands: `cronbark exec`, `cronbark ping`, `cronbark start`,
  `cronbark success`, `cronbark fail`, `cronbark tick`, `cronbark discover`.
- Default API base URL set to `https://api.cronbark.com` (override via
  `CRONBARK_URL` environment variable).

[Unreleased]: https://github.com/wookja-0/cronbark-sdk/compare/HEAD...HEAD
