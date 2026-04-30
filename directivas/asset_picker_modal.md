# ASSET PICKER MODAL — DIRECTIVA MVP TENANT-SAFE

## 1. OBJETIVO

Sustituir la edición manual primitiva de `asset_id` por un Asset Picker Modal tenant-safe con feed backend
paginado y galería visual lazy-loaded. Sin autosave. Policy de Save Sync explícito intacto.

## 2. ALCANCE MVP

### Backend
- Endpoint: `GET /api/projects/{project_id}/assets`
  - Filtros obligatorios:
    - project_id exacto (path)
    - organization_id del tenant actual (del context)
    - mime_type IN ('image/png', 'image/jpeg', 'image/webp')
    - solo assets con status='indexed'
  - Orden: created_at DESC
  - Paginación: page + size (default size=20)
  - Respuesta por item:
    - asset_id, file_name, mime_type, created_at
    - preview_url: `/api/projects/{project_id}/presentation/assets/{asset_id}/preview`
    - thumbnail_url: mismo preview_url
  - NO exponer rutas físicas (canonical_path, relative_path)
  - NO incluir JSON/audio/documentos

### Frontend
- Componente: `AssetPickerModal`
  - Props: isOpen, projectId, currentAssetId, onSelect, onClose
  - Estados: isLoading, assetPage, assets[], paginationMeta, error
  - Grid scrollable de thumbnails lazy-loaded
  - Click actualiza dirtyShots localmente (sin PUT inmediato)
  - Cierra al seleccionar

### Integración con Storyboard Builder
- Route: `/projects/:projectId/storyboard-builder`
- ShotCard: botón "Cambiar Asset" abre AssetPickerModal
- On select: dirtyShots[n].asset_id = selected, dirtyShots[n].isDirty = true
- "Guardar Storyboard" hace bulk PUT real
- UI bloqueada durante save

## 3. RESTRICCIONES
- NO autosave
- NO uploads directos
- NO búsqueda semántica
- NO versionado/retención
- Cambios mínimos, demo-friendly, tenant-safe

## 4. CRITERIOS ACEPTACIÓN
- Feed backend paginado de assets image/* tenant-safe
- AssetPickerModal funcional
- Modal actualiza dirtyShots sin guardar automáticamente
- Guardar Storyboard persiste asset_id swap
- PDF exportado refleja el swap
- Tenant B bloqueado contra feed del proyecto A
- No regresión en el Builder ni Presentation