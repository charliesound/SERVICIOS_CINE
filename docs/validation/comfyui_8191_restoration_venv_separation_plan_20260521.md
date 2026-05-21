# 8191 Restoration Venv Separation Plan

**Date:** 2026-05-21 21:36:00
**Phase:** COMFYUI.1D.1 planning only
**Script:** `scripts/dev/prepare_comfyui_8191_restoration_venv.py`

## Executive Summary

- `:8191` **still shares Python environment with `:8188`**.
- Current path: `/home/harliesound/ai/ComfyUI_instances/ComfyUI-restoration/.venv-restoration`
- Current state: **symlink** to `/home/harliesound/ai/ComfyUI_instances/ComfyUI-image/.venv-image`
- Separation of the venv itself is **safe and recommended**.
- Restarting `:8191` with the current `launch_instance_fixed.sh` after separation is **not yet safe**, because the launcher auto-installs:
  - base `requirements.txt`
  - `custom_nodes` requirements
  - `nunchaku` wheel when detected

## Current State

| Item | Value |
|------|-------|
| Instance dir | `/home/harliesound/ai/ComfyUI_instances/ComfyUI-restoration` |
| `.venv-restoration` exists | `yes` |
| `.venv-restoration` is symlink | `yes` |
| Symlink target | `/home/harliesound/ai/ComfyUI_instances/ComfyUI-image/.venv-image` |
| Shares venv with `:8188` | `yes` |
| Python version in shared venv | `Python 3.12.3` |
| Current `pip freeze` package count | `589` |
| `requirements.txt` exists | `yes` |
| `requirements.txt` lines | `32` |
| `models` path | symlink to `/mnt/d/COMFYUI_OK/models` |
| `models/checkpoints` exists | `no` |
| `user` path | symlink to `/home/harliesound/ai/ComfyUI_profiles/restoration/user` |
| `custom_nodes` path | symlink to `/home/harliesound/ai/ComfyUI_profiles/restoration/custom_nodes` |

## Launch Script Review

File reviewed: `/home/harliesound/ai/ComfyUI_instances/ComfyUI-restoration/launch_instance_fixed.sh`

Confirmed behaviors:

1. Uses `VENV_DIR="${VENV_DIR:-$INSTANCE_DIR/.venv-$PROFILE}"`.
2. Installs base instance requirements automatically:
   - `python -m pip -q install -r "$INSTANCE_DIR/requirements.txt"`
3. Installs `custom_nodes` requirements automatically:
   - `find "$INSTANCE_DIR/custom_nodes" -maxdepth 2 -name requirements.txt`
4. Installs `nunchaku` automatically when `nunchaku_nodes` exists.

Implication:

- Creating a separate `:8191` venv is safe.
- Restarting `:8191` with the current launcher is a separate risk event and should be handled in a follow-up phase.

## Risks

1. **Shared venv risk today**
   - Any pip change in `:8188` still affects `:8191`.

2. **Launcher auto-install risk after separation**
   - Even with a new isolated venv, the current launcher would install all `custom_nodes` requirements on restart.
   - That would violate the current desire to repair `8191` incrementally.

3. **Restoration models path risk**
   - `:8191` points `models -> /mnt/d/COMFYUI_OK/models`
   - That backing store lacks `models/checkpoints`, which is already breaking `NunchakuDepthPreprocessor`.

4. **Plugin drift risk**
   - `zsq_prompt` is incompatible with current core `VAELoader.vae_list(s)` signature.
   - `ComfyUI-RealESRGAN_Upscaler` depends on a `basicsr/realesrgan` combination that is not currently healthy in the shared venv.

## Backup Plan

Planned backup root:

- `/opt/SERVICIOS_CINE/OLD/comfyui_venv_backups/20260521/8191_restoration_venv_<timestamp>/`

Planned backup artifacts:

1. `metadata.json`
2. `pip_freeze_before.txt`
3. `venv_symlink_backup` pointing back to `.venv-image` if current state is a symlink
4. `pip_freeze_after_venv_create.txt`
5. `pip_freeze_after_base_requirements.txt`

## Rollback Plan

If the current state remains a symlink, rollback is simple:

1. `rm -rf /home/harliesound/ai/ComfyUI_instances/ComfyUI-restoration/.venv-restoration`
2. `ln -s "/home/harliesound/ai/ComfyUI_instances/ComfyUI-image/.venv-image" /home/harliesound/ai/ComfyUI_instances/ComfyUI-restoration/.venv-restoration`

No `:8188` files need to be changed for rollback.

## Proposed Commands

Dry-run proposed these exact steps:

1. `mkdir -p /opt/SERVICIOS_CINE/OLD/comfyui_venv_backups/20260521/8191_restoration_venv_<timestamp>`
2. `python3 -m pip freeze > .../pip_freeze_before.txt` using current `.venv-restoration` python
3. `ln -s "/home/harliesound/ai/ComfyUI_instances/ComfyUI-image/.venv-image" .../venv_symlink_backup`
4. `rm /home/harliesound/ai/ComfyUI_instances/ComfyUI-restoration/.venv-restoration`
5. `/usr/bin/python3 -m venv /home/harliesound/ai/ComfyUI_instances/ComfyUI-restoration/.venv-restoration`
6. `/home/harliesound/ai/ComfyUI_instances/ComfyUI-restoration/.venv-restoration/bin/python3 --version`
7. `/home/harliesound/ai/ComfyUI_instances/ComfyUI-restoration/.venv-restoration/bin/python3 -m pip freeze > .../pip_freeze_after_venv_create.txt`
8. `/home/harliesound/ai/ComfyUI_instances/ComfyUI-restoration/.venv-restoration/bin/python3 -m pip install -r /home/harliesound/ai/ComfyUI_instances/ComfyUI-restoration/requirements.txt`
9. `/home/harliesound/ai/ComfyUI_instances/ComfyUI-restoration/.venv-restoration/bin/python3 -m pip freeze > .../pip_freeze_after_base_requirements.txt`

Important:

- This separation script does **not** restart `:8191`.
- This separation script does **not** install `custom_nodes` requirements.

## Dry-Run Result

Command executed:

- `python3 -u scripts/dev/prepare_comfyui_8191_restoration_venv.py --dry-run`

Observed result:

- `.venv-restoration` is confirmed as a symlink to `.venv-image`
- Shared package set size: `589`
- `models/checkpoints` missing in restoration model store
- Launcher auto-installs base requirements, `custom_nodes` requirements, and `nunchaku`
- Separation apply verdict from script: **GO with warnings**

## GO/NO-GO

### Apply venv separation only

**GO with warnings**

Reason:

- The apply step only detaches `:8191` from `:8188` and creates a new base venv.
- It does not modify `:8188`.
- It does not touch workflows, models, or `custom_nodes` contents.

### Restart `:8191` with current launcher after separation

**NO-GO**

Reason:

- The current launcher immediately installs `custom_nodes` requirements and `nunchaku` on restart.
- That makes post-separation repair non-deterministic.

## Recommended Next Step

1. Approve `--apply` for venv separation only.
2. In the next subphase, prepare a **safe restoration start path** that avoids automatic `custom_nodes` dependency installation.
3. Only then begin real repair of:
   - `ComfyUI-RealESRGAN_Upscaler`
   - `zsq_prompt`
   - `NunchakuDepthPreprocessor`

## ComfyUI-Copilot

- Recommendation remains **NO-GO**.
- Do not install or enable Copilot during the restoration repair track.
