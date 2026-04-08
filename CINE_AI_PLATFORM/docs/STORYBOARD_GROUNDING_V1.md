# Storyboard Grounding V1

## Objetivo
- transformar la planificacion cinematografica en informacion visual concreta para shots/prompts
- usar shot_intent, beat_type y scene_breakdowns para seleccionar sujetos, localizacion, props y accion
- enriquecer prompt_base con composicion, enfoque y contexto visual
- evitar prompts barrocos o sobrecargados

## Reglas minimas
- establishing -> espacio, localizacion, composicion abierta
- wide -> orientacion espacial, cuerpo completo o accion
- medium -> cobertura equilibrada
- close_up -> enfasis facial o emocional
- two_shot -> dos personajes, relacion espacial clara
- over_shoulder -> conversacion, eje implicito
- insert/detail -> prop u objeto dominante
- reaction -> emocion o respuesta del personaje

## Integracion con planner
- storyboard_grounding_service.py genera grounding por beat
- sequence_planner_service.py usa grounding para enriquecer prompt_base
- si no hay breakdowns o shot_intent, cae al comportamiento heuristico actual
- grounding se expone en cada shot para uso futuro

## Fuera de alcance
- eje 180 formal
- blocking avanzado
- evaluacion visual de imagenes
- ranking de imagenes

## Estado esperado de V1
- prompts mas alineados con intencion cinematografica
- seleccion controlada de sujetos, props y localizacion
- composicion adaptada a shot_intent
- fallback intacto si falta informacion
