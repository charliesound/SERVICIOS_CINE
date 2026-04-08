# Cinematic Planning V3

## Objetivo
- usar parsed_scenes y scene_breakdowns para proponer una cobertura visual mas razonable
- clasificar beats por tipo (dialogue, action, exposition, reaction, insert)
- asignar shot_intent util (establishing, wide, medium, close_up, two_shot, over_shoulder, insert, reaction, detail)
- incluir motivacion breve por beat
- mejorar la seleccion de shot_type en el planner sin romper compatibilidad

## Reglas minimas
- localizacion nueva -> establishing o wide inicial
- dialogo entre 2+ personajes -> two_shot + over_shoulder + reaction
- accion dominante -> wide de orientacion + medium/close de detalle
- props relevantes -> insert/detail cuando tenga sentido narrativo
- moving_elements -> priorizar claridad espacial
- semi_moving_elements -> planos de apoyo cuando contribuyan

## Integracion con planner
- cinematic_planning_service.py genera beats planificados desde scene_breakdowns
- sequence_planner_service.py usa planned_beats si existen, fallback a heuristico
- _resolve_shot_type_from_planning() mapea shot_intent a shot_type del sistema actual
- si no hay shot_intent, cae al selector heuristico existente

## Fuera de alcance
- eje 180 formal
- blocking 3D
- direccion de fotografia avanzada
- parser Fountain/FDX

## Estado esperado de V3
- cobertura conversacional basica para dialogo
- orientacion espacial para accion
- inserts razonables para props
- fallback intacto si no hay estructura suficiente
