# Continuidad de Eje Formal V1

## Objetivo
- asignar continuidad espacial simple en escenas conversacionales
- mantener coherencia de eje, direccion de mirada y posicion relativa entre personajes
- mejorar coherencia de two_shot, over_shoulder, reaction y close_up conversacional

## Reglas minimas
- detectar escenas/beats con potencial conversacional (2+ personajes hablando)
- establecer axis_side consistente para toda la conversacion
- asignar eyeline_direction hacia el interlocutor
- definir screen_position (left_third/right_third/centered) alternando por shot
- establecer counterpart_anchor para reaction y over_shoulder

## Integracion con planner
- continuity_formal_service.py genera continuidad por shot
- sequence_planner_service.py asigna continuity_formal a cada shot conversacional
- si no hay escena conversacional, no asigna continuidad (None)
- no rompe grounding, render inputs ni shots existentes

## Fuera de alcance
- eje 180 completo con geometria espacial
- blocking 3D
- reconstruccion espacial compleja
- evaluacion visual automatica

## Estado esperado de V1
- coherencia visual mejorada en dialogos
- fallback intacto si no hay informacion suficiente
- no se inventa continuidad absurda en escenas no conversacionales
