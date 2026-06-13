# AILink/CID Script-to-Production Breakdown Spec v1

Fase: `AILINK.CID.SCRIPT_TO_PRODUCTION_BREAKDOWN.SPEC.PHASE1`
Fecha: 2026-06-13
Tipo: especificación documental y test-only

Último HEAD estable conocido: `a73628f`.
Último tag estable conocido: `ailink-cid-dev-stable-production-finance-control-demo-data-contract-phase4-20260613`.
Etiqueta de seguridad: No runtime changes.

Nota obligatoria: Esta fase es conceptual/documental. No representa producto disponible. No representa funcionalidad implementada. No genera Excel real. No genera PDF real. No genera HTML real. No crea archivo `.xlsx`, `.csv`, `.pdf` ni `.html`. No es contrato API ni esquema de base de datos.

Contrato conceptual, no esquema de base de datos ni contrato API.

## 1. Nombre provisional

`AILink Script-to-Production Breakdown` como posible herramienta independiente futura.

`CID Script-to-Production Breakdown` como futuro flujo dentro de CID.

Encaje dentro de:
- `CID Script Intelligence`: análisis de guiones, detección de elementos narrativos, extracción de datos estructurados.
- `CID Production Intelligence`: desglose de producción, estimación de jornadas, asignación de departamentos, análisis de viabilidad.
- `CID Production Finance Control`: conexión entre presupuesto previsto del desglose y gasto real de producción.

Ambos nombres son provisionales y no autorizan implementación runtime.

## 2. Propósito

Script-to-Production Breakdown permite que un productor introduzca un guion y obtenga:

- Desglose de producción por escena y por departamento.
- Detección de complejidad narrativa, artística, logística, técnica y financiera.
- Estimación presupuestaria preliminar por categorías.
- Análisis de viabilidad con semáforos de riesgo.
- Recomendaciones de ajuste para reducir costes y riesgos.
- Conexión futura con Production Finance Control para comparar presupuesto previsto vs gasto real.

Esta herramienta no sustituye al productor, al director de producción ni a la asesoría profesional. Requiere revisión humana obligatoria.

## 3. Flujo conceptual

El flujo conceptual de Script-to-Production Breakdown sigue estos pasos:

1. **Entrada de guion**: el productor carga un guion en formato texto.
2. **Normalización del texto**: se estandariza el formato, se eliminan caracteres especiales.
3. **Detección de escenas**: se identifican los límites de cada escena.
4. **Extracción de personajes**: se detectan personajes por escena.
5. **Extracción de localizaciones**: se identifican localizaciones mencionadas.
6. **Detección interior/exterior**: se clasifica cada escena.
7. **Detección día/noche**: se clasifica cada escena.
8. **Elementos de producción**: se detectan arte, vestuario, maquillaje, atrezzo, vehículos, animales, menores, armas, agua, fuego, stunts, VFX, música, sonido.
9. **Riesgos**: se evalúa complejidad logística, artística, técnica y financiera.
10. **Estimación de jornadas**: se calculan días de rodaje necesarios.
11. **Presupuesto preliminar**: se generan rangos por categoría.
12. **Análisis de viabilidad**: se asignan semáforos por indicador.
13. **Recomendaciones**: se proponen ajustes para reducir costes y riesgos.
14. **Exportación futura**: vista en pantalla, Excel editable, PDF opcional, conexión con Production Finance Control.

Ninguno de estos pasos está implementado en esta fase.

## 4. Datos que debe extraer del guion

Campos conceptuales que el futuro sistema debe extraer:

- escenas
- secuencias
- páginas aproximadas
- personajes
- figuración
- localizaciones
- decorados
- interior/exterior
- día/noche
- época
- arte
- vestuario
- maquillaje
- atrezzo
- vehículos
- animales
- menores
- armas simuladas
- agua
- fuego
- stunts
- VFX
- música
- sonido complejo
- permisos
- viajes
- clima
- necesidades especiales

## 5. Desglose por escena

Tabla conceptual con columnas por escena:

| Campo | Descripción |
|-------|-------------|
| scene_id | identificador único de escena |
| número_escena | número original del guion |
| página_aproximada | página aproximada del guion |
| encabezado_escena | INT/EXT - LOCALIZACIÓN - DÍA/NOCHE |
| localización | localización detectada |
| interior_exterior | interior o exterior |
| día_noche | día o noche |
| personajes | lista de personajes presentes |
| figuración | número estimado de figurantes |
| elementos_arte | arte, decorados, atrezzo |
| vestuario_maquillaje | necesidades de vestuario y maquillaje |
| necesidades_cámara | movimientos de cámara, grúas, drones |
| necesidades_sonido | sonido directo, ADR, ambiental |
| VFX | efectos visuales necesarios |
| stunts_riesgo | acrobacias, riesgos de seguridad |
| permisos | permisos necesarios |
| complejidad | baja/media/alta |
| departamentos_afectados | lista de departamentos involucrados |
| notas_producción | observaciones para el equipo |

## 6. Desglose por departamentos

Departamentos cubiertos por el desglose:

- producción
- dirección
- ayudantía de dirección
- cámara
- sonido
- arte
- vestuario
- maquillaje
- localizaciones
- transporte
- catering
- VFX
- postproducción
- música
- legal/seguros
- distribución/marketing

## 7. Análisis de viabilidad

Indicadores conceptuales de viabilidad:

- complejidad logística
- complejidad artística
- complejidad técnica
- complejidad financiera
- riesgo de calendario
- riesgo de permisos
- riesgo de postproducción
- riesgo de localizaciones
- riesgo de reparto
- riesgo de cashflow
- viabilidad global

## 8. Semáforos de viabilidad

Estados conceptuales de semáforo:

- **verde**: viable con recursos bajos o controlados
- **amarillo**: viable con ajustes
- **naranja**: riesgo medio o alto
- **rojo**: no recomendable sin financiación o cambios significativos
- **gris**: información insuficiente para evaluar

## 9. Presupuesto preliminar

Categorías conceptuales con rangos:

| Categoría | Estimación baja | Estimación media | Estimación alta | Nivel de confianza | Supuestos usados |
|-----------|-----------------|------------------|-----------------|-------------------|------------------|
| equipo técnico | — | — | — | — | — |
| reparto | — | — | — | — | — |
| figuración | — | — | — | — | — |
| cámara | — | — | — | — | — |
| sonido | — | — | — | — | — |
| arte | — | — | — | — | — |
| vestuario | — | — | — | — | — |
| maquillaje | — | — | — | — | — |
| localizaciones | — | — | — | — | — |
| transporte | — | — | — | — | — |
| catering | — | — | — | — | — |
| seguros | — | — | — | — | — |
| permisos | — | — | — | — | — |
| VFX | — | — | — | — | — |
| música | — | — | — | — | — |
| postproducción | — | — | — | — | — |
| legal | — | — | — | — | — |
| contingencia | — | — | — | — | — |

Las estimaciones conceptuales usan rangos: estimación baja, estimación media, estimación alta, con un nivel de confianza y supuestos documentados. No son presupuesto definitivo.

## 10. Recomendaciones automáticas conceptuales

Tipos de recomendación que el futuro sistema podría proponer:

- reducir localizaciones
- agrupar escenas por decorado
- agrupar noches
- reducir figuración
- reducir VFX
- convertir exteriores complejos en interiores controlados
- simplificar vehículos, animales o stunts
- ajustar escenas con permisos costosos
- aumentar contingencia si hay riesgo alto
- revisar guion con productor y dirección de producción

Estas recomendaciones son conceptuales y requieren validación humana.

## 11. Salidas futuras

El futuro Script-to-Production Breakdown debe ofrecer:

- **Vista en pantalla del desglose**: visualización interactiva del desglose por escena y por departamento.
- **Vista en pantalla de la matriz de viabilidad**: semáforos e indicadores de riesgo.
- **Vista en pantalla del presupuesto preliminar**: rangos por categoría con nivel de confianza.
- **Excel editable como salida principal de trabajo**: el productor y el equipo pueden editar, ajustar y trabajar sobre el desglose exportado. Esta es la salida principal prevista para la demo y para uso profesional.
- **PDF opcional bajo demanda del cliente**: generación de PDF solo cuando el cliente lo precise, no de forma automática ni prioritaria. El PDF es una exportación complementaria, no la salida principal.
- **Exportación futura a Production Finance Control**: el presupuesto previsto se conectará con el gasto real para detectar desviaciones.
- **Conexión futura con plan de rodaje**: el desglose alimentará el plan de rodaje.
- **Conexión futura con call sheet / orden diaria**: las escenas del desglose se vincularán con las ordenes diarias.
- **Conexión futura con partes de rodaje**: el desglose se comparará con los partes de rodaje reales.
- **Conexión futura con montaje diario**: el desglose de escenas se vinculará con el montaje diario.

Ninguna de estas salidas está implementada en esta fase. No se genera Excel real, no se genera PDF real, no se genera HTML real.

## 12. Encaje con Production Finance Control

Script-to-Production Breakdown genera un presupuesto previsto que en el futuro se conectará con Production Finance Control:

- Script-to-Production Breakdown genera presupuesto previsto por categorías.
- Production Finance Control compara presupuesto previsto vs gasto real.
- El futuro Excel financiero de Production Finance Control puede recibir categorías y estimaciones desde el desglose.
- Las desviaciones entre previsto y real se podrán detectar durante la producción.
- No se implementa esa integración en esta fase.

## 13. Encaje con AILink Sync Dialogue

Sync Dialogue sigue siendo herramienta independiente. Script-to-Production Breakdown no toca Sync Dialogue.

En futuro CID, ambos pueden conectarse a través de:
- escenas
- tomas
- diálogos
- montaje diario

No se promete integración real en esta fase.

## 14. Encaje con presentación agosto/septiembre

Esta línea puede ser una demo muy atractiva para productores en la presentación agosto/septiembre.

Objetivo de demo futura: introducir un guion ficticio y obtener desglose de producción, análisis de viabilidad y presupuesto preliminar. La demo mostrará:

- Vista en pantalla del desglose por escena y por departamento.
- Vista en pantalla de la matriz de viabilidad con semáforos.
- Vista en pantalla del presupuesto preliminar con rangos.
- Excel editable como salida principal de trabajo.
- PDF opcional bajo demanda del cliente.

Debe comunicarse como beta/controlada. No debe venderse como presupuesto definitivo ni sustituto del productor, director de producción o asesoría.

## 15. No-goals

- No parser real.
- No IA real.
- No lectura de guiones reales.
- No lectura de PDFs reales.
- No Final Draft import.
- No Fountain import.
- No OCR.
- No RAG multimodal.
- No generar Excel real.
- No generar `.xlsx`.
- No generar `.csv`.
- No generar PDF real.
- No generar HTML real.
- No PDF automático.
- No exportación real en esta fase.
- No presupuesto definitivo: no presupuesto definitivo.
- no sustituto de productor.
- no sustituto de director de producción.
- No sustituto de asesoría.
- no integración real con Production Finance Control.
- no integración real con Sync Dialogue.
- No integración real con plan de rodaje.
- No runtime changes.
- No tocar CID SaaS actual.

## 16. Claims permitidos

- "genera un primer desglose orientativo"
- "ayuda a detectar riesgos de producción"
- "propone una estimación financiera preliminar"
- "requiere revisión humana"
- "sirve como apoyo al productor y al equipo de producción"

## 17. Claims prohibidos

- "calcula el presupuesto exacto"
- "sustituye al productor"
- "sustituye al director de producción"
- "garantiza viabilidad"
- "produce un presupuesto oficial"
- "funcionalidad implementada"
- "producto disponible"
- "integración real ya disponible"

Referencia: HEAD estable `a73628f`, tag estable `ailink-cid-dev-stable-production-finance-control-demo-data-contract-phase4-20260613`.
