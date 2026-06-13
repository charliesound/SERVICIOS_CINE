# AILink/CID Production Finance Control Demo Data Contract v1

Fase: `AILINK.CID.PRODUCTION_FINANCE_CONTROL.EXCEL.TEMPLATE.DEMO.DATA.CONTRACT.PHASE4`
Fecha: 2026-06-13
Tipo: contrato documental y test-only

Último HEAD estable conocido: `5caf6aa`.
Último tag estable conocido: `ailink-cid-dev-stable-production-finance-control-excel-template-spec-phase3-20260613`.
Etiqueta de seguridad: No runtime changes.

Nota obligatoria: Esta fase es conceptual/documental. No representa producto disponible. No representa funcionalidad implementada. No genera Excel real. No crea archivo `.xlsx`. No crea archivo `.csv`. No es contrato API ni esquema de base de datos. Los datos son ficticios y solo sirven para demo.

Contrato conceptual, no esquema de base de datos ni contrato API.

## 1. Propósito

Este contrato define datos ficticios de demo para la futura plantilla Excel editable de AILink Production Finance Control. Prepara una demo visual segura para la presentación agosto/septiembre, no usa datos reales, no usa facturas reales, no usa nóminas reales, no usa contratos reales y no usa datos personales reales. No genera Excel real.

Los datos son completamente ficticios y sirven exclusivamente para demostrar cómo se vería la futura plantilla editable con datos controlados.

## 2. Nota obligatoria

- Esta fase es conceptual/documental.
- No representa producto disponible.
- No representa funcionalidad implementada.
- No genera Excel real.
- No crea archivo `.xlsx`.
- No crea archivo `.csv`.
- No es contrato API ni esquema de base de datos.
- Los datos son ficticios y solo sirven para demo.

Los datos no deben interpretarse como datos reales, facturas reales, contratos reales, nóminas reales ni cuentas bancarias reales.

## 3. Proyecto demo ficticio

Definición de la producción ficticia para la demo:

- **Título**: Proyecto Demo Aurora
- **Tipo**: largometraje independiente
- **Periodo de producción**: 8 semanas
- **Moneda**: EUR
- **Presupuesto aprobado**: 250.000 EUR
- **Objetivo de demo**: mostrar ingresos, gastos, contratos, nóminas, cashflow, alertas y revisión humana en una plantilla Excel editable futura.

Proyecto Demo Aurora es un proyecto ficticio que sirve para demostrar el control financiero de producción audiovisual asistido. No se trata de un proyecto real.

## 4. Datos demo de ingresos

Tabla conceptual con 8 ingresos ficticios del Proyecto Demo Aurora:

| income_id | fecha | pagador | categoría_ingreso | concepto | base | IVA repercutido | retención | total | fecha_prevista_cobro | fecha_real_cobro | estado_cobro | revisión_humana | alerta |
|-----------|-------|---------|-------------------|----------|------|-----------------|-----------|-------|----------------------|------------------|--------------|-----------------|--------|
| INC-DEMO-01 | 2026-07-01 | Pagador Demo Productor 01 | aportación productor | aportación capital productor | 50.000 | 10.500 | 1.500 | 59.000 | 2026-07-15 | 2026-07-14 | cobrado | pendiente | ninguna |
| INC-DEMO-02 | 2026-07-05 | Pagador Demo Coproductor 01 | coproducción | coproducción internacional | 40.000 | 8.400 | 1.200 | 47.200 | 2026-08-01 | 2026-07-28 | cobrado | pendiente | ninguna |
| INC-DEMO-03 | 2026-07-10 | Pagador Demo Subvención 01 | subvención | subvención cultural | 30.000 | 0 | 0 | 30.000 | 2026-08-15 | — | pendiente | pendiente | ingreso previsto no cobrado |
| INC-DEMO-04 | 2026-07-15 | Pagador Demo Distribuidor 01 | preventa | preventa territorio nacional | 25.000 | 5.250 | 750 | 29.500 | 2026-09-01 | — | pendiente | pendiente | ingreso previsto no cobrado |
| INC-DEMO-05 | 2026-07-20 | Pagador Demo Plataforma 01 | televisión/plataforma | venta derechos emisión | 20.000 | 4.200 | 600 | 23.600 | 2026-09-15 | — | pendiente | pendiente | cobro sin factura emitida |
| INC-DEMO-06 | 2026-07-25 | Pagador Demo Patrocinador 01 | patrocinio | patrocinio producto | 15.000 | 3.150 | 450 | 17.700 | 2026-08-30 | 2026-08-25 | cobrado | pendiente | ninguna |
| INC-DEMO-07 | 2026-08-01 | Pagador Demo Inversor 01 | inversión privada | inversión privada capital | 35.000 | 7.350 | 1.050 | 41.300 | 2026-09-10 | — | pendiente | pendiente | ingreso previsto no cobrado |
| INC-DEMO-08 | 2026-08-05 | Pagador Demo Distribuidor 02 | anticipo distribución | anticipo distribución internacional | 20.000 | 4.200 | 600 | 23.600 | 2026-09-20 | — | pendiente | pendiente | ingreso previsto no cobrado |

Estos datos son completamente ficticios. No corresponden a facturas reales ni pagos reales.

## 5. Datos demo de gastos

Tabla conceptual con 14 gastos ficticios del Proyecto Demo Aurora:

| expense_id | fecha | proveedor | categoría_gasto | concepto | base_imponible | IVA soportado | retención | total | vencimiento | estado_pago | revisión_humana | alerta |
|------------|-------|-----------|-----------------|----------|----------------|---------------|-----------|-------|-------------|-------------|-----------------|--------|
| EXP-DEMO-01 | 2026-07-01 | Proveedor Demo Cámara 01 | cámara | alquiler equipo de cámara 4K | 8.000 | 1.680 | 240 | 9.440 | 2026-07-31 | pagado | pendiente | ninguna |
| EXP-DEMO-02 | 2026-07-03 | Proveedor Demo Sonido 01 | sonido | equipo de sonido ambiental | 4.000 | 840 | 120 | 4.720 | 2026-07-31 | pagado | pendiente | ninguna |
| EXP-DEMO-03 | 2026-07-05 | Proveedor Demo Arte 01 | arte | decorados y utilería | 6.000 | 1.260 | 180 | 7.080 | 2026-08-15 | pendiente | pendiente | factura sin contrato |
| EXP-DEMO-04 | 2026-07-07 | Proveedor Demo Vestuario 01 | vestuario | vestuario personajes principales | 3.500 | 735 | 105 | 4.130 | 2026-08-10 | pendiente | pendiente | ninguna |
| EXP-DEMO-05 | 2026-07-10 | Proveedor Demo Maquillaje 01 | maquillaje | maquillaje y peluquería | 2.500 | 525 | 75 | 2.950 | 2026-08-05 | pendiente | pendiente | ninguna |
| EXP-DEMO-06 | 2026-07-12 | Proveedor Demo Localización 01 | localizaciones | alquiler plató principal | 10.000 | 2.100 | 300 | 11.800 | 2026-08-20 | pendiente | pendiente | documento duplicado |
| EXP-DEMO-07 | 2026-07-15 | Proveedor Demo Transporte 01 | transporte | furgonetas y desplazamientos | 5.000 | 1.050 | 150 | 5.900 | 2026-08-25 | pendiente | pendiente | ninguna |
| EXP-DEMO-08 | 2026-07-18 | Proveedor Demo Catering 01 | catering | servicio de catering rodaje | 4.500 | 945 | 135 | 5.310 | 2026-08-15 | pagado | pendiente | ninguna |
| EXP-DEMO-09 | 2026-07-20 | Proveedor Demo Postproducción 01 | postproducción | montaje y postproducción | 15.000 | 3.150 | 450 | 17.700 | 2026-09-30 | pendiente | pendiente | desviación frente a presupuesto |
| EXP-DEMO-10 | 2026-07-25 | Proveedor Demo VFX 01 | VFX | efectos visuales | 12.000 | 2.520 | 360 | 14.160 | 2026-10-15 | pendiente | pendiente | importe raro |
| EXP-DEMO-11 | 2026-08-01 | Proveedor Demo Música 01 | música | composición banda sonora | 8.000 | 1.680 | 240 | 9.440 | 2026-09-15 | pendiente | pendiente | ninguna |
| EXP-DEMO-12 | 2026-08-05 | Proveedor Demo Seguros 01 | seguros | seguro de producción | 3.000 | 630 | 90 | 3.540 | 2026-08-20 | pagado | pendiente | ninguna |
| EXP-DEMO-13 | 2026-08-10 | Proveedor Demo Equipo Técnico 01 | equipo técnico | iluminación y grip | 6.500 | 1.365 | 195 | 7.670 | 2026-09-05 | pendiente | pendiente | IVA sospechoso |
| EXP-DEMO-14 | 2026-08-15 | Proveedor Demo Reparto 01 | reparto | cachés actores secundarios | 7.000 | 1.470 | 210 | 8.260 | 2026-09-10 | pendiente | pendiente | retención sospechosa |

Estos datos son completamente ficticios. No corresponden a facturas reales ni proveedores reales.

## 6. Datos demo de contratos

Tabla conceptual con 8 contratos ficticios del Proyecto Demo Aurora:

| contract_id | tipo_contrato | parte | importe_total | fecha_firma | fecha_inicio | fecha_fin | estado | relación_con_factura | relación_con_pago_cobro | alerta |
|-------------|---------------|-------|---------------|-------------|--------------|-----------|--------|---------------------|------------------------|--------|
| CON-DEMO-01 | contrato de actor | Trabajador Ficticio 01 | 15.000 | 2026-06-15 | 2026-07-01 | 2026-08-31 | activo | EXP-DEMO-14 | ninguno | ninguna |
| CON-DEMO-02 | contrato de técnico | Trabajador Ficticio 02 | 10.000 | 2026-06-18 | 2026-07-01 | 2026-08-31 | activo | ninguno | ninguno | contrato sin factura |
| CON-DEMO-03 | alquiler de cámara | Proveedor Demo Cámara 01 | 9.440 | 2026-06-20 | 2026-07-01 | 2026-07-31 | activo | EXP-DEMO-01 | EXP-DEMO-01 | ninguna |
| CON-DEMO-04 | localización | Proveedor Demo Localización 01 | 11.800 | 2026-06-22 | 2026-07-12 | 2026-08-20 | activo | EXP-DEMO-06 | ninguno | factura sin contrato |
| CON-DEMO-05 | música | Proveedor Demo Música 01 | 9.440 | 2026-06-25 | 2026-08-01 | 2026-09-15 | activo | EXP-DEMO-11 | ninguno | ninguna |
| CON-DEMO-06 | seguro | Proveedor Demo Seguros 01 | 3.540 | 2026-06-28 | 2026-08-05 | 2026-08-20 | activo | EXP-DEMO-12 | EXP-DEMO-12 | ninguna |
| CON-DEMO-07 | coproducción | Pagador Demo Coproductor 01 | 47.200 | 2026-06-30 | 2026-07-05 | 2026-09-30 | activo | INC-DEMO-02 | INC-DEMO-02 | ninguna |
| CON-DEMO-08 | distribución | Pagador Demo Distribuidor 01 | 29.500 | 2026-07-01 | 2026-07-15 | 2026-12-31 | activo | INC-DEMO-04 | ninguno | contrato sin factura |

Estos datos son completamente ficticios. No corresponden a contratos reales ni partes reales.

## 7. Datos demo de nóminas

Tabla conceptual con 6 nóminas ficticias del Proyecto Demo Aurora:

| payroll_id | trabajador_ficticio | puesto | departamento | periodo | bruto | retenciones | coste_empresa | neto | fecha_pago | estado_pago | revisión_humana | alerta |
|------------|---------------------|--------|--------------|---------|-------|-------------|---------------|------|------------|-------------|-----------------|--------|
| PAYROLL-DEMO-01 | Trabajador Ficticio 01 | dirección de producción | producción | julio 2026 | 5.000 | 1.250 | 6.000 | 3.750 | 2026-07-31 | pagado | pendiente | ninguna |
| PAYROLL-DEMO-02 | Trabajador Ficticio 02 | ayudante de dirección | producción | julio 2026 | 3.000 | 600 | 3.600 | 2.400 | 2026-07-31 | pagado | pendiente | nómina sin pago |
| PAYROLL-DEMO-03 | Trabajador Ficticio 03 | cámara | técnico | julio 2026 | 3.500 | 770 | 4.200 | 2.730 | 2026-07-31 | pagado | pendiente | ninguna |
| PAYROLL-DEMO-04 | Trabajador Ficticio 04 | sonido | técnico | julio 2026 | 3.200 | 672 | 3.840 | 2.528 | 2026-07-31 | pagado | pendiente | ninguna |
| PAYROLL-DEMO-05 | Trabajador Ficticio 05 | arte | arte | julio 2026 | 2.800 | 532 | 3.360 | 2.268 | 2026-07-31 | pendiente | pendiente | nómina sin pago |
| PAYROLL-DEMO-06 | Trabajador Ficticio 06 | producción | producción | julio 2026 | 2.500 | 450 | 3.000 | 2.050 | 2026-07-31 | pendiente | pendiente | trabajador nuevo |

**Nota**: Esta hoja no es motor de nóminas. No calcula nóminas reales. No genera pagos reales. No sustituye asesoría laboral ni contabilidad oficial. Los datos son completamente ficticios.

## 8. Datos demo de pagos y cobros

Ejemplos ficticios de pagos y cobros:

**Pagos conciliados:**
- EXP-DEMO-01: pago de 9.440 EUR a Proveedor Demo Cámara 01, conciliado con factura.
- EXP-DEMO-08: pago de 5.310 EUR a Proveedor Demo Catering 01, conciliado con factura.
- EXP-DEMO-12: pago de 3.540 EUR a Proveedor Demo Seguros 01, conciliado con factura.

**Pagos pendientes:**
- EXP-DEMO-03: 7.080 EUR pendiente a Proveedor Demo Arte 01.
- EXP-DEMO-09: 17.700 EUR pendiente a Proveedor Demo Postproducción 01.

**Cobros recibidos:**
- INC-DEMO-01: 59.000 EUR cobrado de Pagador Demo Productor 01.
- INC-DEMO-02: 47.200 EUR cobrado de Pagador Demo Coproductor 01.
- INC-DEMO-06: 17.700 EUR cobrado de Pagador Demo Patrocinador 01.

**Cobros previstos:**
- INC-DEMO-03: 30.000 EUR previsto de Pagador Demo Subvención 01.
- INC-DEMO-04: 29.500 EUR previsto de Pagador Demo Distribuidor 01.

**Pago sin documento:**
- Pago de 1.200 EUR a Proveedor Demo Varios 01, sin factura asociada.

**Ingreso previsto no cobrado:**
- INC-DEMO-07: 41.300 EUR previsto de Pagador Demo Inversor 01, no cobrado.

No ejecutar pagos reales. Todos los datos son ficticios.

## 9. Datos demo de conciliación bancaria

Tabla conceptual con 8 líneas bancarias ficticias:

| bank_line_id | fecha_banco | concepto_banco | importe_banco | posible_documento_asociado | entidad_asociada | confianza_match | estado_conciliación | alerta |
|--------------|-------------|----------------|---------------|---------------------------|------------------|-----------------|---------------------|--------|
| BANK-DEMO-01 | 2026-07-14 | transferencia productor | 59.000 | INC-DEMO-01 | Pagador Demo Productor 01 | alta | conciliado | ninguna |
| BANK-DEMO-02 | 2026-07-28 | transferencia coproductor | 47.200 | INC-DEMO-02 | Pagador Demo Coproductor 01 | alta | conciliado | ninguna |
| BANK-DEMO-03 | 2026-07-31 | pago alquiler cámara | -9.440 | EXP-DEMO-01 | Proveedor Demo Cámara 01 | alta | conciliado | ninguna |
| BANK-DEMO-04 | 2026-08-01 | transferencia subvención | 30.000 | INC-DEMO-03 | Pagador Demo Subvención 01 | baja | pendiente | baja confianza OCR futura |
| BANK-DEMO-05 | 2026-08-05 | pago catering | -5.310 | EXP-DEMO-08 | Proveedor Demo Catering 01 | alta | conciliado | ninguna |
| BANK-DEMO-06 | 2026-08-10 | transferencia desconocida | 8.500 | ninguno | ninguno | baja | pendiente | pago sin documento |
| BANK-DEMO-07 | 2026-08-15 | pago seguro | -3.540 | EXP-DEMO-12 | Proveedor Demo Seguros 01 | alta | conciliado | ninguna |
| BANK-DEMO-08 | 2026-08-20 | transferencia patrocinador | 17.700 | INC-DEMO-06 | Pagador Demo Patrocinador 01 | media | pendiente | baja confianza OCR futura |

**Nota**: Esta fase no implementa conciliación bancaria real. No accede a cuentas bancarias reales. No ejecuta conciliación automática. Los datos son completamente ficticios.

## 10. Datos demo de presupuesto vs real

Tabla conceptual por categoría:

| categoría | presupuesto_aprobado | gasto_real | comprometido | pendiente_pago | desviación_euros | desviación_porcentaje | semáforo |
|-----------|---------------------|------------|--------------|----------------|------------------|----------------------|----------|
| cámara | 20.000 | 9.440 | 0 | 0 | 10.560 | 52,8% | verde |
| sonido | 10.000 | 4.720 | 0 | 0 | 5.280 | 52,8% | verde |
| arte | 15.000 | 7.080 | 0 | 7.080 | 7.920 | 52,8% | verde |
| localizaciones | 12.000 | 11.800 | 0 | 11.800 | 200 | 1,7% | amarillo |
| transporte | 8.000 | 5.900 | 0 | 5.900 | 2.100 | 26,3% | verde |
| catering | 6.000 | 5.310 | 0 | 0 | 690 | 11,5% | verde |
| postproducción | 15.000 | 17.700 | 0 | 17.700 | -2.700 | -18% | rojo |
| seguros | 4.000 | 3.540 | 0 | 0 | 460 | 11,5% | verde |
| VFX | 10.000 | 14.160 | 0 | 14.160 | -4.160 | -41,6% | rojo |
| música | 8.000 | 9.440 | 0 | 9.440 | -1.440 | -18% | rojo |
| vestuario | 5.000 | 4.130 | 0 | 4.130 | 870 | 17,4% | verde |
| maquillaje | 4.000 | 2.950 | 0 | 2.950 | 1.050 | 26,3% | verde |
| equipo técnico | 8.000 | 7.670 | 0 | 7.670 | 330 | 4,1% | verde |
| reparto | 10.000 | 8.260 | 0 | 8.260 | 1.740 | 17,4% | verde |

## 11. Datos demo de cashflow

Tabla conceptual con 8 semanas del Proyecto Demo Aurora:

| semana | ingresos_previstos | ingresos_cobrados | gastos_previstos | gastos_pagados | saldo_semanal | saldo_acumulado | necesidad_de_caja | alerta |
|--------|-------------------|-------------------|------------------|----------------|---------------|-----------------|-------------------|--------|
| CF-DEMO-01 | 59.000 | 59.000 | 25.000 | 18.880 | 40.120 | 40.120 | 0 | ninguna |
| CF-DEMO-02 | 47.200 | 47.200 | 22.000 | 14.590 | 32.610 | 72.730 | 0 | ninguna |
| CF-DEMO-03 | 30.000 | 0 | 20.000 | 12.310 | -12.310 | 60.420 | 12.310 | saldo semanal negativo |
| CF-DEMO-04 | 29.500 | 0 | 18.000 | 8.860 | -8.860 | 51.560 | 8.860 | saldo semanal negativo |
| CF-DEMO-05 | 23.600 | 0 | 15.000 | 17.700 | -17.700 | 33.860 | 17.700 | saldo semanal negativo |
| CF-DEMO-06 | 17.700 | 17.700 | 12.000 | 3.540 | 14.160 | 48.020 | 0 | ninguna |
| CF-DEMO-07 | 41.300 | 0 | 10.000 | 9.440 | -9.440 | 38.580 | 9.440 | saldo semanal negativo |
| CF-DEMO-08 | 23.600 | 0 | 8.000 | 7.670 | -7.670 | 30.910 | 7.670 | saldo semanal negativo |

## 12. Alertas demo

Alertas incluidas en los datos de demo:

- factura sin contrato (EXP-DEMO-03)
- contrato sin factura (CON-DEMO-02, CON-DEMO-08)
- nómina sin pago (PAYROLL-DEMO-02, PAYROLL-DEMO-05)
- pago sin documento (BANK-DEMO-06)
- ingreso previsto no cobrado (INC-DEMO-03, INC-DEMO-04, INC-DEMO-07)
- cobro sin factura emitida (INC-DEMO-05)
- documento duplicado (EXP-DEMO-06)
- proveedor nuevo (Proveedor Demo Varios 01)
- trabajador nuevo (PAYROLL-DEMO-06)
- pagador nuevo (Pagador Demo Inversor 01)
- fecha fuera de periodo (ninguna en datos actuales)
- importe raro (EXP-DEMO-10)
- IVA sospechoso (EXP-DEMO-13)
- retención sospechosa (EXP-DEMO-14)
- desviación frente a presupuesto (EXP-DEMO-09)
- saldo semanal negativo (CF-DEMO-03, CF-DEMO-04, CF-DEMO-05, CF-DEMO-07, CF-DEMO-08)
- baja confianza OCR futura (BANK-DEMO-04, BANK-DEMO-08)
- documento sin revisión (múltiples documentos pendientes de revisión humana)

## 13. Criterios visuales de la futura demo

Cómo debe verse el futuro Excel editable de Production Finance Control:

- Resumen ejecutivo claro en la primera hoja.
- KPIs arriba: ingresos totales, gastos totales, resultado neto, saldo previsto, pagos vencidos, cobros vencidos, alertas críticas.
- Tablas debajo: datos detallados por hoja.
- Gráficos laterales o por sección: visualización de tendencias y distribuciones.
- Semáforos verde/amarillo/rojo: indicadores visuales de estado.
- Alertas críticas visibles: destacadas en color y posición.
- Texto ejecutivo final: resumen, tendencias, desviaciones, necesidades de caja, recomendaciones.
- Hojas editables: cada hoja debe ser editable para revisión humana.
- Hoja de revisión manual visible: trazabilidad de correcciones.
- Trazabilidad documental visible: evidencias y documentos asociados.

## 14. Gráficos conceptuales de demo

Gráficos conceptuales que la futura plantilla debe incluir:

- gasto por categoría: distribución de gastos por tipo.
- ingresos por categoría: distribución de ingresos por fuente.
- cashflow acumulado: evolución semanal del saldo acumulado.
- presupuesto vs real: comparación por categoría con semáforos.
- ranking de proveedores: gasto acumulado por proveedor.
- ranking de pagadores: ingreso acumulado por pagador.
- alertas por gravedad: distribución de alertas por tipo y severidad.
- vencimientos próximos: pagos y cobros próximos a vencer.

## 15. Criterios de seguridad

- datos 100% ficticios;
- no datos reales;
- no datos personales reales;
- no facturas reales;
- no contratos reales;
- no nóminas reales;
- no cuentas bancarias reales;
- no emails reales;
- no teléfonos reales;
- no documentos de identidad reales;
- no documentos de identificación bancaria reales;
- no cumplimiento legal automático;
- no software fiscal certificado;
- no motor de nóminas;
- no sustituye asesoría;
- no sustituir asesoría;
- revisión humana obligatoria;
- trazabilidad documental conceptual.

## 16. No-goals

- No generar Excel real.
- No generar `.xlsx`.
- No generar `.csv`.
- No generar datos reales.
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

## 17. Encaje con presentación agosto/septiembre

Estos datos ficticios permitirán preparar una demo visual controlada de Production Finance Control. Junto a AILink Sync Dialogue como demo funcional principal y CID como visión integral, la demo de Production Finance Control mostrará cómo se vería el control financiero editable de una producción audiovisual.

La demo incluirá:
- Datos ficticios del Proyecto Demo Aurora.
- Plantilla Excel editable conceptual con todas las hojas definidas.
- Gráficos conceptuales de distribución, tendencias y alertas.
- Alertas demostrativas con revisión humana visible.
- Trazabilidad documental conceptual.

No se presenta como producto disponible. No se presenta como funcionalidad implementada. Es una demo visual controlada para presentación agosto/septiembre.

Referencia: HEAD estable `5caf6aa`, tag estable `ailink-cid-dev-stable-production-finance-control-excel-template-spec-phase3-20260613`.
