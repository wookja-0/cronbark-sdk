"""
CronBark Python SDK
크론잡 모니터링을 위한 간편 연동 라이브러리.

사용 예:
    import cronbark

    # 환경변수 또는 직접 설정
    cronbark.configure(token="YOUR_TOKEN", base_url="https://api.cronbark.com")

    # 컨텍스트 매니저 — 자동 start/success/fail
    with cronbark.monitor("backup-daily"):
        run_backup()

    # 데코레이터
    @cronbark.job("report-gen")
    def generate_report():
        ...

    # 수동 호출
    cronbark.ping("YOUR_TOKEN")
    cronbark.start("YOUR_TOKEN")
    cronbark.success("YOUR_TOKEN", output="Done: 100 rows")
    cronbark.fail("YOUR_TOKEN", error_message="Connection refused")
    cronbark.tick("YOUR_TOKEN")
"""

from cronbark.client import (
    configure,
    fail,
    job,
    monitor,
    ping,
    start,
    success,
    tick,
)

__version__ = "0.0.1"

__all__ = [
    "configure",
    "monitor",
    "job",
    "ping",
    "start",
    "success",
    "fail",
    "tick",
]
