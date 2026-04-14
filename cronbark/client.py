"""
CronBark Python SDK 클라이언트.
HTTP API를 래핑하여 간편한 크론잡 모니터링을 제공한다.
"""

import functools
import os
import sys
import traceback
from contextlib import contextmanager
from typing import Any, Callable, Optional

import httpx

# ── 글로벌 설정 ────────────────────────────────────────────────

_config = {
    "token": os.environ.get("CRONBARK_TOKEN", ""),
    "base_url": os.environ.get("CRONBARK_URL", "https://api.cronbark.com"),
    "timeout": 10,
}


def configure(
    token: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: int = 10,
) -> None:
    """SDK 글로벌 설정을 변경한다."""
    if token is not None:
        _config["token"] = token
    if base_url is not None:
        _config["base_url"] = base_url
    _config["timeout"] = timeout


def _get_token(token: Optional[str] = None) -> str:
    """토큰을 결정한다 (직접 전달 > 환경변수 > 글로벌 설정)."""
    return token or _config["token"] or os.environ.get("CRONBARK_TOKEN", "")


def _api_url(token: str, endpoint: str) -> str:
    """API URL을 구성한다."""
    base = _config["base_url"].rstrip("/")
    return f"{base}/api/v1/health/{token}/{endpoint}"


def _send(token: str, endpoint: str, body: Optional[dict] = None) -> dict:
    """
    텔레메트리 이벤트를 전송한다.
    실패해도 예외를 발생시키지 않고 에러 dict를 반환한다.
    """
    url = _api_url(token, endpoint)
    try:
        with httpx.Client(timeout=_config["timeout"]) as client:
            if body:
                resp = client.post(url, json=body)
            else:
                resp = client.post(url)
            return resp.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── 공개 API ─────────────────────────────────────────────────


def ping(token: Optional[str] = None) -> dict:
    """간단 ping — start+success를 한 번에."""
    t = _get_token(token)
    base = _config["base_url"].rstrip("/")
    url = f"{base}/api/v1/ping/{t}"
    try:
        with httpx.Client(timeout=_config["timeout"]) as client:
            resp = client.get(url)
            return resp.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}


def start(token: Optional[str] = None) -> dict:
    """실행 시작을 알린다."""
    return _send(_get_token(token), "start")


def success(
    token: Optional[str] = None,
    output: Optional[str] = None,
    metrics: Optional[dict] = None,
) -> dict:
    """실행 성공을 알린다. output/metrics를 함께 전송할 수 있다."""
    body = {}
    if output:
        body["output"] = output
    if metrics:
        body["metrics"] = metrics
    return _send(_get_token(token), "success", body or None)


def fail(
    token: Optional[str] = None,
    error_message: Optional[str] = None,
    output: Optional[str] = None,
) -> dict:
    """실행 실패를 알린다."""
    body = {}
    if error_message:
        body["error_message"] = error_message
    if output:
        body["output"] = output
    return _send(_get_token(token), "fail", body or None)


def tick(token: Optional[str] = None) -> dict:
    """하트비트를 전송한다 (start 없이 즉시 성공)."""
    return _send(_get_token(token), "tick")


# ── 컨텍스트 매니저 & 데코레이터 ───────────────────────────────


@contextmanager
def monitor(token: Optional[str] = None):
    """
    컨텍스트 매니저 — with 블록 진입 시 start, 종료 시 success/fail 자동 전송.

    사용 예:
        with cronbark.monitor("YOUR_TOKEN"):
            run_backup()
    """
    t = _get_token(token)
    start(t)
    try:
        yield
        success(t)
    except Exception as e:
        # stdout/stderr 캡처
        tb = traceback.format_exc()
        fail(t, error_message=str(e), output=tb)
        raise


def job(token: Optional[str] = None) -> Callable:
    """
    데코레이터 — 함수 실행을 자동으로 모니터링한다.

    사용 예:
        @cronbark.job("YOUR_TOKEN")
        def generate_report():
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with monitor(token):
                return func(*args, **kwargs)

        return wrapper

    return decorator
