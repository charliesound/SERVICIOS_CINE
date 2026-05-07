# Ollama Qwen3 + Gemma4 Storyboard Pipeline

## Overview

Pipeline local usando **Ollama + RTX 5090** para análisis cinematográfico y generación de prompts de storyboard para ComfyUI.

---

## 1. Installation

### Install Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Download Models
```bash
# Analysis model (required)
ollama pull qwen3:30b

# Visual refinement model (preferred)
ollama pull gemma4:26b
# or
ollama pull gemma4:31b

# Fallback if Gemma4 not available
ollama pull qwen3:30b
```

---

## 2. GPU Setup (RTX 5090)

### Verify GPU
```bash
nvidia-smi
ollama ps
```

### Start Ollama with GPU
```bash
# If using CUDA
CUDA_VISIBLE_DEVICES=0 ollama serve

# Or just start normally (Ollama auto-detects GPU)
ollama serve
```

---

## 3. Environment Variables

Update `.env` or `.env.example`:

```bash
# Ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_ANALYSIS_MODEL=qwen3:30b
OLLAMA_VISUAL_MODEL=gemma4:26b
OLLAMA_FALLBACK_MODEL=qwen3:30b
OLLAMA_TIMEOUT_SECONDS=240
OLLAMA_NUM_CTX=32768
OLLAMA_TEMPERATURE_ANALYSIS=0.25
OLLAMA_TEMPERATURE_VISUAL=0.55
OLLAMA_USE_LOCAL_ANALYSIS=true
OLLAMA_USE_DUAL_MODEL_STORYBOARD=true
```

---

## 4. Start Backend

```bash
cd /opt/SERVICIOS_CINE/src
python -m uvicorn app:app --host 127.0.0.1 --port 8010 --reload
```

---

## 5. Verify Status

```bash
# Ollama health
curl http://127.0.0.1:11434/api/tags

# Backend health
curl http://127.0.0.1:8010/health

# Ollama status via backend
curl http://127.0.0.1:8010/api/ops/ollama/status
```

---

## 6. Test Script Analysis

```bash
# Get auth credential
AUTH_BEARER="<AUTH_BEARER_FROM_LOGIN>"

# Analyze script with Qwen3:30b
curl -X POST "http://127.0.0.1:8010/api/projects/$PROJECT_ID/analyze/local-ollama" \
  -H "Authorization: Bearer $AUTH_BEARER"
```

**Expected response:**
```json
{
  "project_id": "44c7366f...",
  "model": "qwen3:30b",
  "analysis_type": "local_ollama_script_analysis",
  "summary": "...",
  "genre": "Drama",
  "scenes": [...],
  "base_storyboard_prompt": "..."
}
```

---

## 7. Test Storyboard Prompts

```bash
# Generate storyboard prompts with visual refinement
curl -X POST "http://127.0.0.1:8010/api/projects/$PROJECT_ID/storyboard/prompts/from-analysis" \
  -H "Authorization: Bearer $AUTH_BEARER" \
  -H "Content-Type: application/json" \
  -d '{
    "generation_mode": "FULL_SCRIPT",
    "refine_with_visual_model": true
  }'
```

**Expected response:**
```json
{
  "project_id": "44c7366f...",
  "analysis_model": "qwen3:30b",
  "visual_model": "gemma4:26b",
  "generation_mode": "FULL_SCRIPT",
  "storyboard_prompts": [
    {
      "scene_number": 1,
      "refined_storyboard_prompt": "...",
      "comfyui_positive_prompt": "...",
      "shot_design": {...}
    }
  ]
}
```

---

## 8. Architecture

```
Script (text)
    ↓
Qwen3:30b Analysis
    ↓ (base_storyboard_prompt per scene)
Gemma4:26b Visual Refinement (preferred)
    ↓ (fallback: Qwen3:30b)
Refined Prompts for ComfyUI
    ↓
Storyboard Generation (ComfyUI)
```

---

## 9. Fallback Strategy

| Scenario | Action |
|-----------|--------|
| Gemma4 not installed | Auto-fallback to Qwen3:30b |
| Qwen3:30b not installed | Error: "Run ollama pull qwen3:30b" |
| Ollama not running | Error: "Ollama not available" |
| Invalid JSON from model | Error: "Model returned invalid JSON" |

---

## 10. Progress Tracking

Frontend shows progress via polling:

```
pending → processing → refining_prompts → completed
```

Endpoints for progress:
- `GET /api/projects/{id}/jobs/{job_id}` (if using ProjectJob)
- Status returned in response with `progress.percent` and `progress.stage`

---

## 11. Validation

```bash
cd /opt/SERVICIOS_CINE

# Compile check
python -m py_compile $(find src -name "*.py" | tr '\n' ' ')

# Run smoke test
.venv/bin/python scripts/smoke_ollama_qwen_storyboard_analysis.py \
  --base-url http://127.0.0.1:8010

# Integration tests
.venv/bin/python -m pytest tests/integration/ -q

# Frontend build
cd src_frontend && npm run build
```

---

## 12. Next Steps

1. Connect prompts directly to ComfyUI workflows
2. Implement actual image generation via ComfyUI
3. Add WebSocket for real-time progress
4. Support multiple visual models (SDXL, Flux, Wan)
5. Add batch storyboard rendering
