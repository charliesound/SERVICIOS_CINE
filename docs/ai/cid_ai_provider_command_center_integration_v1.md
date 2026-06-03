# CID - Integracion del proveedor IA en Command Center

**Documento:** `docs/ai/cid_ai_provider_command_center_integration_v1.md`
**Version:** 1.0
**Fecha:** 2026-06-03
**Tags:** `CID`, `ai`, `command-center`, `provider-integration`, `product-architecture`, `ux-model`
**Basado en:** `docs/ai/cid_ai_provider_model_v1.md`, `docs/business/cid_credits_business_model_v1.md`, `docs/business/cid_credit_purchase_flow_v1.md`, `docs/product/cid_project_command_center_branches_v1.md`, `docs/product/cid_project_command_center_data_model_v1.md`, `docs/frontend/cid_command_center_frontend_readiness_audit_v1.md`

---

## Indice

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Objetivo de la integracion](#2-objetivo-de-la-integracion)
3. [Que debe mostrar el Command Center](#3-que-debe-mostrar-el-command-center)
4. [Estados visibles](#4-estados-visibles)
5. [Relacion con CreditPool](#5-relacion-con-creditpool)
6. [Alertas en Command Center](#6-alertas-en-command-center)
7. [Visibilidad por rol](#7-visibilidad-por-rol)
8. [Que deberia ver cada rama](#8-que-deberia-ver-cada-rama)
9. [Que NO mostrar a todos](#9-que-no-mostrar-a-todos)
10. [Reglas de seguridad visual](#10-reglas-de-seguridad-visual)
11. [Placeholder frontend recomendado](#11-placeholder-frontend-recomendado)
12. [Relacion interna con proveedores](#12-relacion-interna-con-proveedores)
13. [Que NO implementar todavia](#13-que-no-implementar-todavia)
14. [Riesgos](#14-riesgos)
15. [Proxima fase](#15-proxima-fase)

---

## 1. Resumen ejecutivo

Este documento define **como debe aparecer la IA dentro del CID Project Command Center** desde una perspectiva de producto y experiencia de usuario.

El principio fundamental es:

> El cliente no necesita saber que herramientas tecnicas usa CID. El cliente quiere resultados, control de coste, privacidad y fiabilidad.

### Decision de arquitectura de referencia
- **Motor IA por defecto:** Ollama / modelos locales gestionados por CID.
- **APIs externas opcionales:** OpenAI API, Anthropic API y otros proveedores compatibles futuros.
- **BYOK opcional:** el cliente puede aportar su propia API key si quiere usar su cuenta externa.
- **ComfyUI / GPU CID:** se usa para generacion visual, storyboard, concept art, video, restauracion, doblaje y otros procesos audiovisuales.
- **Hybrid Mode:** CID puede combinar Ollama, APIs externas y ComfyUI segun tarea, coste, privacidad y disponibilidad.

Por tanto, la experiencia principal del Command Center debe hablar en terminos de:
- estado del motor IA del proyecto
- resultados esperados
- coste y creditos
- privacidad
- fiabilidad
- acciones operativas

Y no en terminos de:
- proveedor tecnico especifico
- endpoint
- modelo concreto
- GPU
- routing interno
- claves tecnicas

La complejidad tecnica solo debe aflorar en una capa avanzada de configuracion para roles autorizados.

---

## 2. Objetivo de la integracion

El objetivo de la integracion no es mostrar al cliente la arquitectura interna de IA, sino ofrecer una **vista funcional y comprensible** dentro del proyecto.

La integracion en Command Center debe permitir responder visualmente a estas preguntas:
- La IA del proyecto esta lista o requiere atencion?
- Que resultados puede producir la IA dentro de este proyecto?
- Hay riesgo de coste o de agotamiento de creditos?
- El modo de privacidad es suficiente para este material?
- El servicio esta disponible, degradado o en cola?

La pantalla no debe convertirse en un panel tecnico de infraestructura.

---

## 3. Que debe mostrar el Command Center

### 3.1 Motor IA del proyecto
El Command Center debe mostrar un bloque visible de **Motor IA del proyecto** con un estado sintetico y legible.

Debe poder indicar:
- Activo
- Pendiente de configuracion
- Requiere atencion
- Desactivado
- Modo privado / reforzado si aplica

### 3.1.1 Modo visible simplificado
La experiencia principal no debe mostrar el nombre tecnico del proveedor real salvo en configuracion avanzada para roles autorizados.

El modo visible simplificado debe expresarse como:
- **CID Local**
- **CID Optimizado**
- **Cliente API configurada**
- **Modo hibrido**
- **Servicio no disponible**

### 3.2 Resultado esperado
La UI debe hablar de capacidades funcionales, no de herramientas internas.

Debe poder resumir resultados como:
- analisis de guion
- storyboard
- concept art
- dossier
- financiacion
- traduccion / doblaje
- postproduccion
- delivery

### 3.3 Coste visible
La vista principal debe mostrar el estado economico del uso IA de forma comprensible:
- creditos disponibles
- creditos usados
- creditos restantes
- alerta de consumo
- opcion futura **Anadir creditos**

### 3.4 Privacidad visible
La UI principal debe mostrar el nivel de privacidad de forma semantica:
- estandar
- reforzada
- local / privado

La indicacion de BYOK solo debe aparecer para roles autorizados y en lenguaje orientado al cliente, por ejemplo:
- **clave del cliente configurada**

No debe mostrarse el nombre del proveedor, endpoint o secreto asociado en la vista principal.

### 3.5 Fiabilidad visible
La UI debe expresar salud operativa sin entrar en detalles de proveedor:
- disponible
- en cola
- degradado
- requiere configuracion
- servicio no disponible

### 3.6 Acciones visibles
Las acciones funcionales del bloque IA deben expresarse en lenguaje de resultado:
- Generar
- Analizar
- Revisar
- Preparar
- Configurar IA (solo para roles autorizados)

---

## 4. Estados visibles

### Estados principales del bloque IA del proyecto

| Estado visible | Significado funcional |
|---|---|
| **Configurado** | El proyecto tiene un modo IA utilizable y puede ejecutar operaciones compatibles. |
| **Pendiente de configuracion** | Falta definir el modo IA o activar una capacidad necesaria. |
| **Requiere atencion** | Hay una incidencia de coste, privacidad, disponibilidad o configuracion que requiere decision. |
| **Modo hibrido** | El proyecto combina varios modos IA segun operacion, modulo o sensibilidad del dato. |
| **Desactivado** | La IA del proyecto esta deshabilitada o no debe usarse en este contexto. |

### Regla de producto
Estos estados deben ser visibles y comprensibles para perfiles no tecnicos.

---

## 5. Relacion con CreditPool

La integracion del proveedor IA debe quedar conectada de forma clara con el modelo de creditos.

### Reglas visibles en Command Center
- **CID Managed AI** consume creditos CID
- **ComfyUI / GPU CID** consume creditos CID
- **BYOK** puede no consumir creditos GPU CID
- el cargo de orquestacion BYOK queda pendiente de definicion comercial

### Regla UX
La pantalla no debe confundir:
- creditos CID
- coste externo del cliente en modo BYOK
- coste de servicios o soporte enterprise

---

## 6. Alertas en Command Center

El bloque IA del proyecto debe poder mostrar alertas funcionales como:
- proveedor no configurado
- clave pendiente
- creditos bajos
- uso BYOK activo
- proveedor local no disponible
- GPU CID en cola
- privacidad reforzada activa

### Regla UX
Las alertas deben presentarse como riesgo o accion pendiente, no como detalle tecnico del stack.

---

## 7. Visibilidad por rol

### Productor Propietario
Debe ver:
- coste
- estado
- creditos
- resultados esperados
- alertas operativas
- accion futura de configuracion si el producto la habilita

### Productor Ejecutivo
Debe ver:
- estado del motor IA
- creditos y alertas de consumo
- riesgo economico y disponibilidad general

### Admin de organizacion
Debe ver:
- estado global de configuracion
- señales de riesgo
- posibilidad futura de acceso a configuracion avanzada segun politica de organizacion

### Admin tecnico / Enterprise
Debe ver, en una capa avanzada y autorizada:
- proveedor efectivo
- referencia parcial de claves
- modo avanzado
- estado de configuracion y disponibilidad

### Jefe de Produccion
Debe ver:
- impacto en coste, creditos y riesgo de produccion
- disponibilidad operativa, cola o degradacion

### Director
Debe ver:
- acciones creativas
- resultados esperados
- nivel de privacidad de materiales

### Post Supervisor
Debe ver:
- estado de IA aplicada a post / delivery
- disponibilidad operativa de procesos visuales o de restauracion / doblaje si aplica

### Resto de roles
Deben ver solo:
- resultado operativo
- o ningun detalle, si no tienen relacion con el uso IA del proyecto

### Regla funcional
La vista principal debe priorizar lenguaje funcional. Los detalles de proveedor, clave o modo avanzado no deben ser visibles a todos.

---

## 8. Que deberia ver cada rama

### Rama 1 - Produccion & Financiacion
Debe ver principalmente:
- coste
- creditos
- riesgo economico
- alertas de consumo o saturacion operativa

### Rama 2 - Creativo & Rodaje
Debe ver principalmente:
- proveedor creativo activo expresado como motor o modo funcional, no como stack tecnico
- privacidad de guion y materiales
- disponibilidad para analisis, storyboard, concept art y desarrollo creativo

### Rama 3 - Postproduccion, Entrega & Comercializacion
Debe ver principalmente:
- proveedor o modo visual/post expresado como capacidad operativa
- disponibilidad de GPU o cola si afecta a delivery o post
- soporte IA para delivery, restauracion, doblaje o materiales finales

### Regla de producto
Las ramas no son silos. La informacion IA debe poder aparecer en varias ramas con distintos niveles de detalle segun impacto funcional.

---

## 9. Que NO mostrar a todos

No deben mostrarse a todos los usuarios:
- claves secretas
- costes detallados externos
- configuracion sensible
- logs tecnicos

### Regla
La experiencia principal del Command Center debe ocultar la capa tecnica y dejarla reservada a configuracion avanzada autorizada.

---

## 10. Reglas de seguridad visual

### Reglas obligatorias
- nunca mostrar API key completa
- solo mostrar los ultimos 4 caracteres si existe referencia visual
- no mostrar secretos en errores
- no exponer logs sensibles
- no mostrar proveedor tecnico a usuarios no autorizados
- no confundir creditos CID con costes externos BYOK

### Regla de diseño
La UI debe mostrar seguridad y estado, no secretos ni metadatos internos peligrosos.

---

## 11. Placeholder frontend recomendado

El bloque recomendado en futuras iteraciones frontend es:

### Bloque principal
- **Proveedor IA del proyecto**

### Elementos visibles
- badge de modo IA
- resumen de creditos
- aviso BYOK o local si aplica
- accion futura **Configurar proveedor IA**

### Regla UX
Incluso si internamente existe un provider model complejo, la vista principal debe seguir siendo compacta, ejecutiva y comprensible.

---

## 12. Relacion interna con proveedores

Internamente, CID puede operar con:
- Ollama como motor por defecto
- OpenAI API opcional
- Anthropic API opcional
- BYOK opcional
- ComfyUI / GPU CID
- GPU cliente en Enterprise
- Hybrid Mode

### Regla de experiencia principal
Esta capa interna debe quedar **oculta en la experiencia principal** y solo mostrarse en configuracion avanzada para perfiles autorizados.

---

## 13. Que NO implementar todavia

No implementar todavia:
- selector real
- guardado de claves
- backend
- UI funcional
- routing real
- test conexion real

### Regla de alcance
Este documento no disena endpoints, contratos tecnicos ni componentes implementados. Solo define arquitectura funcional para futura UI.

---

## 14. Riesgos

### Riesgos principales
- confusion entre creditos CID y BYOK
- exposicion de secretos
- costes externos inesperados
- proveedores no disponibles
- falsa sensacion de privacidad
- fallback mal entendido

### Riesgos adicionales
- sobrecarga cognitiva si la UI muestra demasiado detalle tecnico
- mala interpretacion del estado IA por roles no tecnicos
- mezcla de responsabilidad economica y responsabilidad creativa sin separacion clara

---

## 15. Proxima fase

**`CID.AI.PROVIDER.COMMAND.CENTER.INTEGRATION.REVIEW.1`**

La siguiente fase debe revisar:
- si el lenguaje visible sigue siendo orientado a resultado y no a stack tecnico
- si la relacion con creditos y BYOK se entiende sin ambiguedad
- si la visibilidad por rol es coherente con el modelo de acceso
- si la futura integracion frontend puede representarlo con placeholders seguros

---

## Historial de revisiones

| Fecha | Version | Cambios |
|---|---|---|
| 2026-06-03 | 1.0 | Creacion inicial del modelo de integracion del proveedor IA dentro del CID Project Command Center, orientado a experiencia funcional y no tecnica. |
