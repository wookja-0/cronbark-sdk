"""스모크 테스트 — 패키지 임포트 및 버전 확인."""

import cronbark


def test_import():
    """패키지가 정상적으로 임포트되는지 확인."""
    assert cronbark is not None


def test_version():
    """버전이 예상 값과 일치하는지 확인."""
    assert cronbark.__version__ == "0.0.1"


def test_public_api():
    """공개 API가 모두 export 되어 있는지 확인."""
    for name in ("configure", "monitor", "job", "ping", "start", "success", "fail", "tick"):
        assert hasattr(cronbark, name), f"cronbark.{name} 누락"
