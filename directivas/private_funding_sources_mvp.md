# PRIVATE FUNDING SOURCES MVP - DIRECTIVA

## Objetivo
Construir el MVP del módulo de "Fuentes privadas del productor" para definir de forma clara y persistente la brecha de financiación del proyecto (Funding Gap).

## Decisión de producto
- Este bloque NO trata ayudas públicas todavía
- Este bloque NO trata matching todavía  
- Este bloque SÍ trata dinero privado, comprometido o previsto por el productor

## 1. Modelos de datos

### ProjectFundingSource
```python
class ProjectFundingSource(Base):
    __tablename__ = "project_funding_sources"
    __table_args__ = (
        Index("ix_pfs_project_org", "project_id", "organization_id"),
    )
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # enum
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    status: Mapped[str] = mapped_column(String(20), default="projected")  # enum
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### source_type (enum)
- equity
- private_investor
- pre_sale
- minimum_guarantee
- in_kind
- brand_partnership
- loan
- other

### status (enum)
- secured (confirmado, comprometido formalmente)
- negotiating (en negociación activa)
- projected (previsto/proyectado)

## 2. Endpoints Backend

| Método | Endpoint | Descripción |
|--------|---------|-----------|
| GET | /api/projects/{project_id}/funding/private-sources | Lista todas las fuentes privadas del proyecto |
| POST | /api/projects/{project_id}/funding/private-sources | Crea nueva fuente privada |
| PATCH | /api/projects/{project_id}/funding/private-sources/{source_id} | Actualiza fuente existente |
| DELETE | /api/projects/{project_id}/funding/private-sources/{source_id} | Elimina fuente |
| GET | /api/projects/{project_id}/funding/private-summary | Resumen financiero con funding gap |

## 3. Reglas funcionales

### Cálculo de Funding Gap
```
current_funding_gap = total_budget - secured
optimistic_funding_gap = total_budget - (secured + negotiating + projected)
```

### Validaciones
- Proyecto debe tener budget registrado
- fuente cruzada entre tenants NO permitida
- Si se elimina fuente, recalcular resumen automáticamente
- No tocar budget base del proyecto

### Tenant Safety
- Todo ligado a project_id + organization_id
- Tenant B no puede leer ni editar fuentes privadas de A
- Admin solo según reglas actuales
- No romper ownership actual

## 4. Frontend MVP

### UI Requerida
- Tabla o cards de fuentes privadas por proyecto
- CRUD básico (crear, editar, eliminar)
- Resumen superior:
  - Total Budget: [X]
  - Secured: [X]
  - Negotiating: [X]
  - Projected: [X]
  - **Funding Gap (current)**: [X]
  - Funding Gap (optimistic): [X]
- Botón "Guardar" cuando haga falta
- UX simple, clara y estable

### Política de guardado
- Sin autosave agresivo
- Mensajes claros de éxito/fallo
- Reload limpio tras cambios si conviene

## 5. NO hacer todavía

- Ayudas públicas
- Funding matcher automático
- Dossier export
- Billing/tiers
- Reporting avanzado
- Conectores privados externos

## 6. Criterios de aceptación

- [ ] CRUD de fuentes privadas por proyecto funciona
- [ ] Resumen financiero con funding gap responde 200
- [ ] Funding gap se calcula correctamente
- [ ] Tenant B bloqueado de datos de A
- [ ] No regresión en budget/presentation/export/builder
- [ ] UI mínima funcional

## 7. Dependencias

- models/production.py (nuevo modelo)
- routes/project_funding_routes.py (nuevo archivo de rutas)
- services/project_funding_service.py (nuevo servicio)
- schemas/ (nuevos schemas si aplica)
- Frontend: ProjectDetailPage.tsx o página dedicada

## metadata
- created: 2026-04-21
- status: MVP
- owner: fullstack team