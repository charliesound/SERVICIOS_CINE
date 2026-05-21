# ComfyUI Workflow Cross-Check Audit

**Date:** 2026-05-21 21:12:05
**Script:** `scripts/dev/audit_comfyui_workflow_crosscheck.py`

## Executive Summary

- **Total workflows found:** 463
- **Valid (parsed successfully):** 441
- **Invalid/unparseable:** 22
- **HIGH priority for CID:** 394
- **MEDIUM priority:** 47
- **LOW priority:** 0

### Workflows by Family

| Family | Count |
|--------|------:|
| image_still | 264 |
| video_cine | 123 |
| utility | 47 |
| three_d | 3 |
| dubbing_audio | 2 |
| storyboard | 1 |
| restoration | 1 |

## Cross-Reference: Workflows vs Instances

### Best Instance per Workflow

| Workflow | Family | Priority | Nodes Req. | Best Instance | Missing | Diag |
|----------|--------|----------|-----------|---------------|--------|------|
| cinematic_storyboard_sdxl.json | image_still | HIGH | 6 | :8188 | 0 | GO |
| storyboard_fast_sdxl.json | image_still | HIGH | 6 | :8188 | 0 | GO |
| cinematic_storyboard_sdxl.template.json | image_still | HIGH | 6 | :8188 | 0 | GO |
| storyboard_fast_sdxl.template.json | image_still | HIGH | 6 | :8188 | 0 | GO |
| flux_cine_2.template.json | image_still | HIGH | 9 | :8188 | 0 | GO |
| 01-faceswap.json | image_still | HIGH | 16 | :8188 | 2 | WARNING |
| 01a_Qwen-Image Distill.json | image_still | HIGH | 11 | :8188 | 2 | WARNING |
| 01a_Qwen-Image Distill“Character Bible”.json | video_cine | HIGH | 3 | :8188 | 2 | WARNING |
| 01_Qwen-Image (T2I).json | video_cine | HIGH | 3 | :8188 | 2 | WARNING |
| 01_qwen_t2i_subgraphed_Capitulo18.json | video_cine | HIGH | 3 | :8188 | 2 | WARNING |
| 02_FLUX_Base realista.json | image_still | HIGH | 3 | :8188 | 2 | WARNING |
| 05-seamless_texture.json | image_still | HIGH | 12 | :8188 | 1 | WARNING |
| 05_Wan2.2 14B FLF2V (First+Last Frame to Video).json | image_still | HIGH | 16 | :8188 | 0 | GO |
| 06-seamless_equilateral.json | image_still | HIGH | 15 | :8188 | 1 | WARNING |
| 10_WF_ComfyUI_IP_Adapter_Plus_Integración_de_prompts_de_imagen_y.json | image_still | HIGH | 17 | :8188 | 2 | WARNING |
| 11 - Reactor.json | image_still | HIGH | 10 | :8188 | 0 | GO |
| 12 - Faceswap_instantID_IpAdapter.json | image_still | HIGH | 14 | :8188 | 0 | GO |
| 12a - Faceswap_instantID.json | image_still | HIGH | 11 | :8188 | 0 | GO |
| 14 - BGRM_Bria_Remover.json | video_cine | HIGH | 4 | :8188 | 0 | GO |
| 14a -.json | video_cine | HIGH | 4 | :8188 | 0 | GO |
| 15 - workflow1.json | utility | MEDIUM | 5 | :8188 | 0 | GO |
| 15a - workflow2.json | video_cine | HIGH | 8 | :8188 | 0 | GO |
| 16 - Influencer.json | image_still | HIGH | 27 | :8188 | 2 | WARNING |
| 17 - workflow_flux_standar.json | image_still | HIGH | 13 | :8188 | 2 | WARNING |
| 18 - Florens_i2i.json | image_still | HIGH | 18 | :8188 | 0 | GO |
| 18a - workflow_nf4.json | image_still | HIGH | 10 | :8188 | 1 | WARNING |
| 20 - ControlNet_Cany_Depth_HED.json | image_still | HIGH | 20 | :8188 | 6 | NO-GO |
| 21 - 3D_Render_Completo.json | image_still | HIGH | 21 | :8188 | 1 | WARNING |
| 21 - ComfyUI - Render de Stilos.json | image_still | HIGH | 28 | :8188 | 2 | WARNING |
| 21 - ComfyUI - Render de Stilos__677be3b6.json | image_still | HIGH | 28 | :8188 | 2 | WARNING |
| 22 - Batch_Prompts_Florence2.json | image_still | HIGH | 16 | :8188 | 4 | WARNING |
| 23 - Inpainting_Upscaler_FLUX.json | image_still | HIGH | 26 | :8188 | 2 | WARNING |
| 24 - CatVTON_Cambia_Ropa_Modelos.json | utility | MEDIUM | 10 | :8188 | 4 | WARNING |
| 24 - ComfyUI_ CatVTON.json | utility | MEDIUM | 6 | :8188 | 0 | GO |
| 25 - ComfyUI FLUX - Composición.json | image_still | HIGH | 10 | :8188 | 0 | GO |
| 29 - ComfyUI_FluxUpscaler.json | image_still | HIGH | 33 | :8188 | 2 | WARNING |
| 32 - ComfyUI Colorize Photos-Final.json | image_still | HIGH | 17 | :8188 | 1 | WARNING |
| 33 - ComfyUI - Flux_Redux_Combine Images.json | image_still | HIGH | 16 | :8188 | 2 | WARNING |
| 34 - ComfyUI - Cambio_otras_FLUX.json | image_still | HIGH | 23 | :8188 | 0 | GO |
| 34 - ComfyUI - Cambio_Ropa_FLUX.json | image_still | HIGH | 21 | :8188 | 0 | GO |
| 34 - ComfyUI -FLUX Inpainting.json | image_still | HIGH | 11 | :8188 | 0 | GO |
| 35 - ComfyUI - Cambio de Fondo.json | image_still | HIGH | 31 | :8188 | 3 | WARNING |
| 37b_BODYSWAP 2_2.json | image_still | HIGH | 19 | :8188 | 3 | WARNING |
| 37_BODYSWAP 2_GUFF_2.json | image_still | HIGH | 28 | :8188 | 2 | WARNING |
| 37_BODYSWAP 2_GUFF_2_desordenado_modificado.json | image_still | HIGH | 31 | :8188 | 4 | WARNING |
| 3_ComfyUI_tableDiffusion_Standar_2_KSamplers.json | image_still | HIGH | 9 | :8188 | 1 | WARNING |
| 41_ComfyUI_PULID (1 Cara).json | image_still | HIGH | 23 | :8188 | 5 | WARNING |
| 41_ComfyUI_PULID (2 caras).json | image_still | HIGH | 26 | :8188 | 6 | NO-GO |
| 58 - Hiperrealismo-Qwen.json | image_still | HIGH | 16 | :8188 | 2 | WARNING |
| 63relightingQwen.json | image_still | HIGH | 15 | :8188 | 1 | WARNING |
| *... and 391 more* | | | | | | |

### Aggregate Missing Nodes per Instance

| Instance | Total Missing | External Nodes |
|----------|-------------:|----------------|
| :8188 still | 1601 | 393 |
| :8189 video | 2081 | 393 |
| :8190 dubbing | 2287 | 393 |
| :8191 restoration | 1626 | 393 |
| :8192 3d | 3452 | 393 |

### Nodes Requiring External Installation

These nodes are not found in any instance's object_info nor in local custom_nodes:

- `00093772-bf7d-47a3-8c4c-c29965d31336`
- `00a07f4d-d12a-4255-a63e-f17cbc13dbd3`
- `014000e7-58f1-44cf-b764-cf15d4559d2d`
- `024ffd1a-eb57-4930-96b0-f61b1125e911`
- `07b8db07-5236-4589-9347-b3fd7b936d55`
- `0867c4f0-1670-4efa-9195-cb61affe1c9e`
- `0d267b71-f69c-4715-b24d-77983a47db38`
- `0f47377a-2933-4dba-9791-a9c54b078226`
- `1135e349-dce8-45e8-8905-aaa86675429b`
- `16c4feb3-9adc-4bfd-ab30-e57cab73ffbf`
- `1b165832-48d7-439f-8635-a156c338ac6d`
- `1bff7d11-288a-4011-afd5-b901733d4f90`
- `1ea4fa01-a81b-4420-a03c-f60019e69a92`
- `24fa26a4-166e-4f16-aa41-fdf04f07700f`
- `2a4b2cc0-db37-4302-a067-da392f38f06b`
- `2b61e18f-9327-49e6-98af-da8e557c2336`
- `2c61139d-9c34-4c7e-a083-7a67cc4770ad`
- `2dc75cab-e957-4437-a5bb-2afb0ea00516`
- `30ef1e74-19ac-44b5-b6d9-872acdf0c6e1`
- `31d4829e-74b4-48a0-a610-1708e106b780`
- `36d62718-4b8d-47b5-826c-1ab28b0c1457`
- `37eb9014-2859-4cb4-94e3-1c0dd0717f0e`
- `3a6c1476-6f05-42ca-b5b2-913140988506`
- `3ad0b41c-8c47-4e10-a53e-ed340cc26b5f`
- `3eaa20c4-5842-4fe4-87df-c0a7e83a6a78`
- `40e3faf7-eef2-4977-916c-9f47d4903f38`
- `50d1e076-f024-4de9-9193-ec81e321e1dc`
- `55e214e1-4bed-4bda-8246-b83931369f04`
- `58374208-7916-4582-9f02-035a4536f14b`
- `5ab36065-da85-4170-856a-d66e8af6b42d`
- `5abd9f6f-0b12-4c44-a593-f974b3d732a5`
- `646e06d4-ef7d-4e2d-9266-3f03de5d7f0b`
- `65e1c5bd-6c3a-4569-960f-5a9656bb6cef`
- `6a20d49e-c1e9-4e92-a7aa-f5550649f6f0`
- `6aafa765-0602-4408-b31b-e021886884d6`
- `7aad998c-49e7-433f-bfb9-b1ac2680aa9e`
- `7f69112d-3211-40a8-96e0-ae5dc843224b`
- `805a5f96-6fdd-45a4-a1f3-623234fa734f`
- `809e2017-0ccb-4667-b9d8-19102e83c301`
- `813daba6-ec1d-42dd-87bc-4f0f6e084a8d`
- `85c93ab6-8a61-4f3c-8618-30f33ac9a97f`
- `874f986e-c628-43d6-8e5b-258f36c7e949`
- `8a41ffb9-6ce7-4bec-80f5-c6ac49e87434`
- `8bdb5fbd-97a0-498a-bdca-4d4befb92b1e`
- `999e6c03-bebc-42af-ba36-6a6e2ccad87f`
- `AnimateDiffCombine`
- `AnimateDiffLoader`
- `AnimateDiffModuleLoader`
- `AnimateDiffSampler`
- `AnimateDiffSlidingWindowOptions`

## Model Availability

- **Models referenced in workflows:** 1553
- **Found:** 1071
- **Missing:** 482

### Missing Models

- `cid_storyboard_preview` (from `cinematic_storyboard_sdxl.template.json`)
- `{{CHECKPOINT_NAME}}` (from `cinematic_storyboard_sdxl.template.json`)
- `cid_storyboard_fast` (from `storyboard_fast_sdxl.template.json`)
- `{{CHECKPOINT_NAME}}` (from `storyboard_fast_sdxl.template.json`)
- `FILM_FLUX/SHOT` (from `flux_cine_2.template.json`)
- `revAnimated_v122.safetensors` (from `05-seamless_texture.json`)
- `SDXL\360RedmondResized.safetensors` (from `06-seamless_equilateral.json`)
- `SDXL\xl_more_art-full_v1.safetensors` (from `06-seamless_equilateral.json`)
- `juggernautXL_v9Rdphoto2Lightning.safetensors` (from `06-seamless_equilateral.json`)
- `4xUltrasharp_4xUltrasharpV10.pt` (from `10_WF_ComfyUI_IP_Adapter_Plus_Integración_de_prompts_de_imagen_y.json`)
- `TTPLANET_Controlnet_Tile_realistic_v2_fp16.safetensors` (from `10_WF_ComfyUI_IP_Adapter_Plus_Integración_de_prompts_de_imagen_y.json`)
- `XL1..5_epicrealismXL_v8Kiss.safetensors` (from `10_WF_ComfyUI_IP_Adapter_Plus_Integración_de_prompts_de_imagen_y.json`)
- `XL1.0_juggernautXL_juggXIByRundiffusion.safetensors` (from `11 - Reactor.json`)
- `XL1.0_juggernautXL_juggXIByRundiffusion.safetensors` (from `12 - Faceswap_instantID_IpAdapter.json`)
- `XL1.0_juggernautXL_juggXIByRundiffusion.safetensors` (from `12a - Faceswap_instantID.json`)
- `XL1..5_epicrealismXL_v8Kiss.safetensors` (from `16 - Influencer.json`)
- `Flux1DevFp8_v10.safetensors` (from `17 - workflow_flux_standar.json`)
- `Flux1DevFp8_v10.safetensors` (from `18 - Florens_i2i.json`)
- `FLUX.1-dev-Controlnet-Union.safetensors` (from `20 - ControlNet_Cany_Depth_HED.json`)
- `depth_anything_vitl14.pth` (from `20 - ControlNet_Cany_Depth_HED.json`)
- `flux-canny-controlnet-v3.safetensors` (from `20 - ControlNet_Cany_Depth_HED.json`)
- `SD15_analogMadness_v70.safetensors` (from `21 - 3D_Render_Completo.json`)
- `depth_anything_vits14.pth` (from `21 - 3D_Render_Completo.json`)
- `depth_anything_vits14.pth` (from `21 - ComfyUI - Render de Stilos.json`)
- `depth_anything_vits14.pth` (from `21 - ComfyUI - Render de Stilos__677be3b6.json`)
- `Flux1DevFp8_v10.safetensors` (from `22 - Batch_Prompts_Florence2.json`)
- `4x_NMKD-Siax_200k.pth` (from `23 - Inpainting_Upscaler_FLUX.json`)
- `Flux1DevFp8_v10.safetensors` (from `23 - Inpainting_Upscaler_FLUX.json`)
- `v1-5-pruned-emaonly.safetensors` (from `32 - ComfyUI Colorize Photos-Final.json`)
- `flux\catviton.safetensors` (from `34 - ComfyUI - Cambio_Ropa_FLUX.json`)
- `pixelwave_flux1Dev03.safetensors` (from `35 - ComfyUI - Cambio de Fondo.json`)
- `XL1.0_juggernautXL_juggXIByRundiffusion.safetensors` (from `37b_BODYSWAP 2_2.json`)
- `controlnet-union-sdxl-1.0.safetensors` (from `37b_BODYSWAP 2_2.json`)
- `FLUX.1-dev-Controlnet-Union.safetensors` (from `37_BODYSWAP 2_GUFF_2.json`)
- `FLUX.1-dev-Controlnet-Union.safetensors` (from `37_BODYSWAP 2_GUFF_2_desordenado_modificado.json`)
- `XL1..5_epicrealismXL_v8Kiss.safetensors` (from `3_ComfyUI_tableDiffusion_Standar_2_KSamplers.json`)
- `pulid_flux_v0.9.1.safetensors` (from `41_ComfyUI_PULID (1 Cara).json`)
- `pulid_flux_v0.9.1.safetensors` (from `41_ComfyUI_PULID (2 caras).json`)
- `[Tutorial](https://docs.comfy.org/tutorials/image/qwen/qwen-image-edit)


## Model links

You can find all the models on [Comfy-Org/Qwen-Image_ComfyUI](https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/tree/main) and  [Comfy-Org/Qwen-Image-Edit_ComfyUI](https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI) 

**Diffusion model**

- [qwen_image_edit_2509_fp8_e4m3fn.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_edit_2509_fp8_e4m3fn.safetensors)

**LoRA**

- [Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors](https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Edit-2509/Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors)

**Text encoder**

- [qwen_2.5_vl_7b_fp8_scaled.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors)

**VAE**

- [qwen_image_vae.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors)

Model Storage Location

```
📂 ComfyUI/
├── 📂 models/
│   ├── 📂 diffusion_models/
│   │   └── qwen_image_edit_2509_fp8_e4m3fn.safetensors
│   ├── 📂 loras/
│   │   └── Qwen-Image-Lightning-4steps-V1.0.safetensors
│   ├── 📂 vae/
│   │   └── qwen_image_vae.safetensors
│   └── 📂 text_encoders/
│       └── qwen_2.5_vl_7b_fp8_scaled.safetensors
```

## Report issue
If you have any problems running this workflow, please report template-related issues via this link: [report the template issue here](https://github.com/Comfy-Org/workflow_templates/issues)` (from `63relightingQwen.json`)
- `qwen-edit-2509-multi-angle-lighting.safetensors` (from `63relightingQwen.json`)
- `[Tutorial](https://docs.comfy.org/tutorials/image/qwen/qwen-image-edit)


## Model links

You can find all the models on [Comfy-Org/Qwen-Image_ComfyUI](https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/tree/main) and  [Comfy-Org/Qwen-Image-Edit_ComfyUI](https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI) 

**Diffusion model**

- [qwen_image_edit_2509_fp8_e4m3fn.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_edit_2509_fp8_e4m3fn.safetensors)

**LoRA**

- [Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors](https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Edit-2509/Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors)

**Text encoder**

- [qwen_2.5_vl_7b_fp8_scaled.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors)

**VAE**

- [qwen_image_vae.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors)

Model Storage Location

```
📂 ComfyUI/
├── 📂 models/
│   ├── 📂 diffusion_models/
│   │   └── qwen_image_edit_2509_fp8_e4m3fn.safetensors
│   ├── 📂 loras/
│   │   └── Qwen-Image-Lightning-4steps-V1.0.safetensors
│   ├── 📂 vae/
│   │   └── qwen_image_vae.safetensors
│   └── 📂 text_encoders/
│       └── qwen_2.5_vl_7b_fp8_scaled.safetensors
```

## Report issue
If you have any problems running this workflow, please report template-related issues via this link: [report the template issue here](https://github.com/Comfy-Org/workflow_templates/issues)` (from `63relightingQwen_B.json`)
- `qwen-edit-2509-multi-angle-lighting.safetensors` (from `63relightingQwen_B.json`)
- `extract-outfit_v3.safetensors` (from `65_qwen_image_edit_outfit_transfer_Tecnolitas.json`)
- `Juggernaut_X_RunDiffusion.safetensors` (from `7a - ComfyUI Máscaras en Profundidad_RGB.json`)
- `Juggernaut_X_RunDiffusion.safetensors` (from `7b - ComfyUI Máscaras en Profundidad_Cambio_Objetos y mas.json`)
- `XL1..5_epicrealismXL_v8Kiss.safetensors` (from `9 - ComfyUI ControlNet - Procesamiento de imágenes.json`)
- `depth_anything_vitl14.pth` (from `9 - ComfyUI ControlNet - Procesamiento de imágenes.json`)
- `z_image_turbo_fp8_e4m3fn.safetensors` (from `AcademiaSD_Z-Image_v05.json`)
- `bad-picture-chill-75v.pt` (from `change-clothes.json`)
- `control_v11p_sd15_openpose_fp16.safetensors` (from `change-clothes.json`)
- `picxReal_10.safetensors` (from `change-clothes.json`)
- `SDXL/SDXL_base_1.0.safetensors` (from `comfyui_unreal_textures.json`)
- `clip/clip_sdxl.safetensors` (from `comfyui_unreal_textures.json`)
- `Flux1DevFp8_v10.safetensors` (from `Comprobar_LoRAs_Flux.json`)
- `Xap1flux.safetensors` (from `Comprobar_LoRAs_Flux.json`)
- `flux.1-lite-8B-alpha.safetensors` (from `control-flux-image-visualization.json`)
- `DJZmerger\cosRealJuggXL-hermit.safetensors` (from `cosTrio-Tpose-Factory-v12.json`)
- `DJZmerger\realvis_juggernaut_hermite.safetensors` (from `cosTrio-Tpose-Factory-v12.json`)
- `XL\OpenPoseXL2.safetensors` (from `cosTrio-Tpose-Factory-v12.json`)
- `civit\Thorra_SDXL_public_r1.safetensors` (from `cosTrio-Tpose-Factory-v12.json`)
- `civit\nkh-horror.safetensors` (from `cosTrio-Tpose-Factory-v12.json`)
- `civit\not-the-true-world.safetensors` (from `cosTrio-Tpose-Factory-v12.json`)
- `civit\xjx_style.safetensors` (from `cosTrio-Tpose-Factory-v12.json`)
- `civit\yjy-microscopy.safetensors` (from `cosTrio-Tpose-Factory-v12.json`)
- `thorraV1.safetensors` (from `cosTrio-Tpose-Factory-v12.json`)
- `If you get an error in any of the nodes above make sure the files are in the correct directories.

See the top of the examples page for the links : https://comfyanonymous.github.io/ComfyUI_examples/flux/

flux1-dev.safetensors goes in: ComfyUI/models/unet/

t5xxl_fp16.safetensors and clip_l.safetensors go in: ComfyUI/models/clip/

ae.safetensors goes in: ComfyUI/models/vae/


Tip: You can set the weight_dtype above to one of the fp8 types if you have memory issues.` (from `creacion imagenes FLUX por Promt .json`)
- `base_10-10-07_zavychromaxl_b1.safetensors_0.png` (from `faceswapv2.json`)
- `4x_NMKD-Siax_200k.pth` (from `flux-flux-pulid-instantid-realistic-face-swap.json`)
- `dreamshaperXL_v21TurboDPMSDE.safetensors` (from `flux-flux-pulid-instantid-realistic-face-swap.json`)
- `pulid_flux_v0.9.0.safetensors` (from `flux-flux-pulid-instantid-realistic-face-swap.json`)
- `pulid_flux_v0.9.1.safetensors` (from `flux-redux-pulid-face-swap-clone-any-portrait-photography.json`)
- `sigclip_patch14-384.safetensors` (from `flux-redux-pulid-face-swap-clone-any-portrait-photography.json`)
- `Cr!stian.safetensors` (from `FluxLORA_Capitulo13.json`)
- `The checkpoint goes in ComfyUI/models/unet (not checkpoints)
Download the original weights here:
https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/flux1-dev.sft

Download the fp8 version for <24gb vram systems:
https://huggingface.co/Kijai/flux-fp8/blob/main/flux1-dev-fp8.safetensors

Text encoders go in ComfyUI/models/clip:
https://huggingface.co/comfyanonymous/flux_text_encoders/tree/main

VAE (ae.sft) goes in ComfyUI/models/vae:
https://huggingface.co/black-forest-labs/FLUX.1-schnell/blob/main/ae.sft

Download the fp8 t5xxl for degraded quality but less RAM use
Launch ComfyUI with "--lowvram" arg (in the .bat file) to offload text encoder to CPU.

I can confirm this runs on:
- RTX 3090 (24gb) 1.29s/it
- RTX 4070 (12gb) 85s/it
Both running the fp8 quantized version. The 4070 is very slow though.` (from `FluxRealLoraWorkflowjson.json`)
- `FLUX_CHECKPOINT.safetensors` (from `Hacer pelicula - copia.json`)
- `FLUX_CONTROLNET_CANNY.safetensors` (from `Hacer pelicula - copia.json`)
- `FLUX_CHECKPOINT.safetensors` (from `Hacer_pelicula_decorado_solo_controlnet.json`)
- `FLUX_CONTROLNET_CANNY.safetensors` (from `Hacer_pelicula_decorado_solo_controlnet.json`)
- `FLUX_CHECKPOINT.safetensors` (from `Hacer_pelicula_inpaint_solo.json`)
- `FLUX_CHECKPOINT.safetensors` (from `Hacer_pelicula_storyboard_solo.json`)
- `cardosAnime_v20.safetensors` (from `Hooks_Máscaras_para_LoRAs.json`)
- `pixel art.safetensors` (from `Hooks_Máscaras_para_LoRAs.json`)
- `cardosAnime_v20.safetensors` (from `Hooks_Máscaras_para_LoRAs_y_para_scheduler_combinado.json`)
- `pixel art.safetensors` (from `Hooks_Máscaras_para_LoRAs_y_para_scheduler_combinado.json`)
- `sd1_5\PixelArtRedmond15V-PixelArt-PIXARFK.safetensors` (from `Hooks_Máscaras_para_LoRAs_y_para_scheduler_combinado.json`)
- `dreamshaper_8.safetensors` (from `img2img-painting.json`)
- `RealVisXL V4.safetensors` (from `inpaint-outpaint-with-controlnet-union-sdxl.json`)
- `controlnet-union-sdxl-1.safetensors` (from `inpaint-outpaint-with-controlnet-union-sdxl.json`)
- `depth_anything_vitl14.pth` (from `Inpainting workflow for changing a specific object.json`)
- `juggernautXL_v9Rdphoto2Lightning.safetensors` (from `Inpainting workflow for changing a specific object.json`)
- `sdxl/AlbedoBaseXL.safetensors` (from `InstantID_basic.json`)
- `sdxl/AlbedoBaseXL.safetensors` (from `InstantID_depth.json`)
- `sdxl/AlbedoBaseXL.safetensors` (from `InstantID_IPAdapter.json`)
- `IPAdapter_image_encoder_sd15.safetensors` (from `instantid_monalisa.json`)
- `sdxl/AlbedoBaseXL.safetensors` (from `instantid_monalisa.json`)
- `sdxl/AlbedoBaseXL.safetensors` (from `InstantID_multi_id.json`)
- `sdxl/AlbedoBaseXL.safetensors` (from `InstantID_posed.json`)
- `cardosAnime_v20.safetensors` (from `LoRA_Como_Scheduler.json`)
- `pixel art.safetensors` (from `LoRA_Como_Scheduler.json`)
- `dreamshaper_8.safetensors` (from `magical-img2img-render.json`)
- `xap001.safetensors` (from `Multi_LoRA_Upscaled.json`)
- `1xDeNoise_realplksr_otf.safetensors` (from `NSFW SFW ACE Faceswap V1.0.json`)
- `1x_DeBLR.pth` (from `NSFW SFW ACE Faceswap V1.0.json`)
- `4x_foolhardy_Remacri.pth` (from `NSFW SFW ACE Faceswap V1.0.json`)
- `flux1-turbo.safetensors` (from `nunchaku-flux.1-dev.json`)
- `revAnimated_v122.safetensors` (from `Olivio EASY workflow.json`)
- `revAnimated_v122.safetensors` (from `Olivio Model Switch workflow.json`)
- `FormulaXL 2.0.safetensors` (from `prompt-composer-sdxl-turbo-workflow.json`)
- `sd_xl_turbo_1.0_fp16.safetensors` (from `prompt-composer-sdxl-turbo-workflow.json`)
- `clip_vision_vit_h.safetensors` (from `SB_Character_FLUX.json`)
- `clip_vision_vit_h.safetensors` (from `SB_Character_FLUX__76688531.json`)
- `clip_vision_g.safetensors` (from `SB_Character_SDXL.json`)
- `controlnet-openpose-sdxl-1.0.safetensors` (from `SB_Character_SDXL.json`)
- `sdxl_base_1.0.safetensors` (from `SB_Character_SDXL.json`)
- `4x_NMKD-Siax_200k.pth` (from `shermanvv_flux___pulid___in_context_lora__2k_out_per_image_comfyworkflows.json`)
- `FLUX/FLUX.1-schnell-dev-merged-fp8-4step.safetensors` (from `shermanvv_flux___pulid___in_context_lora__2k_out_per_image_comfyworkflows.json`)
- `FLUX/portrait-photography.safetensors` (from `shermanvv_flux___pulid___in_context_lora__2k_out_per_image_comfyworkflows.json`)
- `flux/Flux.1-dev-Controlnet-Upscaler.safetensors` (from `shermanvv_flux___pulid___in_context_lora__2k_out_per_image_comfyworkflows.json`)
- `pulid_flux_v0.9.0.safetensors` (from `shermanvv_flux___pulid___in_context_lora__2k_out_per_image_comfyworkflows.json`)
- `v1-5-pruned-emaonly.safetensors` (from `Standar_WorkFlow.json`)
- `sd3.5_large.safetensors` (from `sup3rmass1ve_sd3_5_large_with_searge_prompt_enhance_and_lora_and_upscale_comfyworkflows.json`)
- `DAT_x4.pth` (from `the_writer_nightmare___4_comfyworkflows.json`)
- `OpenPoseXL2.safetensors` (from `the_writer_nightmare___4_comfyworkflows.json`)
- `RMSDXL_Darkness_Cinema.safetensors` (from `the_writer_nightmare___4_comfyworkflows.json`)
- `add-detail-xl.safetensors` (from `the_writer_nightmare___4_comfyworkflows.json`)
- `ral-dissolve-sdxl.safetensors` (from `the_writer_nightmare___4_comfyworkflows.json`)
- `ral-mythcr-sdxl.safetensors` (from `the_writer_nightmare___4_comfyworkflows.json`)
- `zavychromaxl_v90.safetensors` (from `the_writer_nightmare___4_comfyworkflows.json`)
- `nier_anime_style_offset.safetensors` (from `using-loras.json`)
- `phoenixdressV.2-0000010.safetensors` (from `using-loras.json`)
- `promisedNeverland_offset.safetensors` (from `using-loras.json`)
- `sd3.5_large_fp8_scaled.safetensors` (from `V-1-SD.json`)
- `4x_foolhardy_Remacri.pth` (from `workflow-4x-quick-upscale-fyoo07TxBwG1JLuyKZHA-comfyuistudio-openart.ai.json`)
- `CinematicRedmond.safetensors` (from `workflow-accelerate-the-generation-speed-Cfi0e0ME28jHdXXDILE5-datou-openart.ai.json`)
- `animagine-xl-3.1.safetensors` (from `workflow-accelerate-the-generation-speed-Cfi0e0ME28jHdXXDILE5-datou-openart.ai.json`)
- `Qwen-Image-2512-Lightning-4steps-V1.0-bf16.safetensors` (from `workflow-comfyui-tutorial-major-update-for-qwen-image-2512-LehKKPn8aBJhwJ641mo7-cgpixel_ai_art-openart.ai__edb98335.json`)
- `FLUX\flux.1-controlnet-Upscaler.safetensors` (from `workflow-flux-controlnet-upscale-XsEKTG1cvnRXYdsPsQVc-cychenyue-openart.ai.json`)
- `Flux\Flux_Ultimator.safetensors` (from `workflow-flux-controlnet-upscale-XsEKTG1cvnRXYdsPsQVc-cychenyue-openart.ai.json`)
- `pulid_flux_v0.9.0.safetensors` (from `workflow-flux-pulid-face-swap-with-upscale-4NCT0bt7k471EXpTBlLi-chin_buzzing_26-openart.ai.json`)
- `4x_NMKD-Siax_200k.pth` (from `workflow-flux-your-ootd-flux-D6q01xaUd0AOf6A9OQym-jaylin-openart.ai.json`)
- `Flux手部稳定器.safetensors` (from `workflow-flux-your-ootd-flux-D6q01xaUd0AOf6A9OQym-jaylin-openart.ai.json`)
- `Flux洗图神器.safetensors` (from `workflow-flux-your-ootd-flux-D6q01xaUd0AOf6A9OQym-jaylin-openart.ai.json`)
- `depth_anything_vitl14.pth` (from `workflow-flux-your-ootd-flux-D6q01xaUd0AOf6A9OQym-jaylin-openart.ai.json`)
- `epicDiffusion_epicDiffusion11.safetensors` (from `workflow-lesson-6-model-switch-and-masking---comfy-academy-mVvngwUewT8Tfqs727YH-oliviosarikas-openart.ai.json`)
- `revAnimated_v122EOL.safetensors` (from `workflow-lesson-6-model-switch-and-masking---comfy-academy-mVvngwUewT8Tfqs727YH-oliviosarikas-openart.ai.json`)
- `Edit-Multiple-angles.safetensors` (from `workflow-qwen-image-edit-2509-multiple-perspectives-on-characters-selfless-dedication-i2FDdfiAdOU5g2ANtZaU-north_ai-openart.ai.json`)
- `Qwen-Image-Edit-2509_fp8_e4m3fn.safetensors` (from `workflow-qwen-image-edit-2509-multiple-perspectives-on-characters-selfless-dedication-i2FDdfiAdOU5g2ANtZaU-north_ai-openart.ai.json`)
- `Qwen-Image-Edit-Lightning-8steps-V1.0.safetensors` (from `workflow-qwen-image-edit-2509-multiple-perspectives-on-characters-selfless-dedication-i2FDdfiAdOU5g2ANtZaU-north_ai-openart.ai.json`)
- `flux\realistic\F.1高清摄影系列_HDR_v1.safetensors` (from `workflow-restore-old-and-damaged-photosflux-kontext-yXttxLAnquPMZ9feVI7g-datou-openart.ai.json`)
- `svdq-int4_r32-flux.1-kontext-dev.safetensors` (from `workflow-simple-clean-fast-nunchaku-kontext-lora-CSUdCgX2qoPsKYI5pz9f-ailab-openart.ai.json`)
- `control_v11f1p_sd15_depth.safetensors` (from `workflow_controlnet_cine_comfyui.json`)
- `salidas/controlnet_cine` (from `workflow_controlnet_cine_comfyui.json`)
- `sdxl_base_1.0.safetensors` (from `workflow_controlnet_cine_comfyui.json`)
- `7th_anime_v3_A-fp16.safetensors` (from `workflow_mbw.json`)
- `Basil_mix_fixed.safetensors` (from `workflow_mbw.json`)
- `kl-f8-anime2.ckpt` (from `workflow_mbw.json`)
- `7th_anime_v3_A-fp16.safetensors` (from `workflow_mbw_multi.json`)
- `Basil_mix_fixed.safetensors` (from `workflow_mbw_multi.json`)
- `kl-f8-anime2.ckpt` (from `workflow_mbw_multi.json`)
- `sd15_8gb_cine_scope` (from `workflow_sd15_8gb_cine_gtx1080.json`)
- `sd15_8gb_cine_scope_softedge` (from `workflow_sd15_8gb_cine_gtx1080.json`)
- `v1-5-pruned-emaonly.safetensors` (from `workflow_sd15_8gb_cine_gtx1080.json`)
- `1.5\control_v11f1e_sd15_tile.pth` (from `workflow_Tiled_Diffusion_Base.json`)
- `1.5\photon_v1.safetensors` (from `workflow_Tiled_Diffusion_Base.json`)
- `7th_anime_v3_A-fp16.safetensors` (from `workflow_xyz_model_clip.json`)
- `Basil_mix_fixed.safetensors` (from `workflow_xyz_model_clip.json`)
- `kl-f8-anime2.ckpt` (from `workflow_xyz_model_clip.json`)
- `7th_anime_v3_A-fp16.safetensors` (from `workflow_xyz_vae.json`)
- `kl-f8-anime2.ckpt` (from `workflow_xyz_vae.json`)
- `juggernautXL_juggXIByRundiffusion.safetensors` (from `z_studio_sketch_into_a_real_image_similar_to_the_reference_image__comfyworkflows.json`)
- `revAnimated_v122.safetensors` (from `02-film_interpolation.json`)
- `sd15\rev-arcane-realistic-Precision.FP16-no-ema-clip-fix.safetensors` (from `03-animation_builder-condition-lerp.json`)
- `revAnimated_v122.safetensors` (from `04-animation_builder-deforum.json`)
- `4x-ClearRealityV1.pth` (from `Academia_SD_Self-Forcing_VACE_I2V (1).json`)
- `Wan2.1-T2V-1.3B-Self-Forcing-DMD-VACE-FP8_e4m3fn.safetensors` (from `Academia_SD_Self-Forcing_VACE_I2V (1).json`)
- `rife47.pth` (from `Academia_SD_Self-Forcing_VACE_I2V (1).json`)
- `1.5control_v1p_sd15_qrcode_monster_v2.safetensors` (from `Animar_imagenes_audio_OK.json`)
- `AnimateLCM_sd15_t2v.ckpt` (from `Animar_imagenes_audio_OK.json`)
- `SD15_realisticComicBook_v10.safetensors` (from `Animar_imagenes_audio_OK.json`)
- `v3_sd15_adapter.ckpt` (from `Animar_imagenes_audio_OK.json`)
- `v3_sd15_sparsectrl_rgb.ckpt` (from `Animar_imagenes_audio_OK.json`)
- `anything_fp16.safetensors` (from `ComfyUI workflow animatediff+ipadapter.json`)
- `mdjrny-v4.ckpt` (from `ComfyUI workflow animatediff+ipadapter.json`)
- `v3_sd15_mm.ckpt` (from `ComfyUI workflow animatediff+ipadapter.json`)
- `4x_foolhardy_Remacri.pth` (from `easy-logo-animation.json`)
- `control_v11f1e_sd15_tile.pth` (from `easy-logo-animation.json`)
- `control_v11p_sd15_canny.pth` (from `easy-logo-animation.json`)
- `control_v11p_sd15_depth.pth` (from `easy-logo-animation.json`)
- `dreamshaper_8.safetensors` (from `easy-logo-animation.json`)
- `rife47.pth` (from `easy-logo-animation.json`)
- `v3_sd15_mm.ckpt` (from `easy-logo-animation.json`)
- `4xFaceUpSharpDAT.pth` (from `easy-video-faceswap.json`)
- `4x_NMKD-Siax_200k.pth` (from `easy-video-faceswap.json`)
- `rife47.pth` (from `easy-video-faceswap.json`)
- `4x_foolhardy_Remacri.pth` (from `Fast-hunyuan-30-fps-with-hd-upscaler-8K3Gp4BxCCXSsDh2BhKk.json`)
- `rife47.pth` (from `Fast-hunyuan-30-fps-with-hd-upscaler-8K3Gp4BxCCXSsDh2BhKk.json`)
- `Wan2_1-T2V-1_3B_fp8_e4m3fn.safetensors` (from `Generación_Vídeos_WAN_2.1.json`)
- `open-clip-xlm-roberta-large-vit-huge-14_visual_fp16.safetensors` (from `Generación_Vídeos_WAN_2.1.json`)
- `umt5-xxl-enc-fp8_e4m3fn.safetensors` (from `Generación_Vídeos_WAN_2.1.json`)
- `longcat\LongCat_TI2V_comfy_fp8_e4m3fn_scaled_KJ.safetensors` (from `LongCat_TI2V_example_01-1-1.json`)
- `n_wan_umt5-xxl_fp8_scaled.safetensors` (from `nsfw-prompt-skill-wan22-t2v-GbgACSHB2CYhDFXsEXTx-benjamin-openart.ai.json`)
- `red lingerie and black stockings.safetensors` (from `nsfw-prompt-skill-wan22-t2v-GbgACSHB2CYhDFXsEXTx-benjamin-openart.ai.json`)
- `svd_xt_1_1.safetensors` (from `Sonic_sincronización_audio-labios.json`)
- `unet.pth` (from `Sonic_sincronización_audio-labios.json`)
- `2024-05-06/23-36-25/good_body_movement_1/900_good_body_movement_1_r64_temporal_unet.safetensors` (from `steerable-motion_smooth-n-steady.json`)
- `2xHigurashi_v1_compact_270k.pth` (from `steerable-motion_smooth-n-steady.json`)
- `OpenPoseXL2.safetensors` (from `steerable-motion_smooth-n-steady.json`)
- `Realistic_Vision_V5.0.safetensors` (from `steerable-motion_smooth-n-steady.json`)
- `film_net_fp32.pt` (from `steerable-motion_smooth-n-steady.json`)
- `v3_sd15_mm.ckpt` (from `steerable-motion_smooth-n-steady.json`)
- `v3_sd15_sparsectrl_rgb.ckpt` (from `steerable-motion_smooth-n-steady.json`)
- `4x_foolhardy_Remacri.pth` (from `VIDEO 13 WF.json`)
- `AbsoluteReality_1.8.1_pruned.safetensors` (from `VIDEO 13 WF.json`)
- `AnimateLCM_sd15_t2v.ckpt` (from `VIDEO 13 WF.json`)
- `CogVideoX-Fun-V1.1-5b-InP-MPS.safetensors` (from `VIDEO 13 WF.json`)
- `animatediff\control_v1p_sd15_qrcode_monster.safetensors` (from `VIDEO 13 WF.json`)
- `clipvision-for-ip-adapter.safetensors` (from `VIDEO 13 WF.json`)
- `control_v11f1p_sd15_depth.safetensors` (from `VIDEO 13 WF.json`)
- `control_v11p_sd15_openpose.safetensors` (from `VIDEO 13 WF.json`)
- `dw-ll_ucoco_384_bs5.torchscript.pt` (from `VIDEO 13 WF.json`)
- `film_net_fp32.pt` (from `VIDEO 13 WF.json`)
- `hunyuan_video_t2v_720p_bf16.safetensors` (from `VIDEO 13 WF.json`)
- `lotus-depth-g-v2-0.safetensors` (from `VIDEO 13 WF.json`)
- `rife47.pth` (from `VIDEO 13 WF.json`)
- `svd_xt.safetensors` (from `VIDEO 13 WF.json`)
- `WanVideo\Wan2_1-T2V-1_3B_fp8_e4m3fn.safetensors` (from `wanvideo_vid2vid_example_01.json`)
- `dw-ll_ucoco_384_bs5.torchscript.pt` (from `workflow-free-digital-human-bcculjSnGEcDuGhoNhkd-discus_disastrous_37-openart.ai.json`)
- `yolox_l.torchscript.pt` (from `workflow-free-digital-human-bcculjSnGEcDuGhoNhkd-discus_disastrous_37-openart.ai.json`)
- `control_v11f1p_sd15_depth.pth` (from `workflow-inner-reflections-vid2vid-style-conversion-sd-15---ipadapter-batch-unfold-aHKgex49Qh2kYE2X78Oh-peccary_vivacious_97-openart.ai.json`)
- `temporaldiff-v1-animatediff.ckpt` (from `workflow-inner-reflections-vid2vid-style-conversion-sd-15---ipadapter-batch-unfold-aHKgex49Qh2kYE2X78Oh-peccary_vivacious_97-openart.ai.json`)
- `z1.5\Anime - expmixLine_v3.safetensors` (from `workflow-inner-reflections-vid2vid-style-conversion-sd-15---ipadapter-batch-unfold-aHKgex49Qh2kYE2X78Oh-peccary_vivacious_97-openart.ai.json`)
- `AnimateLCM_sd15_t2v.ckpt` (from `workflow-perfect-lip-sync-ai-face-animation-jEIRkxkIGvuC6Nwm69Uz-comfyuiblog-openart.ai.json`)
- `MimicMotionMergedUnet_1-1-fp16.safetensors` (from `workflow-perfect-lip-sync-ai-face-animation-jEIRkxkIGvuC6Nwm69Uz-comfyuiblog-openart.ai.json`)
- `control_v11f1p_sd15_depth_fp16.safetensors` (from `workflow-perfect-lip-sync-ai-face-animation-jEIRkxkIGvuC6Nwm69Uz-comfyuiblog-openart.ai.json`)
- `depth_anything_v2_vitl.pth` (from `workflow-perfect-lip-sync-ai-face-animation-jEIRkxkIGvuC6Nwm69Uz-comfyuiblog-openart.ai.json`)
- `juggernaut_reborn.safetensors` (from `workflow-perfect-lip-sync-ai-face-animation-jEIRkxkIGvuC6Nwm69Uz-comfyuiblog-openart.ai.json`)
- `rife47.pth` (from `workflow-perfect-lip-sync-ai-face-animation-jEIRkxkIGvuC6Nwm69Uz-comfyuiblog-openart.ai.json`)
- `add_detail.safetensors` (from `workflow-realistic-video-animatediff-v3-szroMANBgp98pkj6F67h-sergegreen-openart.ai.json`)
- `v3_sd15_adapter.ckpt` (from `workflow-realistic-video-animatediff-v3-szroMANBgp98pkj6F67h-sergegreen-openart.ai.json`)
- `v3_sd15_mm.ckpt` (from `workflow-realistic-video-animatediff-v3-szroMANBgp98pkj6F67h-sergegreen-openart.ai.json`)
- `seedvr2_ema_7b_sharp_fp16.safetensors` (from `workflow-remove-mosaic-repair-images-v1-368JqukDF5dwJ9fHOXja-foxinn-openart.ai.json`)
- `2x_NMKD-UpgifLiteV2_210k.pth` (from `workflow-simple-prompt-travel-animations.json`)
- `control_v11f1e_sd15_tile_fp16.safetensors` (from `workflow-simple-prompt-travel-animations.json`)
- `controlnet_inpaintDepthHandFp16.safetensors` (from `workflow-simple-prompt-travel-animations.json`)
- `film_net_fp32.pt` (from `workflow-simple-prompt-travel-animations.json`)
- `kawaiiRealisticAnime_r04.safetensors` (from `workflow-simple-prompt-travel-animations.json`)
- `perky_breasts1.safetensors` (from `workflow-simple-prompt-travel-animations.json`)
- `photon_v1.safetensors` (from `workflow-simple-prompt-travel-animations.json`)
- `rife47.pth` (from `workflow-simple-prompt-travel-animations.json`)
- `segm/PitHandDetailer-v1-seg.pt` (from `workflow-simple-prompt-travel-animations.json`)
- `v3_sd15_adapter.ckpt` (from `workflow-simple-prompt-travel-animations.json`)
- `v3_sd15_mm.ckpt` (from `workflow-simple-prompt-travel-animations.json`)
- `BounceHighWan2_2.safetensors` (from `workflow-strong-body-impact-super-v2-F9dMZ9JENnBTevO9H97d-sexygirl-openart.ai.json`)
- `smoothMixWan22I2V14B_i2vHigh.safetensors` (from `workflow-strong-body-impact-super-v2-F9dMZ9JENnBTevO9H97d-sexygirl-openart.ai.json`)
- `smoothMixWan22I2V14B_i2vLow.safetensors` (from `workflow-strong-body-impact-super-v2-F9dMZ9JENnBTevO9H97d-sexygirl-openart.ai.json`)
- `wan21NSFWClipVisionH_v10.safetensors` (from `workflow-strong-body-impact-super-v2-F9dMZ9JENnBTevO9H97d-sexygirl-openart.ai.json`)
- `wan22-f4c3spl4sh-100epoc-high-k3nk.safetensors` (from `workflow-strong-body-impact-super-v2-F9dMZ9JENnBTevO9H97d-sexygirl-openart.ai.json`)
- `wan22-f4c3spl4sh-154epoc-low-k3nk.safetensors` (from `workflow-strong-body-impact-super-v2-F9dMZ9JENnBTevO9H97d-sexygirl-openart.ai.json`)
- `v3_sd15_mm.ckpt` (from `1 - Basic Vid2Vid 1 ControlNet.json`)
- `z1.5\Anime - darkSushiMixMix_colorful.safetensors` (from `1 - Basic Vid2Vid 1 ControlNet.json`)
- `control_v11f1p_sd15_depth.pth` (from `2 - Vid2Vid Multi-ControlNet.json`)
- `control_v11p_sd15_openpose.pth` (from `2 - Vid2Vid Multi-ControlNet.json`)
- `dw-ll_ucoco_384_bs5.torchscript.pt` (from `2 - Vid2Vid Multi-ControlNet.json`)
- `v3_sd15_mm.ckpt` (from `2 - Vid2Vid Multi-ControlNet.json`)
- `z1.5\Anime - darkSushiMixMix_colorful.safetensors` (from `2 - Vid2Vid Multi-ControlNet.json`)
- `v3_sd15_mm.ckpt` (from `3 - Basic Txt2Vid.json`)
- `z1.5\Anime - darkSushiMixMix_colorful.safetensors` (from `3 - Basic Txt2Vid.json`)
- `v3_sd15_mm.ckpt` (from `4 - Vid2Vid with Prompt Scheduling.json`)
- `z1.5\Anime - darkSushiMixMix_colorful.safetensors` (from `4 - Vid2Vid with Prompt Scheduling.json`)
- `v3_sd15_mm.ckpt` (from `5 - Txt2Vid with Prompt Scheduling.json`)
- `z1.5\Anime - darkSushiMixMix_colorful.safetensors` (from `5 - Txt2Vid with Prompt Scheduling.json`)
- `svd_xt.safetensors` (from `comfyworkflows_e392cc0b_a776_4958_854f_adf51f785c2a.json`)
- `smoothMixWan22I2V14B_i2vHigh.safetensors` (from `workflow-svi-2-pro-automatic-prompt---video-extension-tJnPfu881Sp2HQ4CmtxW-north_ai-openart.ai.json`)
- `smoothMixWan22I2V14B_i2vLow.safetensors` (from `workflow-svi-2-pro-automatic-prompt---video-extension-tJnPfu881Sp2HQ4CmtxW-north_ai-openart.ai.json`)
- `Wan2_2-I2V-A14B-LOW_fp8_e4m3fn_scaled_KJ.safetensors` (from `workflow-wan22-14b-image-video-hd-version-XC06OMwupt9qC7euN61H-north_ai-openart.ai.json`)
- `Wan2.2-Fun-A14B-InP-LOW-HPS2.1_resized_dynamic_avg_rank_15_bf16.safetensors` (from `workflow-wan22-animate-swap-anythingauto-seg-Jk5WFuRDcpXWIlMLk7Ds-faborohacks-openart.ai.json`)
- `Wan21_Uni3C_controlnet_fp16.safetensors` (from `workflow-wan22-animate-swap-anythingauto-seg-Jk5WFuRDcpXWIlMLk7Ds-faborohacks-openart.ai.json`)
- `Wan22Animate/Wan2_2-Animate-14B_fp8_e5m2_scaled_KJ.safetensors` (from `workflow-wan22-animate-swap-anythingauto-seg-Jk5WFuRDcpXWIlMLk7Ds-faborohacks-openart.ai.json`)
- `dw-ll_ucoco_384_bs5.torchscript.pt` (from `workflow-wan22-animate-swap-anythingauto-seg-Jk5WFuRDcpXWIlMLk7Ds-faborohacks-openart.ai.json`)
- `yolox_l.torchscript.pt` (from `workflow-wan22-animate-swap-anythingauto-seg-Jk5WFuRDcpXWIlMLk7Ds-faborohacks-openart.ai.json`)
- `seedvr2_ema_7b_fp8_e4m3fn.safetensors` (from `workflow-wan2_2-video-clothes-try-onfun-vace-version-cpBoTySGoyLPwSZ9HCzj-faborohacks-openart.ai.json`)
- `depth_anything_v2_vitl.pth` (from `Roda-ReactiveDepth-V30.json`)
- `gimmvfi_r_arb_lpips_fp32.safetensors` (from `Roda-ReactScrub-GIMMSync-V30.json`)
- `[Tutorial](https://docs.comfy.org/tutorials/video/wan/wan2_2)


## Model links

**text_encoders**

- [umt5_xxl_fp8_e4m3fn_scaled.safetensors](https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors)

**loras**

- [wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors](https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors)
- [wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors](https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors)

**diffusion_models**

- [wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors](https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors)
- [wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors](https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors)

**vae**

- [wan_2.1_vae.safetensors](https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors)


Model Storage Location

```
📂 ComfyUI/
├── 📂 models/
│   ├── 📂 text_encoders/
│   │      └── umt5_xxl_fp8_e4m3fn_scaled.safetensors
│   ├── 📂 loras/
│   │      ├── wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors
│   │      └── wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors
│   ├── 📂 diffusion_models/
│   │      ├── wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors
│   │      └── wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors
│   └── 📂 vae/
│          └── wan_2.1_vae.safetensors
```

## Report issue

If you encounter any issues when running this workflow, [report template issue here](https://github.com/Comfy-Org/workflow_templates/issues)
` (from `05_Wan2.2 14B FLF2V (First+Last Frame to Video).json`)
- `## Model Links

**LTX-2 Model Weights**

- [ltx-2-19b-dev.safetensors](https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-19b-dev.safetensors)
- [ ltx-2-19b-distilled-lora-384.safetensors ](https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-19b-distilled-lora-384.safetensors)
- [ ltx-2-spatial-upscaler-x2-1.0.safetensors ](https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-spatial-upscaler-x2-1.0.safetensors)


**Text Encoder**
- [Google Gemma 3](https://huggingface.co/google/gemma-3-12b-it-qat-q4_0-unquantized)

Please download the entire folder - 

- Run: 
 1. cd models/text_encoders
 2. git clone https://huggingface.co/google/gemma-3-12b-it-qat-q4_0-unquantized

*Full documentation can be found [here](https://docs.ltx.video/open-source-model/integration-tools/comfy-ui#text-encoder)

**Sampler**

- [RES4LYF](https://github.com/ClownsharkBatwing/RES4LYF)



**Model Storage Location**

```
📂 ComfyUI/
├── 📂 models/
│   ├── 📂 text_encoders/
│   │      ├── gemma-3-12b-it-qat-q4_0-unquantized/model-00001-of-00005.safetensors
│   ├── 📂 checkpoints/
│   │      └── ltx-2-19b-dev.safetensors
│   ├── 📂 loras/
│   │      └── ltx-2-19b-distilled-lora-384.safetensors
│   ├── 📂 latent_upscale_models/ 
           └── ltx-2-spatial-upscaler-x2-1.0.safetensors
```

**Assets**
- [base model image](https://github.com/Lightricks/ComfyUI-LTXVideo/blob/master/example_workflows/assets/base%20model%20image.png)

## Report Issues
To report any issues when running this workflow, [go to GitHub](https://github.com/Lightricks/ComfyUI-LTXVideo/issues)
` (from `06_LTX-2  Image to Video.json`)
- `animatediff_sd15_t2v.safetensors` (from `Flujo_Profesional_ComfyUI.json`)
- `ipadapter_plus_face.safetensors` (from `Flujo_Profesional_ComfyUI.json`)
- `4x_NickelbackFS_72000_G.pth` (from `Lonecats ZIT All in one Ver 6.0.json`)
- `ZIT\gonzalomoZpop_v30AIO.safetensors` (from `Lonecats ZIT All in one Ver 6.0.json`)
- `bbox/Eyeful_v2-Paired.pt` (from `Lonecats ZIT All in one Ver 6.0.json`)
- `bbox/face_yolov8n_v2.pt` (from `Lonecats ZIT All in one Ver 6.0.json`)
- `XL1..5_epicrealismXL_v8Kiss.safetensors` (from `13 - Image2video.json`)
- `film_net_fp32.pt` (from `13 - Image2video.json`)
- `stableVideoDiffusion_v10.safetensors` (from `13 - Image2video.json`)
- `SD15_realisticComicBook_v10.safetensors` (from `13a - text2video.json`)
- `mm_sd_v14.ckpt` (from `13a - text2video.json`)
- `juggernautXL_v8Rundiffusion.safetensors` (from `13_Tuto_2_Tecnolitas.json`)
- `mm_sd_v14.ckpt` (from `13_Tuto_2_Tecnolitas.json`)
- `revAnimated_v122.safetensors` (from `13_Tuto_2_Tecnolitas.json`)
- `stableVideoDiffusion_v10.safetensors` (from `13_Tuto_2_Tecnolitas.json`)
- `juggernautXL_v8Rundiffusion.safetensors` (from `13_Tuto_Tecnolitas.json`)
- `stableVideoDiffusion_v10.safetensors` (from `13_Tuto_Tecnolitas.json`)
- `rife47.pth` (from `40_LTX_IMG2VID.json`)
- `open-clip-xlm-roberta-large-vit-huge-14_fp16.safetensors` (from `46_WANvideo-i2v-lines-v20.json`)
- `open-clip-xlm-roberta-large-vit-huge-14_fp16.safetensors` (from `46_WANvideo-t2v-lines-v10.json`)
- `WAN21\Wan_2.1_Fun_Control_1.3B.safetensors` (from `50-Wan2_1_control_tecnolitas.json`)
- `dw-ll_ucoco_384_bs5.torchscript.pt` (from `50-Wan2_1_control_tecnolitas.json`)
- `2   NSFW\frankenstein_v2.safetensors` (from `broctor_29b3eccb_685f_48bb_b9fb_8aecf2a91af2_comfyworkflows.json`)
- `GATOWSKY.pt` (from `broctor_29b3eccb_685f_48bb_b9fb_8aecf2a91af2_comfyworkflows.json`)
- `more_details.safetensors` (from `broctor_29b3eccb_685f_48bb_b9fb_8aecf2a91af2_comfyworkflows.json`)
- `nagatiti.safetensors` (from `broctor_29b3eccb_685f_48bb_b9fb_8aecf2a91af2_comfyworkflows.json`)
- `01推文二次元.safetensors` (from `comfyworkflows_66c20349_b2d9_4456_b12d_1c1e7273c1e8.json`)
- `control_v11f1e_sd15_tile.pth` (from `comfyworkflows_66c20349_b2d9_4456_b12d_1c1e7273c1e8.json`)
- `FLUX1devControlnetInpaintingBeta.safetensors` (from `COMPACT Flux Control-Net inpainting with batch.json`)
- `\.safetensors:[^ ]*` (from `COMPACT Flux Control-Net inpainting with batch.json`)
- `1.5_perfect hands.safetensors` (from `cwkc_merry_xmas_comfyworkflows.json`)
- `SDXL\DetailedEyes_V3.safetensors` (from `cwkc_merry_xmas_comfyworkflows.json`)
- `SDXL\SDXL_NSFW\imperfectXLTrueNSFW_v65.safetensors` (from `cwkc_merry_xmas_comfyworkflows.json`)
- `SDXL\add-detail-xl.safetensors` (from `cwkc_merry_xmas_comfyworkflows.json`)
- `SDXL\perfect hands 2.safetensors` (from `cwkc_merry_xmas_comfyworkflows.json`)
- `more_details.safetensors` (from `cwkc_merry_xmas_comfyworkflows.json`)
- `rife49.pth` (from `cwkc_merry_xmas_comfyworkflows.json`)
- `stableVideoDiffusion_img2vidXt.safetensors` (from `cwkc_merry_xmas_comfyworkflows.json`)
- `control_v11f1p_sd15_depth_fp16.safetensors` (from `friedtofu_499d1bbf_c2b6_404c_bc4d_e1eb74e09b8a_comfyworkflows.json`)
- `control_v11p_sd15_openpose.pth` (from `friedtofu_499d1bbf_c2b6_404c_bc4d_e1eb74e09b8a_comfyworkflows.json`)
- `OpenPoseXL2.safetensors` (from `jon_king_alien_dancer_comfyworkflows.json`)
- `sdxl/Alien/Aliens_AILF_SDXL.safetensors` (from `jon_king_alien_dancer_comfyworkflows.json`)
- `sdxl/MAY/SDXL_black_and_color_Sa_May.safetensors` (from `jon_king_alien_dancer_comfyworkflows.json`)
- `sdxl/NEW/zkeleton-sdxl.safetensors` (from `jon_king_alien_dancer_comfyworkflows.json`)
- `sdxl/morphxl_v10.safetensors` (from `jon_king_alien_dancer_comfyworkflows.json`)
- `LongCat_TI2V_comfy_fp8_e4m3fn_scaled_KJ.safetensors` (from `LongCat_TI2V_Paris_Girl_Street_Cafe.json`)
- `## Model Links

**LTX-2 Model Weights**

- [ltx-2-19b-dev.safetensors](https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-19b-dev.safetensors)
- [ ltx-2-19b-distilled-lora-384.safetensors ](https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-19b-distilled-lora-384.safetensors)
- [ ltx-2-spatial-upscaler-x2-1.0.safetensors ](https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-spatial-upscaler-x2-1.0.safetensors)


**Text Encoder**
- [Google Gemma 3](https://huggingface.co/google/gemma-3-12b-it-qat-q4_0-unquantized)

Please download the entire folder - 

- Run: 
 1. cd models/text_encoders
 2. git clone https://huggingface.co/google/gemma-3-12b-it-qat-q4_0-unquantized

*Full documentation can be found [here](https://docs.ltx.video/open-source-model/integration-tools/comfy-ui#text-encoder)

**Sampler**

- [RES4LYF](https://github.com/ClownsharkBatwing/RES4LYF)



**Model Storage Location**

```
📂 ComfyUI/
├── 📂 models/
│   ├── 📂 text_encoders/
│   │      ├── gemma-3-12b-it-qat-q4_0-unquantized/model-00001-of-00005.safetensors
│   ├── 📂 checkpoints/
│   │      └── ltx-2-19b-dev.safetensors
│   ├── 📂 loras/
│   │      └── ltx-2-19b-distilled-lora-384.safetensors
│   ├── 📂 latent_upscale_models/ 
           └── ltx-2-spatial-upscaler-x2-1.0.safetensors
```

**Assets**
- [base model image](https://github.com/Lightricks/ComfyUI-LTXVideo/blob/master/example_workflows/assets/base%20model%20image.png)

## Report Issues
To report any issues when running this workflow, [go to GitHub](https://github.com/Lightricks/ComfyUI-LTXVideo/issues)
` (from `LTX-2_I2V_Full_wLora.json`)
- `## Model Links

**LTX-2 Model Weights**

- [ltx-2-19b-distilled.safetensors](https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-19b-distilled.safetensors)
- [ ltx-2-spatial-upscaler-x2-1.0.safetensors ](https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-spatial-upscaler-x2-1.0.safetensors)
- [ IC LoRA - Canny ](https://huggingface.co/Lightricks/LTX-2-19b-IC-LoRA-Canny-Control/resolve/main/ltx-2-19b-ic-lora-canny-control.safetensors)
- [ IC LoRA - Depth ](https://huggingface.co/Lightricks/LTX-2-19b-IC-LoRA-Depth-Control/resolve/main/ltx-2-19b-ic-lora-depth-control.safetensors)
- [ IC LoRA - Pose ](https://huggingface.co/Lightricks/LTX-2-19b-IC-LoRA-Pose-Control/resolve/main/ltx-2-19b-ic-lora-pose-control.safetensors)



**Text Encoder**
- [Google Gemma 3](https://huggingface.co/google/gemma-3-12b-it-qat-q4_0-unquantized)

Please download the entire folder - 

- Run: 
 1. cd models/text_encoders
 2. git clone https://huggingface.co/google/gemma-3-12b-it-qat-q4_0-unquantized

*Full documentation can be found [here](https://docs.ltx.video/open-source-model/integration-tools/comfy-ui#text-encoder)


**Model Storage Location**

```
📂 ComfyUI/
├── 📂 models/
│   ├── 📂 text_encoders/
│   │      ├── gemma-3-12b-it-qat-q4_0-unquantized/model-00001-of-00005.safetensors
│   ├── 📂 checkpoints/
│   │      └── ltx-2-19b-distilled.safetensors
│   ├── 📂 latent_upscale_models/ 
│   │      └── ltx-2-spatial-upscaler-x2-1.0.safetensors
│   ├── 📂 loras/ 
│           └── ltx-2-19b-ic-lora-canny-control.safetensors
│           └── ltx-2-19b-ic-lora-depth-control.safetensors
│           └── ltx-2-19b-ic-lora-pose-control.safetensors
```
**Assets**
- [buildings.mp4 (input video)](https://github.com/Lightricks/ComfyUI-LTXVideo/blob/master/example_workflows/assets/buildings.mp4)
- [buildings ff (first frame)](https://github.com/Lightricks/ComfyUI-LTXVideo/blob/master/example_workflows/assets/buildings%20ff.png)

## Report Issues
To report any issues when running this workflow, [go to GitHub](https://github.com/Lightricks/ComfyUI-LTXVideo/issues)
` (from `LTX-2_ICLoRA_All_Distilled.json`)
- `## Model Links

**LTX-2 Model Weights**

- [ltx-2-19b-dev.safetensors](https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-19b-dev.safetensors)
- [ ltx-2-19b-distilled-lora-384.safetensors ](https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-19b-distilled-lora-384.safetensors)
- [ ltx-2-spatial-upscaler-x2-1.0.safetensors ](https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-spatial-upscaler-x2-1.0.safetensors)


**Text Encoder**
- [Google Gemma 3](https://huggingface.co/google/gemma-3-12b-it-qat-q4_0-unquantized)

Please download the entire folder - 

- Run: 
 1. cd models/text_encoders
 2. git clone https://huggingface.co/google/gemma-3-12b-it-qat-q4_0-unquantized

*Full documentation can be found [here](https://docs.ltx.video/open-source-model/integration-tools/comfy-ui#text-encoder)

**Sampler**

- [RES4LYF](https://github.com/ClownsharkBatwing/RES4LYF)


**Model Storage Location**

```
📂 ComfyUI/
├── 📂 models/
│   ├── 📂 text_encoders/
│   │      ├── gemma-3-12b-it-qat-q4_0-unquantized/model-00001-of-00005.safetensors
│   ├── 📂 checkpoints/
│   │      └── ltx-2-19b-dev.safetensors
│   ├── 📂 loras/
│   │      └── ltx-2-19b-distilled-lora-384.safetensors
│   ├── 📂 latent_upscale_models/ 
           └── ltx-2-spatial-upscaler-x2-1.0.safetensors
```

## Report Issues
To report any issues when running this workflow, [go to GitHub](https://github.com/Lightricks/ComfyUI-LTXVideo/issues)
` (from `LTX-2_T2V_Full_wLora.json`)
- `## Model Links

**LTX-2 Model Weights**

- [ltx-2-19b-dev.safetensors](https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-19b-dev.safetensors)
- [ltx-2-19b-ic-lora-detailer.safetensors](https://huggingface.co/Lightricks/LTX-2-19b-IC-LoRA-Detailer/resolve/main/ltx-2-19b-ic-lora-detailer.safetensors)

**Text Encoder**
- [Google Gemma 3](https://huggingface.co/google/gemma-3-12b-it-qat-q4_0-unquantized)

Please download the entire folder - 

- Run: 
 1. cd models/text_encoders
 2. git clone https://huggingface.co/google/gemma-3-12b-it-qat-q4_0-unquantized

*Full documentation can be found [here](https://docs.ltx.video/open-source-model/integration-tools/comfy-ui#text-encoder)

**Model Storage Location**

```
📂 ComfyUI/
├── 📂 models/
│   ├── 📂 text_encoders/
│   │      ├── gemma-3-12b-it-qat-q4_0-unquantized/model-00001-of-00005.safetensors
│   ├── 📂 checkpoints/
│   │      └── ltx-2-19b-dev.safetensors
│   ├── 📂 loras/
│   │      ├── ltx-2-19b-ic-lora-detailer.safetensors

```

## Report Issues
To report any issues when running this workflow, [go to GitHub](https://github.com/Lightricks/ComfyUI-LTXVideo/issues)
` (from `LTX-2_V2V_Detailer.json`)
- `seedvr2_ema_7b_sharp_fp16.safetensors` (from `SeedVR2_4K_image_upscale.json`)
- `
## Model links

You can find the step distilled model weight here: [kandinsky-50-video-lite](https://huggingface.co/collections/kandinskylab/kandinsky-50-video-lite)

**text_encoders**

- [qwen_2.5_vl_7b_fp8_scaled.safetensors](https://huggingface.co/Comfy-Org/HunyuanVideo_1.5_repackaged/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors)
- [clip_l.safetensors](https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors?download=true)

**diffusion_models**

- [kandinsky5lite_t2v_sft_5s.safetensors](https://huggingface.co/kandinskylab/Kandinsky-5.0-T2V-Lite-sft-5s/resolve/main/model/kandinsky5lite_t2v_sft_5s.safetensors)

**vae**

- [hunyuan_video_vae_bf16.safetensors](https://huggingface.co/Kijai/HunyuanVideo_comfy/resolve/main/hunyuan_video_vae_bf16.safetensors)


Model Storage Location

```
📂 ComfyUI/
├── 📂 models/
│   ├── 📂 text_encoders/
│   │      ├── qwen_2.5_vl_7b_fp8_scaled.safetensors
│   │      └── clip_l.safetensors
│   ├── 📂 diffusion_models/
│   │      └── kandinsky5lite_t2v_sft_5s.safetensors
│   └── 📂 vae/
│          └── hunyuan_video_vae_bf16.safetensors
```

## Report issue

If you found any issues when running this workflow, [report template issue here](https://github.com/Comfy-Org/workflow_templates/issues)
` (from `video_kandinsky5_t2v.json`)
- `- Huggingface: [Lightricks/LTX-2](https://huggingface.co/Lightricks/LTX-2)
- Github: [LTX-2](https://github.com/Lightricks/LTX-2)

## LTX-2 Prompting Tips

1. **Core Actions**: Describe events and actions as they occur over time  
2. **Visual Details**: Describe all visual details you want to appear in the video  
3. **Audio**: Describe sounds and dialogue needed for the scene

## Report LTX-2 Issues
To report any issues when running this workflow, [go to GitHub](https://github.com/Lightricks/ComfyUI-LTXVideo/issues)

## Model links (for local users)

**checkpoints**
- [ltx-2-19b-dev.safetensors](https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-19b-dev.safetensors)
- [ltx-2-19b-dev-fp8.safetensors](https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-19b-dev-fp8.safetensors)

**text_encoders**

- [gemma_3_12B_it_fp4_mixed.safetensors](https://huggingface.co/Comfy-Org/ltx-2/resolve/main/split_files/text_encoders/gemma_3_12B_it_fp4_mixed.safetensors)

**loras**

- [ltx-2-19b-distilled-lora-384.safetensors](https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-19b-distilled-lora-384.safetensors)
- [ltx-2-19b-lora-camera-control-dolly-left.safetensors](https://huggingface.co/Lightricks/LTX-2-19b-LoRA-Camera-Control-Dolly-Left/resolve/main/ltx-2-19b-lora-camera-control-dolly-left.safetensors)

**latent_upscale_models**

- [ltx-2-spatial-upscaler-x2-1.0.safetensors](https://huggingface.co/Lightricks/LTX-2/resolve/main/ltx-2-spatial-upscaler-x2-1.0.safetensors)


Model Storage Location

```
📂 ComfyUI/
├── 📂 models/
│   ├── 📂 checkpoints/
│   │      ├── ltx-2-19b-dev.safetensors
│   │      └── ltx-2-19b-dev-fp8.safetensors
│   ├── 📂 text_encoders/
│   │      └── gemma_3_12B_it_fp4_mixed.safetensors
│   ├── 📂 loras/
│   │      ├── ltx-2-19b-distilled-lora-384.safetensors
│   │      └── ltx-2-19b-lora-camera-control-dolly-left.safetensors
│   └── 📂 latent_upscale_models/
│          └── ltx-2-spatial-upscaler-x2-1.0.safetensors
```


## Report other issues

Note: please update ComfyUI first ([guide](https://docs.comfy.org/zh-CN/installation/update_comfyui)) and prepare required models. Desktop/Cloud ship stable builds; nightly-supported models may not be included yet, please wait for the next stable release.

- Cannot run / runtime errors: [ComfyUI/issues](https://github.com/comfyanonymous/ComfyUI/issues)
- UI / frontend issues: [ComfyUI_frontend/issues](https://github.com/Comfy-Org/ComfyUI_frontend/issues)
- Workflow issues: [workflow_templates/issues](https://github.com/Comfy-Org/workflow_templates/issues)` (from `video_ltx2_t2v.json`)
- `rife47.pth` (from `wan2.2_14B_IMG2VID_FLF.json`)
- `rife47.pth` (from `Wan2.2_I2V_14B_Loop_v05.json`)
- `rife47.pth` (from `Wan2.2_I2V_14B_Loop_V3.json`)
- `rife47.pth` (from `Wan2.2_I2V_14B_V4.json`)
- `rife47.pth` (from `Wan2.2_I2V_14B_V5_Multilora.json`)
- `rife47.pth` (from `Wan2.2_I2V_14B_V7_Loop.json`)
- `4x-ClearRealityV1.pth` (from `wan2.2_T2V_14b_FLF_Upscaler.json`)
- `rife47.pth` (from `wan2.2_T2V_14b_FLF_Upscaler.json`)
- `rife47.pth` (from `wan2.2_T2V_14b_V7.json`)
- `rife47.pth` (from `wan2.2_T2V_14b_V8_multilora.json`)
- `Wan14B_RealismBoost.safetensors` (from `Wan22Animate_AcademiaSD_v24.json`)
- `dw-ll_ucoco_384_bs5.torchscript.pt` (from `Wan22Animate_AcademiaSD_v24.json`)
- `lightx2v_I2V_14B_480p_cfg_step_distill_rank128_bf16.safetensors` (from `Wan22Animate_AcademiaSD_v24.json`)
- `rife49.pth` (from `Wan22Animate_AcademiaSD_v24.json`)
- `yolox_l.torchscript.pt` (from `Wan22Animate_AcademiaSD_v24.json`)
- `rife47.pth` (from `Wan_FusionX_I2V_AcademiaSD_loops_v3.json`)
- `rife49.pth` (from `AcademiaSD_Hunyuan1.5_I2V_v03.json`)
- `4x-ClearRealityV1.pth` (from `AcademiaSD_Wan21_Vace_R2V.json`)
- `rife47.pth` (from `AcademiaSD_Wan21_Vace_R2V.json`)
- `rife47.pth` (from `ACADEMIA_SD WAN 2.2 IMG2VID LOOP VERSION, MULTILORA, SAGEATTENTION 2.2 AND FRAME INTERPOLATION.json`)
- `rife47.pth` (from `Wan_FusionX_I2V_AcademiaSD_V3.json`)
- `HoloCine\Wan2_2-T2V-A14B-LOW-HoloCine-full_fp8_e4m3fn_scaled_KJ.safetensors` (from `Wan_Holocine_AcademiaSD_v14.json`)
- `rife47.pth` (from `Wan_Holocine_AcademiaSD_v14.json`)
- `Technically_Color_Z_Image_Turbo_v1_renderartist_2000.safetensors` (from `64-z-image-turbo-colorfix.json`)
- `qwen3_4b_fp8_scaled.safetensors` (from `64-z-image-turbo-colorfix.json`)
- `4x-ClearRealityV1.pth` (from `Video_55_T2V_Self-Forcing.json`)
- `rife47.pth` (from `Video_55_T2V_Self-Forcing.json`)
- `self_forcing_dmd.pt` (from `Video_55_T2V_Self-Forcing.json`)
- `# 🚀 Z-Image-Turbo-AIO

## Ultra-Fast Photorealistic Generation!

✨ **8-Step Lightning Speed**
✨ **VAE + Text Encoder integrated**
✨ **Bilingual text rendering (EN/CN)**
✨ **No negative prompts needed**

---

## 🔄 Two Versions Available:

### 🟢 Z-Image-BF16-AIO (20 GB)
**Maximum Precision**
- Precision: BFloat16
- Steps: 8-10 (recommended: 8)
- CFG: 1.0 (keep at 1.0!)
- Sampler: res_multistep
- Scheduler: simple
- VRAM: 8GB works!

### 🟡 Z-Image-FP8-AIO (10 GB)
**Speed & Efficiency**
- Precision: FP8
- Steps: 8-10 (recommended: 8)
- CFG: 1.0 (keep at 1.0!)
- Sampler: res_multistep
- Scheduler: simple
- VRAM: 8GB perfect!

---

## ⚙️ Critical Settings

### Both Versions:
- Steps: 8
- CFG: 1.0 (don't change!)
- Sampler: res_multistep
- Scheduler: simple
- Resolution: 1920×1088 tested
- NO negative prompts

💡 Natural language prompts work best!

---

## 📥 Downloads

**Main Model (Pick ONE):**
- 🟢 Z-Image-BF16-AIO (20GB)
- 🟡 Z-Image-FP8-AIO (10GB)

**NO Lightning LoRAs Needed!**
Already optimized for 8-step generation.

---

## 📂 Installation

```
📂 ComfyUI/models/
└── 📂 checkpoints/
    └── z-image-turbo-fp8-aio.safetensors
```

No separate VAE/encoder needed!` (from `IMG-IMG--z-image-turbo-AIO-Upscaled-SeedVR2-workflow.json`)
- `seedvr2_ema_7b_sharp_fp16.safetensors` (from `IMG-IMG--z-image-turbo-AIO-Upscaled-SeedVR2-workflow.json`)
- `ILXL\xRicaMix_ILXL_v2.safetensors` (from `___2d_3d_comfyworkflows.json`)
- `- Guide: [Subgraph](https://docs.comfy.org/interface/features/subgraph)

## Model links

**text_encoders**

- [clip_l.safetensors](https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors)
- [t5xxl_fp16.safetensors](https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors)

**diffusion_models**

- [flux1-krea-dev_fp8_scaled.safetensors](https://huggingface.co/Comfy-Org/FLUX.1-Krea-dev_ComfyUI/resolve/main/split_files/diffusion_models/flux1-krea-dev_fp8_scaled.safetensors)

**vae**

- [ae.safetensors](https://huggingface.co/Comfy-Org/Lumina_Image_2.0_Repackaged/resolve/main/split_files/vae/ae.safetensors)


Model Storage Location

```
📂 ComfyUI/
├── 📂 models/
│   ├── 📂 text_encoders/
│   │      ├── clip_l.safetensors
│   │      └── t5xxl_fp16.safetensors
│   ├── 📂 diffusion_models/
│   │      └── flux1-krea-dev_fp8_scaled.safetensors
│   └── 📂 vae/
│          └── ae.safetensors
```

## Report issue

Note: please update ComfyUI first ([guide](https://docs.comfy.org/installation/update_comfyui)) and prepare required models. Desktop/Cloud will be updated after the stable release; nightly-supported models may not be included yet, please wait for the next stable release.

- Cannot run / runtime errors: [ComfyUI/issues](https://github.com/Comfy-Org/ComfyUI/issues)
- UI / frontend issues: [ComfyUI_frontend/issues](https://github.com/Comfy-Org/ComfyUI_frontend/issues)
- Workflow issues: [workflow_templates/issues](https://github.com/Comfy-Org/workflow_templates/issues)
` (from `flux1_krea_dev.json`)
- `Guide: [Subgraph](https://docs.comfy.org/interface/features/subgraph)

## Model Links (for Local Users)

**diffusion_models**

- [qwen_image_2512_fp8_e4m3fn.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_2512_fp8_e4m3fn.safetensors)

**text_encoders**

- [qwen_2.5_vl_7b_fp8_scaled.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors)

**vae**

- [qwen_image_vae.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors)

**loras**

- [Qwen-Image-2512-Lightning-4steps-V1.0-fp32.safetensors](https://huggingface.co/lightx2v/Qwen-Image-2512-Lightning/resolve/main/Qwen-Image-2512-Lightning-4steps-V1.0-fp32.safetensors)


## Model Storage Location

```
📂 ComfyUI/
├── 📂 models/
│   ├── 📂 diffusion_models/
│   │   └── qwen_image_2512_fp8_e4m3fn.safetensors
│   ├── 📂 text_encoders/
│   │   └── qwen_2.5_vl_7b_fp8_scaled.safetensors
│   ├── 📂 vae/
│   │   └── qwen_image_vae.safetensors
│   └── 📂 loras/
│       └── Qwen-Image-2512-Lightning-4steps-V1.0-fp32.safetensors
```

## Report Issue

Note: Please update ComfyUI first ([guide](https://docs.comfy.org/installation/update_comfyui)) and prepare required models. Desktop/Cloud will be updated after the stable release; nightly-supported models may not be included yet, please wait for the next stable release.

- Cannot run / runtime errors: [ComfyUI/issues](https://github.com/comfyanonymous/ComfyUI/issues)
- UI / frontend issues: [ComfyUI_frontend/issues](https://github.com/Comfy-Org/ComfyUI_frontend/issues)
- Workflow issues: [workflow_templates/issues](https://github.com/Comfy-Org/workflow_templates/issues)
` (from `image_qwen_Image_2512.json`)
- `dw-ll_ucoco_384_bs5.torchscript.pt` (from `LTX-2.3_ICLoRA_Union_Control_Distilled.json`)
- `Guide: [Subgraph](https://docs.comfy.org/interface/features/subgraph)

## Report issue

Note: please update ComfyUI first ([guide](https://docs.comfy.org/zh-CN/installation/update_comfyui)) and prepare required models. Desktop/Cloud ship stable builds; nightly-supported models may not be included yet, please wait for the next stable release.

- Cannot run / runtime errors: [ComfyUI/issues](https://github.com/comfyanonymous/ComfyUI/issues)
- UI / frontend issues: [ComfyUI_frontend/issues](https://github.com/Comfy-Org/ComfyUI_frontend/issues)
- Workflow issues: [workflow_templates/issues](https://github.com/Comfy-Org/workflow_templates/issues)


## Model links

**text_encoders**

- [qwen_2.5_vl_7b_fp8_scaled.safetensors](https://huggingface.co/Comfy-Org/HunyuanVideo_1.5_repackaged/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors)

**diffusion_models**

- [qwen_image_layered_bf16.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image-Layered_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_layered_bf16.safetensors)

**vae**

- [qwen_image_layered_vae.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image-Layered_ComfyUI/resolve/main/split_files/vae/qwen_image_layered_vae.safetensors)


Model Storage Location

```
📂 ComfyUI/
├── 📂 models/
│   ├── 📂 text_encoders/
│   │      └── qwen_2.5_vl_7b_fp8_scaled.safetensors
│   ├── 📂 diffusion_models/
│   │      └── qwen_image_layered_bf16.safetensors
│   └── 📂 vae/
│          └── qwen_image_layered_vae.safetensors
```

## FP8 

By default we are using bf16, it will require high VRAM, for fp8 please visit [qwen_image_layered_fp8mixed.safetensors](https://huggingface.co/Comfy-Org/Qwen-Image-Layered_ComfyUI/blob/main/split_files/diffusion_models/qwen_image_layered_fp8mixed.safetensors)

Then update the **Load Diffusion model** node inside the [Subgraph](https://docs.comfy.org/interface/features/subgraph) to use it.` (from `Qwen-image-layers_00003_.json`)
- `v1-5-pruned-emaonly-fp16.safetensors` (from `Unsaved Workflow.json`)
- `## Model Links (for Local Users)

**diffusion_models**

- [Wan2_1-I2V-14B-480p_fp8_e4m3fn_scaled_KJ.safetensors](https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/resolve/main/I2V/Wan2_1-I2V-14B-480p_fp8_e4m3fn_scaled_KJ.safetensors)

**text_encoders**

- [umt5_xxl_fp8_e4m3fn_scaled.safetensors](https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors)

**model_patches**

- [wan2.1_infiniteTalk_single_fp16.safetensors](https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/model_patches/wan2.1_infiniteTalk_single_fp16.safetensors)
- [wan2.1_infiniteTalk_multi_fp16.safetensors](https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/model_patches/wan2.1_infiniteTalk_multi_fp16.safetensors)

**audio_encoders**

- [wav2vec2-chinese-base_fp16.safetensors](https://huggingface.co/Kijai/wav2vec2_safetensors/resolve/main/wav2vec2-chinese-base_fp16.safetensors)

**vae**

- [Wan2_1_VAE_bf16.safetensors](https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Wan2_1_VAE_bf16.safetensors)

**loras**

- [lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors](https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Lightx2v/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors)


## Model Storage Location

```
📂 ComfyUI/
├── 📂 models/
│   ├── 📂 diffusion_models/
│   │   └─── Wan2_1-I2V-14B-480p_fp8_e4m3fn_scaled_KJ.safetensors
│   ├── 📂 text_encoders/
│   │   └─── umt5_xxl_fp8_e4m3fn_scaled.safetensors
│   ├── 📂 model_patches/
│   │   ├─── wan2.1_infiniteTalk_single_fp16.safetensors
│   │   └─── wan2.1_infiniteTalk_multi_fp16.safetensors
│   ├── 📂 audio_encoders/
│   │   └─── wav2vec2-chinese-base_fp16.safetensors
│   ├── 📂 vae/
│   │   └─── Wan2_1_VAE_bf16.safetensors
│   ├── 📂 loras/
│   │   └─── lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors
```

## Report Issue

Note: Please update ComfyUI first ([guide](https://docs.comfy.org/zh-CN/installation/update_comfyui)) and prepare required models. Desktop/Cloud ship stable builds; nightly-supported models may not be included yet, please wait for the next stable release.

- Cannot run / runtime errors: [ComfyUI/issues](https://github.com/comfyanonymous/ComfyUI/issues)
- UI / frontend issues: [ComfyUI_frontend/issues](https://github.com/Comfy-Org/ComfyUI_frontend/issues)
- Workflow issues: [workflow_templates/issues](https://github.com/Comfy-Org/workflow_templates/issues)
` (from `video_wan2_1_infinitetalk_doblaje.json`)
- `01_master/salon_master_clean` (from `01_master_clean_api.json`)
- `02_depth/salon_depth_final` (from `02_depth_pass_api.json`)
- `02_depth/salon_depth_raw` (from `02_depth_pass_api.json`)
- `depth_anything_v2_vitl.pth` (from `02_depth_pass_api.json`)
- `depth_anything_v2_vitl.pth` (from `02_depth_pass_workflow.json`)
- `depth_anything_v2_vitl.pth` (from `02_depth_pass_workflow_fixed.json`)
- `03_edges/salon_canny` (from `03_edges_pass_api.json`)
- `03_edges/salon_lineart` (from `03_edges_pass_api.json`)
- `03_edges/salon_softedge` (from `03_edges_pass_api.json`)
- `04_masks/mask_lamp` (from `04_masks_object_api.json`)
- `04_masks/mask_sofa` (from `04_masks_object_api.json`)
- `04_masks/mask_table` (from `04_masks_object_api.json`)
- `04_masks/mask_tv_cabinet` (from `04_masks_object_api.json`)
- `04_masks/mask_window` (from `04_masks_object_api.json`)
- `05_cleanplates/clean_no_sofa` (from `05_cleanplate_inpaint_api.json`)
- `control_v11p_sd15_canny.pth` (from `05_cleanplate_inpaint_api.json`)
- `06_refs_aux/salon_extension` (from `06_room_extension_api.json`)
- `Flux_iniverseMixXLSFWNSFW_flux1DNsfwFp8V10.safetensors` (from `19 - Flux_Inpainting.json`)
- `TU_CHECKPOINT_SD15.safetensors` (from `workflow_cine_sd15_estilizado_239.json`)
- `control_v11f1p_sd15_depth.safetensors` (from `workflow_cine_sd15_estilizado_239.json`)
- `control_v11p_sd15_canny.safetensors` (from `workflow_cine_sd15_estilizado_239.json`)
- `control_v11p_sd15_openpose.safetensors` (from `workflow_cine_sd15_estilizado_239.json`)
- `salidas/sd15_estilizado_cine_scope` (from `workflow_cine_sd15_estilizado_239.json`)
- `t2iadapter_light_sd15.pth` (from `workflow_cine_sd15_estilizado_239.json`)
- `TU_CHECKPOINT_SD15.safetensors` (from `workflow_cine_sd15_realista_239.json`)
- `control_v11f1p_sd15_depth.safetensors` (from `workflow_cine_sd15_realista_239.json`)
- `control_v11p_sd15_canny.safetensors` (from `workflow_cine_sd15_realista_239.json`)
- `control_v11p_sd15_openpose.safetensors` (from `workflow_cine_sd15_realista_239.json`)
- `salidas/sd15_realista_cine_scope` (from `workflow_cine_sd15_realista_239.json`)
- `t2iadapter_light_sd15.pth` (from `workflow_cine_sd15_realista_239.json`)
- `TU_CHECKPOINT_SDXL.safetensors` (from `workflow_cine_sdxl_estilizado_239.json`)
- `control_v11f1p_sd15_depth.safetensors` (from `workflow_cine_sdxl_estilizado_239.json`)
- `control_v11p_sd15_canny.safetensors` (from `workflow_cine_sdxl_estilizado_239.json`)
- `control_v11p_sd15_openpose.safetensors` (from `workflow_cine_sdxl_estilizado_239.json`)
- `salidas/sdxl_estilizado_cine_scope` (from `workflow_cine_sdxl_estilizado_239.json`)
- `t2iadapter_light_sd15.pth` (from `workflow_cine_sdxl_estilizado_239.json`)
- `TU_CHECKPOINT_SDXL.safetensors` (from `workflow_cine_sdxl_realista_239.json`)
- `control_v11f1p_sd15_depth.safetensors` (from `workflow_cine_sdxl_realista_239.json`)
- `control_v11p_sd15_canny.safetensors` (from `workflow_cine_sdxl_realista_239.json`)
- `control_v11p_sd15_openpose.safetensors` (from `workflow_cine_sdxl_realista_239.json`)
- `salidas/sdxl_realista_cine_scope` (from `workflow_cine_sdxl_realista_239.json`)
- `t2iadapter_light_sd15.pth` (from `workflow_cine_sdxl_realista_239.json`)
- `SRPO-fp8_e4m3fn.safetensors` (from `comfyui_SRPO-workflow-quantization-with-image-to-image.json`)
- `SDXL/SDXL_base_1.0.safetensors` (from `comfyui_unreal_postgrading.json`)
- `clip/clip_sdxl.safetensors` (from `comfyui_unreal_postgrading.json`)
- `SDXL/SDXL_base_1.0.safetensors` (from `comfyui_unreal_storyboard.json`)
- `clip/clip_sdxl.safetensors` (from `comfyui_unreal_storyboard.json`)
- `pixelwave_flux1Dev03.safetensors` (from `35 ComfyUI - Cambio de Fondo_fixed.json`)
- `Catviton.safetensors` (from `Advanced Flux Outfit Changer.json`)
- `base_10-10-07_zavychromaxl_b1.safetensors_0.png` (from `workflow_faceswap.json`)
- `Cr!stian.safetensors` (from `FluxLORA_Capitulo13.json`)
- `hidream_i1_fast_fp8.safetensors` (from `hidream_i1_fast_Capitulo17.json`)
- `Lyra-v6

- stable Audio 1.0
- txt 2 song (toggle)
- song 2 song (toggle)

video: https://www.youtube.com/watch?v=T9pys5OtDpc
workflow: https://civitai.com/models/579066


you will need:
https://huggingface.co/google-t5/t5-base/blob/main/model.safetensors
place inside /models/clip/ 
and rename "t5_base.safetensors"

https://huggingface.co/stabilityai/stable-audio-open-1.0/tree/main
place inside /models/checkpoints/stable-audio/
and rename "stable_audio_open_1.0.safetensors"` (from `Lyra-v6.json`)
- `stable-audio\stable_audio_open_1.0.safetensors` (from `Lyra-v6.json`)
- `t5_base.safetensors` (from `Lyra-v6.json`)
- `1xDeNoise_realplksr_otf.safetensors` (from `NSFW SFW ACE Faceswap V1.0.json`)
- `1x_DeBLR.pth` (from `NSFW SFW ACE Faceswap V1.0.json`)
- `4x_foolhardy_Remacri.pth` (from `NSFW SFW ACE Faceswap V1.0.json`)
- `qwen3_4b_fp8_scaled.safetensors` (from `z_image_turbo_Low_vram.json`)
- `qwen_image_canny_diffsynth_controlnet.safetensors` (from `image_qwen_image_controlnet_patch_Capitulo18.json`)
- `depth_anything_v2_vitl.pth` (from `Roda-ReactiveDepth-V30.json`)
- `gimmvfi_r_arb_lpips_fp32.safetensors` (from `Roda-ReactScrub-GIMMSync-V30.json`)
- `controlnet-union-sdxl-1.0.safetensors` (from `SKIN_FIX_Capitulo16.json`)
- `qwreal.safetensors` (from `SKIN_FIX_Capitulo16.json`)
- `SDXL/SDXL_base_1.0.safetensors` (from `comfyui_storyboard_animado.json`)
- `clip/clip_sdxl.safetensors` (from `comfyui_storyboard_animado.json`)
- `Cr!st!anKMIA.safetensors` (from `Hiresfix_Capitulo15.json`)
- `RealESR\4x-ESRGAN.pth` (from `Upscale_workflow_4x-ESRGAN_Capitulo15.json`)
- `wan2.2-anime.safetensors` (from `A_1080_a_2K_wan2.2_graph.json`)
- `dreamshaper_8.safetensors` (from `B 1080 a 2k flux.json`)
- `RESTO_CHECKPOINT.safetensors` (from `PASO_4_ComfyUI_RESTO_core_img2img_upscale.json`)
- `FILM_FLUX/SHOT` (from `prueba cine 2.json`)
- `FILM_WAN22/SEQ` (from `prueba cine wan.json`)
- `FILM_SHOT` (from `prueba cine.json`)
- `controlnet-canny-sdxl.safetensors` (from `prueba cine.json`)
- `sdxl_base_1.0.safetensors` (from `prueba cine.json`)
- `dreamshaper_8.safetensors` (from `prueba.json`)
- `wan_image_restore.safetensors` (from `restauracion_foto_base.json`)
- `wan_video_restore.safetensors` (from `restauracion_video_frames_base.json`)
- `Clip L.safetensors` (from `Wan Refine Flux.json`)
- `Fluxmania V6I_fp8.safetensors` (from `Wan Refine Flux.json`)
- `T5 fp16.safetensors` (from `Wan Refine Flux.json`)
- `wan_2.2.safetensors` (from `wan2.2 renstauracion fotos_V2.json`)
- `wan2.2_image_restoration_fp16.safetensors` (from `WAN_RESTO_FOTO_PASO_1.json`)
- `wan2.2_image_restoration_fp16.safetensors` (from `WAN_RESTO_VIDEO_PASO_2.json`)
- `Wan21-14B-SCAIL-preview_fp8_e4m3fn_scaled_KJ.safetensors` (from `WAN_SCAIL_workflow.json`)
- `cascade\stable_cascade_stage_b.safetensors` (from `2024-04-07 cascade+controlnet 完美放大图像.png`)
- `cascade\stable_cascade_stage_c.safetensors` (from `2024-04-07 cascade+controlnet 完美放大图像.png`)
- `cascade\super_resolution.safetensors` (from `2024-04-07 cascade+controlnet 完美放大图像.png`)
- `DJZmerger\cosRealJuggXL-hermit.safetensors` (from `Tpose-Template.png`)
- `DJZmerger\realvis_juggernaut_hermite.safetensors` (from `Tpose-Template.png`)
- `XL\OpenPoseXL2.safetensors` (from `Tpose-Template.png`)
- `civit\Thorra_SDXL_public_r1.safetensors` (from `Tpose-Template.png`)
- `civit\nkh-horror.safetensors` (from `Tpose-Template.png`)
- `civit\not-the-true-world.safetensors` (from `Tpose-Template.png`)
- `civit\xjx_style.safetensors` (from `Tpose-Template.png`)
- `civit\yjy-microscopy.safetensors` (from `Tpose-Template.png`)
- `johnsonV1.safetensors` (from `Tpose-Template.png`)
- `If you get an error in any of the nodes above make sure the files are in the correct directories.

See the top of the examples page for the links : https://comfyanonymous.github.io/ComfyUI_examples/flux/

flux1-schnell.safetensors goes in: ComfyUI/models/unet/

t5xxl_fp16.safetensors and clip_l.safetensors go in: ComfyUI/models/clip/

ae.safetensors goes in: ComfyUI/models/vae/


Tip: You can set the weight_dtype above to one of the fp8 types if you have memory issues.` (from `flux_schnell_example.png`)
- `4x-UltraMix_Balanced.pth` (from `sdxl-recommended-res-calc_upscale-case.png`)
- `SDXL\SSD-1B.safetensors` (from `sdxl-recommended-res-calc_upscale-case.png`)
- `flux\Flux_å°çº¢ä¹¦çå®é£æ ¼ä¸¨æ¥å¸¸ç§çä¸¨æè´é¼ç_V2.safetensors` (from `wave-speed-flux.png`)
- `Cosmos-1_0-Diffusion-7B-Text2World.safetensors` (from `2025-01-15 nvidia cosmos workflow.png`)
- `cosmos_cv8x8x8_1.0.safetensors` (from `2025-01-15 nvidia cosmos workflow.png`)
- `oldt5_xxl_fp8_e4m3fn_scaled.safetensors` (from `2025-01-15 nvidia cosmos workflow.png`)
- `# model links:

VAE, text_encoder:

[https://huggingface.co/Kijai/WanVideo_comfy](https://huggingface.co/Kijai/WanVideo_comfy)

fp8_scaled version:

[https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/blob/main/MoCha/Wan2_1_mocha-14B-preview_fp8_e4m3fn_scaled_KJ.safetensors](https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/blob/main/MoCha/Wan2_1_mocha-14B-preview_fp8_e4m3fn_scaled_KJ.safetensors)` (from `Mo-Cha-Replace-Anyone-in-a-Video.png`)
- `WanVideo/MoCha/Wan2_1_mocha-14B-preview_fp8_e4m3fn_scaled_KJ.safetensors` (from `Mo-Cha-Replace-Anyone-in-a-Video.png`)

## Custom Nodes per Instance

### :8188 — Image / Still (99 custom nodes)

- **ComfyMath** | git: https://github.com/evanspearman/ComfyMath | has requirements.txt
- **ComfyUI-AutoCropFaces** | git: https://github.com/liusida/ComfyUI-AutoCropFaces
- **ComfyUI-BRIA_AI-RMBG** | git: https://github.com/ZHO-ZHO-ZHO/ComfyUI-BRIA_AI-RMBG
- **ComfyUI-CatvtonFluxWrapper** | git: https://github.com/lujiazho/ComfyUI-CatvtonFluxWrapper
- **ComfyUI-Chat-GPT-Integration** | git: https://github.com/vienteck/ComfyUI-Chat-GPT-Integration
- **ComfyUI-Copilot** | git: https://github.com/AIDC-AI/ComfyUI-Copilot.git | has requirements.txt
- **ComfyUI-DepthAnythingV3** | has requirements.txt
- **ComfyUI-Dummy_Node_Pack** | git: https://github.com/FuryNocturn/ComfyUI-Dummy_Node_Pack
- **ComfyUI-EsesImageResize** | git: https://github.com/quasiblob/ComfyUI-EsesImageResize
- **ComfyUI-ExtendIPAdapterClipVision** | git: https://github.com/vahlok-alunmid/ComfyUI-ExtendIPAdapterClipVision
- **ComfyUI-GGUF** | has requirements.txt
- **ComfyUI-HQ-Image-Save** | git: https://github.com/spacepxl/ComfyUI-HQ-Image-Save | has requirements.txt
- **ComfyUI-IPAdapter-Flux** | git: https://github.com/Shakker-Labs/ComfyUI-IPAdapter-Flux | has requirements.txt
- **ComfyUI-Image-Filters** | git: https://github.com/spacepxl/ComfyUI-Image-Filters | has requirements.txt
- **ComfyUI-LTXVideo** | git: https://github.com/Lightricks/ComfyUI-LTXVideo | has requirements.txt
- **ComfyUI-Manager** | git: https://github.com/ltdrdata/ComfyUI-Manager.git | has requirements.txt
- **ComfyUI-MingNodes** | git: https://github.com/mingsky-ai/ComfyUI-MingNodes | has requirements.txt
- **ComfyUI-QwenImageLoraLoader**
- **ComfyUI-QwenVL** | has requirements.txt
- **ComfyUI-ReActor** | git: https://github.com/Gourieff/ComfyUI-ReActor | has requirements.txt
  *... and 79 more*

### :8189 — Video / Cine (69 custom nodes)

- **ComfyLiterals** | git: https://github.com/M1kep/ComfyLiterals
- **ComfyMath** | git: https://github.com/evanspearman/ComfyMath | has requirements.txt
- **ComfyUI-AnimateDiff-Evolved** | git: https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved
- **ComfyUI-Copilot** | git: https://github.com/AIDC-AI/ComfyUI-Copilot.git | has requirements.txt
- **ComfyUI-Frame-Interpolation** | git: https://github.com/Fannovel16/ComfyUI-Frame-Interpolation
- **ComfyUI-FramePackWrapper** | git: https://github.com/kijai/ComfyUI-FramePackWrapper.git | has requirements.txt
- **ComfyUI-GGUF** | has requirements.txt
- **ComfyUI-LTX13B-Blockswap** | git: https://github.com/Njbx/ComfyUI-LTX13B-Blockswap
- **ComfyUI-LTX2-R2V** | git: https://github.com/fangcun010/ComfyUI-LTX2-R2V
- **ComfyUI-LTX2-Visual-LoRA** | git: https://github.com/seanhan19911990-source/ComfyUI-LTX2-Visual-LoRA
- **ComfyUI-LTXVideo** | git: https://github.com/Lightricks/ComfyUI-LTXVideo | has requirements.txt
- **ComfyUI-LTXVideo-Extra** | git: https://github.com/domprosys/ComfyUI-LTXVideo-Extra
- **ComfyUI-Manager** | git: https://github.com/ltdrdata/ComfyUI-Manager.git | has requirements.txt
- **ComfyUI-MelBandRoFormer** | has requirements.txt
- **ComfyUI-MuseTalk_FSH** | git: https://github.com/AIFSH/ComfyUI-MuseTalk_FSH.git | has requirements.txt
- **ComfyUI-PainterLTXV2** | git: https://github.com/princepainter/ComfyUI-PainterLTXV2
- **ComfyUI-WanAnimatePreprocess** | has requirements.txt
- **ComfyUI-WanVideoWrapper** | has requirements.txt
- **ComfyUI_wav2lip** | git: https://github.com/ShmuelRonen/ComfyUI_wav2lip | has requirements.txt
- **Comfyui_segformer_b2_clothes** | git: https://github.com/StartHua/Comfyui_segformer_b2_clothes.git | has requirements.txt
  *... and 49 more*

### :8190 — Dubbing / Audio (37 custom nodes)

- **ComfyLiterals** | git: https://github.com/M1kep/ComfyLiterals
- **ComfyMath** | git: https://github.com/evanspearman/ComfyMath | has requirements.txt
- **ComfyUI-Copilot** | git: https://github.com/AIDC-AI/ComfyUI-Copilot.git | has requirements.txt
- **ComfyUI-F5-TTS** | git: https://github.com/niknah/ComfyUI-F5-TTS.git | has requirements.txt
- **ComfyUI-FishAudioS2** | git: https://github.com/Saganaki22/ComfyUI-FishAudioS2.git | has requirements.txt
- **ComfyUI-GGUF** | has requirements.txt
- **ComfyUI-MMAudio** | git: https://github.com/kijai/ComfyUI-MMAudio.git | has requirements.txt
- **ComfyUI-Manager** | git: https://github.com/ltdrdata/ComfyUI-Manager.git | has requirements.txt
- **ComfyUI-MelBandRoFormer** | git: https://github.com/kijai/ComfyUI-MelBandRoFormer | has requirements.txt
- **ComfyUI-OmniVoice-TTS** | git: https://github.com/Saganaki22/ComfyUI-OmniVoice-TTS.git | has requirements.txt
- **ComfyUI-Qwen3-TTS** | git: https://github.com/wanaigc/ComfyUI-Qwen3-TTS.git | has requirements.txt
- **ComfyUI-RVC_DISABLED** | git: https://github.com/AIFSH/ComfyUI-RVC.git | has requirements.txt
- **ComfyUI-WanVideoWrapper** | has requirements.txt
- **ComfyUI-Whisper** | git: https://github.com/yuvraj108c/ComfyUI-Whisper.git | has requirements.txt
- **ComfyUI-XTTS** | git: https://github.com/AIFSH/ComfyUI-XTTS.git | has requirements.txt
- **ComfyUI_Comfyroll_CustomNodes** | git: https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes
- **ComfyUI_MegaTTS3** | git: https://github.com/billwuhao/ComfyUI_MegaTTS3.git | has requirements.txt
- **ComfyUI_StepAudioTTS** | git: https://github.com/billwuhao/ComfyUI_StepAudioTTS.git | has requirements.txt
- **Comfyui_segformer_b2_clothes_DISABLED** | git: https://github.com/StartHua/Comfyui_segformer_b2_clothes.git | has requirements.txt
- **Crystools-MonitorOnly** | has requirements.txt
  *... and 17 more*

### :8191 — Restoration (101 custom nodes)

- **ComfyMath** | git: https://github.com/evanspearman/ComfyMath | has requirements.txt
- **ComfyUI-AutoCropFaces** | git: https://github.com/liusida/ComfyUI-AutoCropFaces
- **ComfyUI-BRIA_AI-RMBG** | git: https://github.com/ZHO-ZHO-ZHO/ComfyUI-BRIA_AI-RMBG
- **ComfyUI-CatvtonFluxWrapper** | git: https://github.com/lujiazho/ComfyUI-CatvtonFluxWrapper
- **ComfyUI-Chat-GPT-Integration** | git: https://github.com/vienteck/ComfyUI-Chat-GPT-Integration
- **ComfyUI-Copilot** | git: https://github.com/AIDC-AI/ComfyUI-Copilot.git | has requirements.txt
- **ComfyUI-DepthAnythingV3** | has requirements.txt
- **ComfyUI-Dummy_Node_Pack** | git: https://github.com/FuryNocturn/ComfyUI-Dummy_Node_Pack
- **ComfyUI-EsesImageResize** | git: https://github.com/quasiblob/ComfyUI-EsesImageResize
- **ComfyUI-ExtendIPAdapterClipVision** | git: https://github.com/vahlok-alunmid/ComfyUI-ExtendIPAdapterClipVision
- **ComfyUI-GGUF** | has requirements.txt
- **ComfyUI-HQ-Image-Save** | git: https://github.com/spacepxl/ComfyUI-HQ-Image-Save | has requirements.txt
- **ComfyUI-IPAdapter-Flux** | git: https://github.com/Shakker-Labs/ComfyUI-IPAdapter-Flux | has requirements.txt
- **ComfyUI-Image-Filters** | git: https://github.com/spacepxl/ComfyUI-Image-Filters | has requirements.txt
- **ComfyUI-LTXVideo** | git: https://github.com/Lightricks/ComfyUI-LTXVideo | has requirements.txt
- **ComfyUI-Manager** | git: https://github.com/ltdrdata/ComfyUI-Manager.git | has requirements.txt
- **ComfyUI-MingNodes** | git: https://github.com/mingsky-ai/ComfyUI-MingNodes | has requirements.txt
- **ComfyUI-QwenImageLoraLoader**
- **ComfyUI-QwenVL** | has requirements.txt
- **ComfyUI-ReActor** | git: https://github.com/Gourieff/ComfyUI-ReActor | has requirements.txt
  *... and 81 more*

### :8192 — 3D (1 custom nodes)

- **ComfyUI-3D-Pack** | git: https://github.com/MrForExample/ComfyUI-3D-Pack.git | has requirements.txt

### G: Hub Custom Nodes Repository

- **ComfyUI-Manager** | git: https://github.com/ltdrdata/ComfyUI-Manager.git
- **comfy-mtb**
- **comfyui-easy-use**
- **comfyui_controlnet_aux**
- **comfyui_essentials**
- **efficiency-nodes-comfyui**
- **rgthree-comfy**

## Key Workflow Details

### cinematic_storyboard_sdxl.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 6
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### storyboard_fast_sdxl.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 6
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### cinematic_storyboard_sdxl.template.json
- **Family:** image_still
- **Format:** api
- **Required nodes:** 6
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### storyboard_fast_sdxl.template.json
- **Family:** image_still
- **Format:** api
- **Required nodes:** 6
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### flux_cine_2.template.json
- **Family:** image_still
- **Format:** api
- **Required nodes:** 9
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### 01-faceswap.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 16
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: Reroute, Text box)
  - :8189: 8 missing (2 external: Reroute, Text box)
  - :8190: 9 missing (2 external: Reroute, Text box)
  - :8191: 2 missing (2 external: Reroute, Text box)
  - :8192: 9 missing (2 external: Reroute, Text box)

### 01a_Qwen-Image Distill.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 11
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: MarkdownNote, Note)
  - :8189: 2 missing (2 external: MarkdownNote, Note)
  - :8190: 2 missing (2 external: MarkdownNote, Note)
  - :8191: 2 missing (2 external: MarkdownNote, Note)
  - :8192: 2 missing (2 external: MarkdownNote, Note)

### 01a_Qwen-Image Distill“Character Bible”.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 3
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: MarkdownNote, e5cfe5ba-2ae0-4bc4-869f-ab2228cb44d3)
  - :8189: 2 missing (2 external: MarkdownNote, e5cfe5ba-2ae0-4bc4-869f-ab2228cb44d3)
  - :8190: 2 missing (2 external: MarkdownNote, e5cfe5ba-2ae0-4bc4-869f-ab2228cb44d3)
  - :8191: 2 missing (2 external: MarkdownNote, e5cfe5ba-2ae0-4bc4-869f-ab2228cb44d3)
  - :8192: 2 missing (2 external: MarkdownNote, e5cfe5ba-2ae0-4bc4-869f-ab2228cb44d3)

### 01_Qwen-Image (T2I).json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 3
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: MarkdownNote, e5cfe5ba-2ae0-4bc4-869f-ab2228cb44d3)
  - :8189: 2 missing (2 external: MarkdownNote, e5cfe5ba-2ae0-4bc4-869f-ab2228cb44d3)
  - :8190: 2 missing (2 external: MarkdownNote, e5cfe5ba-2ae0-4bc4-869f-ab2228cb44d3)
  - :8191: 2 missing (2 external: MarkdownNote, e5cfe5ba-2ae0-4bc4-869f-ab2228cb44d3)
  - :8192: 2 missing (2 external: MarkdownNote, e5cfe5ba-2ae0-4bc4-869f-ab2228cb44d3)

### 01_qwen_t2i_subgraphed_Capitulo18.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 3
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: 2c61139d-9c34-4c7e-a083-7a67cc4770ad, MarkdownNote)
  - :8189: 2 missing (2 external: 2c61139d-9c34-4c7e-a083-7a67cc4770ad, MarkdownNote)
  - :8190: 2 missing (2 external: 2c61139d-9c34-4c7e-a083-7a67cc4770ad, MarkdownNote)
  - :8191: 2 missing (2 external: 2c61139d-9c34-4c7e-a083-7a67cc4770ad, MarkdownNote)
  - :8192: 2 missing (2 external: 2c61139d-9c34-4c7e-a083-7a67cc4770ad, MarkdownNote)

### 02_FLUX_Base realista.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 3
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: MarkdownNote, fc11e656-d80a-42fa-ae56-c197af368516)
  - :8189: 2 missing (2 external: MarkdownNote, fc11e656-d80a-42fa-ae56-c197af368516)
  - :8190: 2 missing (2 external: MarkdownNote, fc11e656-d80a-42fa-ae56-c197af368516)
  - :8191: 2 missing (2 external: MarkdownNote, fc11e656-d80a-42fa-ae56-c197af368516)
  - :8192: 2 missing (2 external: MarkdownNote, fc11e656-d80a-42fa-ae56-c197af368516)

### 05-seamless_texture.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 12
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Reroute)
  - :8189: 5 missing (1 external: Reroute)
  - :8190: 5 missing (1 external: Reroute)
  - :8191: 1 missing (1 external: Reroute)
  - :8192: 5 missing (1 external: Reroute)

### 05_Wan2.2 14B FLF2V (First+Last Frame to Video).json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 16
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 2 missing
  - :8190: 2 missing
  - :8191: 0 missing
  - :8192: 2 missing

### 06-seamless_equilateral.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 15
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Geometry Sphere (mtb))
  - :8189: 5 missing (1 external: Geometry Sphere (mtb))
  - :8190: 7 missing (1 external: Geometry Sphere (mtb))
  - :8191: 1 missing (1 external: Geometry Sphere (mtb))
  - :8192: 7 missing (1 external: Geometry Sphere (mtb))

### 10_WF_ComfyUI_IP_Adapter_Plus_Integración_de_prompts_de_imagen_y.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 17
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: Note, UltimateSDUpscale)
  - :8189: 2 missing (2 external: Note, UltimateSDUpscale)
  - :8190: 5 missing (2 external: Note, UltimateSDUpscale)
  - :8191: 2 missing (2 external: Note, UltimateSDUpscale)
  - :8192: 5 missing (2 external: Note, UltimateSDUpscale)

### 11 - Reactor.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 1 missing
  - :8190: 1 missing
  - :8191: 0 missing
  - :8192: 1 missing

### 12 - Faceswap_instantID_IpAdapter.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 14
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 7 missing
  - :8190: 9 missing
  - :8191: 0 missing
  - :8192: 11 missing

### 12a - Faceswap_instantID.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 11
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 3 missing
  - :8190: 3 missing
  - :8191: 0 missing
  - :8192: 3 missing

### 14 - BGRM_Bria_Remover.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 4
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 2 missing
  - :8190: 2 missing
  - :8191: 0 missing
  - :8192: 2 missing

### 14a -.json
- **Family:** video_cine
- **Format:** api
- **Required nodes:** 4
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 2 missing
  - :8190: 2 missing
  - :8191: 0 missing
  - :8192: 2 missing

### 15a - workflow2.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 8
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 7 missing
  - :8190: 7 missing
  - :8191: 0 missing
  - :8192: 7 missing

### 16 - Influencer.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 27
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: Note, Reroute)
  - :8189: 13 missing (2 external: Note, Reroute)
  - :8190: 11 missing (2 external: Note, Reroute)
  - :8191: 2 missing (2 external: Note, Reroute)
  - :8192: 14 missing (2 external: Note, Reroute)

### 17 - workflow_flux_standar.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 13
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: RandomNoise //Inspire, Reroute)
  - :8189: 2 missing (2 external: RandomNoise //Inspire, Reroute)
  - :8190: 2 missing (2 external: RandomNoise //Inspire, Reroute)
  - :8191: 2 missing (2 external: RandomNoise //Inspire, Reroute)
  - :8192: 2 missing (2 external: RandomNoise //Inspire, Reroute)

### 18 - Florens_i2i.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 18
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 2 missing
  - :8190: 4 missing
  - :8191: 0 missing
  - :8192: 5 missing

### 18a - workflow_nf4.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: CheckpointLoaderNF4)
  - :8189: 1 missing (1 external: CheckpointLoaderNF4)
  - :8190: 1 missing (1 external: CheckpointLoaderNF4)
  - :8191: 1 missing (1 external: CheckpointLoaderNF4)
  - :8192: 1 missing (1 external: CheckpointLoaderNF4)

### 20 - ControlNet_Cany_Depth_HED.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 20
- **Best instance:** :8188 (missing 6)
  - :8188: 6 missing (6 external: ApplyFluxControlNet, InstantX Flux Union ControlNet Loader, LoadFluxControlNet, Note, Reroute)
  - :8189: 6 missing (6 external: ApplyFluxControlNet, InstantX Flux Union ControlNet Loader, LoadFluxControlNet, Note, Reroute)
  - :8190: 9 missing (6 external: ApplyFluxControlNet, InstantX Flux Union ControlNet Loader, LoadFluxControlNet, Note, Reroute)
  - :8191: 6 missing (6 external: ApplyFluxControlNet, InstantX Flux Union ControlNet Loader, LoadFluxControlNet, Note, Reroute)
  - :8192: 10 missing (6 external: ApplyFluxControlNet, InstantX Flux Union ControlNet Loader, LoadFluxControlNet, Note, Reroute)

### 21 - 3D_Render_Completo.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 21
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Reroute)
  - :8189: 1 missing (1 external: Reroute)
  - :8190: 10 missing (1 external: Reroute)
  - :8191: 1 missing (1 external: Reroute)
  - :8192: 10 missing (1 external: Reroute)

### 21 - ComfyUI - Render de Stilos.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 28
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: Note, Reroute)
  - :8189: 3 missing (2 external: Note, Reroute)
  - :8190: 12 missing (2 external: Note, Reroute)
  - :8191: 2 missing (2 external: Note, Reroute)
  - :8192: 12 missing (2 external: Note, Reroute)

### 21 - ComfyUI - Render de Stilos__677be3b6.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 28
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: Note, Reroute)
  - :8189: 3 missing (2 external: Note, Reroute)
  - :8190: 12 missing (2 external: Note, Reroute)
  - :8191: 2 missing (2 external: Note, Reroute)
  - :8192: 12 missing (2 external: Note, Reroute)

### 22 - Batch_Prompts_Florence2.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 16
- **Best instance:** :8188 (missing 4)
  - :8188: 4 missing (4 external: LoadImageListFromDir //Inspire, LoadPromptsFromFile //Inspire, SaveText, UnzipPrompt //Inspire)
  - :8189: 4 missing (4 external: LoadImageListFromDir //Inspire, LoadPromptsFromFile //Inspire, SaveText, UnzipPrompt //Inspire)
  - :8190: 6 missing (4 external: LoadImageListFromDir //Inspire, LoadPromptsFromFile //Inspire, SaveText, UnzipPrompt //Inspire)
  - :8191: 4 missing (4 external: LoadImageListFromDir //Inspire, LoadPromptsFromFile //Inspire, SaveText, UnzipPrompt //Inspire)
  - :8192: 6 missing (4 external: LoadImageListFromDir //Inspire, LoadPromptsFromFile //Inspire, SaveText, UnzipPrompt //Inspire)

### 23 - Inpainting_Upscaler_FLUX.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 26
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: Note, UltimateSDUpscale)
  - :8189: 3 missing (2 external: Note, UltimateSDUpscale)
  - :8190: 5 missing (2 external: Note, UltimateSDUpscale)
  - :8191: 2 missing (2 external: Note, UltimateSDUpscale)
  - :8192: 8 missing (2 external: Note, UltimateSDUpscale)

### 25 - ComfyUI FLUX - Composición.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 2 missing
  - :8190: 2 missing
  - :8191: 0 missing
  - :8192: 4 missing

### 29 - ComfyUI_FluxUpscaler.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 33
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: Note, Reroute)
  - :8189: 9 missing (2 external: Note, Reroute)
  - :8190: 9 missing (2 external: Note, Reroute)
  - :8191: 2 missing (2 external: Note, Reroute)
  - :8192: 12 missing (2 external: Note, Reroute)

### 32 - ComfyUI Colorize Photos-Final.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 17
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: BNK_Unsampler)
  - :8189: 2 missing (1 external: BNK_Unsampler)
  - :8190: 7 missing (1 external: BNK_Unsampler)
  - :8191: 1 missing (1 external: BNK_Unsampler)
  - :8192: 7 missing (1 external: BNK_Unsampler)

### 33 - ComfyUI - Flux_Redux_Combine Images.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 16
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: Note, PrimitiveNode)
  - :8189: 3 missing (2 external: Note, PrimitiveNode)
  - :8190: 3 missing (2 external: Note, PrimitiveNode)
  - :8191: 2 missing (2 external: Note, PrimitiveNode)
  - :8192: 5 missing (2 external: Note, PrimitiveNode)

### 34 - ComfyUI - Cambio_otras_FLUX.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 23
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 3 missing
  - :8190: 6 missing
  - :8191: 0 missing
  - :8192: 9 missing

### 34 - ComfyUI - Cambio_Ropa_FLUX.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 21
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 3 missing
  - :8190: 4 missing
  - :8191: 0 missing
  - :8192: 7 missing

### 34 - ComfyUI -FLUX Inpainting.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 11
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### 35 - ComfyUI - Cambio de Fondo.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 31
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: Fast Groups Bypasser (rgthree), GetNode, SetNode)
  - :8189: 6 missing (3 external: Fast Groups Bypasser (rgthree), GetNode, SetNode)
  - :8190: 11 missing (3 external: Fast Groups Bypasser (rgthree), GetNode, SetNode)
  - :8191: 3 missing (3 external: Fast Groups Bypasser (rgthree), GetNode, SetNode)
  - :8192: 13 missing (3 external: Fast Groups Bypasser (rgthree), GetNode, SetNode)

### 37b_BODYSWAP 2_2.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 19
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: InpaintResize, Load Styles CSV, Textbox)
  - :8189: 5 missing (3 external: InpaintResize, Load Styles CSV, Textbox)
  - :8190: 4 missing (3 external: InpaintResize, Load Styles CSV, Textbox)
  - :8191: 3 missing (3 external: InpaintResize, Load Styles CSV, Textbox)
  - :8192: 9 missing (3 external: InpaintResize, Load Styles CSV, Textbox)

### 37_BODYSWAP 2_GUFF_2.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 28
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: Load Styles CSV, Textbox)
  - :8189: 6 missing (2 external: Load Styles CSV, Textbox)
  - :8190: 4 missing (2 external: Load Styles CSV, Textbox)
  - :8191: 2 missing (2 external: Load Styles CSV, Textbox)
  - :8192: 11 missing (2 external: Load Styles CSV, Textbox)

### 37_BODYSWAP 2_GUFF_2_desordenado_modificado.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 31
- **Best instance:** :8188 (missing 4)
  - :8188: 4 missing (4 external: GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything), Load Styles CSV, Textbox)
  - :8189: 8 missing (4 external: GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything), Load Styles CSV, Textbox)
  - :8190: 6 missing (4 external: GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything), Load Styles CSV, Textbox)
  - :8191: 4 missing (4 external: GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything), Load Styles CSV, Textbox)
  - :8192: 14 missing (4 external: GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything), Load Styles CSV, Textbox)

### 3_ComfyUI_tableDiffusion_Standar_2_KSamplers.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 9
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: PrimitiveNode)
  - :8189: 1 missing (1 external: PrimitiveNode)
  - :8190: 1 missing (1 external: PrimitiveNode)
  - :8191: 1 missing (1 external: PrimitiveNode)
  - :8192: 1 missing (1 external: PrimitiveNode)

### 41_ComfyUI_PULID (1 Cara).json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 23
- **Best instance:** :8188 (missing 5)
  - :8188: 5 missing (5 external: ApplyPulidFlux, Load Styles CSV, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)
  - :8189: 6 missing (5 external: ApplyPulidFlux, Load Styles CSV, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)
  - :8190: 8 missing (5 external: ApplyPulidFlux, Load Styles CSV, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)
  - :8191: 5 missing (5 external: ApplyPulidFlux, Load Styles CSV, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)
  - :8192: 9 missing (5 external: ApplyPulidFlux, Load Styles CSV, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)

### 41_ComfyUI_PULID (2 caras).json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 26
- **Best instance:** :8188 (missing 6)
  - :8188: 6 missing (6 external: ApplyPulidFlux, Load Styles CSV, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)
  - :8189: 7 missing (6 external: ApplyPulidFlux, Load Styles CSV, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)
  - :8190: 8 missing (6 external: ApplyPulidFlux, Load Styles CSV, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)
  - :8191: 6 missing (6 external: ApplyPulidFlux, Load Styles CSV, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)
  - :8192: 9 missing (6 external: ApplyPulidFlux, Load Styles CSV, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)

### 58 - Hiperrealismo-Qwen.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 16
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: MarkdownNote, Note)
  - :8189: 2 missing (2 external: MarkdownNote, Note)
  - :8190: 2 missing (2 external: MarkdownNote, Note)
  - :8191: 2 missing (2 external: MarkdownNote, Note)
  - :8192: 2 missing (2 external: MarkdownNote, Note)

### 63relightingQwen.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 15
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 1 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 1 missing (1 external: MarkdownNote)

### 63relightingQwen_B.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 16
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 1 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 1 missing (1 external: MarkdownNote)

### 65_qwen_image_edit_outfit_transfer_Tecnolitas.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 15
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: GetNode, SetNode)
  - :8189: 2 missing (2 external: GetNode, SetNode)
  - :8190: 2 missing (2 external: GetNode, SetNode)
  - :8191: 2 missing (2 external: GetNode, SetNode)
  - :8192: 2 missing (2 external: GetNode, SetNode)

### 7b - ComfyUI Máscaras en Profundidad_Cambio_Objetos y mas.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 11
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: Note, PrimitiveNode, Reroute)
  - :8189: 3 missing (3 external: Note, PrimitiveNode, Reroute)
  - :8190: 3 missing (3 external: Note, PrimitiveNode, Reroute)
  - :8191: 3 missing (3 external: Note, PrimitiveNode, Reroute)
  - :8192: 3 missing (3 external: Note, PrimitiveNode, Reroute)

### AcademiaSD_Z-Image-Turbo_Controlnet.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 17
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 1 missing
  - :8190: 3 missing
  - :8191: 0 missing
  - :8192: 4 missing

### AcademiaSD_Z-Image_v05.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 11
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: PrimitiveNode)
  - :8189: 2 missing (1 external: PrimitiveNode)
  - :8190: 2 missing (1 external: PrimitiveNode)
  - :8191: 1 missing (1 external: PrimitiveNode)
  - :8192: 3 missing (1 external: PrimitiveNode)

### ACADEMIA_SD QWEN-IMAGE TXT2IMG.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 12
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 1 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 3 missing

### comfyui-workflow-for-flux-simple-iuRdGnfzmTbOOzONIiVV-maitruclam-openart.ai.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 12
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### comfyui_SRPO-workflow-quantization-with-image-to-image.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 27
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 3 missing (1 external: MarkdownNote)
  - :8190: 6 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 12 missing (1 external: MarkdownNote)

### comfyui_unreal_textures.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 8
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### comfyui_workflow_previz_refine.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 5
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: UpscaleImage, VHS_FramesToVideoWAudio, VHS_VideoToFramesWAudio)
  - :8189: 3 missing (3 external: UpscaleImage, VHS_FramesToVideoWAudio, VHS_VideoToFramesWAudio)
  - :8190: 3 missing (3 external: UpscaleImage, VHS_FramesToVideoWAudio, VHS_VideoToFramesWAudio)
  - :8191: 3 missing (3 external: UpscaleImage, VHS_FramesToVideoWAudio, VHS_VideoToFramesWAudio)
  - :8192: 3 missing (3 external: UpscaleImage, VHS_FramesToVideoWAudio, VHS_VideoToFramesWAudio)

### Comprobar_LoRAs_Flux.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 18
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 1 missing
  - :8191: 0 missing
  - :8192: 3 missing

### Conditioning.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 11
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 1 missing

### Conditioning_2b.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 14
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: PrimitiveNode)
  - :8189: 1 missing (1 external: PrimitiveNode)
  - :8190: 1 missing (1 external: PrimitiveNode)
  - :8191: 1 missing (1 external: PrimitiveNode)
  - :8192: 2 missing (1 external: PrimitiveNode)

### Conditioning_2b__29248acc.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 14
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: PrimitiveNode)
  - :8189: 1 missing (1 external: PrimitiveNode)
  - :8190: 1 missing (1 external: PrimitiveNode)
  - :8191: 1 missing (1 external: PrimitiveNode)
  - :8192: 2 missing (1 external: PrimitiveNode)

### control-flux-image-visualization.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 14
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MultiAreaConditioning)
  - :8189: 2 missing (1 external: MultiAreaConditioning)
  - :8190: 2 missing (1 external: MultiAreaConditioning)
  - :8191: 1 missing (1 external: MultiAreaConditioning)
  - :8192: 2 missing (1 external: MultiAreaConditioning)

### cosTrio-Tpose-Factory-v12.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 36
- **Best instance:** :8188 (missing 6)
  - :8188: 6 missing (6 external: AspectSize, DF_Text_Box, Fast Groups Bypasser (rgthree), ImageSegmentationCustom, Note)
  - :8189: 20 missing (6 external: AspectSize, DF_Text_Box, Fast Groups Bypasser (rgthree), ImageSegmentationCustom, Note)
  - :8190: 19 missing (6 external: AspectSize, DF_Text_Box, Fast Groups Bypasser (rgthree), ImageSegmentationCustom, Note)
  - :8191: 6 missing (6 external: AspectSize, DF_Text_Box, Fast Groups Bypasser (rgthree), ImageSegmentationCustom, Note)
  - :8192: 27 missing (6 external: AspectSize, DF_Text_Box, Fast Groups Bypasser (rgthree), ImageSegmentationCustom, Note)

### creacion imagenes FLUX por Promt .json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 16
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: Note, PrimitiveNode)
  - :8189: 2 missing (2 external: Note, PrimitiveNode)
  - :8190: 2 missing (2 external: Note, PrimitiveNode)
  - :8191: 2 missing (2 external: Note, PrimitiveNode)
  - :8192: 2 missing (2 external: Note, PrimitiveNode)

### crear imagenes con flux 1.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 11
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 2 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 4 missing (1 external: MarkdownNote)

### discover-the-perfect-flux-alternative-for-low-vram-users-.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 12
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 2 missing
  - :8191: 0 missing
  - :8192: 2 missing

### enhance-your-ai-art-with-the-flux-prompt-generator.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: FluxPromptGenerator)
  - :8189: 2 missing (1 external: FluxPromptGenerator)
  - :8190: 3 missing (1 external: FluxPromptGenerator)
  - :8191: 1 missing (1 external: FluxPromptGenerator)
  - :8192: 3 missing (1 external: FluxPromptGenerator)

### example_workflow.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 11
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 1 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 3 missing (1 external: MarkdownNote)

### florence.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 16
- **Best instance:** :8188 (missing 4)
  - :8188: 4 missing (4 external: LoadImageListFromDir //Inspire, LoadPromptsFromFile //Inspire, SaveText, UnzipPrompt //Inspire)
  - :8189: 4 missing (4 external: LoadImageListFromDir //Inspire, LoadPromptsFromFile //Inspire, SaveText, UnzipPrompt //Inspire)
  - :8190: 6 missing (4 external: LoadImageListFromDir //Inspire, LoadPromptsFromFile //Inspire, SaveText, UnzipPrompt //Inspire)
  - :8191: 4 missing (4 external: LoadImageListFromDir //Inspire, LoadPromptsFromFile //Inspire, SaveText, UnzipPrompt //Inspire)
  - :8192: 6 missing (4 external: LoadImageListFromDir //Inspire, LoadPromptsFromFile //Inspire, SaveText, UnzipPrompt //Inspire)

### flux-fill-inpaint-example.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 11
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### flux-flux-pulid-instantid-realistic-face-swap.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 26
- **Best instance:** :8188 (missing 5)
  - :8188: 5 missing (4 external: ApplyPulidFlux, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)
  - :8189: 9 missing (4 external: ApplyPulidFlux, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)
  - :8190: 9 missing (4 external: ApplyPulidFlux, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)
  - :8191: 5 missing (4 external: ApplyPulidFlux, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)
  - :8192: 13 missing (4 external: ApplyPulidFlux, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)

### flux-inpainting-technique.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 17
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 1 missing
  - :8190: 1 missing
  - :8191: 0 missing
  - :8192: 3 missing

### flux-redux-pulid-face-swap-clone-any-portrait-photography.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 21
- **Best instance:** :8188 (missing 5)
  - :8188: 5 missing (5 external: ApplyPulidFlux, DF_Get_image_size, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)
  - :8189: 5 missing (5 external: ApplyPulidFlux, DF_Get_image_size, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)
  - :8190: 5 missing (5 external: ApplyPulidFlux, DF_Get_image_size, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)
  - :8191: 5 missing (5 external: ApplyPulidFlux, DF_Get_image_size, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)
  - :8192: 5 missing (5 external: ApplyPulidFlux, DF_Get_image_size, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)

### flux-simple-iu-maitruclam-openart.ai.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 12
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### flux.1-krea-dev-gguf.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 1 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 2 missing (1 external: MarkdownNote)

### FluxDepth_Capitulo11 (1).json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 12
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 1 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 1 missing (1 external: MarkdownNote)

### FluxInpainting_Capitulo10.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 12
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 1 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 1 missing (1 external: MarkdownNote)

### FluxLORA_Capitulo13.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### FluxOutpainting_Capitulo10.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 13
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 1 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 1 missing (1 external: MarkdownNote)

### FluxRealLoraWorkflowjson.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 18
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: Int Literal, Note, String Literal)
  - :8189: 3 missing (3 external: Int Literal, Note, String Literal)
  - :8190: 3 missing (3 external: Int Literal, Note, String Literal)
  - :8191: 3 missing (3 external: Int Literal, Note, String Literal)
  - :8192: 3 missing (3 external: Int Literal, Note, String Literal)

### Flux_Ace++.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 30
- **Best instance:** :8188 (missing 5)
  - :8188: 5 missing (5 external: Fast Groups Bypasser (rgthree), GetNode, Note, Reroute, SetNode)
  - :8189: 10 missing (5 external: Fast Groups Bypasser (rgthree), GetNode, Note, Reroute, SetNode)
  - :8190: 6 missing (5 external: Fast Groups Bypasser (rgthree), GetNode, Note, Reroute, SetNode)
  - :8191: 5 missing (5 external: Fast Groups Bypasser (rgthree), GetNode, Note, Reroute, SetNode)
  - :8192: 14 missing (5 external: Fast Groups Bypasser (rgthree), GetNode, Note, Reroute, SetNode)

### Flux_ClipTextEncodeFlux_Capitulo7.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### Flux_Fill_Outpainting.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 15
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 1 missing
  - :8190: 2 missing
  - :8191: 0 missing
  - :8192: 3 missing

### Flux_Fill_Redux_inpainting.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 14
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Reroute)
  - :8189: 1 missing (1 external: Reroute)
  - :8190: 3 missing (1 external: Reroute)
  - :8191: 1 missing (1 external: Reroute)
  - :8192: 3 missing (1 external: Reroute)

### Flux_Fill_Redux_inpainting_Florence.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 15
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Reroute)
  - :8189: 1 missing (1 external: Reroute)
  - :8190: 3 missing (1 external: Reroute)
  - :8191: 1 missing (1 external: Reroute)
  - :8192: 3 missing (1 external: Reroute)

### Flux_Krea_I2I_multilora_v2.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 15
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 4 missing
  - :8190: 1 missing
  - :8191: 0 missing
  - :8192: 6 missing

### Flux_Krea_T2I_multilora_v2.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 12
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 3 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 5 missing

### flux_lora_train_Capitulo14.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 24
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: GetNode, Note, SetNode)
  - :8189: 21 missing (3 external: GetNode, Note, SetNode)
  - :8190: 15 missing (3 external: GetNode, Note, SetNode)
  - :8191: 15 missing (3 external: GetNode, Note, SetNode)
  - :8192: 22 missing (3 external: GetNode, Note, SetNode)

### Hacer pelicula - copia.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 16
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: IPAdapterApply, rgthree.ImageSwitch, rgthree.Int)
  - :8189: 3 missing (3 external: IPAdapterApply, rgthree.ImageSwitch, rgthree.Int)
  - :8190: 4 missing (3 external: IPAdapterApply, rgthree.ImageSwitch, rgthree.Int)
  - :8191: 3 missing (3 external: IPAdapterApply, rgthree.ImageSwitch, rgthree.Int)
  - :8192: 4 missing (3 external: IPAdapterApply, rgthree.ImageSwitch, rgthree.Int)

### Hacer_pelicula_decorado_solo_controlnet.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### Hacer_pelicula_inpaint_solo.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 7
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### Hacer_pelicula_storyboard_solo.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 6
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### hidream_e1_Capitulo17.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 18
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: MarkdownNote, PrimitiveNode, Reroute)
  - :8189: 3 missing (3 external: MarkdownNote, PrimitiveNode, Reroute)
  - :8190: 3 missing (3 external: MarkdownNote, PrimitiveNode, Reroute)
  - :8191: 3 missing (3 external: MarkdownNote, PrimitiveNode, Reroute)
  - :8192: 3 missing (3 external: MarkdownNote, PrimitiveNode, Reroute)

### hidream_i1_full_Capitulo17.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 1 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 1 missing (1 external: MarkdownNote)

### Hooks_Máscaras_para_LoRAs.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 16
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Reroute)
  - :8189: 1 missing (1 external: Reroute)
  - :8190: 1 missing (1 external: Reroute)
  - :8191: 1 missing (1 external: Reroute)
  - :8192: 1 missing (1 external: Reroute)

### Hooks_Máscaras_para_LoRAs_y_para_scheduler_combinado.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 19
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Reroute)
  - :8189: 1 missing (1 external: Reroute)
  - :8190: 1 missing (1 external: Reroute)
  - :8191: 1 missing (1 external: Reroute)
  - :8192: 1 missing (1 external: Reroute)

### image_qwen_image_instantx_controlnet_Capitulo18.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 19
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: MarkdownNote, Note, ef3b4b73-ce32-4a60-a60e-d7f278bf6b14)
  - :8189: 3 missing (3 external: MarkdownNote, Note, ef3b4b73-ce32-4a60-a60e-d7f278bf6b14)
  - :8190: 3 missing (3 external: MarkdownNote, Note, ef3b4b73-ce32-4a60-a60e-d7f278bf6b14)
  - :8191: 3 missing (3 external: MarkdownNote, Note, ef3b4b73-ce32-4a60-a60e-d7f278bf6b14)
  - :8192: 3 missing (3 external: MarkdownNote, Note, ef3b4b73-ce32-4a60-a60e-d7f278bf6b14)

### image_qwen_image_instantx_inpainting_controlnet.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 24
- **Best instance:** :8188 (missing 5)
  - :8188: 5 missing (5 external: 2a4b2cc0-db37-4302-a067-da392f38f06b, MarkdownNote, Note, cade3e30-0eb2-4fd2-bf6e-8518f3a96e0c, f93c215e-c393-460e-9534-ed2c3d8a652e)
  - :8189: 5 missing (5 external: 2a4b2cc0-db37-4302-a067-da392f38f06b, MarkdownNote, Note, cade3e30-0eb2-4fd2-bf6e-8518f3a96e0c, f93c215e-c393-460e-9534-ed2c3d8a652e)
  - :8190: 5 missing (5 external: 2a4b2cc0-db37-4302-a067-da392f38f06b, MarkdownNote, Note, cade3e30-0eb2-4fd2-bf6e-8518f3a96e0c, f93c215e-c393-460e-9534-ed2c3d8a652e)
  - :8191: 5 missing (5 external: 2a4b2cc0-db37-4302-a067-da392f38f06b, MarkdownNote, Note, cade3e30-0eb2-4fd2-bf6e-8518f3a96e0c, f93c215e-c393-460e-9534-ed2c3d8a652e)
  - :8192: 5 missing (5 external: 2a4b2cc0-db37-4302-a067-da392f38f06b, MarkdownNote, Note, cade3e30-0eb2-4fd2-bf6e-8518f3a96e0c, f93c215e-c393-460e-9534-ed2c3d8a652e)

### img2img-painting.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 11
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### inpaint-outpaint-with-controlnet-union-sdxl.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 14
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 4 missing
  - :8190: 6 missing
  - :8191: 0 missing
  - :8192: 6 missing

### Inpainting workflow for changing a specific object.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 30
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything), SAMModelLoader (segment anything))
  - :8189: 6 missing (3 external: GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything), SAMModelLoader (segment anything))
  - :8190: 14 missing (3 external: GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything), SAMModelLoader (segment anything))
  - :8191: 3 missing (3 external: GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything), SAMModelLoader (segment anything))
  - :8192: 19 missing (3 external: GroundingDinoModelLoader (segment anything), GroundingDinoSAMSegment (segment anything), SAMModelLoader (segment anything))

### Inpaiting.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 11
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Note)
  - :8189: 1 missing (1 external: Note)
  - :8190: 2 missing (1 external: Note)
  - :8191: 1 missing (1 external: Note)
  - :8192: 2 missing (1 external: Note)

### Inpaiting_mascaras_tuto.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 13
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Reroute)
  - :8189: 1 missing (1 external: Reroute)
  - :8190: 1 missing (1 external: Reroute)
  - :8191: 1 missing (1 external: Reroute)
  - :8192: 5 missing (1 external: Reroute)

### Insta-Lo-RAm-Your-Virtual-Influencer-Generator.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 25
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: GetNode, SetNode)
  - :8189: 5 missing (2 external: GetNode, SetNode)
  - :8190: 2 missing (2 external: GetNode, SetNode)
  - :8191: 2 missing (2 external: GetNode, SetNode)
  - :8192: 7 missing (2 external: GetNode, SetNode)

### InstantID_basic.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 11
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 3 missing
  - :8190: 3 missing
  - :8191: 0 missing
  - :8192: 3 missing

### InstantID_depth.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 13
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 3 missing
  - :8190: 4 missing
  - :8191: 0 missing
  - :8192: 4 missing

### InstantID_IPAdapter.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 14
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 3 missing
  - :8190: 5 missing
  - :8191: 0 missing
  - :8192: 5 missing

### instantid_monalisa.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 23
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: FaceAnalysisModels, FaceEmbedDistance, IPAdapterApply)
  - :8189: 6 missing (3 external: FaceAnalysisModels, FaceEmbedDistance, IPAdapterApply)
  - :8190: 8 missing (3 external: FaceAnalysisModels, FaceEmbedDistance, IPAdapterApply)
  - :8191: 3 missing (3 external: FaceAnalysisModels, FaceEmbedDistance, IPAdapterApply)
  - :8192: 9 missing (3 external: FaceAnalysisModels, FaceEmbedDistance, IPAdapterApply)

### InstantID_multi_id.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 17
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 3 missing
  - :8190: 3 missing
  - :8191: 0 missing
  - :8192: 4 missing

### InstantID_posed.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 11
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 3 missing
  - :8190: 3 missing
  - :8191: 0 missing
  - :8192: 3 missing

### LoRA_Como_Scheduler.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 13
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### magical-img2img-render.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 13
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Reroute)
  - :8189: 2 missing (1 external: Reroute)
  - :8190: 3 missing (1 external: Reroute)
  - :8191: 1 missing (1 external: Reroute)
  - :8192: 4 missing (1 external: Reroute)

### Multi_LoRA_Upscaled.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: PrimitiveNode)
  - :8189: 3 missing (1 external: PrimitiveNode)
  - :8190: 1 missing (1 external: PrimitiveNode)
  - :8191: 1 missing (1 external: PrimitiveNode)
  - :8192: 3 missing (1 external: PrimitiveNode)

### Multi_LoRA_Upscaled__423c17ae.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: PrimitiveNode)
  - :8189: 3 missing (1 external: PrimitiveNode)
  - :8190: 1 missing (1 external: PrimitiveNode)
  - :8191: 1 missing (1 external: PrimitiveNode)
  - :8192: 3 missing (1 external: PrimitiveNode)

### NSFW SFW ACE Faceswap V1.0.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 62
- **Best instance:** :8188 (missing 6)
  - :8188: 6 missing (6 external: Fast Bypasser (rgthree), Fast Groups Bypasser (rgthree), Label (rgthree), Note, Reroute)
  - :8189: 23 missing (6 external: Fast Bypasser (rgthree), Fast Groups Bypasser (rgthree), Label (rgthree), Note, Reroute)
  - :8190: 22 missing (6 external: Fast Bypasser (rgthree), Fast Groups Bypasser (rgthree), Label (rgthree), Note, Reroute)
  - :8191: 6 missing (6 external: Fast Bypasser (rgthree), Fast Groups Bypasser (rgthree), Label (rgthree), Note, Reroute)
  - :8192: 36 missing (6 external: Fast Bypasser (rgthree), Fast Groups Bypasser (rgthree), Label (rgthree), Note, Reroute)

### nunchaku-flux.1-dev.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 16
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: PrimitiveNode)
  - :8189: 4 missing (1 external: PrimitiveNode)
  - :8190: 4 missing (1 external: PrimitiveNode)
  - :8191: 1 missing (1 external: PrimitiveNode)
  - :8192: 4 missing (1 external: PrimitiveNode)

### Olivio EASY workflow.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 6
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: UltimateSDUpscale)
  - :8189: 3 missing (1 external: UltimateSDUpscale)
  - :8190: 3 missing (1 external: UltimateSDUpscale)
  - :8191: 1 missing (1 external: UltimateSDUpscale)
  - :8192: 3 missing (1 external: UltimateSDUpscale)

### Olivio Model Switch workflow.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 7
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: UltimateSDUpscale)
  - :8189: 3 missing (1 external: UltimateSDUpscale)
  - :8190: 3 missing (1 external: UltimateSDUpscale)
  - :8191: 1 missing (1 external: UltimateSDUpscale)
  - :8192: 3 missing (1 external: UltimateSDUpscale)

### prompt-composer-sdxl-turbo-workflow.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 15
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: PrimitiveNode)
  - :8189: 5 missing (1 external: PrimitiveNode)
  - :8190: 5 missing (1 external: PrimitiveNode)
  - :8191: 1 missing (1 external: PrimitiveNode)
  - :8192: 5 missing (1 external: PrimitiveNode)

### prueba cine 2.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 11
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 1 missing
  - :8191: 0 missing
  - :8192: 1 missing

### Qwen-Image-creador de promt e imagenes.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 21
- **Best instance:** :8188 (missing 6)
  - :8188: 6 missing (6 external: Fast Groups Bypasser (rgthree), GetNode, Label (rgthree), MarkdownNote, Note)
  - :8189: 9 missing (6 external: Fast Groups Bypasser (rgthree), GetNode, Label (rgthree), MarkdownNote, Note)
  - :8190: 10 missing (6 external: Fast Groups Bypasser (rgthree), GetNode, Label (rgthree), MarkdownNote, Note)
  - :8191: 6 missing (6 external: Fast Groups Bypasser (rgthree), GetNode, Label (rgthree), MarkdownNote, Note)
  - :8192: 11 missing (6 external: Fast Groups Bypasser (rgthree), GetNode, Label (rgthree), MarkdownNote, Note)

### SB_Character_FLUX.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 16
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 2 missing
  - :8190: 2 missing
  - :8191: 0 missing
  - :8192: 2 missing

### SB_Character_FLUX__76688531.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 16
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 2 missing
  - :8190: 2 missing
  - :8191: 0 missing
  - :8192: 2 missing

### SB_Character_SDXL.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 14
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: IPAdapterApply, OpenPosePreprocessor)
  - :8189: 2 missing (2 external: IPAdapterApply, OpenPosePreprocessor)
  - :8190: 3 missing (2 external: IPAdapterApply, OpenPosePreprocessor)
  - :8191: 2 missing (2 external: IPAdapterApply, OpenPosePreprocessor)
  - :8192: 3 missing (2 external: IPAdapterApply, OpenPosePreprocessor)

### shermanvv_flux___pulid___in_context_lora__2k_out_per_image_comfyworkflows.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 25
- **Best instance:** :8188 (missing 7)
  - :8188: 7 missing (7 external: ApplyPulidFlux, PrimitiveNode, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)
  - :8189: 8 missing (7 external: ApplyPulidFlux, PrimitiveNode, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)
  - :8190: 9 missing (7 external: ApplyPulidFlux, PrimitiveNode, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)
  - :8191: 7 missing (7 external: ApplyPulidFlux, PrimitiveNode, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)
  - :8192: 11 missing (7 external: ApplyPulidFlux, PrimitiveNode, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader, PulidFluxModelLoader)

### SRPO-workflow.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 15
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: PrimitiveNode)
  - :8189: 1 missing (1 external: PrimitiveNode)
  - :8190: 1 missing (1 external: PrimitiveNode)
  - :8191: 1 missing (1 external: PrimitiveNode)
  - :8192: 1 missing (1 external: PrimitiveNode)

### Standar_WorkFlow.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 6
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### sup3rmass1ve_sd3_5_large_with_searge_prompt_enhance_and_lora_and_upscale_comfyworkflows.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 14
- **Best instance:** :8188 (missing 4)
  - :8188: 4 missing (3 external: Searge_Output_Node, UltimateSDUpscale, workflow>Prompt/Model/Clip/Vae Loader)
  - :8189: 4 missing (3 external: Searge_Output_Node, UltimateSDUpscale, workflow>Prompt/Model/Clip/Vae Loader)
  - :8190: 4 missing (3 external: Searge_Output_Node, UltimateSDUpscale, workflow>Prompt/Model/Clip/Vae Loader)
  - :8191: 4 missing (3 external: Searge_Output_Node, UltimateSDUpscale, workflow>Prompt/Model/Clip/Vae Loader)
  - :8192: 7 missing (3 external: Searge_Output_Node, UltimateSDUpscale, workflow>Prompt/Model/Clip/Vae Loader)

### the_writer_nightmare___4_comfyworkflows.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 23
- **Best instance:** :8188 (missing 6)
  - :8188: 6 missing (6 external: ComfyUIStyler, LoraTagLoader, PerturbedAttention, Seed Generator, UltimateSDUpscale)
  - :8189: 17 missing (6 external: ComfyUIStyler, LoraTagLoader, PerturbedAttention, Seed Generator, UltimateSDUpscale)
  - :8190: 18 missing (6 external: ComfyUIStyler, LoraTagLoader, PerturbedAttention, Seed Generator, UltimateSDUpscale)
  - :8191: 6 missing (6 external: ComfyUIStyler, LoraTagLoader, PerturbedAttention, Seed Generator, UltimateSDUpscale)
  - :8192: 20 missing (6 external: ComfyUIStyler, LoraTagLoader, PerturbedAttention, Seed Generator, UltimateSDUpscale)

### using-loras.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 13
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Reroute)
  - :8189: 4 missing (1 external: Reroute)
  - :8190: 2 missing (1 external: Reroute)
  - :8191: 1 missing (1 external: Reroute)
  - :8192: 4 missing (1 external: Reroute)

### V-1-SD.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 7
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 1 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 1 missing (1 external: MarkdownNote)

### workflow-4x-quick-upscale-fyoo07TxBwG1JLuyKZHA-comfyuistudio-openart.ai.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 4
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: Note, workflow/GROUP)
  - :8189: 2 missing (2 external: Note, workflow/GROUP)
  - :8190: 2 missing (2 external: Note, workflow/GROUP)
  - :8191: 2 missing (2 external: Note, workflow/GROUP)
  - :8192: 2 missing (2 external: Note, workflow/GROUP)

### workflow-accelerate-the-generation-speed-Cfi0e0ME28jHdXXDILE5-datou-openart.ai.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 16
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: SamplerTCD EulerA, TCDScheduler)
  - :8189: 4 missing (2 external: SamplerTCD EulerA, TCDScheduler)
  - :8190: 2 missing (2 external: SamplerTCD EulerA, TCDScheduler)
  - :8191: 2 missing (2 external: SamplerTCD EulerA, TCDScheduler)
  - :8192: 4 missing (2 external: SamplerTCD EulerA, TCDScheduler)

### workflow-comfyui-tutorial-major-update-for-qwen-image-2512-LehKKPn8aBJhwJ641mo7-cgpixel_ai_art-openart.ai.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 21
- **Best instance:** :8188 (missing 6)
  - :8188: 6 missing (6 external: Fast Groups Bypasser (rgthree), GetNode, Label (rgthree), MarkdownNote, Note)
  - :8189: 9 missing (6 external: Fast Groups Bypasser (rgthree), GetNode, Label (rgthree), MarkdownNote, Note)
  - :8190: 10 missing (6 external: Fast Groups Bypasser (rgthree), GetNode, Label (rgthree), MarkdownNote, Note)
  - :8191: 6 missing (6 external: Fast Groups Bypasser (rgthree), GetNode, Label (rgthree), MarkdownNote, Note)
  - :8192: 11 missing (6 external: Fast Groups Bypasser (rgthree), GetNode, Label (rgthree), MarkdownNote, Note)

### workflow-comfyui-tutorial-major-update-for-qwen-image-2512-LehKKPn8aBJhwJ641mo7-cgpixel_ai_art-openart.ai__edb98335.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 21
- **Best instance:** :8188 (missing 6)
  - :8188: 6 missing (6 external: Fast Groups Bypasser (rgthree), GetNode, Label (rgthree), MarkdownNote, Note)
  - :8189: 9 missing (6 external: Fast Groups Bypasser (rgthree), GetNode, Label (rgthree), MarkdownNote, Note)
  - :8190: 10 missing (6 external: Fast Groups Bypasser (rgthree), GetNode, Label (rgthree), MarkdownNote, Note)
  - :8191: 6 missing (6 external: Fast Groups Bypasser (rgthree), GetNode, Label (rgthree), MarkdownNote, Note)
  - :8192: 11 missing (6 external: Fast Groups Bypasser (rgthree), GetNode, Label (rgthree), MarkdownNote, Note)

### workflow-flux-controlnet-upscale-XsEKTG1cvnRXYdsPsQVc-cychenyue-openart.ai.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 20
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: Molmo7BDbnb, Note)
  - :8189: 3 missing (2 external: Molmo7BDbnb, Note)
  - :8190: 3 missing (2 external: Molmo7BDbnb, Note)
  - :8191: 2 missing (2 external: Molmo7BDbnb, Note)
  - :8192: 4 missing (2 external: Molmo7BDbnb, Note)

### workflow-flux-pulid-face-swap-with-upscale-4NCT0bt7k471EXpTBlLi-chin_buzzing_26-openart.ai.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 21
- **Best instance:** :8188 (missing 6)
  - :8188: 6 missing (6 external: ApplyPulidFlux, Label (rgthree), Note, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader)
  - :8189: 7 missing (6 external: ApplyPulidFlux, Label (rgthree), Note, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader)
  - :8190: 7 missing (6 external: ApplyPulidFlux, Label (rgthree), Note, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader)
  - :8191: 6 missing (6 external: ApplyPulidFlux, Label (rgthree), Note, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader)
  - :8192: 7 missing (6 external: ApplyPulidFlux, Label (rgthree), Note, PulidFluxEvaClipLoader, PulidFluxInsightFaceLoader)

### workflow-flux-your-ootd-flux-D6q01xaUd0AOf6A9OQym-jaylin-openart.ai.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 51
- **Best instance:** :8188 (missing 13)
  - :8188: 13 missing (12 external: Fast Groups Bypasser (rgthree), GetNode, Multi Text Merge, Note, PortraitMaster)
  - :8189: 18 missing (12 external: Fast Groups Bypasser (rgthree), GetNode, Multi Text Merge, Note, PortraitMaster)
  - :8190: 22 missing (12 external: Fast Groups Bypasser (rgthree), GetNode, Multi Text Merge, Note, PortraitMaster)
  - :8191: 13 missing (12 external: Fast Groups Bypasser (rgthree), GetNode, Multi Text Merge, Note, PortraitMaster)
  - :8192: 27 missing (12 external: Fast Groups Bypasser (rgthree), GetNode, Multi Text Merge, Note, PortraitMaster)

### workflow-hidream-full-824ixsLCZZeX4GEidHsz-datou-openart.ai.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 2
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: HiDreamSampler)
  - :8189: 1 missing (1 external: HiDreamSampler)
  - :8190: 1 missing (1 external: HiDreamSampler)
  - :8191: 1 missing (1 external: HiDreamSampler)
  - :8192: 1 missing (1 external: HiDreamSampler)

### workflow-lesson-6-model-switch-and-masking---comfy-academy-mVvngwUewT8Tfqs727YH-oliviosarikas-openart.ai.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 15
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Note)
  - :8189: 2 missing (1 external: Note)
  - :8190: 1 missing (1 external: Note)
  - :8191: 1 missing (1 external: Note)
  - :8192: 2 missing (1 external: Note)

### workflow-qwen-image-edit-2509-multiple-perspectives-on-characters-selfless-dedication-i2FDdfiAdOU5g2ANtZaU-north_ai-openart.ai.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 22
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Label (rgthree))
  - :8189: 1 missing (1 external: Label (rgthree))
  - :8190: 6 missing (1 external: Label (rgthree))
  - :8191: 1 missing (1 external: Label (rgthree))
  - :8192: 7 missing (1 external: Label (rgthree))

### workflow-restore-old-and-damaged-photosflux-kontext-yXttxLAnquPMZ9feVI7g-datou-openart.ai.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 24
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: Google-Gemini, Note)
  - :8189: 7 missing (2 external: Google-Gemini, Note)
  - :8190: 8 missing (2 external: Google-Gemini, Note)
  - :8191: 2 missing (2 external: Google-Gemini, Note)
  - :8192: 10 missing (2 external: Google-Gemini, Note)

### workflow-simple-clean-fast-nunchaku-kontext-lora-CSUdCgX2qoPsKYI5pz9f-ailab-openart.ai.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 19
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: Note, ailab_SaveImage)
  - :8189: 7 missing (2 external: Note, ailab_SaveImage)
  - :8190: 8 missing (2 external: Note, ailab_SaveImage)
  - :8191: 2 missing (2 external: Note, ailab_SaveImage)
  - :8192: 9 missing (2 external: Note, ailab_SaveImage)

### workflow.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 12
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 1 missing
  - :8190: 1 missing
  - :8191: 0 missing
  - :8192: 3 missing

### workflow_controlnet_cine_comfyui.json
- **Family:** image_still
- **Format:** api
- **Required nodes:** 15
- **Best instance:** :8188 (missing 6)
  - :8188: 6 missing (6 external: ApplyControlNet, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply, NormalBAE_Preprocessor)
  - :8189: 6 missing (6 external: ApplyControlNet, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply, NormalBAE_Preprocessor)
  - :8190: 7 missing (6 external: ApplyControlNet, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply, NormalBAE_Preprocessor)
  - :8191: 6 missing (6 external: ApplyControlNet, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply, NormalBAE_Preprocessor)
  - :8192: 7 missing (6 external: ApplyControlNet, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply, NormalBAE_Preprocessor)

### workflow_mbw.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 12
- **Best instance:** :8188 (missing 8)
  - :8188: 8 missing (8 external: Dict2Model, GridImage, KSamplerSetting, KSamplerXYZ, PrimitiveNode)
  - :8189: 8 missing (8 external: Dict2Model, GridImage, KSamplerSetting, KSamplerXYZ, PrimitiveNode)
  - :8190: 8 missing (8 external: Dict2Model, GridImage, KSamplerSetting, KSamplerXYZ, PrimitiveNode)
  - :8191: 8 missing (8 external: Dict2Model, GridImage, KSamplerSetting, KSamplerXYZ, PrimitiveNode)
  - :8192: 8 missing (8 external: Dict2Model, GridImage, KSamplerSetting, KSamplerXYZ, PrimitiveNode)

### workflow_mbw_multi.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 11
- **Best instance:** :8188 (missing 7)
  - :8188: 7 missing (7 external: GridImage, KSamplerSetting, KSamplerXYZ, PrimitiveNode, StateDictLoader)
  - :8189: 7 missing (7 external: GridImage, KSamplerSetting, KSamplerXYZ, PrimitiveNode, StateDictLoader)
  - :8190: 7 missing (7 external: GridImage, KSamplerSetting, KSamplerXYZ, PrimitiveNode, StateDictLoader)
  - :8191: 7 missing (7 external: GridImage, KSamplerSetting, KSamplerXYZ, PrimitiveNode, StateDictLoader)
  - :8192: 7 missing (7 external: GridImage, KSamplerSetting, KSamplerXYZ, PrimitiveNode, StateDictLoader)

### workflow_sd15_8gb_cine_gtx1080.json
- **Family:** image_still
- **Format:** api
- **Required nodes:** 10
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: ApplyControlNet, HED_Preprocessor)
  - :8189: 2 missing (2 external: ApplyControlNet, HED_Preprocessor)
  - :8190: 2 missing (2 external: ApplyControlNet, HED_Preprocessor)
  - :8191: 2 missing (2 external: ApplyControlNet, HED_Preprocessor)
  - :8192: 2 missing (2 external: ApplyControlNet, HED_Preprocessor)

### workflow_Tiled_Diffusion_Base.json
- **Family:** image_still
- **Format:** api
- **Required nodes:** 15
- **Best instance:** :8188 (missing 4)
  - :8188: 4 missing (4 external: BNK_CLIPTextEncodeAdvanced, TiledDiffusion, VAEDecodeTiled_TiledDiffusion, VAEEncodeTiled_TiledDiffusion)
  - :8189: 6 missing (4 external: BNK_CLIPTextEncodeAdvanced, TiledDiffusion, VAEDecodeTiled_TiledDiffusion, VAEEncodeTiled_TiledDiffusion)
  - :8190: 6 missing (4 external: BNK_CLIPTextEncodeAdvanced, TiledDiffusion, VAEDecodeTiled_TiledDiffusion, VAEEncodeTiled_TiledDiffusion)
  - :8191: 4 missing (4 external: BNK_CLIPTextEncodeAdvanced, TiledDiffusion, VAEDecodeTiled_TiledDiffusion, VAEEncodeTiled_TiledDiffusion)
  - :8192: 7 missing (4 external: BNK_CLIPTextEncodeAdvanced, TiledDiffusion, VAEDecodeTiled_TiledDiffusion, VAEEncodeTiled_TiledDiffusion)

### workflow_xyz_model_clip.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 13
- **Best instance:** :8188 (missing 9)
  - :8188: 9 missing (9 external: CLIPIter, Dict2Model, GridImage, KSamplerSetting, KSamplerXYZ)
  - :8189: 9 missing (9 external: CLIPIter, Dict2Model, GridImage, KSamplerSetting, KSamplerXYZ)
  - :8190: 9 missing (9 external: CLIPIter, Dict2Model, GridImage, KSamplerSetting, KSamplerXYZ)
  - :8191: 9 missing (9 external: CLIPIter, Dict2Model, GridImage, KSamplerSetting, KSamplerXYZ)
  - :8192: 9 missing (9 external: CLIPIter, Dict2Model, GridImage, KSamplerSetting, KSamplerXYZ)

### workflow_xyz_vae.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 12
- **Best instance:** :8188 (missing 8)
  - :8188: 8 missing (8 external: Dict2Model, GridImage, KSamplerSetting, KSamplerXYZ, PrimitiveNode)
  - :8189: 8 missing (8 external: Dict2Model, GridImage, KSamplerSetting, KSamplerXYZ, PrimitiveNode)
  - :8190: 8 missing (8 external: Dict2Model, GridImage, KSamplerSetting, KSamplerXYZ, PrimitiveNode)
  - :8191: 8 missing (8 external: Dict2Model, GridImage, KSamplerSetting, KSamplerXYZ, PrimitiveNode)
  - :8192: 8 missing (8 external: Dict2Model, GridImage, KSamplerSetting, KSamplerXYZ, PrimitiveNode)

### YarvixPA - Flux Kontext_V2 (1).json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 22
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Fast Groups Bypasser (rgthree))
  - :8189: 2 missing (1 external: Fast Groups Bypasser (rgthree))
  - :8190: 2 missing (1 external: Fast Groups Bypasser (rgthree))
  - :8191: 1 missing (1 external: Fast Groups Bypasser (rgthree))
  - :8192: 7 missing (1 external: Fast Groups Bypasser (rgthree))

### z_image_turbo_Low_vram.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 13
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Note)
  - :8189: 1 missing (1 external: Note)
  - :8190: 1 missing (1 external: Note)
  - :8191: 1 missing (1 external: Note)
  - :8192: 2 missing (1 external: Note)

### z_studio_sketch_into_a_real_image_similar_to_the_reference_image__comfyworkflows.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 14
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 4 missing
  - :8191: 0 missing
  - :8192: 4 missing

### ___2d_3d_comfyworkflows.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 23
- **Best instance:** :8191 (missing 2)
  - :8188: 3 missing (2 external: Fast Groups Bypasser (rgthree), Note)
  - :8189: 8 missing (2 external: Fast Groups Bypasser (rgthree), Note)
  - :8190: 5 missing (2 external: Fast Groups Bypasser (rgthree), Note)
  - :8191: 2 missing (2 external: Fast Groups Bypasser (rgthree), Note)
  - :8192: 14 missing (2 external: Fast Groups Bypasser (rgthree), Note)

### 02-film_interpolation.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 15
- **Best instance:** :8188 (missing 5)
  - :8188: 5 missing (5 external: Film Interpolation (mtb), Load Film Model (mtb), PrimitiveNode, Reroute, Text box)
  - :8189: 8 missing (5 external: Film Interpolation (mtb), Load Film Model (mtb), PrimitiveNode, Reroute, Text box)
  - :8190: 8 missing (5 external: Film Interpolation (mtb), Load Film Model (mtb), PrimitiveNode, Reroute, Text box)
  - :8191: 5 missing (5 external: Film Interpolation (mtb), Load Film Model (mtb), PrimitiveNode, Reroute, Text box)
  - :8192: 8 missing (5 external: Film Interpolation (mtb), Load Film Model (mtb), PrimitiveNode, Reroute, Text box)

### 03-animation_builder-condition-lerp.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 17
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: Note Plus (mtb), PrimitiveNode, Reroute)
  - :8189: 7 missing (3 external: Note Plus (mtb), PrimitiveNode, Reroute)
  - :8190: 7 missing (3 external: Note Plus (mtb), PrimitiveNode, Reroute)
  - :8191: 3 missing (3 external: Note Plus (mtb), PrimitiveNode, Reroute)
  - :8192: 7 missing (3 external: Note Plus (mtb), PrimitiveNode, Reroute)

### 04-animation_builder-deforum.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 17
- **Best instance:** :8188 (missing 4)
  - :8188: 4 missing (4 external: Note, PrimitiveNode, Reroute, Text box)
  - :8189: 10 missing (4 external: Note, PrimitiveNode, Reroute, Text box)
  - :8190: 10 missing (4 external: Note, PrimitiveNode, Reroute, Text box)
  - :8191: 4 missing (4 external: Note, PrimitiveNode, Reroute, Text box)
  - :8192: 10 missing (4 external: Note, PrimitiveNode, Reroute, Text box)

### Academia_SD_Self-Forcing_VACE_I2V (1).json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 22
- **Best instance:** :8189 (missing 2)
  - :8188: 3 missing
  - :8189: 2 missing
  - :8190: 2 missing
  - :8191: 3 missing
  - :8192: 8 missing

### Animar_imagenes_audio_OK.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 39
- **Best instance:** :8188 (missing 10)
  - :8188: 10 missing
  - :8189: 14 missing
  - :8190: 16 missing
  - :8191: 10 missing
  - :8192: 28 missing

### basic-video-face-swap.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 5
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 1 missing
  - :8190: 1 missing
  - :8191: 0 missing
  - :8192: 3 missing

### ComfyUI workflow animatediff+ipadapter.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 16
- **Best instance:** :8189 (missing 3)
  - :8188: 4 missing (3 external: IPAdapterApply, Note, PrimitiveNode)
  - :8189: 3 missing (3 external: IPAdapterApply, Note, PrimitiveNode)
  - :8190: 5 missing (3 external: IPAdapterApply, Note, PrimitiveNode)
  - :8191: 4 missing (3 external: IPAdapterApply, Note, PrimitiveNode)
  - :8192: 6 missing (3 external: IPAdapterApply, Note, PrimitiveNode)

### crear personajes prueba.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 12
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 1 missing
  - :8190: 3 missing
  - :8191: 0 missing
  - :8192: 4 missing

### easy-logo-animation.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 35
- **Best instance:** :8188 (missing 6)
  - :8188: 6 missing (5 external: AnimateDiffCombine, AnimateDiffModuleLoader, AnimateDiffSampler, AnimateDiffSlidingWindowOptions, seed _O)
  - :8189: 8 missing (5 external: AnimateDiffCombine, AnimateDiffModuleLoader, AnimateDiffSampler, AnimateDiffSlidingWindowOptions, seed _O)
  - :8190: 10 missing (5 external: AnimateDiffCombine, AnimateDiffModuleLoader, AnimateDiffSampler, AnimateDiffSlidingWindowOptions, seed _O)
  - :8191: 6 missing (5 external: AnimateDiffCombine, AnimateDiffModuleLoader, AnimateDiffSampler, AnimateDiffSlidingWindowOptions, seed _O)
  - :8192: 17 missing (5 external: AnimateDiffCombine, AnimateDiffModuleLoader, AnimateDiffSampler, AnimateDiffSlidingWindowOptions, seed _O)

### easy-video-faceswap.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 14
- **Best instance:** :8188 (missing 4)
  - :8188: 4 missing (3 external: Note, Reroute, YouTubeVideoLoader)
  - :8189: 5 missing (3 external: Note, Reroute, YouTubeVideoLoader)
  - :8190: 5 missing (3 external: Note, Reroute, YouTubeVideoLoader)
  - :8191: 4 missing (3 external: Note, Reroute, YouTubeVideoLoader)
  - :8192: 8 missing (3 external: Note, Reroute, YouTubeVideoLoader)

### Fast-hunyuan-30-fps-with-hd-upscaler-8K3Gp4BxCCXSsDh2BhKk.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 27
- **Best instance:** :8189 (missing 2)
  - :8188: 3 missing (2 external: Fast Groups Bypasser (rgthree), Note)
  - :8189: 2 missing (2 external: Fast Groups Bypasser (rgthree), Note)
  - :8190: 6 missing (2 external: Fast Groups Bypasser (rgthree), Note)
  - :8191: 3 missing (2 external: Fast Groups Bypasser (rgthree), Note)
  - :8192: 11 missing (2 external: Fast Groups Bypasser (rgthree), Note)

### Generación_Vídeos_WAN_2.1.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 12
- **Best instance:** :8189 (missing 0)
  - :8188: 10 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 10 missing
  - :8192: 11 missing

### LatentSync-basic.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 9
- **Best instance:** :8188 (missing 4)
  - :8188: 4 missing (4 external: D_LatentSyncNode, D_VideoLengthAdjuster, GetNode, SetNode)
  - :8189: 4 missing (4 external: D_LatentSyncNode, D_VideoLengthAdjuster, GetNode, SetNode)
  - :8190: 4 missing (4 external: D_LatentSyncNode, D_VideoLengthAdjuster, GetNode, SetNode)
  - :8191: 4 missing (4 external: D_LatentSyncNode, D_VideoLengthAdjuster, GetNode, SetNode)
  - :8192: 8 missing (4 external: D_LatentSyncNode, D_VideoLengthAdjuster, GetNode, SetNode)

### latentsync_comfyui_basic-1-4-1.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 6
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: D_LatentSyncNode, D_VideoLengthAdjuster, Reroute)
  - :8189: 3 missing (3 external: D_LatentSyncNode, D_VideoLengthAdjuster, Reroute)
  - :8190: 3 missing (3 external: D_LatentSyncNode, D_VideoLengthAdjuster, Reroute)
  - :8191: 3 missing (3 external: D_LatentSyncNode, D_VideoLengthAdjuster, Reroute)
  - :8192: 5 missing (3 external: D_LatentSyncNode, D_VideoLengthAdjuster, Reroute)

### LongCat_TI2V_example_01-1-1.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 27
- **Best instance:** :8190 (missing 6)
  - :8188: 20 missing (6 external: GetNode, MarkdownNote, Note, PrimitiveNode, Reroute)
  - :8189: 11 missing (6 external: GetNode, MarkdownNote, Note, PrimitiveNode, Reroute)
  - :8190: 6 missing (6 external: GetNode, MarkdownNote, Note, PrimitiveNode, Reroute)
  - :8191: 20 missing (6 external: GetNode, MarkdownNote, Note, PrimitiveNode, Reroute)
  - :8192: 26 missing (6 external: GetNode, MarkdownNote, Note, PrimitiveNode, Reroute)

### ltxvideo-i2v.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 20
- **Best instance:** :8188 (missing 4)
  - :8188: 4 missing (4 external: LTXVLoader, LTXVModelConfigurator, LTXVShiftSigmas, Note)
  - :8189: 7 missing (4 external: LTXVLoader, LTXVModelConfigurator, LTXVShiftSigmas, Note)
  - :8190: 10 missing (4 external: LTXVLoader, LTXVModelConfigurator, LTXVShiftSigmas, Note)
  - :8191: 4 missing (4 external: LTXVLoader, LTXVModelConfigurator, LTXVShiftSigmas, Note)
  - :8192: 12 missing (4 external: LTXVLoader, LTXVModelConfigurator, LTXVShiftSigmas, Note)

### make-anyone-say-anything-musetalk-cosyvoice.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 11
- **Best instance:** :8188 (missing 6)
  - :8188: 6 missing (6 external: CosyVoiceNode, MuseTalkCupAudio, MuseTalkRun, Note, TextNode)
  - :8189: 6 missing (6 external: CosyVoiceNode, MuseTalkCupAudio, MuseTalkRun, Note, TextNode)
  - :8190: 6 missing (6 external: CosyVoiceNode, MuseTalkCupAudio, MuseTalkRun, Note, TextNode)
  - :8191: 6 missing (6 external: CosyVoiceNode, MuseTalkCupAudio, MuseTalkRun, Note, TextNode)
  - :8192: 9 missing (6 external: CosyVoiceNode, MuseTalkCupAudio, MuseTalkRun, Note, TextNode)

### nsfw-prompt-skill-wan22-t2v-GbgACSHB2CYhDFXsEXTx-benjamin-openart.ai.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 17
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Note)
  - :8189: 3 missing (1 external: Note)
  - :8190: 2 missing (1 external: Note)
  - :8191: 1 missing (1 external: Note)
  - :8192: 5 missing (1 external: Note)

### PH_FLUXTOOLS_2_COG_v052.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 42
- **Best instance:** :8189 (missing 11)
  - :8188: 13 missing (8 external: Compare-🔬, Fast Groups Bypasser (rgthree), Float-🔬, If ANY return A else B-🔬, Int-🔬)
  - :8189: 11 missing (8 external: Compare-🔬, Fast Groups Bypasser (rgthree), Float-🔬, If ANY return A else B-🔬, Int-🔬)
  - :8190: 16 missing (8 external: Compare-🔬, Fast Groups Bypasser (rgthree), Float-🔬, If ANY return A else B-🔬, Int-🔬)
  - :8191: 13 missing (8 external: Compare-🔬, Fast Groups Bypasser (rgthree), Float-🔬, If ANY return A else B-🔬, Int-🔬)
  - :8192: 22 missing (8 external: Compare-🔬, Fast Groups Bypasser (rgthree), Float-🔬, If ANY return A else B-🔬, Int-🔬)

### remove-video-background.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 6
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 2 missing
  - :8190: 2 missing
  - :8191: 0 missing
  - :8192: 6 missing

### Sonic_sincronización_audio-labios.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 7
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: SONICSampler, SONICTLoader, SONIC_PreData)
  - :8189: 3 missing (3 external: SONICSampler, SONICTLoader, SONIC_PreData)
  - :8190: 3 missing (3 external: SONICSampler, SONICTLoader, SONIC_PreData)
  - :8191: 3 missing (3 external: SONICSampler, SONICTLoader, SONIC_PreData)
  - :8192: 5 missing (3 external: SONICSampler, SONICTLoader, SONIC_PreData)

### steerable-motion_smooth-n-steady.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 40
- **Best instance:** :8188 (missing 16)
  - :8188: 16 missing (8 external: BatchCreativeInterpolation, BatchValueScheduleLatentInput, Int Input [Dream], IpaConfiguration, Note Plus (mtb))
  - :8189: 16 missing (8 external: BatchCreativeInterpolation, BatchValueScheduleLatentInput, Int Input [Dream], IpaConfiguration, Note Plus (mtb))
  - :8190: 25 missing (8 external: BatchCreativeInterpolation, BatchValueScheduleLatentInput, Int Input [Dream], IpaConfiguration, Note Plus (mtb))
  - :8191: 16 missing (8 external: BatchCreativeInterpolation, BatchValueScheduleLatentInput, Int Input [Dream], IpaConfiguration, Note Plus (mtb))
  - :8192: 34 missing (8 external: BatchCreativeInterpolation, BatchValueScheduleLatentInput, Int Input [Dream], IpaConfiguration, Note Plus (mtb))

### txt_to_img_to_video.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### VIDEO 13 WF.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 99
- **Best instance:** :8189 (missing 31)
  - :8188: 32 missing (19 external: BatchPromptSchedule, DownloadAndLoadPyramidFlowModel, Fast Bypasser (rgthree), Fast Groups Muter (rgthree), GetNode)
  - :8189: 31 missing (19 external: BatchPromptSchedule, DownloadAndLoadPyramidFlowModel, Fast Bypasser (rgthree), Fast Groups Muter (rgthree), GetNode)
  - :8190: 47 missing (19 external: BatchPromptSchedule, DownloadAndLoadPyramidFlowModel, Fast Bypasser (rgthree), Fast Groups Muter (rgthree), GetNode)
  - :8191: 32 missing (19 external: BatchPromptSchedule, DownloadAndLoadPyramidFlowModel, Fast Bypasser (rgthree), Fast Groups Muter (rgthree), GetNode)
  - :8192: 61 missing (19 external: BatchPromptSchedule, DownloadAndLoadPyramidFlowModel, Fast Bypasser (rgthree), Fast Groups Muter (rgthree), GetNode)

### WAN22_reference_mask.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 3
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### wanvideo_vid2vid_example_01.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 15
- **Best instance:** :8190 (missing 1)
  - :8188: 11 missing (1 external: Note)
  - :8189: 3 missing (1 external: Note)
  - :8190: 1 missing (1 external: Note)
  - :8191: 11 missing (1 external: Note)
  - :8192: 15 missing (1 external: Note)

### wav2lip fix.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 5
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing
  - :8189: 1 missing
  - :8190: 2 missing
  - :8191: 1 missing
  - :8192: 4 missing

### Wav2Lip.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 6
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing
  - :8189: 2 missing
  - :8190: 3 missing
  - :8191: 1 missing
  - :8192: 6 missing

### wf.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 6
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: MuseTalkCupAudio, MuseTalkRun, VHS_FILENAMES_STRING_MuseTalk)
  - :8189: 3 missing (3 external: MuseTalkCupAudio, MuseTalkRun, VHS_FILENAMES_STRING_MuseTalk)
  - :8190: 3 missing (3 external: MuseTalkCupAudio, MuseTalkRun, VHS_FILENAMES_STRING_MuseTalk)
  - :8191: 3 missing (3 external: MuseTalkCupAudio, MuseTalkRun, VHS_FILENAMES_STRING_MuseTalk)
  - :8192: 6 missing (3 external: MuseTalkCupAudio, MuseTalkRun, VHS_FILENAMES_STRING_MuseTalk)

### workflow-free-digital-human-bcculjSnGEcDuGhoNhkd-discus_disastrous_37-openart.ai.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 32
- **Best instance:** :8188 (missing 14)
  - :8188: 14 missing (13 external: ChatTTS_, GetNode, LoadWhisperModel, Note, OpenVoiceClone)
  - :8189: 18 missing (13 external: ChatTTS_, GetNode, LoadWhisperModel, Note, OpenVoiceClone)
  - :8190: 18 missing (13 external: ChatTTS_, GetNode, LoadWhisperModel, Note, OpenVoiceClone)
  - :8191: 14 missing (13 external: ChatTTS_, GetNode, LoadWhisperModel, Note, OpenVoiceClone)
  - :8192: 26 missing (13 external: ChatTTS_, GetNode, LoadWhisperModel, Note, OpenVoiceClone)

### workflow-inner-reflections-vid2vid-style-conversion-sd-15---ipadapter-batch-unfold-aHKgex49Qh2kYE2X78Oh-peccary_vivacious_97-openart.ai.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 22
- **Best instance:** :8189 (missing 3)
  - :8188: 4 missing (2 external: IPAdapterApply, PrimitiveNode)
  - :8189: 3 missing (2 external: IPAdapterApply, PrimitiveNode)
  - :8190: 8 missing (2 external: IPAdapterApply, PrimitiveNode)
  - :8191: 4 missing (2 external: IPAdapterApply, PrimitiveNode)
  - :8192: 10 missing (2 external: IPAdapterApply, PrimitiveNode)

### workflow-perfect-lip-sync-ai-face-animation-jEIRkxkIGvuC6Nwm69Uz-comfyuiblog-openart.ai.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 44
- **Best instance:** :8189 (missing 11)
  - :8188: 20 missing (8 external: DownloadAndLoadLivePortraitModels, LivePortraitComposite, LivePortraitCropper, LivePortraitLoadMediaPipeCropper, LivePortraitProcess)
  - :8189: 11 missing (8 external: DownloadAndLoadLivePortraitModels, LivePortraitComposite, LivePortraitCropper, LivePortraitLoadMediaPipeCropper, LivePortraitProcess)
  - :8190: 21 missing (8 external: DownloadAndLoadLivePortraitModels, LivePortraitComposite, LivePortraitCropper, LivePortraitLoadMediaPipeCropper, LivePortraitProcess)
  - :8191: 20 missing (8 external: DownloadAndLoadLivePortraitModels, LivePortraitComposite, LivePortraitCropper, LivePortraitLoadMediaPipeCropper, LivePortraitProcess)
  - :8192: 32 missing (8 external: DownloadAndLoadLivePortraitModels, LivePortraitComposite, LivePortraitCropper, LivePortraitLoadMediaPipeCropper, LivePortraitProcess)

### workflow-realistic-video-animatediff-v3-szroMANBgp98pkj6F67h-sergegreen-openart.ai.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 23
- **Best instance:** :8189 (missing 6)
  - :8188: 8 missing (4 external: BatchPromptSchedule, Note, PrimitiveNode, Text box)
  - :8189: 6 missing (4 external: BatchPromptSchedule, Note, PrimitiveNode, Text box)
  - :8190: 11 missing (4 external: BatchPromptSchedule, Note, PrimitiveNode, Text box)
  - :8191: 8 missing (4 external: BatchPromptSchedule, Note, PrimitiveNode, Text box)
  - :8192: 13 missing (4 external: BatchPromptSchedule, Note, PrimitiveNode, Text box)

### workflow-remove-mosaic-repair-images-v1-368JqukDF5dwJ9fHOXja-foxinn-openart.ai.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 34
- **Best instance:** :8188 (missing 5)
  - :8188: 5 missing (5 external: GetNode, MarkdownNote, SetNode, TTP_Image_Assy, TTP_Image_Tile_Batch)
  - :8189: 9 missing (5 external: GetNode, MarkdownNote, SetNode, TTP_Image_Assy, TTP_Image_Tile_Batch)
  - :8190: 14 missing (5 external: GetNode, MarkdownNote, SetNode, TTP_Image_Assy, TTP_Image_Tile_Batch)
  - :8191: 5 missing (5 external: GetNode, MarkdownNote, SetNode, TTP_Image_Assy, TTP_Image_Tile_Batch)
  - :8192: 17 missing (5 external: GetNode, MarkdownNote, SetNode, TTP_Image_Assy, TTP_Image_Tile_Batch)

### workflow-simple-prompt-travel-animations.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 55
- **Best instance:** :8188 (missing 14)
  - :8188: 14 missing (7 external: BatchPromptSchedule, Fast Groups Bypasser (rgthree), GetKeyFrames, ImageSelector, Note)
  - :8189: 17 missing (7 external: BatchPromptSchedule, Fast Groups Bypasser (rgthree), GetKeyFrames, ImageSelector, Note)
  - :8190: 24 missing (7 external: BatchPromptSchedule, Fast Groups Bypasser (rgthree), GetKeyFrames, ImageSelector, Note)
  - :8191: 14 missing (7 external: BatchPromptSchedule, Fast Groups Bypasser (rgthree), GetKeyFrames, ImageSelector, Note)
  - :8192: 36 missing (7 external: BatchPromptSchedule, Fast Groups Bypasser (rgthree), GetKeyFrames, ImageSelector, Note)

### workflow-strong-body-impact-super-v2-F9dMZ9JENnBTevO9H97d-sexygirl-openart.ai.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 37
- **Best instance:** :8188 (missing 6)
  - :8188: 6 missing (5 external: GetNode, HunyuanVideoFoley, Note, Reroute, SetNode)
  - :8189: 10 missing (5 external: GetNode, HunyuanVideoFoley, Note, Reroute, SetNode)
  - :8190: 12 missing (5 external: GetNode, HunyuanVideoFoley, Note, Reroute, SetNode)
  - :8191: 6 missing (5 external: GetNode, HunyuanVideoFoley, Note, Reroute, SetNode)
  - :8192: 18 missing (5 external: GetNode, HunyuanVideoFoley, Note, Reroute, SetNode)

### 1 - Basic Vid2Vid 1 ControlNet.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 20
- **Best instance:** :8189 (missing 3)
  - :8188: 6 missing (1 external: PrimitiveNode)
  - :8189: 3 missing (1 external: PrimitiveNode)
  - :8190: 9 missing (1 external: PrimitiveNode)
  - :8191: 6 missing (1 external: PrimitiveNode)
  - :8192: 11 missing (1 external: PrimitiveNode)

### 2 - Vid2Vid Multi-ControlNet.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 21
- **Best instance:** :8189 (missing 3)
  - :8188: 6 missing (1 external: PrimitiveNode)
  - :8189: 3 missing (1 external: PrimitiveNode)
  - :8190: 10 missing (1 external: PrimitiveNode)
  - :8191: 6 missing (1 external: PrimitiveNode)
  - :8192: 12 missing (1 external: PrimitiveNode)

### 3 - Basic Txt2Vid.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 14
- **Best instance:** :8189 (missing 1)
  - :8188: 7 missing (1 external: PrimitiveNode)
  - :8189: 1 missing (1 external: PrimitiveNode)
  - :8190: 7 missing (1 external: PrimitiveNode)
  - :8191: 7 missing (1 external: PrimitiveNode)
  - :8192: 8 missing (1 external: PrimitiveNode)

### 4 - Vid2Vid with Prompt Scheduling.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 21
- **Best instance:** :8189 (missing 4)
  - :8188: 7 missing (2 external: BatchPromptScheduleLatentInput, PrimitiveNode)
  - :8189: 4 missing (2 external: BatchPromptScheduleLatentInput, PrimitiveNode)
  - :8190: 10 missing (2 external: BatchPromptScheduleLatentInput, PrimitiveNode)
  - :8191: 7 missing (2 external: BatchPromptScheduleLatentInput, PrimitiveNode)
  - :8192: 12 missing (2 external: BatchPromptScheduleLatentInput, PrimitiveNode)

### 5 - Txt2Vid with Prompt Scheduling.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 15
- **Best instance:** :8189 (missing 2)
  - :8188: 8 missing (2 external: BatchPromptScheduleLatentInput, PrimitiveNode)
  - :8189: 2 missing (2 external: BatchPromptScheduleLatentInput, PrimitiveNode)
  - :8190: 8 missing (2 external: BatchPromptScheduleLatentInput, PrimitiveNode)
  - :8191: 8 missing (2 external: BatchPromptScheduleLatentInput, PrimitiveNode)
  - :8192: 9 missing (2 external: BatchPromptScheduleLatentInput, PrimitiveNode)

### comfyworkflows_e392cc0b_a776_4958_854f_adf51f785c2a.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 1 missing

### comfyworkflows_svd_____.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8189 (missing 1)
  - :8188: 2 missing (1 external: Reroute)
  - :8189: 1 missing (1 external: Reroute)
  - :8190: 2 missing (1 external: Reroute)
  - :8191: 2 missing (1 external: Reroute)
  - :8192: 2 missing (1 external: Reroute)

### appinfo-workflow.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 11
- **Best instance:** :8189 (missing 0)
  - :8188: 1 missing
  - :8189: 0 missing
  - :8190: 9 missing
  - :8191: 1 missing
  - :8192: 9 missing

### liveportrait_image_example_01.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 19
- **Best instance:** :8188 (missing 11)
  - :8188: 11 missing (11 external: DownloadAndLoadLivePortraitModels, LivePortraitComposite, LivePortraitCropper, LivePortraitLoadCropper, LivePortraitLoadFaceAlignmentCropper)
  - :8189: 15 missing (11 external: DownloadAndLoadLivePortraitModels, LivePortraitComposite, LivePortraitCropper, LivePortraitLoadCropper, LivePortraitLoadFaceAlignmentCropper)
  - :8190: 11 missing (11 external: DownloadAndLoadLivePortraitModels, LivePortraitComposite, LivePortraitCropper, LivePortraitLoadCropper, LivePortraitLoadFaceAlignmentCropper)
  - :8191: 11 missing (11 external: DownloadAndLoadLivePortraitModels, LivePortraitComposite, LivePortraitCropper, LivePortraitLoadCropper, LivePortraitLoadFaceAlignmentCropper)
  - :8192: 18 missing (11 external: DownloadAndLoadLivePortraitModels, LivePortraitComposite, LivePortraitCropper, LivePortraitLoadCropper, LivePortraitLoadFaceAlignmentCropper)

### liveportrait_realtime_example_01.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 11
- **Best instance:** :8188 (missing 5)
  - :8188: 5 missing (5 external: DownloadAndLoadLivePortraitModels, LivePortraitCropper, LivePortraitLoadMediaPipeCropper, LivePortraitProcess, Note)
  - :8189: 9 missing (5 external: DownloadAndLoadLivePortraitModels, LivePortraitCropper, LivePortraitLoadMediaPipeCropper, LivePortraitProcess, Note)
  - :8190: 5 missing (5 external: DownloadAndLoadLivePortraitModels, LivePortraitCropper, LivePortraitLoadMediaPipeCropper, LivePortraitProcess, Note)
  - :8191: 5 missing (5 external: DownloadAndLoadLivePortraitModels, LivePortraitCropper, LivePortraitLoadMediaPipeCropper, LivePortraitProcess, Note)
  - :8192: 9 missing (5 external: DownloadAndLoadLivePortraitModels, LivePortraitCropper, LivePortraitLoadMediaPipeCropper, LivePortraitProcess, Note)

### liveportrait_video_example_02.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 18
- **Best instance:** :8188 (missing 10)
  - :8188: 10 missing (10 external: DownloadAndLoadLivePortraitModels, LivePortraitComposite, LivePortraitCropper, LivePortraitLoadCropper, LivePortraitLoadMediaPipeCropper)
  - :8189: 14 missing (10 external: DownloadAndLoadLivePortraitModels, LivePortraitComposite, LivePortraitCropper, LivePortraitLoadCropper, LivePortraitLoadMediaPipeCropper)
  - :8190: 10 missing (10 external: DownloadAndLoadLivePortraitModels, LivePortraitComposite, LivePortraitCropper, LivePortraitLoadCropper, LivePortraitLoadMediaPipeCropper)
  - :8191: 10 missing (10 external: DownloadAndLoadLivePortraitModels, LivePortraitComposite, LivePortraitCropper, LivePortraitLoadCropper, LivePortraitLoadMediaPipeCropper)
  - :8192: 18 missing (10 external: DownloadAndLoadLivePortraitModels, LivePortraitComposite, LivePortraitCropper, LivePortraitLoadCropper, LivePortraitLoadMediaPipeCropper)

### live_workflow.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 5
- **Best instance:** :8189 (missing 0)
  - :8188: 1 missing
  - :8189: 0 missing
  - :8190: 5 missing
  - :8191: 1 missing
  - :8192: 5 missing

### v2v-workflow.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 5
- **Best instance:** :8189 (missing 0)
  - :8188: 1 missing
  - :8189: 0 missing
  - :8190: 5 missing
  - :8191: 1 missing
  - :8192: 5 missing

### 全家福模式-workflow.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 8
- **Best instance:** :8189 (missing 0)
  - :8188: 2 missing
  - :8189: 0 missing
  - :8190: 7 missing
  - :8191: 2 missing
  - :8192: 7 missing

### workflow-image-to-image-image-to-video-style-transfer-with-flux-2-klein-telestyle-nodes-PhrPTEUAG5x2d1jKqYVB-cgpixel_ai_art-openart.ai.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 16
- **Best instance:** :8188 (missing 8)
  - :8188: 8 missing (8 external: 1bff7d11-288a-4011-afd5-b901733d4f90, 7f69112d-3211-40a8-96e0-ae5dc843224b, Fast Groups Bypasser (rgthree), Label (rgthree), MarkdownNote)
  - :8189: 10 missing (8 external: 1bff7d11-288a-4011-afd5-b901733d4f90, 7f69112d-3211-40a8-96e0-ae5dc843224b, Fast Groups Bypasser (rgthree), Label (rgthree), MarkdownNote)
  - :8190: 11 missing (8 external: 1bff7d11-288a-4011-afd5-b901733d4f90, 7f69112d-3211-40a8-96e0-ae5dc843224b, Fast Groups Bypasser (rgthree), Label (rgthree), MarkdownNote)
  - :8191: 8 missing (8 external: 1bff7d11-288a-4011-afd5-b901733d4f90, 7f69112d-3211-40a8-96e0-ae5dc843224b, Fast Groups Bypasser (rgthree), Label (rgthree), MarkdownNote)
  - :8192: 13 missing (8 external: 1bff7d11-288a-4011-afd5-b901733d4f90, 7f69112d-3211-40a8-96e0-ae5dc843224b, Fast Groups Bypasser (rgthree), Label (rgthree), MarkdownNote)

### workflow-svi-2-pro-automatic-prompt---video-extension-tJnPfu881Sp2HQ4CmtxW-north_ai-openart.ai.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 27
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (2 external: GetNode, SetNode)
  - :8189: 13 missing (2 external: GetNode, SetNode)
  - :8190: 6 missing (2 external: GetNode, SetNode)
  - :8191: 3 missing (2 external: GetNode, SetNode)
  - :8192: 19 missing (2 external: GetNode, SetNode)

### workflow-wan22-14b-image-video-hd-version-XC06OMwupt9qC7euN61H-north_ai-openart.ai.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 39
- **Best instance:** :8189 (missing 17)
  - :8188: 24 missing (13 external: Bjornulf_ShowInt, Fast Groups Muter (rgthree), JjkShowText, JjkText, Note)
  - :8189: 17 missing (13 external: Bjornulf_ShowInt, Fast Groups Muter (rgthree), JjkShowText, JjkText, Note)
  - :8190: 18 missing (13 external: Bjornulf_ShowInt, Fast Groups Muter (rgthree), JjkShowText, JjkText, Note)
  - :8191: 24 missing (13 external: Bjornulf_ShowInt, Fast Groups Muter (rgthree), JjkShowText, JjkText, Note)
  - :8192: 35 missing (13 external: Bjornulf_ShowInt, Fast Groups Muter (rgthree), JjkShowText, JjkText, Note)

### workflow-wan22-animate-swap-anythingauto-seg-Jk5WFuRDcpXWIlMLk7Ds-faborohacks-openart.ai.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 45
- **Best instance:** :8190 (missing 14)
  - :8188: 27 missing (10 external: Fast Groups Muter (rgthree), GetNode, LayerMask: LoadSegmentAnythingModels, LayerMask: SegmentAnythingUltra V3, LayerUtility: GeminiV2)
  - :8189: 17 missing (10 external: Fast Groups Muter (rgthree), GetNode, LayerMask: LoadSegmentAnythingModels, LayerMask: SegmentAnythingUltra V3, LayerUtility: GeminiV2)
  - :8190: 14 missing (10 external: Fast Groups Muter (rgthree), GetNode, LayerMask: LoadSegmentAnythingModels, LayerMask: SegmentAnythingUltra V3, LayerUtility: GeminiV2)
  - :8191: 27 missing (10 external: Fast Groups Muter (rgthree), GetNode, LayerMask: LoadSegmentAnythingModels, LayerMask: SegmentAnythingUltra V3, LayerUtility: GeminiV2)
  - :8192: 41 missing (10 external: Fast Groups Muter (rgthree), GetNode, LayerMask: LoadSegmentAnythingModels, LayerMask: SegmentAnythingUltra V3, LayerUtility: GeminiV2)

### workflow-wan2_2-video-clothes-try-onfun-vace-version-cpBoTySGoyLPwSZ9HCzj-faborohacks-openart.ai.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 39
- **Best instance:** :8189 (missing 14)
  - :8188: 21 missing (8 external: GetNode, LayerUtility: GeminiV2, Note, PrimitiveNode, Reroute)
  - :8189: 14 missing (8 external: GetNode, LayerUtility: GeminiV2, Note, PrimitiveNode, Reroute)
  - :8190: 14 missing (8 external: GetNode, LayerUtility: GeminiV2, Note, PrimitiveNode, Reroute)
  - :8191: 21 missing (8 external: GetNode, LayerUtility: GeminiV2, Note, PrimitiveNode, Reroute)
  - :8192: 35 missing (8 external: GetNode, LayerUtility: GeminiV2, Note, PrimitiveNode, Reroute)

### image_chrono_edit_14B.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 5
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: 2b61e18f-9327-49e6-98af-da8e557c2336, 813daba6-ec1d-42dd-87bc-4f0f6e084a8d, MarkdownNote)
  - :8189: 3 missing (3 external: 2b61e18f-9327-49e6-98af-da8e557c2336, 813daba6-ec1d-42dd-87bc-4f0f6e084a8d, MarkdownNote)
  - :8190: 3 missing (3 external: 2b61e18f-9327-49e6-98af-da8e557c2336, 813daba6-ec1d-42dd-87bc-4f0f6e084a8d, MarkdownNote)
  - :8191: 3 missing (3 external: 2b61e18f-9327-49e6-98af-da8e557c2336, 813daba6-ec1d-42dd-87bc-4f0f6e084a8d, MarkdownNote)
  - :8192: 3 missing (3 external: 2b61e18f-9327-49e6-98af-da8e557c2336, 813daba6-ec1d-42dd-87bc-4f0f6e084a8d, MarkdownNote)

### Roda-ReactiveDepth-V30.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 17
- **Best instance:** :8188 (missing 10)
  - :8188: 10 missing (10 external: AudioFeatureExtractor, Depthflow, DepthflowEffectDOF, DepthflowEffectVignette, DepthflowMotionPresetOrbital)
  - :8189: 11 missing (10 external: AudioFeatureExtractor, Depthflow, DepthflowEffectDOF, DepthflowEffectVignette, DepthflowMotionPresetOrbital)
  - :8190: 12 missing (10 external: AudioFeatureExtractor, Depthflow, DepthflowEffectDOF, DepthflowEffectVignette, DepthflowMotionPresetOrbital)
  - :8191: 10 missing (10 external: AudioFeatureExtractor, Depthflow, DepthflowEffectDOF, DepthflowEffectVignette, DepthflowMotionPresetOrbital)
  - :8192: 16 missing (10 external: AudioFeatureExtractor, Depthflow, DepthflowEffectDOF, DepthflowEffectVignette, DepthflowMotionPresetOrbital)

### Roda-ReactiveVideo-Scrubber-V20.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 17
- **Best instance:** :8188 (missing 9)
  - :8188: 9 missing (9 external: AudioFeatureExtractor, AudioSeparator, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio, FlexVideoDirection)
  - :8189: 11 missing (9 external: AudioFeatureExtractor, AudioSeparator, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio, FlexVideoDirection)
  - :8190: 11 missing (9 external: AudioFeatureExtractor, AudioSeparator, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio, FlexVideoDirection)
  - :8191: 9 missing (9 external: AudioFeatureExtractor, AudioSeparator, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio, FlexVideoDirection)
  - :8192: 17 missing (9 external: AudioFeatureExtractor, AudioSeparator, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio, FlexVideoDirection)

### Roda-ReactScrub-GIMMSync-V30.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 22
- **Best instance:** :8188 (missing 11)
  - :8188: 11 missing (11 external: AudioFeatureExtractor, AudioSeparator, DownloadAndLoadGIMMVFIModel, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio)
  - :8189: 14 missing (11 external: AudioFeatureExtractor, AudioSeparator, DownloadAndLoadGIMMVFIModel, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio)
  - :8190: 14 missing (11 external: AudioFeatureExtractor, AudioSeparator, DownloadAndLoadGIMMVFIModel, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio)
  - :8191: 11 missing (11 external: AudioFeatureExtractor, AudioSeparator, DownloadAndLoadGIMMVFIModel, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio)
  - :8192: 22 missing (11 external: AudioFeatureExtractor, AudioSeparator, DownloadAndLoadGIMMVFIModel, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio)

### 04_Wan2.2 14B I2V (Image to Video).json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 14
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: MarkdownNote, Note)
  - :8189: 2 missing (2 external: MarkdownNote, Note)
  - :8190: 2 missing (2 external: MarkdownNote, Note)
  - :8191: 2 missing (2 external: MarkdownNote, Note)
  - :8192: 2 missing (2 external: MarkdownNote, Note)

### 05_Wan2.2 14B FLF2V (First+Last Frame to Video).json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 14
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: MarkdownNote, Note)
  - :8189: 2 missing (2 external: MarkdownNote, Note)
  - :8190: 2 missing (2 external: MarkdownNote, Note)
  - :8191: 2 missing (2 external: MarkdownNote, Note)
  - :8192: 2 missing (2 external: MarkdownNote, Note)

### 06_LTX-2  Image to Video.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 18
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: 3eaa20c4-5842-4fe4-87df-c0a7e83a6a78, MarkdownNote)
  - :8189: 2 missing (2 external: 3eaa20c4-5842-4fe4-87df-c0a7e83a6a78, MarkdownNote)
  - :8190: 4 missing (2 external: 3eaa20c4-5842-4fe4-87df-c0a7e83a6a78, MarkdownNote)
  - :8191: 2 missing (2 external: 3eaa20c4-5842-4fe4-87df-c0a7e83a6a78, MarkdownNote)
  - :8192: 5 missing (2 external: 3eaa20c4-5842-4fe4-87df-c0a7e83a6a78, MarkdownNote)

### Flujo_Profesional_ComfyUI.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 6)
  - :8188: 6 missing (6 external: AnimateDiffLoader, CombineFrames, IPAdapterLoader, LoadVideoFrames, PreviewVideo)
  - :8189: 6 missing (6 external: AnimateDiffLoader, CombineFrames, IPAdapterLoader, LoadVideoFrames, PreviewVideo)
  - :8190: 6 missing (6 external: AnimateDiffLoader, CombineFrames, IPAdapterLoader, LoadVideoFrames, PreviewVideo)
  - :8191: 6 missing (6 external: AnimateDiffLoader, CombineFrames, IPAdapterLoader, LoadVideoFrames, PreviewVideo)
  - :8192: 6 missing (6 external: AnimateDiffLoader, CombineFrames, IPAdapterLoader, LoadVideoFrames, PreviewVideo)

### SVI 2.0 PRO WORKFLOW.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 27
- **Best instance:** :8188 (missing 12)
  - :8188: 12 missing (12 external: 00a07f4d-d12a-4255-a63e-f17cbc13dbd3, 024ffd1a-eb57-4930-96b0-f61b1125e911, 1b165832-48d7-439f-8635-a156c338ac6d, 24fa26a4-166e-4f16-aa41-fdf04f07700f, 31d4829e-74b4-48a0-a610-1708e106b780)
  - :8189: 15 missing (12 external: 00a07f4d-d12a-4255-a63e-f17cbc13dbd3, 024ffd1a-eb57-4930-96b0-f61b1125e911, 1b165832-48d7-439f-8635-a156c338ac6d, 24fa26a4-166e-4f16-aa41-fdf04f07700f, 31d4829e-74b4-48a0-a610-1708e106b780)
  - :8190: 12 missing (12 external: 00a07f4d-d12a-4255-a63e-f17cbc13dbd3, 024ffd1a-eb57-4930-96b0-f61b1125e911, 1b165832-48d7-439f-8635-a156c338ac6d, 24fa26a4-166e-4f16-aa41-fdf04f07700f, 31d4829e-74b4-48a0-a610-1708e106b780)
  - :8191: 12 missing (12 external: 00a07f4d-d12a-4255-a63e-f17cbc13dbd3, 024ffd1a-eb57-4930-96b0-f61b1125e911, 1b165832-48d7-439f-8635-a156c338ac6d, 24fa26a4-166e-4f16-aa41-fdf04f07700f, 31d4829e-74b4-48a0-a610-1708e106b780)
  - :8192: 16 missing (12 external: 00a07f4d-d12a-4255-a63e-f17cbc13dbd3, 024ffd1a-eb57-4930-96b0-f61b1125e911, 1b165832-48d7-439f-8635-a156c338ac6d, 24fa26a4-166e-4f16-aa41-fdf04f07700f, 31d4829e-74b4-48a0-a610-1708e106b780)

### 13 - Image2video.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 14
- **Best instance:** :8189 (missing 0)
  - :8188: 1 missing
  - :8189: 0 missing
  - :8190: 1 missing
  - :8191: 1 missing
  - :8192: 3 missing

### 13a - text2video.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 13
- **Best instance:** :8189 (missing 2)
  - :8188: 5 missing (2 external: BatchPromptSchedule, PrimitiveNode)
  - :8189: 2 missing (2 external: BatchPromptSchedule, PrimitiveNode)
  - :8190: 6 missing (2 external: BatchPromptSchedule, PrimitiveNode)
  - :8191: 5 missing (2 external: BatchPromptSchedule, PrimitiveNode)
  - :8192: 7 missing (2 external: BatchPromptSchedule, PrimitiveNode)

### 13_Tuto_2_Tecnolitas.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 19
- **Best instance:** :8189 (missing 2)
  - :8188: 5 missing (2 external: BatchPromptSchedule, PrimitiveNode)
  - :8189: 2 missing (2 external: BatchPromptSchedule, PrimitiveNode)
  - :8190: 7 missing (2 external: BatchPromptSchedule, PrimitiveNode)
  - :8191: 5 missing (2 external: BatchPromptSchedule, PrimitiveNode)
  - :8192: 8 missing (2 external: BatchPromptSchedule, PrimitiveNode)

### 13_Tuto_Tecnolitas.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 13
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 1 missing
  - :8191: 0 missing
  - :8192: 2 missing

### 40_LTX_IMG2VID.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 19
- **Best instance:** :8188 (missing 4)
  - :8188: 4 missing (3 external: LTXVLoader, LTXVModelConfigurator, LTXVShiftSigmas)
  - :8189: 5 missing (3 external: LTXVLoader, LTXVModelConfigurator, LTXVShiftSigmas)
  - :8190: 8 missing (3 external: LTXVLoader, LTXVModelConfigurator, LTXVShiftSigmas)
  - :8191: 4 missing (3 external: LTXVLoader, LTXVModelConfigurator, LTXVShiftSigmas)
  - :8192: 11 missing (3 external: LTXVLoader, LTXVModelConfigurator, LTXVShiftSigmas)

### 46_WANvideo-i2v-lines-v20.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 14
- **Best instance:** :8189 (missing 2)
  - :8188: 12 missing (2 external: Label (rgthree), Note)
  - :8189: 2 missing (2 external: Label (rgthree), Note)
  - :8190: 2 missing (2 external: Label (rgthree), Note)
  - :8191: 12 missing (2 external: Label (rgthree), Note)
  - :8192: 13 missing (2 external: Label (rgthree), Note)

### 46_WANvideo-t2v-lines-v10.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 14
- **Best instance:** :8189 (missing 2)
  - :8188: 12 missing (2 external: Label (rgthree), Note)
  - :8189: 2 missing (2 external: Label (rgthree), Note)
  - :8190: 2 missing (2 external: Label (rgthree), Note)
  - :8191: 12 missing (2 external: Label (rgthree), Note)
  - :8192: 13 missing (2 external: Label (rgthree), Note)

### 50-Wan2_1_control_tecnolitas.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 34
- **Best instance:** :8188 (missing 4)
  - :8188: 4 missing (4 external: Fast Groups Bypasser (rgthree), GetNode, Reroute, SetNode)
  - :8189: 13 missing (4 external: Fast Groups Bypasser (rgthree), GetNode, Reroute, SetNode)
  - :8190: 9 missing (4 external: Fast Groups Bypasser (rgthree), GetNode, Reroute, SetNode)
  - :8191: 4 missing (4 external: Fast Groups Bypasser (rgthree), GetNode, Reroute, SetNode)
  - :8192: 20 missing (4 external: Fast Groups Bypasser (rgthree), GetNode, Reroute, SetNode)

### broctor_29b3eccb_685f_48bb_b9fb_8aecf2a91af2_comfyworkflows.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 19
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (2 external: IPAdapterApply, PrimitiveNode)
  - :8189: 4 missing (2 external: IPAdapterApply, PrimitiveNode)
  - :8190: 6 missing (2 external: IPAdapterApply, PrimitiveNode)
  - :8191: 3 missing (2 external: IPAdapterApply, PrimitiveNode)
  - :8192: 8 missing (2 external: IPAdapterApply, PrimitiveNode)

### comfyworkflows_66c20349_b2d9_4456_b12d_1c1e7273c1e8.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 16
- **Best instance:** :8189 (missing 2)
  - :8188: 3 missing (1 external: PrimitiveNode)
  - :8189: 2 missing (1 external: PrimitiveNode)
  - :8190: 4 missing (1 external: PrimitiveNode)
  - :8191: 3 missing (1 external: PrimitiveNode)
  - :8192: 6 missing (1 external: PrimitiveNode)

### cwkc_merry_xmas_comfyworkflows.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 24
- **Best instance:** :8188 (missing 7)
  - :8188: 7 missing (6 external: Note, Reroute, Sampler Selector, Scheduler Selector, Seed Generator)
  - :8189: 9 missing (6 external: Note, Reroute, Sampler Selector, Scheduler Selector, Seed Generator)
  - :8190: 7 missing (6 external: Note, Reroute, Sampler Selector, Scheduler Selector, Seed Generator)
  - :8191: 7 missing (6 external: Note, Reroute, Sampler Selector, Scheduler Selector, Seed Generator)
  - :8192: 14 missing (6 external: Note, Reroute, Sampler Selector, Scheduler Selector, Seed Generator)

### friedtofu_499d1bbf_c2b6_404c_bc4d_e1eb74e09b8a_comfyworkflows.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 17
- **Best instance:** :8189 (missing 2)
  - :8188: 4 missing (1 external: PrimitiveNode)
  - :8189: 2 missing (1 external: PrimitiveNode)
  - :8190: 7 missing (1 external: PrimitiveNode)
  - :8191: 4 missing (1 external: PrimitiveNode)
  - :8192: 9 missing (1 external: PrimitiveNode)

### hunyuan_video_text_to_video.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 18
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: MarkdownNote, Note)
  - :8189: 2 missing (2 external: MarkdownNote, Note)
  - :8190: 2 missing (2 external: MarkdownNote, Note)
  - :8191: 2 missing (2 external: MarkdownNote, Note)
  - :8192: 2 missing (2 external: MarkdownNote, Note)

### jon_king_alien_dancer_comfyworkflows.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 21
- **Best instance:** :8188 (missing 5)
  - :8188: 5 missing (3 external: LoraInfo, LoraStackLoader_PoP, Reroute)
  - :8189: 5 missing (3 external: LoraInfo, LoraStackLoader_PoP, Reroute)
  - :8190: 9 missing (3 external: LoraInfo, LoraStackLoader_PoP, Reroute)
  - :8191: 5 missing (3 external: LoraInfo, LoraStackLoader_PoP, Reroute)
  - :8192: 10 missing (3 external: LoraInfo, LoraStackLoader_PoP, Reroute)

### LongCat_TI2V_Paris_Girl_Street_Cafe.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 27
- **Best instance:** :8190 (missing 6)
  - :8188: 20 missing (6 external: GetNode, MarkdownNote, Note, PrimitiveNode, Reroute)
  - :8189: 11 missing (6 external: GetNode, MarkdownNote, Note, PrimitiveNode, Reroute)
  - :8190: 6 missing (6 external: GetNode, MarkdownNote, Note, PrimitiveNode, Reroute)
  - :8191: 20 missing (6 external: GetNode, MarkdownNote, Note, PrimitiveNode, Reroute)
  - :8192: 26 missing (6 external: GetNode, MarkdownNote, Note, PrimitiveNode, Reroute)

### LTX-2_I2V_Full_wLora.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 18
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: 3eaa20c4-5842-4fe4-87df-c0a7e83a6a78, MarkdownNote)
  - :8189: 2 missing (2 external: 3eaa20c4-5842-4fe4-87df-c0a7e83a6a78, MarkdownNote)
  - :8190: 4 missing (2 external: 3eaa20c4-5842-4fe4-87df-c0a7e83a6a78, MarkdownNote)
  - :8191: 2 missing (2 external: 3eaa20c4-5842-4fe4-87df-c0a7e83a6a78, MarkdownNote)
  - :8192: 5 missing (2 external: 3eaa20c4-5842-4fe4-87df-c0a7e83a6a78, MarkdownNote)

### LTX-2_ICLoRA_All_Distilled.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 8
- **Best instance:** :8188 (missing 4)
  - :8188: 4 missing (4 external: 2dc75cab-e957-4437-a5bb-2afb0ea00516, 3ad0b41c-8c47-4e10-a53e-ed340cc26b5f, MarkdownNote, b83ac947-e174-4a8e-b0c1-f7c3b8f00419)
  - :8189: 4 missing (4 external: 2dc75cab-e957-4437-a5bb-2afb0ea00516, 3ad0b41c-8c47-4e10-a53e-ed340cc26b5f, MarkdownNote, b83ac947-e174-4a8e-b0c1-f7c3b8f00419)
  - :8190: 4 missing (4 external: 2dc75cab-e957-4437-a5bb-2afb0ea00516, 3ad0b41c-8c47-4e10-a53e-ed340cc26b5f, MarkdownNote, b83ac947-e174-4a8e-b0c1-f7c3b8f00419)
  - :8191: 4 missing (4 external: 2dc75cab-e957-4437-a5bb-2afb0ea00516, 3ad0b41c-8c47-4e10-a53e-ed340cc26b5f, MarkdownNote, b83ac947-e174-4a8e-b0c1-f7c3b8f00419)
  - :8192: 4 missing (4 external: 2dc75cab-e957-4437-a5bb-2afb0ea00516, 3ad0b41c-8c47-4e10-a53e-ed340cc26b5f, MarkdownNote, b83ac947-e174-4a8e-b0c1-f7c3b8f00419)

### LTX-2_T2V_Full_wLora.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 17
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: 65e1c5bd-6c3a-4569-960f-5a9656bb6cef, MarkdownNote)
  - :8189: 2 missing (2 external: 65e1c5bd-6c3a-4569-960f-5a9656bb6cef, MarkdownNote)
  - :8190: 4 missing (2 external: 65e1c5bd-6c3a-4569-960f-5a9656bb6cef, MarkdownNote)
  - :8191: 2 missing (2 external: 65e1c5bd-6c3a-4569-960f-5a9656bb6cef, MarkdownNote)
  - :8192: 5 missing (2 external: 65e1c5bd-6c3a-4569-960f-5a9656bb6cef, MarkdownNote)

### LTX-2_T2V_MIO.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 6
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### LTX-2_V2V_Detailer.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 18
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 4 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 4 missing (1 external: MarkdownNote)

### nsfw-prompt-skill-wan22-t2v-GbgACSHB2CYhDFXsEXTx-benjamin-openart.ai.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 17
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Note)
  - :8189: 3 missing (1 external: Note)
  - :8190: 2 missing (1 external: Note)
  - :8191: 1 missing (1 external: Note)
  - :8192: 5 missing (1 external: Note)

### restaurar_cugan.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 5
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 1 missing
  - :8191: 0 missing
  - :8192: 5 missing

### SeedVR2_4K_image_upscale.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 8
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Note)
  - :8189: 1 missing (1 external: Note)
  - :8190: 5 missing (1 external: Note)
  - :8191: 1 missing (1 external: Note)
  - :8192: 5 missing (1 external: Note)

### video_hunyuan_video_1.5_720p_t2v.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 23
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: MarkdownNote, Note)
  - :8189: 2 missing (2 external: MarkdownNote, Note)
  - :8190: 2 missing (2 external: MarkdownNote, Note)
  - :8191: 2 missing (2 external: MarkdownNote, Note)
  - :8192: 2 missing (2 external: MarkdownNote, Note)

### video_kandinsky5_i2v.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 4
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: 6a20d49e-c1e9-4e92-a7aa-f5550649f6f0, MarkdownNote)
  - :8189: 2 missing (2 external: 6a20d49e-c1e9-4e92-a7aa-f5550649f6f0, MarkdownNote)
  - :8190: 2 missing (2 external: 6a20d49e-c1e9-4e92-a7aa-f5550649f6f0, MarkdownNote)
  - :8191: 2 missing (2 external: 6a20d49e-c1e9-4e92-a7aa-f5550649f6f0, MarkdownNote)
  - :8192: 2 missing (2 external: 6a20d49e-c1e9-4e92-a7aa-f5550649f6f0, MarkdownNote)

### video_kandinsky5_t2v.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 3
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: 7aad998c-49e7-433f-bfb9-b1ac2680aa9e, MarkdownNote)
  - :8189: 2 missing (2 external: 7aad998c-49e7-433f-bfb9-b1ac2680aa9e, MarkdownNote)
  - :8190: 2 missing (2 external: 7aad998c-49e7-433f-bfb9-b1ac2680aa9e, MarkdownNote)
  - :8191: 2 missing (2 external: 7aad998c-49e7-433f-bfb9-b1ac2680aa9e, MarkdownNote)
  - :8192: 2 missing (2 external: 7aad998c-49e7-433f-bfb9-b1ac2680aa9e, MarkdownNote)

### video_ltx2_t2v.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 3
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: MarkdownNote, b7c2d337-c38d-4c04-922b-2d638449d13e)
  - :8189: 2 missing (2 external: MarkdownNote, b7c2d337-c38d-4c04-922b-2d638449d13e)
  - :8190: 2 missing (2 external: MarkdownNote, b7c2d337-c38d-4c04-922b-2d638449d13e)
  - :8191: 2 missing (2 external: MarkdownNote, b7c2d337-c38d-4c04-922b-2d638449d13e)
  - :8192: 2 missing (2 external: MarkdownNote, b7c2d337-c38d-4c04-922b-2d638449d13e)

### video_wan2_2_14B_t2v.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 13
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: MarkdownNote, Note)
  - :8189: 2 missing (2 external: MarkdownNote, Note)
  - :8190: 2 missing (2 external: MarkdownNote, Note)
  - :8191: 2 missing (2 external: MarkdownNote, Note)
  - :8192: 2 missing (2 external: MarkdownNote, Note)

### video_wan2_2_5B_fun_control.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 16
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 1 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 1 missing (1 external: MarkdownNote)

### video_wanmove_480p.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 22
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: MarkdownNote, Reroute)
  - :8189: 2 missing (2 external: MarkdownNote, Reroute)
  - :8190: 2 missing (2 external: MarkdownNote, Reroute)
  - :8191: 2 missing (2 external: MarkdownNote, Reroute)
  - :8192: 2 missing (2 external: MarkdownNote, Reroute)

### wan2.2_14B_IMG2VID_FLF.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 18
- **Best instance:** :8190 (missing 0)
  - :8188: 2 missing
  - :8189: 3 missing
  - :8190: 0 missing
  - :8191: 2 missing
  - :8192: 9 missing

### Wan2.2_I2V_14B_Loop_v05.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 24
- **Best instance:** :8190 (missing 0)
  - :8188: 2 missing
  - :8189: 8 missing
  - :8190: 0 missing
  - :8191: 2 missing
  - :8192: 16 missing

### Wan2.2_I2V_14B_Loop_V3.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 24
- **Best instance:** :8190 (missing 0)
  - :8188: 2 missing
  - :8189: 8 missing
  - :8190: 0 missing
  - :8191: 2 missing
  - :8192: 16 missing

### Wan2.2_I2V_14B_V4.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 18
- **Best instance:** :8190 (missing 0)
  - :8188: 2 missing
  - :8189: 4 missing
  - :8190: 0 missing
  - :8191: 2 missing
  - :8192: 8 missing

### Wan2.2_I2V_14B_V5_Multilora.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 18
- **Best instance:** :8190 (missing 0)
  - :8188: 2 missing
  - :8189: 4 missing
  - :8190: 0 missing
  - :8191: 2 missing
  - :8192: 10 missing

### Wan2.2_I2V_14B_V7_Loop.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 24
- **Best instance:** :8190 (missing 0)
  - :8188: 2 missing
  - :8189: 8 missing
  - :8190: 0 missing
  - :8191: 2 missing
  - :8192: 16 missing

### wan2.2_T2V_14b_FLF_Upscaler.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 22
- **Best instance:** :8190 (missing 1)
  - :8188: 2 missing
  - :8189: 4 missing
  - :8190: 1 missing
  - :8191: 2 missing
  - :8192: 10 missing

### wan2.2_T2V_14b_V7.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 17
- **Best instance:** :8190 (missing 0)
  - :8188: 2 missing
  - :8189: 4 missing
  - :8190: 0 missing
  - :8191: 2 missing
  - :8192: 8 missing

### wan2.2_T2V_14b_V8_multilora.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 17
- **Best instance:** :8190 (missing 0)
  - :8188: 2 missing
  - :8189: 4 missing
  - :8190: 0 missing
  - :8191: 2 missing
  - :8192: 10 missing

### Wan22Animate_AcademiaSD_v24.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 38
- **Best instance:** :8190 (missing 8)
  - :8188: 16 missing (3 external: Label (rgthree), Reroute, SetNode)
  - :8189: 11 missing (3 external: Label (rgthree), Reroute, SetNode)
  - :8190: 8 missing (3 external: Label (rgthree), Reroute, SetNode)
  - :8191: 16 missing (3 external: Label (rgthree), Reroute, SetNode)
  - :8192: 32 missing (3 external: Label (rgthree), Reroute, SetNode)

### Wan_FusionX_I2V_AcademiaSD_loops_v3.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 29
- **Best instance:** :8190 (missing 1)
  - :8188: 2 missing
  - :8189: 10 missing
  - :8190: 1 missing
  - :8191: 2 missing
  - :8192: 20 missing

### AcademiaSD_Hunyuan1.5_I2V_v03.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 21
- **Best instance:** :8190 (missing 2)
  - :8188: 3 missing (1 external: Label (rgthree))
  - :8189: 4 missing (1 external: Label (rgthree))
  - :8190: 2 missing (1 external: Label (rgthree))
  - :8191: 3 missing (1 external: Label (rgthree))
  - :8192: 10 missing (1 external: Label (rgthree))

### AcademiaSD_Wan21_Vace_R2V.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 24
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing
  - :8189: 4 missing
  - :8190: 5 missing
  - :8191: 2 missing
  - :8192: 13 missing

### ACADEMIA_SD WAN 2.2 IMG2VID LOOP VERSION, MULTILORA, SAGEATTENTION 2.2 AND FRAME INTERPOLATION.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 24
- **Best instance:** :8190 (missing 0)
  - :8188: 2 missing
  - :8189: 8 missing
  - :8190: 0 missing
  - :8191: 2 missing
  - :8192: 16 missing

### Wan_FusionX_I2V_AcademiaSD_V3.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 21
- **Best instance:** :8190 (missing 1)
  - :8188: 2 missing
  - :8189: 6 missing
  - :8190: 1 missing
  - :8191: 2 missing
  - :8192: 13 missing

### Wan_Holocine_AcademiaSD_v14.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 19
- **Best instance:** :8190 (missing 1)
  - :8188: 2 missing
  - :8189: 3 missing
  - :8190: 1 missing
  - :8191: 2 missing
  - :8192: 10 missing

### 64-z-image-turbo-colorfix.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 29
- **Best instance:** :8188 (missing 7)
  - :8188: 7 missing (7 external: Any Multi-Switch [RvTools], Fast Groups Bypasser (rgthree), Label (rgthree), Note, ResolutionMaster)
  - :8189: 8 missing (7 external: Any Multi-Switch [RvTools], Fast Groups Bypasser (rgthree), Label (rgthree), Note, ResolutionMaster)
  - :8190: 12 missing (7 external: Any Multi-Switch [RvTools], Fast Groups Bypasser (rgthree), Label (rgthree), Note, ResolutionMaster)
  - :8191: 7 missing (7 external: Any Multi-Switch [RvTools], Fast Groups Bypasser (rgthree), Label (rgthree), Note, ResolutionMaster)
  - :8192: 14 missing (7 external: Any Multi-Switch [RvTools], Fast Groups Bypasser (rgthree), Label (rgthree), Note, ResolutionMaster)

### Video_55_T2V_Self-Forcing.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 19
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing
  - :8189: 2 missing
  - :8190: 2 missing
  - :8191: 2 missing
  - :8192: 8 missing

### IMG-IMG--z-image-turbo-AIO-Upscaled-SeedVR2-workflow.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 22
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: Fast Groups Bypasser (rgthree), MarkdownNote, Reroute)
  - :8189: 3 missing (3 external: Fast Groups Bypasser (rgthree), MarkdownNote, Reroute)
  - :8190: 8 missing (3 external: Fast Groups Bypasser (rgthree), MarkdownNote, Reroute)
  - :8191: 3 missing (3 external: Fast Groups Bypasser (rgthree), MarkdownNote, Reroute)
  - :8192: 11 missing (3 external: Fast Groups Bypasser (rgthree), MarkdownNote, Reroute)

### WORKING_restauracion_animacion_GUI.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 3
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 1 missing
  - :8191: 0 missing
  - :8192: 1 missing

### WORKING_restauracion_cine_GUI.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 3
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 1 missing

### ___2d_3d_comfyworkflows.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 23
- **Best instance:** :8191 (missing 2)
  - :8188: 3 missing (2 external: Fast Groups Bypasser (rgthree), Note)
  - :8189: 8 missing (2 external: Fast Groups Bypasser (rgthree), Note)
  - :8190: 5 missing (2 external: Fast Groups Bypasser (rgthree), Note)
  - :8191: 2 missing (2 external: Fast Groups Bypasser (rgthree), Note)
  - :8192: 14 missing (2 external: Fast Groups Bypasser (rgthree), Note)

### 3d_hunyuan3d-v2.1.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 11
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 1 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 1 missing (1 external: MarkdownNote)

### 01_master_clean_api.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 7
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 2 missing
  - :8190: 1 missing
  - :8191: 0 missing
  - :8192: 2 missing

### 01_storyboard_fast_flux_schnell_ADAPTADO.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 8
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Note)
  - :8189: 1 missing (1 external: Note)
  - :8190: 1 missing (1 external: Note)
  - :8191: 1 missing (1 external: Note)
  - :8192: 1 missing (1 external: Note)

### 02_FLUX-Byte-Dance-USO-Single-Img2-Img.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 16
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: 805a5f96-6fdd-45a4-a1f3-623234fa734f, MarkdownNote)
  - :8189: 2 missing (2 external: 805a5f96-6fdd-45a4-a1f3-623234fa734f, MarkdownNote)
  - :8190: 2 missing (2 external: 805a5f96-6fdd-45a4-a1f3-623234fa734f, MarkdownNote)
  - :8191: 2 missing (2 external: 805a5f96-6fdd-45a4-a1f3-623234fa734f, MarkdownNote)
  - :8192: 2 missing (2 external: 805a5f96-6fdd-45a4-a1f3-623234fa734f, MarkdownNote)

### 02_storyboard_character_consistency_flux_ipadapter_ADAPTADO.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 12
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Note)
  - :8189: 1 missing (1 external: Note)
  - :8190: 3 missing (1 external: Note)
  - :8191: 1 missing (1 external: Note)
  - :8192: 3 missing (1 external: Note)

### 03_FLUX-Krea-Text2-Image.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 1 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 1 missing (1 external: MarkdownNote)

### ACADEMIA FireRed-Image-Edit-3-sources-multilora inpain outpain upscale.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 34
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Fast Groups Bypasser (rgthree))
  - :8189: 4 missing (1 external: Fast Groups Bypasser (rgthree))
  - :8190: 7 missing (1 external: Fast Groups Bypasser (rgthree))
  - :8191: 1 missing (1 external: Fast Groups Bypasser (rgthree))
  - :8192: 13 missing (1 external: Fast Groups Bypasser (rgthree))

### creacion de video desde imagen fija.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 12
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 1 missing
  - :8190: 1 missing
  - :8191: 0 missing
  - :8192: 1 missing

### flux1_krea_dev.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 3
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: 1135e349-dce8-45e8-8905-aaa86675429b, MarkdownNote)
  - :8189: 2 missing (2 external: 1135e349-dce8-45e8-8905-aaa86675429b, MarkdownNote)
  - :8190: 2 missing (2 external: 1135e349-dce8-45e8-8905-aaa86675429b, MarkdownNote)
  - :8191: 2 missing (2 external: 1135e349-dce8-45e8-8905-aaa86675429b, MarkdownNote)
  - :8192: 2 missing (2 external: 1135e349-dce8-45e8-8905-aaa86675429b, MarkdownNote)

### generador de loras multiples list prompts.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 25
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: GetNode, SetNode)
  - :8189: 5 missing (2 external: GetNode, SetNode)
  - :8190: 2 missing (2 external: GetNode, SetNode)
  - :8191: 2 missing (2 external: GetNode, SetNode)
  - :8192: 7 missing (2 external: GetNode, SetNode)

### image_flux2_text_to_image.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 3
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: MarkdownNote, e3a57dc6-b2bf-4d05-927d-3715b40d2a77)
  - :8189: 2 missing (2 external: MarkdownNote, e3a57dc6-b2bf-4d05-927d-3715b40d2a77)
  - :8190: 2 missing (2 external: MarkdownNote, e3a57dc6-b2bf-4d05-927d-3715b40d2a77)
  - :8191: 2 missing (2 external: MarkdownNote, e3a57dc6-b2bf-4d05-927d-3715b40d2a77)
  - :8192: 2 missing (2 external: MarkdownNote, e3a57dc6-b2bf-4d05-927d-3715b40d2a77)

### image_qwen_Image_2512.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 3
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: MarkdownNote, c3c58f7e-2004-43ae-8b06-a956294bf7f4)
  - :8189: 2 missing (2 external: MarkdownNote, c3c58f7e-2004-43ae-8b06-a956294bf7f4)
  - :8190: 2 missing (2 external: MarkdownNote, c3c58f7e-2004-43ae-8b06-a956294bf7f4)
  - :8191: 2 missing (2 external: MarkdownNote, c3c58f7e-2004-43ae-8b06-a956294bf7f4)
  - :8192: 2 missing (2 external: MarkdownNote, c3c58f7e-2004-43ae-8b06-a956294bf7f4)

### image_z_image_turbo.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 3
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: MarkdownNote, f2fdebf6-dfaf-43b6-9eb2-7f70613cfdc1)
  - :8189: 2 missing (2 external: MarkdownNote, f2fdebf6-dfaf-43b6-9eb2-7f70613cfdc1)
  - :8190: 2 missing (2 external: MarkdownNote, f2fdebf6-dfaf-43b6-9eb2-7f70613cfdc1)
  - :8191: 2 missing (2 external: MarkdownNote, f2fdebf6-dfaf-43b6-9eb2-7f70613cfdc1)
  - :8192: 2 missing (2 external: MarkdownNote, f2fdebf6-dfaf-43b6-9eb2-7f70613cfdc1)

### LTX-2.3_ICLoRA_Motion_Track_Distilled.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 35
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 6 missing
  - :8191: 0 missing
  - :8192: 8 missing

### LTX-2.3_ICLoRA_Union_Control_Distilled.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 38
- **Best instance:** :8189 (missing 0)
  - :8188: 2 missing
  - :8189: 0 missing
  - :8190: 8 missing
  - :8191: 2 missing
  - :8192: 10 missing

### LTX-2.3_T2V_I2V_Single_Stage_Distilled_Full.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 33
- **Best instance:** :8189 (missing 0)
  - :8188: 1 missing
  - :8189: 0 missing
  - :8190: 5 missing
  - :8191: 1 missing
  - :8192: 6 missing

### LTX-2.3_T2V_I2V_Two_Stage_Distilled.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 31
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 2 missing
  - :8191: 0 missing
  - :8192: 3 missing

### Unsaved Workflow (2).json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 6
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### Unsaved Workflow.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 6
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### video_wan2_1_infinitetalk_doblaje.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 23
- **Best instance:** :8188 (missing 4)
  - :8188: 4 missing (4 external: 16c4feb3-9adc-4bfd-ab30-e57cab73ffbf, 58374208-7916-4582-9f02-035a4536f14b, MarkdownNote, Reroute)
  - :8189: 4 missing (4 external: 16c4feb3-9adc-4bfd-ab30-e57cab73ffbf, 58374208-7916-4582-9f02-035a4536f14b, MarkdownNote, Reroute)
  - :8190: 4 missing (4 external: 16c4feb3-9adc-4bfd-ab30-e57cab73ffbf, 58374208-7916-4582-9f02-035a4536f14b, MarkdownNote, Reroute)
  - :8191: 4 missing (4 external: 16c4feb3-9adc-4bfd-ab30-e57cab73ffbf, 58374208-7916-4582-9f02-035a4536f14b, MarkdownNote, Reroute)
  - :8192: 4 missing (4 external: 16c4feb3-9adc-4bfd-ab30-e57cab73ffbf, 58374208-7916-4582-9f02-035a4536f14b, MarkdownNote, Reroute)

### Wan2-2-Ultimate-Text-To-Image-fast-render-cinematic-quality.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 11
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Note)
  - :8189: 2 missing (1 external: Note)
  - :8190: 2 missing (1 external: Note)
  - :8191: 1 missing (1 external: Note)
  - :8192: 2 missing (1 external: Note)

### n8n_previz_comfy_davinci.json
- **Family:** storyboard
- **Format:** ui
- **Required nodes:** 3
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: n8n-nodes-base.cron, n8n-nodes-base.executeCommand, n8n-nodes-base.httpRequest)
  - :8189: 3 missing (3 external: n8n-nodes-base.cron, n8n-nodes-base.executeCommand, n8n-nodes-base.httpRequest)
  - :8190: 3 missing (3 external: n8n-nodes-base.cron, n8n-nodes-base.executeCommand, n8n-nodes-base.httpRequest)
  - :8191: 3 missing (3 external: n8n-nodes-base.cron, n8n-nodes-base.executeCommand, n8n-nodes-base.httpRequest)
  - :8192: 3 missing (3 external: n8n-nodes-base.cron, n8n-nodes-base.executeCommand, n8n-nodes-base.httpRequest)

### prompt-composer-base-workflow.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 7
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 7 missing
  - :8190: 7 missing
  - :8191: 0 missing
  - :8192: 7 missing

### Qwen3-TTS Voice Clone (Reference).json
- **Family:** dubbing_audio
- **Format:** ui
- **Required nodes:** 8
- **Best instance:** :8190 (missing 1)
  - :8188: 6 missing (1 external: Note)
  - :8189: 6 missing (1 external: Note)
  - :8190: 1 missing (1 external: Note)
  - :8191: 6 missing (1 external: Note)
  - :8192: 6 missing (1 external: Note)

### 01_master_clean_api.json
- **Family:** video_cine
- **Format:** api
- **Required nodes:** 7
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 2 missing
  - :8190: 1 missing
  - :8191: 0 missing
  - :8192: 2 missing

### 02_depth_pass_api.json
- **Family:** three_d
- **Format:** api
- **Required nodes:** 7
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: DepthAnythingV2Loader, ImageLevels)
  - :8189: 3 missing (2 external: DepthAnythingV2Loader, ImageLevels)
  - :8190: 3 missing (2 external: DepthAnythingV2Loader, ImageLevels)
  - :8191: 2 missing (2 external: DepthAnythingV2Loader, ImageLevels)
  - :8192: 4 missing (2 external: DepthAnythingV2Loader, ImageLevels)

### 02_depth_pass_workflow.json
- **Family:** three_d
- **Format:** ui
- **Required nodes:** 7
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: DepthAnythingV2Loader, ImageLevels)
  - :8189: 3 missing (2 external: DepthAnythingV2Loader, ImageLevels)
  - :8190: 3 missing (2 external: DepthAnythingV2Loader, ImageLevels)
  - :8191: 2 missing (2 external: DepthAnythingV2Loader, ImageLevels)
  - :8192: 4 missing (2 external: DepthAnythingV2Loader, ImageLevels)

### 02_depth_pass_workflow_fixed.json
- **Family:** three_d
- **Format:** ui
- **Required nodes:** 7
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: DepthAnythingV2Loader, ImageLevels)
  - :8189: 3 missing (2 external: DepthAnythingV2Loader, ImageLevels)
  - :8190: 3 missing (2 external: DepthAnythingV2Loader, ImageLevels)
  - :8191: 2 missing (2 external: DepthAnythingV2Loader, ImageLevels)
  - :8192: 4 missing (2 external: DepthAnythingV2Loader, ImageLevels)

### 03_edges_pass_api.json
- **Family:** video_cine
- **Format:** api
- **Required nodes:** 5
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: SoftEdgePreprocessor)
  - :8189: 1 missing (1 external: SoftEdgePreprocessor)
  - :8190: 3 missing (1 external: SoftEdgePreprocessor)
  - :8191: 1 missing (1 external: SoftEdgePreprocessor)
  - :8192: 3 missing (1 external: SoftEdgePreprocessor)

### 03_edges_pass_workflow.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 5
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: SoftEdgePreprocessor)
  - :8189: 1 missing (1 external: SoftEdgePreprocessor)
  - :8190: 3 missing (1 external: SoftEdgePreprocessor)
  - :8191: 1 missing (1 external: SoftEdgePreprocessor)
  - :8192: 3 missing (1 external: SoftEdgePreprocessor)

### 05_cleanplate_inpaint_api.json
- **Family:** image_still
- **Format:** api
- **Required nodes:** 11
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: CLIPTextEncodePair)
  - :8189: 1 missing (1 external: CLIPTextEncodePair)
  - :8190: 3 missing (1 external: CLIPTextEncodePair)
  - :8191: 1 missing (1 external: CLIPTextEncodePair)
  - :8192: 3 missing (1 external: CLIPTextEncodePair)

### 06_room_extension_api.json
- **Family:** image_still
- **Format:** api
- **Required nodes:** 13
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: CLIPTextEncodePair, PaddingToMask)
  - :8189: 2 missing (2 external: CLIPTextEncodePair, PaddingToMask)
  - :8190: 4 missing (2 external: CLIPTextEncodePair, PaddingToMask)
  - :8191: 2 missing (2 external: CLIPTextEncodePair, PaddingToMask)
  - :8192: 4 missing (2 external: CLIPTextEncodePair, PaddingToMask)

### 06_room_extension_workflow.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 13
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: CLIPTextEncodePair, PaddingToMask)
  - :8189: 2 missing (2 external: CLIPTextEncodePair, PaddingToMask)
  - :8190: 4 missing (2 external: CLIPTextEncodePair, PaddingToMask)
  - :8191: 2 missing (2 external: CLIPTextEncodePair, PaddingToMask)
  - :8192: 4 missing (2 external: CLIPTextEncodePair, PaddingToMask)

### 19 - Flux_Inpainting.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 14
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 1 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 2 missing

### workflow_cine_sd15_estilizado_239.json
- **Family:** image_still
- **Format:** api
- **Required nodes:** 19
- **Best instance:** :8188 (missing 10)
  - :8188: 10 missing (10 external: ApplyControlNet, CannyEdge_Preprocessor, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply)
  - :8189: 10 missing (10 external: ApplyControlNet, CannyEdge_Preprocessor, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply)
  - :8190: 11 missing (10 external: ApplyControlNet, CannyEdge_Preprocessor, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply)
  - :8191: 10 missing (10 external: ApplyControlNet, CannyEdge_Preprocessor, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply)
  - :8192: 11 missing (10 external: ApplyControlNet, CannyEdge_Preprocessor, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply)

### workflow_cine_sd15_realista_239.json
- **Family:** image_still
- **Format:** api
- **Required nodes:** 19
- **Best instance:** :8188 (missing 10)
  - :8188: 10 missing (10 external: ApplyControlNet, CannyEdge_Preprocessor, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply)
  - :8189: 10 missing (10 external: ApplyControlNet, CannyEdge_Preprocessor, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply)
  - :8190: 11 missing (10 external: ApplyControlNet, CannyEdge_Preprocessor, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply)
  - :8191: 10 missing (10 external: ApplyControlNet, CannyEdge_Preprocessor, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply)
  - :8192: 11 missing (10 external: ApplyControlNet, CannyEdge_Preprocessor, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply)

### workflow_cine_sdxl_estilizado_239.json
- **Family:** image_still
- **Format:** api
- **Required nodes:** 19
- **Best instance:** :8188 (missing 10)
  - :8188: 10 missing (10 external: ApplyControlNet, CannyEdge_Preprocessor, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply)
  - :8189: 10 missing (10 external: ApplyControlNet, CannyEdge_Preprocessor, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply)
  - :8190: 11 missing (10 external: ApplyControlNet, CannyEdge_Preprocessor, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply)
  - :8191: 10 missing (10 external: ApplyControlNet, CannyEdge_Preprocessor, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply)
  - :8192: 11 missing (10 external: ApplyControlNet, CannyEdge_Preprocessor, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply)

### workflow_cine_sdxl_realista_239.json
- **Family:** image_still
- **Format:** api
- **Required nodes:** 19
- **Best instance:** :8188 (missing 10)
  - :8188: 10 missing (10 external: ApplyControlNet, CannyEdge_Preprocessor, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply)
  - :8189: 10 missing (10 external: ApplyControlNet, CannyEdge_Preprocessor, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply)
  - :8190: 11 missing (10 external: ApplyControlNet, CannyEdge_Preprocessor, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply)
  - :8191: 10 missing (10 external: ApplyControlNet, CannyEdge_Preprocessor, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply)
  - :8192: 11 missing (10 external: ApplyControlNet, CannyEdge_Preprocessor, DepthAnything_Preprocessor, HED_Preprocessor, IPAdapterApply)

### comfyui_SRPO-workflow-quantization-with-image-to-image.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 27
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 3 missing (1 external: MarkdownNote)
  - :8190: 6 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 12 missing (1 external: MarkdownNote)

### comfyui_unreal_postgrading.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 9
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### comfyui_unreal_storyboard.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 6
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### 35 ComfyUI - Cambio de Fondo_fixed.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 31
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: Fast Groups Bypasser (rgthree), GetNode, SetNode)
  - :8189: 6 missing (3 external: Fast Groups Bypasser (rgthree), GetNode, SetNode)
  - :8190: 11 missing (3 external: Fast Groups Bypasser (rgthree), GetNode, SetNode)
  - :8191: 3 missing (3 external: Fast Groups Bypasser (rgthree), GetNode, SetNode)
  - :8192: 13 missing (3 external: Fast Groups Bypasser (rgthree), GetNode, SetNode)

### Cambia_Fondos_CreaEscenarios_Flux_ControlNet - copia.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 30
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: GetNode, Note, SetNode)
  - :8189: 6 missing (3 external: GetNode, Note, SetNode)
  - :8190: 10 missing (3 external: GetNode, Note, SetNode)
  - :8191: 3 missing (3 external: GetNode, Note, SetNode)
  - :8192: 12 missing (3 external: GetNode, Note, SetNode)

### Cambia_Fondos_CreaEscenarios_Flux_ControlNet_FIXED.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 31
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: GetNode, Note, SetNode)
  - :8189: 6 missing (3 external: GetNode, Note, SetNode)
  - :8190: 11 missing (3 external: GetNode, Note, SetNode)
  - :8191: 3 missing (3 external: GetNode, Note, SetNode)
  - :8192: 13 missing (3 external: GetNode, Note, SetNode)

### Cambia_Fondos_CreaEscenarios_Flux_ControlNet_OK_fixed_NORMALIZED.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 31
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: GetNode, Note, SetNode)
  - :8189: 6 missing (3 external: GetNode, Note, SetNode)
  - :8190: 11 missing (3 external: GetNode, Note, SetNode)
  - :8191: 3 missing (3 external: GetNode, Note, SetNode)
  - :8192: 13 missing (3 external: GetNode, Note, SetNode)

### Advanced Flux Outfit Changer.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 20
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 3 missing
  - :8190: 4 missing
  - :8191: 0 missing
  - :8192: 7 missing

### Cambio_Ropa_FLUX_simple.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 19
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Reroute)
  - :8189: 4 missing (1 external: Reroute)
  - :8190: 4 missing (1 external: Reroute)
  - :8191: 1 missing (1 external: Reroute)
  - :8192: 4 missing (1 external: Reroute)

### Básico_FluxFP8_Capitulo6.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 8
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: MarkdownNote, Note)
  - :8189: 2 missing (2 external: MarkdownNote, Note)
  - :8190: 2 missing (2 external: MarkdownNote, Note)
  - :8191: 2 missing (2 external: MarkdownNote, Note)
  - :8192: 2 missing (2 external: MarkdownNote, Note)

### CreacionDepth_Capitulo11.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 15
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 1 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 1 missing (1 external: MarkdownNote)

### FluxCanny_Capitulo11.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 13
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 1 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 1 missing (1 external: MarkdownNote)

### FluxDepth_Capitulo11 (1).json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 12
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 1 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 1 missing (1 external: MarkdownNote)

### FluxInpainting_Capitulo10.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 12
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 1 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 1 missing (1 external: MarkdownNote)

### FluxLORA_Capitulo13.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### FluxOutpainting_Capitulo10.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 13
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 1 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 1 missing (1 external: MarkdownNote)

### Flux_ClipTextEncodeFlux_Capitulo7.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### flux_lora_train_Capitulo14.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 24
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: GetNode, Note, SetNode)
  - :8189: 21 missing (3 external: GetNode, Note, SetNode)
  - :8190: 15 missing (3 external: GetNode, Note, SetNode)
  - :8191: 15 missing (3 external: GetNode, Note, SetNode)
  - :8192: 22 missing (3 external: GetNode, Note, SetNode)

### hidream_e1_Capitulo17.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 18
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: MarkdownNote, PrimitiveNode, Reroute)
  - :8189: 3 missing (3 external: MarkdownNote, PrimitiveNode, Reroute)
  - :8190: 3 missing (3 external: MarkdownNote, PrimitiveNode, Reroute)
  - :8191: 3 missing (3 external: MarkdownNote, PrimitiveNode, Reroute)
  - :8192: 3 missing (3 external: MarkdownNote, PrimitiveNode, Reroute)

### hidream_i1_fast_Capitulo17.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 1 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 1 missing (1 external: MarkdownNote)

### hidream_i1_full_Capitulo17.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 1 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 1 missing (1 external: MarkdownNote)

### LatentSync-basic.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 9
- **Best instance:** :8188 (missing 4)
  - :8188: 4 missing (4 external: D_LatentSyncNode, D_VideoLengthAdjuster, GetNode, SetNode)
  - :8189: 4 missing (4 external: D_LatentSyncNode, D_VideoLengthAdjuster, GetNode, SetNode)
  - :8190: 4 missing (4 external: D_LatentSyncNode, D_VideoLengthAdjuster, GetNode, SetNode)
  - :8191: 4 missing (4 external: D_LatentSyncNode, D_VideoLengthAdjuster, GetNode, SetNode)
  - :8192: 8 missing (4 external: D_LatentSyncNode, D_VideoLengthAdjuster, GetNode, SetNode)

### Lyra-v6.json
- **Family:** dubbing_audio
- **Format:** ui
- **Required nodes:** 14
- **Best instance:** :8188 (missing 4)
  - :8188: 4 missing (4 external: Fast Groups Bypasser (rgthree), Note, PrimitiveNode, Reroute)
  - :8189: 4 missing (4 external: Fast Groups Bypasser (rgthree), Note, PrimitiveNode, Reroute)
  - :8190: 4 missing (4 external: Fast Groups Bypasser (rgthree), Note, PrimitiveNode, Reroute)
  - :8191: 4 missing (4 external: Fast Groups Bypasser (rgthree), Note, PrimitiveNode, Reroute)
  - :8192: 4 missing (4 external: Fast Groups Bypasser (rgthree), Note, PrimitiveNode, Reroute)

### NSFW SFW ACE Faceswap V1.0.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 62
- **Best instance:** :8188 (missing 6)
  - :8188: 6 missing (6 external: Fast Bypasser (rgthree), Fast Groups Bypasser (rgthree), Label (rgthree), Note, Reroute)
  - :8189: 23 missing (6 external: Fast Bypasser (rgthree), Fast Groups Bypasser (rgthree), Label (rgthree), Note, Reroute)
  - :8190: 22 missing (6 external: Fast Bypasser (rgthree), Fast Groups Bypasser (rgthree), Label (rgthree), Note, Reroute)
  - :8191: 6 missing (6 external: Fast Bypasser (rgthree), Fast Groups Bypasser (rgthree), Label (rgthree), Note, Reroute)
  - :8192: 36 missing (6 external: Fast Bypasser (rgthree), Fast Groups Bypasser (rgthree), Label (rgthree), Note, Reroute)

### z_image_turbo_Low_vram.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 13
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Note)
  - :8189: 1 missing (1 external: Note)
  - :8190: 1 missing (1 external: Note)
  - :8191: 1 missing (1 external: Note)
  - :8192: 2 missing (1 external: Note)

### 01_qwen_t2i_subgraphed_Capitulo18.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 3
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: 2c61139d-9c34-4c7e-a083-7a67cc4770ad, MarkdownNote)
  - :8189: 2 missing (2 external: 2c61139d-9c34-4c7e-a083-7a67cc4770ad, MarkdownNote)
  - :8190: 2 missing (2 external: 2c61139d-9c34-4c7e-a083-7a67cc4770ad, MarkdownNote)
  - :8191: 2 missing (2 external: 2c61139d-9c34-4c7e-a083-7a67cc4770ad, MarkdownNote)
  - :8192: 2 missing (2 external: 2c61139d-9c34-4c7e-a083-7a67cc4770ad, MarkdownNote)

### image_qwen_image_controlnet_patch_Capitulo18.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 18
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: MarkdownNote, Note)
  - :8189: 2 missing (2 external: MarkdownNote, Note)
  - :8190: 2 missing (2 external: MarkdownNote, Note)
  - :8191: 2 missing (2 external: MarkdownNote, Note)
  - :8192: 2 missing (2 external: MarkdownNote, Note)

### image_qwen_image_edit_2509_Capitulo18.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 16
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: MarkdownNote, c46c74c1-cfc4-41eb-81a8-9c6701737ef6)
  - :8189: 2 missing (2 external: MarkdownNote, c46c74c1-cfc4-41eb-81a8-9c6701737ef6)
  - :8190: 2 missing (2 external: MarkdownNote, c46c74c1-cfc4-41eb-81a8-9c6701737ef6)
  - :8191: 2 missing (2 external: MarkdownNote, c46c74c1-cfc4-41eb-81a8-9c6701737ef6)
  - :8192: 2 missing (2 external: MarkdownNote, c46c74c1-cfc4-41eb-81a8-9c6701737ef6)

### image_qwen_image_instantx_controlnet_Capitulo18.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 19
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: MarkdownNote, Note, ef3b4b73-ce32-4a60-a60e-d7f278bf6b14)
  - :8189: 3 missing (3 external: MarkdownNote, Note, ef3b4b73-ce32-4a60-a60e-d7f278bf6b14)
  - :8190: 3 missing (3 external: MarkdownNote, Note, ef3b4b73-ce32-4a60-a60e-d7f278bf6b14)
  - :8191: 3 missing (3 external: MarkdownNote, Note, ef3b4b73-ce32-4a60-a60e-d7f278bf6b14)
  - :8192: 3 missing (3 external: MarkdownNote, Note, ef3b4b73-ce32-4a60-a60e-d7f278bf6b14)

### Roda-ReactiveDepth-V30.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 17
- **Best instance:** :8188 (missing 10)
  - :8188: 10 missing (10 external: AudioFeatureExtractor, Depthflow, DepthflowEffectDOF, DepthflowEffectVignette, DepthflowMotionPresetOrbital)
  - :8189: 11 missing (10 external: AudioFeatureExtractor, Depthflow, DepthflowEffectDOF, DepthflowEffectVignette, DepthflowMotionPresetOrbital)
  - :8190: 12 missing (10 external: AudioFeatureExtractor, Depthflow, DepthflowEffectDOF, DepthflowEffectVignette, DepthflowMotionPresetOrbital)
  - :8191: 10 missing (10 external: AudioFeatureExtractor, Depthflow, DepthflowEffectDOF, DepthflowEffectVignette, DepthflowMotionPresetOrbital)
  - :8192: 16 missing (10 external: AudioFeatureExtractor, Depthflow, DepthflowEffectDOF, DepthflowEffectVignette, DepthflowMotionPresetOrbital)

### Roda-ReactiveVideo-Scrubber-V20.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 17
- **Best instance:** :8188 (missing 9)
  - :8188: 9 missing (9 external: AudioFeatureExtractor, AudioSeparator, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio, FlexVideoDirection)
  - :8189: 11 missing (9 external: AudioFeatureExtractor, AudioSeparator, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio, FlexVideoDirection)
  - :8190: 11 missing (9 external: AudioFeatureExtractor, AudioSeparator, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio, FlexVideoDirection)
  - :8191: 9 missing (9 external: AudioFeatureExtractor, AudioSeparator, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio, FlexVideoDirection)
  - :8192: 17 missing (9 external: AudioFeatureExtractor, AudioSeparator, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio, FlexVideoDirection)

### Roda-ReactScrub-GIMMSync-V30.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 22
- **Best instance:** :8188 (missing 11)
  - :8188: 11 missing (11 external: AudioFeatureExtractor, AudioSeparator, DownloadAndLoadGIMMVFIModel, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio)
  - :8189: 14 missing (11 external: AudioFeatureExtractor, AudioSeparator, DownloadAndLoadGIMMVFIModel, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio)
  - :8190: 14 missing (11 external: AudioFeatureExtractor, AudioSeparator, DownloadAndLoadGIMMVFIModel, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio)
  - :8191: 11 missing (11 external: AudioFeatureExtractor, AudioSeparator, DownloadAndLoadGIMMVFIModel, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio)
  - :8192: 22 missing (11 external: AudioFeatureExtractor, AudioSeparator, DownloadAndLoadGIMMVFIModel, DownloadOpenUnmixModel, EmptyImageAndMaskFromAudio)

### SKIN_FIX_Capitulo16.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 37
- **Best instance:** :8188 (missing 7)
  - :8188: 7 missing (7 external: FaceParse(FaceParsing), FaceParsingModelLoader(FaceParsing), FaceParsingProcessorLoader(FaceParsing), FaceParsingResultsParser(FaceParsing), Fast Groups Bypasser (rgthree))
  - :8189: 13 missing (7 external: FaceParse(FaceParsing), FaceParsingModelLoader(FaceParsing), FaceParsingProcessorLoader(FaceParsing), FaceParsingResultsParser(FaceParsing), Fast Groups Bypasser (rgthree))
  - :8190: 14 missing (7 external: FaceParse(FaceParsing), FaceParsingModelLoader(FaceParsing), FaceParsingProcessorLoader(FaceParsing), FaceParsingResultsParser(FaceParsing), Fast Groups Bypasser (rgthree))
  - :8191: 7 missing (7 external: FaceParse(FaceParsing), FaceParsingModelLoader(FaceParsing), FaceParsingProcessorLoader(FaceParsing), FaceParsingResultsParser(FaceParsing), Fast Groups Bypasser (rgthree))
  - :8192: 19 missing (7 external: FaceParse(FaceParsing), FaceParsingModelLoader(FaceParsing), FaceParsingProcessorLoader(FaceParsing), FaceParsingResultsParser(FaceParsing), Fast Groups Bypasser (rgthree))

### n8n_workflow_ue5_comfyui.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 4
- **Best instance:** :8188 (missing 4)
  - :8188: 4 missing (4 external: n8n-nodes-base.function, n8n-nodes-base.httpRequest, n8n-nodes-base.telegram, n8n-nodes-base.webhook)
  - :8189: 4 missing (4 external: n8n-nodes-base.function, n8n-nodes-base.httpRequest, n8n-nodes-base.telegram, n8n-nodes-base.webhook)
  - :8190: 4 missing (4 external: n8n-nodes-base.function, n8n-nodes-base.httpRequest, n8n-nodes-base.telegram, n8n-nodes-base.webhook)
  - :8191: 4 missing (4 external: n8n-nodes-base.function, n8n-nodes-base.httpRequest, n8n-nodes-base.telegram, n8n-nodes-base.webhook)
  - :8192: 4 missing (4 external: n8n-nodes-base.function, n8n-nodes-base.httpRequest, n8n-nodes-base.telegram, n8n-nodes-base.webhook)

### comfyui_previs_wan22.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 9
- **Best instance:** :8188 (missing 7)
  - :8188: 7 missing (7 external: TextInput, WAN22_CameraHint, WAN22_EncodePrompt, WAN22_GenerateVideo, WAN22_ModelLoader)
  - :8189: 7 missing (7 external: TextInput, WAN22_CameraHint, WAN22_EncodePrompt, WAN22_GenerateVideo, WAN22_ModelLoader)
  - :8190: 7 missing (7 external: TextInput, WAN22_CameraHint, WAN22_EncodePrompt, WAN22_GenerateVideo, WAN22_ModelLoader)
  - :8191: 7 missing (7 external: TextInput, WAN22_CameraHint, WAN22_EncodePrompt, WAN22_GenerateVideo, WAN22_ModelLoader)
  - :8192: 8 missing (7 external: TextInput, WAN22_CameraHint, WAN22_EncodePrompt, WAN22_GenerateVideo, WAN22_ModelLoader)

### comfyui_storyboard_animado.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: VHS_KeyframeAnimator)
  - :8189: 1 missing (1 external: VHS_KeyframeAnimator)
  - :8190: 1 missing (1 external: VHS_KeyframeAnimator)
  - :8191: 1 missing (1 external: VHS_KeyframeAnimator)
  - :8192: 3 missing (1 external: VHS_KeyframeAnimator)

### Hiresfix_Capitulo15.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 12
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: MarkdownNote)
  - :8189: 1 missing (1 external: MarkdownNote)
  - :8190: 1 missing (1 external: MarkdownNote)
  - :8191: 1 missing (1 external: MarkdownNote)
  - :8192: 1 missing (1 external: MarkdownNote)

### Upscaler_Basic_Capitulo15.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 5
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: SeedVR2BlockSwap, SeedVR2TilingUpscaler)
  - :8189: 2 missing (2 external: SeedVR2BlockSwap, SeedVR2TilingUpscaler)
  - :8190: 2 missing (2 external: SeedVR2BlockSwap, SeedVR2TilingUpscaler)
  - :8191: 2 missing (2 external: SeedVR2BlockSwap, SeedVR2TilingUpscaler)
  - :8192: 3 missing (2 external: SeedVR2BlockSwap, SeedVR2TilingUpscaler)

### Upscale_workflow_4x-ESRGAN_Capitulo15.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 4
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### A 1080 a 2k_wan2.2.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 9
- **Best instance:** :8188 (missing 6)
  - :8188: 6 missing (6 external: ColorAdjustmentSoft, KSampler_img2img, LoadImageBatchFromFolder, PreDenoise_Soft, SaveImage_TIFF16)
  - :8189: 6 missing (6 external: ColorAdjustmentSoft, KSampler_img2img, LoadImageBatchFromFolder, PreDenoise_Soft, SaveImage_TIFF16)
  - :8190: 6 missing (6 external: ColorAdjustmentSoft, KSampler_img2img, LoadImageBatchFromFolder, PreDenoise_Soft, SaveImage_TIFF16)
  - :8191: 6 missing (6 external: ColorAdjustmentSoft, KSampler_img2img, LoadImageBatchFromFolder, PreDenoise_Soft, SaveImage_TIFF16)
  - :8192: 6 missing (6 external: ColorAdjustmentSoft, KSampler_img2img, LoadImageBatchFromFolder, PreDenoise_Soft, SaveImage_TIFF16)

### A 1080 a 2k_wan_2.2.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 8
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: ImageAdjustments)
  - :8189: 1 missing (1 external: ImageAdjustments)
  - :8190: 1 missing (1 external: ImageAdjustments)
  - :8191: 1 missing (1 external: ImageAdjustments)
  - :8192: 1 missing (1 external: ImageAdjustments)

### A_1080_a_2K_wan2.2_graph.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 9
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: ImageAdjustments)
  - :8189: 1 missing (1 external: ImageAdjustments)
  - :8190: 1 missing (1 external: ImageAdjustments)
  - :8191: 1 missing (1 external: ImageAdjustments)
  - :8192: 1 missing (1 external: ImageAdjustments)

### B 1080 a 2k flux.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: ImageResize, LoadVAE, RealCUGAN)
  - :8189: 3 missing (3 external: ImageResize, LoadVAE, RealCUGAN)
  - :8190: 3 missing (3 external: ImageResize, LoadVAE, RealCUGAN)
  - :8191: 3 missing (3 external: ImageResize, LoadVAE, RealCUGAN)
  - :8192: 3 missing (3 external: ImageResize, LoadVAE, RealCUGAN)

### B 1080 a 2k fluxv2.json
- **Family:** image_still
- **Format:** api
- **Required nodes:** 3
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: ImageResize)
  - :8189: 1 missing (1 external: ImageResize)
  - :8190: 1 missing (1 external: ImageResize)
  - :8191: 1 missing (1 external: ImageResize)
  - :8192: 1 missing (1 external: ImageResize)

### image_flux2_text_to_image(API).json
- **Family:** image_still
- **Format:** api
- **Required nodes:** 13
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### image_z_image_turbo.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 3
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: MarkdownNote, f2fdebf6-dfaf-43b6-9eb2-7f70613cfdc1)
  - :8189: 2 missing (2 external: MarkdownNote, f2fdebf6-dfaf-43b6-9eb2-7f70613cfdc1)
  - :8190: 2 missing (2 external: MarkdownNote, f2fdebf6-dfaf-43b6-9eb2-7f70613cfdc1)
  - :8191: 2 missing (2 external: MarkdownNote, f2fdebf6-dfaf-43b6-9eb2-7f70613cfdc1)
  - :8192: 2 missing (2 external: MarkdownNote, f2fdebf6-dfaf-43b6-9eb2-7f70613cfdc1)

### PASO_3_n8n_batch_frames_comfyui.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 8
- **Best instance:** :8188 (missing 8)
  - :8188: 8 missing (8 external: n8n-nodes-base.code, n8n-nodes-base.httpRequest, n8n-nodes-base.if, n8n-nodes-base.readWriteFile, n8n-nodes-base.set)
  - :8189: 8 missing (8 external: n8n-nodes-base.code, n8n-nodes-base.httpRequest, n8n-nodes-base.if, n8n-nodes-base.readWriteFile, n8n-nodes-base.set)
  - :8190: 8 missing (8 external: n8n-nodes-base.code, n8n-nodes-base.httpRequest, n8n-nodes-base.if, n8n-nodes-base.readWriteFile, n8n-nodes-base.set)
  - :8191: 8 missing (8 external: n8n-nodes-base.code, n8n-nodes-base.httpRequest, n8n-nodes-base.if, n8n-nodes-base.readWriteFile, n8n-nodes-base.set)
  - :8192: 8 missing (8 external: n8n-nodes-base.code, n8n-nodes-base.httpRequest, n8n-nodes-base.if, n8n-nodes-base.readWriteFile, n8n-nodes-base.set)

### PASO_4_ComfyUI_RESTO_core_img2img_upscale.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 9
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### PASO_5_n8n_assemble_frames_ffmpeg.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 3
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: n8n-nodes-base.executeCommand, n8n-nodes-base.manualTrigger, n8n-nodes-base.set)
  - :8189: 3 missing (3 external: n8n-nodes-base.executeCommand, n8n-nodes-base.manualTrigger, n8n-nodes-base.set)
  - :8190: 3 missing (3 external: n8n-nodes-base.executeCommand, n8n-nodes-base.manualTrigger, n8n-nodes-base.set)
  - :8191: 3 missing (3 external: n8n-nodes-base.executeCommand, n8n-nodes-base.manualTrigger, n8n-nodes-base.set)
  - :8192: 3 missing (3 external: n8n-nodes-base.executeCommand, n8n-nodes-base.manualTrigger, n8n-nodes-base.set)

### prueba cine 2.json
- **Family:** image_still
- **Format:** api
- **Required nodes:** 9
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### prueba cine wan.json
- **Family:** image_still
- **Format:** api
- **Required nodes:** 10
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### prueba cine.json
- **Family:** image_still
- **Format:** api
- **Required nodes:** 10
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### prueba.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 4)
  - :8188: 4 missing (4 external: ImageResize, LoadImageBatch, LoadVAE, RealCUGAN)
  - :8189: 4 missing (4 external: ImageResize, LoadImageBatch, LoadVAE, RealCUGAN)
  - :8190: 4 missing (4 external: ImageResize, LoadImageBatch, LoadVAE, RealCUGAN)
  - :8191: 4 missing (4 external: ImageResize, LoadImageBatch, LoadVAE, RealCUGAN)
  - :8192: 4 missing (4 external: ImageResize, LoadImageBatch, LoadVAE, RealCUGAN)

### restauracion_foto_base.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 6
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### restauracion_video_frames_base.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 6
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: LoadImageBatch)
  - :8189: 1 missing (1 external: LoadImageBatch)
  - :8190: 1 missing (1 external: LoadImageBatch)
  - :8191: 1 missing (1 external: LoadImageBatch)
  - :8192: 1 missing (1 external: LoadImageBatch)

### restore_1.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 15
- **Best instance:** :8188 (missing 8)
  - :8188: 8 missing (8 external: BatchDone, Bloom, FluxKSampler, Grain, LUTApply)
  - :8189: 9 missing (8 external: BatchDone, Bloom, FluxKSampler, Grain, LUTApply)
  - :8190: 9 missing (8 external: BatchDone, Bloom, FluxKSampler, Grain, LUTApply)
  - :8191: 8 missing (8 external: BatchDone, Bloom, FluxKSampler, Grain, LUTApply)
  - :8192: 9 missing (8 external: BatchDone, Bloom, FluxKSampler, Grain, LUTApply)

### ruido, arañazos, suavizado, mejora facial, color & upscale.json
- **Family:** restoration
- **Format:** ui
- **Required nodes:** 9
- **Best instance:** :8188 (missing 6)
  - :8188: 6 missing (6 external: ColorFix, FACE_RESTORE, ImageDenoise, ImageScratchRepair, Sharpen)
  - :8189: 6 missing (6 external: ColorFix, FACE_RESTORE, ImageDenoise, ImageScratchRepair, Sharpen)
  - :8190: 6 missing (6 external: ColorFix, FACE_RESTORE, ImageDenoise, ImageScratchRepair, Sharpen)
  - :8191: 6 missing (6 external: ColorFix, FACE_RESTORE, ImageDenoise, ImageScratchRepair, Sharpen)
  - :8192: 6 missing (6 external: ColorFix, FACE_RESTORE, ImageDenoise, ImageScratchRepair, Sharpen)

### Seedance2.0_First-Last-Frame _to_Video.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 3
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 1 missing
  - :8190: 1 missing
  - :8191: 1 missing
  - :8192: 1 missing

### seedance20_094c40ffb14f.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 6
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: ByteDanceCreateImageAsset, MarkdownNote)
  - :8189: 3 missing (2 external: ByteDanceCreateImageAsset, MarkdownNote)
  - :8190: 3 missing (2 external: ByteDanceCreateImageAsset, MarkdownNote)
  - :8191: 3 missing (2 external: ByteDanceCreateImageAsset, MarkdownNote)
  - :8192: 3 missing (2 external: ByteDanceCreateImageAsset, MarkdownNote)

### Seedance_2.0_Reference_to_Video.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 3
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 1 missing
  - :8190: 1 missing
  - :8191: 1 missing
  - :8192: 1 missing

### upscale_supir_cine.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 3
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: SUPIRUpscale)
  - :8189: 1 missing (1 external: SUPIRUpscale)
  - :8190: 1 missing (1 external: SUPIRUpscale)
  - :8191: 1 missing (1 external: SUPIRUpscale)
  - :8192: 1 missing (1 external: SUPIRUpscale)

### upscale_video_supir_batch.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 3
- **Best instance:** :8188 (missing 2)
  - :8188: 2 missing (2 external: LoadImageBatch, SUPIRUpscale)
  - :8189: 2 missing (2 external: LoadImageBatch, SUPIRUpscale)
  - :8190: 2 missing (2 external: LoadImageBatch, SUPIRUpscale)
  - :8191: 2 missing (2 external: LoadImageBatch, SUPIRUpscale)
  - :8192: 2 missing (2 external: LoadImageBatch, SUPIRUpscale)

### up_to_4K.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 9
- **Best instance:** :8188 (missing 5)
  - :8188: 5 missing (5 external: BatchDone, Bloom, FluxKSampler, Grain, LUTApply)
  - :8189: 6 missing (5 external: BatchDone, Bloom, FluxKSampler, Grain, LUTApply)
  - :8190: 6 missing (5 external: BatchDone, Bloom, FluxKSampler, Grain, LUTApply)
  - :8191: 5 missing (5 external: BatchDone, Bloom, FluxKSampler, Grain, LUTApply)
  - :8192: 6 missing (5 external: BatchDone, Bloom, FluxKSampler, Grain, LUTApply)

### WAN + SDXL + Flux + LUT + Grain + Bloom + Batch.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 15
- **Best instance:** :8188 (missing 8)
  - :8188: 8 missing (8 external: BatchDone, Bloom, FluxKSampler, Grain, LUTApply)
  - :8189: 9 missing (8 external: BatchDone, Bloom, FluxKSampler, Grain, LUTApply)
  - :8190: 9 missing (8 external: BatchDone, Bloom, FluxKSampler, Grain, LUTApply)
  - :8191: 8 missing (8 external: BatchDone, Bloom, FluxKSampler, Grain, LUTApply)
  - :8192: 9 missing (8 external: BatchDone, Bloom, FluxKSampler, Grain, LUTApply)

### WAN 2.2 → LUT 2383 → TIFF 2K.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 9
- **Best instance:** :8188 (missing 5)
  - :8188: 5 missing (5 external: FluxKSampler, LUTApply, WAN22_HighNoise, WAN22_LowNoise, WAN_PreProcess)
  - :8189: 6 missing (5 external: FluxKSampler, LUTApply, WAN22_HighNoise, WAN22_LowNoise, WAN_PreProcess)
  - :8190: 6 missing (5 external: FluxKSampler, LUTApply, WAN22_HighNoise, WAN22_LowNoise, WAN_PreProcess)
  - :8191: 5 missing (5 external: FluxKSampler, LUTApply, WAN22_HighNoise, WAN22_LowNoise, WAN_PreProcess)
  - :8192: 6 missing (5 external: FluxKSampler, LUTApply, WAN22_HighNoise, WAN22_LowNoise, WAN_PreProcess)

### Wan Refine Flux.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 42
- **Best instance:** :8188 (missing 9)
  - :8188: 9 missing (6 external: FastFilmGrain, ImageComparer, Image_Size_Extractor, LoadImageExtended, Note)
  - :8189: 13 missing (6 external: FastFilmGrain, ImageComparer, Image_Size_Extractor, LoadImageExtended, Note)
  - :8190: 15 missing (6 external: FastFilmGrain, ImageComparer, Image_Size_Extractor, LoadImageExtended, Note)
  - :8191: 9 missing (6 external: FastFilmGrain, ImageComparer, Image_Size_Extractor, LoadImageExtended, Note)
  - :8192: 24 missing (6 external: FastFilmGrain, ImageComparer, Image_Size_Extractor, LoadImageExtended, Note)

### wan2.2 renstauracion fotos.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 11
- **Best instance:** :8188 (missing 7)
  - :8188: 7 missing (7 external: UpscaleImage, WAN22Loader, WAN22_Infer, WAS_Color_Correct, WAS_Image_Denoise)
  - :8189: 7 missing (7 external: UpscaleImage, WAN22Loader, WAN22_Infer, WAS_Color_Correct, WAS_Image_Denoise)
  - :8190: 7 missing (7 external: UpscaleImage, WAN22Loader, WAN22_Infer, WAS_Color_Correct, WAS_Image_Denoise)
  - :8191: 7 missing (7 external: UpscaleImage, WAN22Loader, WAN22_Infer, WAS_Color_Correct, WAS_Image_Denoise)
  - :8192: 7 missing (7 external: UpscaleImage, WAN22Loader, WAN22_Infer, WAS_Color_Correct, WAS_Image_Denoise)

### wan2.2 renstauracion fotos_V2.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 8
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: ImageResize)
  - :8189: 1 missing (1 external: ImageResize)
  - :8190: 1 missing (1 external: ImageResize)
  - :8191: 1 missing (1 external: ImageResize)
  - :8192: 1 missing (1 external: ImageResize)

### wan2.2 renstauracion fotos_V2_FIXED.json
- **Family:** image_still
- **Format:** ui
- **Required nodes:** 8
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: ImageResize)
  - :8189: 1 missing (1 external: ImageResize)
  - :8190: 1 missing (1 external: ImageResize)
  - :8191: 1 missing (1 external: ImageResize)
  - :8192: 1 missing (1 external: ImageResize)

### wan22_animate_preprocess_MDMZ_071025.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 34
- **Best instance:** :8190 (missing 9)
  - :8188: 20 missing (4 external: GetNode, MarkdownNote, Note, SetNode)
  - :8189: 11 missing (4 external: GetNode, MarkdownNote, Note, SetNode)
  - :8190: 9 missing (4 external: GetNode, MarkdownNote, Note, SetNode)
  - :8191: 20 missing (4 external: GetNode, MarkdownNote, Note, SetNode)
  - :8192: 31 missing (4 external: GetNode, MarkdownNote, Note, SetNode)

### wanvideo_multitalk_test_02.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 22
- **Best instance:** :8189 (missing 1)
  - :8188: 16 missing
  - :8189: 1 missing
  - :8190: 2 missing
  - :8191: 16 missing
  - :8192: 18 missing

### WAN_RESTO_FOTO_PASO_1.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 8
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### WAN_RESTO_VIDEO_PASO_2.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 10
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### WAN_SCAIL_workflow.json
- **Family:** video_cine
- **Format:** ui
- **Required nodes:** 36
- **Best instance:** :8190 (missing 8)
  - :8188: 26 missing (7 external: GetNode, MarkdownNote, Note, PoseDetectionVitPoseToDWPose, RenderNLFPoses)
  - :8189: 13 missing (7 external: GetNode, MarkdownNote, Note, PoseDetectionVitPoseToDWPose, RenderNLFPoses)
  - :8190: 8 missing (7 external: GetNode, MarkdownNote, Note, PoseDetectionVitPoseToDWPose, RenderNLFPoses)
  - :8191: 26 missing (7 external: GetNode, MarkdownNote, Note, PoseDetectionVitPoseToDWPose, RenderNLFPoses)
  - :8192: 34 missing (7 external: GetNode, MarkdownNote, Note, PoseDetectionVitPoseToDWPose, RenderNLFPoses)

### 2024-04-07 cascade+controlnet 完美放大图像.png
- **Family:** image_still
- **Format:** embedded
- **Required nodes:** 10
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 0 missing

### Kazitorials-avatar-generator.png
- **Family:** image_still
- **Format:** embedded
- **Required nodes:** 12
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 3 missing
  - :8190: 3 missing
  - :8191: 0 missing
  - :8192: 3 missing

### SRPO-workflow.png
- **Family:** image_still
- **Format:** embedded
- **Required nodes:** 15
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: PrimitiveNode)
  - :8189: 1 missing (1 external: PrimitiveNode)
  - :8190: 1 missing (1 external: PrimitiveNode)
  - :8191: 1 missing (1 external: PrimitiveNode)
  - :8192: 1 missing (1 external: PrimitiveNode)

### Tpose-Template.png
- **Family:** image_still
- **Format:** embedded
- **Required nodes:** 34
- **Best instance:** :8188 (missing 5)
  - :8188: 5 missing (5 external: AspectSize, DF_Text_Box, Fast Groups Bypasser (rgthree), Note, Reroute)
  - :8189: 18 missing (5 external: AspectSize, DF_Text_Box, Fast Groups Bypasser (rgthree), Note, Reroute)
  - :8190: 17 missing (5 external: AspectSize, DF_Text_Box, Fast Groups Bypasser (rgthree), Note, Reroute)
  - :8191: 5 missing (5 external: AspectSize, DF_Text_Box, Fast Groups Bypasser (rgthree), Note, Reroute)
  - :8192: 25 missing (5 external: AspectSize, DF_Text_Box, Fast Groups Bypasser (rgthree), Note, Reroute)

### Wan2-2-Ultimate-Text-To-Image-fast-render-cinematic-quality.png
- **Family:** image_still
- **Format:** embedded
- **Required nodes:** 11
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Note)
  - :8189: 2 missing (1 external: Note)
  - :8190: 2 missing (1 external: Note)
  - :8191: 1 missing (1 external: Note)
  - :8192: 2 missing (1 external: Note)

### flux_schnell_example.png
- **Family:** image_still
- **Format:** embedded
- **Required nodes:** 13
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: Note)
  - :8189: 1 missing (1 external: Note)
  - :8190: 1 missing (1 external: Note)
  - :8191: 1 missing (1 external: Note)
  - :8192: 1 missing (1 external: Note)

### sdxl-recommended-res-calc_upscale-case.png
- **Family:** image_still
- **Format:** embedded
- **Required nodes:** 17
- **Best instance:** :8188 (missing 4)
  - :8188: 4 missing (4 external: Note, PrimitiveNode, RecommendedResCalc, Reroute)
  - :8189: 4 missing (4 external: Note, PrimitiveNode, RecommendedResCalc, Reroute)
  - :8190: 4 missing (4 external: Note, PrimitiveNode, RecommendedResCalc, Reroute)
  - :8191: 4 missing (4 external: Note, PrimitiveNode, RecommendedResCalc, Reroute)
  - :8192: 4 missing (4 external: Note, PrimitiveNode, RecommendedResCalc, Reroute)

### wave-speed-flux.png
- **Family:** image_still
- **Format:** embedded
- **Required nodes:** 15
- **Best instance:** :8188 (missing 3)
  - :8188: 3 missing (3 external: ApplyFBCacheOnModel, PrimitiveNode, SetNode)
  - :8189: 3 missing (3 external: ApplyFBCacheOnModel, PrimitiveNode, SetNode)
  - :8190: 3 missing (3 external: ApplyFBCacheOnModel, PrimitiveNode, SetNode)
  - :8191: 3 missing (3 external: ApplyFBCacheOnModel, PrimitiveNode, SetNode)
  - :8192: 3 missing (3 external: ApplyFBCacheOnModel, PrimitiveNode, SetNode)

### 2025-01-07 latent sync唇形拟合.png
- **Family:** video_cine
- **Format:** embedded
- **Required nodes:** 4
- **Best instance:** :8188 (missing 1)
  - :8188: 1 missing (1 external: D_LatentSyncNode)
  - :8189: 1 missing (1 external: D_LatentSyncNode)
  - :8190: 1 missing (1 external: D_LatentSyncNode)
  - :8191: 1 missing (1 external: D_LatentSyncNode)
  - :8192: 3 missing (1 external: D_LatentSyncNode)

### 2025-01-15 nvidia cosmos workflow.png
- **Family:** video_cine
- **Format:** embedded
- **Required nodes:** 8
- **Best instance:** :8188 (missing 0)
  - :8188: 0 missing
  - :8189: 0 missing
  - :8190: 0 missing
  - :8191: 0 missing
  - :8192: 1 missing

### Mo-Cha-Replace-Anyone-in-a-Video.png
- **Family:** video_cine
- **Format:** embedded
- **Required nodes:** 26
- **Best instance:** :8190 (missing 6)
  - :8188: 14 missing (4 external: GetNode, MarkdownNote, Note, SetNode)
  - :8189: 9 missing (4 external: GetNode, MarkdownNote, Note, SetNode)
  - :8190: 6 missing (4 external: GetNode, MarkdownNote, Note, SetNode)
  - :8191: 14 missing (4 external: GetNode, MarkdownNote, Note, SetNode)
  - :8192: 23 missing (4 external: GetNode, MarkdownNote, Note, SetNode)
