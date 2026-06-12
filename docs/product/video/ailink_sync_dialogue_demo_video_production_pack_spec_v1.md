# AILink Sync Dialogue — Demo Video Production Pack Spec v1

## 1. Objetivo

Este documento define el paquete final esperado para producir y publicar el vídeo demo comercial de AILink Sync Dialogue.

Esta fase no crea vídeo, no crea MP4, no crea audio, no crea miniaturas, no crea capturas, no crea assets binarios nuevos y no toca landing, frontend, backend, CID SaaS, Supabase, CRM, tracking, cookies, Docker, runtime ni configuración.

Resumen explícito de no-creación:

- No crea MP4.
- No crea audio.
- No crea miniaturas.
- No crea assets binarios nuevos.

## 2. Materiales de entrada

- docs/product/video/ailink_sync_dialogue_demo_video_script_v1.md
- docs/product/video/ailink_sync_dialogue_demo_video_subtitles_es_v1.srt
- docs/product/video/ailink_sync_dialogue_demo_video_voiceover_es_v1.txt
- docs/product/video/ailink_sync_dialogue_demo_video_subtitles_readme_v1.md
- docs/product/video/ailink_sync_dialogue_demo_video_assembly_runbook_v1.md
- docs/product/social/ailink_sync_dialogue_social_launch_pack_v1.md
- docs/product/beta/ailink_sync_dialogue_beta_leads_operations_runbook_v1.md
- docs/product/landing/ailink_sync_dialogue_static_landing.html
- docs/product/assets/ailink_sync_dialogue/assets_manifest.json

## 3. Non-goals

Esta fase no debe renderizar vídeo, crear MP4, MOV, WAV, MP3, PNG, JPG, miniaturas, capturas, proyectos de montaje, modificar subtítulos, modificar locución, modificar assets existentes, modificar landing, implementar formulario, implementar CRM, implementar Supabase, implementar automatizaciones, implementar tracking, tocar frontend, tocar backend, tocar CID SaaS, tocar Docker, tocar runtime, añadir dependencias ni publicar nada.

## 4. Paquete de producción futuro

Una fase futura podrá crear un paquete bajo:

docs/product/video/production_pack/ailink_sync_dialogue_demo_v1/

Esa carpeta no se crea en esta fase.

El paquete futuro podrá contener vídeo master horizontal, versión corta horizontal, versión cuadrada, versión vertical, subtítulos, locución final, miniaturas, README de publicación, checklist, metadata y copys finales para LinkedIn/Facebook.

## 5. Nombres de archivo recomendados

- ailink_sync_dialogue_demo_master_1920x1080_es_v1.mp4
- ailink_sync_dialogue_demo_short_1920x1080_es_v1.mp4
- ailink_sync_dialogue_demo_square_1080x1080_es_v1.mp4
- ailink_sync_dialogue_demo_vertical_1080x1920_es_v1.mp4
- ailink_sync_dialogue_demo_subtitles_es_v1.srt
- ailink_sync_dialogue_demo_voiceover_es_v1.wav
- ailink_sync_dialogue_demo_thumbnail_1920x1080_es_v1.png
- ailink_sync_dialogue_demo_thumbnail_1080x1080_es_v1.png
- ailink_sync_dialogue_demo_publication_readme_v1.md
- ailink_sync_dialogue_demo_publication_metadata_v1.json
- ailink_sync_dialogue_demo_publication_checklist_v1.md

Reglas: usar minúsculas, guiones bajos, idioma, versión, sin espacios, sin caracteres especiales, sin nombres de clientes, sin fechas de proyectos reales y sin rutas locales.

## 6. Versiones recomendadas

### 6.1 Master horizontal

Resolución 1920x1080, orientación horizontal, duración 75 a 105 segundos, para landing, YouTube privado/no listado y presentación comercial.

### 6.2 Versión corta horizontal

Resolución 1920x1080, orientación horizontal, duración 30 a 45 segundos, para envío directo a leads.

### 6.3 Versión cuadrada

Resolución 1080x1080, duración 30 a 60 segundos, para LinkedIn y Facebook.

### 6.4 Versión vertical

Resolución 1080x1920, duración 20 a 45 segundos, para reels, stories, shorts y clips de expectativa.

## 7. Subtítulos

Fuente: docs/product/video/ailink_sync_dialogue_demo_video_subtitles_es_v1.srt

Mantener SRT separado, revisar legibilidad, no cambiar significado sin actualizar fuente y evitar subtítulos demasiado bajos en versiones verticales.

## 8. Locución

Fuente: docs/product/video/ailink_sync_dialogue_demo_video_voiceover_es_v1.txt

Salida futura recomendada: ailink_sync_dialogue_demo_voiceover_es_v1.wav

La voz debe ser clara, sin ruido, sin claims improvisados y sin prometer funcionalidades futuras como disponibles.

## 9. Miniaturas

Miniaturas futuras recomendadas:

- ailink_sync_dialogue_demo_thumbnail_1920x1080_es_v1.png
- ailink_sync_dialogue_demo_thumbnail_1080x1080_es_v1.png

Texto recomendado: Prepara vídeo, audio y metadata antes del montaje.

No decir producto final, sincronización automática completa, edición automática ni que sustituye al montador.

## 10. Metadatos de publicación

Archivo futuro recomendado: ailink_sync_dialogue_demo_publication_metadata_v1.json

Campos recomendados: title, short_title, description, language, duration_seconds, version, target_audience, publication_channels, landing_url, beta_status, limitations, cta, source_assets, review_status, approved_by, approved_at.

El archivo no se crea en esta fase.

## 11. Canales previstos

Landing AILinkCinema, LinkedIn, Facebook, enlace directo a leads beta, presentación privada a escuelas de cine, productoras y equipos de postproducción.

No publicar automáticamente. No activar automatizaciones.

## 12. Checklist de revisión editorial

- El vídeo explica el problema en los primeros segundos.
- El vídeo muestra AILink Sync Dialogue como herramienta independiente.
- El vídeo no confunde AILink Sync Dialogue con CID.
- El vídeo menciona beta privada.
- El vídeo no promete acceso inmediato.
- El vídeo no pide subir material audiovisual.
- El vídeo no usa material real de clientes.
- El vídeo no muestra rutas privadas.
- El vídeo no muestra emails reales.
- El vídeo no muestra secretos.
- El vídeo no muestra .env.
- El vídeo no promete waveform sync.
- El vídeo no promete transcripción.
- El vídeo no promete claqueta visual.
- El vídeo no promete integración directa con editores.
- El vídeo no promete producto final.
- El CTA coincide con la landing y el flujo manual de leads.

## 13. Checklist técnico

Resolución correcta. Audio claro. Subtítulos revisados, textos legibles, tablas con zoom suficiente, sin notificaciones del sistema, sin material sensible, sin cortes bruscos, duración dentro del rango, peso razonable, nombre de archivo correcto, versión correcta y backup local controlado.

## 14. Checklist legal/comercial

Aviso de beta privada coherente, landing legal revisada, formulario real no enlazado si no está preparado, sin promesas de cumplimiento legal, sin promesas de resultados perfectos, sin captación de datos fuera del flujo previsto, sin cookies/tracking sin consentimiento cuando aplique, sin uso engañoso de marcas de terceros y sin material audiovisual de terceros sin autorización.

## 15. Relación con leads beta

El vídeo debe servir para explicar el producto antes de una demo, filtrar leads que no encajan, reforzar el mensaje local-first, preparar preguntas de cualificación y aumentar confianza sin prometer producto final.

Debe alinearse con:

- docs/product/beta/ailink_sync_dialogue_beta_leads_operations_runbook_v1.md
- docs/product/legal/ailink_sync_dialogue_landing_legal_integration_spec_v1.md
- docs/product/social/ailink_sync_dialogue_social_launch_pack_v1.md

## 16. Criterios de aceptación del paquete futuro

El paquete futuro será aceptable si existe master horizontal, SRT, locución final o pista de voz integrada, miniatura, README, metadata, checklist, nombres convencionales, versiones claras, sin material sensible, sin secretos, sin contradicción con landing, leads ni beta privada.

## 17. Criterios de aceptación de esta fase

Esta fase se considera válida si define paquete futuro, nombres de archivo, versiones horizontal/corta/cuadrada/vertical, subtítulos, locución, miniaturas, metadatos, canales, checklist editorial, checklist técnico, checklist legal/comercial, separación AILink Sync Dialogue/CID y no crea vídeos, audio, miniaturas, assets, runtime, frontend ni backend.
