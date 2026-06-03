# CID — Modelo de negocio de créditos IA

**Documento:** `docs/business/cid_credits_business_model_v1.md`
**Versión:** 1.0
**Fecha:** 2026-06-02
**Tags:** `CID`, `business-model`, `credits`, `ai`, `monetization`, `gpu`
**Basado en:** `cid_project_command_center_branches_v1.md`, `cid_project_access_model_v1.md`

---

## Índice

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Principios del sistema de créditos](#2-principios-del-sistema-de-créditos)
3. [Qué consume créditos](#3-qué-consume-créditos)
4. [Qué NO consume créditos](#4-qué-no-consume-créditos)
5. [Storyboard IA](#5-storyboard-ia)
6. [Concept Art](#6-concept-art)
7. [Character Bible IA](#7-character-bible-ia)
8. [Visual Bible IA](#8-visual-bible-ia)
9. [Image Generation](#9-image-generation)
10. [Video Generation](#10-video-generation)
11. [Dubbing](#11-dubbing)
12. [Voice Cloning](#12-voice-cloning)
13. [Transcripción](#13-transcripción)
14. [Restauración](#14-restauración)
15. [Análisis IA](#15-análisis-ia)
16. [OCR documental](#16-ocr-documental)
17. [Agentes IA](#17-agentes-ia)
18. [Entrenamiento personalizado](#18-entrenamiento-personalizado)
19. [Créditos por operación (conceptual)](#19-créditos-por-operación-conceptual)
20. [Créditos incluidos por plan](#20-créditos-incluidos-por-plan)
21. [Compra de créditos extra](#21-compra-de-créditos-extra)
22. [Alertas de consumo](#22-alertas-de-consumo)
23. [Dashboard de consumo](#23-dashboard-de-consumo)
24. [Riesgos de abuso](#24-riesgos-de-abuso)
25. [Protección de rentabilidad RTX 5090](#25-protección-de-rentabilidad-rtx-5090)
26. [Casos de uso productor](#26-casos-de-uso-productor)
27. [Casos de uso estudio](#27-casos-de-uso-estudio)
28. [Qué NO definir todavía](#28-qué-no-definir-todavía)
29. [Próxima fase](#29-próxima-fase)

---

## 1. Resumen ejecutivo

Este documento define el **sistema de créditos IA** de CID como un componente independiente de:
- **Licencias** (plan de suscripción: Starter / Pro / Studio / Enterprise) — determina capacidad de usuarios y funciones disponibles.
- **Usuarios** (personas con acceso a CID) — determinado por el plan y la invitación del Productor Propietario.
- **Permisos** (qué puede ver/hacer cada usuario en cada rama) — gobernado por el modelo de acceso piramidal.

Los **créditos IA** son la unidad de consumo para operaciones de inteligencia artificial. No sustituyen ni dependen de licencias, usuarios o permisos: son un plano ortogonal. Un usuario puede tener acceso completo a CID pero no tener créditos suficientes para ejecutar una generación de video. Inversamente, un usuario puede tener créditos pero no tener permiso para acceder al módulo de storyboard.

### Modelo conceptual

```
LICENCIA (plan)   ───→  Acceso a la plataforma (usuarios, módulos)
PERMISOS (rol)    ───→  Qué puede ver/hacer cada usuario en cada rama
CRÉDITOS IA       ───→  Combustible para operaciones de IA (no afecta a lo anterior)
```

Cada plan incluye un lote mensual de créditos. Al agotarlos, el usuario puede comprar créditos extra o esperar al siguiente ciclo. Los créditos no utilizados no se acumulan entre meses (modelo "use or lose") salvo en planes Enterprise.

---

## 2. Principios del sistema de créditos

### P1 — Separación de licencia y consumo
El plan de licencia determina el acceso a la plataforma. Los créditos determinan el uso de IA. No se puede convertir créditos en acceso ni viceversa.

### P2 — Consumo por uso real
Cada operación de IA consume créditos en el momento de ejecución. No hay suscripción a funciones IA individuales. Se paga por lo que se usa, dentro del límite del plan.

### P3 — Transparencia de coste por operación
Cada operación muestra su coste en créditos antes de ejecutarse. El usuario sabe cuánto va a consumir antes de confirmar.

### P4 — Sin bloqueo sorpresa
Cuando los créditos se agotan, el sistema no bloquea al usuario de forma abrupta. Ofrece la opción de comprar créditos extra o reducir la calidad de la operación para consumir menos.

### P5 — Los créditos son del proyecto, no del usuario
Los créditos incluidos en el plan pertenecen al proyecto. Cualquier miembro con permisos para usar una función IA consume del mismo pool. El Productor Propietario puede establecer topes por usuario.

### P6 — Protección de rentabilidad
El sistema de créditos debe garantizar que el coste de computación (GPU/hardware) está cubierto por el precio de los créditos, incluyendo un margen que sostenga el negocio. Esto es especialmente crítico para operaciones pesadas como video generation o entrenamiento personalizado.

### P7 — Incentivo a la eficiencia
Las operaciones que consumen más recursos deben costar más créditos. El usuario tiene incentivo a optimizar: reducir resolución, usar modelos ligeros, programar en horas valle.

### P8 — Sin acumulación sin límite
Los créditos mensuales no acumulan entre meses para evitar que un proyecto acumule una reserva que disocie el ingreso del coste real. Los créditos comprados extra pueden tener una ventana de caducidad (ej. 12 meses).

---

## 3. Qué consume créditos

Toda operación que requiera inferencia de modelos de IA generativa, análisis con LLM, generación de assets o procesamiento computacional intensivo:

- Generación de storyboard (imágenes por plano)
- Generación de concept art
- Character Bible (generación de personajes)
- Visual Bible (estilización coherente)
- Image generation (cualquier generación de imagen fuera de los módulos anteriores)
- Video generation (cortos, secuencias, previews)
- Dubbing (síntesis de voz + sincronía labial)
- Voice Cloning (creación y uso de modelos de voz personalizados)
- Transcripción (audio a texto con diarización)
- Restauración (eliminación de ruido, mejora de calidad, colorización)
- Análisis IA (análisis de guion, detección de estructura narrativa, análisis de personajes)
- OCR documental (reconocimiento de texto en documentos escaneados)
- Agentes IA (ejecución de tareas autónomas con contexto)
- Entrenamiento personalizado (fine-tuning de modelos con datos del proyecto)

---

## 4. Qué NO consume créditos

- Inicio de sesión y navegación por la plataforma
- Lectura de datos existentes (presupuestos, calendarios, miembros)
- Visualización de storyboard ya generado
- Descarga de assets ya generados
- Operaciones CRUD estándar (crear/editar/eliminar tareas, notas, etc.)
- Búsqueda y filtrado de datos
- Exportación de informes sin generación IA
- Notificaciones y alertas
- Acceso al dashboard de consumo de créditos
- Visualización del historial de consumo

---

## 5. Storyboard IA

**Módulo:** Rama 2 — Creativo y Rodaje.
**Descripción:** Generación de storyboard visual a partir del guion. El sistema analiza el script, detecta planos y genera imágenes secuenciales.

### Consumo de créditos

| Operación | Créditos | Notas |
|---|---|---|
| Generar storyboard completo (guion < 30 págs) | 1 crédito por 5 planos estimados | El sistema analiza el guion, divide en planos y genera imágenes secuenciales |
| Regenerar un plano específico | 1 crédito por 3 variantes | El usuario puede pedir variaciones de un plano con nuevo prompt |
| Añadir plano manualmente con prompt | 1 crédito por imagen | Inserción de un plano nuevo entre secuencia existente |
| Storyboard en lote (> 30 págs) | 1 crédito por 3 planos estimados | El coste por plano se reduce en lotes grandes |

### Reglas
- El storyboard generado se almacena como asset del proyecto y no consume créditos al visualizarlo.
- Si el usuario rechaza el storyboard completo y solicita regeneración, consume créditos de nuevo (solo la regeneración final aceptada se conserva sin coste adicional de visualización).
- El Productor Propietario puede establecer un límite de créditos por usuario en storyboard para evitar que un director consuma todo el pool.

---

## 6. Concept Art

**Módulo:** Rama 2 — Creativo y Rodaje.
**Descripción:** Generación de arte conceptual y key visual para el proyecto. Imágenes de alta calidad para presentación a inversores, festivales o plataformas.

### Consumo de créditos

| Operación | Créditos | Notas |
|---|---|---|
| Generar concept art (una imagen) | 2 créditos | Resolución alta, calidad de presentación |
| Batch de concept art (5 imágenes simultáneas) | 8 créditos | Las imágenes del mismo batch comparten contexto, reduciendo coste unitario |
| Refinamiento de concept art (inpainting/outpainting) | 1 crédito por modificación | Ajustes localizados sobre una imagen existente |
| Key visual para póster | 3 créditos | Resolución máxima, orientación vertical, lista para presentación |

### Reglas
- El concept art generado se etiqueta con el proyecto y el usuario generador.
- Las imágenes aceptadas pueden promoverse a "activo oficial del proyecto" (no consume créditos).
- El refinamiento solo consume créditos si implica nueva inferencia (no si es solo edición no-IA como recorte o ajuste de brillo).

---

## 7. Character Bible IA

**Módulo:** Rama 2 — Creativo y Rodaje.
**Descripción:** Creación de fichas de personaje con imagen generada por IA + descripción extraída del guion. Consistencia visual entre generaciones del mismo personaje.

### Consumo de créditos

| Operación | Créditos | Notas |
|---|---|---|
| Crear personaje (descripción + imagen inicial) | 2 créditos | Extrae datos del guion y genera imagen base |
| Generar variante del personaje (expresión, ángulo, vestuario) | 1 crédito por imagen | Mantiene consistencia facial |
| Sincronizar personaje entre storyboard y concept art | 1 crédito | Asegura que el personaje generado en storyboard coincide con la Character Bible |
| Agregar personaje manualmente (sin guion) | 1 crédito | Input manual del usuario con descripción + opciones de estilo |

### Reglas
- La Character Bible mantiene un "modelo ligero" del personaje para asegurar consistencia. Crear este modelo ligero consume créditos en la primera generación pero no en generaciones posteriores del mismo personaje.
- Si el usuario modifica sustancialmente la descripción del personaje, regenerar el modelo ligero consume créditos de nuevo.
- La Character Bible puede contener hasta 20 personajes por proyecto sin coste adicional de almacenamiento. Personajes adicionales pueden requerir plan Studio+.

---

## 8. Visual Bible IA

**Módulo:** Rama 2 — Creativo y Rodaje.
**Descripción:** Definición del estilo visual coherente del proyecto: paleta de color, iluminación, textura, atmósfera. Aplica como referencia a storyboard y concept art.

### Consumo de créditos

| Operación | Créditos | Notas |
|---|---|---|
| Definir estilo visual desde referencias | 2 créditos | El sistema analiza 3-5 imágenes de referencia y extrae paleta, iluminación, textura |
| Aplicar Visual Bible a storyboard existente | 1 crédito por cada 10 planos | Reestiliza el storyboard según la guía visual definida |
| Generar preview de estilo | 1 crédito | Aplica el estilo a una escena de prueba antes de aplicarlo a todo el proyecto |
| Actualizar Visual Bible con nuevas referencias | 1 crédito | El usuario añade referencias y el sistema refina el estilo |

### Reglas
- Solo puede haber una Visual Bible activa por proyecto.
- Cambiar la Visual Bible después de haber generado storyboard requiere regenerar los planos afectados (consume créditos de storyboard, no de Visual Bible).
- La Visual Bible no consume créditos al consultarla ni al compartirla con el equipo.

---

## 9. Image Generation

**Módulo:** Disponible en Rama 2 y Rama 3.
**Descripción:** Generación de imágenes independiente de los módulos anteriores. Útil para referencias, mood boards, material de marketing, pósters, thumbnails.

### Consumo de créditos

| Operación | Créditos | Notas |
|---|---|---|
| Generar imagen (resolución estándar, 1024x1024) | 1 crédito | Una imagen, calidad estándar |
| Generar imagen (alta resolución, 2048x2048+) | 3 créditos | Cuádruple de resolución, indicado para impresión o presentación |
| Imagen con controlnet (pose, depth, edge) | 2 créditos | La imagen se genera con guía estructural a partir de una referencia |
| Batch (4 imágenes) | 3 créditos | Coste reducido por imagen en generación simultánea |
| Variaciones de una imagen existente | 1 crédito por 4 variaciones | El usuario sube una imagen y pide variaciones de estilo o composición |

### Reglas
- Las imágenes generadas se almacenan en el módulo de assets del proyecto.
- El usuario puede marcar imágenes como "favoritas" que no cuentan para el límite de almacenamiento del plan.
- La generación con modelos de pago (Midjourney, DALL·E si se integran) puede tener un coste adicional en créditos respecto a modelos open-source locales.

---

## 10. Video Generation

**Módulo:** Rama 2 — Creativo y Rodaje / Rama 3 — Postproducción.
**Descripción:** Generación de secuencias de video cortas a partir de prompt o storyboard. Útil para previzualización, animatics, teasers.

### Consumo de créditos

| Operación | Créditos | Notas |
|---|---|---|
| Video corto (< 5 segundos, 720p) | 5 créditos | Previz rápida, ideal para animatics |
| Video medio (5-15 segundos, 1080p) | 15 créditos | Calidad de presentación intermedia |
| Video largo (15-30 segundos, 1080p) | 30 créditos | Secuencias completas para teasers o muestras |
| Video con storyboard como input | 10 créditos base + 1 crédito por segundo | El sistema usa el storyboard como guía estructural para la generación |
| Video en lote (misma escena, múltiples tomas) | 20% descuento sobre coste unitario | Variantes de una misma escena comparten latente inicial |

### Reglas
- La generación de video es la operación más intensiva en cómputo. Los créditos reflejan el coste real de GPU.
- El usuario puede seleccionar calidad (borrador, estándar, alta) que afecta al coste en créditos directamente.
- Los videos generados se etiquetan con resolución, duración, modelo usado y fecha para trazabilidad.
- El Productor Propietario puede deshabilitar la generación de video a nivel de proyecto si el consumo no está justificado.

---

## 11. Dubbing

**Módulo:** Rama 3 — Postproducción, Entrega y Comercialización.
**Descripción:** Doblaje de diálogos con síntesis de voz + sincronía labial. Soporta múltiples idiomas.

### Consumo de créditos

| Operación | Créditos | Notas |
|---|---|---|
| Doblaje de un minuto de diálogo (1 idioma) | 3 créditos | Síntesis de voz + ajuste de sincronía |
| Doblaje de un minuto (cada idioma adicional) | 2 créditos | El coste por idioma extra es menor porque el análisis de sincronía se reutiliza |
| Doblaje con clonación de voz del actor original | 5 créditos + el coste de voz clonada | Requiere Voice Cloning previo |
| Ajuste manual de sincronía (corrección de palabra) | 0.5 créditos | El usuario corrige una palabra o frase y el sistema reajusta |
| Preview de doblaje (solo 10 segundos) | 1 crédito | Prueba rápida antes de confirmar el doblaje completo |

### Reglas
- El doblaje requiere que exista un audio original o un guion con diálogos marcados.
- Los audios generados se almacenan en el proyecto y se asocian a la escena correspondiente.
- Si el usuario modifica el guion después de generar el doblaje, el doblaje queda marcado como "desactualizado" y debe regenerarse (consume créditos de nuevo).

---

## 12. Voice Cloning

**Módulo:** Rama 3 — Postproducción, Entrega y Comercialización.
**Descripción:** Creación de un modelo de voz personalizado a partir de muestras de audio. Uso posterior en dubbing o narración.

### Consumo de créditos

| Operación | Créditos | Notas |
|---|---|---|
| Clonar voz (5-15 minutos de muestra) | 25 créditos | Entrenamiento del modelo de voz. Coste único por voz. |
| Clonar voz rápida (1-3 minutos de muestra) | 15 créditos | Calidad inferior, útil para pruebas o voces secundarias |
| Actualizar modelo de voz (nuevas muestras) | 5 créditos | Refinamiento del modelo existente con muestras adicionales. |
| Almacenar modelo de voz (por mes) | Sin coste en créditos | El almacenamiento del modelo no consume créditos. Está incluido en el plan hasta el límite de 3 voces (Starter/Pro) o ilimitado (Studio+). |
| Uso de voz clonada en dubbing | Coste del doblaje + 1 crédito extra | Cada uso de una voz clonada tiene un pequeño coste adicional sobre el doblaje base. |

### Reglas
- La voz clonada solo puede usarse en proyectos del mismo usuario/organización que la creó.
- No se permite la descarga del modelo de voz. Solo puede usarse dentro de CID.
- El Productor Propietario debe autorizar explícitamente la clonación de voz en el proyecto (protección legal).
- Las muestras de audio se eliminan tras el entrenamiento. No se conservan en servidores.
- Planes Starter: hasta 3 voces clonadas. Pro: hasta 5. Studio+: ilimitado.

---

## 13. Transcripción

**Módulo:** Disponible en Rama 2 y Rama 3.
**Descripción:** Transcripción de audio a texto con detección de hablante (diarización). Útil para entrevistas, reuniones, notas de voz, material de archivo.

### Consumo de créditos

| Operación | Créditos | Notas |
|---|---|---|
| Transcripción de 1 minuto de audio | 0.2 créditos | Coste muy bajo. Una hora de audio = 12 créditos |
| Transcripción con diarización (detección de hablantes) | 0.3 créditos por minuto | Identifica quién habla en cada segmento |
| Transcripción + traducción a otro idioma | 0.5 créditos por minuto | Transcribe y traduce simultáneamente |
| Transcripción de video (extraer pista de audio + transcribir) | 0.4 créditos por minuto | Incluye extracción de audio + transcripción |

### Reglas
- La transcripción no tiene límite de duración por operación (sí límite práctico de 2 horas por archivo).
- Los textos transcritos se almacenan como documentos en el proyecto y se indexan para búsqueda.
- La diarización requiere al menos 30 segundos de audio por hablante para ser fiable.
- Si el usuario corrige la transcripción manualmente, la corrección no consume créditos.

---

## 14. Restauración

**Módulo:** Rama 3 — Postproducción, Entrega y Comercialización.
**Descripción:** Mejora de calidad de material de archivo: eliminación de ruido, reducción de grano, aumento de resolución, colorización, estabilización.

### Consumo de créditos

| Operación | Créditos | Notas |
|---|---|---|
| Eliminación de ruido de audio (por minuto) | 0.5 créditos | Limpieza de audio ambiental, zumbidos, clics |
| Mejora de video (reducción de grano, por minuto) | 2 créditos | Restauración ligera, mejora de calidad visual |
| Aumento de resolución (de SD a HD, por minuto) | 5 créditos | Escalado con IA |
| Aumento de resolución (de HD a 4K, por minuto) | 10 créditos | Escalado pesado, consume mucha GPU |
| Colorización de video B/N (por minuto) | 8 créditos | Colorización con IA + referencias históricas |
| Restauración completa (audio + video + resolución, por minuto) | 15 créditos | Paquete completo de restauración. Descuento sobre operaciones individuales |
| Preview de restauración (solo 10 segundos) | 1 crédito | Preview rápida antes de aplicar a todo el metraje |

### Reglas
- La restauración preview permite al usuario ver el resultado antes de consumir créditos completos.
- La restauración se aplica sobre el asset original sin modificarlo; se crea un nuevo asset restaurado.
- Si el usuario no está satisfecho con la preview, puede ajustar parámetros sin coste adicional de preview (máximo 3 previews por operación).

---

## 15. Análisis IA

**Módulo:** Ramas 1, 2 y 3 (transversal).
**Descripción:** Análisis inteligente de guion, presupuesto, plan de rodaje, métricas de producción. Incluye detección de estructura narrativa, arcos de personaje, análisis de riesgos, cobertura de localizaciones.

### Consumo de créditos

| Operación | Créditos | Notas |
|---|---|---|
| Análisis completo de guion (detección de estructura, personajes, localizaciones) | 3 créditos | Análisis narrativo completo. Hasta 120 páginas de guion |
| Análisis de riesgos de producción (guion + presupuesto) | 3 créditos | Cruza datos de guion con presupuesto y plan de rodaje |
| Detección de incoherencias narrativas | 2 créditos | Compara eventos entre versiones de guion y señala contradicciones |
| Comparación entre dos versiones de guion | 2 créditos | Diff semántico entre versiones de guion |
| Análisis de personajes (extracción de perfiles, arcos, relaciones) | 2 créditos | Genera o actualiza la ficha de personajes del proyecto |
| Análisis de cobertura de localizaciones | 2 créditos | Detecta localizaciones mencionadas y su estado de gestión |
| Análisis de métricas de producción (dashboard inteligente) | 1 crédito por análisis | Resumen ejecutivo generado por IA del estado del proyecto |

### Reglas
- El análisis IA consume créditos solo en el momento de la petición. Los resultados se almacenan y no consumen créditos al consultarlos.
- Cada análisis genera un informe que queda disponible en el proyecto sin coste recurrente.
- Si el proyecto tiene datos insuficientes para un análisis fiable, el sistema notifica al usuario y no consume créditos (o consume la mitad si el análisis es parcial).

---

## 16. OCR documental

**Módulo:** Rama 1 — Producción y Financiación.
**Descripción:** Reconocimiento de texto en documentos escaneados: contratos, facturas, informes de producción, documentación legal.

### Consumo de créditos

| Operación | Créditos | Notas |
|---|---|---|
| OCR de una página (documento estándar) | 0.1 créditos | Texto limpio, documento mecanografiado |
| OCR de una página (documento manuscrito) | 0.3 créditos | Escritura manual, puede requerir post-corrección |
| OCR de documento completo (lote, hasta 100 páginas) | 5 créditos | Coste reducido por página en lotes grandes |
| OCR con extracción de campos (factura: fecha, importe, proveedor) | 1 crédito por documento | OCR + NLP para extraer datos estructurados |
| OCR multilingüe (documento mezcla idiomas) | 0.2 créditos por página | Detección y transcripción multilingüe |

### Reglas
- Los textos extraídos por OCR se almacenan como metadatos del documento.
- Si el OCR tiene baja confianza (< 80%), se marca para revisión manual pero no se devuelve el crédito (el procesamiento se ejecutó igualmente).
- El usuario puede solicitar re-OCR de una página con diferentes parámetros (idioma, modo manuscrito) que consume créditos de nuevo.

---

## 17. Agentes IA

**Módulo:** Transversal (Ramas 1, 2 y 3).
**Descripción:** Agentes autónomos que ejecutan tareas con contexto del proyecto. Ejemplos: agente de producción que genera órdenes de compra, agente de post que supervisa entregas, agente de financiación que busca subvenciones.

### Consumo de créditos

| Operación | Créditos | Notas |
|---|---|---|
| Crear y configurar un agente | 2 créditos | Definición del propósito, contexto y herramientas del agente |
| Ejecución de una tarea simple por el agente | 0.5 créditos | Tarea acotada: generar un documento, actualizar un campo, enviar una notificación |
| Ejecución de una tarea compleja (multi-paso) | 2 créditos | Tarea que requiere razonamiento secuencial: analizar, decidir, ejecutar, verificar |
| Agente en modo supervisado (requiere aprobación humana en cada paso) | 0.3 créditos por paso | El agente propone acciones que el usuario debe aprobar antes de ejecutar |
| Sesión de agente continuo (30 minutos de ejecución autónoma) | 5 créditos | El agente trabaja de forma continuada en una tarea de larga duración con contexto persistente |

### Reglas
- Los agentes IA solo operan dentro del proyecto y con los datos a los que el usuario que los creó tiene acceso.
- El Productor Propietario puede listar, deshabilitar o eliminar agentes en su proyecto.
- Cada agente tiene un log de acciones visible para el Productor Propietario.
- Si un agente consume más de 20 créditos en un día, se pausa automáticamente y notifica al Productor.
- Los agentes no pueden ejecutar acciones destructivas (eliminar proyectos, revocar usuarios) sin aprobación explícita.

---

## 18. Entrenamiento personalizado

**Módulo:** Enterprise (bajo petición).
**Descripción:** Fine-tuning de modelos con datos del proyecto para generar resultados especializados: estilo visual propio, voces personalizadas, modelos de personaje, modelos de documento.

### Consumo de créditos

| Operación | Créditos | Notas |
|---|---|---|
| Entrenamiento LoRA (dataset < 50 imágenes) | 50 créditos | Entrenamiento ligero para estilo o personaje |
| Entrenamiento LoRA (dataset 50-200 imágenes) | 100 créditos | Entrenamiento completo para estilo visual de producción |
| Fine-tuning completo de modelo (dataset > 200 imágenes o datos mixtos) | 300 créditos | Entrenamiento pesado, requiere plan Enterprise |
| Fine-tuning de modelo de voz (+20 minutos de muestra) | 80 créditos | Especialización de voz clonada con más datos |
| Almacenamiento de modelo fine-tuned (por mes) | Sin coste en créditos | Incluido en Enterprise |
| Inferencia con modelo personalizado (por operación) | Coste de la operación base × 1.5 | Usar un modelo fine-tuned tiene un recargo del 50% sobre la operación estándar |

### Reglas
- El entrenamiento personalizado solo está disponible en plan Enterprise o como compra adicional en Studio.
- Los modelos entrenados son propiedad del proyecto/organización. No se reutilizan para otros clientes.
- El entrenamiento requiere aprobación previa del equipo de CID para garantizar disponibilidad de GPU.
- No hay reembolso de créditos si el entrenamiento no converge (el cómputo se ejecutó igualmente).

---

## 19. Créditos por operación (conceptual)

### Tabla resumen de costes

| Categoría | Operación típica | Créditos | Rango esperado |
|---|---|---|---|
| **Storyboard** | Generar storyboard completo | 1 crédito por 5 planos | 5-40 créditos por proyecto |
| **Concept Art** | Una imagen de alta calidad | 2 créditos | 2-20 créditos por proyecto |
| **Character Bible** | Crear personaje + imagen | 2 créditos | 2-40 créditos por proyecto |
| **Visual Bible** | Definir estilo visual | 2 créditos | 2-6 créditos por proyecto |
| **Image Generation** | Una imagen estándar | 1 crédito | 1-50 créditos por proyecto |
| **Video Generation** | Video de 5-15 segundos | 5-30 créditos | 10-300 créditos por proyecto |
| **Dubbing** | 1 minuto de doblaje | 3 créditos | 10-200 créditos por proyecto |
| **Voice Cloning** | Clonar voz | 15-25 créditos | 15-150 créditos por proyecto |
| **Transcripción** | 1 minuto de audio | 0.2-0.5 créditos | 5-50 créditos por proyecto |
| **Restauración** | 1 minuto de restauración completa | 15 créditos | 30-500 créditos por proyecto |
| **Análisis IA** | Análisis completo de guion | 3 créditos | 5-30 créditos por proyecto |
| **OCR documental** | Una página escaneada | 0.1 créditos | 1-20 créditos por proyecto |
| **Agentes IA** | Tarea simple | 0.5 créditos | Variable |
| **Entrenamiento** | LoRA completo | 50-100 créditos | 50-300 créditos por entrenamiento |

### Modelo de redondeo
Los créditos fraccionarios se redondean al alza (0.1 crédito consumido = 1 crédito contabilizado) para evitar acumulación de fracciones imperceptibles.

---

## 20. Créditos incluidos por plan

| Plan | Créditos mensuales | Créditos acumulables | Prioridad de GPU | Funciones IA disponibles |
|---|---|---|---|---|
| **Starter** | 100 créditos/mes | No | Cola estándar | Storyboard, Image Gen, Transcripción, Análisis IA, OCR. Sin Video Gen, sin Voice Cloning, sin Agentes. |
| **Pro** | 300 créditos/mes | No | Cola estándar | Todo excepto Entrenamiento personalizado. Voice Cloning hasta 3 voces. |
| **Studio** | 1 000 créditos/mes | Hasta 500 créditos no usados al mes siguiente | Cola prioritaria | Todo excepto Entrenamiento personalizado. Voice Cloning hasta 10 voces. |
| **Premium** | 3 000 créditos/mes | Hasta 1 000 créditos no usados al mes siguiente | Cola prioritaria | Todo excepto Entrenamiento personalizado. Voice Cloning ilimitado. Auditoría completa. |
| **Enterprise** | Personalizado (mín. 3 000) | Sí, sin límite | Cola dedicada | Todo incluido. Entrenamiento personalizado. Prioridad en generación de video. |

### Reglas de créditos incluidos
- Los créditos se asignan al proyecto, no al usuario. Cualquier miembro del proyecto puede consumirlos según sus permisos.
- Los créditos no utilizados al final del mes se pierden (use or lose), excepto en Studio (hasta 500) y Enterprise (sin límite).
- Si un proyecto consume todos sus créditos mensuales antes de fin de mes, puede comprar créditos extra (ver §21).
- El Productor Propietario puede distribuir créditos entre usuarios o dejar el pool común.
- Los créditos consumidos por operaciones fallidas se reembolsan automáticamente si el error es imputable al sistema (no al usuario).

---

## 21. Compra de créditos extra

### Paquetes de créditos (conceptuales)

| Paquete | Créditos | Bonificación | Precio conceptual |
|---|---|---|---|
| **Recarga pequeña** | 100 créditos | — | Coste unitario base (referencia) |
| **Recarga mediana** | 500 créditos | + 10 % (550 créditos total) | Descuento por volumen |
| **Recarga grande** | 2 000 créditos | + 20 % (2 400 créditos total) | Descuento mayor |
| **Recarga enterprise** | 10 000 créditos | + 30 % (13 000 créditos total) | Descuento máximo |

### Reglas de créditos extra
- Los créditos extra tienen prioridad de consumo sobre los créditos del plan (se consumen primero los extra para evitar que caduquen).
- Los créditos extra caducan a los 12 meses de su compra.
- La compra de créditos extra no requiere cambio de plan.
- Las recargas se aplican al proyecto inmediatamente.
- El Productor Propietario puede comprar créditos extra para su proyecto. Los miembros del proyecto no pueden comprar créditos directamente.

---

## 22. Alertas de consumo

### Tipos de alerta

| Alerta | Disparador | Destinatario | Medio |
|---|---|---|---|
| **Uso elevado** | Consumo > 50 % de los créditos mensuales en los primeros 15 días del mes | Productor Propietario | Email + notificación in-app |
| **Uso crítico** | Consumo > 80 % de los créditos mensuales | Productor Propietario | Email + notificación in-app |
| **Agotamiento** | Créditos mensuales agotados | Productor Propietario + usuario que intenta operar | Email + notificación in-app + aviso en operación |
| **Créditos extra bajos** | Créditos extra < 20 % del paquete comprado | Productor Propietario | Email |
| **Pico de consumo** | Más de 50 créditos en 1 hora por un solo usuario | Productor Propietario | Notificación in-app |
| **Límite de usuario alcanzado** | Un usuario alcanza el tope definido por el Productor | Usuario + Productor | Notificación in-app |
| **Créditos a punto de caducar** | Créditos extra a menos de 30 días de caducar | Productor Propietario | Email |

### Reglas de alertas
- El Productor Propietario puede configurar umbrales personalizados.
- Las alertas no bloquean la operación (excepto si los créditos están agotados y no hay créditos extra).
- Las alertas se registran en el log de auditoría del proyecto.

---

## 23. Dashboard de consumo

### Indicadores

| Indicador | Descripción |
|---|---|
| **Créditos restantes** | Créditos del plan disponibles + créditos extra disponibles |
| **Créditos consumidos hoy** | Consumo del día actual |
| **Créditos consumidos este mes** | Consumo del ciclo mensual actual |
| **Créditos por operación** | Desglose de consumo por tipo de operación (storyboard, video, etc.) |
| **Créditos por usuario** | Consumo individual de cada miembro del proyecto |
| **Créditos por rama** | Consumo agregado por rama funcional |
| **Proyección de agotamiento** | Estimación de cuándo se agotarán los créditos al ritmo actual |
| **Créditos extra disponibles** | Saldo de créditos comprados adicionalmente |
| **Créditos a punto de caducar** | Créditos extra que caducarán en los próximos 30 días |

### Reglas del dashboard
- Visible para el Productor Propietario y Productor Ejecutivo.
- Los usuarios no-propietarios ven solo su propio consumo, no el total del proyecto (salvo autorización expresa).
- El dashboard exporta a CSV el historial de consumo de los últimos 12 meses.

---

## 24. Riesgos de abuso

| Riesgo | Descripción | Severidad | Mitigación |
|---|---|---|---|
| **R1 — Consumo masivo por un solo usuario** | Un miembro del proyecto consume todos los créditos en operaciones no esenciales (ej. image generation experimental) sin control | Alta | El Productor Propietario puede establecer topes por usuario. Alertas de pico de consumo. |
| **R2 — Automatización de consumo** | Un usuario escribe scripts o usa agentes para consumir créditos de forma automatizada sin supervisión | Alta | Límite de 20 créditos/día para agentes sin supervisión. Auditoría de acceso API. Detección de patrones anómalos. |
| **R3 — Regeneración excesiva** | Un usuario regenera storyboard o imágenes repetidamente hasta obtener el resultado deseado, consumiendo créditos sin control | Media | La regeneración tiene un límite de 5 intentos por operación antes de requerir confirmación del Productor. Cada intento adicional muestra una advertencia de consumo acelerado. |
| **R4 — Uso de voz clonada en proyectos no autorizados** | Un usuario clona una voz y la usa fuera del proyecto original | Alta | La voz clonada está vinculada al proyecto. No se permite exportar el modelo. El uso en otros proyectos requiere nueva autorización del Productor. |
| **R5 — Saturación de GPU por operaciones simultáneas** | Múltiples usuarios del mismo proyecto lanzan operaciones pesadas simultáneamente, degradando la experiencia de todos | Media | Cola de operaciones por proyecto. Límite de 2 operaciones pesadas simultáneas por proyecto (configurable en Studio+). |
| **R6 — Fraude en compra de créditos** | Un usuario compra créditos con método de pago fraudulento, los consume y luego solicita reembolso | Alta | Los créditos comprados no son reembolsables. El consumo es inmediato. El reembolso solo aplica si CID cancela el servicio. |
| **R7 — Acumulación de créditos Enterprise** | Un proyecto Enterprise acumula miles de créditos sin consumir, desvinculando el ingreso del coste real de GPU | Baja | Enterprise tiene revisión periódica de consumo. Si un proyecto acumula consistentemente, se renegocia el plan. |
| **R8 — Uso de créditos en proyectos zombi** | Un proyecto archivado o congelado sigue teniendo créditos activos que se desperdician | Baja | Los créditos se pausan cuando el proyecto pasa a estado ARCHIVADO o CONGELADO. Se reactivan al volver a ACTIVO. |

---

## 25. Protección de rentabilidad RTX 5090

**Contexto:** CID ejecuta modelos de IA en GPUs locales (infraestructura propia con RTX 5090 u otros aceleradores). El coste de computación es el principal componente de coste variable del producto. El sistema de créditos debe garantizar que los ingresos por uso de IA cubren este coste y generan margen.

### Principios de rentabilidad

1. **Coste por crédito > coste de GPU por crédito.** El precio de un crédito debe fijarse por encima del coste de computación de la operación más pesada que representa. Esto asegura que incluso en el peor caso (todo el consumo es en video generation pesado), el margen es positivo.

2. **Los créditos incluidos en el plan tienen un coste implícito.** El precio del plan de licencia incluye créditos cuyo coste de GPU está cubierto por la suscripción base. El margen del plan debe absorber el coste medio esperado de consumo de IA.

3. **Los créditos extra son puro margen.** Una vez que el plan cubre la GPU base, la venta de créditos extra es ingreso directo con un coste de GPU inferior al precio de venta.

4. **Operaciones pesadas requieren proporción de créditos mayor.** Video generation y entrenamiento tienen un coste de créditos deliberadamente alto para reflejar su coste real de GPU y evitar que usuarios intensivos erosionen el margen.

5. **Colas y priorización.** Los planes Studio+ tienen cola prioritaria. En momentos de alta demanda de GPU, los planes Starter y Pro pueden experimentar tiempos de espera mayores, lo que incentiva el upgrade.

### Modelo de coste conceptual

| Componente | Relación con créditos |
|---|---|
| GPU coste fijo (amortización RTX 5090 + mantenimiento) | Cubierto por suscripciones base + margen de créditos |
| GPU coste variable (electricidad, refrigeración, desgaste) | Cubierto por créditos consumidos |
| Modelo de IA (peso, licencia, hosting) | Incluido en el coste por crédito de cada operación |
| Almacenamiento de assets generados | Incluido en el plan (no consume créditos) |
| Ancho de banda para descarga de assets | Incluido en el plan |

### Riesgos de rentabilidad

| Riesgo | Descripción | Mitigación |
|---|---|---|
| **R1 — Cliente intensivo en GPU con plan bajo** | Un cliente Starter que solo usa video generation consume créditos cuyo coste de GPU supera el precio del plan | El coste de video generation es alto en créditos (30 créditos por 30 segundos). Un Starter tiene 100 créditos → 3 videos al mes. Si necesita más, debe comprar créditos extra o hacer upgrade. |
| **R2 — Pico de demanda simultánea** | Todos los proyectos lanzan operaciones pesadas a la vez, saturando la GPU | Cola de operaciones. Los planes superiores tienen prioridad. El sistema puede escalar horizontalmente si la demanda lo justifica. |
| **R3 — Modelo de IA más caro de lo previsto** | Un modelo open-source deja de ser gratuito o requiere licencia comercial | El coste de créditos incluye un colchón para absorber incrementos de coste de modelos. Revisión trimestral de costes. |
| **R4 — Canibalización de suscripción por créditos** | Usuarios compran el plan más barato y viven de créditos extra, erosionando el incentivo a hacer upgrade | Los planes superiores tienen coste por crédito inferior (créditos incluidos + descuento en paquetes). Un usuario intensivo siempre prefiere Studio a Starter + 3 recargas. |

---

## 26. Casos de uso productor

### Productor independiente (producción pequeña, 5-8 personas)

**Perfil:** Paula, productora de una ópera prima. Equipo reducido. Presupuesto ajustado. Necesita CID para organizar la producción y presentar material a posibles inversores.

**Consumo mensual típico:**

| Operación | Cantidad | Créditos |
|---|---|---|
| Análisis de guion (1 vez) | 1 | 3 |
| Storyboard completo (30 páginas de guion ≈ 15 planos) | 1 | 3 |
| Concept art para presentación (3 imágenes) | 3 | 6 |
| Character Bible (4 personajes principales) | 4 | 8 |
| OCR documental (10 páginas de contratos) | 10 | 1 |
| Transcripción (2 horas de entrevistas) | 120 min | 24 |
| Generación de imágenes para mood board | 20 | 20 |
| **Total** | | **65 créditos** |

**Plan recomendado:** Pro (300 créditos/mes). Con 65 créditos de consumo estimado, tiene margen para experimentar y afrontar imprevistos.

**Comportamiento esperado:** Paula usa créditos de forma irregular. Hay meses de mucha creación (storyboard, concept art) y meses de solo consulta (sin consumo de créditos). El plan Pro le da 300 créditos que usa cuando los necesita, sin preocuparse por recargas.

### Productor de cine (producción mediana, 10-20 personas)

**Perfil:** Marcos, productor de una película de 3M€. Tiene jefe de producción, director, guionista, equipo de post. La producción dura 6 meses de preproducción + 3 meses de rodaje + 4 meses de post.

**Consumo mensual típico (pico en preproducción):**

| Operación | Cantidad | Créditos |
|---|---|---|
| Análisis de guion + detección de riesgos | 2 | 6 |
| Storyboard completo (60 páginas ≈ 30 planos) | 1 | 6 |
| Concept art (10 imágenes para inversores) | 10 | 20 |
| Character Bible (8 personajes) | 8 | 16 |
| Visual Bible | 1 | 2 |
| Doblaje de secuencia para pitch (3 min, 2 idiomas) | 1 | 9 |
| Transcripción (reuniones, 5 horas) | 300 min | 60 |
| Análisis de producción (métricas) | 4 | 4 |
| OCR (20 páginas de documentación) | 20 | 2 |
| Generación de imágenes (referencias, 50) | 50 | 50 |
| **Total** | | **175 créditos** |

**Plan recomendado:** Studio (1 000 créditos/mes). El consumo de 175 créditos en pico le deja mucho margen. En meses de rodaje el consumo baja a ~50 créditos (transcripción, análisis). En post el consumo sube de nuevo (doblaje, restauración).

**Comportamiento esperado:** Marcos valora la cola prioritaria de Studio porque en preproducción el tiempo de generación importa (tiene deadlines de presentación). Los créditos acumulables hasta 500 le permiten trasladar créditos no usados de meses de rodaje a meses de post.

---

## 27. Casos de uso estudio

### Estudio de postproducción (especializado en restauración)

**Perfil:** Restaura Films, estudio que digitaliza y restaura archivo fílmico. 15 empleados. Trabajan con material antiguo (B/N, deteriorado) y necesitan restauración intensiva.

**Consumo mensual típico:**

| Operación | Cantidad | Créditos |
|---|---|---|
| Restauración completa de corto (10 min) | 10 min × 15 créditos | 150 |
| Restauración de audio (10 min) | 10 min × 0.5 créditos | 5 |
| Transcripción de diálogos restaurados (10 min) | 10 min × 0.3 | 3 |
| OCR de documentación de archivo (100 páginas) | 100 | 10 |
| Análisis IA de metraje (detección de escenas) | 5 análisis | 5 |
| Video previews para cliente (5 previews) | 5 | 5 |
| **Total** | | **178 créditos** |

**Plan recomendado:** Studio (1 000 créditos/mes) + recarga mediana mensual (500 créditos extra). El consumo de ~1 200 créditos/mes justifica una recarga periódica.

**Comportamiento esperado:** El uso es estable y predecible. Cada proyecto de restauración tiene un coste conocido en créditos: 150 créditos por 10 minutos de restauración. El estudio cobra a sus clientes incluyendo el coste de créditos CID como parte del presupuesto. La cola prioritaria es esencial porque el estudio trabaja con entregas semanales.

### Estudio de animación (uso intensivo de Storyboard + Video Gen)

**Perfil:** Animatoon, estudio de animación 2D. 25 empleados. Usan CID para previz, storyboard y animatics. Generan mucho contenido visual cada semana.

**Consumo mensual típico:**

| Operación | Cantidad | Créditos |
|---|---|---|
| Storyboard (5 secuencias por semana = 20/mes) | 20 | 100 |
| Image generation (fondos, personajes, props) | 200 | 200 |
| Video generation (animatics, 15 segundos cada uno) | 10 videos × 15 créditos | 150 |
| Character Bible (creación + variantes) | 5 personajes | 15 |
| Análisis IA de guion (episodios) | 10 análisis | 30 |
| Doblaje de preview (5 min × 3 idiomas) | 5 × 5 créditos | 25 |
| Voice Cloning (voces de personajes recurrentes) | 3 nuevas/mes | 60 |
| **Total** | | **580 créditos** |

**Plan recomendado:** Studio (1 000 créditos/mes). Con 580 créditos de consumo, tienen margen. La cola prioritaria de Studio es importante porque generan contenido constantemente y no pueden esperar en cola estándar. Acumulan créditos de meses tranquilos para meses intensivos de entrega.

---

## 28. Qué NO definir todavía

| Aspecto | Motivo |
|---|---|
| **Precio en euros/dólares por crédito** | Depende de costes de GPU, estrategia de pricing y mercado objetivo. Debe definirse en la fase de fijación de precios, no en arquitectura de producto. |
| **Sistema de facturación (Stripe, etc.)** | Depende de la pila tecnológica y del proveedor de pagos. No es arquitectura de producto. |
| **Modelo de reembolsos y disputas** | Depende de términos legales y proveedor de pagos. |
| **Impuestos (IVA, VAT, etc.)** | Depende de jurisdicción fiscal y estrategia de internacionalización. |
| **Conversión entre créditos y moneda local** | Debe definirse en la fase de pricing, no aquí. |
| **Integración con ERP/accounting** | Depende del stack contable del cliente Enterprise. No es parte del producto base. |
| **Programa de referidos o créditos promocionales** | Estrategia de marketing, no de producto. |
| **Mercado de créditos entre proyectos** | Riesgo de arbitraje y canibalización. Solo explorar si hay demanda explícita. |
| **Créditos por acción social (descuento por proyectos culturales)** | Política de precios, no de producto. |
| **Modelo de suscripción freemium** | Decisión comercial pendiente. No definida. |
| **API pública de generación para terceros** | Requiere modelo de seguridad y facturación independiente. |

---

## 29. Próxima fase

**CID.PRODUCT.ARCHITECTURE.DATA.MODEL.1** — Revisar el modelo de datos (`cid_project_command_center_data_model_v1.md`) para:

1. Añadir entidades necesarias para el sistema de créditos: `CreditPool`, `CreditTransaction`, `CreditPackage`, `CreditAlert`.
2. Definir relaciones entre `CreditPool` y `Project`, `User`, `Operation`.
3. Definir campos para seguimiento de consumo por operación, por usuario, por rama.
4. Evaluar si el modelo de datos actual puede soportar la contabilidad de créditos sin cambios estructurales.

---

## Historial de revisiones

| Fecha | Versión | Cambios |
|---|---|---|
| 2026-06-02 | 1.0 | Creación inicial del modelo de negocio de créditos IA con 29 secciones. |
| 2026-06-03 | 1.1 | Añadido plan Premium: §20 (3.000 créditos/mes, acumulación 1.000, cola prioritaria, Voice Cloning ilimitado). 5 planes alineados con Access Model y Pricing. |
