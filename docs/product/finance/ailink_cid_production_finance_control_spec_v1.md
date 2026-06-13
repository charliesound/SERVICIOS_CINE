# AILink/CID Production Finance Control Spec v1

Fase: `AILINK.CID.PRODUCTION_FINANCE_CONTROL.SPEC.PHASE1`
Fecha: 2026-06-13
Tipo: especificación documental y test-only

Último HEAD estable conocido: `5256f76`.
Último tag estable conocido: `ailink-cid-dev-stable-sync-dialogue-product-guard-smoke-phase4-1-20260613`.
Etiqueta de seguridad: No runtime changes.

Nota de vigencia: Esta fase es conceptual/documental; no representa un producto disponible ni una funcionalidad implementada.

## 1. Nombre provisional

- `AILink Production Finance Control`: posible herramienta independiente
  local-first futura.
- `CID Production Finance Control`: futuro módulo dentro de `CID Production Intelligence`.

Ambos nombres son provisionales y no autorizan implementación runtime.

## 2. Propósito

Production Finance Control es control financiero asistido y revisable para
producción audiovisual. Su objetivo es preparar, organizar y revisar información
financiera de una producción: ingresos, gastos, contratos, nóminas, asesoría,
pagos, cobros, presupuesto vs real, cashflow y conciliación bancaria.

En esta especificación, “pagos” se refiere al control documental/financiero de pagos de producción: vencimientos, estados, evidencias y revisión manual. No se refiere a pasarelas de pago, Stripe, checkout, billing runtime ni pagos reales del SaaS.

El reporte resultante debe ser editable y revisable. No sustituye a la asesoría,
gestoría, contabilidad oficial ni revisión humana. No debe presentarse como
software fiscal certificado, no debe declarar cumplimiento legal automático y no
debe emitir una fiscal certification claim.

La propuesta se centra en trazabilidad documental, preparación de información,
control interno, evidencias y revisión humana obligatoria.

## 3. Encaje en AILinkCinema y CID

Encaje AILinkCinema:

- `AILink Production Finance Control` puede evolucionar como herramienta
  independiente local-first.
- La primera versión conceptual debe trabajar con documentos y datos ficticios o
  controlados.
- La privacidad documental es obligatoria.

Encaje CID:

- `CID Production Finance Control` puede ser un futuro módulo dentro de `CID Production Intelligence`.
- Su relación futura puede incluir plan de rodaje, partes de producción,
  presupuesto, proveedores, personal, contratos y delivery.
- No debe tocar CID SaaS actual.
- No debe tocar CID AI Jobs, credit ledger, billing, worker mock, frontend actual
  ni PostgreSQL actual.
- No debe mezclarse con AILink Sync Dialogue.

## 4. Flujo audiovisual cubierto

La especificación se alinea con el flujo general de producción audiovisual:

1. Guion.
2. Producción.
3. Rodaje.
4. Partes de producción.
5. Montaje.
6. Distribución.
7. Venta.

La herramienta debe ayudar a conectar evidencias financieras con ese flujo, sin
convertirse en contabilidad oficial ni motor fiscal.

## 5. Principios

- Local-first en la primera herramienta independiente.
- Privacidad documental.
- Revisión humana obligatoria.
- Trazabilidad documental de cada movimiento y evidencia.
- No promises of automatic legal compliance.
- No automatic legal compliance claim.
- No fiscal certification claim.
- No payroll engine claim.
- No asesoría replacement claim.
- No runtime changes.
- No sustituye a la asesoría.
- No sustituye a gestoría, contabilidad oficial ni revisión humana.

## 6. Bloques funcionales

- Ingresos.
- Gastos.
- Facturas recibidas.
- Facturas emitidas.
- Contratos.
- Nóminas y personal.
- Asesoría y obligaciones.
- Pagos.
- Cobros.
- Extractos bancarios.
- Conciliación bancaria.
- Presupuesto vs real.
- Cashflow.
- Alertas.
- Evidencias documentales.
- Revisión manual.

## 7. Campos principales para gastos

- fecha;
- número de documento;
- proveedor;
- NIF/CIF;
- concepto;
- categoría de gasto;
- base imponible;
- IVA soportado;
- retención si aplica;
- total;
- vencimiento;
- estado de pago;
- archivo origen;
- confianza de extracción;
- alertas.

## 8. Campos principales para ingresos

- fecha;
- número de documento;
- pagador o entidad;
- NIF/CIF;
- concepto;
- categoría de ingreso;
- base;
- IVA repercutido si aplica;
- retención si aplica;
- total;
- fecha prevista de cobro;
- fecha real de cobro si existe;
- estado de cobro;
- archivo origen;
- confianza de extracción;
- alertas.

## 9. Contratos

Tipos de contrato contemplados:

- actores;
- técnicos;
- proveedores;
- alquileres;
- localizaciones;
- coproducción;
- distribución;
- cesión de derechos;
- música;
- seguros;
- asesoría.

## 10. Nóminas y personal

Campos previstos:

- trabajador;
- puesto;
- departamento;
- periodo;
- bruto;
- retenciones;
- coste empresa;
- neto;
- fecha de pago;
- estado de pago;
- documento asociado.

Este bloque no es un payroll engine. No calcula nóminas oficiales ni sustituye a
asesoría, gestoría, contabilidad oficial ni revisión humana.

## 11. Asesoría y obligaciones

Áreas previstas:

- nóminas;
- seguros sociales;
- IVA;
- retenciones;
- modelos fiscales;
- altas/bajas;
- cierre contable de producción;
- envío a asesoría;
- confirmación de asesoría.

El objetivo es preparar información y evidencias para revisión, no declarar
cumplimiento legal automático.

## 12. Conciliación bancaria

Casos previstos:

- pagos contra facturas;
- cobros contra ingresos;
- nóminas contra transferencias;
- contratos contra hitos de pago;
- pagos sin documento;
- documentos sin pago;
- importes no coincidentes.

Esta fase no implementa conciliación bancaria real.

## 13. Excel editable futuro

El Excel editable es una salida futura prevista, no una implementación en esta
fase.

Hojas previstas:

- Resumen ejecutivo.
- Movimientos.
- Ingresos.
- Gastos.
- Contratos.
- Nóminas.
- Asesoría y obligaciones.
- Conciliación bancaria.
- Presupuesto vs real.
- Cashflow.
- Proveedores.
- Pagadores.
- Personal.
- Vencimientos de pago.
- Vencimientos de cobro.
- Alertas.
- Revisión manual.
- Evidencias.
- Configuración.

## 14. KPIs

- ingresos totales;
- gastos totales;
- resultado neto;
- presupuesto aprobado;
- gasto real;
- comprometido;
- pendiente de pago;
- pendiente de cobro;
- coste de personal;
- coste de proveedores;
- saldo previsto;
- saldo a 30 días;
- pagos vencidos;
- cobros vencidos;
- contratos pendientes;
- documentos sin conciliar;
- alertas críticas.

## 15. Alertas

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
- baja confianza OCR;
- documento sin revisión.

La alerta de baja confianza OCR es una señal conceptual futura. Esta fase no
implementa OCR.

## 16. Roadmap

1. Spec.
2. Modelo financiero contractual.
3. Plantilla Excel con datos ficticios.
4. Importación CSV/Excel.
5. PDFs con texto.
6. OCR.
7. Captura móvil PWA.
8. Conciliación bancaria.
9. Integración futura en CID SaaS.

Cada paso requiere fase explícita, pruebas propias y revisión de alcance.
Este roadmap es solo roadmap conceptual: OCR, PWA, Excel, PDF y conciliación bancaria no son claim comercial, producto disponible ni disponibilidad actual.

## 17. No-goals

- No implementar código runtime.
- No implementar OCR.
- No implementar app móvil/PWA.
- No implementar Excel real todavía.
- No implementar importación PDF.
- No implementar conciliación bancaria real.
- No emitir facturas oficiales.
- No sustituir asesoría.
- No sustituir gestoría.
- No sustituir contabilidad oficial.
- No sustituir revisión humana.
- No declarar cumplimiento legal automático.
- No tocar CID SaaS actual.
- No tocar AILink Sync Dialogue.
- No tocar CID AI Jobs.
- No tocar credit ledger.
- No tocar billing.
- No tocar pasarelas de pago, pagos reales ni billing runtime.
- No tocar worker mock.
- No tocar frontend actual.
- No tocar PostgreSQL actual.
- No tocar cualquier runtime existente.

## 18. Criterios de aceptación

- Documento creado en
  `docs/product/finance/ailink_cid_production_finance_control_spec_v1.md`.
- Test creado en
  `tests/unit/test_ailink_cid_production_finance_control_spec.py`.
- La fase queda estrictamente documental/test-only.
- No runtime changes.
- No staging, commit, tag ni push.
