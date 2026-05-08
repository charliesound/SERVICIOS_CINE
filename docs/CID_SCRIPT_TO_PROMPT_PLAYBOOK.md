# CID Script-to-Prompt Playbook

## Purpose

Este playbook convierte la promesa de CID en una operativa repetible. Sirve para equipos de producto, narrativa, storyboard, arte y rendering que necesiten pasar de guion a salida visual con trazabilidad y coherencia.

## Step-by-step Flow

### Step 1. Script Intake

#### Entra
- guion completo
- idioma
- genero
- tono
- referencias existentes
- restricciones de cliente o proyecto

#### Sale
- texto limpio
- secuencias detectadas
- escenas detectadas
- personajes normalizados
- localizaciones normalizadas

#### Criterio de calidad
- no hay personajes duplicados por naming inconsistente
- no hay escenas sin slugline interpretada
- el texto queda listo para parseo semantico

### Step 2. Narrative Parsing

#### Entra
- escena limpia
- contexto de secuencia

#### Sale
- objetivo dramatico
- conflicto
- emocion dominante
- accion principal
- accion secundaria
- atmosfera
- relevancia narrativa

#### Criterio de calidad
- la escena no queda resumida solo como “una conversacion” o “momento dramatico”
- la accion y la intencion quedan operables para camara y arte

### Step 3. Production Breakdown

#### Entra
- escena parseada

#### Sale
- personajes
- props
- vestuario inferible
- necesidades tecnicas
- interior/exterior
- continuidad necesaria

#### Criterio de calidad
- el breakdown sirve tanto a produccion como a imagen
- se detectan elementos que afectan storyboard, arte o continuidad

### Step 4. Cinematic Intent

#### Entra
- scene parsing
- production breakdown
- project visual bible

#### Sale
- framing
- angle
- lens
- movement
- palette
- lighting
- composition
- emotional visual goal

#### Criterio de calidad
- la intencion visual no es generica
- la escena puede traducirse a storyboard, moodboard y frame controlado sin perder sentido

### Step 5. Prompt Construction

#### Entra
- scene anchor
- cinematic intent
- output type
- continuity memory

#### Sale
- PromptSpec

#### Criterio de calidad
- contiene required elements claros
- contiene forbidden elements claros
- no podria aplicarse indistintamente a escenas diferentes

### Step 6. Semantic Validation

#### Entra
- PromptSpec
- ScriptScene
- CinematicIntent

#### Sale
- validado / rechazado
- lista de issues

#### Criterio de calidad
- si el prompt se vuelve abstracto, se bloquea
- si el sujeto principal no aparece, se bloquea
- si el output type no coincide con el objetivo, se bloquea

### Step 7. Render

#### Entra
- PromptSpec validado
- workflow/render backend

#### Sale
- imagen candidata
- metadatos de render

#### Criterio de calidad
- output trazable a escena y prompt exactos
- seeds, workflow y anchors preservados

### Step 8. Visual QA

#### Entra
- imagen renderizada
- PromptSpec
- CinematicIntent
- copy/product context si aplica

#### Sale
- VisualQAEvaluation
- veredicto
- decision: aprobar, regenerar, remapear o descartar

#### Criterio de calidad
- la imagen se entiende visualmente sin explicacion adicional
- representa el texto correcto
- mantiene coherencia con el resto de la secuencia o producto

## Failure Modes

### Failure: prompt generico

#### Sintoma
La misma imagen podria servir para cinco escenas distintas.

#### Correccion
Forzar scene anchor, action anchor y subject priority.

### Failure: imagen bonita pero sin sentido

#### Sintoma
Buena luz y estilo premium, pero no representa el copy ni el objetivo del output.

#### Correccion
Revisar output type rules y required elements.

### Failure: storyboard que parece poster

#### Sintoma
Sale una sola imagen fuerte en lugar de previsualizacion secuencial.

#### Correccion
Exigir multiple-panel grammar, shot logic y continuity marks.

### Failure: moodboard que parece frame aislado

#### Sintoma
No hay estructura editorial ni referencias.

#### Correccion
Exigir board layout, palette cues, character references y location references.

### Failure: generacion controlada que no muestra control

#### Sintoma
La imagen no enseña prompt, pipeline ni validacion.

#### Correccion
Exigir flow clarity: prompt -> generation -> checkpoint.

## Operational Rules by Output Type

### analysis_view
- debe mostrar estructura y entidades
- no debe verse como concept art ni como frame hero

### moodboard
- debe parecer board editorial
- no debe parecer una sola escena cinematica cerrada

### storyboard_frame / storyboard_board
- debe tener gramatica de storyboard
- no puede ser solo belleza atmosferica

### controlled_frame_generation
- debe mostrar proceso y control
- no puede perder legibilidad por sobrecarga tecnica

### key_visual
- puede ser la salida mas artistica
- pero sigue anclada a scene/sequence/project visual bible

## Quality Gates

### Gate 1. Narrative Gate
- la salida representa el objetivo dramatico de la escena

### Gate 2. Semantic Gate
- personajes, localizacion, accion y tono coinciden

### Gate 3. Cinematic Gate
- framing, composicion y lighting responden a la intencion visual

### Gate 4. Continuity Gate
- no rompe personaje, localizacion, secuencia o project bible

### Gate 5. Product Gate
- si la salida se usa en landing/demo, la imagen comunica el feature correcto

## Landing Application Checklist

### Analisis de guion
- script visible
- breakdown visible
- personajes/localizaciones/planos/produccion visibles

### Moodboards visuales
- board editorial real
- referencias multiples
- direccion artistica clara

### Storyboards cinematograficos
- varios paneles
- lenguaje de previsualizacion
- continuidad visible

### Generacion visual controlada
- prompt visible o inferible
- pipeline nodal claro
- frame generado
- validacion/coherencia

## Proposed Service Responsibilities

- `script_scene_parser_service.py`: produce ScriptSequence y ScriptScene
- `cinematic_intent_service.py`: produce CinematicIntent
- `prompt_construction_service.py`: produce PromptSpec por output type
- `semantic_prompt_validation_service.py`: aplica semantic gates
- `visual_qc_service.py`: produce VisualQAEvaluation
- `continuity_memory_service.py`: provee memorias y restricciones persistentes

## Playbook Outcome

Si el equipo sigue este flujo, CID deja de generar “imagenes bonitas” sin relacion con el guion y pasa a generar salidas trazables, cinematograficamente utiles y semanticamente defendibles.
