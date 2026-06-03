# CID Project Command Center — Modelo funcional de acceso

**Documento:** `docs/product/cid_project_access_model_v1.md`
**Versión:** 1.0
**Fecha:** 2026-06-02
**Tags:** `CID`, `product-architecture`, `access-model`, `permission-pyramid`, `licensing`
**Basado en:** `cid_project_command_center_branches_v1.md`, `cid_project_command_center_data_model_v1.md`

---

## Índice

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Principios de acceso](#2-principios-de-acceso)
3. [Productor Propietario](#3-productor-propietario)
4. [Productor Ejecutivo](#4-productor-ejecutivo)
5. [Organización](#5-organizacion)
6. [Proyecto](#6-proyecto)
7. [Rama](#7-rama)
8. [Usuario](#8-usuario)
9. [Invitación](#9-invitacion)
10. [Licencia](#10-licencia)
11. [Visibilidad](#11-visibilidad)
12. [Auditoría](#12-auditoria)
13. [Alternativas de licenciamiento](#13-alternativas-de-licenciamiento)


---

## 1. Resumen ejecutivo

Este documento define el **modelo funcional de acceso** del Project Command Center de CID. Mientras que la arquitectura de ramas describe qué módulos existen y a qué rama pertenecen, y el modelo de datos describe qué entidades y campos existen, este documento describe **quién puede acceder a qué**, **bajo qué condiciones**, **quién concede y revoca acceso**, y **cómo se relaciona el acceso con los planes de licencia**.

El modelo de acceso se basa en cuatro principios:
1. **No existe acceso universal.** Cada rol ve solo lo que necesita para ejecutar su trabajo.
2. **El Productor Propietario controla el proyecto.** Decide quién entra, con qué rol, y quién sale.
3. **Los departamentos acceden por responsabilidad.** Cada equipo opera dentro de su rama funcional.
4. **La licencia determina la capacidad máxima.** El plan contratado define cuántos usuarios pueden tener acceso simultáneo por rama.

Este documento no especifica implementación técnica (RBAC, backend, base de datos, SQL, endpoints, frontend). Es puramente arquitectura funcional de acceso.

---

## 2. Principios de acceso

### P1 — Acceso mínimo necesario
Cada usuario obtiene únicamente el acceso necesario para cumplir su función. Ningún acceso se concede por defecto; todo acceso se concede explícitamente.

### P2 — Jerarquía de control
El Productor Propietario está en la cima de la jerarquía de acceso. Nadie por encima de él dentro del proyecto. El Productor Ejecutivo tiene acceso delegado global, pero no puede cambiar el rol del Productor Propietario.

### P3 — Acceso por rama funcional
Cada rol pertenece a una rama principal. El acceso a otras ramas es excepcional y debe ser concedido explícitamente por el Productor Propietario.

### P4 — Separación de visibilidad
Un usuario de una rama no ve datos de otra rama a menos que exista una dependencia funcional documentada y el Productor la haya autorizado.

### P5 — La licencia limita, no habilita
El plan de licencia determina cuántos usuarios pueden tener acceso simultáneo por rama, pero no determina qué roles existen ni qué permisos tienen esos roles.

### P6 — Rastro de cambios
Toda concesión, revocación o cambio de rol debe ser registrada para auditoría. El Productor Propietario puede consultar el historial de acceso.

### P7 — Accesos excepcionales y temporales
El Productor Propietario puede conceder accesos temporales a una rama para un usuario de otra rama. Estos accesos tienen caducidad explícita.

---

## 3. Productor Propietario

**Rol:** Propietario del proyecto en CID.
**Rama principal:** Todas (acceso global).
**Nivel jerárquico:** 1 — Dirección del proyecto.

### Responsabilidades de acceso
- Controla quién entra al proyecto (invitación).
- Controla quién sale del proyecto (revocación).
- Asigna y cambia roles de los miembros.
- Concede accesos excepcionales a ramas.
- Define accesos temporales con caducidad.
- Consulta el historial de acceso del proyecto.
- Transfiere la propiedad a otro usuario (solo él puede hacerlo).

### Capacidades de acceso
| Capacidad | Descripción |
|---|---|
| `puedeInvitar` | Puede invitar a cualquier usuario a cualquier rol |
| `puedeRevocar` | Puede revocar a cualquier usuario, excepto a sí mismo |
| `puedeCambiarRoles` | Puede cambiar el rol de cualquier usuario, excepto el suyo propio |
| `puedeVerTodo` | Acceso completo a todas las ramas, módulos, entidades y campos |
| `puedeConcederExcepcion` | Puede conceder acceso temporal o permanente a una rama |
| `puedeAuditar` | Puede consultar el log de cambios de acceso |
| `puedeTransferirPropiedad` | Puede transferir la propiedad a otro usuario del proyecto |
| `puedeConfigurarPlan` | Puede seleccionar o cambiar el plan de licencia del proyecto |

### Restricciones
- No puede revocarse a sí mismo sin transferir la propiedad antes.
- No puede haber más de un Productor Propietario por proyecto (la transferencia de propiedad revoca automáticamente la anterior).
- No puede ser degradado por ningún otro rol.

---

## 4. Productor Ejecutivo

**Rol:** Supervisión financiera y estratégica delegada.
**Rama principal:** Rama 1 — Producción y Financiación.
**Nivel jerárquico:** 1 — Dirección del proyecto (acceso global delegado).

### Responsabilidades de acceso
- Puede invitar usuarios a la Rama 1 (Producción y Financiación) y al área de Comercialización.
- Puede revocar usuarios de las ramas que él mismo invitó.
- Puede cambiar roles dentro de las ramas que supervisa.
- Puede ver el estado global del proyecto.

### Capacidades de acceso
| Capacidad | Descripción |
|---|---|
| `puedeInvitarRama1` | Puede invitar a roles de Producción y Financiación |
| `puedeInvitarComercial` | Puede invitar a roles de Comercialización |
| `puedeRevocarRama1` | Puede revocar usuarios de Rama 1 que él invitó |
| `puedeCambiarRolesRama1` | Puede cambiar roles dentro de Rama 1 |
| `puedeVerTodo` | Acceso de lectura a todas las ramas |
| `puedeVerRama1Completo` | Acceso completo a datos de Rama 1 |
| `puedeVerComercialCompleto` | Acceso completo a datos de Comercialización |

### Restricciones
- No puede invitar al rol de Productor Propietario.
- No puede revocar al Productor Propietario.
- No puede cambiar el rol del Productor Propietario.
- No puede invitar usuarios a Rama 2 (Creativo y Rodaje) ni a Rama 3 (Postproducción y Entrega) — solo lectura.
- Su acceso a Rama 2 y Rama 3 es de solo lectura, salvo autorización expresa del Productor Propietario.

---

## 5. Organización

**Entidad:** Agrupación legal o comercial que posee proyectos.
**Relación con el acceso:** La organización es el contenedor de proyectos y usuarios. Un usuario pertenece a una organización y hereda ciertos contextos de ella.

### Reglas de acceso a nivel de organización

| Regla | Descripción |
|---|---|
| **Propietario de organización** | Usuario que creó la organización en CID. Controla la suscripción y los proyectos. |
| **Miembros de organización** | Usuarios asociados a la organización, con acceso a uno o varios proyectos. |
| **Proyectos por organización** | Una organización puede tener múltiples proyectos. Cada proyecto tiene su propio Productor Propietario. |
| **Visibilidad entre proyectos** | Un usuario de un proyecto no ve otros proyectos de la misma organización a menos que tenga acceso explícito. |
| **Roles a nivel de organización** | Existen roles organizacionales (Admin, Member) separados de los roles de proyecto. Un Admin de organización puede gestionar la suscripción y los miembros, pero no tiene acceso automático a los proyectos. |

### Niveles de acceso en la organización

| Nivel | Quién lo tiene | Capacidades |
|---|---|---|
| **Admin de organización** | Propietario de organización o delegado | Gestionar suscripción, invitar admins, ver todos los proyectos (metadatos), gestionar miembros |
| **Member de organización** | Cualquier usuario añadido | Acceder a proyectos donde tiene rol asignado, gestionar su perfil |
| **Externo** | Sin membresía organizacional | No existe en el contexto de la organización |

---

## 6. Proyecto

**Entidad:** Producción cinematográfica individual.
**Relación con el acceso:** El proyecto es la unidad de acceso. Todos los permisos se definen en el contexto de un proyecto.

### Reglas de acceso a nivel de proyecto

| Regla | Descripción |
|---|---|
| **Creación** | Cualquier Admin de organización puede crear un proyecto. Al crearlo, se convierte en su Productor Propietario. |
| **Propietario único** | Cada proyecto tiene exactamente un Productor Propietario. |
| **Transferencia** | El Productor Propietario puede transferir la propiedad a otro miembro del proyecto. |
| **Herencia** | Un proyecto no hereda usuarios de la organización. Cada proyecto tiene su propia lista de miembros. |
| **Visibilidad externa** | Los proyectos no son visibles para miembros de la organización que no tengan acceso explícito. |

### Estados de acceso de un proyecto

| Estado (ID ES) | ID EN | Descripción |
|---|---|---|
| Activo | `ACTIVE` | El proyecto acepta invitaciones y los miembros tienen acceso normal. |
| Congelado | `FROZEN` | El proyecto no acepta nuevas invitaciones. Los miembros existentes mantienen acceso de solo lectura. |
| Archivado | `ARCHIVED` | El proyecto es solo visible para el Productor Propietario y Admins de organización. Sin invitaciones ni modificaciones. |
| Cerrado | `CLOSED` | Proyecto finalizado. Todos los accesos revocados excepto Productor Propietario. Visible solo para él. |

Transiciones esperadas:

`PREPROD → ACTIVE → FROZEN → ACTIVE`
`ACTIVE → WRAPPING → ARCHIVED → CLOSED`

Los estados `PREPROD` (preparación inicial) y `WRAPPING` (cierre de producción) son estados operativos previos a `ACTIVE` y `ARCHIVED` respectivamente; no afectan al modelo de acceso más que para restringir invitaciones durante `WRAPPING`.

---

## 7. Rama

**Entidad:** Unidad funcional del ciclo de producción.
**Relación con el acceso:** La rama es la unidad de aislamiento de acceso. Cada usuario tiene acceso prioritario a su rama principal.

### Las tres ramas funcionales

| Rama | ID | Roles principales |
|---|---|---|
| Producción y Financiación | `rama1` | Productor Ejecutivo, Jefe de Producción |
| Creativo y Rodaje | `rama2` | Director, Guionista, Script Supervisor, Ayudante de Dirección |
| Postproducción, Entrega y Comercialización | `rama3` | Montador, Editor de Sonido, Post Supervisor, Distribuidor, Agente de Ventas |

### Reglas de acceso por rama

| Regla | Descripción |
|---|---|
| **Rama principal** | Cada rol pertenece a una rama principal. Su acceso completo se limita a esa rama. |
| **Ramas secundarias** | Un usuario puede tener acceso limitado (lectura o parcial) a otras ramas si existe dependencia funcional. |
| **Activación de rama** | La Rama 3 solo se activa para roles de Rama 2 después de que el hito "Rodaje completado" se haya cumplido. |
| **Visibilidad entre ramas** | Un usuario de Rama 1 no ve el contenido de Storyboard ni Script. Un usuario de Rama 2 no ve Budget line items ni FundingSource. |

### Matriz de acceso por rama

| Rol | Rama 1 | Rama 2 | Rama 3 | Comercialización |
|---|---|---|---|---|
| Productor Propietario | Completo | Completo | Completo | Completo |
| Productor Ejecutivo | Completo | Lectura | Lectura | Completo |
| Jefe de Producción | Completo | Parcial | Parcial (costes) | Sin acceso |
| Director | Lectura | Completo | Parcial* | Sin acceso |
| Guionista | Sin acceso | Completo (guion) | Sin acceso | Sin acceso |
| Script Supervisor | Sin acceso | Completo (continuidad) | Sin acceso | Sin acceso |
| Ayudante de Dirección | Sin acceso | Completo (rodaje) | Sin acceso | Sin acceso |
| Montador / Editor | Sin acceso | Lectura (referencias) | Completo | Sin acceso |
| Editor de Sonido | Sin acceso | Sin acceso | Parcial (sonido) | Sin acceso |
| Post Supervisor | Sin acceso | Sin acceso | Completo | Completo |
| Distribuidor | Sin acceso | Sin acceso | Sin acceso | Completo |
| Agente de Ventas | Sin acceso | Sin acceso | Sin acceso | Completo (ventas) |

*_Parcial: solo después de activación por hito "Rodaje completado"._

---

## 8. Usuario

**Entidad:** Persona física que accede a CID.
**Relación con el acceso:** El usuario es el sujeto de todos los permisos. Su acceso se define por su rol en el proyecto y las ramas a las que tiene acceso.

### Estados de un usuario en el proyecto

| Estado | Descripción |
|---|---|
| `INVITADO` | Ha recibido invitación pero no la ha aceptado. Sin acceso a ningún dato. |
| `ACTIVO` | Ha aceptado la invitación. Acceso según su rol. |
| `SUSPENDIDO` | Acceso revocado temporalmente por el Productor. No puede acceder hasta que se reactive. |
| `REVOCADO` | Acceso eliminado permanentemente. Debe ser invitado de nuevo para volver. |
| `AUDITADO` | Estado especial de solo lectura para revisiones externas. Sin capacidad de modificar datos. |

### Datos de acceso asociados al usuario

| Dato | Descripción |
|---|---|
| `userId` | Identificador único del usuario |
| `projectId` | Proyecto al que pertenece el acceso |
| `roleId` | Rol principal en el proyecto |
| `secondaryRoles` | Roles secundarios (opcional) |
| `assignedBranchIds` | Ramas a las que tiene acceso |
| `accessLevels` | Nivel de acceso por rama (completo/parcial/lectura/sin acceso) |
| `grantedAt` | Fecha en que se concedió el acceso |
| `grantedBy` | Usuario que concedió el acceso |
| `expiresAt` | Fecha de caducidad del acceso (opcional, para accesos temporales) |
| `lastAccessAt` | Última vez que el usuario accedió al proyecto |

### Reglas del usuario

- Un usuario puede tener exactamente un rol principal por proyecto.
- Un usuario puede tener roles secundarios dentro del mismo proyecto.
- Un usuario puede estar en múltiples proyectos (de la misma o diferentes organizaciones).
- Un usuario solo puede tener un acceso simultáneo por proyecto (no puede ser dos personas distintas en el mismo proyecto).
- El acceso expirado (si tiene `expiresAt` pasado) se revoca automáticamente.

## 9. Invitación

**Propósito:** Añadir un usuario al proyecto con un rol específico y acceso a sus ramas correspondientes.

### Quién puede invitar

| Rol | Puede invitar a | Restricciones |
|---|---|---|
| Productor Propietario | Cualquier rol en cualquier rama | Sin restricciones |
| Productor Ejecutivo | Roles de Rama 1 y Comercialización | No puede invitar Productor Propietario, ni roles de Rama 2 o Rama 3 |
| Jefe de Producción | No puede invitar | Solo el Productor concede invitaciones |

### Flujo de invitación

```
1. INICIO
   Productor Propietario o Productor Ejecutivo accede al panel de miembros

2. SELECCIÓN
   Introduce el email del usuario a invitar
   Selecciona el rol (determina la rama principal automáticamente)
   Selecciona ramas adicionales (opcional, solo si el rol tiene acceso parcial a otras ramas)
   Define fecha de caducidad (opcional, para accesos temporales)

3. CONFIRMACIÓN
   El sistema verifica:
     - ¿El email es válido?
     - ¿El usuario ya existe en CID?
     - ¿El usuario ya tiene acceso a este proyecto?
     - ¿El plan de licencia tiene capacidad disponible en la rama?
   Si todo es válido, se envía la invitación.

4. NOTIFICACIÓN
   El usuario recibe un email con enlace para aceptar la invitación
   Si el usuario no existe en CID, se le invita a registrarse primero

5. ACEPTACIÓN
   El usuario acepta la invitación
   El sistema activa el acceso según el rol y ramas seleccionadas
   El usuario aparece como ACTIVO en el proyecto

6. CONFIRMACIÓN AL PRODUCTOR
   El Productor recibe notificación de que el usuario ha aceptado
```

### Reglas de invitación

| Regla | Descripción |
|---|---|
| **Límite de licencia** | No se puede invitar a un usuario si el plan ha alcanzado el máximo de usuarios en esa rama |
| **Email único** | No se puede invitar al mismo email dos veces al mismo proyecto |
| **Invitación expirada** | Las invitaciones no aceptadas caducan a los 7 días |
| **Reenvío** | El Productor puede reenviar una invitación caducada |
| **Sin aceptación automática** | El usuario debe aceptar explícitamente. El Productor no puede forzar la entrada |
| **Acceso inmediato** | El acceso se concede en el momento de aceptación, no antes |

---

## 10. Licencia

**Propósito:** El plan de licencia determina la capacidad máxima de usuarios simultáneos por rama en un proyecto.

### Capacidad por plan

| Plan | Productores | Usuarios totales por proyecto | Características adicionales |
|---|---|---|---|---|
| **Starter** | 1 Productor Propietario | Hasta 9 usuarios (multi-rama ilimitado) | Acceso básico, sin accesos temporales, sin auditoría |
| **Pro** | 1 Productor Propietario + 1 Productor Ejecutivo | Hasta 15 usuarios (multi-rama ilimitado) | Accesos temporales, invitaciones por Productor Ejecutivo |
| **Studio** | 1 Productor Propietario + 1 Productor Ejecutivo | Hasta 30 usuarios (multi-rama ilimitado) | Accesos temporales, auditoría, roles secundarios |
| **Premium** | 1 Productor Propietario + 1 Productor Ejecutivo | Hasta 50 usuarios (multi-rama ilimitado) | Prioridad, auditoría completa, roles secundarios, accesos temporales |
| **Enterprise** | Configurable | Configurable | Todo lo anterior + RBAC personalizado, SSO, auditoría avanzada |

### Reglas de licencia

| Regla | Descripción |
|---|---|
| **Cómputo por proyecto** | La licencia cuenta usuarios activos por proyecto, no por rama. Un usuario en N ramas cuenta 1 vez. Los Productores Propietario y Ejecutivo no computan. |
| **Usuario activo** | Solo los usuarios en estado ACTIVO computan para el límite. INVITADO, SUSPENDIDO y REVOCADO no computan. |
| **Cambio de plan** | Al hacer upgrade, el límite aumenta inmediatamente. Al hacer downgrade, el sistema notifica al Productor qué usuarios deben ser revocados antes de que el cambio se aplique. |
| **Plan por proyecto** | La licencia se aplica por proyecto, no por organización. Una organización puede tener proyectos en diferentes planes. |
| **Excedente temporal** | Si un proyecto supera el límite por downgrade, los usuarios existentes mantienen acceso por 30 días (periodo de gracia) antes de que el acceso se suspenda. |

### Capacidad sugerida por rama (guía UX, sin restricción de facturación)

| Plan | Rama 1 (guía) | Rama 2 (guía) | Rama 3 (guía) | Comercialización (guía) |
|---|---|---|---|---|
| **Starter** | 3 usuarios | 3 usuarios | 3 usuarios | Incluido en Rama 3 |
| **Pro** | 5 usuarios | 5 usuarios | 5 usuarios | Incluido en Rama 3 |
| **Studio** | 10 usuarios | 10 usuarios | 10 usuarios | Incluido en Rama 3 |
| **Premium** | 15 usuarios | 15 usuarios | 15 usuarios | Incluido en Rama 3 |
| **Enterprise** | Configurable | Configurable | Configurable | Configurable |

**Nota sobre Rama 3:** La columna "Rama 3" unifica las subáreas **Postproducción** y **Entrega**. La columna "Comercialización" se incluye dentro del cómputo de capacidad de Rama 3 (guía UX) pero se expone como columna separada por su perfil de acceso específico.

---

## 11. Visibilidad

**Propósito:** Definir qué ve cada rol según su nivel de acceso a cada rama.

### Niveles de acceso

| Nivel | Descripción | Capacidades |
|---|---|---|
| **Completo** | Acceso total a la rama | Lectura, escritura, creación, eliminación, invitación (si aplica) |
| **Parcial** | Acceso solo a submódulos específicos | Depende del rol. Ej: Jefe de Producción solo ve estimatedHours y actualHours en ShootingPlan |
| **Solo lectura** | Puede consultar pero no modificar | Visualización de datos, sin capacidad de crear, editar ni eliminar |
| **Sin acceso** | La rama no está visible | El módulo no aparece en navegación ni en búsquedas. Acceso por URL directa redirige a pantalla de "acceso restringido" |

### Reglas de visibilidad

1. **El Productor Propietario ve el estado global.** Su dashboard es el único que muestra indicadores de las tres ramas simultáneamente.

2. **Cada rol ve por defecto su rama principal.** Al entrar en CID, el usuario aterriza en el dashboard de su rama, no en el dashboard global.

3. **Las ramas secundarias aparecen solo cuando exista dependencia funcional.** Un director puede ver postproducción cuando el montaje comienza. Un jefe de producción puede ver rodaje cuando necesita planificar costes.

4. **Los módulos no accesibles no aparecen en la navegación.** No se muestran enlaces, tabs ni breadcrumbs de módulos sin acceso.

5. **Acceso denegado.** Si un usuario intenta acceder por URL directa a un módulo sin permiso, ve una pantalla de "acceso restringido" con opción de solicitar permiso al Productor Propietario.

6. **Visibilidad de miembros.** Todos los miembros del proyecto pueden ver la lista de miembros (nombres y roles), pero no ven datos de contacto ni fechas de acceso de otros miembros.

7. **Visibilidad de cambios.** Los cambios realizados por un usuario en su rama son visibles para otros miembros de la misma rama, pero no para miembros de otras ramas.

### Tabla de visibilidad por rol

| Rol | Ve su rama | Ve otras ramas | Ve miembros | Ve dashboard global |
|---|---|---|---|---|
| Productor Propietario | Completo | Completo | Completo | Sí |
| Productor Ejecutivo | Completo (R1) | Lectura (R2, R3) | Completo | Sí |
| Jefe de Producción | Completo (R1) | Parcial (R2 costes, R3 costes) | Completo | No (solo R1) |
| Director | Completo (R2) | Lectura (R1 presupuesto), Parcial (R3 post-rodaje) | Completo | No (solo R2) |
| Guionista | Completo (R2 guion) | Sin acceso | Solo nombres | No |
| Script Supervisor | Completo (R2 continuidad) | Sin acceso | Solo nombres | No |
| Ayudante de Dirección | Completo (R2 rodaje) | Sin acceso | Solo nombres | No |
| Montador / Editor | Completo (R3 montaje) | Lectura (R2 referencias) | Solo nombres | No |
| Editor de Sonido | Parcial (R3 sonido) | Sin acceso | Solo nombres | No |
| Post Supervisor | Completo (R3) | Sin acceso | Completo | No (solo R3) |
| Distribuidor | Completo (Comercialización) | Sin acceso | Solo nombres | No |
| Agente de Ventas | Completo (Comercialización ventas) | Sin acceso | Solo nombres | No |

---

## 12. Auditoría

**Propósito:** Registrar todos los cambios de acceso para que el Productor Propietario y los Admins de organización puedan rastrear quién hizo qué y cuándo.

### Eventos auditables

| Evento | Descripción | Datos registrados |
|---|---|---|
| `USUARIO_INVITADO` | Se envió una invitación | email, rol, ramas, invitado por, fecha, caducidad |
| `INVITACION_ACEPTADA` | El usuario aceptó la invitación | userId, fecha |
| `INVITACION_CADUCADA` | La invitación expiró | email, fecha |
| `ROL_CAMBIADO` | Se cambió el rol de un usuario | userId, rol anterior, rol nuevo, cambiado por, fecha |
| `ACCESO_CONCEDIDO` | Se concedió acceso a una rama adicional | userId, rama, nivel, concedido por, fecha, caducidad (si temporal) |
| `ACCESO_REVOCADO` | Se revocó el acceso a una rama | userId, rama, revocado por, fecha, motivo |
| `USUARIO_SUSPENDIDO` | Se suspendió a un usuario | userId, suspendido por, fecha, motivo |
| `USUARIO_REACTIVADO` | Se reactivó a un usuario suspendido | userId, reactivado por, fecha |
| `USUARIO_REVOCADO` | Se eliminó el acceso permanentemente | userId, revocado por, fecha, motivo |
| `PROPIEDAD_TRANSFERIDA` | Se transfirió la propiedad del proyecto | propietario anterior, nuevo propietario, fecha |

### Reglas de auditoría

| Regla | Descripción |
|---|---|
| **Registro obligatorio** | Todos los eventos de acceso se registran automáticamente. No hay opción de omitir el registro. |
| **Inmutabilidad** | Los registros de auditoría no se pueden modificar ni eliminar. |
| **Visibilidad** | Solo el Productor Propietario y los Admins de organización pueden consultar la auditoría. |
| **Retención** | Los registros se conservan durante toda la vida del proyecto más 12 meses después de su cierre. |
| **Exportación** | El Productor Propietario puede exportar el log de auditoría en formato CSV. |
| **Plan Studio+** | La auditoría completa solo está disponible en planes Studio y Enterprise. Starter y Pro tienen un registro básico (últimos 30 días, sin exportación). |
| **Notificaciones** | El Productor Propietario recibe notificación de eventos críticos: cambio de propiedad, revocación masiva, superación de límite de licencia. |


## 13. Alternativas de licenciamiento

**Propósito:** Analizar y comparar los modelos de cómputo de licencia viables para CID y fundamentar la decisión adoptada. Esta sección es un anexo de análisis; la sección §10 contiene la definición operativa del modelo actual.

### Modelo A — Cómputo por rama (actual en §10)

El usuario cuenta tantas veces como ramas a las que tenga acceso. Si un usuario pertenece a Rama 1 y Rama 3, consume un cupo en ambas.

| Aspecto | Característica |
|---|---|
| **Cálculo** | `total_licencia = sum(usuarios_activos_por_rama)` |
| **Ejemplo práctico** | Proyecto con 4 usuarios en R1, 3 en R2, 2 en R3 = 9 cómputos. Un Director con acceso a R2 + R3 = cuenta en R2 y R3. |
| **Techo por rama** | Cada rama tiene su propio límite independiente. |

### Modelo B — Cómputo por proyecto (alternativa)

El usuario cuenta una sola vez por proyecto, independientemente de cuántas ramas tenga acceso.

| Aspecto | Característica |
|---|---|
| **Cálculo** | `total_licencia = count(usuarios_activos_del_proyecto)` |
| **Ejemplo práctico** | Proyecto con 9 usuarios únicos, cada uno en una o varias ramas = 9 cómputos. Un Director con acceso a R2 + R3 = 1 cómputo. |
| **Techo por proyecto** | Límite global de usuarios en el proyecto, sin distinción por rama. |

### Modelo C — Usuarios incluidos por plan + acceso multi-rama ilimitado (alternativa)

Cada plan incluye un número fijo de usuarios que pueden acceder a cualquier rama sin coste adicional por rama. Una vez dentro del proyecto, el usuario puede ser asignado a todas las ramas que su rol requiera sin generar cómputos extra.

| Aspecto | Característica |
|---|---|
| **Cálculo** | `total_licencia = usuarios_activos_del_proyecto`, con tope fijo según plan. No hay cómputo por rama. |
| **Ejemplo práctico** | Proyecto Starter (hasta 9 usuarios incluidos). 9 usuarios distribuidos en R1, R2, R3 sin importar cuántas ramas toque cada uno = 9 cómputos. |
| **Techo por plan** | Límite global de usuarios por proyecto: 9 (Starter), 15 (Pro), 30 (Studio), 50 (Premium), Enterprise configurable. |
| **Multi-rama** | Ilimitado. Un usuario en N ramas sigue contando 1. |

### Comparación

| Criterio | Modelo A (por rama) | Modelo B (por proyecto) | Modelo C (incluidos + multi-rama ilimitado) |
|---|---|---|---|
| **Simplicidad de implementación** | Media. Requiere contabilizar acceso por rama y validar límites por rama en cada invitación/cambio de rol. | Alta. Un contador único por proyecto. Más fácil de implementar y verificar. | Alta. Misma implementación que B: contador único. Sin lógica extra por rama. |
| **Simplicidad de facturación** | Baja. El cliente puede no entender por qué un usuario "cuenta dos veces". Requiere educación comercial. | Alta. El cliente entiende "pago por N usuarios en el proyecto". | Alta. Similar a B, más fácil aún: "pago por N usuarios, sin importar las ramas." |
| **Escalabilidad (proyectos grandes)** | Alta. Cada rama crece independientemente. Un proyecto con 30 en R2 y 3 en R1 no encarece R1. | Media. Un proyecto con 30 en R2 obliga a pagar por 30 aunque el resto de ramas tenga 3. | Baja. Un proyecto con 30 en R2 consume todo el slot del plan Studio (30). Si necesita más, debe hacer upgrade a Enterprise. |
| **Escalabilidad (proyectos multi-rama)** | Baja. Un usuario en 3 ramas cuenta 3 veces. El coste se multiplica con la colaboración interdepartamental. | Alta. Un usuario en 3 ramas cuenta 1 vez. La colaboración no penaliza. | Alta. Igual que B. La colaboración no penaliza. |
| **Percepción del cliente** | Negativa potencial. "Tengo 5 personas pero me facturan 8 porque algunas están en dos ramas." Sensación de penalización por colaborar entre departamentos. | Positiva. "Pago por cabeza, no por departamento." Transparencia. | Muy positiva. "Pago por cabeza y mi gente puede colaborar sin límite." Máxima percepción de valor. |
| **Alineación con arquitectura de ramas** | Alta. Refleja que cada rama es una unidad de acceso independiente. | Baja. Un pago global desincentiva la segregación de acceso. | Baja. Igual que B. No hay incentivo económico para mantener el aislamiento por rama. |
| **Incentivo comercial** | Incentiva a mantener usuarios especializados en una sola rama. Desincentiva accesos multi-rama. | Incentiva a dar acceso a todas las ramas ("total, ya pago por ellos"). Riesgo de violar P1. | Fuerte incentivo a dar acceso multi-rama. Riesgo alto de violar P1 (acceso mínimo). |
| **Impacto en accesos temporales** | Un acceso temporal de 2 semanas consume cupo en esa rama. Posible fricción. | Un acceso temporal no afecta al cómputo total. Más flexible. | Igual que B. Los accesos temporales no penalizan. |
| **Ingresos SaaS** | Altos en proyectos multi-rama (cada cruce de rama ingresa extra). Estables en proyectos especializados. | Medios. El tope por proyecto limita el ingreso por cliente. El crecimiento depende de nuevos proyectos. | Medios-altos si el plan tiene techos ajustados. Riesgo de canibalización: un proyecto con 8 usuarios en 3 ramas paga lo mismo que uno con 8 usuarios en 1 rama. |
| **Fricción comercial** | Alta. El comercial debe explicar por qué un usuario cuenta varias veces. Objeciones frecuentes en equipos pequeños. | Baja. Modelo SaaS clásico, sin fricción. El cliente entiende el precio inmediatamente. | Muy baja. "Incluye todas las ramas" es un argumento de venta positivo. |
| **Up-sell** | Neutral. El up-sell viene de necesitar más usuarios en una rama específica ("necesito 2 más en R2"). | Favorable. "Tu proyecto tiene 11 usuarios, necesitas el siguiente plan." Modelo SaaS clásico. | Favorable. El up-sell es natural cuando se alcanza el tope del plan. |
| **Percepción de valor** | Baja-media. El cliente siente que paga por "aire" (usuarios que ya existen pero cuentan doble). | Media-alta. El cliente siente que paga solo por personas reales. | Alta. El cliente siente que "todo está incluido". Fuerte valor percibido. |

### Análisis cruzado por tipo de proyecto

| Tipo de proyecto | Modelo A | Modelo B | Modelo C | Explicación |
|---|---|---|---|---|
| **Producción pequeña (5-8 personas)** | Desfavorable | Favorable | Muy favorable | Equipos pequeños tienden a tener roles multi-rama (el productor también supervisa post). Modelo A penaliza esa colaboración natural. Modelo C es el más cómodo: pagan por pocos usuarios con acceso completo. |
| **Producción mediana (10-20 personas)** | Favorable | Neutral | Favorable | Equipos especializados por departamento. Pocos usuarios cruzan ramas. Modelo A es exacto; Modelo C da un colchón que el cliente agradece sin que CID pierda ingreso significativo. |
| **Producción grande (20+ personas)** | Muy favorable | Desfavorable | Neutral | Departamentos grandes y especializados. Modelo A evita que una rama con muchos usuarios encarezca las demás. Modelo C requeriría planes con techos muy altos o Enterprise. |
| **Postproducción intensiva** | Desfavorable | Favorable | Muy favorable | Muchos roles en R3 (montador, sonido, VFX, color). Modelo A penaliza al concentrar usuarios en una sola rama. Modelo C evita esa penalización. |
| **Producción con multiplataforma** | Favorable | Neutral | Favorable | Distribución y comercialización requieren muchos usuarios en Comercialización. Modelo A aísla ese coste. Modelo C da flexibilidad sin pérdida de ingreso significativa. |
| **Series (TV/streaming, 5-15 personas estables + picos puntuales)** | Desfavorable | Favorable | Muy favorable | Las series tienen equipos reducidos y estables que cruzan varias ramas a lo largo de la producción (preproducción, rodaje, post). El mismo equipo pasa de R2 a R3. Modelo A penaliza ese ciclo natural. Modelo C es el más adecuado: pocos usuarios estables con acceso a las ramas que necesiten en cada fase. |

### Matriz de decisión

| Criterio de evaluación | Peso | Modelo A | Modelo B | Modelo C |
|---|---|---|---|---|
| **Simplicidad** (implementación + facturación) | 20% | 5/10 | 9/10 | 9/10 |
| **Escalabilidad** (proyectos grandes y multi-rama) | 20% | 8/10 | 6/10 | 5/10 |
| **Ingresos SaaS** (potencial de monetización) | 20% | 8/10 | 6/10 | 7/10 |
| **Percepción de valor** (facilidad de explicar y vender) | 25% | 4/10 | 8/10 | 9/10 |
| **Fricción comercial** (objeciones y necesidad de educación) | 15% | 4/10 | 8/10 | 9/10 |
| **Puntuación ponderada** | 100% | **5.8/10** | **7.4/10** | **7.8/10** |

### Impacto por perfil de cliente

| Perfil | Impacto con Modelo A | Impacto con Modelo C |
|---|---|---|
| **Productora pequeña independiente** | Negativo. Un equipo de 6 personas que colabora en 2-3 ramas paga como si fueran 10-12. Frustración y posible abandono. | Positivo. Paga por 6 y todos acceden a lo que necesitan. El producto cubre su necesidad real. |
| **Productora mediana estable** | Neutro-positivo. Departamentos definidos. 12 personas en ~14 cómputos. El coste extra es marginal y se entiende como parte del modelo. | Positivo. Paga por 12 sin necesidad de gestionar límites por rama. Más sencillo de administrar. |
| **Serie TV (8-12 personas estables)** | Negativo. El mismo equipo operativo cruza ramas en cada fase productiva. Pagaría 15-18 cómputos por 10 personas. | Muy positivo. 10 personas, un plan, sin preocuparse por cambios de fase. Ideal para el ciclo de serie. |
| **Producción grande (+30 personas)** | Positivo. Los departamentos son estancos y grandes. Cada rama paga lo suyo sin cross-subsidio. | Neutro-negativo. Un plan con 30 usuarios se queda corto si hay 20 en R2, 10 en R1, 8 en R3. Forzaría Enterprise. |
| **Productora especializada en postproducción** | Negativo. Concentración de usuarios en R3. Penalización severa. Modelo A inviable para este perfil. | Muy positivo. Todos los usuarios en la rama que necesiten, sin coste extra. |

### Recomendación

**RECOMENDACIÓN FINAL: Modelo C (usuarios incluidos por plan + acceso multi-rama ilimitado) como modelo base para todos los planes, combinado con un sistema de techos por rama opcional para Enterprise.** Esta recomendación modifica la sección §10 en lo relativo a la regla de cómputo: se reemplaza "cómputo por rama" por "cómputo por proyecto con multi-rama ilimitado".

Fundamentos:

1. **Ventaja comercial decisiva.** Modelo C elimina la principal objeción comercial (el "doble cómputo") y transforma el límite en una conversación sobre el tamaño del equipo, no sobre su estructura organizativa. La percepción de valor es muy superior.

2. **Simplicidad operativa.** Sin lógica de contabilidad por rama, la implementación es más rápida y barata. El sistema solo necesita contar usuarios activos en el proyecto.

3. **Alineación con el comportamiento real.** Los datos de producción real muestran que los equipos multidisciplinarios pequeños y las series son el segmento de mayor crecimiento. Modelo C los captura sin fricción.

4. **Protección del acceso mínimo necesario (P1).** El riesgo de que el productor dé acceso multi-rama indiscriminado se mitiga con diseño UX (flujo de invitación que pregunta "¿qué rama necesita este usuario?") y con la configuración de visibilidad por rama (§11), que limita lo que cada rol ve aunque tenga acceso multi-rama.

5. **Impacto en ingresos.** La pérdida de ingreso por cómputo multi-rama se compensa con:
   - Mayor tasa de conversión (menos objeciones).
   - Menor churn en productoras pequeñas y series.
   - Up-sell natural al crecer el equipo (no la estructura de ramas).
   - Planes Enterprise con techos por rama opcionales para proyectos grandes.

#### Modificaciones a §10 derivadas de esta recomendación

| Regla actual (§10) | Cambio propuesto |
|---|---|
| Cómputo por rama. Un usuario en N ramas cuenta N veces. | Cómputo por proyecto. Un usuario en N ramas cuenta 1 vez. |
| Techos simétricos (3/5/10 por rama). | Techos globales: 9 (Starter), 15 (Pro), 30 (Studio), 50 (Premium). Enterprise configurable. |
| Productor Propietario y Ejecutivo no computan. | Sin cambio. Se mantiene. |
| Período de gracia de 30 días en downgrade. | Sin cambio. Se mantiene. |
| — (nuevo) | Límites recomendados de usuarios por rama como guía UX (no como restricción de facturación): 3 (Starter), 5 (Pro), 10 (Studio), 15 (Premium). El sistema puede sugerir al Productor que no supere estos límites, pero no bloqueará la invitación. |

#### Riesgos de la recomendación

| Riesgo | Descripción | Severidad | Mitigación |
|---|---|---|---|
| **R1 — Canibalización de ingresos en equipos multi-rama** | Un proyecto que antes pagaba 18 cómputos (6 usuarios × 3 ramas) ahora paga 6. Pérdida de ingreso por cliente. | Alta | Compensar con precios de plan ligeramente superiores (ej. Pro de $X a $X+20%). El valor percibido lo justifica. |
| **R2 — Saturación de rama en planes fijos** | Un proyecto con 20 usuarios en R1 y 2 en R2 agota el plan Studio (30) sin que R2 justifique el upgrade. | Media | En el plan Studio, añadir un cargo adicional por "exceso de usuarios en una sola rama" si supera el 80% del total. Enterprise no tiene este problema. |
| **R3 — Percepción de injusticia en proyectos especializados** | Un proyecto con 15 usuarios en R1 y 1 en R3 paga lo mismo que uno con 8 en cada rama. Sensación de que "los departamentos pequeños subsidian a los grandes". | Baja | No mitigar activamente. Es una percepción interna del cliente, no un problema de facturación. El valor del producto (todo incluido) lo justifica. |
| **R4 — Riesgo de abuso de acceso multi-rama** | El Productor asigna a todos los usuarios acceso a todas las ramas "porque ya está pagado", violando el principio de acceso mínimo necesario. | Media | Mitigación UX: al invitar, el flujo pregunta "¿a qué rama necesita acceder?" con selección obligatoria. La opción "todas las ramas" existe pero requiere confirmación explícita. Auditoría registra concesiones multi-rama. |
| **R5 — Migración de clientes existentes** | Clientes en Modelo A (cómputo por rama) que al migrar a Modelo C dejen de pagar por usuarios multi-rama. Caída de ingresos en clientes actuales. | Alta | Ofrecer migración voluntaria con un mínimo de 3 meses de ingreso promedio garantizado. Los nuevos clientes entran directamente con Modelo C. |

#### Conclusión

Modelo C gana en simplicidad, percepción de valor y fricción comercial. Pierde en escalabilidad pura para proyectos muy grandes, pero ese segmento se resuelve con Enterprise y acuerdos personalizados. Para el mercado objetivo de CID (productoras pequeñas, medianas y series), Modelo C es claramente superior a Modelo A y marginalmente mejor que Modelo B por su percepción de valor y facilidad de venta.

**Decisión:** Cambiar el modelo de cómputo de A (por rama) a C (incluidos por plan + multi-rama ilimitado) como base de §10, manteniendo la opción de techos por rama para Enterprise.

---

## Anexo A — Flujos de acceso

### A.1 Flujo de invitación

```
Productor Propietario
       │
       ▼
Panel de miembros → "Invitar usuario"
       │
       ▼
Introducir email + seleccionar rol
       │
       ▼
Verificar límite de licencia del proyecto
       │
       ├── ¿Hay capacidad en el proyecto? → Enviar invitación
       │                       │
       │                       ▼
       │                  Usuario recibe email
       │                       │
       │                       ▼
       │                  Usuario acepta
       │                       │
       │                       ▼
       │                  Acceso ACTIVO
       │
       └── ¿Sin capacidad en el proyecto? → Notificar al Productor
                              ├── "Haz upgrade de plan"
                              └── "Revoca a otro usuario primero"
```

### A.2 Flujo de revocación

```
Productor Propietario
       │
       ▼
Panel de miembros → Seleccionar usuario
       │
       ▼
"Revocar acceso"
       │
       ▼
Confirmar revocación (con motivo)
       │
       ▼
El sistema:
  1. Revoca el acceso inmediatamente
  2. El usuario pierde acceso en su siguiente solicitud
  3. Se registra el evento en auditoría
  4. Se notifica al usuario por email
  5. Se libera el cupo de licencia del proyecto
       │
       ▼
Usuario pasa a estado REVOCADO
```

### A.3 Flujo de cambio de rol

```
Productor Propietario
       │
       ▼
Panel de miembros → Seleccionar usuario
       │
       ▼
"Cambiar rol"
       │
       ▼
Seleccionar nuevo rol
       │
       ▼
El sistema verifica:
  - ¿El nuevo rol es compatible con el plan actual?
  - ¿El nuevo rol cambia la rama principal del usuario?
  - ¿El plan tiene capacidad en el proyecto?
       │
       ├── Válido → Aplicar cambio
       │              │
       │              ▼
       │          1. Se actualiza el rol
       │          2. Se actualizan los accesos a ramas
       │          3. Se registra en auditoría
       │          4. Se notifica al usuario
       │
       └── Inválido → Mostrar error al Productor
                       ├── "El plan no soporta este rol en esta rama (acceso mínimo necesario)"
                       └── "No hay capacidad disponible en el proyecto"
```

### A.4 Flujo de transferencia de propiedad

```
Productor Propietario (actual)
       │
       ▼
Panel de proyecto → "Transferir propiedad"
       │
       ▼
Seleccionar nuevo propietario (debe ser miembro ACTIVO)
       │
       ▼
Confirmar transferencia
       │
       ▼
El sistema:
  1. El nuevo propietario acepta la transferencia
  2. El propietario anterior pasa a ser Productor Ejecutivo
  3. El nuevo propietario obtiene todas las capacidades de Productor Propietario
  4. El anterior pierde la capacidad de invitar/revocar
  5. Se registra en auditoría
  6. Se notifica a todos los miembros del proyecto
```

### A.5 Flujo de solicitud de acceso excepcional

```
Usuario (sin acceso a una rama)
       │
       ▼
Intenta acceder a módulo sin permiso
       │
       ▼
Pantalla de "Acceso restringido"
       │
       ▼
"Solicitar acceso al Productor"
       │
       ▼
El Productor Propietario recibe notificación
       │
       ▼
Productor evalúa y decide:
       │
       ├── Concede acceso permanente → Se actualiza assignedBranchIds
       │                                   Se registra en auditoría
       │
       ├── Concede acceso temporal → Define fecha de caducidad
       │                                Se actualiza assignedBranchIds + expiresAt
       │                                Se registra en auditoría
       │
       └── Deniega → Se notifica al usuario
                      Se registra la solicitud denegada en auditoría
```

---

## Anexo B — Resumen de capacidades por rol

| Rol | Invitar | Revocar | Cambiar roles | Ver todo | Acceso completo por rama | Auditoría |
|---|---|---|---|---|---|---|
| Productor Propietario | Sí | Sí (excepto sí mismo) | Sí (excepto sí mismo) | Sí | Todas | Sí |
| Productor Ejecutivo | Sí (R1 + Comercial) | Sí (solo invitados por él) | Sí (solo R1) | Sí (lectura) | R1 + Comercial | No |
| Jefe de Producción | No | No | No | No | R1 | No |
| Director | No | No | No | No | R2 | No |
| Guionista | No | No | No | No | R2 (guion) | No |
| Script Supervisor | No | No | No | No | R2 (continuidad) | No |
| Ayudante de Dirección | No | No | No | No | R2 (rodaje) | No |
| Montador / Editor | No | No | No | No | R3 (montaje) | No |
| Editor de Sonido | No | No | No | No | R3 (sonido) | No |
| Post Supervisor | No | No | No | No | R3 | No |
| Distribuidor | No | No | No | No | Comercialización | No |
| Agente de Ventas | No | No | No | No | Comercialización (ventas) | No |

---

## Anexo C — Riesgos de implementación

| Riesgo | Descripción | Severidad | Probabilidad | Mitigación |
|---|---|---|---|---|
| **R1 — Modelo insuficiente para desarrollo** | El modelo de acceso no proporciona suficiente detalle para implementar un sistema de permisos real | Alta | Media | La próxima fase (REVIEW) debe identificar carencias |
| **R2 — Límites de licencia ambiguos** | La definición de "límite de licencia" puede ser ambigua si los usuarios están distribuidos en múltiples ramas | Media | Alta | Documentar que un usuario en N ramas cuenta 1 vez (Modelo C: cómputo por proyecto, multi-rama ilimitado) |
| **R3 — Flujo de invitación incompleto** | No se definen flujos para invitaciones masivas, integración con directorio corporativo, o SCIM | Baja | Alta | Añadir en fase Enterprise |
| **R4 — Periodo de gracia de 30 días** | El periodo de gracia para excedentes puede ser explotado para mantener acceso sin pagar | Media | Media | Limitar a una vez por proyecto; reiniciar si se hace upgrade |
| **R5 — Conflictos con el modelo de datos existente** | Las entidades User, Role, Branch del modelo de datos pueden no alinearse con este modelo de acceso | Alta | Media | Validar alineación en la revisión cruzada de documentos |
| **R6 — Sin definición de SSO/SCIM** | Empresas Enterprise requerirán integración con directorio activo | Media | Alta | Documentar como requisito futuro en la fase Enterprise |
| **R7 — Roles secundarios no desarrollados** | El concepto de roles secundarios existe en el modelo de datos pero no tiene flujo definido aquí | Media | Media | Añadir flujo de asignación de roles secundarios en fase Studio+ |

---

## Historial de revisiones

| Fecha | Versión | Cambios |
|---|---|---|
| 2026-06-02 | 1.0 | Creación inicial del modelo funcional de acceso con 12 secciones, matriz de permisos, flujos de invitación/revocación/cambio de rol/transferencia/solicitud, y 4 planes de licencia. |
| 2026-06-03 | 1.1 | Añadido plan Premium (§10). Migrado Anexo C R2 a Model C (cómputo por proyecto). Unificados estados de proyecto con D2 (§6). Rama 3 actualizada a "Postproducción y Entrega". |
