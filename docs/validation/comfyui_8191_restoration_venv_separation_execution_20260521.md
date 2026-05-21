# 8191 Restoration Venv Separation Execution

**Date:** 2026-05-21 21:45:00
**Phase:** COMFYUI.1D.1 controlled apply
**Command:** `python3 -u scripts/dev/prepare_comfyui_8191_restoration_venv.py --apply`

## Scope

- Target instance: `:8191` restoration
- Action executed: separate `.venv-restoration` from `.venv-image`
- `:8188` touched: no
- `custom_nodes` requirements installed: no
- models modified: no
- `launch_instance_fixed.sh` modified: no
- instance restarted: no

## Result

- `.venv-restoration` is now a **real venv directory**
- It is **no longer a symlink** to `:8188`
- New venv path: `/home/harliesound/ai/ComfyUI_instances/ComfyUI-restoration/.venv-restoration`

## Backup Created

- Backup dir: `/opt/SERVICIOS_CINE/OLD/comfyui_venv_backups/20260521/8191_restoration_venv_20260521_214109`
- Symlink backup created: `venv_symlink_backup`
- Symlink backup target: `/home/harliesound/ai/ComfyUI_instances/ComfyUI-image/.venv-image`

## Pip Freeze Before/After

| Snapshot | Count |
|----------|------:|
| Before separation | 589 |
| After new empty venv create | 0 |
| After base `requirements.txt` install | 97 |

Artifacts:

- `pip_freeze_before.txt`
- `pip_freeze_after_venv_create.txt`
- `pip_freeze_after_base_requirements.txt`

## Required Post-Apply Validation

- `readlink -f .venv-restoration/bin/python` -> `/usr/bin/python3.12`
- `.venv-restoration/bin/python --version` -> `Python 3.12.3`
- `.venv-restoration/bin/python -m pip freeze | wc -l` -> `97`

## Base Requirements Installed

Confirmed installed in the new isolated venv:

- `comfyui_frontend_package==1.38.14`
- `torch==2.12.0`
- plus the rest of instance base requirements from `ComfyUI-restoration/requirements.txt`

Not installed in this phase:

- any `custom_nodes` `requirements.txt`
- any `nunchaku` wheel bootstrap
- any model download

## Incidents

1. No failure occurred during venv separation.
2. `:8191` process remained running from the pre-existing session, which is expected because this phase did not restart it.
3. `models/checkpoints` is still missing under restoration backing store (`/mnt/d/COMFYUI_OK/models`), unchanged.
4. Current launcher behavior remains risky for the next phase because it auto-installs:
   - base requirements
   - `custom_nodes` requirements
   - `nunchaku`

## Impact On 8188

- No changes were made to `/home/harliesound/ai/ComfyUI_instances/ComfyUI-image/.venv-image`
- No restart was performed on `:8188`
- The former sharing relationship was removed only from the `:8191` side

## GO/NO-GO For Safe Start Path Without Auto-Install

**GO**

Rationale:

- The venv isolation prerequisite is now complete.
- The next safe step is to prepare an alternative restoration start path that:
  - activates `.venv-restoration`
  - launches `main.py`
  - does **not** auto-run `custom_nodes` requirements installs
  - does **not** auto-install `nunchaku`

### Current launcher reuse for repair work

**NO-GO**

Rationale:

- `launch_instance_fixed.sh` is still non-deterministic for controlled repair because it installs dependencies automatically on restart.
