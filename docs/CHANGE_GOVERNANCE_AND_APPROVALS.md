# Change Governance and Approvals

## Overview

CID now has governance de cambios:
- Proposals no se aplican automáticamente
- Requiere aprobación por rol autorizado
- Trazabilidad de cambios

## Conceptos Clave

### Baseline Aprobada
- Datos oficialmente aprobados
- No se pueden modificar sin nuevo change request

### Cambios Propuestos
- Cambio de guion → change requests
- Cambio de budget → change requests
- Cambio de shotlist → change requests

### Estados
- **proposed**: Cambio propuesto, pendiente de revisión
- **pending_approval**: Pendiente de aprobación
- **approved**: Aprobado, puede aplicarse
- **rejected**: Rechazado
- **applied**: Aplicado al proyecto
- **cancelled**: Cancelado

## Roles que Pueden Aprobar

| Rol | Módulos que puede aprobar |
|-----|---------------------------|
| producer/admin/owner | Todos |
| director | storyboard, shotlist, editorial, script |
| production_manager | shooting_plan, shotlist |
| editor | editorial |

## Flujo de Cambios

1. Se detecta cambio (ej: nuevo guion)
2. Se genera ProjectChangeRequest
3. Muestra en ChangeRequestsPage
4. Productor/Director revisa y aprueba o rechaza
5. Si aprobado, se puede aplicar

## Shotlist y Plan de Rodaje

### PlannedShot
- proposal → approved → shot/not_shot
- essential/recommended/optional

### ShootingPlan
- draft → approved
- Cobertura detecta faltante

### Coverage
- essential missing → warning
- pickups needed → warning
- escenas sin rodar

## API Endpoints

```
GET  /api/projects/{id}/change-requests
POST /api/projects/{id}/change-requests
POST /api/projects/{id}/change-requests/{id}/approve
POST /api/projects/{id}/change-requests/{id}/reject
POST /api/projects/{id}/change-requests/{id}/apply

GET  /api/projects/{id}/planned-shots
POST /api/projects/{id}/planned-shots/generate
POST /api/projects/{id}/planned-shots/{id}/approve
POST /api/projects/{id}/planned-shots/{id}/reject

GET  /api/projects/{id}/shooting-plans
POST /api/projects/{id}/shooting-plans
GET  /api/projects/{id}/shooting-plans/{id}/coverage
```