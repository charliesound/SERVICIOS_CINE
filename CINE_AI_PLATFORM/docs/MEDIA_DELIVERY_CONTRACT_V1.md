# Media Delivery Contract V1

## Overview

The backend premium (CINE_AI_PLATFORM) now normalizes media delivery for render jobs.
When a ComfyUI render succeeds, the output image filenames are extracted from the
ComfyUI history API and exposed as structured `output_images` with full `view_url`s.

## What Changed

### Backend (`CINE_AI_PLATFORM`)

**1. Schema: `RenderJobResult` now includes `output_images`**

File: `apps/api/src/schemas/render_job.py`

New model:
```python
class RenderJobOutputImage(BaseModel):
    filename: str
    subfolder: str = ""
    image_type: str = "output"
    view_url: Optional[str] = None
    node_id: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
```

`RenderJobResult` gains:
```python
output_images: Optional[List[RenderJobOutputImage]] = None
```

**2. Service: `_build_success_result` extracts images from ComfyUI outputs**

File: `apps/api/src/services/render_jobs_service.py`

The `_extract_output_images()` method now iterates the ComfyUI history `outputs` dict,
extracts every image entry, and constructs the full ComfyUI `/view?` URL:

```
http://<comfyui_base_url>/view?filename=<filename>&type=<type>&subfolder=<subfolder>
```

**3. Persistence**

No SQLite schema change needed. The `result TEXT` column stores JSON, so the new
`output_images` field is automatically persisted and retrieved.

### Frontend (Web Ailink_Cinema)

**4. `lib/cinema.ts` updated**

- Added `RenderJobOutputImage` and `RenderJobResult` types matching the backend schema
- Added `getPrimaryImageUrl(job)` — returns the first `view_url` from `output_images`
- Added `getAllImageUrls(job)` — returns all `view_url`s from `output_images`
- Removed the heuristic `extractImageUrlsFromJob()` scraping function

**5. `storyboard-ai` page updated**

- Uses `getPrimaryImageUrl(job)` instead of heuristic scraping
- Image URLs are set on shot cards when jobs succeed

## Endpoints

### `POST /api/sequence/plan-and-render`

Returns `created_jobs[]` with `result.output_images[]` populated for any jobs
that have already completed (initially all "queued", so `output_images` will be null).

### `GET /api/render/jobs/{job_id}`

Returns the full `RenderJobData` including:
- `status`: "queued" | "running" | "succeeded" | "failed" | "timeout"
- `result.output_images[]`: populated when status is "succeeded"
- `result.output_images[].view_url`: the ComfyUI `/view?` URL for the image
- `error`: populated when status is "failed" or "timeout"

## Degradation

| Scenario | `output_images` | `status` | Frontend behavior |
|---|---|---|---|
| Job queued | `null` | "queued" | Shows "En cola" placeholder |
| Job running | `null` | "running" | Shows "Renderizando" placeholder with spinner |
| Job succeeded, images exist | `[{filename, view_url, ...}]` | "succeeded" | Shows image from `view_url` |
| Job succeeded, no images | `[]` or `null` | "succeeded" | Shows "Renderizado" placeholder |
| Job failed | `null` | "failed" | Shows error message |
| Job timeout | `null` | "timeout" | Shows "Timeout" placeholder |

## What's NOT in V1

- No media proxy or CDN — URLs point directly to ComfyUI's `/view?` endpoint
- No thumbnail generation — uses the full output image
- No image download/serve from the backend API
- No media persistence beyond ComfyUI's output directory
- No image validation or quality checks
- No multi-asset management (DAM)

## Testing

Run: `cd apps/api && python -m pytest tests/test_media_delivery_contract.py -v`

14 tests covering:
- Single/multiple output image extraction
- View URL construction
- Empty/malformed output handling
- Backward compatibility with existing result fields
- Schema serialization
