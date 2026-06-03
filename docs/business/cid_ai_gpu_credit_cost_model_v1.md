# CID - Modelo interno de coste GPU y creditos IA

**Documento:** `docs/business/cid_ai_gpu_credit_cost_model_v1.md`
**Version:** 1.0
**Fecha:** 2026-06-03
**Tags:** `CID`, `business-model`, `gpu-cost`, `credits`, `ollama`, `comfyui`, `product-architecture`
**Basado en:** `docs/business/cid_credits_business_model_v1.md`, `docs/business/cid_credit_purchase_flow_v1.md`, `docs/ai/cid_ai_provider_model_v1.md`

---

## Indice

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Separacion conceptual](#2-separacion-conceptual)
3. [Coste Ollama / LLM local](#3-coste-ollama--llm-local)
4. [Coste ComfyUI / GPU CID](#4-coste-comfyui--gpu-cid)
5. [Coste GPU por hora / minuto](#5-coste-gpu-por-hora--minuto)
6. [Sistema de creditos CID](#6-sistema-de-creditos-cid)
7. [Relacion con Command Center](#7-relacion-con-command-center)
8. [BYOK y APIs externas](#8-byok-y-apis-externas)
9. [Fallos, reintentos y politica comercial](#9-fallos-reintentos-y-politica-comercial)
10. [Metricas futuras a capturar](#10-metricas-futuras-a-capturar)
11. [Riesgos](#11-riesgos)
12. [Recomendacion final](#12-recomendacion-final)

---

## 1. Resumen ejecutivo

CID necesita un **modelo interno de coste GPU y creditos IA** porque el coste real de operar IA no desaparece aunque no exista un coste API visible para el cliente.

### Por que CID necesita este modelo
- para proteger margen operativo
- para no vender por debajo del coste real
- para convertir infraestructura en creditos de proyecto comprensibles
- para separar el discurso comercial visible al cliente del calculo tecnico interno

### Por que no basta con decir "Ollama es gratis"
Aunque Ollama local no tenga coste API por token, sigue teniendo coste real:
- electricidad
- amortizacion de hardware
- mantenimiento
- ocupacion de GPU
- refrigeracion
- coste de oportunidad por bloqueo de capacidad

### Por que ComfyUI debe medirse por tiempo de render y complejidad
ComfyUI no es un coste fijo por llamada. El coste depende de:
- minutos reales de GPU
- complejidad del workflow
- resolucion
- numero de frames o imagenes
- pasos, modelos y controles activados
- reintentos, fallos y ocupacion de cola

### Como alimenta este modelo al CreditPool
El cliente no debe ver Ollama, ComfyUI, segundos GPU ni formulas internas. El cliente ve:
- creditos disponibles
- creditos estimados antes de ejecutar
- creditos consumidos despues
- alertas de consumo

Internamente, CID necesita mapear cada tarea IA a un coste tecnico y a un consumo abstracto de creditos.

---

## 2. Separacion conceptual

CID debe mantener separados estos planos:

### Licencias
- usuarios
- proyectos
- acceso

### Creditos
- consumo IA
- consumo GPU
- consumo API

### Servicios
- onboarding
- soporte
- personalizacion
- setup

### BYOK
- el coste API externo lo asume el cliente
- CID puede aplicar coste de orquestacion, workflow, parsing, seguridad o integracion si se decide comercialmente

### Regla funcional

```text
Licencias != Creditos != Servicios != Factura externa BYOK
```

---

## 3. Coste Ollama / LLM local

Ollama local no tiene coste API por token, pero si tiene coste operativo real.

### Metricas a considerar
- `tokens_input`
- `tokens_output`
- `tokens_totales`
- `tokens_por_segundo_estimados`
- `tiempo_gpu`
- `consumo_kWh`
- `coste_electrico`
- `amortizacion_por_hora_gpu`
- `coste_mantenimiento`
- `margen_CID`
- `coste_por_1M_input_tokens`
- `coste_por_1M_output_tokens`
- `coste_por_tarea`

### Formula base

```text
coste electrico por 1M tokens =
(1.000.000 / tokens_por_segundo / 3600) × consumo_kW × precio_kWh
```

### Formula ampliada

```text
coste total Ollama =
coste electrico
+ amortizacion hardware
+ mantenimiento
+ overhead servidor
+ margen CID
```

### Reglas de interpretacion
- input y output no deben costar lo mismo internamente
- output suele bloquear mas tiempo de inferencia y por tanto puede tener mayor coste real
- tareas largas o con contexto muy amplio deben medirse por tiempo y no solo por tokens nominales

### Recomendacion inicial interna
- input local: **2 EUR - 3 EUR por 1M input tokens** como referencia interna/B2B
- output local: **10 EUR - 15 EUR por 1M output tokens** como referencia interna/B2B

### Regla comercial
- no vender al cliente final el discurso de "tokens baratos"
- empaquetar el valor como servicio audiovisual especializado, no como simple commodity de inferencia

---

## 4. Coste ComfyUI / GPU CID

ComfyUI / GPU CID no tiene coste API externo, pero su coste real depende del tiempo de render y de la complejidad operativa.

### Metricas a considerar
- `segundos_gpu`
- `minutos_gpu`
- `tipo_workflow`
- `resolucion`
- `numero_frames_o_imagenes`
- `steps`
- `modelo_base`
- `controlnet_ipadapter_referencia_personaje`
- `video_vs_imagen`
- `restauracion_vs_generacion`
- `audio_doblaje_si_aplica`
- `vram_estimada`
- `reintentos`
- `fallos_cobrables`
- `fallos_no_cobrables`
- `almacenamiento_temporal`
- `prioridad_cola`

### Formula base

```text
coste ComfyUI =
minutos_GPU × coste_minuto_GPU × factor_workflow × factor_prioridad × factor_reintento
```

### Categorias sugeridas
- Imagen simple / storyboard frame
- Imagen con referencia / personaje / control
- Concept art premium
- Video corto
- Restauracion
- Doblaje / audio
- Procesos largos batch

### Regla de producto
El cliente no debe ver esta formula. Debe ver solo creditos estimados y una senal de intensidad de tarea.

---

## 5. Coste GPU por hora / minuto

CID necesita una referencia base para valorar internamente el uso de GPU.

### Componentes del coste horario
- coste electrico por hora
- amortizacion GPU por hora
- amortizacion del equipo por hora
- mantenimiento
- refrigeracion
- margen
- reserva por fallos / reintentos
- coste de oportunidad

### Formula base

```text
coste_hora_GPU =
(consumo_kW × precio_kWh)
+ amortizacion_hardware_hora
+ mantenimiento_hora
+ overhead_hora
+ margen
```

```text
coste_minuto_GPU = coste_hora_GPU / 60
```

### Rangos internos sugeridos

No fijar todavia precios definitivos, pero trabajar internamente con:
- **coste minimo tecnico**: umbral por debajo del cual CID perderia dinero
- **coste recomendado con margen**: objetivo normal de operacion saludable
- **coste premium / prioritario**: para cola prioritaria o cargas especialmente intensivas

### Regla documental
Estos rangos deben calibrarse con datos reales de carga, no solo con intuicion comercial.

---

## 6. Sistema de creditos CID

### Unidad abstracta
**1 credito CID no debe equivaler publicamente** a:
- 1 token
- 1 segundo GPU
- 1 minuto GPU
- 1 llamada API

Internamente si puede mapearse a coste estimado.

### Regla de producto
El cliente ve creditos consumidos por accion, no infraestructura tecnica subyacente.

### Ejemplos conceptuales
- analisis de guion basico
- informe de lectura largo
- generar 10 frames storyboard
- generar concept art premium
- restaurar clip corto
- preparar dossier con IA
- tarea hibrida: analisis + storyboard

### Regla economica
No poner precios definitivos si no hay datos reales, pero si dejar:
- formulas
- equivalencias internas tentativas
- placeholders de consumo por accion

---

## 7. Relacion con Command Center

### Que vera el cliente
- creditos disponibles
- creditos estimados antes de ejecutar
- creditos consumidos despues
- aviso si la tarea es intensiva
- aviso si no hay creditos suficientes
- consumo separado por rama:
  - Produccion & Financiacion
  - Creativo & Rodaje
  - Postproduccion, Entrega & Comercializacion

### Que NO vera el cliente
- GPU
- Ollama
- ComfyUI
- tokens exactos salvo modo avanzado futuro
- modelos tecnicos
- logs internos
- coste electrico
- coste de amortizacion

### Regla UX
La UI principal debe traducir complejidad tecnica a riesgo, coste y disponibilidad comprensibles.

---

## 8. BYOK y APIs externas

### Regla base
Si el cliente usa su propia API key:
- el coste API externo lo paga el cliente
- CID puede cobrar creditos por:
  - orquestacion
  - almacenamiento
  - parsing
  - seguridad
  - RAG
  - workflow
  - integracion con proyecto

### Regla UX
La UI debe distinguir siempre:
- coste externo del cliente
- creditos CID por orquestacion

### Regla comercial
Nunca mezclar ambos en un unico mensaje confuso.

---

## 9. Fallos, reintentos y politica comercial

### Reglas propuestas
- fallo tecnico interno no deberia consumir credito final o deberia reembolsarse automaticamente
- reintento por cambio creativo si puede consumir creditos
- previsualizacion barata vs render final
- prioridad de cola puede consumir mas creditos
- batch nocturno puede tener menor coste futuro
- acciones canceladas antes de ejecucion no consumen
- acciones canceladas durante ejecucion pueden tener coste parcial

### Regla de negocio
La politica de reintentos debe ser transparente internamente antes de convertirse en UI o pricing.

---

## 10. Metricas futuras a capturar

Sin implementar todavia, CID deberia capturar en el futuro:
- `job_id`
- `project_id`
- `organization_id`
- `branch_id`
- `ai_task_type`
- `provider_mode_internal`
- `visible_mode`
- `tokens_input`
- `tokens_output`
- `gpu_seconds`
- `workflow_type`
- `estimated_credits`
- `final_credits`
- `status`
- `retry_count`
- `error_type`
- `created_at`
- `completed_at`

### Regla funcional
Estas metricas deben alimentar control de margen, auditoria, alertas y ajuste fino del modelo de creditos.

---

## 11. Riesgos

### Riesgos comerciales y tecnicos
- vender por debajo del coste real
- subestimar amortizacion RTX 5090
- no diferenciar Ollama de ComfyUI internamente
- no medir segundos GPU reales
- que el cliente piense que "local" es gratis
- que BYOK parezca gratis para CID
- falta de politica de reintentos
- costes ocultos de almacenamiento y cola
- variabilidad por workflow y resolucion
- saturacion GPU si hay varios clientes

### Riesgo estructural
Sin observabilidad minima del coste, el sistema de creditos puede parecer coherente externamente y ser inviable internamente.

---

## 12. Recomendacion final

### Veredicto
**GO** para pasar despues a:

**`CID.FRONTEND.COMMAND.CENTER.AI.STATUS.PLACEHOLDERS.1`**

### Condicion
Los placeholders frontend deben incluir:
- creditos estimados
- consumo aproximado
- aviso "tarea intensiva"
- estado de disponibilidad
- sin mostrar calculo tecnico interno

### Regla final
El frontend puede representar coste y riesgo, pero nunca debe exponer el modelo interno de calculo GPU/token como si fuera parte de la experiencia principal del cliente.

---

## Historial de revisiones

| Fecha | Version | Cambios |
|---|---|---|
| 2026-06-03 | 1.0 | Creacion inicial del modelo interno de coste GPU y creditos IA para Ollama, ComfyUI y modos de consumo CID. |
