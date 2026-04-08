# SERVICIOS_CINE - Experimental Workflow Assembler

## Overview

Prototype module for semi-automatic workflow assembly.
**ALPHA - Not for production use.**

## Activation

Enable in `config/config.yaml`:
```yaml
experimental:
  enabled: true
  admin_key: "your-secret-key"
```

## Endpoints

### List Modules
```bash
GET /api/workflows/experimental/modules
```

### Get Module Info
```bash
GET /api/workflows/experimental/modules/{module_id}
```

### Assemble Workflow
```bash
POST /api/workflows/experimental/assemble
```

## Authentication

Requires one of:
- `X-Admin-Key: admin-secret-key-change-me` header
- `X-Experimental-Enabled: true` header

## Available Modules

| Module ID | Name | Category | Dependencies |
|-----------|------|----------|--------------|
| upscale_2x | Upscale 2x | image | image_output |
| face_detail | Face Detail | image | image_output |
| color_correct | Color Correction | image | image_output |
| style_transfer | Style Transfer | image | image_output |
| video_interpolation | Video Interpolation | video | video_output |
| video_stabilize | Video Stabilization | video | video_output |
| audio_enhance | Audio Enhancement | audio | audio_output |
| bg_remove | Background Removal | image | image_output |

## Examples

### List Modules
```bash
curl http://localhost:8000/api/workflows/experimental/modules \
  -H "X-Admin-Key: admin-secret-key-change-me"
```

Response:
```json
{
  "modules": [
    {"module_id": "upscale_2x", "name": "Upscale 2x", "category": "image", "dependencies": ["image_output"]},
    {"module_id": "face_detail", "name": "Face Detail", "category": "image", "dependencies": ["image_output"]}
  ],
  "warning": "EXPERIMENTAL - Alpha testing only"
}
```

### Assemble Workflow
```bash
curl -X POST http://localhost:8000/api/workflows/experimental/assemble \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: admin-secret-key-change-me" \
  -d '{
    "base_workflow": "still_text_to_image_pro",
    "modules": ["upscale_2x", "color_correct"],
    "options": {
      "upscale_2x": {"model_name": "real-esrgan-4x.pth"}
    }
  }'
```

Response:
```json
{
  "success": true,
  "workflow": {
    "version": "0.1.0-alpha",
    "experimental": true,
    "base_workflow": "still_text_to_image_pro",
    "modules": ["upscale_2x", "color_correct"],
    "nodes": [
      {"id": "base_loader", "type": "CheckpointLoaderSimple"},
      {"id": "module_upscale_2x", "type": "ImageUpscaleWithModel", "module": true},
      {"id": "module_color_correct", "type": "ColorCorrect", "module": true},
      {"id": "output", "type": "SaveImage"}
    ]
  },
  "warnings": [
    "EXPERIMENTAL: This feature is in alpha testing",
    "Do not use in production environments"
  ],
  "errors": [],
  "stats": {"node_count": 4, "total_inputs": 3}
}
```

## Limitations

- Max 5 modules per workflow
- Max 50 nodes total
- No custom node types allowed
- No arbitrary code execution
- Dependencies must be satisfied

## Security

- Feature-flagged (disabled by default)
- Requires admin key or experimental header
- Validated module registry
- Graph validation before execution

## Status

```bash
curl http://localhost:8000/api/workflows/experimental/status \
  -H "X-Admin-Key: admin-secret-key-change-me"
```

```json
{
  "enabled": true,
  "alpha": true,
  "production_ready": false,
  "available_modules": 8,
  "max_modules": 5,
  "max_nodes": 50
}
```
