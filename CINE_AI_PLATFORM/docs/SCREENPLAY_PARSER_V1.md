# Screenplay Parser V1

## Objetivo
- leer `script_text` con formato screenplay de texto plano
- detectar escenas con headings tipo `INT.`, `EXT.`, `INT/EXT.`
- separar bloques de accion y dialogo
- detectar personaje hablante cuando hay cue claro en mayusculas
- entregar una estructura minima reutilizable por el planner actual

## Entrada
- `script_text` como texto plano

## Salida minima
- `parsed_scenes[]`
- por escena:
  - `scene_id`
  - `heading`
  - `location`
  - `time_of_day`
  - `action_blocks[]`
  - `dialogue_blocks[]`
  - `characters_detected[]`

## Reglas V1
- considera heading valido si la linea empieza por `INT.`, `EXT.`, `INT/EXT.` o `I/E.`
- crea escena nueva por cada heading valido
- interpreta cue de personaje como linea mayoritariamente en mayusculas
- soporta dialogo multilinea bajo el mismo personaje mientras no aparezca otro cue o heading
- acumula accion como bloques de texto entre cues/blank lines

## Integracion con planner
- el planner intenta parsear primero con `ScreenplayParserService`
- si obtiene escenas validas, genera beats desde `action_blocks` y `dialogue_blocks`
- si no obtiene estructura suficiente, cae al flujo heuristico anterior sin romperse

## Fuera de alcance
- parser Fountain completo
- parser FDX / Final Draft
- breakdown avanzado de props
- semovientes / semimovientes
- cobertura cinematografica avanzada

## Estado esperado de V1
- util para guiones de texto plano relativamente limpios
- no sustituye aun a un parser cinematografico completo
- mejora el punto de partida del planner respecto al texto libre heuristico
