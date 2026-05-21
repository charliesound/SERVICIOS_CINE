# ComfyUI Missing Nodes Install Plan

**Date:** 2026-05-21 19:55:46
**Source:** COMFYUI.1B cross-check audit

## Rules

1. **Do NOT execute any command in this document.**
2. This is a planning document for COMFYUI.1C controlled installation.
3. Each installation must have a backup and rollback plan.
4. Prefer local sources (G: hub, other instance) before git clone.

## Missing Nodes Requiring Installation

| Missing Node | Workflow | Recommended Instance | Local Source | External Source Needed | Risk |
|-------------|----------|--------------------|-------------|----------------------|------|
| `Reroute` | 01-faceswap.json | :8188 still | none | YES | high |
| `Text box` | 01-faceswap.json | :8188 still | none | YES | high |
| `MarkdownNote` | 01a_Qwen-Image Distill.json | :8188 still | none | YES | high |
| `Note` | 01a_Qwen-Image Distill.json | :8188 still | none | YES | high |
| `e5cfe5ba-2ae0-4bc4-869f-ab2228cb44d3` | 01a_Qwen-Image Distill“Character Bible”.json | :8188 still | none | YES | high |
| `2c61139d-9c34-4c7e-a083-7a67cc4770ad` | 01_qwen_t2i_subgraphed_Capitulo18.json | :8188 still | none | YES | high |
| `fc11e656-d80a-42fa-ae56-c197af368516` | 02_FLUX_Base realista.json | :8188 still | none | YES | high |
| `Geometry Sphere (mtb)` | 06-seamless_equilateral.json | :8188 still | none | YES | high |
| `UltimateSDUpscale` | 10_WF_ComfyUI_IP_Adapter_Plus_Integración_de_prompts_de_imagen_y.json | :8188 still | none | YES | high |
| `RandomNoise //Inspire` | 17 - workflow_flux_standar.json | :8188 still | none | YES | high |
| `CheckpointLoaderNF4` | 18a - workflow_nf4.json | :8188 still | none | YES | high |
| `ApplyFluxControlNet` | 20 - ControlNet_Cany_Depth_HED.json | :8188 still | none | YES | high |
| `InstantX Flux Union ControlNet Loader` | 20 - ControlNet_Cany_Depth_HED.json | :8188 still | none | YES | high |
| `LoadFluxControlNet` | 20 - ControlNet_Cany_Depth_HED.json | :8188 still | none | YES | high |
| `XlabsSampler` | 20 - ControlNet_Cany_Depth_HED.json | :8188 still | none | YES | high |
| `LoadImageListFromDir //Inspire` | 22 - Batch_Prompts_Florence2.json | :8188 still | none | YES | high |
| `LoadPromptsFromFile //Inspire` | 22 - Batch_Prompts_Florence2.json | :8188 still | none | YES | high |
| `SaveText` | 22 - Batch_Prompts_Florence2.json | :8188 still | none | YES | high |
| `UnzipPrompt //Inspire` | 22 - Batch_Prompts_Florence2.json | :8188 still | none | YES | high |
| `CatVTONWrapper` | 24 - CatVTON_Cambia_Ropa_Modelos.json | :8188 still | none | YES | high |
| `GroundingDinoModelLoader (segment anything)` | 24 - CatVTON_Cambia_Ropa_Modelos.json | :8188 still | none | YES | high |
| `GroundingDinoSAMSegment (segment anything)` | 24 - CatVTON_Cambia_Ropa_Modelos.json | :8188 still | none | YES | high |
| `BNK_Unsampler` | 32 - ComfyUI Colorize Photos-Final.json | :8188 still | none | YES | high |
| `PrimitiveNode` | 33 - ComfyUI - Flux_Redux_Combine Images.json | :8188 still | none | YES | high |
| `Fast Groups Bypasser (rgthree)` | 35 - ComfyUI - Cambio de Fondo.json | :8188 still | none | YES | high |
| `GetNode` | 35 - ComfyUI - Cambio de Fondo.json | :8188 still | none | YES | high |
| `SetNode` | 35 - ComfyUI - Cambio de Fondo.json | :8188 still | none | YES | high |
| `InpaintResize` | 37b_BODYSWAP 2_2.json | :8188 still | none | YES | high |
| `Load Styles CSV` | 37b_BODYSWAP 2_2.json | :8188 still | none | YES | high |
| `Textbox` | 37b_BODYSWAP 2_2.json | :8188 still | none | YES | high |
| `ApplyPulidFlux` | 41_ComfyUI_PULID (1 Cara).json | :8188 still | none | YES | high |
| `PulidFluxEvaClipLoader` | 41_ComfyUI_PULID (1 Cara).json | :8188 still | none | YES | high |
| `PulidFluxInsightFaceLoader` | 41_ComfyUI_PULID (1 Cara).json | :8188 still | none | YES | high |
| `PulidFluxModelLoader` | 41_ComfyUI_PULID (1 Cara).json | :8188 still | none | YES | high |
| `DiffusersCompelPromptEmbedding` | change-clothes.json | :8188 still | none | YES | high |
| `DiffusersControlnetLoader` | change-clothes.json | :8188 still | none | YES | high |
| `DiffusersControlnetUnit` | change-clothes.json | :8188 still | none | YES | high |
| `DiffusersGenerator` | change-clothes.json | :8188 still | none | YES | high |
| `DiffusersPipeline` | change-clothes.json | :8188 still | none | YES | high |
| `DiffusersTextureInversionLoader` | change-clothes.json | :8188 still | none | YES | high |
| `preview_mask` | change-clothes.json | :8188 still | none | YES | high |
| `segformer_b2_clothes` | change-clothes.json | :8188 still | :8189 Comfyui_segformer_b2_clothes | no | medium |
| `UpscaleImage` | comfyui_workflow_previz_refine.json | :8188 still | none | YES | high |
| `VHS_FramesToVideoWAudio` | comfyui_workflow_previz_refine.json | :8188 still | none | YES | high |
| `VHS_VideoToFramesWAudio` | comfyui_workflow_previz_refine.json | :8188 still | none | YES | high |
| `MultiAreaConditioning` | control-flux-image-visualization.json | :8188 still | none | YES | high |
| `AspectSize` | cosTrio-Tpose-Factory-v12.json | :8188 still | none | YES | high |
| `DF_Text_Box` | cosTrio-Tpose-Factory-v12.json | :8188 still | none | YES | high |
| `ImageSegmentationCustom` | cosTrio-Tpose-Factory-v12.json | :8188 still | none | YES | high |
| `FluxPromptGenerator` | enhance-your-ai-art-with-the-flux-prompt-generator.json | :8188 still | none | YES | high |
| `DF_Get_image_size` | flux-redux-pulid-face-swap-clone-any-portrait-photography.json | :8188 still | none | YES | high |
| `Int Literal` | FluxRealLoraWorkflowjson.json | :8188 still | none | YES | high |
| `String Literal` | FluxRealLoraWorkflowjson.json | :8188 still | none | YES | high |
| `FluxTrainEnd` | flux_lora_train_Capitulo14.json | :8188 still | none | YES | high |
| `FluxTrainLoop` | flux_lora_train_Capitulo14.json | :8188 still | none | YES | high |
| `FluxTrainModelSelect` | flux_lora_train_Capitulo14.json | :8188 still | none | YES | high |
| `FluxTrainSave` | flux_lora_train_Capitulo14.json | :8188 still | none | YES | high |
| `FluxTrainValidate` | flux_lora_train_Capitulo14.json | :8188 still | none | YES | high |
| `FluxTrainValidationSettings` | flux_lora_train_Capitulo14.json | :8188 still | none | YES | high |
| `InitFluxLoRATraining` | flux_lora_train_Capitulo14.json | :8188 still | none | YES | high |
| `OptimizerConfig` | flux_lora_train_Capitulo14.json | :8188 still | none | YES | high |
| `TrainDatasetAdd` | flux_lora_train_Capitulo14.json | :8188 still | none | YES | high |
| `TrainDatasetGeneralConfig` | flux_lora_train_Capitulo14.json | :8188 still | none | YES | high |
| `UploadToHuggingFace` | flux_lora_train_Capitulo14.json | :8188 still | none | YES | high |
| `VisualizeLoss` | flux_lora_train_Capitulo14.json | :8188 still | none | YES | high |
| `IPAdapterApply` | Hacer pelicula - copia.json | :8188 still | none | YES | high |
| `rgthree.ImageSwitch` | Hacer pelicula - copia.json | :8188 still | none | YES | high |
| `rgthree.Int` | Hacer pelicula - copia.json | :8188 still | none | YES | high |
| `014000e7-58f1-44cf-b764-cf15d4559d2d` | image_qwen_image_instantx_controlnet.json | :8188 still | none | YES | high |
| `999e6c03-bebc-42af-ba36-6a6e2ccad87f` | image_qwen_image_instantx_controlnet.json | :8188 still | none | YES | high |
| `ef3b4b73-ce32-4a60-a60e-d7f278bf6b14` | image_qwen_image_instantx_controlnet_Capitulo18.json | :8188 still | none | YES | high |
| `2a4b2cc0-db37-4302-a067-da392f38f06b` | image_qwen_image_instantx_inpainting_controlnet.json | :8188 still | none | YES | high |
| `cade3e30-0eb2-4fd2-bf6e-8518f3a96e0c` | image_qwen_image_instantx_inpainting_controlnet.json | :8188 still | none | YES | high |
| `f93c215e-c393-460e-9534-ed2c3d8a652e` | image_qwen_image_instantx_inpainting_controlnet.json | :8188 still | none | YES | high |
| `SAMModelLoader (segment anything)` | Inpainting workflow for changing a specific object.json | :8188 still | none | YES | high |
| `FaceAnalysisModels` | instantid_monalisa.json | :8188 still | none | YES | high |
| `FaceEmbedDistance` | instantid_monalisa.json | :8188 still | none | YES | high |
| `Fast Bypasser (rgthree)` | NSFW SFW ACE Faceswap V1.0.json | :8188 still | none | YES | high |
| `Label (rgthree)` | NSFW SFW ACE Faceswap V1.0.json | :8188 still | none | YES | high |
| `Reroute (rgthree)` | NSFW SFW ACE Faceswap V1.0.json | :8188 still | none | YES | high |
| `OpenPosePreprocessor` | SB_Character_SDXL.json | :8188 still | none | YES | high |
| `Searge_Output_Node` | sup3rmass1ve_sd3_5_large_with_searge_prompt_enhance_and_lora_and_upscale_comfyworkflows.json | :8188 still | none | YES | high |
| `workflow>Prompt/Model/Clip/Vae Loader` | sup3rmass1ve_sd3_5_large_with_searge_prompt_enhance_and_lora_and_upscale_comfyworkflows.json | :8188 still | none | YES | high |
| `0f47377a-2933-4dba-9791-a9c54b078226` | templates-1_click_multiple_character_angles-v1.0.json | :8188 still | none | YES | high |
| `b7908082-f5ff-497d-8e80-e4b0ffde0419` | templates-1_click_multiple_character_angles-v1.0.json | :8188 still | none | YES | high |
| `ComfyUIStyler` | the_writer_nightmare___4_comfyworkflows.json | :8188 still | none | YES | high |
| `LoraTagLoader` | the_writer_nightmare___4_comfyworkflows.json | :8188 still | none | YES | high |
| `PerturbedAttention` | the_writer_nightmare___4_comfyworkflows.json | :8188 still | none | YES | high |
| `Seed Generator` | the_writer_nightmare___4_comfyworkflows.json | :8188 still | none | YES | high |
| `smZ CLIPTextEncode` | the_writer_nightmare___4_comfyworkflows.json | :8188 still | none | YES | high |
| `workflow/GROUP` | workflow-4x-quick-upscale-fyoo07TxBwG1JLuyKZHA-comfyuistudio-openart.ai.json | :8188 still | none | YES | high |
| `SamplerTCD EulerA` | workflow-accelerate-the-generation-speed-Cfi0e0ME28jHdXXDILE5-datou-openart.ai.json | :8188 still | none | YES | high |
| `TCDScheduler` | workflow-accelerate-the-generation-speed-Cfi0e0ME28jHdXXDILE5-datou-openart.ai.json | :8188 still | none | YES | high |
| `07b8db07-5236-4589-9347-b3fd7b936d55` | workflow-flux-2-klein-inpaint-segment-edit-for-accurate-image-edit-vo9umAlx9kjGRaijxRmP-cgpixel_ai_art-openart.ai.json | :8188 still | none | YES | high |
| `0867c4f0-1670-4efa-9195-cb61affe1c9e` | workflow-flux-2-klein-inpaint-segment-edit-for-accurate-image-edit-vo9umAlx9kjGRaijxRmP-cgpixel_ai_art-openart.ai.json | :8188 still | none | YES | high |
| `55e214e1-4bed-4bda-8246-b83931369f04` | workflow-flux-2-klein-inpaint-segment-edit-for-accurate-image-edit-vo9umAlx9kjGRaijxRmP-cgpixel_ai_art-openart.ai.json | :8188 still | none | YES | high |
| `5abd9f6f-0b12-4c44-a593-f974b3d732a5` | workflow-flux-2-klein-inpaint-segment-edit-for-accurate-image-edit-vo9umAlx9kjGRaijxRmP-cgpixel_ai_art-openart.ai.json | :8188 still | none | YES | high |
| `809e2017-0ccb-4667-b9d8-19102e83c301` | workflow-flux-2-klein-inpaint-segment-edit-for-accurate-image-edit-vo9umAlx9kjGRaijxRmP-cgpixel_ai_art-openart.ai.json | :8188 still | none | YES | high |
| `8a41ffb9-6ce7-4bec-80f5-c6ac49e87434` | workflow-flux-2-klein-inpaint-segment-edit-for-accurate-image-edit-vo9umAlx9kjGRaijxRmP-cgpixel_ai_art-openart.ai.json | :8188 still | none | YES | high |
| `a8e409d9-c985-45b8-bcb2-935ac5ef7894` | workflow-flux-2-klein-inpaint-segment-edit-for-accurate-image-edit-vo9umAlx9kjGRaijxRmP-cgpixel_ai_art-openart.ai.json | :8188 still | none | YES | high |
