# UI THUMBNAIL OPTIMIZATION — DIRECTIVA

## 1. OBJETIVO

Optimizar la entrega visual de previews para que el Storyboard Builder y el Asset Picker Modal carguen
thumbnails ligeros (w=320) en lugar de binarios completos. Mantener seguridad tenant-safe
y no romper el contrato existente de previews/full assets para export PDF y persistencia.

## 2. ALCANCE

### Backend
- Endpoint: `GET /api/projects/{project_id}/presentation/assets/{asset_id}/thumbnail?w=320`
  - Param: `w` (int, range 80-800, default 320)
  - Usa `Pillow>=10.0.0` para resize LANCZOS con quality=75 (JPEG/WebP) u optimize (PNG)
  - Solo image/* mime types: image/png, image/jpeg, image/webp
  - Para no-image: HTTP 404
  - Tenant-safe: mismo aislamiento que `/preview` (via `get_asset_preview_payload`)
  - Cabeceras: `Cache-Control: public, max-age=86400, stale-while-revalidate=3600`
  - Endpoint `/preview` se mantiene INTACTO para:
    - Filmstrip (PDF render)
    - Persistencia PDF
    - Vistas full/explícitas que necesiten resolución completa
- Archivo: `src/requirements.txt` — Pillow>=10.0.0 agregado

### URLs de thumbnail actualizadas (antes apuntaban a /preview)
| Archivo | Antes | Ahora |
|---------|-------|-------|
| `project_routes.py` (list_project_image_assets) | `.../preview` | `.../thumbnail` |
| `shot_routes.py` (_serialize_shot) | `.../preview` | `.../thumbnail` |
| `presentation_service.py` (_build_asset_shot_item) | `.../preview` | `.../thumbnail` |
| `presentation_service.py` (_build_storyboard_shot_item) | `.../preview` | `.../thumbnail` |

### Frontend
- `AssetPickerModal` — usa `thumbnail_url` (ya lo hacía) + `loading="lazy"`
- `ShotCard` — usa `thumbnail_url` (ya lo hacía) + `loading="lazy"`
- No cambios de código necesarios: el frontend ya consume `thumbnail_url`

## 3. DECISIONES TECNICAS

- Minimo cambio en backend: solo agregar el nuevo endpoint + actualizar 4 URLs
- No se crea tabla de thumbnails cacheadas (no se abre materializacion legacy)
- No se expone ruta física de archivos
- Pillow ya disponible en el entorno (usado por WeasyPrint transitivamente)
- Lazy loading ya presente en frontend via atributo HTML nativo

## 4. VALIDACION

- tenant A: GET thumbnail -> 200 OK, imagen redimensionada (~10-20KB)
- tenant B: GET thumbnail asset de otro tenant -> 403 Access denied
- AssetPickerModal: renderiza grilla con thumbnails ligeros
- StoryboardBuilderPage: ShotCard renderiza thumbnails ligeros
- GET /preview (full asset) sigue funcionando: filmstrip/PDF intacto
- GET /thumbnail para no-image -> 404

## 5. CRITERIOS DE ACEPTACION

- [x] Entrega de thumbnails ligera tenant-safe para image/*
- [x] AssetPickerModal consume thumbnails ligeros
- [x] ShotCard consume thumbnails ligeros
- [x] tenant B sigue bloqueado
- [x] No regresion en preview full, filmstrip, PDF y persistencia
- [x] Carga visual claramente mas ligera

## 6. ESTADO

THUMBNAIL OPTIMIZATION = CLOSED