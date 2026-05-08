# Landing V4 — Auditoría de razonamiento visual

> FASE 1 — Diagnóstico semántico de los 10 bloques visuales de la landing CID.
> Cada bloque se audita contra el texto real de la landing, la imagen V3 actual y la intención visual que debería transmitir CID.

---

## 1. Hero principal

| Campo | Valor |
|---|---|
| **Texto landing** | "AILinkCinema combina creatividad visual, lienzo colaborativo e inteligencia artificial con un sistema real de producción audiovisual. CID conecta guion, storyboard, planificación, doblaje, sonido, VFX, montaje y distribución en un mismo flujo de trabajo." |
| **Imagen V3** | `landing-hero-main-v3.webp` |
| **Problema semántico** | La imagen V3 muestra un centro operativo genérico con pantallas. No representa el pipeline completo ni la conexión guion→entrega. |
| **Intención visual correcta** | Un centro de control operativo que muestre explícitamente: texto de guion entrando → análisis → storyboard → generación → delivery. Debe leerse como un sistema real, no como decoración. |
| **Propuesta V4** | Dashboard panorámico 1536×864 con el flujo guion→storyboard→generación→entrega visible en paneles interconectados. Colores: carbón, ámber, teal controlado. |

---

## 2. Problema / producción fragmentada

| Campo | Valor |
|---|---|
| **Texto landing** | "Guion, storyboard, producción y post suelen operar en entornos separados. Cada fase pierde contexto de la anterior. Las herramientas de IA aparecen cada semana, pero ninguna está diseñada para integrarse en un flujo de producción real." |
| **Imagen V3** | `landing-problem-fragmented-v3.webp` |
| **Problema semántico** | La imagen es aceptable pero genérica: muestra escritorios separados sin conexión evidente con producción audiovisual real. |
| **Intención visual correcta** | Materiales de producción real (guion impreso, paneles de storyboard, monitor con línea de tiempo) claramente separados, sin conexión entre sí, pero con calidad premium. |
| **Propuesta V4** | Mesa de producción con guion, storyboard impreso, monitor de edición y panel de IA desconectados. Fragmentación organizada, no caos. |

---

## 3. Análisis de guion / IA razona

| Campo | Valor |
|---|---|
| **Texto landing** | "Analiza el guion, identifica personajes, localizaciones y desglose técnico. Recomienda planos y encuadres. La IA estructura, razona y recomienda." |
| **Imagen V3** | `landing-ai-reasoning-v3.webp` |
| **Problema semántico** | Abstracta. Muestra un panel de análisis sin guion real visible. No se ve el texto del guion siendo procesado. |
| **Intención visual correcta** | Interfaz que muestre UN GUIÓN REAL con escenas, personajes y localizaciones extraídas. Debe verse el texto de un guion con overlays de análisis. |
| **Propuesta V4** | Pantalla dividida: izquierda = guion real con líneas resaltadas; derecha = fichas de personajes, localizaciones, planos. Conexiones semánticas visibles. |

---

## 4. Moodboard / biblia visual

| Campo | Valor |
|---|---|
| **Texto landing** | "Construye referencias visuales por escena, personaje y atmósfera. Consolida la dirección artística antes del rodaje." |
| **Imagen V3** | `landing-concept-keyvisual-v3.webp` |
| **Problema semántico** | Muestra un moodboard abstracto sin relación con escenas concretas. No hay conexión con el guion. |
| **Intención visual correcta** | Panel con referencias visuales ORGANIZADAS POR ESCENA: paletas de color, referencias de vestuario, localización, atmósfera. Cada grupo etiquetado con su escena. |
| **Propuesta V4** | Tablero dividido en zonas: cada escena tiene su paleta, referencia de localización, vestuario y luz. Continuidad cromática entre zonas. |

---

## 5. Storyboard / previsualización

| Campo | Valor |
|---|---|
| **Texto landing** | "Construye tu storyboard escena por escena. Cada plano mantiene coherencia narrativa, dirección de arte y continuidad visual. Genera storyboards por plano con encuadre, ángulo e iluminación." |
| **Imagen V3** | `landing-storyboard-preview-v3.webp` |
| **Problema semántico** | Paneles aislados sin secuencia narrativa clara. No se ve progresión de planos ni continuidad. |
| **Intención visual correcta** | Secuencia horizontal REAL de viñetas del mismo personaje/escena: plano general → medio → over shoulder → contraplano → primer plano. Misma luz, mismo vestuario. |
| **Propuesta V4** | Tira de storyboard con 5-6 viñetas consecutivas del mismo personaje en la misma localización. Etiquetas de plano. Raccord visual evidente. |

---

## 6. Generación visual controlada (ComfyUI)

| Campo | Valor |
|---|---|
| **Texto landing** | "Workflows de Flux/SDXL para storyboard, concept art y previz. Control de estilo, iluminación y atmósfera. El sistema valida antes de regenerar." |
| **Imagen V3** | `landing-comfyui-generation-v3.webp` |
| **Problema semántico** | Interfaz de nodos genérica. No muestra el resultado visual concreto ni la validación. |
| **Intención visual correcta** | Nodos (prompt → modelo → imagen) conectados a un panel de resultado donde se ve el frame generado + check de validación. |
| **Propuesta V4** | Workflow node-based visible: caja de prompt → nodo Flux → imagen generada → badge "VALIDADO" o "REVISAR". Panel de resultado cinematográfico. |

---

## 7. Orquestación CID / Pipeline Builder

| Campo | Valor |
|---|---|
| **Texto landing** | "Orquesta el flujo completo: guion → análisis → prompt visual → ComfyUI → storyboard → revisión → entrega. Trazabilidad total." |
| **Imagen V3** | `landing-cid-orchestration-v3.webp` |
| **Problema semántico** | Diagrama abstracto sin peso visual. No comunica que es un producto real funcionando. |
| **Intención visual correcta** | Diagrama de flujo PREMIUM con módulos reales conectados. Cada módulo debe tener una miniatura o icono representativo. |
| **Propuesta V4** | Pipeline horizontal con 7 módulos: Guion 📄 → Análisis 🔍 → Prompt ✏️ → ComfyUI 🎨 → Storyboard 🎞️ → Revisión ✅ → Entrega 📦. Flechas de conexión con trazabilidad. |

---

## 8. Productoras y estudios / Colaboración

| Campo | Valor |
|---|---|
| **Texto landing** | "Comparte storyboards, moodboards y versiones con tu equipo. Director, productor y equipo pueden revisar, comentar y aprobar versiones." |
| **Imagen V3** | `landing-producers-studios-v3.webp` |
| **Problema semántico** | Personas genéricas frente a pantallas. No se distingue el contexto de revisión de producción. |
| **Intención visual correcta** | Director + productor revisando storyboard en monitor grande. Anotaciones visibles. Ambiente de sala de proyección/post. |
| **Propuesta V4** | Sala oscura premium, dos profesionales señalando un storyboard en pantalla grande. Notas adhesivas virtuales. Ambiente de decisión creativa. |

---

## 9. Diferencial profesional / Trazabilidad

| Campo | Valor |
|---|---|
| **Texto landing** | "Cada decisión creativa, cada versión y cada aprobación quedan registradas. La IA acelera, pero las decisiones de calidad y entrega permanecen controladas por el director, el productor y el equipo técnico." |
| **Imagen V3** | `landing-professional-differential-v3.webp` |
| **Problema semántico** | Abstracta: capas tecnológicas sin conexión con flujo de producción real. |
| **Intención visual correcta** | Panel de trazabilidad: versiones, aprobaciones, estados, línea de tiempo de decisiones. Debe sentirse como un sistema de control de producción. |
| **Propuesta V4** | Timeline de producción con versiones (V1, V2, V3...), checkpoints de aprobación (✅ director, ✅ productor), y trazabilidad de cambios. |

---

## 10. Delivery / QC final

| Campo | Valor |
|---|---|
| **Texto landing** | "Entrar en fases avanzadas con más control sobre voz, QC, stems, trazabilidad y compliance. Validamos, revisamos y entregamos. Handoff limpio para cada siguiente fase." |
| **Imagen V3** | `landing-delivery-final-v3.webp` |
| **Problema semántico** | Sala de finishing genérica. No se ve el paquete de entrega ni los checkpoints de QC. |
| **Intención visual correcta** | Panel de QC con métricas, estado de validación, lista de entregables y botón de "Aprobar entrega". |
| **Propuesta V4** | Dashboard de delivery: lista de entregables (master video, stems, subtítulos, metadata), checkmarks de QC, estado "LISTO PARA ENTREGA". Ambiente de sala de postproducción. |

---

## Resumen de hallazgos

| Bloque | Problema principal | Severidad |
|---|---|---|
| Hero | Genérico, no muestra pipeline completo | ALTA |
| Problema | Aceptable pero genérico | MEDIA |
| Análisis guion | Sin guion real visible | ALTA |
| Moodboard | Abstracto, sin organización por escena | ALTA |
| Storyboard | Sin secuencia narrativa real | ALTA |
| ComfyUI | Genérico, sin resultado visual concreto | ALTA |
| Orquestación | Diagrama abstracto sin peso | MEDIA |
| Colaboración | Stock photo genérico | ALTA |
| Trazabilidad | Abstracto sin datos reales | ALTA |
| Delivery | Sin entregables ni QC visibles | ALTA |

> Conclusión: 8 de 10 bloques necesitan regeneración semántica profunda.
> Ninguno de los 10 bloques usa "persona de espaldas mirando pantalla" como solución.
