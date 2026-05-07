# Landing Semantic ComfyUI V3 SOP

## Objetivo

Definir una linea visual coherente para la landing de AILinkCinema y CID donde cada bloque conecte texto, imagen base y movimiento corto dentro del mismo universo cinematografico premium.

Principio central:

texto de landing -> intencion visual -> imagen base -> movimiento coherente -> video corto

## Reglas operativas

- Primero se generan imagenes ancla.
- Despues se planifican y generan videos a partir de esas imagenes.
- No se crea video sin imagen base aprobada.
- No se mezclan prompts que cambien el universo visual entre bloques.
- No se llama a `/prompt` por defecto.
- No se hace render real salvo con flags explicitos.
- No se commitean outputs pesados, originales ni rutas absolutas.
- No se toca `.env`.
- No se toca ninguna `.db`.

## Identidad visual base

- Direccion artistica: tecnologia cinematografica premium, control operativo, interfaces elegantes, realismo sobrio.
- Paleta: charcoal profundo, negro grafito, amber suave, teal contenido, reflejos metalicos discretos.
- Iluminacion: contraste cinematografico, brillo de pantallas controlado, atmosfera limpia, sin look sci-fi barato.
- Movimiento: bajo, estable, con camara lenta, parallax sutil o empuje cinematografico corto.

## Imágenes y vídeos coherentes

La landing debe tener una identidad visual continua. Cada bloque puede tener imagen estatica y, cuando aporte valor, un video breve de 4 a 6 segundos.

Los videos no sustituyen a las imagenes: las complementan. Cada video debe derivar de la imagen base correspondiente mediante image-to-video.

Regla:
- Imagen base = identidad visual del bloque.
- Video = movimiento sutil que refuerza el significado.
- Movimiento bajo, elegante, cinematografico.
- Evitar camara caotica, zoom exagerado, morphing agresivo o deformacion de interfaces.

Formato recomendado:
- Imagen: WebP
- Video: MP4 H.264 o WebM optimizado
- Duracion: 4-6 segundos
- FPS: 24
- Resolucion de trabajo: 1280x720 o 1536x864
- Resolucion web final: 1280x720
- Peso maximo recomendado por video: 3-6 MB
- Hero puede admitir video mas pesado, maximo 8-10 MB si esta muy justificado.

## Flujo V3 recomendado

1. Redactar o revisar prompts semanticos V3 por bloque.
2. Generar payloads de imagen V3 en dry-run.
3. Aprobar las 10 imagenes base V3.
4. Generar solo planes o payloads image-to-video a partir de cada imagen aprobada.
5. Importar y optimizar imagenes antes de tocar referencias publicas.
6. Importar y optimizar videos solo cuando aporten valor real a la landing.
7. Aplicar referencias en frontend con fallback estatico obligatorio.
8. Ejecutar smoke de contrato antes de cualquier aprobacion final.

## Entregables esperados

- Prompt pack V3 con imagen y video por bloque.
- Payloads dry-run en `.tmp/landing_comfyui_v3/`.
- Imagenes finales V3 en `src_frontend/public/landing-media/`.
- Videos finales V3 optimizados en `src_frontend/public/landing-media/`.
- Manifest de importacion para imagenes y videos.
- Script de aplicacion de referencias y smoke contract dedicado.
