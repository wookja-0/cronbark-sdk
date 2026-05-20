"""스모크 테스트 — 패키지 임포트 및 버전 확인."""

import cronbark


def test_import():
    """패키지가 정상적으로 임포트되는지 확인."""
    assert cronbark is not None


def test_version():
    """__version__ 이 설치된 패키지 메타데이터 버전과 일치하는지 확인.

    특정 숫자를 하드코딩하지 않으므로 릴리스마다 깨지지 않는다.
    동시에 __init__.py 의 __version__ 과 pyproject.toml 의 version 이
    어긋나면(둘 중 하나만 올리면) 실패하여 드리프트를 잡아준다.
    """
    from importlib.metadata import version

    assert cronbark.__version__ == version("cronbark")


def test_public_api():
    """공개 API가 모두 export 되어 있는지 확인."""
    for name in ("configure", "monitor", "job", "ping", "start", "success", "fail", "tick"):
        assert hasattr(cronbark, name), f"cronbark.{name} 누락"
