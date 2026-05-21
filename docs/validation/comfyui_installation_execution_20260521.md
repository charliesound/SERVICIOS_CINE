# ComfyUI Installation Execution

**Date:** 2026-05-21 20:52:00
**Phase:** COMFYUI.1C real execution
**Script:** `scripts/dev/install_comfyui_missing_nodes_controlled.py --install`

## Scope

- Destination install instance: `:8188`
- Source instance for cross-copy: `:8189`
- Instances restarted after install: `:8188`, `:8191`
- Instances not modified: `:8189`, `:8190`, `:8192`
- External sources used: none
- Models touched: none

## Safety Notes

- `8188` uses `/home/harliesound/ai/ComfyUI_instances/ComfyUI-image/.venv-image`
- `8191` uses `.venv-restoration` as a symlink to the same image venv
- Any `pip install` executed for `:8188` also affected `:8191`
- This risk was accepted explicitly for COMFYUI.1C execution

## Backups Created

| Instance | Backup file | Size |
|----------|-------------|------|
| `:8188` | `OLD/comfyui_custom_nodes_backups/20260521/8188_image_custom_nodes_before.tar.gz` | 3397.1 MB |
| `:8189` | `OLD/comfyui_custom_nodes_backups/20260521/8189_video_cine_custom_nodes_before.tar.gz` | 2267.9 MB |
| `:8190` | `OLD/comfyui_custom_nodes_backups/20260521/8190_dubbing_audio_custom_nodes_before.tar.gz` | 2812.0 MB |
| `:8191` | `OLD/comfyui_custom_nodes_backups/20260521/8191_restoration_custom_nodes_before.tar.gz` | 3419.2 MB |
| `:8192` | `OLD/comfyui_custom_nodes_backups/20260521/8192_3d_custom_nodes_before.tar.gz` | 918.4 MB |

## Packages Copied To `:8188`

- `Comfyui_segformer_b2_clothes` from `:8189`
- `comfyui-fluxtrainer` from `:8189`

## Pip Packages Installed In `:8188`

- `ComfyUI-GGUF`
- `Comfyui_segformer_b2_clothes`
- `comfy-mtb`
- `comfyui-easy-use`
- `comfyui-fluxtrainer`
- `comfyui-impact-pack`
- `comfyui-videohelpersuite`
- `comfyui_controlnet_aux`
- `comfyui_instantid`
- `efficiency-nodes-comfyui`
- `rgthree-comfy`
- `was-node-suite-comfyui`

## API Validation

### `system_stats`

| Instance | Status |
|----------|--------|
| `:8188` | OK |
| `:8189` | OK |
| `:8190` | OK |
| `:8191` | OK |
| `:8192` | OK |

### `object_info` count diff

| Instance | Before | After | Delta |
|----------|--------|-------|-------|
| `:8188` | 3664 | 3698 | **+34** |
| `:8189` | 2576 | 2576 | 0 |
| `:8190` | 1915 | 1915 | 0 |
| `:8191` | 3654 | 3654 | 0 |
| `:8192` | 654 | 654 | 0 |

## Actual Nodes Added To `:8188` `object_info`

- `ExtractFluxLoRA`
- `FluxKohyaInferenceSampler`
- `FluxTrainAndValidateLoop`
- `FluxTrainBlockSelect`
- `FluxTrainEnd`
- `FluxTrainLoop`
- `FluxTrainModelSelect`
- `FluxTrainResume`
- `FluxTrainSave`
- `FluxTrainSaveModel`
- `FluxTrainValidate`
- `FluxTrainValidationSettings`
- `FluxTrainerLossConfig`
- `InitFluxLoRATraining`
- `InitFluxTraining`
- `InitSD3LoRATraining`
- `InitSDXLLoRATraining`
- `OptimizerConfig`
- `OptimizerConfigAdafactor`
- `OptimizerConfigProdigy`
- `OptimizerConfigProdigyPlusScheduleFree`
- `SD3ModelSelect`
- `SD3TrainValidationSettings`
- `SDXLModelSelect`
- `SDXLTrainValidate`
- `SDXLTrainValidationSettings`
- `TrainDatasetAdd`
- `TrainDatasetGeneralConfig`
- `TrainDatasetRegularization`
- `TrainNetworkConfig`
- `UploadToHuggingFace`
- `VisualizeLoss`
- `segformer_b2_clothes`
- `segformer_b3_fashion`

## Removed Nodes

- None detected in any instance

## What Was Really Installed

### New package directories on `:8188`

- `Comfyui_segformer_b2_clothes`
- `comfyui-fluxtrainer`

### New `object_info` nodes materialized on `:8188`

- 34 new node types were registered after restart
- The node gain came entirely from the copied `segformer` and `fluxtrainer` packages

### Planned nodes that did **not** materialize in `:8188`

- The bulk of pre-existing package-backed missing nodes from the dry-run plan did not add new `object_info` keys after the `pip install -r` refresh
- That means COMFYUI.1C successfully installed the two missing packages and refreshed shared dependencies, but it did not resolve every previously audited missing class type

## Incidents

1. `:8191` `object_info` required a much larger timeout than the other instances.
2. `:8191` startup log shows repeated `object_info` exceptions from existing restoration stack nodes:
   - `ComfyUI-RealESRGAN_Upscaler`: `ModuleNotFoundError: No module named 'basicsr.data.degradations'`
   - `zsq_prompt`: `TypeError: VAELoader.vae_list() missing 1 required positional argument: 's'`
   - `NunchakuDepthPreprocessor`: missing `/models/checkpoints` inside restoration instance path
3. These `:8191` errors pre-existed package copying scope and did not change the final node count, but they slow down `/object_info` significantly.
4. `:8188` restarted cleanly and exposed the expected `fluxtrainer` / `segformer` nodes.

## Result Summary

- Real execution succeeded for the approved COMFYUI.1C scope.
- All 5 backups were created successfully.
- Only `:8188` was modified as destination.
- No models were touched.
- No `custom_nodes` directories were deleted.
- No external clone source was used.
- `:8192` remained untouched.

## GO/NO-GO For COMFYUI.1D

**GO (with warnings)**

Rationale:

- COMFYUI.1C completed its approved installation scope successfully.
- `:8188` gained 34 new node types and now includes the missing `fluxtrainer` / `segformer` families.
- Residual issues are now clearly isolated for COMFYUI.1D:
  - remaining missing node classes in `:8188`
  - restoration-specific `object_info` exceptions on `:8191`
  - model-gap remediation, still out of scope for COMFYUI.1C
