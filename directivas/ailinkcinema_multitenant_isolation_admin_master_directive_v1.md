# Master Directive: Multi-Tenant Isolation & Admin Governance

**Estado:** READY FOR CODE
**Versión:** 1.0
**Project:** AILinkCinema
**Prioridad:** Alta (Fundamental para Producción / Multiusuario)

---

## 1. Resumen Ejecutivo
Para pasar de un entorno de "Demo en Casa" a una plataforma SaaS profesional o multi-productora, es imperativo garantizar que los datos de un cliente (Tenant) sean invisibles e inaccesibles para otros. Esta directiva establece los pilares de aislamiento en base de datos, almacenamiento físico de activos (Storage) y la gobernanza administrativa global para la supervisión del sistema.

## 2. Objetivo Exacto
Blindar el acceso a la información mediante un esquema de "Hard Isolation" basado en `organization_id`, segmentar el storage físico por cliente y habilitar el rol de Administrador Global para auditoría y control de uso.

## 3. Identidad de Tenant (Organización)
- **Entidad Raíz:** `Organization` (en `models/core.py`).
- **Identificador Único:** `organization_id` (UUID36).
- **Herencia Obligatoria:** Todos los usuarios pertenecen a una Organización. Todas las entidades operativas (Proyectos, Jobs, Assets, Exports) deben colgar de una Organización, ya sea directamente o por trazabilidad de proyecto.

## 4. Aislamiento de Base de Datos
- **Filtrado en Consultas:** Ninguna ruta de la API (excepto las de Admin) debe devolver registros que no pertenezcan al `organization_id` del usuario autenticado.
- **Entidades a Validar/Extender:** 
    - `Project`, `User`, `ProjectJob`, `JobHistory`, `MediaAsset`, `IngestScan`, `StorageSource` (Ya tienen el campo).
    - `Deliverable`, `Review`, `Narrative`, `Report` (Deben ser auditadas y, si falta, añadir `organization_id` para evitar JOINs costosos en validaciones de propiedad).
- **Ownership Guard:** Las mutaciones (POST, PUT, DELETE) deben validar que el objeto destino pertenece a la organización del solicitante.

## 5. Aislamiento de Storage (File System)
El almacenamiento físico debe seguir una estructura jerárquica que impida el cruce accidental de binarios:
- **Ruta Base:** `/opt/SERVICIOS_CINE/storage/{organization_id}/`
- **Sub-estructura:**
    - `projects/{project_id}/uploads/`: Material bruto subido.
    - `projects/{project_id}/generated/`: Resultados de IA / Renders.
    - `projects/{project_id}/exports/`: ZIPs y PDFs generados.
    - `temp/`: Espacio temporal de procesamiento (debe limpiarse por job).

## 6. Export Ownership & Security
- **Firmas/Tokens:** Los links de descarga de ZIP/PDF deben validar la sesión y el tenant.
- **Imposibilidad Técnica:** Un usuario de la Org A jamás podrá descargar un asset de la Org B, incluso si adivina el UUID del asset, gracias a la validación de nivel de Tenant en el controlador de entrega.

## 7. Visibilidad Admin vs Cliente
- **Rol Cliente (User/Producer):**
    - Vista limitada a su Organización.
    - Metadatos de uso propios.
- **Rol Admin Global:**
    - Dashboard de supervisión.
    - Visualización de "Health" del sistema (workers, colas de jobs globales).
    - Reportes de consumo por organización (Nº de renders, espacio ocupado).
    - Gestión de estados de pago y planes (Lectura de `billing_plan`).

## 8. Base para Billing Futuro
Sin implementar Stripe todavía, se deben dejar listos los siguientes campos en `Organization`:
- `stripe_customer_id`: String (nullable).
- `subscription_status`: Enum (active, trialing, past_due, canceled).
- `usage_counters`: JSON o tabla relacional para trackear cuotas mensuales.

## 9. Criterios de Aceptación
1. Un usuario autenticado no puede listar proyectos de otra organización editando el ID en la URL.
2. Los assets generados se guardan en carpetas nombradas con el UUID de la organización.
3. El Admin puede ver una lista de todas las organizaciones y su actividad reciente.
4. El sistema rechaza cualquier intento de exportación si el proyecto no pertenece al tenant del usuario.

## 10. Riesgos
- **Migration Drift:** El cambio en la estructura de carpetas requiere mover archivos existentes para no romper la compatibilidad actual.
- **Overhead de Query:** Asegurar que los índices en `organization_id` estén presentes en todas las tablas para no penalizar el rendimiento.

## 11. Orden Recomendado de Implementación
1. **Auditoría de Modelos:** Completar el campo `organization_id` en tablas faltantes (`Deliverable`, `Review`).
2. **Refactor de Storage Service:** Actualizar la lógica de generación de rutas para incluir el tenant.
3. **Middleware de Aislamiento:** Implementar una validación centralizada en los controladores de FastAPI para inyectar el filtro de tenant.
4. **Vistas de Admin:** Crear endpoints protegidos para estadísticas globales.

---

## 12. Veredicto
**READY FOR CODE**

> [!CAUTION]
> El aislamiento de datos es la base de la confianza del cliente. No se debe permitir ninguna excepción "por conveniencia" en las validaciones de ownership.
