# ComfyUI Embedded Workflows from Images

**Date:** 2026-05-21 19:55:46

## Summary

- **Images with ComfyUI metadata:** 13
- **Valid embedded workflows extracted:** 13

### By Family

| Family | Count |
|--------|------:|
| image_still | 8 |
| video_cine | 3 |
| utility | 2 |

### Most Useful for CID (13 workflows)

- `/mnt/g/COMFYUI_HUB/workflows/00_IMAGEN_fija/2024-04-07 cascade+controlnet 完美放大图像.png`
  - Family: image_still, Priority: HIGH
  - Class types (10): CLIPTextEncode, CheckpointLoaderSimple, ControlNetApplyAdvanced, ControlNetLoader, KSampler, LoadImage, SaveImage, StableCascade_StageB_Conditioning, StableCascade_SuperResolutionControlnet, VAEDecode
  - Models: cascade\stable_cascade_stage_b.safetensors, cascade\stable_cascade_stage_c.safetensors, cascade\super_resolution.safetensors

- `/mnt/g/COMFYUI_HUB/workflows/00_IMAGEN_fija/Kazitorials-avatar-generator.png`
  - Family: image_still, Priority: HIGH
  - Class types (12): ApplyInstantID, CLIPTextEncode, CheckpointLoaderSimple, ControlNetLoader, EmptyLatentImage, InstantIDFaceAnalysis, InstantIDModelLoader, KSampler, LoadImage, LoraLoader
  - Models: SDXL-Emoji-Lora-r4.safetensors, instantid-diffusion_pytorch_model.safetensors, turbovisionxlSuperFastXLBasedOnNew_tvxlV431Bakedvae.safetensors

- `/mnt/g/COMFYUI_HUB/workflows/00_IMAGEN_fija/SRPO-workflow.png`
  - Family: image_still, Priority: HIGH
  - Class types (15): BasicGuider, BasicScheduler, CLIPTextEncode, DualCLIPLoader, EmptySD3LatentImage, FluxGuidance, KSamplerSelect, ModelSamplingFlux, PrimitiveNode, RandomNoise
  - Models: SRPO/diffusion_pytorch_model.safetensors, ae.safetensors, clip_l.safetensors, t5xxl_fp16.safetensors

- `/mnt/g/COMFYUI_HUB/workflows/00_IMAGEN_fija/Tpose-Template.png`
  - Family: image_still, Priority: HIGH
  - Class types (34): AspectSize, CLIPTextEncodeSDXL, CR Apply LoRA Stack, CR Apply Multi-ControlNet, CR LoRA Stack, CR Multi-ControlNet Stack, CannyEdgePreprocessor, CheckpointLoaderSimple, ColorMatch, DF_Text_Box
  - Models: DJZmerger\cosRealJuggXL-hermit.safetensors, DJZmerger\realvis_juggernaut_hermite.safetensors, Hyper-SDXL-8steps-lora.safetensors, SUPIR\SUPIR-v0Q_fp16.safetensors, XL\OpenPoseXL2.safetensors

- `/mnt/g/COMFYUI_HUB/workflows/00_IMAGEN_fija/Wan2-2-Ultimate-Text-To-Image-fast-render-cinematic-quality.png`
  - Family: image_still, Priority: HIGH
  - Class types (11): CLIPLoader, CLIPTextEncode, Empty Latent by Ratio (WLSH), KSamplerAdvanced, LoraLoaderModelOnly, ModelSamplingSD3, Note, SaveImage, UNETLoader, VAEDecode
  - Models: Wan2.1_I2V_14B_FusionX_LoRA.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors, wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors, wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors, wan_2.1_vae.safetensors

- `/mnt/g/COMFYUI_HUB/workflows/00_IMAGEN_fija/advanced workflow.png`
  - Family: utility, Priority: MEDIUM
  - Class types (20): AddMask, CXH_Leffa_Viton_Load, CXH_Leffa_Viton_Run, DensePosePreprocessor, GetImageSizeAndCount, GetNode, GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything), GrowMaskWithBlur, ImageCompositeMasked
  - Models: sam_vit_b_01ec64.pth

- `/mnt/g/COMFYUI_HUB/workflows/00_IMAGEN_fija/flux_schnell_example.png`
  - Family: image_still, Priority: HIGH
  - Class types (13): BasicGuider, BasicScheduler, CLIPTextEncode, DualCLIPLoader, EmptyLatentImage, KSamplerSelect, Note, RandomNoise, SamplerCustomAdvanced, SaveImage
  - Models: If you get an error in any of the nodes above make sure the files are in the correct directories.

See the top of the examples page for the links : https://comfyanonymous.github.io/ComfyUI_examples/flux/

flux1-schnell.safetensors goes in: ComfyUI/models/unet/

t5xxl_fp16.safetensors and clip_l.safetensors go in: ComfyUI/models/clip/

ae.safetensors goes in: ComfyUI/models/vae/


Tip: You can set the weight_dtype above to one of the fp8 types if you have memory issues., ae.safetensors, clip_l.safetensors, flux1-schnell.safetensors, t5xxl_fp16.safetensors

- `/mnt/g/COMFYUI_HUB/workflows/00_IMAGEN_fija/official workflow.png`
  - Family: utility, Priority: MEDIUM
  - Class types (12): AddMask, CXH_Leffa_Viton_Load, CXH_Leffa_Viton_Run, DensePosePreprocessor, GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything), LayerMask: MaskGrow, LayerUtility: ImageScaleByAspectRatio V2, LoadImage, MaskPreview+
  - Models: sam_vit_b_01ec64.pth

- `/mnt/g/COMFYUI_HUB/workflows/00_IMAGEN_fija/sdxl-recommended-res-calc_upscale-case.png`
  - Family: image_still, Priority: HIGH
  - Class types (17): CLIPTextEncode, CheckpointLoaderSimple, EmptyLatentImage, ImageScaleBy, ImageUpscaleWithModel, KSampler, LatentUpscaleBy, LoraLoader, Note, PrimitiveNode
  - Models: 4x-UltraMix_Balanced.pth, LCM\SDXL-SSD1B\pytorch_lora_weights.safetensors, SDXL\SSD-1B.safetensors, SDXL\sd_xl_offset_example-lora_1.0.safetensors, SDXL\sdxl-vae-fp16-fix.safetensors

- `/mnt/g/COMFYUI_HUB/workflows/00_IMAGEN_fija/wave-speed-flux.png`
  - Family: image_still, Priority: HIGH
  - Class types (15): ApplyFBCacheOnModel, CLIPTextEncode, ConditioningZeroOut, DualCLIPLoader, EmptySD3LatentImage, FluxGuidance, KSampler, LoraLoaderModelOnly, ModelSamplingFlux, PrimitiveNode
  - Models: ae.safetensors, clip_l.safetensors, flux1-dev-fp8.safetensors, flux\Flux_å°çº¢ä¹¦çå®é£æ ¼ä¸¨æ¥å¸¸ç§çä¸¨æè´é¼ç_V2.safetensors, t5xxl_fp8_e4m3fn.safetensors

- `/mnt/g/COMFYUI_HUB/workflows/00_VIDEO/2025-01-07 latent sync唇形拟合.png`
  - Family: video_cine, Priority: HIGH
  - Class types (4): D_LatentSyncNode, LoadAudio, VHS_LoadVideo, VHS_VideoCombine
  - Models: 

- `/mnt/g/COMFYUI_HUB/workflows/00_VIDEO/2025-01-15 nvidia cosmos workflow.png`
  - Family: video_cine, Priority: HIGH
  - Class types (8): CLIPLoader, CLIPTextEncode, EmptyCosmosLatentVideo, KSampler, UNETLoader, VAEDecode, VAELoader, VHS_VideoCombine
  - Models: Cosmos-1_0-Diffusion-7B-Text2World.safetensors, cosmos_cv8x8x8_1.0.safetensors, oldt5_xxl_fp8_e4m3fn_scaled.safetensors

- `/mnt/g/COMFYUI_HUB/workflows/video_cine/Mo-Cha-Replace-Anyone-in-a-Video.png`
  - Family: video_cine, Priority: HIGH
  - Class types (26): DownloadAndLoadSAM2Model, GetImageRangeFromBatch, GetNode, GrowMaskWithBlur, ImageConcanate, ImageResizeKJv2, LoadImage, MarkdownNote, MaskPreview, MochaEmbeds
  - Models: # model links:

VAE, text_encoder:

[https://huggingface.co/Kijai/WanVideo_comfy](https://huggingface.co/Kijai/WanVideo_comfy)

fp8_scaled version:

[https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/blob/main/MoCha/Wan2_1_mocha-14B-preview_fp8_e4m3fn_scaled_KJ.safetensors](https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/blob/main/MoCha/Wan2_1_mocha-14B-preview_fp8_e4m3fn_scaled_KJ.safetensors), Lightx2v/lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors, WanVideo/MoCha/Wan2_1_mocha-14B-preview_fp8_e4m3fn_scaled_KJ.safetensors, WanVideo/Wan2_1_VAE_bf16.safetensors, WanVideo/umt5-xxl-enc-bf16.safetensors

### Cross-Reference with Instances

#### 2024-04-07 cascade+controlnet 完美放大图像.png
- **Family:** image_still
- **Required nodes:** 10
  - :8188: **GO** — all nodes available
  - :8189: **GO** — all nodes available
  - :8190: **GO** — all nodes available
  - :8191: **GO** — all nodes available
  - :8192: **GO** — all nodes available

#### Kazitorials-avatar-generator.png
- **Family:** image_still
- **Required nodes:** 12
  - :8188: **GO** — all nodes available
  - :8189: 3 missing (ApplyInstantID, InstantIDFaceAnalysis, InstantIDModelLoader)
  - :8190: 3 missing (ApplyInstantID, InstantIDFaceAnalysis, InstantIDModelLoader)
  - :8191: **GO** — all nodes available
  - :8192: 3 missing (ApplyInstantID, InstantIDFaceAnalysis, InstantIDModelLoader)

#### SRPO-workflow.png
- **Family:** image_still
- **Required nodes:** 15
  - :8188: 1 missing (PrimitiveNode)
  - :8189: 1 missing (PrimitiveNode)
  - :8190: 1 missing (PrimitiveNode)
  - :8191: 1 missing (PrimitiveNode)
  - :8192: 1 missing (PrimitiveNode)

#### Tpose-Template.png
- **Family:** image_still
- **Required nodes:** 34
  - :8188: 5 missing (AspectSize, DF_Text_Box, Fast Groups Bypasser (rgthree), Note, Reroute)
  - :8189: 18 missing (AspectSize, CR Apply LoRA Stack, CR Apply Multi-ControlNet, CR LoRA Stack, CR Multi-ControlNet Stack, ColorMatch, DF_Text_Box, Fast Groups Bypasser (rgthree))
  - :8190: 17 missing (AspectSize, CannyEdgePreprocessor, DF_Text_Box, Fast Groups Bypasser (rgthree), Note, OpenposePreprocessor, ReActorFaceSwap, ReActorLoadFaceModel)
  - :8191: 5 missing (AspectSize, DF_Text_Box, Fast Groups Bypasser (rgthree), Note, Reroute)
  - :8192: 25 missing (AspectSize, CR Apply LoRA Stack, CR Apply Multi-ControlNet, CR LoRA Stack, CR Multi-ControlNet Stack, CannyEdgePreprocessor, ColorMatch, DF_Text_Box)

#### Wan2-2-Ultimate-Text-To-Image-fast-render-cinematic-quality.png
- **Family:** image_still
- **Required nodes:** 11
  - :8188: 1 missing (Note)
  - :8189: 2 missing (Empty Latent by Ratio (WLSH), Note)
  - :8190: 2 missing (Empty Latent by Ratio (WLSH), Note)
  - :8191: 1 missing (Note)
  - :8192: 2 missing (Empty Latent by Ratio (WLSH), Note)

#### advanced workflow.png
- **Family:** utility
- **Required nodes:** 20
  - :8188: 6 missing (CXH_Leffa_Viton_Load, CXH_Leffa_Viton_Run, GetNode, GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything), SetNode)
  - :8189: 10 missing (CXH_Leffa_Viton_Load, CXH_Leffa_Viton_Run, GetImageSizeAndCount, GetNode, GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything), GrowMaskWithBlur, ImageResizeKJ)
  - :8190: 9 missing (CXH_Leffa_Viton_Load, CXH_Leffa_Viton_Run, DensePosePreprocessor, GetNode, GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything), ImageScaleToMegapixels, SetNode)
  - :8191: 6 missing (CXH_Leffa_Viton_Load, CXH_Leffa_Viton_Run, GetNode, GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything), SetNode)
  - :8192: 16 missing (AddMask, CXH_Leffa_Viton_Load, CXH_Leffa_Viton_Run, DensePosePreprocessor, GetImageSizeAndCount, GetNode, GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything))

#### flux_schnell_example.png
- **Family:** image_still
- **Required nodes:** 13
  - :8188: 1 missing (Note)
  - :8189: 1 missing (Note)
  - :8190: 1 missing (Note)
  - :8191: 1 missing (Note)
  - :8192: 1 missing (Note)

#### official workflow.png
- **Family:** utility
- **Required nodes:** 12
  - :8188: 4 missing (CXH_Leffa_Viton_Load, CXH_Leffa_Viton_Run, GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything))
  - :8189: 6 missing (CXH_Leffa_Viton_Load, CXH_Leffa_Viton_Run, GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything), LayerMask: MaskGrow, LayerUtility: ImageScaleByAspectRatio V2)
  - :8190: 7 missing (CXH_Leffa_Viton_Load, CXH_Leffa_Viton_Run, DensePosePreprocessor, GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything), LayerMask: MaskGrow, LayerUtility: ImageScaleByAspectRatio V2)
  - :8191: 4 missing (CXH_Leffa_Viton_Load, CXH_Leffa_Viton_Run, GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything))
  - :8192: 10 missing (AddMask, CXH_Leffa_Viton_Load, CXH_Leffa_Viton_Run, DensePosePreprocessor, GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything), LayerMask: MaskGrow, LayerUtility: ImageScaleByAspectRatio V2)

#### sdxl-recommended-res-calc_upscale-case.png
- **Family:** image_still
- **Required nodes:** 17
  - :8188: 4 missing (Note, PrimitiveNode, RecommendedResCalc, Reroute)
  - :8189: 4 missing (Note, PrimitiveNode, RecommendedResCalc, Reroute)
  - :8190: 4 missing (Note, PrimitiveNode, RecommendedResCalc, Reroute)
  - :8191: 4 missing (Note, PrimitiveNode, RecommendedResCalc, Reroute)
  - :8192: 4 missing (Note, PrimitiveNode, RecommendedResCalc, Reroute)

#### wave-speed-flux.png
- **Family:** image_still
- **Required nodes:** 15
  - :8188: 3 missing (ApplyFBCacheOnModel, PrimitiveNode, SetNode)
  - :8189: 3 missing (ApplyFBCacheOnModel, PrimitiveNode, SetNode)
  - :8190: 3 missing (ApplyFBCacheOnModel, PrimitiveNode, SetNode)
  - :8191: 3 missing (ApplyFBCacheOnModel, PrimitiveNode, SetNode)
  - :8192: 3 missing (ApplyFBCacheOnModel, PrimitiveNode, SetNode)

#### 2025-01-07 latent sync唇形拟合.png
- **Family:** video_cine
- **Required nodes:** 4
  - :8188: 1 missing (D_LatentSyncNode)
  - :8189: 1 missing (D_LatentSyncNode)
  - :8190: 1 missing (D_LatentSyncNode)
  - :8191: 1 missing (D_LatentSyncNode)
  - :8192: 3 missing (D_LatentSyncNode, VHS_LoadVideo, VHS_VideoCombine)

#### 2025-01-15 nvidia cosmos workflow.png
- **Family:** video_cine
- **Required nodes:** 8
  - :8188: **GO** — all nodes available
  - :8189: **GO** — all nodes available
  - :8190: **GO** — all nodes available
  - :8191: **GO** — all nodes available
  - :8192: 1 missing (VHS_VideoCombine)

#### Mo-Cha-Replace-Anyone-in-a-Video.png
- **Family:** video_cine
- **Required nodes:** 26
  - :8188: 14 missing (GetNode, MarkdownNote, MochaEmbeds, Note, SetNode, WanVideoBlockSwap, WanVideoDecode, WanVideoLoraSelectMulti)
  - :8189: 9 missing (GetImageRangeFromBatch, GetNode, GrowMaskWithBlur, ImageConcanate, ImageResizeKJv2, MarkdownNote, Note, PointsEditor)
  - :8190: 6 missing (DownloadAndLoadSAM2Model, GetNode, MarkdownNote, Note, Sam2Segmentation, SetNode)
  - :8191: 14 missing (GetNode, MarkdownNote, MochaEmbeds, Note, SetNode, WanVideoBlockSwap, WanVideoDecode, WanVideoLoraSelectMulti)
  - :8192: 23 missing (DownloadAndLoadSAM2Model, GetImageRangeFromBatch, GetNode, GrowMaskWithBlur, ImageConcanate, ImageResizeKJv2, MarkdownNote, MochaEmbeds)
