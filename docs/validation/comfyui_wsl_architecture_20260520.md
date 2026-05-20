# ComfyUI WSL/Linux Architecture — Local Development

## Date
2026-05-20

## Decision
ComfyUI instances run on WSL/Linux, **not** on Docker containers or Windows native.

## Rationale
- Backend CID runs on Docker/Linux.
- WSL/Linux provides native CUDA, PyTorch, and ComfyUI compatibility.
- Custom nodes and shell scripts work without WSL→Docker mount issues.
- Docker ComfyUI (`yanwk/comfyui-boot:cu130-slim-v2`) is **not recommended** due to:
  - Missing dependencies: `nunchaku`, `natsort`
  - Package conflict: `agents` (RL agents vs openai-agents)
  - Result: container crashes on startup (restart count >20 observed)
- Windows host remains as the host/anchor for WSL and Docker Desktop.

## Architecture

```
CID Backend (Docker container)
  → http://172.24.174.31:8188   still / storyboard  (ComfyUI v0.19.3)
  → http://172.24.174.31:8189   video / cine        (ComfyUI v0.14.1)
  → http://172.24.174.31:8190   dubbing / audio      (ComfyUI v0.13.0)
  → http://172.24.174.31:8191   restoration          (ComfyUI v0.13.0)
  → http://172.24.174.31:8192   3D                   (ComfyUI v0.17.0)
```

## Port Mapping

| Port | Instance | ComfyUI Version | Capabilities |
|------|----------|----------------|--------------|
| 8188 | still    | 0.19.3         | image_generation, image_to_image, inpainting, storyboard |
| 8189 | video    | 0.14.1         | text_to_video, image_to_video, video_to_video |
| 8190 | dubbing  | 0.13.0         | tts, voice_clone, audio_sync |
| 8191 | restoration | 0.13.0      | image/video restoration, conform, cleanup |
| 8192 | 3d       | 0.17.0         | 3d_generation, nerf, depth |

## Model & Output Paths

| Resource | Path |
|----------|------|
| Models | `/mnt/i/COMFYUI_OK/models` (I:\ drive) |
| Output hub | `/mnt/g/COMFYUI_HUB/output` (G:\ drive) |
| Workflows | `/mnt/g/COMFYUI_HUB/workflows` |
| Input | `/mnt/g/COMFYUI_HUB/input` |

## Configuration Files

All ComfyUI URLs must point to WSL IP in these files:

| File | Tracked | Purpose |
|------|---------|---------|
| `.env` | No (gitignored) | Local env overrides |
| `.env.example` | Yes | Template with `<WSL_IP>` placeholder |
| `compose.home.yml` | Yes | Docker Compose defaults |
| `src/config/instances.yml` | Yes | Backend instance registry |
| `src/config/instances_01.yml` | Yes | Alternative instance registry |

## Warning
- WSL IP (`172.24.174.31`) may change after restarting WSL or Windows.
- Update `.env` if the IP changes.
- To detect current IP: `hostname -I | awk '{print $1}'`
- Helper script: `scripts/dev/print_comfyui_wsl_env.sh` prints the required env vars.

## Docker ComfyUI (Deactivated)

Not recommended for local development. Documented here for future reference:

- Image: `yanwk/comfyui-boot:cu130-slim-v2`
- Service name: `servicios_cine-comfyui-still-1` on `ailinkcinema_private` network
- Has 56 checkpoints and 714 node types
- Crashes on startup due to missing `nunchaku`, `natsort`, and `agents` package conflict
- Re-enabling requires fixing custom node dependencies in the Docker image

## Quick Reconfiguration After WSL Restart

```bash
# 1. Detect new IP
WSL_IP=$(hostname -I | awk '{print $1}')

# 2. Update .env
sed -i "s|http://[0-9.]*:8188|http://$WSL_IP:8188|g" .env

# 3. Recreate backend
docker compose -f compose.base.yml -f compose.home.yml up -d --force-recreate backend

# 4. Verify
docker exec ailinkcinema_backend env | grep COMFYUI_STILL_BASE_URL
