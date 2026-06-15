# AILink CID - Real Project Pilot Processing Flow

**Phase ID:** AILINK.CID.REAL.PROJECT.PILOT.PROCESSING.PHASE6.3
**Version:** 1.0
**Date:** 2026-06-15
**Status:** flujo privado de procesamiento del primer piloto real, documentación + tests solamente

## 1. Objetivo del piloto real privado

Definir el flujo operativo privado y seguro para procesar el primer guion real autorizado del fundador/usuario, sin introducir el guion, datos reales, respuestas reales, outputs reales ni material confidencial dentro del repositorio.

El primer piloto real utiliza un guion propio autorizado del fundador/usuario, tratado como primer cliente interno-real de CID.

Flujo objetivo:

```text
guion real autorizado
→ intake privado fuera del repo
→ respuestas de cuestionarios fuera del repo
→ procesamiento controlado
→ revisión humana
→ entregables privados
→ feedback del founder
→ decisión de mejoras
```

Esta fase no procesa el guion real. Solo documenta el flujo de procesamiento que se ejecutará en el piloto.

## 2. Materiales permitidos y prohibidos

### Materiales permitidos en el repo

- Esta definición de flujo de procesamiento.
- Plantillas genéricas de intake (definidas en Phase6.2).
- Feedback agregado del founder sin material confidencial.
- Notas de incertidumbre y revisión humana genéricas.

### Materiales prohibidos en el repo

- Guion real.
- Título real del proyecto.
- Escenas reales.
- Diálogos reales.
- Personajes reales o nombres de personajes confidenciales.
- Localizaciones reales.
- Nombres de personas reales.
- Presupuesto real.
- Respuestas reales del founder o del equipo.
- Outputs reales del procesamiento.
- Datos reales del proyecto.
- Material confidencial de cualquier tipo.

## 3. Ubicación privada fuera del repo

El procesamiento del piloto real se ejecuta en una ubicación privada fuera del repositorio.

### Estructura lógica prevista

La estructura lógica de trabajo es la siguiente. No debe crearse físicamente en esta fase:

```text
<directorio_privado_fuera_del_repo>/
├── intake/          ← cuestionarios cumplimentados
├── questionnaires/  ← plantillas y respuestas
├── processing/      ← notas de procesamiento
├── outputs/         ← entregables generados
└── feedback/        ← feedback del founder
```

No se define ruta concreta, título del proyecto, nombre del founder ni datos confidenciales en esta fase.

## 4. Preparación del intake privado

Antes de procesar el guion real:

1. Confirmar que el fundador/usuario ha autorizado explícitamente el uso del guion para el piloto privado.
2. Confirmar titularidad o permiso suficiente sobre el material.
3. Confirmar alcance autorizado del análisis.
4. Confirmar quién puede revisar resultados.
5. Utilizar las plantillas genéricas de intake definidas en Phase6.2.
6. No incluir en el repo las respuestas reales del intake.

## 5. Cumplimentación de cuestionarios fuera del repo

Los cuestionarios por rol se cumplimentan fuera del repositorio.

Reglas:

- Cuestionarios genéricos de Phase6.2 como base.
- Respuestas reales fuera del repo en todo momento.
- No versionar respuestas reales.
- No incluir en el repo datos reales de ninguna respuesta.
- CID utiliza las respuestas para adaptar recomendaciones, marcar incertidumbres y asignar nivel de confianza.

## 6. Flujo de procesamiento controlado

El procesamiento del piloto real sigue un flujo controlado paso a paso:

```text
1. Confirmación de autorización y titularidad
2. Intake privado con plantillas genéricas
3. Cumplimentación de cuestionarios por rol
4. Análisis/desglose de producción
5. Storyboard textual / shotlist preliminar
6. Presupuesto preliminar revisable
7. Plan de rodaje preliminar para ayudantía de dirección
8. Checklist de rodaje
9. Paquete de traspaso a postproducción
10. Revisión humana del founder
11. Entrega de entregables privados
12. Registro de feedback del founder
13. Decisión de mejoras
```

En cada paso CID debe:

- marcar incertidumbres cuando falten datos;
- asignar nivel de confianza (alto, medio, bajo);
- recomendar con mano izquierda, tono diplomático y profesional;
- sugerir, no imponer;
- explicar por qué recomienda algo;
- no sustituir productor, director, ayudante de dirección ni jefes de departamento;
- pedir datos adicionales cuando sea necesario.

## 7. Revisión humana del founder

Toda entrega del piloto requiere revisión humana obligatoria del fundador/usuario.

La revisión humana debe confirmar:

- que el material usado está autorizado;
- que los límites de la beta se entienden;
- que los entregables son preliminares;
- que no se sustituyen roles profesionales;
- que el procesamiento fue privado y controlado.

CID puede preguntar, ordenar, explicar, aconsejar y marcar incertidumbres, pero no impone decisiones.

## 8. Entregables privados esperados

Los entregables privados del piloto se generan fuera del repo y no se versionan.

Entregables esperados:

- resumen de producción privado;
- desglose preliminar privado;
- storyboard textual / shotlist preliminar privado;
- presupuesto preliminar revisable privado;
- plan de rodaje preliminar para ayudantía privado;
- checklist de rodaje privado;
- paquete de traspaso a postproducción privado;
- notas de incertidumbre y revisión humana.

Todos los entregables deben marcarse como preliminares. No se generan en esta fase; solo se definen como entregables esperados.

## 9. Qué no debe versionarse

No debe versionarse dentro del repositorio:

- guion real;
- fragmentos de guion;
- título real del proyecto;
- escenas reales;
- diálogos reales;
- personajes reales o nombres de personajes confidenciales;
- localizaciones reales;
- nombres de personas reales;
- presupuesto real;
- respuestas reales del founder o del equipo;
- outputs reales del procesamiento;
- datos reales del proyecto;
- material confidencial de cualquier tipo;
- fixtures reales;
- outputs del piloto.

## 10. Registro de feedback sin material confidencial

El feedback del fundador/usuario se registra de forma agregada sin revelar material confidencial.

Reglas:

- Feedback agregado: qué funcionó, qué no, qué mejorar.
- No incluir fragmentos de guion, nombres de personajes, escenas específicas ni diálogos.
- No incluir presupuesto real ni datos reales del proyecto.
- Feedback válido para mejorar el flujo de CID sin exponer el material del piloto.

## 11. Criterios de éxito del piloto

El piloto se considera exitoso si:

- el flujo completo se ejecuta de extremo a extremo;
- el procesamiento es privado y controlado;
- no se filtra material confidencial al repo;
- los entregables preliminares se generan correctamente;
- CID marca incertidumbres y nivel de confianza en cada paso;
- CID recomienda con mano izquierda y tono profesional;
- la revisión humana del founder se realiza en cada entrega;
- el feedback del founder se registra sin material confidencial;
- se identifican mejoras para futuras versiones.

## 12. Decisiones posteriores al piloto

Tras el piloto, el fundador/usuario decidirá:

- si el flujo es suficiente para la beta de octubre;
- qué mejoras implementar;
- si expandir a más casos reales autorizados;
- si ajustar cuestionarios o entregables;
- si modificar el alcance de la beta pública.

Estas decisiones se documentarán en fases posteriores.

## 13. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Filtración de material confidencial al repo | Prohibición explícita de incluir guion, título, escenas, diálogos, personajes, localizaciones, nombres, presupuesto real o outputs reales. |
| Confusión entre demo y piloto real | Phase4 Demo Bruma queda como demo histórica. El piloto real es un caso nuevo, autorizado y privado. |
| Sobre-promesa de capacidades | Entregables marcados como preliminares. CID sugiere, no impone. Revisión humana obligatoria. |
| Procesamiento sin revisión humana | Toda entrega requiere revisión humana del founder antes de continuar. |
| Uso de material sin autorización | Confirmación de autorización y titularidad antes de cualquier análisis. |
| Reutilización entre clientes | Prohibición explícita. Memoria aislada por tenant/proyecto. |
| Entrenamiento de modelos con material real | Prohibición explícita. No se entrenan modelos con material del piloto. |

## 14. Criterios de aceptación

La fase se considera aceptada si:

- define el primer piloto real con guion propio autorizado;
- define al fundador/usuario como primer cliente interno-real;
- documenta el flujo de procesamiento, no el contenido;
- no procesa el guion real en esta fase;
- define estructura lógica privada fuera del repo sin crearla físicamente;
- no crea carpetas físicas ni define rutas concretas con datos confidenciales;
- prohíbe incluir guion real, título real, escenas, diálogos, personajes, localizaciones reales, nombres de personas, presupuesto real o material confidencial;
- prohíbe versionar respuestas reales o outputs reales;
- define entregables privados esperados sin generarlos;
- exige procesamiento privado y controlado;
- exige revisión humana obligatoria;
- exige que CID marque incertidumbres y nivel de confianza;
- exige que CID recomiende con mano izquierda, sugiera y no imponga;
- prohíbe entrenamiento de modelos con material real;
- prohíbe reutilización fuera del proyecto;
- no incluye SaaS abierto en esta fase;
- incluye criterios de éxito del piloto;
- incluye riesgos y mitigaciones.
