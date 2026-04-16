"""
CronBark CLI — 터미널에서 크론잡을 모니터링하는 명령줄 도구.

사용 예:
    # 명령어 감싸기 (자동 start → 실행 → success/fail)
    cronbark exec --token TOKEN "python backup.py"

    # 수동 이벤트 전송
    cronbark ping TOKEN
    cronbark start TOKEN
    cronbark success TOKEN
    cronbark fail TOKEN --msg "Connection refused"
    cronbark tick TOKEN

    # crontab 자동 스캔
    cronbark discover
"""

import os
import subprocess
import sys

import click

from cronbark.client import (
    USER_AGENT_CLI,
    _set_user_agent,
    configure,
    fail,
    ping,
    start,
    success,
    tick,
)


@click.group()
@click.option(
    "--url",
    envvar="CRONBARK_URL",
    default="https://api.cronbark.com",
    help="CronBark API URL (기본: https://api.cronbark.com)",
)
def main(url: str):
    """CronBark CLI - 크론잡 모니터링 도구"""
    configure(base_url=url)
    # 실행 이력에 "CLI" 배지로 분류되도록 User-Agent 를 CLI 전용으로 설정
    _set_user_agent(USER_AGENT_CLI)


@main.command(name="ping")
@click.argument("token")
def do_ping(token: str):
    """간단 ping (start + success 한 번에)"""
    result = ping(token)
    click.echo(f"[cronbark] {result.get('status', 'error')}: {result.get('message', '')}")


@main.command(name="start")
@click.argument("token")
def do_start(token: str):
    """실행 시작 알림"""
    result = start(token)
    click.echo(f"[cronbark] {result.get('status', 'error')}: {result.get('message', '')}")


@main.command(name="success")
@click.argument("token")
def do_success(token: str):
    """실행 성공 알림"""
    result = success(token)
    click.echo(f"[cronbark] {result.get('status', 'error')}: {result.get('message', '')}")


@main.command(name="fail")
@click.argument("token")
@click.option("--msg", default=None, help="에러 메시지")
def do_fail(token: str, msg: str):
    """실행 실패 알림"""
    result = fail(token, error_message=msg)
    click.echo(f"[cronbark] {result.get('status', 'error')}: {result.get('message', '')}")


@main.command(name="tick")
@click.argument("token")
def do_tick(token: str):
    """하트비트 전송"""
    result = tick(token)
    click.echo(f"[cronbark] {result.get('status', 'error')}: {result.get('message', '')}")


@main.command(name="exec")
@click.option("--token", envvar="CRONBARK_TOKEN", required=True, help="API 토큰")
@click.argument("command", nargs=-1, required=True)
def do_exec(token: str, command: tuple):
    """
    명령어를 실행하고 결과를 자동 보고한다.

    사용: cronbark exec --token TOKEN "python backup.py"
    """
    cmd_str = " ".join(command)
    click.echo(f"[cronbark] 실행: {cmd_str}")

    # start 전송
    start(token)

    try:
        # 명령어 실행
        result = subprocess.run(
            cmd_str,
            shell=True,
            capture_output=True,
            text=True,
        )

        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += "\n--- STDERR ---\n" + result.stderr

        if result.returncode == 0:
            # 성공
            resp = success(token, output=output[:1_000_000] if output else None)
            click.echo(f"[cronbark] 성공 (exit code 0)")
        else:
            # 실패
            error_msg = f"Exit code {result.returncode}"
            if result.stderr:
                error_msg += f": {result.stderr[:500]}"
            resp = fail(token, error_message=error_msg, output=output[:1_000_000] if output else None)
            click.echo(f"[cronbark] 실패 (exit code {result.returncode})")

        sys.exit(result.returncode)

    except Exception as e:
        fail(token, error_message=str(e))
        click.echo(f"[cronbark] 에러: {e}")
        sys.exit(1)


@main.command()
def discover():
    """
    시스템의 crontab을 스캔하여 등록 가능한 크론잡 목록을 표시한다.
    """
    click.echo("[cronbark] crontab 스캔 중...")

    try:
        # 현재 사용자의 crontab 조회
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            click.echo("[cronbark] crontab이 비어있거나 접근할 수 없습니다.")
            return

        lines = result.stdout.strip().split("\n")
        jobs = []
        for line in lines:
            line = line.strip()
            # 주석과 빈 줄 건너뛰기
            if not line or line.startswith("#"):
                continue
            # 환경변수 설정 건너뛰기
            if "=" in line.split()[0]:
                continue
            jobs.append(line)

        if not jobs:
            click.echo("[cronbark] 등록된 crontab 작업이 없습니다.")
            return

        click.echo(f"\n발견된 크론잡 {len(jobs)}개:\n")
        click.echo(f"{'#':<4} {'스케줄':<20} {'명령어'}")
        click.echo("-" * 70)
        for i, job_line in enumerate(jobs, 1):
            parts = job_line.split(None, 5)
            if len(parts) >= 6:
                schedule = " ".join(parts[:5])
                command = parts[5]
            else:
                schedule = "파싱 불가"
                command = job_line
            click.echo(f"{i:<4} {schedule:<20} {command}")

        click.echo(f"\n[cronbark] 위 크론잡을 CronBark에 등록하려면 각 crontab 명령어를 다음처럼 감싸세요:")
        click.echo('  cronbark exec --token YOUR_TOKEN "명령어"')

    except FileNotFoundError:
        click.echo("[cronbark] crontab 명령어를 찾을 수 없습니다. (Windows에서는 지원되지 않습니다)")
    except Exception as e:
        click.echo(f"[cronbark] 스캔 에러: {e}")
