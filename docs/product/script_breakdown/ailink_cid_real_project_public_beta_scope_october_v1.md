# AILink CID - Real Project Public Beta Scope October

**Phase ID:** AILINK.CID.REAL.PROJECT.PUBLIC.BETA.SCOPE.OCTOBER.PHASE6.1
**Version:** 1.0
**Date:** 2026-06-15
**Status:** alcance documental para beta pública limitada de octubre

## 1. Objetivo de octubre

Definir el alcance acelerado para llegar a una beta pública limitada de CID/AilinkCinema basada en casos reales autorizados.

Objetivo temporal:

- Primeros de octubre: versión pública/enseñable.
- Finales de octubre: beta operativa completa.

La beta no debe intentar publicar todo CID. El producto público principal debe cubrir una línea concreta: desde guion real autorizado hasta planificación de producción, revisión humana y traspaso a postproducción.

## 2. Producto público mínimo

El producto público mínimo de octubre es una beta concreta para proyectos autorizados, no SaaS completo.

Debe permitir trabajar con un guion real autorizado como entrada, siempre con permiso explícito, confidencialidad y revisión humana obligatoria.

No debe incluir dentro del repo guiones reales, fragmentos de guion, datos reales de clientes, nombres reales de proyectos ni materiales confidenciales.

## 3. Flujo completo de beta

Flujo objetivo cerrado:

```text
guion real autorizado
→ cuestionarios por rol
→ análisis/desglose de producción
→ storyboard textual / shotlist preliminar
→ presupuesto preliminar revisable
→ plan de rodaje preliminar para ayudantía de dirección
→ checklist de rodaje
→ paquete de traspaso a postproducción
→ revisión humana
→ entrega beta al cliente
```

Cada salida debe quedar marcada como preliminar cuando corresponda. El sistema debe explicar incertidumbres y pedir datos adicionales si faltan respuestas.

## 4. Casos reales autorizados

La siguiente etapa debe orientarse a casos reales autorizados. Proyecto Demo Bruma queda como demo histórica interna.

El primer caso piloto real será un guion propio autorizado del fundador/usuario, tratado como primer cliente interno-real de CID.

Este piloto interno-real debe cumplir:

- caso real, no demo ficticia;
- autorización directa del titular;
- uso privado y controlado;
- revisión humana obligatoria;
- sin incluir el guion real, escenas, diálogos, nombres de personajes confidenciales ni datos reales del proyecto dentro del repo;
- sin fixtures reales;
- sin outputs reales versionados;
- sin entrenar modelos con ese material;
- sin reutilizar información fuera del proyecto.

El primer piloto interno-real debe validar el flujo completo:

```text
guion real autorizado
→ cuestionarios por rol
→ desglose de producción
→ storyboard textual / shotlist preliminar
→ presupuesto preliminar revisable
→ plan de rodaje preliminar para ayudantía de dirección
→ checklist de rodaje
→ paquete de traspaso a postproducción
→ revisión humana
→ entrega beta al cliente/fundador
```

Reglas:

- Casos reales autorizados.
- Nada de uso de guiones reales sin permiso explícito.
- Nada de guiones reales ni datos de clientes dentro del repo.
- Nada de fragmentos de guion, nombres reales de proyectos ni materiales confidenciales dentro del repo.

## 5. Consentimiento y confidencialidad

Antes de cualquier prueba con material real debe existir permiso explícito para el uso beta concreto.

El consentimiento debe aclarar:

- qué material se puede usar;
- para qué se usa;
- quién puede revisarlo;
- qué entregables se generan;
- que no se entrenan modelos con material del cliente sin permiso explícito;
- que no se reutiliza información entre clientes;
- que la memoria queda aislada por tenant/proyecto.

## 6. CID como sistema interactivo con vida propia

CID debe tener vida propia e interacción continua. No debe ser solo un generador de documentos.

CID debe comportarse como un sistema interactivo que:

- pregunta al cliente o equipo cuando faltan datos;
- marca incertidumbres;
- aconseja con tacto profesional y mano izquierda;
- usa tono diplomático, profesional, prudente y no impositivo;
- explica por qué recomienda algo;
- sugiere, no impone;
- adapta sus recomendaciones según respuestas autorizadas;
- no sustituye a productor, director, ayudante de dirección ni jefes de departamento;
- mantiene revisión humana obligatoria.

## 7. Memoria de proyecto y aprendizaje autorizado

Aprender significa memoria autorizada del proyecto/cliente, no entrenamiento de modelos ni reutilización entre clientes.

Reglas de memoria:

- CID debe aprender solo dentro del proyecto/cliente autorizado.
- No reutilizar información entre clientes.
- No entrenar modelos con material de clientes sin permiso explícito.
- Memoria aislada por tenant/proyecto.
- Aislamiento explícito por `organization_id`, `tenant_id`, `project_id` y `film_id`.

La memoria debe servir para recordar respuestas, decisiones, restricciones y preferencias autorizadas dentro del proyecto, no para alimentar conocimiento global entre clientes.

## 8. Cuestionarios por rol

Los cuestionarios por rol son parte esencial de la inteligencia del sistema. CID pregunta para entender la realidad del proyecto, no para cargar burocracia.

Roles obligatorios:

- productor / jefe de producción
- ayudante de dirección
- director
- dirección de fotografía
- sonido directo
- arte / vestuario / maquillaje
- postproducción

Los cuestionarios deben ayudar a CID a adaptar recomendaciones, marcar incertidumbres y explicar por qué sugiere una acción o una cautela.

## 9. Planificación visual, storyboard textual y shotlist

La beta debe generar planificación visual preliminar:

- storyboard textual;
- shotlist preliminar;
- notas de cobertura visual;
- preguntas pendientes para dirección y fotografía.

Storyboard textual y shotlist preliminar no sustituyen al storyboard artístico, al director ni a dirección de fotografía. Deben servir para preparar conversación y detectar huecos.

## 10. Presupuesto preliminar revisable

La beta debe producir presupuesto preliminar revisable.

Reglas:

- Presupuesto preliminar, no definitivo.
- Debe marcar supuestos e incertidumbres.
- Debe pedir datos cuando falten respuestas.
- Debe explicar por qué sugiere rangos o alertas.
- Debe requerir revisión humana antes de presentarse como base de decisión.

## 11. Plan de rodaje preliminar para ayudantía de dirección

La beta debe generar plan de rodaje preliminar para ayudantía de dirección.

Reglas:

- Plan de rodaje preliminar, no definitivo.
- Debe indicar dependencias, riesgos y datos faltantes.
- Debe ayudar a ayudantía de dirección, no sustituirla.
- Debe permitir revisión humana antes de cualquier decisión operativa.

## 12. Paquete de traspaso a postproducción

La beta debe incluir un Production-to-Post Handoff Package.

Debe incluir, a nivel preliminar:

- necesidades de postproducción detectadas;
- riesgos de continuidad o entrega;
- notas para montaje;
- posibles necesidades de sonido, VFX, color o conformado;
- preguntas pendientes para postproducción.

## 13. Revisión humana obligatoria

Toda entrega beta requiere revisión humana obligatoria.

CID puede preguntar, ordenar, explicar, aconsejar y marcar incertidumbres, pero no impone decisiones.

La revisión humana debe confirmar:

- que el material usado está autorizado;
- que los límites se entienden;
- que el presupuesto es preliminar;
- que el plan de rodaje es preliminar;
- que no se sustituyen roles profesionales.

## 14. Qué queda fuera de octubre

Queda fuera de octubre:

- SaaS completo;
- uso de guiones reales sin permiso explícito;
- meter guiones reales o datos de clientes dentro del repo;
- entrenamiento de modelos con material de clientes sin permiso explícito;
- reutilización de información entre clientes;
- presupuesto definitivo;
- plan de rodaje definitivo;
- sustitución de productor, director, ayudante de dirección o jefes de departamento;
- landing pública completa;
- CRM, Supabase, n8n o formularios reales;
- PDF/HTML/CSV reales como compromiso de producto.

## 15. Roadmap primeros de octubre / finales de octubre

Primeros de octubre: versión pública/enseñable.

- Alcance público explicado con prudencia.
- Flujo beta mostrado de extremo a extremo con material autorizado o entorno controlado.
- Cuestionarios por rol definidos.
- Entregables preliminares explicados.
- Límites legales, de privacidad y revisión humana claros.

Finales de octubre: beta operativa completa.

- Flujo completo ejecutable para caso autorizado.
- Memoria de proyecto autorizada y aislada.
- Preguntas adaptativas por rol.
- Storyboard textual / shotlist preliminar.
- Presupuesto preliminar revisable.
- Plan de rodaje preliminar para ayudantía de dirección.
- Checklist de rodaje.
- Production-to-Post Handoff Package.
- Revisión humana y entrega beta al cliente.

## 16. Riesgos y mitigaciones

- Riesgo: usar material real sin permiso. Mitigación: nada de guiones reales sin permiso explícito.
- Riesgo: filtrar datos de clientes en el repo. Mitigación: nada de guiones reales ni datos de clientes dentro del repo.
- Riesgo: confundir aprendizaje con entrenamiento de modelos. Mitigación: aprendizaje autorizado solo como memoria de proyecto/cliente.
- Riesgo: reutilizar información entre clientes. Mitigación: aislamiento por tenant/proyecto y prohibición explícita.
- Riesgo: prometer demasiado. Mitigación: beta pública limitada, no SaaS completo.
- Riesgo: imponer decisiones. Mitigación: CID aconseja con mano izquierda, sugiere y explica, pero no impone.
- Riesgo: sustituir roles profesionales. Mitigación: revisión humana obligatoria y límites claros por rol.

## 17. Criterios de aceptación de la beta

La beta de octubre se considera aceptable si:

- trabaja solo con casos reales autorizados;
- exige permiso explícito para guion real autorizado;
- no introduce guiones reales ni datos de clientes en el repo;
- ejecuta el flujo completo de beta;
- incluye cuestionarios por rol;
- CID pregunta cuando faltan datos;
- CID marca incertidumbres;
- CID aconseja con tacto profesional y mano izquierda;
- CID explica por qué recomienda algo;
- CID sugiere, no impone;
- mantiene memoria aislada por tenant/proyecto;
- no reutiliza información entre clientes;
- no entrena modelos con material de clientes sin permiso explícito;
- produce storyboard textual y shotlist preliminar;
- produce presupuesto preliminar revisable;
- produce plan de rodaje preliminar para ayudantía de dirección;
- produce Production-to-Post Handoff Package;
- mantiene revisión humana obligatoria;
- se presenta como beta pública limitada, no SaaS completo.
