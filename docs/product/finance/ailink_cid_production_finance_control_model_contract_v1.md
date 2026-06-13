# AILink/CID Production Finance Control Model Contract v1

Fase: `AILINK.CID.PRODUCTION_FINANCE_CONTROL.MODEL.CONTRACT.PHASE2`
Fecha: 2026-06-13
Tipo: contrato documental y test-only

Último HEAD estable conocido: `19a16b7`.
Último tag estable conocido: `ailink-cid-dev-stable-production-finance-control-spec-phase1-20260613`.
Etiqueta de seguridad: No runtime changes.

Nota de vigencia: Esta fase es conceptual/documental; no representa un producto disponible ni una funcionalidad implementada.
Contrato conceptual, no esquema de base de datos ni contrato API.

## 1. Propósito del contrato de modelo

Este contrato define el modelo financiero de Production Finance Control antes de
implementar Excel, OCR, PDF import, CSV import o cualquier runtime. Su función
es fijar entidades, campos, relaciones, estados, invariantes y límites para una
futura herramienta o módulo.

El contrato preserva trazabilidad documental y revisión humana. No sustituye a
asesoría, gestoría, contabilidad oficial ni revisión humana.

## 2. Encaje de producto

`AILink Production Finance Control`:

- posible herramienta independiente local-first futura;
- orientada a control financiero asistido para producción audiovisual;
- trabaja sobre documentación y revisión humana.

`CID Production Finance Control`:

- futuro módulo dentro de `CID Production Intelligence`;
- encajado con plan de rodaje, partes de producción, presupuesto, proveedores,
  personal, contratos y delivery;
- separado de AILink Sync Dialogue;
- separado de CID AI Jobs, credit ledger, billing, worker mock, frontend actual
  y PostgreSQL actual.

## 3. Alcance

El modelo cubre:

- ingresos;
- gastos;
- contratos;
- nóminas;
- asesoría;
- pagos;
- cobros;
- presupuesto vs real;
- cashflow;
- conciliación bancaria;
- alertas;
- evidencias documentales;
- revisión manual.

## 4. Entidades principales

- `ProductionFinanceProject`
- `Budget`
- `BudgetCategory`
- `FinancialMovement`
- `Income`
- `Expense`
- `Contract`
- `InvoiceReceived`
- `InvoiceIssued`
- `PayrollItem`
- `Supplier`
- `Worker`
- `Payer`
- `Payment`
- `Collection`
- `BankStatement`
- `BankStatementLine`
- `ReconciliationMatch`
- `FinancialAlert`
- `DocumentEvidence`
- `ManualReviewItem`

## 5. Campos mínimos compartidos

Campos conceptuales mínimos esperados en el modelo:

- `logical_id`
- `project_id`
- fechas;
- importes;
- moneda;
- estado;
- categoría;
- documento origen;
- confianza de extracción futura;
- revisión humana;
- timestamps conceptuales;
- notas.

Cada entidad puede añadir campos específicos sin perder estos mínimos.

## 6. Campos por entidad

### 6.1 `ProductionFinanceProject`

- `logical_id`
- `project_id`
- nombre del proyecto
- estado del proyecto financiero
- moneda base
- fecha de inicio
- fecha de cierre prevista
- fecha de cierre real
- notas

### 6.2 `Budget`

- `logical_id`
- `project_id`
- fecha de versión
- moneda
- presupuesto aprobado
- gasto previsto
- gasto real
- comprometido
- pendiente de pago
- pendiente de cobro
- saldo previsto
- notas

### 6.3 `BudgetCategory`

- `logical_id`
- `project_id`
- nombre
- tipo
- categoría padre
- moneda
- presupuesto aprobado
- gasto real
- variación
- notas

### 6.4 `FinancialMovement`

- `logical_id`
- `project_id`
- fecha
- tipo de movimiento
- importe
- moneda
- estado
- categoría
- documento origen
- confianza de extracción futura
- revisión humana
- notas

### 6.5 `Income`

- `logical_id`
- `project_id`
- fecha
- número de documento
- pagador o entidad
- NIF/CIF
- concepto
- categoría de ingreso
- base
- IVA repercutido si aplica
- retención si aplica
- total
- fecha prevista de cobro
- fecha real de cobro si existe
- estado de cobro
- documento origen
- confianza de extracción futura
- revisión humana
- notas

### 6.6 `Expense`

- `logical_id`
- `project_id`
- fecha
- número de documento
- proveedor
- NIF/CIF
- concepto
- categoría de gasto
- base imponible
- IVA soportado
- retención si aplica
- total
- vencimiento
- estado de pago
- documento origen
- confianza de extracción futura
- revisión humana
- notas

### 6.7 `Contract`

- `logical_id`
- `project_id`
- tipo de contrato
- parte contratada
- rol
- fecha
- inicio
- fin
- importe
- moneda
- estado
- hitos de pago/cobro
- documento origen
- confianza de extracción futura
- revisión humana
- notas

### 6.8 `InvoiceReceived`

- `logical_id`
- `project_id`
- fecha
- número de factura
- proveedor
- importe
- moneda
- estado
- gasto vinculado
- documento origen
- confianza de extracción futura
- revisión humana
- notas

### 6.9 `InvoiceIssued`

- `logical_id`
- `project_id`
- fecha
- número de factura
- pagador o cliente
- importe
- moneda
- estado
- ingreso vinculado
- documento origen
- confianza de extracción futura
- revisión humana
- notas

### 6.10 `PayrollItem`

- `logical_id`
- `project_id`
- trabajador
- puesto
- departamento
- periodo
- bruto
- retenciones
- coste empresa
- neto
- fecha de pago
- estado de pago
- documento asociado
- revisión humana
- notas

### 6.11 `Supplier`

- `logical_id`
- `project_id`
- nombre
- NIF/CIF
- categoría
- contacto
- estado
- documento origen
- notas

### 6.12 `Worker`

- `logical_id`
- `project_id`
- nombre
- puesto
- departamento
- estado
- documento origen
- notas

### 6.13 `Payer`

- `logical_id`
- `project_id`
- nombre
- NIF/CIF
- categoría
- estado
- documento origen
- notas

### 6.14 `Payment`

- `logical_id`
- `project_id`
- fecha
- importe
- moneda
- método
- estado
- entidad financiera vinculada
- gasto/factura/nómina/contrato vinculado
- documento origen
- revisión humana
- notas

### 6.15 `Collection`

- `logical_id`
- `project_id`
- fecha
- importe
- moneda
- método
- estado
- ingreso/factura emitida/contrato vinculado
- documento origen
- revisión humana
- notas

### 6.16 `BankStatement`

- `logical_id`
- `project_id`
- cuenta
- banco
- periodo
- moneda
- documento origen
- revisión humana
- notas

### 6.17 `BankStatementLine`

- `logical_id`
- `project_id`
- fecha
- descripción
- importe
- moneda
- tipo
- estado
- documento origen
- revisión humana
- notas

### 6.18 `ReconciliationMatch`

- `logical_id`
- `project_id`
- línea bancaria
- entidad financiera concreta
- tipo de coincidencia
- importe
- moneda
- estado
- confianza de extracción futura
- revisión humana
- notas

### 6.19 `FinancialAlert`

- `logical_id`
- `project_id`
- tipo de alerta
- entidad afectada
- severidad
- estado
- documento origen
- revisión humana
- notas

### 6.20 `DocumentEvidence`

- `logical_id`
- `project_id`
- tipo de documento
- archivo origen
- hash o referencia documental
- fecha
- estado
- confianza de extracción futura
- revisión humana
- notas

### 6.21 `ManualReviewItem`

- `logical_id`
- `project_id`
- campo dudoso
- razón
- estado
- responsable
- revisión humana
- fecha de revisión
- resolución
- notas

## 7. Relaciones

- proyecto → presupuesto;
- proyecto → movimientos;
- gasto → proveedor;
- ingreso → pagador;
- contrato → proveedor/trabajador/pagador;
- contrato → hitos de pago/cobro;
- factura recibida → gasto;
- factura emitida → ingreso;
- nómina → trabajador;
- pago → gasto/factura/nómina/contrato;
- cobro → ingreso/factura emitida/contrato;
- extracto bancario → líneas;
- línea bancaria → conciliación;
- documento → evidencia;
- alerta → entidad afectada;
- revisión manual → campo dudoso.

## 8. Estados

Estados admitidos por el contrato:

- draft;
- pending_review;
- reviewed;
- approved;
- pending_payment;
- paid;
- partially_paid;
- overdue;
- cancelled;
- reconciled;
- unmatched;
- disputed.

## 9. Invariantes

- Ningún dato extraído automáticamente se considera definitivo sin revisión
  humana cuando la confianza sea baja.
- Ningún documento financiero debe perder referencia a su archivo origen.
- Un pago bancario conciliado debe apuntar a una entidad financiera concreta.
- Una factura duplicada debe generar alerta, no borrado automático.
- Una nómina no sustituye cálculo laboral oficial.
- Una obligación de asesoría no sustituye presentación fiscal oficial.
- El modelo no emite facturas oficiales.
- El modelo no ejecuta pagos reales.
- El modelo no toca pasarelas, Stripe, checkout ni billing runtime.
- El modelo no avala cumplimiento legal automático.

## 10. Categorías iniciales de gasto

- equipo técnico;
- reparto;
- cámara;
- sonido;
- arte;
- vestuario;
- maquillaje;
- localizaciones;
- transporte;
- catering;
- postproducción;
- VFX;
- música;
- seguros;
- legal;
- administración;
- distribución;
- marketing;
- otros.

## 11. Categorías iniciales de ingreso

- aportación productor;
- coproducción;
- subvención;
- preventas;
- distribución;
- ventas internacionales;
- televisión/plataforma;
- patrocinio;
- product placement;
- crowdfunding;
- inversión privada;
- anticipo;
- otros ingresos.

## 12. Alertas

- factura sin contrato;
- contrato sin factura;
- nómina sin pago;
- pago sin documento;
- ingreso previsto no cobrado;
- cobro sin factura emitida;
- documento duplicado;
- proveedor nuevo;
- trabajador nuevo;
- pagador nuevo;
- fecha fuera de periodo;
- importe raro;
- IVA sospechoso;
- retención sospechosa;
- desviación frente a presupuesto;
- saldo semanal negativo;
- baja confianza OCR futura;
- documento sin revisión.

## 13. Límites

- fase conceptual/documental;
- no producto disponible;
- no funcionalidad implementada;
- no software fiscal certificado;
- no cumplimiento legal automático;
- no motor de nóminas;
- no sustituto de asesoría;
- no pagos reales;
- no billing runtime;
- no OCR;
- no Excel real;
- no PDF import;
- no PWA;
- no conciliación bancaria real.

## 14. Encaje futuro

- Excel template;
- CSV/manual import;
- PDF text import;
- OCR;
- captura móvil PWA;
- conciliación bancaria;
- integración futura en CID Production Intelligence.

Cada una de esas evoluciones requiere fase propia y no está disponible en esta
fase.

## 15. No-goals

- No tocar Docker.
- No tocar Alembic.
- No tocar `.env`.
- No tocar modelos.
- No tocar base de datos / DB.
- No tocar configuración.
- No tocar scripts operativos.
- No implementar código runtime.
- No implementar OCR.
- No implementar Excel.
- No implementar importación PDF.
- No implementar importación CSV.
- No implementar conciliación bancaria real.
- No implementar PWA.
- No crear modelos SQLAlchemy.
- No crear migraciones.
- No tocar pasarelas de pago, pagos reales ni billing runtime.
- No hacer staging, commit, tag ni push.
- No tocar CID SaaS actual.
- No tocar AILink Sync Dialogue.
- No sustituir asesoría, gestoría, contabilidad oficial ni revisión humana.
- No representa una funcionalidad implementada.
- No sustituye a asesoría, gestoría, contabilidad oficial ni revisión humana.

no representa una funcionalidad implementada.
no sustituye a asesoría, gestoría, contabilidad oficial ni revisión humana.

## 16. Criterios de aceptación

- Documento creado en
  `docs/product/finance/ailink_cid_production_finance_control_model_contract_v1.md`.
- Test creado en
  `tests/unit/test_ailink_cid_production_finance_control_model_contract.py`.
- La fase queda estrictamente documental/test-only.
- No runtime changes.
