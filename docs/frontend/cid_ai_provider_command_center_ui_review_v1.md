# CID - Revision UI de proveedor IA en Command Center

**Documento:** `docs/frontend/cid_ai_provider_command_center_ui_review_v1.md`
**Version:** 1.0
**Fecha:** 2026-06-03
**Tags:** `CID`, `frontend`, `ui-review`, `command-center`, `ai-provider`, `ux`
**Basado en:** `docs/ai/cid_ai_provider_command_center_integration_v1.md`

---

## Indice

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Bloques UI recomendados para el Command Center](#2-bloques-ui-recomendados-para-el-command-center)
3. [Visibilidad por rol](#3-visibilidad-por-rol)
4. [Configuracion avanzada futura](#4-configuracion-avanzada-futura)
5. [Reglas de copywriting UI](#5-reglas-de-copywriting-ui)
6. [Riesgos UX / producto](#6-riesgos-ux--producto)
7. [Recomendacion para futura implementacion frontend](#7-recomendacion-para-futura-implementacion-frontend)
8. [Criterios de aceptacion para la futura fase frontend](#8-criterios-de-aceptacion-para-la-futura-fase-frontend)
9. [Decision final](#9-decision-final)

---

## 1. Resumen ejecutivo

La capa IA dentro del CID Project Command Center debe resolver un problema simple: **hacer comprensible la capacidad IA del proyecto sin exponer arquitectura tecnica innecesaria**.

El cliente no necesita saber si CID usa Ollama, APIs externas, ComfyUI o GPU propia. Lo que necesita entender es:
- si la IA del proyecto esta disponible
- que resultados puede obtener
- si el coste esta bajo control
- si el modo de privacidad es adecuado
- si el servicio es fiable o necesita atencion

Por ello, la UI debe presentar la IA como **capacidad de producto** y no como **proveedor tecnico**. El lenguaje visible debe hablar de motores, modos, resultados, creditos, privacidad y disponibilidad; no de modelos, endpoints, puertos o infraestructura interna.

---

## 2. Bloques UI recomendados para el Command Center

### A) AI Engine Status Card

#### Funcion
Bloque principal que resume el estado del motor IA del proyecto.

#### Estados visibles
- Activo
- Pendiente de configuracion
- Requiere atencion
- Desactivado
- Servicio no disponible

#### Texto recomendado ES
- **Activo**: La IA del proyecto esta lista para operar.
- **Pendiente de configuracion**: Falta completar la configuracion base de IA.
- **Requiere atencion**: La IA del proyecto necesita revision o decision.
- **Desactivado**: La IA del proyecto no esta activa en este momento.
- **Servicio no disponible**: La IA del proyecto no esta disponible temporalmente.

#### Texto recomendado EN
- **Active**: Project AI is ready to operate.
- **Pending setup**: Core AI configuration is still incomplete.
- **Needs attention**: Project AI requires review or a decision.
- **Disabled**: Project AI is not active at the moment.
- **Service unavailable**: Project AI is temporarily unavailable.

#### Que debe ver el productor
- estado general
- impacto potencial en coste o continuidad
- si puede seguir operando o debe tomar una decision

#### Que debe ver el director
- si las acciones creativas estan disponibles
- si existe riesgo para materiales sensibles

#### Que debe ver el admin tecnico
- estado funcional general
- acceso posterior a la capa avanzada, nunca en la tarjeta principal

---

### B) AI Mode Indicator

#### Modos visibles al usuario no tecnico
- CID Local
- CID Optimizado
- Cliente API configurada
- Modo hibrido
- Servicio no disponible

#### Significado funcional para usuario no tecnico
- **CID Local**: La IA opera en entorno controlado por CID con foco en privacidad y estabilidad.
- **CID Optimizado**: CID gestiona la mejor combinacion de motores para el proyecto.
- **Cliente API configurada**: El proyecto usa una clave o cuenta externa aportada por el cliente.
- **Modo hibrido**: El proyecto combina varios modos IA segun tarea o disponibilidad.
- **Servicio no disponible**: La capacidad IA no esta operativa temporalmente.

#### Que NO se debe decir en la UI principal
- Ollama
- OpenAI
- Anthropic
- ComfyUI
- GPU
- endpoints
- nombres tecnicos de modelos
- puertos
- routing interno

---

### C) Credit & Cost Visibility Card

#### Objetivo
Hacer visible el estado economico del uso IA sin mezclarlo con licencias ni con facturas externas del cliente.

#### Elementos visibles
- creditos incluidos
- creditos usados
- creditos restantes
- alerta de consumo
- futura accion **Anadir creditos**

#### Regla clave
La tarjeta debe diferenciar siempre:
- **creditos CID**
- **coste externo del cliente** en modo BYOK

#### Mensajes de riesgo recomendados
- "El uso IA del proyecto consume creditos CID."
- "La clave del cliente puede implicar coste externo fuera de CID."
- "Los creditos CID no sustituyen la factura externa del cliente."

---

### D) Privacy Mode Indicator

#### Modos visibles
- Estandar
- Reforzada
- Local / privada
- Clave del cliente configurada (solo para roles autorizados)

#### Riesgo a comunicar
El mayor riesgo UX es la **falsa sensacion de privacidad**: una UI demasiado optimista puede hacer pensar que todo esta aislado cuando no lo esta.

#### Texto visible recomendado ES
- **Estandar**: Flujo IA operativo con configuracion normal del proyecto.
- **Reforzada**: El proyecto prioriza un tratamiento mas controlado del material.
- **Local / privada**: El procesamiento IA se orienta a entorno local o privado.
- **Clave del cliente configurada**: El proyecto usa configuracion externa aportada por el cliente.

#### Texto visible recomendado EN
- **Standard**: Project AI runs with the normal operating setup.
- **Enhanced**: The project prioritises a more controlled handling of material.
- **Local / private**: AI processing is oriented to a local or private environment.
- **Customer key configured**: The project uses an external customer-provided setup.

---

### E) Reliability / Availability Card

#### Estados visibles
- Disponible
- En cola
- Degradado
- Requiere configuracion
- Servicio no disponible

#### Regla de explicacion
La UI puede explicar fallback o degradacion solo en terminos funcionales:
- disponible para operar
- con espera
- con rendimiento reducido
- necesita configuracion
- no disponible

#### Que NO debe explicar
- cambio entre proveedores concretos
- balanceo interno
- colas tecnicas de infraestructura
- fallos internos con detalle de stack

---

### F) Result-Oriented Action Panel

#### Acciones visibles por rama
- Analizar guion
- Generar storyboard
- Preparar dossier
- Evaluar financiacion
- Generar concept art
- Preparar delivery
- Revisar materiales
- Preparar venta / distribucion

#### Regla UX
Las acciones deben expresar **resultado** y no tecnologia. Por ejemplo:
- correcto: "Generar storyboard"
- incorrecto: "Lanzar pipeline ComfyUI"

---

## 3. Visibilidad por rol

| Rol | Que puede ver | Que puede accionar | Que no debe ver | Configuracion avanzada |
|---|---|---|---|---|
| Productor / Productor Ejecutivo | Estado IA, coste, creditos, resultados, alertas | Generar, Analizar, Revisar, Preparar, futura accion de configurar si procede | Claves completas, logs tecnicos, proveedor tecnico detallado | Si, segun permiso de gobierno del proyecto |
| Director | Acciones creativas, resultados esperados, privacidad de materiales | Generar storyboard, concept art, revisar salidas creativas | Coste externo detallado, claves, logs tecnicos | No por defecto |
| Guionista | Estado y acciones ligadas a analisis de guion si aplica | Analizar / Revisar segun flujo | Coste, proveedor, claves, configuracion sensible | No |
| Post Supervisor | Estado IA para post/delivery, disponibilidad operativa | Preparar delivery, revisar materiales, procesos de post compatibles | Claves, proveedor tecnico detallado, logs internos | No por defecto |
| Distribucion / Ventas | Resultado disponible para venta/distribucion si aplica | Preparar venta / distribucion | Claves, proveedor, detalles tecnicos | No |
| Admin organizacion | Estado global, riesgos, consumo y alertas de alto nivel | Futura configuracion segun politica | Secretos completos y logs tecnicos sin autorizacion extra | Si, si el modelo organizacional lo permite |
| Admin tecnico / Enterprise | Estado, coste, privacidad, modo avanzado, referencias parciales de claves | Configuracion avanzada futura | Nunca claves completas en claro | Si |
| Usuario invitado | Solo resultado o acceso muy limitado | Ninguna accion sensible | Coste, proveedor, claves, configuracion | No |

---

## 4. Configuracion avanzada futura

Esta capa debe existir solo como **placeholder documental** en futuras iteraciones.

### Elementos posibles
- proveedor tecnico
- BYOK
- ultimos 4 caracteres de clave
- rotar clave
- borrar clave
- test conexion
- politica de privacidad
- consumo asociado
- logs tecnicos restringidos

### Regla de alcance
Nada de esto se implementa todavia en esta fase. Solo se documenta para que la futura UI no mezcle experiencia principal con configuracion sensible.

---

## 5. Reglas de copywriting UI

### Lenguaje permitido
- orientado a resultado
- orientado a coste
- orientado a privacidad
- orientado a disponibilidad
- orientado a accion clara

### Lenguaje a evitar
- demasiado tecnico
- nombres de herramientas
- falsas promesas
- jerga de infraestructura
- la palabra "gratis" si consume GPU, creditos o API

### Principio de redaccion
La IA debe presentarse como un **servicio funcional del proyecto**, no como una coleccion de integraciones tecnicas.

---

## 6. Riesgos UX / producto

Riesgos principales:
- confusion entre creditos CID y factura externa BYOK
- privacidad mal comunicada
- exceso de informacion tecnica
- estados ambiguos
- errores de proveedor expuestos al cliente
- acciones visibles sin disponibilidad real
- frustracion si "Generar" aparece aunque no haya creditos o servicio

### Regla de mitigacion
Cada bloque UI debe poder responder a una pregunta simple y evitar sobreexplicar infraestructura.

---

## 7. Recomendacion para futura implementacion frontend

### Proxima fase propuesta
**`CID.FRONTEND.COMMAND.CENTER.AI.STATUS.PLACEHOLDERS.1`**

### Alcance futuro sugerido
- anadir tarjetas placeholder al Command Center
- usar datos mock o locales
- sin backend
- sin selector real
- sin claves
- sin conexion real
- i18n ES/EN obligatorio
- acceso por rol simulado solo si ya existe patron en frontend

---

## 8. Criterios de aceptacion para la futura fase frontend

Checklist minimo:
- no se muestran proveedores tecnicos en UI principal
- estados comprensibles
- creditos separados de licencias
- privacidad clara
- roles respetados
- sin claves en frontend
- sin llamadas reales a proveedor
- i18n ES/EN
- responsive
- sin tocar backend

---

## 9. Decision final

### Recomendacion
**GO** para pasar a placeholder frontend.

### Motivo
La capa conceptual ya permite traducir la complejidad del provider model a bloques UI comprensibles, sin necesidad de exponer tecnologia ni de implementar todavia backend, selector real o gestion de claves.

---

## Historial de revisiones

| Fecha | Version | Cambios |
|---|---|---|
| 2026-06-03 | 1.0 | Revision UI inicial para traducir el modelo de proveedor IA del Command Center a bloques frontend comprensibles y orientados a producto. |
