# AILink Sync Dialogue — Static Landing Export Pack

## Objetivo

Este pack contiene una landing estática, exportable y revisable para presentar AILink Sync Dialogue antes de implementar la web pública real.

La fase no toca frontend real, backend, rutas, modelos, servicios, pagos, base de datos de leads, CRM, VPS ni configuración runtime.

## Archivos

- `ailink_sync_dialogue_static_landing.html`: landing HTML autocontenida con CSS embebido.
- `ailink_sync_dialogue_static_landing_README.md`: este documento.
- `tests/unit/test_ailink_sync_dialogue_static_landing.py`: tests de estructura, seguridad y referencias a assets.

## Assets usados

La landing usa rutas relativas hacia el pack ya auditado:

- `../assets/ailink_sync_dialogue/hero-report-mockup.png`
- `../assets/ailink_sync_dialogue/report-summary.png`
- `../assets/ailink_sync_dialogue/match-suggestions-table.png`
- `../assets/ailink_sync_dialogue/media-files-table.png`
- `../assets/ailink_sync_dialogue/privacy-local-first.png`
- `../assets/ailink_sync_dialogue/linkedin-beta-card.png`

## Cómo revisar localmente

Abrir el archivo HTML directamente desde el explorador de archivos o navegador.

Archivo:

`docs/product/landing/ailink_sync_dialogue_static_landing.html`

## Qué incluye

- Hero comercial.
- Problema que resuelve.
- Qué hace ahora.
- Cómo funciona.
- Outputs principales.
- Privacidad local-first.
- Público objetivo.
- Bloque de beta privada.
- FAQ.
- CTA final.
- Uso de assets PNG ya auditados.

## Qué no incluye

- Formulario real.
- Envío de datos.
- Tracking.
- Integración CRM.
- Backend.
- Cloud.
- URLs externas.
- Scripts JavaScript.
- Dependencias externas.
- Política legal final.

## Criterio comercial

Esta landing vende una beta/prototipo útil, no un producto final cerrado.

Mensaje principal:

> Prepara el material de rodaje para montaje en minutos.

Mensaje de privacidad:

> El material permanece en el disco del cliente. Sin cloud en la versión actual.

## Siguiente fase posible

Después de validar visualmente este HTML, se puede avanzar a una de estas opciones:

1. Crear contenido social de lanzamiento para LinkedIn/Facebook.
2. Implementar una landing web real fuera del backend.
3. Preparar formulario beta legalmente revisado.
4. Preparar demo comercial en vídeo.
