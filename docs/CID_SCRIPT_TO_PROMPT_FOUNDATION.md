# CID Script-to-Prompt Foundation

## Vision

CID no debe generar imagenes por estilo ni por intuicion superficial. Debe operar como un sistema narrativo y cinematografico trazable donde cada salida visual nace de un fragmento concreto del guion, se traduce a una intencion visual controlada y se valida antes y despues de render.

Objetivo canonico:

`guion -> analisis estructurado -> intencion visual por secuencia/escena -> prompt cinematografico controlado -> validacion semantica -> imagen/video -> QA visual -> continuidad`

Esto corrige el problema revelado por la landing: imagenes visualmente atractivas pero semanticamente debiles, ambiguas o reutilizables para escenas que no comparten la misma funcion dramatica.

## Diagnostico del problema real

### Que esta fallando

- Prompts demasiado genericos o reutilizables entre escenas distintas.
- Traduccion pobre entre accion dramatica y gramatica visual.
- Ausencia de anclajes fuertes a guion, escena, personaje y localizacion.
- Exceso de abstraccion tecnologica y de “tech art” en salidas que deberian representar produccion cinematografica concreta.
- Falta de reglas explicitas sobre que debe verse y que no debe verse para cada output type.
- Falta de validacion semantica previa al render y de QA visual posterior.
- Falta de memoria de continuidad entre escenas, planos y variantes.

### Por que falla

Porque el pipeline actual puede saltar demasiado pronto de texto a prompt visual sin pasar por una capa robusta de parseo narrativo, intencion cinematografica y validacion de correspondencia.

### Que capa debe corregirse primero

La primera capa a corregir es la union entre `Narrative Parsing`, `Cinematic Intent Layer` y `Prompt Construction Layer`. Si esa traduccion no es robusta, cualquier render posterior sera bonito pero semanticamente fragil.

## Canonical CID Pipeline

### 1. Script Intake

#### Input
- guion completo
- metadatos del proyecto
- idioma
- genero
- tono
- referencias visuales si existen

#### Responsibilities
- limpiar y normalizar el texto
- detectar secuencias y escenas
- normalizar nombres de personajes
- normalizar localizaciones
- detectar acciones clave y transiciones

#### Output
- script limpio
- secuencias detectadas
- escenas detectadas
- personajes normalizados
- localizaciones normalizadas
- acciones clave detectadas

### 2. Narrative Parsing

Por cada secuencia y escena, CID debe extraer:
- objetivo dramatico
- conflicto
- emocion dominante
- personajes implicados
- localizacion
- tiempo del dia
- accion principal
- accion secundaria
- atmosfera
- ritmo
- relevancia narrativa

No es suficiente resumir texto. Esta capa debe producir una interpretacion cinematica y operativa util para direccion, storyboard, arte y produccion.

### 3. Production Breakdown

Por cada escena, CID debe extraer:
- personajes
- props
- vestuario inferible
- FX / VFX si aplica
- necesidades de produccion
- interior / exterior
- continuidad necesaria
- dependencias entre escenas

Esta capa conecta narrativa y produccion. Evita prompts visuales que ignoran restricciones reales del rodaje o post.

### 4. Cinematic Intent Layer

CID debe traducir la escena a lenguaje visual controlado:
- tipo de plano recomendado
- tamano de plano
- angulo
- altura de camara
- focal sugerida
- movimiento sugerido
- iluminacion narrativa
- paleta
- blocking
- composicion
- textura visual
- referente emocional de la imagen

La salida de esta capa no es una imagen. Es una especificacion cinematografica.

### 5. Prompt Construction Layer

CID genera prompts por tipo de salida:
- analysis view
- moodboard
- concept art
- storyboard frame
- key visual
- controlled frame generation
- image-to-video anchor

Todo prompt debe contener estos anchors:
- script anchor
- scene anchor
- character anchor
- location anchor
- action anchor
- cinematic anchor
- style anchor
- continuity anchor
- exclusion / negative anchor

### 6. Semantic Validation Layer

Antes del render, CID debe verificar:
- que el prompt corresponde a la escena correcta
- que representa accion, personajes y localizacion correctos
- que no deriva a abstraccion vacia
- que no contradice la intencion dramatica
- que el output_type coincide con el bloque o producto esperado
- que el prompt no sirve indistintamente para cinco escenas distintas

### 7. Visual QA Layer

Despues del render, CID debe evaluar:
- imagen vs intencion visual
- imagen vs texto/copy
- imagen vs continuidad de proyecto

Veredictos minimos:
- semantically_correct
- visually_weak
- too_abstract
- wrong_subject
- wrong_cinematic_grammar
- continuity_risk
- needs_regen

## Canonical Data Objects

### ScriptSequence

```json
{
  "sequence_id": "seq_003",
  "title": "Decision in the meeting room",
  "start_page": 12,
  "end_page": 15,
  "summary": "The director reviews the visual plan while the team waits.",
  "dramatic_function": "decision_turning_point",
  "emotional_tone": "contained_tension",
  "scenes": ["scene_003_01", "scene_003_02"]
}
```

### ScriptScene

```json
{
  "scene_id": "scene_003_01",
  "sequence_id": "seq_003",
  "slugline": "INT. SALA DE REUNIONES - NOCHE",
  "location": "sala de reuniones",
  "interior_exterior": "interior",
  "time_of_day": "night",
  "characters": ["DIRECTORA", "EQUIPO"],
  "action_summary": "La directora revisa el storyboard antes de tomar una decision.",
  "narrative_goal": "visual_decision",
  "emotional_state": "creative_tension",
  "production_notes": ["pantallas", "storyboard impreso o digital", "equipo en espera"],
  "continuity_notes": ["mantener misma paleta ambar/cian", "mismo espacio visual para secuencia"]
}
```

### CinematicIntent

```json
{
  "intent_id": "intent_scene_003_01_storyboard_review",
  "scene_id": "scene_003_01",
  "visual_goal": "hacer visible la toma de decisiones sobre storyboard",
  "subject_priority": ["directora", "storyboard", "pantallas de revision"],
  "framing": "medium_wide",
  "angle": "eye_level",
  "lens": "40mm_equivalent",
  "camera_movement": "static_or_subtle_push",
  "lighting": "warm practical + cool screen balance",
  "palette": ["charcoal", "amber", "soft cyan"],
  "mood": "contained_tension",
  "composition_notes": "clear focal hierarchy, breathing room, review table visible",
  "exclusions": ["generic futuristic HUD", "meaningless abstract glow"]
}
```

### PromptSpec

```json
{
  "prompt_id": "prompt_scene_003_01_storyboard_frame_v1",
  "scene_id": "scene_003_01",
  "output_type": "storyboard_frame",
  "prompt": "...",
  "negative_prompt": "...",
  "required_elements": ["storyboard panels", "director review context", "night interior"],
  "forbidden_elements": ["single abstract frame", "unrelated character", "generic sci-fi UI"],
  "continuity_constraints": ["same room palette as previous scene", "same wardrobe anchor"],
  "semantic_tags": ["storyboard", "review", "interior_night", "creative_tension"],
  "confidence_score": 0.88
}
```

### VisualQAEvaluation

```json
{
  "prompt_id": "prompt_scene_003_01_storyboard_frame_v1",
  "output_asset": "scene_003_01_storyboard_frame_v1.webp",
  "semantic_match_score": 0.91,
  "cinematic_match_score": 0.86,
  "continuity_score": 0.84,
  "issues": ["storyboard_panels_not_explicit_enough"],
  "verdict": "needs_regen"
}
```

## Script -> Prompt Translation Rules

### Core rules

1. Todo prompt debe nombrar sujeto principal explicito.
2. Todo prompt debe contener accion explicita.
3. Todo prompt debe contener entorno explicito.
4. Todo prompt debe contener intencion visual explicita.
5. Todo prompt debe contener exclusiones claras.
6. Ningun prompt puede ser intercambiable entre escenas dramaticamente distintas.

### Output-type rules

#### Analysis View
- Debe representar parseo y desglose de guion.
- No debe parecer una escena narrativa generica.
- Debe mostrar estructura, entidades, relaciones o breakdown.

#### Moodboard
- Debe representar referencias de personaje, atmosfera, paleta, localizacion o vestuario.
- No debe reducirse a una sola imagen hero oscura.
- Debe sentirse editorial y de direccion artistica.

#### Storyboard
- Debe incluir gramatica de storyboard o previsualizacion.
- Debe mostrar varios paneles o equivalentes visuales de secuencia.
- No debe ser solo un frame bonito.

#### Controlled Frame Generation
- Debe representar pipeline, preparacion de prompt, generacion y validacion.
- No debe parecer una imagen narrativa sin proceso.

### Heuristics

- evitar prompt bonito pero vacio
- evitar terminos demasiado abstractos
- evitar tech art cuando el objetivo es produccion cinematografica
- exigir sujeto principal explicito
- exigir accion explicita
- exigir entorno explicito
- exigir intencion visual explicita

## Cinematic Coherence Subpipeline

### 1. Scene Memory
Mantiene el estado visual y narrativo de una escena concreta: sujetos, accion, tono, blocking, clima, iluminacion y proposito visual.

### 2. Character Visual Memory
Mantiene anclajes persistentes por personaje:
- rasgos visuales
- vestuario por secuencia
- energia emocional
- relacion espacial con otros personajes

### 3. Location Visual Memory
Mantiene persistencia de:
- arquitectura
- layout
- luz base
- props fijos
- textura del entorno

### 4. Sequence Style Memory
Mantiene cohesion por secuencia:
- paleta
- cobertura
- densidad visual
- movimiento dominante
- progresion emocional

### 5. Project Visual Bible
Memoria maestra del proyecto:
- tono general
- referencias canonicas
- restricciones de estilo
- reglas de continuidad
- prohibiciones visuales

### Uso por tipo de salida

- storyboard: usa Scene Memory + Character Visual Memory + Sequence Style Memory
- concept art: usa Project Visual Bible + Location Visual Memory + Character Visual Memory
- moodboard: usa Project Visual Bible + Sequence Style Memory
- key visual: usa Project Visual Bible + Cinematic Intent
- video coherente futuro: usa todas las memorias, especialmente Scene Memory y continuity constraints frame-to-frame

## Landing as Product Proof

### 1. Analisis de guion

- output type: `analysis_view`
- input de guion necesario: slugline, personajes, localizacion, acciones, necesidades de produccion, shot hints
- debe verse: guion, breakdown, personajes, localizaciones, planos, produccion
- no debe verse: nodos genericos, abstraccion vacia, solo una pantalla bonita
- prompt: debe partir de script anchor + production breakdown + narrative parsing
- validacion: la imagen debe leerse como desglose cinematografico, no como UI vaga

### 2. Moodboards visuales

- output type: `moodboard`
- input de guion necesario: atmosfera, personajes, vestuario inferible, localizacion, tono, textura visual
- debe verse: referencias visuales, personaje, vestuario, paleta, atmosfera, localizaciones
- no debe verse: figura aislada de espaldas, abstraccion sin contexto, escena cerrada demasiado oscura
- prompt: debe anclar personaje + atmosfera + art direction + board layout
- validacion: la imagen debe funcionar como board editorial de direccion artistica

### 3. Storyboards cinematograficos

- output type: `storyboard_frame` o `storyboard_board`
- input de guion necesario: accion principal, progresion de plano, blocking, continuidad entre beats
- debe verse: varios paneles, encuadres, flechas, continuidad, lenguaje de previsualizacion
- no debe verse: una sola foto hero, collage abstracto, moodboard disfrazado de storyboard
- prompt: debe anclar shot list + camera grammar + sequence continuity
- validacion: si no parece storyboard en 2-3 segundos, falla

### 4. Generacion visual controlada

- output type: `controlled_frame_generation`
- input de guion necesario: scene anchor, action anchor, cinematic intent, style anchor, validation criteria
- debe verse: preparacion de prompt, pipeline nodal, frame generado, checkpoint de validacion
- no debe verse: un solo nodo, una escena narrativa sin proceso, caos visual tecnico
- prompt: debe describir pipeline y control, no solo output artistico
- validacion: si no se entiende prompt -> generacion -> control, falla

## Proposed Future Backend Services

- `script_scene_parser_service.py`: segmenta secuencias/escenas y normaliza entidades
- `cinematic_intent_service.py`: traduce narrativa a gramatica visual
- `prompt_construction_service.py`: compone PromptSpec por output type
- `semantic_prompt_validation_service.py`: valida correspondencia escena/prompt/output
- `visual_qc_service.py`: califica imagen resultante contra intent y copy
- `continuity_memory_service.py`: administra memorias de personaje, localizacion, secuencia y proyecto

## Foundation Outcome

Cuando esta base opera correctamente, CID no genera imagenes porque si. Entiende el guion, traduce la escena a intencion cinematografica, construye prompts controlados, valida semanticamente la salida y mantiene coherencia narrativa y visual.
