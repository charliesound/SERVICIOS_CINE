# CID - Flujo de compra de creditos IA

**Documento:** `docs/business/cid_credit_purchase_flow_v1.md`
**Version:** 1.0
**Fecha:** 2026-06-03
**Tags:** `CID`, `business-model`, `credits`, `purchase-flow`, `product-architecture`, `monetization`
**Basado en:** `cid_credits_business_model_v1.md`, `cid_project_access_model_v1.md`, `cid_project_command_center_data_model_v1.md`

---

## Indice

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Principios del flujo de compra](#2-principios-del-flujo-de-compra)
3. [Separacion entre licencias, creditos y servicios](#3-separacion-entre-licencias-creditos-y-servicios)
4. [Quien puede comprar creditos](#4-quien-puede-comprar-creditos)
5. [Quien no puede comprar creditos por defecto](#5-quien-no-puede-comprar-creditos-por-defecto)
6. [Packs conceptuales de creditos](#6-packs-conceptuales-de-creditos)
7. [Flujo conceptual de compra](#7-flujo-conceptual-de-compra)
8. [Estados de compra](#8-estados-de-compra)
9. [Estados del CreditPool](#9-estados-del-creditpool)
10. [Alertas](#10-alertas)
11. [Reglas de auditoria](#11-reglas-de-auditoria)
12. [Seguridad](#12-seguridad)
13. [Casos de error](#13-casos-de-error)
14. [Relacion con BYOK / API key del cliente](#14-relacion-con-byok--api-key-del-cliente)
15. [Relacion con Command Center](#15-relacion-con-command-center)
16. [Que NO implementar todavia](#16-que-no-implementar-todavia)
17. [Riesgos](#17-riesgos)
18. [Proxima fase sugerida](#18-proxima-fase-sugerida)

---

## 1. Resumen ejecutivo

Este documento define el **flujo conceptual de compra de creditos IA dentro de CID**. El objetivo es que el productor pueda comprar creditos adicionales sin obligar al cliente a abrir cuentas separadas en proveedores externos de IA, GPU o pagos.

El principio base es:

```text
Cliente compra dentro de CID
CID gestiona el cobro
CID valida la transaccion
CID actualiza el CreditPool del proyecto
CID registra recibo, auditoria y alertas
```

Este flujo se diseña como **arquitectura de producto y negocio**, no como implementacion tecnica real. No se asume que exista ya una pasarela de pago, facturacion operativa, webhooks activos ni backend de compra implementado.

El productor no necesita crear cuenta en OpenAI, Runway, Stripe ni otros servicios externos para comprar creditos IA de proyecto dentro de la experiencia CID.

---

## 2. Principios del flujo de compra

### P1 - La compra sucede dentro de CID
El cliente inicia, confirma y consulta la compra desde CID. No debe depender de onboarding manual en servicios externos para el flujo normal de compra de creditos.

### P2 - Los creditos pertenecen al proyecto
Los creditos comprados se anaden al **CreditPool del proyecto**, no al usuario individual.

### P3 - El pago no cambia licencias ni permisos
Comprar creditos aumenta capacidad de consumo IA, pero no aumenta usuarios, no cambia visibilidad y no altera el plan de acceso por si mismo.

### P4 - Transparencia antes de consumir
El usuario autorizado debe ver que esta comprando creditos para consumo IA/GPU, no una ampliacion de licencia.

### P5 - Trazabilidad completa
Toda compra debe dejar rastro funcional: quien la inicio, para que proyecto, por que pack, con que saldo anterior y con que saldo posterior.

### P6 - Seguridad por defecto
CID no debe almacenar datos de tarjeta, secretos de pago ni claves sensibles en logs o documentos funcionales.

### P7 - Reversibilidad controlada
Si una compra queda en estado inconsistente, el sistema debe permitir reconciliar saldo y auditoria sin duplicar cargos ni duplicar creditos.

---

## 3. Separacion entre licencias, creditos y servicios

CID debe mantener tres planos diferenciados:

### Licencias
- Determinan acceso a la plataforma.
- Determinan capacidad de usuarios, proyectos y modulos visibles.
- Se relacionan con onboarding, invitaciones y visibilidad.

### Creditos
- Determinan consumo IA/GPU.
- Se consumen por operaciones de generacion, analisis o procesamiento intensivo.
- Se agregan al CreditPool del proyecto.

### Servicios
- Cubren onboarding, soporte, acompanamiento, personalizacion o despliegue especial.
- No deben mezclarse con creditos ni con licencias en el discurso comercial u operativo.

### Regla funcional

```text
Licencia != Creditos != Servicios
```

Un proyecto puede tener licencia activa y quedarse sin creditos.
Un proyecto puede comprar creditos extra sin cambiar de licencia.
Un cliente puede contratar servicios sin alterar su saldo de creditos.

---

## 4. Quien puede comprar creditos

Por defecto, el sistema debe permitir compra de creditos solo a perfiles con responsabilidad economica o de gobierno del proyecto.

### Perfiles autorizados por defecto
- **Productor Propietario**
- **Productor Ejecutivo autorizado**
- **Admin de organizacion**

### Regla funcional
La compra debe estar asociada a un permiso explicito de compra, aunque el usuario tenga acceso global al proyecto.

---

## 5. Quien no puede comprar creditos por defecto

Los siguientes perfiles no deben poder comprar creditos por defecto:
- director
- guionista
- script
- montador
- editor de sonido
- distribuidor
- agente de ventas

### Regla funcional
Estos perfiles pueden ver estado o alertas de consumo si el producto lo decide en fases futuras, pero no deben iniciar compras por defecto sin delegacion expresa.

---

## 6. Packs conceptuales de creditos

Los packs de compra se definen de forma conceptual. **No se fijan precios definitivos** en este documento.

### Packs base
- **+500** creditos
- **+1.000** creditos
- **+3.000** creditos
- **+10.000** creditos
- **Enterprise personalizado**

### Regla funcional
Cada pack debe presentar:
- volumen de creditos
- descripcion conceptual del uso esperado
- nota de que el precio final puede variar por politica comercial o por entorno enterprise

### Importante
Este documento no fija precio final, divisa final, impuestos finales ni estructura contractual cerrada.

---

## 7. Flujo conceptual de compra

### Paso 1 - Alerta de creditos bajos
El proyecto entra en estado `bajo`, `critico` o `agotado` y muestra alerta al Productor Propietario, Productor Ejecutivo autorizado y/o Admin de organizacion.

### Paso 2 - Boton "Anadir creditos"
Desde la tarjeta futura del CreditPool del proyecto aparece la accion de compra.

### Paso 3 - Seleccion de pack
El usuario autorizado selecciona uno de los packs conceptuales o una opcion enterprise personalizada.

### Paso 4 - Confirmacion
CID resume:
- proyecto afectado
- pack seleccionado
- volumen de creditos
- importe conceptual a confirmar
- aviso de que el saldo se anadira al CreditPool del proyecto

### Paso 5 - Pago
CID redirige o muestra el flujo de cobro dentro de su propia experiencia. El cliente no necesita alta operativa manual en proveedores externos.

### Paso 6 - Validacion
CID valida que la compra fue aceptada antes de actualizar saldo.

### Paso 7 - Actualizacion del CreditPool
El CreditPool del proyecto recibe el incremento correspondiente.

### Paso 8 - Recibo / factura
CID registra comprobante funcional de la operacion y deja rastro para facturacion posterior si aplica.

### Paso 9 - Auditoria
CID registra evento de auditoria con saldo anterior, saldo posterior, usuario y proyecto.

---

## 8. Estados de compra

### Estados funcionales
- `iniciado`
- `pendiente_de_pago`
- `pagado`
- `fallido`
- `cancelado`
- `reembolsado` (si aplica)

### Reglas
- `pagado` es el unico estado que puede aumentar saldo.
- `fallido` no modifica saldo.
- `cancelado` no modifica saldo.
- `reembolsado` requiere log de reversa o ajuste manual del CreditPool si procede.

---

## 9. Estados del CreditPool

### Estados funcionales
- `suficiente`
- `bajo`
- `critico`
- `agotado`
- `bloqueado`

### Interpretacion
- **suficiente**: el proyecto puede operar con normalidad.
- **bajo**: hay que anticipar recarga.
- **critico**: el proyecto puede sufrir interrupciones en funciones IA.
- **agotado**: no se deben lanzar operaciones IA que consuman creditos.
- **bloqueado**: estado excepcional por fraude, disputa, inconsistencia o suspension operativa.

---

## 10. Alertas

### Alertas de consumo
- 80% consumido
- 90% consumido
- creditos agotados

### Alertas de compra
- compra pendiente
- pago fallido

### Reglas
- Las alertas deben ser visibles para quienes pueden comprar.
- En fases futuras, algunas alertas podran ser visibles a perfiles informativos sin permiso de compra.

---

## 11. Reglas de auditoria

Cada compra debe registrar como minimo:
- quien compro
- cuando compro
- proyecto afectado
- pack comprado
- importe conceptual (sin fijar precio final en este documento)
- saldo anterior
- saldo posterior

### Regla funcional
La auditoria debe permitir distinguir entre:
- compra iniciada
- compra pagada
- creditos aplicados
- creditos reconciliados manualmente

---

## 12. Seguridad

### Reglas base
- no exponer datos sensibles en la UI funcional
- no guardar datos de tarjeta en CID
- no registrar claves de pago en logs
- permitir revocar permisos de compra

### Reglas adicionales
- las operaciones de compra deben requerir rol autorizado
- el proyecto archivado o cerrado no deberia aceptar compras normales sin regla especial
- un estado `bloqueado` del CreditPool debe impedir recargas automaticas hasta revision

---

## 13. Casos de error

### Pago rechazado
La compra queda en `fallido` y el CreditPool no cambia.

### Pago duplicado
Debe existir mecanismo de idempotencia funcional o conciliacion posterior para evitar doble aplicacion de creditos.

### Webhook no recibido
Aunque el documento no diseña integracion real, el modelo debe contemplar validacion diferida o reconciliacion manual.

### Compra aprobada pero creditos no aplicados
Debe existir estado intermedio auditable y proceso de correccion.

### Downgrade de plan
El downgrade de licencia no debe borrar creditos comprados ya concedidos, salvo politica futura explicitamente definida.

### Proyecto archivado
La compra normal debe bloquearse o exigir regla especial si el proyecto ya no deberia consumir IA.

---

## 14. Relacion con BYOK / API key del cliente

Si el cliente usa su propia API key o infraestructura propia, parte del consumo puede **no descontar creditos GPU CID** o puede requerir una regla distinta de contabilizacion.

### Regla documental
Este punto queda **pendiente de decision** y debe documentarse en la siguiente fase sugerida del modelo de proveedores IA.

---

## 15. Relacion con Command Center

### Presencia en el proyecto
- El **CreditPool** aparece como tarjeta del proyecto en el Command Center.
- El boton futuro **"Anadir creditos"** nace en ese contexto de proyecto.
- Las alertas visibles se orientan a Productor Propietario y Productor Ejecutivo.

### Regla funcional
El Command Center no debe mostrar la compra como si ya estuviera implementada; solo debe reservar su espacio conceptual y su semantica de negocio.

---

## 16. Que NO implementar todavia

No implementar todavia:
- Stripe real
- facturacion real
- backend
- webhooks
- pagos
- UI real de compra
- compra real

### Regla de alcance
Este documento describe la arquitectura de producto/negocio, no una integracion tecnica operativa.

---

## 17. Riesgos

### Riesgos principales
- abuso de creditos
- compras no autorizadas
- doble cargo
- fraude
- soporte al cliente
- saturacion GPU

### Riesgos secundarios
- reconciliacion manual costosa
- ambiguedad con BYOK
- confusion entre licencia y creditos
- compras sobre proyectos sin actividad real

---

## 18. Proxima fase sugerida

**`CID.AI.PROVIDER.MODEL.1`**

La siguiente fase debe definir:
- relacion entre CreditPool y proveedores IA
- diferencias entre consumo CID y consumo BYOK
- reglas de atribucion de coste GPU
- que operaciones descuentan del pool y cuales no

---

## Historial de revisiones

| Fecha | Version | Cambios |
|---|---|---|
| 2026-06-03 | 1.0 | Creacion inicial del flujo conceptual de compra de creditos IA dentro de CID, sin integracion tecnica ni precios finales. |
