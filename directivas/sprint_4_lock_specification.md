# Sprint 4 Locking Specification: Postproduction & Assembly

## 1. Objetivo del Sprint
Establecer la conexión entre el material visual generado (S3) y el flujo editorial técnico, permitiendo la organización de **Clips** y la visualización del primer **Assembly Cut** (montaje inicial) trazable por escena.

## 2. Alcance Exacto
### Entra:
- **Jerarquía Editorial:** Relación funcional `Scene -> Clip -> AssemblyCut`.
- **Media Pool (Clips Overview):** Gestión centralizada de todos los clips (vícteo/audio) del proyecto.
- **Scene Clips View:** Asociación manual o sugerida de clips a escenas específicas.
- **Postproduction Workspace (Assembly Cut):** Vista de previsualización secuencial de los clips asociados a una escena o secuencia.
- **Vínculo Trazable:** El usuario puede navegar desde el guion hasta el clip montado.

### No Entra:
- **Timeline Editing (NLE):** No hay arrastre de clips, transiciones ni edición de audio multipista profesional.
- **Video Generation Multi-Scene:** No se genera el vídeo final del largometraje en este sprint.
- **Color Grading / VFX:** No hay herramientas de postproducción de imagen avanzada.

## 3. Vistas Finales
1.  **Clips Overview:** Repositorio central de archivos de vídeo y audio organizados por metadatos (Duración, Resolución, Escena asociada).
2.  **Scene Clips View:** Dentro del *Scene Workspace*, una pestaña dedicada para ver qué clips han sido asignados a esa escena específica.
3.  **Postproduction Workspace:** Reproductor que concatena automáticamente los clips favoritos de una escena para ver el "Ritmo" de la misma.
4.  **Assembly Cut Detail:** Ficha técnica del ensamblado actual con lista de clips incluidos y su orden de aparición.

## 4. Acciones del Usuario por Vista
- **Clips Overview:** Subir clips manualmente, renombrar, asignar a Escena/Personaje.
- **Scene Clips View:** Seleccionar qué clips de la escena forman parte del "Corte Actual".
- **Postproduction Workspace:** Reproducir la secuencia de clips (Assembly) de la escena.
- **Assembly Cut Card:** Ver qué porcentaje del guion está ya cubierto por metraje real (Placeholder visual).

## 5. Nivel de Control (MVP)
- **Asociación:** El usuario marca clips como "Aptos para Montaje".
- **Ordenación:** El sistema ordena los clips basándose en el orden de los *Shots* definidos en el Sprint 3.
- **Visualización:** Reproducción secuencial (Concat) para validación rápida.

## 6. Datos Demo Obligatorios
- **Clips Demo:** Al menos 4 clips de vídeo cortos (5s) para la escena principal de *The Robot's Journey*.
- **Assembly Demo:** Un montaje funcional de la Escena 02 que demuestre la transición entre clips.

## 7. Estados Vacíos / Placeholders
- **Empty Clips View:** "No clips assigned to this scene. Link your generated assets or upload footage."
- **NLE Timeline Placeholder:** Una franja visual estática que representa el tiempo pero que no es editable (Tooltip: "NLE Editor coming soon").
- **Transcript Placeholder:** Área de texto con "Automatic Transcript" marcado como (Coming Soon).

## 8. Percepción del Producto
- **Continuidad Editorial:** El productor siente que el guion está "cobrando vida" de forma secuencial.
- **Organización:** Se percibe un orden industrial; el material no está perdido en carpetas, está en su "Sitio Editorial".
- **Trazabilidad:** Un error en el montaje se puede rastrear directamente al guion o al shot original.

## 9. Criterios de Terminado (DoD)
- [ ] El modelo de datos soporta la relación `Scene -> Clip -> AssemblyCut`.
- [ ] La vista "Postproduction Workspace" puede reproducir una secuencia de clips en orden.
- [ ] Se puede asociar un activo visual de S3 a un Clip editorial de S4.
- [ ] El `Project Overview` muestra el estado de "Assembly Coverage" (% de escenas con clips).
- [ ] Demo Interna: "Navegar de Guion a Escena, ver sus Clips y reproducir el Assembly de 20 segundos".

## 10. Decisiones Congeladas
1.  **Linear Assembly:** El primer montaje se basa en la ordenación de los Shots. No hay capas de vídeo superpuestas.
2.  **Clip Atomicity:** Un Clip es la unidad mínima editorial. No se permiten "sub-clips" o recortes dentro de la plataforma en este sprint.
3.  **Local Direct Playback:** Los clips se reproducen mediante streaming directo desde el almacenamiento local del orquestador.
