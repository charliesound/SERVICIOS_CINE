#!/usr/bin/env python3

from pathlib import Path
import os
import stat
import sys


ROOT = Path('/opt/SERVICIOS_CINE')


def is_executable(path: Path) -> bool:
    return bool(path.stat().st_mode & stat.S_IXUSR)


def env_contains(path: Path, expected: str) -> bool:
    return expected in path.read_text(encoding='utf-8')


def main() -> int:
    checks: list[tuple[str, bool]] = []

    compose_base = ROOT / 'compose.base.yml'
    compose_home = ROOT / 'compose.home.yml'
    env_file = ROOT / '.env'
    start_script = ROOT / 'scripts' / 'start_home_demo.sh'
    stop_script = ROOT / 'scripts' / 'stop_home_demo.sh'
    health_script = ROOT / 'scripts' / 'check_home_demo_health.sh'
    bat_file = ROOT / 'arranque_ailinkcinema_cid_demo.bat'
    runbook = ROOT / 'docs' / 'deployment' / 'TAILSCALE_HOME_DEMO_RUNBOOK.md'
    firewall_doc = ROOT / 'docs' / 'deployment' / 'WINDOWS_FIREWALL_TAILSCALE_RULES.md'

    checks.append(('compose.base.yml exists', compose_base.exists()))
    checks.append(('compose.home.yml exists', compose_home.exists()))
    checks.append(('.env exists', env_file.exists()))

    if env_file.exists():
        checks.append(('.env has TAILSCALE_IP', env_contains(env_file, 'TAILSCALE_IP=100.121.83.126')))
        checks.append(('.env has PUBLIC_HOST', env_contains(env_file, 'PUBLIC_HOST=100.121.83.126')))
    else:
        checks.append(('.env has TAILSCALE_IP', False))
        checks.append(('.env has PUBLIC_HOST', False))

    for label, path in [
        ('start_home_demo.sh exists', start_script),
        ('stop_home_demo.sh exists', stop_script),
        ('check_home_demo_health.sh exists', health_script),
        ('arranque_ailinkcinema_cid_demo.bat exists', bat_file),
        ('TAILSCALE_HOME_DEMO_RUNBOOK.md exists', runbook),
        ('WINDOWS_FIREWALL_TAILSCALE_RULES.md exists', firewall_doc),
    ]:
        checks.append((label, path.exists()))

    for label, path in [
        ('start_home_demo.sh executable', start_script),
        ('stop_home_demo.sh executable', stop_script),
        ('check_home_demo_health.sh executable', health_script),
    ]:
        checks.append((label, path.exists() and is_executable(path)))

    forbidden_refs = ['docker-compose.local.yml', '.env.local']
    files_to_scan = [start_script, stop_script, health_script, bat_file]
    for ref in forbidden_refs:
        ref_ok = True
        for path in files_to_scan:
            if path.exists() and ref in path.read_text(encoding='utf-8'):
                ref_ok = False
                break
        checks.append((f'new scripts do not require {ref}', ref_ok))

    failed = False
    for label, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'} - {label}")
        if not ok:
            failed = True

    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
