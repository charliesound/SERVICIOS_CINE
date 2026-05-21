#!/usr/bin/env python3
"""Prepare an isolated venv for ComfyUI restoration instance (:8191).

Default mode is dry-run. Use --apply to perform the separation.

Scope:
- Inspect current restoration instance wiring
- Backup current .venv-restoration symlink or venv
- Create an independent .venv-restoration if approved
- Install only base instance requirements.txt
- Do not install custom_nodes requirements
- Do not restart the instance
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path("/opt/SERVICIOS_CINE")
INSTANCE_DIR = Path("/home/harliesound/ai/ComfyUI_instances/ComfyUI-restoration")
IMAGE_INSTANCE_DIR = Path("/home/harliesound/ai/ComfyUI_instances/ComfyUI-image")
CURRENT_VENV = INSTANCE_DIR / ".venv-restoration"
IMAGE_VENV = IMAGE_INSTANCE_DIR / ".venv-image"
REQUIREMENTS = INSTANCE_DIR / "requirements.txt"
LAUNCH_SCRIPT = INSTANCE_DIR / "launch_instance_fixed.sh"
BACKUP_ROOT = ROOT / "OLD" / "comfyui_venv_backups" / "20260521"
SYSTEM_PYTHON = Path("/usr/bin/python3")


def log(message: str, level: str = "INFO") -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {message}", flush=True)


def run(cmd: list[str], timeout: int = 600) -> subprocess.CompletedProcess[str]:
    log("Running: " + " ".join(str(x) for x in cmd))
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def inspect_state() -> dict:
    launch_text = read_text(LAUNCH_SCRIPT)
    state = {
        "instance_dir": str(INSTANCE_DIR),
        "instance_dir_exists": INSTANCE_DIR.exists(),
        "current_venv": str(CURRENT_VENV),
        "venv_exists": CURRENT_VENV.exists(),
        "venv_is_symlink": CURRENT_VENV.is_symlink(),
        "venv_target": os.readlink(CURRENT_VENV) if CURRENT_VENV.is_symlink() else None,
        "venv_resolved": str(CURRENT_VENV.resolve()) if CURRENT_VENV.exists() else None,
        "image_venv": str(IMAGE_VENV),
        "image_venv_exists": IMAGE_VENV.exists(),
        "image_venv_resolved": str(IMAGE_VENV.resolve()) if IMAGE_VENV.exists() else None,
        "shares_with_8188": CURRENT_VENV.exists() and IMAGE_VENV.exists() and CURRENT_VENV.resolve() == IMAGE_VENV.resolve(),
        "requirements_exists": REQUIREMENTS.exists(),
        "requirements_line_count": len(read_text(REQUIREMENTS).splitlines()) if REQUIREMENTS.exists() else 0,
        "launch_script_exists": LAUNCH_SCRIPT.exists(),
        "launch_installs_base_requirements": "pip -q install -r \"$INSTANCE_DIR/requirements.txt\"" in launch_text,
        "launch_installs_custom_node_requirements": "find \"$INSTANCE_DIR/custom_nodes\" -maxdepth 2 -name requirements.txt" in launch_text,
        "launch_installs_nunchaku": "Installing nunchaku" in launch_text,
        "models_path_exists": (INSTANCE_DIR / "models").exists(),
        "models_is_symlink": (INSTANCE_DIR / "models").is_symlink(),
        "models_target": os.readlink(INSTANCE_DIR / "models") if (INSTANCE_DIR / "models").is_symlink() else None,
        "models_resolved": str((INSTANCE_DIR / "models").resolve()) if (INSTANCE_DIR / "models").exists() else None,
        "models_checkpoints_exists": (INSTANCE_DIR / "models" / "checkpoints").exists(),
        "user_path_exists": (INSTANCE_DIR / "user").exists(),
        "user_is_symlink": (INSTANCE_DIR / "user").is_symlink(),
        "user_target": os.readlink(INSTANCE_DIR / "user") if (INSTANCE_DIR / "user").is_symlink() else None,
        "user_resolved": str((INSTANCE_DIR / "user").resolve()) if (INSTANCE_DIR / "user").exists() else None,
        "custom_nodes_exists": (INSTANCE_DIR / "custom_nodes").exists(),
        "custom_nodes_is_symlink": (INSTANCE_DIR / "custom_nodes").is_symlink(),
        "custom_nodes_target": os.readlink(INSTANCE_DIR / "custom_nodes") if (INSTANCE_DIR / "custom_nodes").is_symlink() else None,
    }

    if CURRENT_VENV.exists() and (CURRENT_VENV / "bin" / "python3").exists():
        py = CURRENT_VENV / "bin" / "python3"
        ver = run([str(py), "--version"], timeout=60)
        freeze = run([str(py), "-m", "pip", "freeze"], timeout=120)
        state["python_version"] = (ver.stdout or ver.stderr).strip()
        state["pip_freeze_count"] = len([x for x in freeze.stdout.splitlines() if x.strip()]) if freeze.returncode == 0 else None
    else:
        state["python_version"] = None
        state["pip_freeze_count"] = None

    return state


def build_plan(state: dict) -> dict:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = BACKUP_ROOT / f"8191_restoration_venv_{ts}"
    backup_link = backup_dir / "venv_symlink_backup"
    backup_dir_copy = backup_dir / "venv_dir_backup"
    freeze_before = backup_dir / "pip_freeze_before.txt"
    freeze_after_create = backup_dir / "pip_freeze_after_venv_create.txt"
    freeze_after_base = backup_dir / "pip_freeze_after_base_requirements.txt"
    metadata_path = backup_dir / "metadata.json"

    commands = [
        f"mkdir -p {backup_dir}",
        f"python3 -m pip freeze > {freeze_before}  # using current .venv-restoration python",
    ]
    if state["venv_is_symlink"]:
        commands += [
            f"ln -s \"{state['venv_target']}\" {backup_link}",
            f"rm {CURRENT_VENV}",
        ]
    else:
        commands += [f"mv {CURRENT_VENV} {backup_dir_copy}"]
    commands += [
        f"{SYSTEM_PYTHON} -m venv {CURRENT_VENV}",
        f"{CURRENT_VENV / 'bin' / 'python3'} --version",
        f"{CURRENT_VENV / 'bin' / 'python3'} -m pip freeze > {freeze_after_create}",
        f"{CURRENT_VENV / 'bin' / 'python3'} -m pip install -r {REQUIREMENTS}",
        f"{CURRENT_VENV / 'bin' / 'python3'} -m pip freeze > {freeze_after_base}",
    ]

    risks = [
        "Current 8191 launcher auto-installs custom_nodes requirements and nunchaku on restart.",
        "Creating a separate venv is safe, but restarting with the current launcher will reintroduce uncontrolled dependency installation.",
        "8191 models path still lacks models/checkpoints in /mnt/d/COMFYUI_OK/models.",
        "No 8188 files should be modified during separation; only the 8191 symlink entry should change.",
    ]

    rollback = []
    if state["venv_is_symlink"]:
        rollback = [
            f"rm -rf {CURRENT_VENV}",
            f"ln -s \"{state['venv_target']}\" {CURRENT_VENV}",
        ]
    else:
        rollback = [
            f"rm -rf {CURRENT_VENV}",
            f"mv {backup_dir_copy} {CURRENT_VENV}",
        ]

    return {
        "timestamp": ts,
        "backup_dir": str(backup_dir),
        "metadata_path": str(metadata_path),
        "freeze_before": str(freeze_before),
        "freeze_after_create": str(freeze_after_create),
        "freeze_after_base": str(freeze_after_base),
        "commands": commands,
        "risks": risks,
        "rollback": rollback,
        "go_apply": state["shares_with_8188"] and state["requirements_exists"] and state["launch_script_exists"],
        "go_reason": "GO with warnings: venv separation itself is safe, but restart remains blocked by current launcher auto-install behavior.",
    }


def print_summary(state: dict, plan: dict, mode: str) -> None:
    log("=" * 70)
    log(f"8191 restoration venv separation — {mode}")
    log("=" * 70)
    log(f"Instance dir: {state['instance_dir']}")
    log(f"Current venv exists: {state['venv_exists']}")
    log(f"Current venv is symlink: {state['venv_is_symlink']}")
    log(f"Shares with 8188: {state['shares_with_8188']}")
    log(f"Current python version: {state['python_version']}")
    log(f"Current pip freeze count: {state['pip_freeze_count']}")
    log(f"Models path: {state['models_resolved']}")
    log(f"Models/checkpoints exists: {state['models_checkpoints_exists']}")
    log(f"User dir: {state['user_resolved']}")
    log(f"Launch installs base requirements: {state['launch_installs_base_requirements']}")
    log(f"Launch installs custom_nodes requirements: {state['launch_installs_custom_node_requirements']}")
    log(f"Launch installs nunchaku: {state['launch_installs_nunchaku']}")
    log(f"Backup dir: {plan['backup_dir']}")
    log(f"GO/NO-GO for apply: {'GO' if plan['go_apply'] else 'NO-GO'}")
    log(plan['go_reason'], "WARN" if plan['go_apply'] else "ERROR")
    log("Planned commands:")
    for cmd in plan["commands"]:
        log(f"  - {cmd}")
    log("Rollback plan:")
    for cmd in plan["rollback"]:
        log(f"  - {cmd}")
    log("Risks:")
    for risk in plan["risks"]:
        log(f"  - {risk}", "WARN")


def apply_plan(state: dict, plan: dict) -> int:
    backup_dir = Path(plan["backup_dir"])
    backup_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "state_before": state,
        "plan": plan,
        "applied_at": datetime.now().isoformat(),
    }
    Path(plan["metadata_path"]).write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    current_python = CURRENT_VENV / "bin" / "python3"
    if current_python.exists():
        freeze_before = run([str(current_python), "-m", "pip", "freeze"], timeout=180)
        Path(plan["freeze_before"]).write_text(freeze_before.stdout, encoding="utf-8")

    if CURRENT_VENV.is_symlink():
        os.symlink(os.readlink(CURRENT_VENV), backup_dir / "venv_symlink_backup")
        CURRENT_VENV.unlink()
    elif CURRENT_VENV.exists():
        shutil.move(str(CURRENT_VENV), str(backup_dir / "venv_dir_backup"))

    created = run([str(SYSTEM_PYTHON), "-m", "venv", str(CURRENT_VENV)], timeout=600)
    if created.returncode != 0:
        log(created.stderr[:800], "ERROR")
        return 1

    new_python = CURRENT_VENV / "bin" / "python3"
    ver = run([str(new_python), "--version"], timeout=60)
    if ver.returncode != 0:
        log(ver.stderr[:800], "ERROR")
        return 1

    freeze_after_create = run([str(new_python), "-m", "pip", "freeze"], timeout=180)
    Path(plan["freeze_after_create"]).write_text(freeze_after_create.stdout, encoding="utf-8")

    base_install = run([str(new_python), "-m", "pip", "install", "-r", str(REQUIREMENTS)], timeout=3600)
    if base_install.returncode != 0:
        log(base_install.stderr[:1200] or base_install.stdout[:1200], "ERROR")
        return 1

    freeze_after_base = run([str(new_python), "-m", "pip", "freeze"], timeout=180)
    Path(plan["freeze_after_base"]).write_text(freeze_after_base.stdout, encoding="utf-8")
    log("Apply completed. No restart was performed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare isolated 8191 restoration venv")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--apply", action="store_true", help="Apply the separation plan")
    group.add_argument("--dry-run", action="store_true", help="Preview only (default)")
    args = parser.parse_args()

    state = inspect_state()
    plan = build_plan(state)
    mode = "apply" if args.apply else "dry-run"
    print_summary(state, plan, mode)

    if not args.apply:
        return 0
    return apply_plan(state, plan)


if __name__ == "__main__":
    sys.exit(main())
