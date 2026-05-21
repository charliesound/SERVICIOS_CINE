# ComfyUI Node Inventory Audit

**Date:** 2026-05-21 19:54:44
**Script:** `scripts/dev/audit_comfyui_node_inventory.py`

## Executive Summary

- **Total instances:** 5
- **GO:** 1
- **WARNING:** 3
- **NO-GO:** 1
- **Unreachable:** 0

### :8188 — Image / Still

- **ComfyUI version:** 0.19.3
- **Total nodes:** 3664

#### Family Distribution

| Family | Count | % |
|--------|------:|---:|
| Image / Still | 1248 | 34.1% |
| Video / Cine | 327 | 8.9% |
| Audio / Dubbing | 64 | 1.7% |
| Restoration | 73 | 2.0% |
| 3D | 85 | 2.3% |
| Utility / General | 1061 | 29.0% |
| Unknown | 806 | 22.0% |

#### Top Categories

- ImpactPack/Util: 70
- jamesWalker55: 68
- 😺dzNodes/LayerUtility: 60
- 😺dzNodes/LayerMask: 57
- Swwan/image: 53
- conditioning/video_models: 40
- ArtVenture/Utils: 33
- Image-Filters/image: 33
- WAS Suite/Image/Masking: 32
- EasyUse/Image: 32

#### Out-of-Profile Nodes

- **Video / Cine** (20): AILab_ImageCombiner, AILab_MaskCombiner, APGGuider, AddLabel, Animation Builder (mtb), AnyBooleanSwitch (Swwan), AnySwitch (Swwan), ApplyRifleXRoPE_HunuyanVideo, ApplyRifleXRoPE_WanVideo, BboxDetectorCombined_v2
- **Audio / Dubbing** (20): AnalyzeAudio, Audio Cut (mtb), Audio Duration (mtb), Audio Isolate Speaker (mtb), Audio Resample (mtb), Audio Sequence (mtb), Audio Stack (mtb), Audio To Text (mtb), AudioAdjustVolume, AudioConcat
- **Restoration** (20): AILab_CropObject, AutoCropFaces, BBox Force Dimensions (mtb), BatchCropFromMask, BatchCropFromMaskAdvanced, BatchUncrop, BatchUncropAdvanced, Bbox (mtb), Bbox From Mask (mtb), CR Select Resize Method
- **3D** (20): 3DImage, Batch Float Normalize (mtb), BatchNormalizeImage, CM_ComposeVec2, CM_ComposeVec3, CM_ComposeVec4, CameraPoseVisualizer, ConvertNormals, CtrlNet OpenPose Pipe (JPS), CtrlNet OpenPose Settings (JPS)

**✅ GO** — Preferred family 'Image / Still' represents 34.1% of all nodes — adequate for purpose.

---

### :8189 — Video / Cine

- **ComfyUI version:** 0.14.1
- **Total nodes:** 2576

#### Family Distribution

| Family | Count | % |
|--------|------:|---:|
| Image / Still | 969 | 37.6% |
| Video / Cine | 538 | 20.9% |
| Audio / Dubbing | 29 | 1.1% |
| Restoration | 23 | 0.9% |
| 3D | 50 | 1.9% |
| Utility / General | 457 | 17.7% |
| Unknown | 510 | 19.8% |

#### Top Categories

- WanVideoWrapper: 138
- RES4LYF/sigmas: 72
- ImpactPack/Util: 70
- conditioning/video_models: 37
- HunyuanVideoWrapper: 33
- WAS Suite/Image/Masking: 32
- EasyUse/Image: 32
- RES4LYF/latents: 27
- EasyUse/Logic: 25
- rgthree: 24

#### Out-of-Profile Nodes

- **Audio / Dubbing** (20): AnalyzeAudio, AudioAdjustVolume, AudioConcat, AudioCrop, AudioEncoderLoader, AudioGetTempo, AudioMerge, AudioPlay, AudioSeparation, AudioSpeedShift
- **Restoration** (20): CenterCropImages, DenoiseScheduleHookProvider, Image Inset Crop (rgthree), ImageColorMatch+, ImageColorMatchAdobe+, ImageCropByAlpha, ImpactFrom_SEG_ELT_crop_region, Mask Crop Dominant Region, Mask Crop Minority Region, Mask Crop Region
- **3D** (20): 3DImage, CM_ComposeVec2, CM_ComposeVec3, CM_ComposeVec4, DepthAnything_V2, DepthCrafter, DepthViewer, DownloadAndLoadDepthAnythingV2Model, DownloadAndLoadDepthCrafterModel, DrawGaussianNoiseOnImage
- **Utility / General** (20): AddMask, Any Switch (rgthree), AreaToMask, BLIP Model Loader, BatchCount+, BatchImagesNode, BatchMasksNode, BitwiseAndMask, BitwiseAndMaskForEach, Boolean To Text

**⚠️ WARNING** — Preferred 'Video / Cine' is only 20.9%, but combined with 'Image / Still' reaches 58.5%. COMFYUI.1B cross-check needed.

---

### :8190 — Dubbing / Audio

- **ComfyUI version:** 0.13.0
- **Total nodes:** 1915

#### Family Distribution

| Family | Count | % |
|--------|------:|---:|
| Image / Still | 580 | 30.3% |
| Video / Cine | 327 | 17.1% |
| Audio / Dubbing | 107 | 5.6% |
| Restoration | 24 | 1.3% |
| 3D | 35 | 1.8% |
| Utility / General | 557 | 29.1% |
| Unknown | 285 | 14.9% |

#### Top Categories

- WanVideoWrapper: 137
- ImpactPack/Util: 70
- KJNodes/image: 56
- conditioning/video_models: 34
- 🏵️Fill Nodes/Image: 32
- rgthree: 24
- KJNodes/masking: 24
- 🏵️Fill Nodes/Utility: 24
- api node/video/Kling: 21
- 🏵️Fill Nodes/AI: 20

#### Out-of-Profile Nodes

- **Image / Still** (20): AcademiaSD_BatchLoader, AcademiaSD_MultiLora, AddNoiseToTrackPath, AlignYourStepsScheduler, ApplyCLIPSeg+, Audio IPAdapter Transitions, Audio Prompt Schedule, AudioEncoderEncode, BasicGuider, BasicScheduler
- **Video / Cine** (20): AMT VFI, ATM VFI, Add Subtitles To Frames, ApplyRifleXRoPE_HunuyanVideo, ApplyRifleXRoPE_WanVideo, BboxDetectorCombined_v2, BriaRemoveVideoBackground, ByteDanceFirstLastFrameNode, ByteDanceImageReferenceNode, ByteDanceTextToVideoNode
- **Restoration** (20): BatchCropFromMask, BatchCropFromMaskAdvanced, BatchUncrop, BatchUncropAdvanced, CR Select Resize Method, CenterCropImages, ColorMatch, DenoiseScheduleHookProvider, FL_ImageAspectCropper, Image Inset Crop (rgthree)
- **3D** (20): CM_ComposeVec2, CM_ComposeVec3, CM_ComposeVec4, CameraPoseVisualizer, DrawGaussianNoiseOnImage, ImageNormalize_Neg1_To_1, ImpactDecomposeSEGS, ImpactGaussianBlurMask, ImpactGaussianBlurMaskInSEGS, LoadResAdapterNormalization

**⚠️ WARNING** — Preferred 'Audio / Dubbing' is only 5.6%, but combined with 'Utility / General' reaches 34.7%. COMFYUI.1B cross-check needed.

---

### :8191 — Restoration

- **ComfyUI version:** 0.13.0
- **Total nodes:** 3654

#### Family Distribution

| Family | Count | % |
|--------|------:|---:|
| Image / Still | 1262 | 34.5% |
| Video / Cine | 318 | 8.7% |
| Audio / Dubbing | 56 | 1.5% |
| Restoration | 72 | 2.0% |
| 3D | 77 | 2.1% |
| Utility / General | 1054 | 28.8% |
| Unknown | 815 | 22.3% |

#### Top Categories

- ImpactPack/Util: 70
- jamesWalker55: 68
- 😺dzNodes/LayerUtility: 60
- 😺dzNodes/LayerMask: 57
- Swwan/image: 53
- conditioning/video_models: 39
- ArtVenture/Utils: 33
- Image-Filters/image: 33
- WAS Suite/Image/Masking: 32
- EasyUse/Image: 32

#### Out-of-Profile Nodes

- **Image / Still** (20): ACN_AdvancedControlNetApply, ACN_AdvancedControlNetApplySingle, ACN_AdvancedControlNetApplySingle_v2, ACN_AdvancedControlNetApply_v2, ACN_ControlNet++InputNode, ACN_ControlNet++LoaderAdvanced, ACN_ControlNet++LoaderSingle, ACN_ControlNetLoaderAdvanced, ACN_CtrLoRALoader, ACN_CustomControlNetWeightsFlux
- **Video / Cine** (20): AILab_ImageCombiner, AILab_MaskCombiner, APGGuider, AddLabel, Animation Builder (mtb), AnyBooleanSwitch (Swwan), AnySwitch (Swwan), ApplyRifleXRoPE_HunuyanVideo, ApplyRifleXRoPE_WanVideo, BboxDetectorCombined_v2
- **Audio / Dubbing** (20): AnalyzeAudio, Audio Cut (mtb), Audio Duration (mtb), Audio Isolate Speaker (mtb), Audio Resample (mtb), Audio Sequence (mtb), Audio Stack (mtb), Audio To Text (mtb), AudioAdjustVolume, AudioConcat
- **3D** (20): 3DImage, Batch Float Normalize (mtb), BatchNormalizeImage, CM_ComposeVec2, CM_ComposeVec3, CM_ComposeVec4, CameraPoseVisualizer, ConvertNormals, CtrlNet OpenPose Pipe (JPS), CtrlNet OpenPose Settings (JPS)

**⚠️ WARNING** — Preferred 'Restoration' is only 2.0%, but combined with 'Utility / General' reaches 30.8%. COMFYUI.1B cross-check needed.

---

### :8192 — 3D

- **ComfyUI version:** 0.17.0
- **Total nodes:** 654

#### Family Distribution

| Family | Count | % |
|--------|------:|---:|
| Image / Still | 299 | 45.7% |
| Video / Cine | 90 | 13.8% |
| Audio / Dubbing | 26 | 4.0% |
| Restoration | 8 | 1.2% |
| 3D | 30 | 4.6% |
| Utility / General | 117 | 17.9% |
| Unknown | 84 | 12.8% |

#### Top Categories

- conditioning/video_models: 32
- api node/video/Kling: 22
- loaders: 18
- api node/image/Recraft: 18
- conditioning: 17
- audio: 17
- image: 16
- advanced/model_merging/model_specific: 15
- _for_testing: 14
- mask: 13

#### Out-of-Profile Nodes

- **Image / Still** (20): AlignYourStepsScheduler, AudioEncoderEncode, BasicGuider, BasicScheduler, BatchLatentsNode, BetaSamplingScheduler, ByteDanceImageToVideoNode, CLIPAttentionMultiply, CLIPLoader, CLIPMergeAdd
- **Video / Cine** (20): BriaRemoveVideoBackground, ByteDanceFirstLastFrameNode, ByteDanceImageReferenceNode, ByteDanceTextToVideoNode, CombineHooks2, CombineHooks4, CombineHooks8, CreateHookKeyframe, CreateHookKeyframesFromFloats, CreateHookKeyframesInterpolated
- **Audio / Dubbing** (20): AudioAdjustVolume, AudioConcat, AudioEncoderLoader, AudioEqualizer3Band, AudioMerge, ElevenLabsAudioIsolation, ElevenLabsInstantVoiceClone, ElevenLabsSpeechToSpeech, ElevenLabsSpeechToText, ElevenLabsTextToDialogue
- **Restoration** (8): CenterCropImages, CropByBBoxes, RandomCropImages, ResizeAndPadImage, ResizeImageMaskNode, ResizeImagesByLongerEdge, ResizeImagesByShorterEdge, SplitSigmasDenoise

**❌ NO-GO** — Preferred '3D' is only 4.6% — insufficient coverage.

---

## Recommendations

### ComfyUI-Copilot

- Do **not** install ComfyUI-Copilot yet.
- **Candidato preliminar:** 8188 (Image/Still) if its inventory diagnostic is GO.
- Do not install on 8189/8190/8191/8192 until profile validation (COMFYUI.1B) is complete.
