# AILink/CID Production Finance Control Excel Template Spec v1

Fase: `AILINK.CID.PRODUCTION_FINANCE_CONTROL.EXCEL.TEMPLATE.SPEC.PHASE3`
Fecha: 2026-06-13
Tipo: especificación documental y test-only

Último HEAD estable conocido: `3cdd5c5`.
Último tag estable conocido: `ailink-cid-dev-stable-production-finance-control-model-contract-phase2-20260613`.
Etiqueta de seguridad: No runtime changes.

Nota obligatoria: Esta fase es conceptual/documental. No representa producto disponible. No representa funcionalidad implementada. No genera Excel real. No crea archivo `.xlsx`. No es contrato API ni esquema de base de datos.
Contrato conceptual, no esquema de base de datos ni contrato API.

## 1. Propósito de la plantilla

La plantilla es un reporte financiero editable y revisable, pensado para Excel,
Numbers y Google Sheets mediante un `.xlsx` futuro. Su función es organizar
control financiero de producción audiovisual con trazabilidad documental y
revisión humana.

Excel editable es el formato conceptual de salida previsto para esta plantilla.

No sustituye asesoría, gestoría, contabilidad oficial ni revisión humana. No es
software fiscal certificado. No declara cumplimiento legal automático. No
ejecuta pagos reales.

no es software fiscal certificado.
no declara cumplimiento legal automático.

La plantilla se entiende como diseño conceptual de salida tabular y analítica,
no como plantilla generada ni como archivo real.

## 2. Encaje de producto

`AILink Production Finance Control`:

- herramienta independiente local-first futura;
- orientada a control financiero asistido;
- permite una salida editable para uso documental.

`CID Production Finance Control`:

- futuro módulo dentro de `CID Production Intelligence`;
- encajado con producción, presupuesto, proveedores, personal, contratos y
  delivery;
- separado de AILink Sync Dialogue;
- separado de CID AI Jobs, credit ledger, billing, worker mock, frontend actual
  y PostgreSQL actual.

## 3. Separación de capas

Esta fase separa claramente:

- diseño conceptual de plantilla;
- implementación real futura;
- generación real de Excel;
- importación CSV/PDF;
- OCR;
- conciliación bancaria real;
- PWA.

Nada de lo anterior está implementado en esta fase.

## 4. Hojas previstas

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
- Glosario.

## 5. Resumen ejecutivo

KPIs conceptuales:

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

Texto ejecutivo final:

- resumen;
- tendencias;
- desviaciones;
- necesidades de caja;
- recomendaciones.

## 6. Movimientos

Tabla maestra conceptual de movimientos financieros.

Columnas mínimas:

- movement_id;
- project_id;
- tipo_movimiento;
- fecha;
- periodo;
- entidad;
- documento_asociado;
- categoría;
- subcategoría;
- base;
- IVA;
- retención;
- total;
- moneda;
- estado;
- vencimiento;
- pagado_cobrado;
- pendiente;
- confianza_extracción;
- revisión_humana;
- alertas;
- notas.

## 7. Ingresos

Columnas:

- income_id;
- project_id;
- fecha;
- número_documento;
- pagador;
- NIF/CIF;
- concepto;
- categoría_ingreso;
- base;
- IVA repercutido;
- retención;
- total;
- fecha_prevista_cobro;
- fecha_real_cobro;
- estado_cobro;
- documento_origen;
- confianza_extracción;
- revisión_humana;
- alertas;
- notas.

## 8. Gastos

Columnas:

- expense_id;
- project_id;
- fecha;
- número_documento;
- proveedor;
- NIF/CIF;
- concepto;
- categoría_gasto;
- base_imponible;
- IVA soportado;
- retención;
- total;
- vencimiento;
- estado_pago;
- documento_origen;
- confianza_extracción;
- revisión_humana;
- alertas;
- notas.

## 9. Contratos

Columnas:

- contract_id;
- project_id;
- tipo_contrato;
- parte;
- NIF/CIF;
- fecha_firma;
- fecha_inicio;
- fecha_fin;
- importe_total;
- moneda;
- hitos_pago_cobro;
- estado;
- documento_origen;
- relación_con_factura;
- relación_con_pago_cobro;
- revisión_humana;
- alertas;
- notas.

## 10. Nóminas

Columnas:

- payroll_id;
- project_id;
- trabajador;
- DNI/NIE;
- puesto;
- departamento;
- periodo;
- bruto;
- retenciones;
- coste_empresa;
- neto;
- fecha_pago;
- estado_pago;
- documento_asociado;
- revisión_humana;
- alertas;
- notas.

La hoja no es motor de nóminas.

## 11. Asesoría y obligaciones

Columnas:

- obligation_id;
- project_id;
- obligación;
- periodo;
- responsable;
- fecha_límite;
- documento_relacionado;
- importe;
- estado;
- fecha_envío_asesoría;
- fecha_confirmación_asesoría;
- observaciones.

La hoja no sustituye presentación fiscal ni asesoría.

## 12. Conciliación bancaria

Columnas:

- reconciliation_id;
- bank_line_id;
- fecha_banco;
- concepto_banco;
- importe_banco;
- cuenta;
- posible_documento_asociado;
- entidad_asociada;
- confianza_match;
- estado_conciliación;
- alerta;
- revisión_humana;
- notas.

Esta fase no implementa conciliación bancaria real.

## 13. Presupuesto vs real

Columnas:

- categoría;
- presupuesto_aprobado;
- gasto_real;
- comprometido;
- pendiente_pago;
- desviación_euros;
- desviación_porcentaje;
- porcentaje_consumido;
- semáforo;
- notas.

## 14. Cashflow

Columnas:

- semana;
- ingresos_previstos;
- ingresos_cobrados;
- gastos_previstos;
- gastos_pagados;
- saldo_semanal;
- saldo_acumulado;
- necesidad_de_caja;
- alertas.

Incluye evolución semanal de ingresos, gastos y saldo acumulado.

## 15. Proveedores y pagadores

La plantilla incluye hojas de referencia para:

- Proveedores.
- Pagadores.

Estas hojas ayudan a rankings, control repetido, alertas y revisión humana.

## 16. Personal

La plantilla incluye hoja de referencia para:

- Personal.

Sirve para vincular nóminas, contratos, costes y alertas.

## 17. Vencimientos

La plantilla incluye:

- Vencimientos de pago.
- Vencimientos de cobro.

Estas vistas apoyan caja, alertas y revisión humana.

## 18. Alertas

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

## 19. Revisión manual

Columnas:

- review_id;
- entidad_afectada;
- campo_dudoso;
- valor_detectado;
- confianza;
- corrección_humana;
- usuario_revisor_conceptual;
- estado_revisión;
- comentario;
- fecha_revisión_conceptual.

La revisión manual es obligatoria cuando la confianza es baja o hay alerta.

## 20. Evidencias

Columnas:

- evidence_id;
- entidad_relacionada;
- archivo_origen;
- hash_documento_conceptual;
- fecha_importación_conceptual;
- estado_documento;
- notas.

La hoja mantiene trazabilidad documental.

## 21. Configuración

Listas conceptuales:

- categorías de gasto;
- categorías de ingreso;
- estados;
- monedas;
- departamentos;
- tipos de contrato;
- tipos de obligación;
- umbrales de alerta;
- periodo de producción.

## 22. Glosario

La hoja de glosario aclara:

- términos financieros;
- estados;
- siglas;
- categorías;
- criterios de revisión;
- criterios de alerta.

## 23. Gráficos conceptuales

- gasto por categoría;
- ingresos por categoría;
- evolución semanal de gasto;
- evolución semanal de ingresos;
- cashflow acumulado;
- ranking de proveedores;
- ranking de pagadores;
- presupuesto vs real;
- alertas por gravedad.

## 24. Validaciones conceptuales

- importes numéricos;
- fechas válidas;
- vencimientos no anteriores sin alerta;
- categorías desde lista;
- estados desde lista;
- moneda desde lista;
- NIF/CIF opcional pero recomendado;
- documento_origen recomendado;
- revisión humana obligatoria si confianza es baja.

## 25. Fórmulas conceptuales

- total = base + IVA - retención;
- pendiente = total - pagado_cobrado;
- resultado_neto = ingresos_totales - gastos_totales;
- desviación = presupuesto_aprobado - gasto_real;
- porcentaje_consumido = gasto_real / presupuesto_aprobado;
- saldo_semanal = ingresos_cobrados - gastos_pagados;
- saldo_acumulado = saldo_acumulado_anterior + saldo_semanal.

## 26. No-goals

- No generar Excel real.
- No generar `.xlsx`.
- No implementar fórmulas reales.
- No implementar gráficos reales.
- No implementar OCR.
- No importar PDF.
- No importar CSV.
- No implementar conciliación bancaria real.
- No ejecutar pagos reales.
- No tocar billing runtime.
- No tocar pasarelas, Stripe ni checkout.
- No software fiscal certificado.
- No cumplimiento legal automático.
- No motor de nóminas.
- No sustituir asesoría.
- No runtime changes.

## 27. Criterios de aceptación

- Documento creado en
  `docs/product/finance/ailink_cid_production_finance_control_excel_template_spec_v1.md`.
- Test creado en
  `tests/unit/test_ailink_cid_production_finance_control_excel_template_spec.py`.
- La fase queda estrictamente documental/test-only.
- No genera Excel real.
- No crea archivo `.xlsx`.
- No runtime changes.
- No es contrato API ni esquema de base de datos.
