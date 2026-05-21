# ComfyUI Installation Plan Review

**Date:** 2026-05-21 20:18:37
**Source:** COMFYUI.1C controlled installation analysis

## Executive Summary

| Metric | Value |
|--------|-------|
| Total plan entries | 100 |
| UUIDs (parsing artifacts, skip) | 18 |
| Core nodes (already exist, skip) | 16 |
| Installable candidates | 66 |
| Unknown (needs research) | 0 |

## :8188 — image

### Candidates (66)

| Node | Package | Source | Pip? | Risk |
|------|---------|--------|------|------|
| `MarkdownNote` | rgthree-comfy | Dir exists (needs pip) | YES | high |
| `Geometry Sphere (mtb)` | comfy-mtb | Dir exists (needs pip) | YES | high |
| `UltimateSDUpscale` | comfyui-impact-pack | Dir exists (needs pip) | YES | high |
| `RandomNoise //Inspire` | comfyui-impact-pack | Dir exists (needs pip) | YES | high |
| `CheckpointLoaderNF4` | ComfyUI-GGUF | Dir exists (needs pip) | YES | high |
| `ApplyFluxControlNet` | ComfyUI_AdvancedRefluxControl | Dir exists | no | high |
| `InstantX Flux Union ControlNet Loader` | ComfyUI_AdvancedRefluxControl | Dir exists | no | high |
| `LoadFluxControlNet` | ComfyUI_AdvancedRefluxControl | Dir exists | no | high |
| `XlabsSampler` | ComfyUI_AdvancedRefluxControl | Dir exists | no | high |
| `LoadImageListFromDir //Inspire` | comfyui-impact-pack | Dir exists (needs pip) | YES | high |
| `LoadPromptsFromFile //Inspire` | comfyui-impact-pack | Dir exists (needs pip) | YES | high |
| `UnzipPrompt //Inspire` | comfyui-impact-pack | Dir exists (needs pip) | YES | high |
| `CatVTONWrapper` | ComfyUI-CatvtonFluxWrapper | Dir exists | no | high |
| `GroundingDinoModelLoader (segment anything)` | comfyui-impact-pack | Dir exists (needs pip) | YES | high |
| `GroundingDinoSAMSegment (segment anything)` | comfyui-impact-pack | Dir exists (needs pip) | YES | high |
| `BNK_Unsampler` | comfyui-impact-pack | Dir exists (needs pip) | YES | high |
| `Fast Groups Bypasser (rgthree)` | rgthree-comfy | Dir exists (needs pip) | YES | high |
| `GetNode` | efficiency-nodes-comfyui | Dir exists (needs pip) | YES | high |
| `SetNode` | efficiency-nodes-comfyui | Dir exists (needs pip) | YES | high |
| `InpaintResize` | comfyui-inpaint-nodes | Dir exists | no | high |
| `Load Styles CSV` | was-node-suite-comfyui | Dir exists (needs pip) | YES | high |
| `ApplyPulidFlux` | comfyui_ipadapter_plus | Dir exists | no | high |
| `PulidFluxEvaClipLoader` | comfyui_ipadapter_plus | Dir exists | no | high |
| `PulidFluxInsightFaceLoader` | comfyui_ipadapter_plus | Dir exists | no | high |
| `PulidFluxModelLoader` | comfyui_ipadapter_plus | Dir exists | no | high |
| `DiffusersCompelPromptEmbedding` | comfyui-impact-pack | Dir exists (needs pip) | YES | high |
| `DiffusersControlnetLoader` | comfyui-impact-pack | Dir exists (needs pip) | YES | high |
| `DiffusersControlnetUnit` | comfyui-impact-pack | Dir exists (needs pip) | YES | high |
| `DiffusersGenerator` | comfyui-impact-pack | Dir exists (needs pip) | YES | high |
| `DiffusersPipeline` | comfyui-impact-pack | Dir exists (needs pip) | YES | high |
| `DiffusersTextureInversionLoader` | comfyui-impact-pack | Dir exists (needs pip) | YES | high |
| `segformer_b2_clothes` | Comfyui_segformer_b2_clothes | From :8189 | no | medium |
| `VHS_FramesToVideoWAudio` | comfyui-videohelpersuite | Dir exists (needs pip) | YES | high |
| `VHS_VideoToFramesWAudio` | comfyui-videohelpersuite | Dir exists (needs pip) | YES | high |
| `MultiAreaConditioning` | comfyui-advanced-controlnet | Dir exists | no | high |
| `ImageSegmentationCustom` | was-node-suite-comfyui | Dir exists (needs pip) | YES | high |
| `FluxPromptGenerator` | comfyui-easy-use | Dir exists (needs pip) | YES | high |
| `FluxTrainEnd` | comfyui-fluxtrainer | From :8189 | no | high |
| `FluxTrainLoop` | comfyui-fluxtrainer | From :8189 | no | high |
| `FluxTrainModelSelect` | comfyui-fluxtrainer | From :8189 | no | high |
| `FluxTrainSave` | comfyui-fluxtrainer | From :8189 | no | high |
| `FluxTrainValidate` | comfyui-fluxtrainer | From :8189 | no | high |
| `FluxTrainValidationSettings` | comfyui-fluxtrainer | From :8189 | no | high |
| `InitFluxLoRATraining` | comfyui-fluxtrainer | From :8189 | no | high |
| `OptimizerConfig` | comfyui-fluxtrainer | From :8189 | no | high |
| `TrainDatasetAdd` | comfyui-fluxtrainer | From :8189 | no | high |
| `TrainDatasetGeneralConfig` | comfyui-fluxtrainer | From :8189 | no | high |
| `UploadToHuggingFace` | comfyui-fluxtrainer | From :8189 | no | high |
| `VisualizeLoss` | comfyui-fluxtrainer | From :8189 | no | high |
| `IPAdapterApply` | comfyui_ipadapter_plus | Dir exists | no | high |
| `rgthree.ImageSwitch` | rgthree-comfy | Dir exists (needs pip) | YES | high |
| `rgthree.Int` | rgthree-comfy | Dir exists (needs pip) | YES | high |
| `SAMModelLoader (segment anything)` | comfyui-segment-anything-2 | Dir exists | no | high |
| `FaceAnalysisModels` | comfyui_instantid | Dir exists (needs pip) | YES | high |
| `FaceEmbedDistance` | comfyui_instantid | Dir exists (needs pip) | YES | high |
| `Fast Bypasser (rgthree)` | rgthree-comfy | Dir exists (needs pip) | YES | high |
| `Label (rgthree)` | rgthree-comfy | Dir exists (needs pip) | YES | high |
| `Reroute (rgthree)` | rgthree-comfy | Dir exists (needs pip) | YES | high |
| `OpenPosePreprocessor` | comfyui_controlnet_aux | Dir exists (needs pip) | YES | high |
| `Searge_Output_Node` | comfyui-easy-use | Dir exists (needs pip) | YES | high |
| `ComfyUIStyler` | sdxl_prompt_styler | Dir exists | no | high |
| `LoraTagLoader` | comfyui-easy-use | Dir exists (needs pip) | YES | high |
| `PerturbedAttention` | comfyui-easy-use | Dir exists (needs pip) | YES | high |
| `smZ CLIPTextEncode` | comfyui-custom-scripts | Dir exists | no | high |
| `SamplerTCD EulerA` | comfyui-impact-pack | Dir exists (needs pip) | YES | high |
| `TCDScheduler` | comfyui-impact-pack | Dir exists (needs pip) | YES | high |

### Pip Dependencies

- ComfyUI-GGUF
- Comfyui_segformer_b2_clothes
- comfy-mtb
- comfyui-easy-use
- comfyui-fluxtrainer
- comfyui-impact-pack
- comfyui-videohelpersuite
- comfyui_controlnet_aux
- comfyui_instantid
- efficiency-nodes-comfyui
- rgthree-comfy
- was-node-suite-comfyui

### Exempt (Skipped)

- `Reroute`: Core ComfyUI node — may need version update or is missing from object_info
- `Text box`: Core ComfyUI node — may need version update or is missing from object_info
- `Note`: Core ComfyUI node — may need version update or is missing from object_info
- `e5cfe5ba-2ae0-4bc4-869f-ab2228cb44d3`: UUID (parsing artifact from API-format workflow)
- `2c61139d-9c34-4c7e-a083-7a67cc4770ad`: UUID (parsing artifact from API-format workflow)
- `fc11e656-d80a-42fa-ae56-c197af368516`: UUID (parsing artifact from API-format workflow)
- `SaveText`: Core ComfyUI node — may need version update or is missing from object_info
- `PrimitiveNode`: Core ComfyUI node — may need version update or is missing from object_info
- `Textbox`: Core ComfyUI node — may need version update or is missing from object_info
- `preview_mask`: Core ComfyUI node — may need version update or is missing from object_info
- `UpscaleImage`: Core ComfyUI node — may need version update or is missing from object_info
- `AspectSize`: Core ComfyUI node — may need version update or is missing from object_info
- `DF_Text_Box`: Core ComfyUI node — may need version update or is missing from object_info
- `DF_Get_image_size`: Core ComfyUI node — may need version update or is missing from object_info
- `Int Literal`: Core ComfyUI node — may need version update or is missing from object_info
- `String Literal`: Core ComfyUI node — may need version update or is missing from object_info
- `014000e7-58f1-44cf-b764-cf15d4559d2d`: UUID (parsing artifact from API-format workflow)
- `999e6c03-bebc-42af-ba36-6a6e2ccad87f`: UUID (parsing artifact from API-format workflow)
- `ef3b4b73-ce32-4a60-a60e-d7f278bf6b14`: UUID (parsing artifact from API-format workflow)
- `2a4b2cc0-db37-4302-a067-da392f38f06b`: UUID (parsing artifact from API-format workflow)
- `cade3e30-0eb2-4fd2-bf6e-8518f3a96e0c`: UUID (parsing artifact from API-format workflow)
- `f93c215e-c393-460e-9534-ed2c3d8a652e`: UUID (parsing artifact from API-format workflow)
- `workflow>Prompt/Model/Clip/Vae Loader`: Workflow UI keyword, not a node
- `0f47377a-2933-4dba-9791-a9c54b078226`: UUID (parsing artifact from API-format workflow)
- `b7908082-f5ff-497d-8e80-e4b0ffde0419`: UUID (parsing artifact from API-format workflow)
- `Seed Generator`: Core ComfyUI node — may need version update or is missing from object_info
- `workflow/GROUP`: Workflow UI keyword, not a node
- `07b8db07-5236-4589-9347-b3fd7b936d55`: UUID (parsing artifact from API-format workflow)
- `0867c4f0-1670-4efa-9195-cb61affe1c9e`: UUID (parsing artifact from API-format workflow)
- `55e214e1-4bed-4bda-8246-b83931369f04`: UUID (parsing artifact from API-format workflow)
- `5abd9f6f-0b12-4c44-a593-f974b3d732a5`: UUID (parsing artifact from API-format workflow)
- `809e2017-0ccb-4667-b9d8-19102e83c301`: UUID (parsing artifact from API-format workflow)
- `8a41ffb9-6ce7-4bec-80f5-c6ac49e87434`: UUID (parsing artifact from API-format workflow)
- `a8e409d9-c985-45b8-bcb2-935ac5ef7894`: UUID (parsing artifact from API-format workflow)

## :8189 — video_cine

### Candidates (0)

*No candidates for this instance*

## :8190 — dubbing_audio

### Candidates (0)

*No candidates for this instance*

## :8191 — restoration

### Candidates (0)

*No candidates for this instance*

## :8192 — 3d

### Candidates (0)

*No candidates for this instance*

## Cross-Instance Package Availability

| Package | 8188 | 8189 | 8190 | 8191 | 8192 | G: hub |
|---------|------|------|------|------|------|--------|
| ComfyUI-CatvtonFluxWrapper | YES | no | no | YES | no | no |
| ComfyUI-GGUF | YES | YES | YES | YES | no | no |
| ComfyUI_AdvancedRefluxControl | YES | no | no | YES | no | no |
| Comfyui_segformer_b2_clothes | no | YES | no | no | no | no |
| comfy-mtb | YES | no | no | YES | no | YES |
| comfyui-advanced-controlnet | YES | no | no | YES | no | no |
| comfyui-custom-scripts | YES | no | no | YES | no | no |
| comfyui-easy-use | YES | YES | no | YES | no | YES |
| comfyui-fluxtrainer | no | YES | no | no | no | no |
| comfyui-impact-pack | YES | YES | YES | YES | no | no |
| comfyui-inpaint-nodes | YES | no | no | YES | no | no |
| comfyui-segment-anything-2 | YES | YES | no | YES | no | no |
| comfyui-videohelpersuite | YES | YES | YES | YES | no | no |
| comfyui_controlnet_aux | YES | YES | no | YES | no | YES |
| comfyui_instantid | YES | no | no | YES | no | no |
| comfyui_ipadapter_plus | YES | YES | no | YES | no | no |
| efficiency-nodes-comfyui | YES | no | no | YES | no | YES |
| rgthree-comfy | YES | YES | YES | YES | no | YES |
| sdxl_prompt_styler | YES | no | no | YES | no | no |
| was-node-suite-comfyui | YES | YES | no | YES | no | no |

## Venv Isolation Assessment

- **Verdict:** WARNING
- **Shared venv:** True
- **Reason:** 8188 uses `/home/harliesound/ai/ComfyUI_instances/ComfyUI-image/.venv-image` and 8191 `.venv-restoration` is a symlink to it. Any pip install done for :8188 also affects :8191.

## GO/NO-GO Assessment

- **66 / 100** entries can be installed (66%)
- **18** UUID entries (skip)
- **16** core nodes (skip, version check needed)
- **0** unknown entries (manual research)
- **Venv risk:** WARNING — 8188 uses `/home/harliesound/ai/ComfyUI_instances/ComfyUI-image/.venv-image` and 8191 `.venv-restoration` is a symlink to it. Any pip install done for :8188 also affects :8191.

**GO (with warnings — shared venv accepted, pip install affects all instances)**
