# AILink Sync Dialogue — Landing Visual Assets Pack

Este paquete contiene los assets visuales generados para la landing de AILink Sync Dialogue.

## Origen

Todos los assets se generan a partir de la demo controlada de metadata:

`scripts/demo/create_sync_dialogue_metadata_demo.py`

No se ha utilizado material real de clientes, proyectos ni producciones.
No se han subido archivos a ningún servidor.

## Assets incluidos

- `hero-report-mockup.png`: Imagen principal del hero de landing. Muestra el reporte HTML con resumen de conteos y tabla de match suggestions.
- `report-summary.png`: Tarjeta de resumen con totales de vídeo/audio y formatos de salida.
- `match-suggestions-table.png`: Tabla de sugerencias de sincronía con confianza, score y estrategia.
- `media-files-table.png`: Inventario de archivos detectados con tipo, duración, codec y timecode.
- `privacy-local-first.png`: Pieza visual sobre privacidad local: el material no sale del disco del cliente.
- `linkedin-beta-card.png`: Imagen cuadrada para redes sociales (1080×1080) con CTA de beta privada.

## Cómo regenerar

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
python scripts/demo/generate_sync_dialogue_landing_assets.py \
    --output-dir docs/product/assets/ailink_sync_dialogue \
    --force
```

## Privacidad

Todos los assets usan exclusivamente metadata controlada y nombres de archivo genéricos.
Ningún asset contiene:
- Rutas de sistema personales
- Nombres reales de clientes o producciones
- Material audiovisual sensible
- Emails o datos personales
- Logos de terceros sin autorización

## Uso previsto

- Landing pública de AILink Sync Dialogue
- Publicaciones en LinkedIn y Facebook
- Presentaciones comerciales
- Mockups básicos de producto
