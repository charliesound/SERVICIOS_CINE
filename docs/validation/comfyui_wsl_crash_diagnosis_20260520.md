# ComfyUI WSL Crash Diagnosis — 2026-05-20

## Objective
Determine why WSL ComfyUI 8188 crashes during `still_storyboard_frame` rendering and why the Visual Bible smoke could not complete.

## Environment
- GPU: NVIDIA GeForce RTX 5090 (32GB VRAM)
- RAM: 54GB (46GB available at idle)
- Swap: 32GB (0 used)
- OS: WSL2 (Ubuntu)
- ComfyUI: v0.19.3 (port 8188, still/image instance)
- Python: 3.12.3, PyTorch 2.10.0+cu128
- Custom nodes: ~100 (including lora-manager, enhancement-utils, deploy, image-metadata-extension)

## Root Cause
**CASO C — custom node API incompatibility (TypeError)**

The execution wrapper chain in `comfyui-lora-manager/py/metadata_collector/metadata_hook.py` does NOT forward the new `ui_outputs` positional parameter added in ComfyUI v0.19.3.

### Error chain (from profile log):
```
execution.py:711 execute_async()
→ comfyui-deploy/custom_routes.py:1352 (swizzle_execute)
→ comfyui-enhancement-utils/profiler/hooks.py:171 (patched_execute)
→ comfyui_image_metadata_extension/modules/__init__.py (wraps execution)
→ comfyui-lora-manager/py/metadata_collector/metadata_hook.py:206
  → TypeError: execute() missing 1 required positional argument: 'ui_outputs'
```

### What happens:
1. CID submits a prompt via POST /prompt
2. ComfyUI accepts it (returns prompt_id) 
3. Execution starts but immediately crashes with TypeError
4. The job stays in queue_running forever (process alive, GPU idle)
5. CID scheduler retries until 3600s global timeout
6. Each retry hits the same TypeError

This is NOT an OOM, NOT a GPU crash, NOT a WSL process crash, NOT a Docker issue.

## Evidence
- **No OOM killer**: dmesg, syslog, journalctl show no OOM events
- **VRAM headroom**: 27GB free at idle, peak 12.6GB during render
- **GPU healthy**: 49°C idle, 45°C after render, 575W P1 state
- **Process alive**: State=S (sleeping), 54 threads, RSS 2.1GB, never killed
- **Queue stuck**: prompt stuck in queue_running for 235+ seconds (test 1)
- **Render succeeds after fix**: 101s, 8 steps, 1024x1024, valid 1.3MB PNG

## Fix Applied
Removed 4 conflicting custom nodes from `custom_nodes/`:

| Node | Reason | Backup Location |
|------|--------|-----------------|
| `comfyui-lora-manager` | metadata_hook.py:206 TypeError | `custom_nodes_BACKUP_CRASHFIX/` |
| `comfyui-enhancement-utils` | profiler hooks.py:171 in chain | same |
| `comfyui_image_metadata_extension` | modules/__init__.py wraps execute | same |
| `comfyui-deploy` | custom_routes.py:1352 swizzle_execute | same |

**Note**: Renaming to `.DISABLED` does NOT work — ComfyUI v0.19.3 loads ALL subdirectories.

## Result After Fix
- Basic SDXL render (8 steps, 1024x1024, Juggernaut-XL): **101 seconds, clean completion**
- VRAM peak: 12.6GB (well within 32GB limit)
- GPU utilization: 5+ it/s denoising
- No errors in log
- Other instances (8189-8192) unaffected

## Impact on CID Pipeline
The 4 removed nodes provide:
- **lora-manager**: LoRA loading/management (CID may use LoRAs in some workflows)
- **enhancement-utils**: image enhancement nodes
- **image-metadata-extension**: metadata injection for images
- **deploy**: workflow deployment/publishing

If CID's `still_storyboard_frame` workflow uses custom nodes from these packages, they will fail with "unknown node type" errors. However, the base render now works.

## CID Pipeline Smoke Validation (2026-05-20)

After the fix, the full CID pipeline was re-validated:

| Test | Result | Details |
|------|--------|---------|
| Basic SDXL render | ✅ | 8 steps, 1024x1024, Juggernaut-XL, 101s, valid 1.3MB PNG |
| CID storyboard smoke | ✅ | SINGLE_SCENE, preset=cinematic_realistic, ~35s render |
| Image asset creation | ✅ | `storyboard_aef10e1a_001_45b70a99_00001_.png` in `media_assets` |
| Visual Bible metadata | ✅ | `metadata_json.visual_bible.applied=true`, `visual_bible_id` presente |
| ComfyUI history | ✅ | 2 prompts ejecutados, node 7 output, no TypeError, no timeout |

**Confirmed**: No WSL/GPU/OOM issue remains. The fix (removing 4 custom nodes) resolves the crash completely.

## Recommendations
1. **Immediate**: Keep the 4 nodes removed from 8188's custom_nodes. The CID pipeline works for standard SDXL workflows — validated end-to-end.
2. **If LoRAs needed**: Re-enable `comfyui-lora-manager` by fixing `metadata_hook.py:206` to forward `ui_outputs` parameter.
3. **Permanent fix**: Update the metadata_hook in comfyui-lora-manager to be compatible with ComfyUI v0.19.3+'s execute() signature.
4. **Before re-enabling custom nodes**: Wait for upstream fix or patch metadata_hook.py manually. The 4 nodes remain safely backed up in `custom_nodes_BACKUP_CRASHFIX/`.
5. **Stable WSL startup**: Currently running via systemd + tmux. Instance 8188 was restarted manually with nohup. For production: use systemd user services or run_all script.

## ComfyUI Instance Notes
- **Installation**: `/home/harliesound/ai/ComfyUI_instances/ComfyUI-image/` (separate venv)
- **Models**: `/mnt/i/COMFYUI_OK/models/` (I: drive)
- **Output**: `/home/harliesound/ai/ComfyUI_instances/ComfyUI-image/output/`
- **Profile**: `/home/harliesound/ai/ComfyUI_profiles/image/user/`
- **Extra paths**: `/mnt/i/COMFYUI_OK/models/` mapped via extra_model_paths.yaml
- **Other instances**: 8189 (video, v0.14.1), 8190 (dubbing, v0.13.0), 8191 (restoration, v0.13.0), 8192 (3d, v0.17.0)
- **All share GPU**: cuda:0, no MIG configured

## Commands for Re-Enablement
```bash
# Restore disabled nodes
cd /home/harliesound/ai/ComfyUI_instances/ComfyUI-image
mv custom_nodes_BACKUP_CRASHFIX/comfyui-lora-manager.DISABLED custom_nodes/
mv custom_nodes_BACKUP_CRASHFIX/comfyui-enhancement-utils.DISABLED custom_nodes/
mv custom_nodes_BACKUP_CRASHFIX/comfyui_image_metadata_extension.DISABLED custom_nodes/
mv custom_nodes_BACKUP_CRASHFIX/comfyui-deploy.DISABLED custom_nodes/

# Restart
kill $(pgrep -f "port 8188")
# ... start via tmux or nohup
```
