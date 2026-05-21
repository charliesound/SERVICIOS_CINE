# ComfyUI Post-Install Validation

**Date:** 2026-05-21 21:20:00
**Phase:** COMFYUI.1D audit-only post-install validation

## Executive Summary

- `8188` remains **GO** after COMFYUI.1C and now exposes **3698** node types (`+34`).
- Workflow diagnostics changed from **GO/WARNING/NO-GO = 113/239/89** to **113/241/87**.
- Real reduction: **NO-GO -2** and **WARNING +2** with **0** workflows promoted to GO.
- The only workflows that improved were the two copies of `flux_lora_train_Capitulo14.json`, both moving from `NO-GO` to `WARNING`.
- `8191` still answers `/system_stats` and `/object_info`, but `/object_info` is slow and noisy due to three pre-existing broken custom-node paths.
- Missing models remain **482**, with critical concentration in storyboard/image and video/cine flows.
- Recommendation: **do not install ComfyUI-Copilot yet**.

## Instance Changes

| Instance | Before object_info | After object_info | Delta | Current audit diag |
|----------|--------------------|-------------------|-------|--------------------|
| `:8188` | 3664 | 3698 | +34 | GO |
| `:8189` | 2576 | 2576 | +0 | WARNING |
| `:8190` | 1915 | 1915 | +0 | WARNING |
| `:8191` | 3654 | 3654 | +0 | WARNING |
| `:8192` | 654 | 654 | +0 | NO-GO |

## New Nodes Detected In `:8188`

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

## Workflow Diagnostic Change

- Before: `GO 113` / `WARNING 239` / `NO-GO 89`
- After: `GO 113` / `WARNING 241` / `NO-GO 87`
- Transitions: `NO-GO -> WARNING = 2`; no regressions detected.

### Workflows That Improved

- `flux_lora_train_Capitulo14.json`
  Path: `/mnt/g/COMFYUI_HUB/workflows/00_IMAGEN_fija/flux_lora_train_Capitulo14.json`
  Change: `NO-GO -> WARNING` (`15 -> 3` missing nodes)
  Newly satisfied in `:8188`: `FluxTrainEnd, FluxTrainLoop, FluxTrainModelSelect, FluxTrainSave, FluxTrainValidate, FluxTrainValidationSettings, InitFluxLoRATraining, OptimizerConfig, TrainDatasetAdd, TrainDatasetGeneralConfig, UploadToHuggingFace, VisualizeLoss`
- `flux_lora_train_Capitulo14.json`
  Path: `/mnt/g/COMFYUI_HUB/workflows/Workflow confyui/flux_lora_train_Capitulo14/flux_lora_train_Capitulo14.json`
  Change: `NO-GO -> WARNING` (`15 -> 3` missing nodes)
  Newly satisfied in `:8188`: `FluxTrainEnd, FluxTrainLoop, FluxTrainModelSelect, FluxTrainSave, FluxTrainValidate, FluxTrainValidationSettings, InitFluxLoRATraining, OptimizerConfig, TrainDatasetAdd, TrainDatasetGeneralConfig, UploadToHuggingFace, VisualizeLoss`

### Workflows Still NO-GO

- Count: **87**
- `VIDEO 13 WF.json`: best `:8189`, missing `31` (`ACN_AdvancedControlNetApply, ACN_AdvancedControlNetApply_v2, BatchPromptSchedule, ControlNetLoaderAdvanced, CreateFadeMaskAdvanced, DownloadAndLoadPyramidFlowModel, Fast Bypasser (rgthree), Fast Groups Muter (rgthree), GetImageSizeAndCount, GetNode`)
- `Lonecats ZIT All in one Ver 6.0.json`: best `:8191`, missing `28` (`Bookmark (rgthree), DF_Int_to_Float, DF_Text, ExpressionEditor, Fast Bypasser (rgthree), Fast Groups Bypasser (rgthree), Fast Groups Muter (rgthree), Fast Muter (rgthree), Film Grain, GetNode`)
- `COMPACT Flux Control-Net inpainting with batch.json`: best `:8191`, missing `26` (`ApplyFBCacheOnModel, Civitai Hash Fetcher (Image Saver), CyberEve_BatchImageLoopClose, CyberEve_BatchImageLoopOpen, CyberEve_LoopIndexSwitch, CyberEve_MaskMerge, CyberEve_MaskSegmentation, Fast Bypasser (rgthree), Fast Groups Bypasser (rgthree), Fast Groups Muter (rgthree)`)
- `_4x4 (5).json`: best `:8189`, missing `19` (`00093772-bf7d-47a3-8c4c-c29965d31336, 0d267b71-f69c-4715-b24d-77983a47db38, 30ef1e74-19ac-44b5-b6d9-872acdf0c6e1, 36d62718-4b8d-47b5-826c-1ab28b0c1457, 37eb9014-2859-4cb4-94e3-1c0dd0717f0e, 3a6c1476-6f05-42ca-b5b2-913140988506, 40e3faf7-eef2-4977-916c-9f47d4903f38, 50d1e076-f024-4de9-9193-ec81e321e1dc, 5ab36065-da85-4170-856a-d66e8af6b42d, 646e06d4-ef7d-4e2d-9266-3f03de5d7f0b`)
- `workflow-wan22-14b-image-video-hd-version-XC06OMwupt9qC7euN61H-north_ai-openart.ai.json`: best `:8189`, missing `17` (`Bjornulf_ShowInt, CR Text Concatenate, Fast Groups Muter (rgthree), ImageResizeKJv2, JWInteger, JjkShowText, JjkText, MathExpression|pysssss, Note, PrimitiveNode`)
- `steerable-motion_smooth-n-steady.json`: best `:8188`, missing `16` (`ADE_AnimateDiffLoRALoader, ADE_AnimateDiffUniformContextOptions, ADE_ApplyAnimateDiffModel, ADE_EmptyLatentImageLarge, ADE_LoadAnimateDiffModel, ADE_MultivalDynamic, ADE_UseEvolvedSampling, BatchCreativeInterpolation, BatchValueScheduleLatentInput, FILM VFI`)
- `Roda-ReactiveVideo-CSGB-smooth-V82.json`: best `:8188`, missing `14` (`AudioFeatureExtractor, AudioSeparator, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio, FeatureSmoothing, FlexImageBloom, FlexImageChromaticAberration, FlexImageGlitch, FlexVideoSpeed, Note`)
- `Roda-ReactiveVideo-CSGB-smooth-V82.json`: best `:8188`, missing `14` (`AudioFeatureExtractor, AudioSeparator, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio, FeatureSmoothing, FlexImageBloom, FlexImageChromaticAberration, FlexImageGlitch, FlexVideoSpeed, Note`)
- `workflow-free-digital-human-bcculjSnGEcDuGhoNhkd-discus_disastrous_37-openart.ai.json`: best `:8188`, missing `14` (`Apply Whisper, ChatTTS_, GetNode, LoadWhisperModel, Note, OpenVoiceClone, Qwen2_ModelLoader_Zho, Qwen2_Zho, SetNode, String Literal`)
- `workflow-simple-prompt-travel-animations.json`: best `:8188`, missing `14` (`ADE_AnimateDiffSamplingSettings, ADE_ApplyAnimateDiffModelSimple, ADE_LoadAnimateDiffModel, ADE_StandardUniformContextOptions, ADE_UseEvolvedSampling, BatchPromptSchedule, FILM VFI, Fast Groups Bypasser (rgthree), GetKeyFrames, ImageSelector`)
- `workflow-wan22-animate-swap-anythingauto-seg-Jk5WFuRDcpXWIlMLk7Ds-faborohacks-openart.ai.json`: best `:8190`, missing `14` (`DWPreprocessor, Fast Groups Muter (rgthree), GetNode, LayerMask: LoadSegmentAnythingModels, LayerMask: SegmentAnythingUltra V3, LayerUtility: GeminiV2, Note, PixelPerfectResolution, RH_Captioner, Reroute`)
- `workflow-wan2_2-video-clothes-try-onfun-vace-version-cpBoTySGoyLPwSZ9HCzj-faborohacks-openart.ai.json`: best `:8189`, missing `14` (`CR Text, GetNode, GrowMaskWithBlur, ImageConcanate, ImageScaleToMegapixels, LayerMask: SegformerB2ClothesUltra, LayerUtility: GeminiV2, LayerUtility: ImageScaleByAspectRatio V2, Note, PrimitiveNode`)
- `Roda-ReactiveVideo-CSGB-V80.json`: best `:8188`, missing `13` (`AudioFeatureExtractor, AudioSeparator, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio, FlexImageBloom, FlexImageChromaticAberration, FlexImageGlitch, FlexVideoSpeed, Note, PrimitiveNode`)
- `Roda-ReactiveVideo-CSGB-V80.json`: best `:8188`, missing `13` (`AudioFeatureExtractor, AudioSeparator, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio, FlexImageBloom, FlexImageChromaticAberration, FlexImageGlitch, FlexVideoSpeed, Note, PrimitiveNode`)
- `workflow-flux-2-klein-inpaint-segment-edit-for-accurate-image-edit-vo9umAlx9kjGRaijxRmP-cgpixel_ai_art-openart.ai.json`: best `:8188`, missing `13` (`07b8db07-5236-4589-9347-b3fd7b936d55, 0867c4f0-1670-4efa-9195-cb61affe1c9e, 55e214e1-4bed-4bda-8246-b83931369f04, 5abd9f6f-0b12-4c44-a593-f974b3d732a5, 809e2017-0ccb-4667-b9d8-19102e83c301, 8a41ffb9-6ce7-4bec-80f5-c6ac49e87434, Fast Groups Bypasser (rgthree), Label (rgthree), MarkdownNote, Note`)
- `workflow-flux-your-ootd-flux-D6q01xaUd0AOf6A9OQym-jaylin-openart.ai.json`: best `:8188`, missing `13` (`Fast Groups Bypasser (rgthree), GetNode, Int, Multi Text Merge, Note, PortraitMaster, RH_Captioner, Reroute, SDXLRecommendedImageSize, SetNode`)
- `SVI 2.0 PRO WORKFLOW.json`: best `:8188`, missing `12` (`00a07f4d-d12a-4255-a63e-f17cbc13dbd3, 024ffd1a-eb57-4930-96b0-f61b1125e911, 1b165832-48d7-439f-8635-a156c338ac6d, 24fa26a4-166e-4f16-aa41-fdf04f07700f, 31d4829e-74b4-48a0-a610-1708e106b780, GetNode, Reroute, SetNode, ad67aa55-e34c-423c-b725-113c73a2c39f, c5a95b71-2875-4c1e-930a-368bc51e3aa7`)
- `PH_FLUXTOOLS_2_COG_v052.json`: best `:8189`, missing `11` (`Compare-🔬, Fast Groups Bypasser (rgthree), Float-🔬, GrowMaskWithBlur, INTConstant, If ANY return A else B-🔬, ImageResizeKJ, Int-🔬, Label (rgthree), Note Plus (mtb)`)
- `Roda-ReactScrub-GIMMSync-V30.json`: best `:8188`, missing `11` (`AudioFeatureExtractor, AudioSeparator, DownloadAndLoadGIMMVFIModel, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio, FlexVideoDirection, GIMMVFI_interpolate, Note, PrimitiveNode, ProjectFilePathNode`)
- `Roda-ReactScrub-GIMMSync-V30.json`: best `:8188`, missing `11` (`AudioFeatureExtractor, AudioSeparator, DownloadAndLoadGIMMVFIModel, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio, FlexVideoDirection, GIMMVFI_interpolate, Note, PrimitiveNode, ProjectFilePathNode`)
- `Roda-ReactiveVideo-CSG-V78.json`: best `:8188`, missing `11` (`AudioFeatureExtractor, AudioSeparator, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio, FlexImageChromaticAberration, FlexImageGlitch, FlexVideoSpeed, Note, PrimitiveNode, ProjectFilePathNode`)
- `Roda-ReactiveVideo-CSG-V78.json`: best `:8188`, missing `11` (`AudioFeatureExtractor, AudioSeparator, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio, FlexImageChromaticAberration, FlexImageGlitch, FlexVideoSpeed, Note, PrimitiveNode, ProjectFilePathNode`)
- `liveportrait_image_example_01.json`: best `:8188`, missing `11` (`DownloadAndLoadLivePortraitModels, LivePortraitComposite, LivePortraitCropper, LivePortraitLoadCropper, LivePortraitLoadFaceAlignmentCropper, LivePortraitLoadMediaPipeCropper, LivePortraitProcess, LivePortraitRetargeting, Note, PrimitiveNode`)
- `workflow-perfect-lip-sync-ai-face-animation-jEIRkxkIGvuC6Nwm69Uz-comfyuiblog-openart.ai.json`: best `:8189`, missing `11` (`CreateShapeMask, DownloadAndLoadLivePortraitModels, GrowMaskWithBlur, LivePortraitComposite, LivePortraitCropper, LivePortraitLoadMediaPipeCropper, LivePortraitProcess, LivePortraitRetargeting, Note, ReActorFaceSwap`)
- `Animar_imagenes_audio_OK.json`: best `:8188`, missing `10` (`ADE_ApplyAnimateDiffModelSimple, ADE_LoadAnimateDiffModel, ADE_LoopedUniformContextOptions, ADE_MultivalDynamic, ADE_UseEvolvedSampling, Audio Analysis, Audio IPAdapter Transitions, Audio Peaks Detection, Load Audio Separation Model, Repeat Image To Count`)

## Remaining Missing Nodes

- Unique missing node names across best-instance evaluations: **458**

| Missing node | Affected workflows |
|--------------|-------------------:|
| `Note` | 120 |
| `MarkdownNote` | 81 |
| `PrimitiveNode` | 68 |
| `Reroute` | 63 |
| `SetNode` | 36 |
| `GetNode` | 35 |
| `Fast Groups Bypasser (rgthree)` | 28 |
| `Seed Generator` | 24 |
| `AudioFeatureExtractor` | 22 |
| `ProjectFilePathNode` | 22 |
| `AudioSeparator` | 20 |
| `DownloadOpenUnmixModel` | 20 |
| `EmptyImageAndMaskFromAudio` | 20 |
| `Label (rgthree)` | 18 |
| `IPAdapterApply` | 11 |
| `FlexImageChromaticAberration` | 10 |
| `UltimateSDUpscale` | 8 |
| `ControlNetLoaderAdvanced` | 8 |
| `FlexImageGlitch` | 8 |
| `FlexVideoSpeed` | 8 |
| `RIFE VFI` | 7 |
| `GroundingDinoModelLoader (segment anything)` | 6 |
| `GroundingDinoSAMSegment (segment anything)` | 6 |
| `Textbox` | 6 |
| `ApplyPulidFlux` | 6 |
| `PulidFluxEvaClipLoader` | 6 |
| `PulidFluxInsightFaceLoader` | 6 |
| `PulidFluxModelLoader` | 6 |
| `ApplyControlNet` | 6 |
| `HED_Preprocessor` | 6 |
| `FlexImageBloom` | 6 |
| `Load Styles CSV` | 5 |
| `Fast Bypasser (rgthree)` | 5 |
| `DepthAnything_Preprocessor` | 5 |
| `NormalBAE_Preprocessor` | 5 |
| `BatchPromptSchedule` | 5 |
| `Fast Groups Muter (rgthree)` | 5 |
| `easy cleanGpuUsed` | 5 |
| `ImageResize` | 5 |
| `Text box` | 4 |
| `Int` | 4 |
| `GridImage` | 4 |
| `KSamplerSetting` | 4 |
| `KSamplerXYZ` | 4 |
| `StateDictLoader` | 4 |
| `VAEDecodeBatched` | 4 |
| `D_LatentSyncNode` | 4 |
| `ACN_AdvancedControlNetApply` | 4 |
| `DownloadAndLoadLivePortraitModels` | 4 |
| `LivePortraitCropper` | 4 |
| `LivePortraitLoadMediaPipeCropper` | 4 |
| `LivePortraitProcess` | 4 |
| `FlexVideoDirection` | 4 |
| `CannyEdge_Preprocessor` | 4 |
| `Lineart_Preprocessor` | 4 |
| `OpenPose_Preprocessor` | 4 |
| `T2IAdapterApply` | 4 |
| `T2IAdapterModelLoader` | 4 |
| `FluxKSampler` | 4 |
| `LUTApply` | 4 |

## Missing Models Prioritized

- Total missing model references: **482**

| Bucket | Count |
|--------|------:|
| `storyboard/image` / `critical` | 136 |
| `video/cine` / `critical` | 25 |
| `restoration` / `critical` | 0 |
| `3D` / `critical` | 5 |
| `optional/demo` / `demo_optional` | 19 |
| `ambiguous` / `ambiguous` | 0 |

## 8191 Errors Diagnosed

### ComfyUI-RealESRGAN_Upscaler
- Origin: `/home/harliesound/ai/ComfyUI_profiles/restoration/custom_nodes/ComfyUI-RealESRGAN_Upscaler/realesrgan/realesrgan_upscaler.py`
- Error: `ModuleNotFoundError: No module named basicsr.data.degradations`
- Cause: The custom node imports pip package realesrgan/basicsr directly; current shared venv has basicsr 1.4.2 and realesrgan 0.3.0 with import/registry incompatibility against this ComfyUI stack.
- Repair options:
  - separate restoration venv from image first
  - pin a compatible basicsr/realesrgan pair only in restoration venv
  - or disable ComfyUI-RealESRGAN_Upscaler if not required for CID restoration workflows

### zsq_prompt
- Origin: `/home/harliesound/ai/ComfyUI_profiles/restoration/custom_nodes/zsq_prompt/nodes/zsq_loader.py:767`
- Error: `TypeError: VAELoader.vae_list() missing 1 required positional argument: s`
- Cause: zsq_prompt calls VAELoader.vae_list() with no argument, but current ComfyUI nodes.py declares staticmethod vae_list(s), so the plugin is incompatible with this core signature.
- Repair options:
  - patch zsq_prompt to call VAELoader.vae_list(None) or folder_paths.get_filename_list("vae") directly
  - or update zsq_prompt to a ComfyUI-compatible revision
  - or disable the broken loader node if CID does not need it

### NunchakuDepthPreprocessor
- Origin: `/home/harliesound/ai/ComfyUI_profiles/restoration/custom_nodes/nunchaku_nodes/nodes/preprocessors/depth.py:43-45`
- Error: `FileNotFoundError: /home/harliesound/ai/ComfyUI_instances/ComfyUI-restoration/models/checkpoints`
- Cause: Restoration instance points models symlink to /mnt/d/COMFYUI_OK/models, but that backing store lacks a checkpoints directory. The node assumes instance-local folder_paths.models_dir/checkpoints exists.
- Repair options:
  - create or map a valid checkpoints directory in restoration model store
  - or patch the node to tolerate missing checkpoints dir
  - or remove/disable deprecated Nunchaku depth preprocessor and use comfyui_controlnet_aux Depth Anything instead

## 8191 Repair Plan

1. Separate `:8191` restoration venv from `:8188` image before any repair pip action.
2. Revalidate `ComfyUI-RealESRGAN_Upscaler` in the isolated restoration venv with a pinned compatible `basicsr`/`realesrgan` pair.
3. Patch or replace `zsq_prompt` loader usage of `VAELoader.vae_list()`; update plugin if a compatible revision exists.
4. Fix restoration model-path topology so `models/checkpoints` exists for deprecated Nunchaku preprocessing, or disable that node in favor of `comfyui_controlnet_aux`.
5. Re-run `/object_info` timing and node audit after each isolated repair.

## Missing Models Plan

1. Download nothing in 1D.
2. Start with a curated critical wave for `8188 storyboard/image`, then `8189 video/cine`.
3. Resolve ambiguous placeholder references (`{{CHECKPOINT_NAME}}`, tutorial text blobs, malformed names) before any download.
4. Prefer local rename/symlink remediation where an alternate local stem already exists.
5. Use the dedicated download plan report for per-model routing, sources and commands.

## Recommendations

- Separate `:8191` venv from `:8188`: **YES, recommended before real repair**.
- Repair `:8191` now in shared venv: **NO-GO**.
- Controlled `:8191` repair after venv split: **GO**.
- Missing-model mass download now: **NO-GO**.
- Critical-first curated model plan: **GO** after approval.
- ComfyUI-Copilot installation: **NO-GO** until 8191 repair and critical model wave are closed.