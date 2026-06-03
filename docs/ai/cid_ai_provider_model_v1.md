# CID - Modelo funcional de proveedores IA

**Documento:** `docs/ai/cid_ai_provider_model_v1.md`
**Version:** 1.0
**Fecha:** 2026-06-03
**Tags:** `CID`, `ai`, `provider-model`, `byok`, `ollama`, `comfyui`, `product-architecture`
**Basado en:** `docs/business/cid_credits_business_model_v1.md`, `docs/business/cid_credit_purchase_flow_v1.md`, `docs/product/cid_project_access_model_v1.md`

---

## Indice

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Principios del modelo](#2-principios-del-modelo)
3. [Tabla comparativa de modos](#3-tabla-comparativa-de-modos)
4. [Cuando usar cada modo](#4-cuando-usar-cada-modo)
5. [Relacion con creditos IA](#5-relacion-con-creditos-ia)
6. [Relacion con compra de creditos](#6-relacion-con-compra-de-creditos)
7. [Relacion con planes Starter / Pro / Studio / Premium / Enterprise](#7-relacion-con-planes-starter--pro--studio--premium--enterprise)
8. [Seguridad de claves secretas](#8-seguridad-de-claves-secretas)
9. [Gestion de API keys](#9-gestion-de-api-keys)
10. [Reglas BYOK](#10-reglas-byok)
11. [Privacidad y confidencialidad de guiones y materiales](#11-privacidad-y-confidencialidad-de-guiones-y-materiales)
12. [Auditoria de uso IA](#12-auditoria-de-uso-ia)
13. [Fallbacks entre proveedores](#13-fallbacks-entre-proveedores)
14. [Riesgos](#14-riesgos)
15. [Que NO implementar todavia](#15-que-no-implementar-todavia)
16. [Proxima fase](#16-proxima-fase)

---

## 1. Resumen ejecutivo

Este documento define el **modelo funcional para elegir proveedor IA dentro de CID**. El objetivo es permitir que un proyecto opere con distintos modos de suministro de IA sin mezclar decisiones de acceso, decisiones de facturacion y decisiones de infraestructura.

CID debe poder trabajar, a nivel conceptual, con seis modos:
- **CID Managed AI**
- **Customer API Key / BYOK**
- **Local Ollama**
- **ComfyUI / GPU CID**
- **ComfyUI / GPU cliente**
- **Hybrid Mode**

El modelo se mantiene deliberadamente como **arquitectura funcional y de producto**. No afirma que la seleccion real de proveedor, el enrutado real, el guardado real de claves o el switching automatico ya existan implementados.

La idea base es:

```text
Proyecto CID
  -> puede definir una estrategia de proveedor IA
  -> puede consumir creditos CID o consumo externo del cliente segun modo
  -> puede priorizar privacidad, coste, control o rendimiento
```

---

## 2. Principios del modelo

### P1 - El proveedor es una decision de proyecto, no de marketing
La eleccion del proveedor debe responder a necesidades reales de coste, privacidad, latencia, gobernanza y capacidad.

### P2 - El proveedor no redefine permisos
Elegir proveedor IA no cambia por si mismo roles, visibilidad ni acceso funcional dentro del proyecto.

### P3 - Creditos y proveedor no son lo mismo
Un proveedor puede consumir creditos CID, consumo externo del cliente o una mezcla de ambos. El proveedor tecnico y el modelo economico deben documentarse por separado.

### P4 - BYOK no significa ausencia de reglas CID
Aunque el cliente aporte una API key, CID puede seguir aplicando reglas de orquestacion, auditoria, control funcional o cargos de servicio si asi se decide comercialmente.

### P5 - Privacidad y trazabilidad deben poder convivir
Los modos con mayor privacidad local no deben impedir trazabilidad funcional minima. Los modos con mayor trazabilidad no deben exponer secretos ni materiales sensibles.

### P6 - Hybrid es un modo de producto valido
Un mismo proyecto puede usar varios proveedores segun tarea: LLM externo para analisis, Ollama local para privacidad, ComfyUI CID para generacion visual y GPU cliente para cargas enterprise.

### P7 - Seguridad primero
Las claves y secretos nunca deben residir en frontend ni quedar visibles en navegador o logs.

---

## 3. Tabla comparativa de modos

| Modo | Quien opera la IA | Donde corre | Quien asume coste directo | Consume creditos CID | Privacidad | Complejidad operativa |
|---|---|---|---|---|---|---|
| CID Managed AI | CID | Infraestructura gestionada por CID | CID (repercutido al cliente via creditos) | Si | Media | Baja para cliente |
| Customer API Key / BYOK | Cliente | Proveedor externo del cliente | Cliente | Pendiente de definicion comercial | Media | Media |
| Local Ollama | Cliente o instalacion privada | Infra local/privada | Cliente | No necesariamente | Alta | Media-alta |
| ComfyUI / GPU CID | CID | GPU e infraestructura CID | CID (repercutido al cliente via creditos) | Si | Media | Baja para cliente |
| ComfyUI / GPU cliente | Cliente / enterprise privado | GPU del cliente | Cliente | No necesariamente | Alta | Alta |
| Hybrid Mode | Mixto | Mixto | Mixto | Mixto | Variable | Alta |

---

## 4. Cuando usar cada modo

### 4.1 CID Managed AI
Usar cuando:
- el cliente quiere simplicidad operativa
- el proyecto necesita entrar rapido sin gestionar claves ni infraestructura
- CID quiere ofrecer experiencia controlada con consumo via creditos CID

### 4.2 Customer API Key / BYOK
Usar cuando:
- el cliente ya tiene contrato o cuenta propia con un proveedor IA
- el cliente quiere asumir directamente el coste API externo
- el cliente necesita trazabilidad separada en su propia cuenta

### 4.3 Local Ollama
Usar cuando:
- la privacidad del material sea prioritaria
- el cliente disponga de servidor privado o instalacion controlada
- se quiera minimizar exposicion de guiones o materiales a servicios externos

### 4.4 ComfyUI / GPU CID
Usar cuando:
- el proyecto necesita storyboard, concept art, video, restauracion o doblaje sin operar infraestructura propia
- CID quiere proteger margen GPU con creditos y colas controladas
- el cliente necesita una experiencia visual gestionada por CID

### 4.5 ComfyUI / GPU cliente
Usar cuando:
- el cliente enterprise tiene infraestructura propia
- el cliente necesita aislamiento fuerte o cumplimiento especifico
- CID solo aporta configuracion, soporte o mantenimiento selectivo

### 4.6 Hybrid Mode
Usar cuando:
- el proyecto combina requisitos de privacidad, coste y rendimiento
- diferentes modulos necesitan proveedores distintos
- se desea separar analisis textual, generacion visual y procesamiento local

---

## 5. Relacion con creditos IA

### CID Managed AI
- consume creditos CID

### ComfyUI / GPU CID
- consume creditos CID
- especialmente relevante para generacion visual, video, restauracion y doblaje

### BYOK
- el coste API lo asume el cliente en su cuenta externa
- **CID puede cobrar creditos de orquestacion si se decide**, pero eso queda pendiente de definicion comercial

### Local Ollama
- no implica necesariamente consumo de creditos CID
- podria tener reglas de servicio o soporte separadas en enterprise

### ComfyUI / GPU cliente
- no implica necesariamente consumo de creditos CID por GPU
- puede existir coste de soporte/maintenance por parte de CID

### Hybrid Mode
- combina politicas de consumo distintas segun proveedor y modulo

---

## 6. Relacion con compra de creditos

El flujo de compra de creditos documentado en `cid_credit_purchase_flow_v1.md` aplica sobre todo a:
- **CID Managed AI**
- **ComfyUI / GPU CID**

### Regla funcional
Si el proyecto consume capacidad IA gestionada por CID, el Productor Propietario o perfil autorizado debe poder ampliar el CreditPool del proyecto sin alta operativa en proveedores externos.

### Caso BYOK
BYOK puede reducir o eliminar necesidad de compra de creditos GPU CID para ciertas operaciones, pero esa regla queda pendiente de definicion comercial y debe alinearse con la politica de orquestacion.

---

## 7. Relacion con planes Starter / Pro / Studio / Premium / Enterprise

### Starter
- acceso limitado a modos simples
- orientado a escenarios donde CID Managed AI sea suficiente

### Pro
- mayor volumen de uso y mas margen para creditos CID
- puede abrir puerta a configuraciones mas flexibles de IA gestionada

### Studio
- mas capacidad de consumo, mas proyectos y mas necesidad de control por rama
- candidato natural para ComfyUI / GPU CID en volumen moderado-alto

### Premium
- mayor elasticidad de creditos y operaciones IA
- puede combinar varios modos con mayor libertad operativa

### Enterprise
- modo natural para BYOK, Ollama local, ComfyUI / GPU cliente y Hybrid Mode
- prioriza aislamiento, seguridad, control de infraestructura y soporte especializado

### Regla funcional
El plan no define por si solo el proveedor tecnico, pero condiciona que modos son razonables comercial y operativamente para cada cliente.

---

## 8. Seguridad de claves secretas

### Reglas obligatorias
- nunca guardar API keys en frontend
- nunca exponer claves al navegador
- nunca registrar claves en logs
- mostrar solo los ultimos 4 caracteres
- permitir borrar o rotar clave
- permitir test de conexion sin revelar el secreto
- aislamiento por organizacion/proyecto
- cifrado obligatorio en futura implementacion backend

### Regla de producto
La interfaz debe hablar de claves como secretos gestionados, no como texto visible o editable libremente en cliente web.

---

## 9. Gestion de API keys

### Reglas funcionales
- una organizacion puede necesitar varias claves para distintos proveedores
- una clave puede quedar asociada a organizacion, proyecto o contexto enterprise segun politica futura
- la clave debe poder marcarse como activa, rotada o revocada
- el sistema debe mostrar solo referencia parcial del secreto (ultimos 4 caracteres)
- debe existir accion conceptual de prueba de conexion sin exponer la clave

### Importante
Este documento no define almacenamiento real, cifrado real ni UX final de gestion de claves.

---

## 10. Reglas BYOK

### Principios BYOK
- el cliente aporta su propia API key
- el coste del proveedor externo se carga en la cuenta del cliente
- CID no debe prometer que BYOK ya esta operativo si no esta verificado
- CID puede mantener capa de orquestacion, auditoria y politica de uso
- el cobro de creditos CID por orquestacion queda pendiente de definicion comercial

### Preguntas abiertas que NO se cierran aqui
- si BYOK descuenta cero creditos CID
- si BYOK descuenta creditos de orquestacion
- si algunos modulos obligan a CID Managed AI aunque exista BYOK

---

## 11. Privacidad y confidencialidad de guiones y materiales

### Regla general
La eleccion del proveedor debe considerar sensibilidad del material:
- guiones no publicados
- materiales de casting
- documentos financieros
- concept art no lanzado
- cortes editoriales

### Modos con mayor privacidad potencial
- Local Ollama
- ComfyUI / GPU cliente

### Modos con mayor dependencia de terceros
- CID Managed AI con proveedor externo
- BYOK sobre proveedor cloud del cliente

### Regla documental
La privacidad no depende solo del modo, sino tambien de retencion, logging, caching, soporte y gobierno de acceso.

---

## 12. Auditoria de uso IA

Toda operacion IA deberia poder registrar funcionalmente:
- proyecto
- organizacion
- usuario
- modulo
- modo/proveedor seleccionado
- si consumio creditos CID o consumo externo
- estado de ejecucion
- fecha y hora

### Regla funcional
La auditoria debe existir aunque el proveedor real cambie. El usuario no deberia perder trazabilidad por operar en modo hibrido.

---

## 13. Fallbacks entre proveedores

### Casos conceptuales de fallback
- si un proveedor LLM falla, degradar a otro proveedor gestionado por CID si existe regla permitida
- si BYOK no responde, permitir desactivar temporalmente ese modo y volver a CID Managed AI si el proyecto tiene creditos
- si ComfyUI / GPU CID esta saturado, redirigir a cola o a GPU cliente si la instalacion enterprise existe
- si un modelo local no esta disponible, ofrecer cambio a proveedor gestionado o detener la operacion segun sensibilidad del dato

### Regla funcional
Los fallbacks no deben cambiar silenciosamente politicas de coste o privacidad. El proyecto debe tener reglas explicitas para evitar sorpresas.

---

## 14. Riesgos

### Riesgos principales
- fuga de claves
- costes inesperados del cliente
- saturacion GPU
- latencia
- modelos no disponibles
- errores de proveedor
- datos sensibles

### Riesgos adicionales
- confusion entre BYOK y creditos CID
- trazabilidad incompleta en modo hibrido
- soporte complejo en entornos enterprise mixtos
- dependencia excesiva de un unico proveedor

---

## 15. Que NO implementar todavia

No implementar todavia:
- guardado real de claves
- cifrado real
- backend
- UI
- pagos
- seleccion real de proveedor
- routing real

### Regla de alcance
Este documento no describe endpoints, contratos tecnicos ni componentes implementados. Solo define arquitectura funcional y de producto.

---

## 16. Proxima fase

**`CID.AI.PROVIDER.COMMAND.CENTER.INTEGRATION.1`**

La siguiente fase debe definir:
- como aparece la seleccion conceptual de proveedor en el Command Center
- como se expresa la relacion entre proveedor, CreditPool y modos de consumo
- que señales de riesgo, privacidad o coste deben verse por proyecto
- que decisiones siguen reservadas a backend y cuales pueden documentarse en frontend como placeholders funcionales

---

## Historial de revisiones

| Fecha | Version | Cambios |
|---|---|---|
| 2026-06-03 | 1.0 | Creacion inicial del modelo funcional de proveedores IA en CID, incluyendo CID Managed AI, BYOK, Ollama, ComfyUI y modo hibrido. |
