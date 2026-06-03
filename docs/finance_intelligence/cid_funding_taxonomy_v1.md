# CID Funding Intelligence — Taxonomy v1

## 1. Resumen ejecutivo

Este documento unifica la investigacion de España, Europa e Iberoamerica en una taxonomia unica para el futuro modulo CID Funding Intelligence. No constituye asesoramiento legal, fiscal, financiero ni de inversion.

Base documental:
- `spain_funding_sources_research_v1.md`
- `europe_funding_sources_research_v1.md`
- `cid_funding_intelligence_data_model_v1.md`

La taxonomia define tipos de fuente, campos minimos, reglas de elegibilidad, compatibilidades conceptuales, estados de verificacion, niveles de confianza, formatos, fases y reglas de recomendacion. Todo dato no confirmado con fuente oficial accesible se marca como `PENDIENTE DE VERIFICACION`.

Ninguna combinacion de fuentes presentada en este documento debe interpretarse como financiacion cerrada sin revision profesional especializada.

## 2. Objetivo de la taxonomia

- Unificar criterios de clasificacion entre España, Europa e Iberoamerica en un solo esquema.
- Permitir que un proyecto CID reciba recomendaciones de financiacion estructuradas por tipo de fuente, fase, formato y territorio.
- Separar fuentes verificadas de fuentes pendientes para evitar falsas certezas.
- Proporcionar una base estable para evolucionar hacia dataset, motor de reglas y estimaciones (CID.FINANCE.INTELLIGENCE.DATASET.SPEC.1).

## 3. Principios

### 3.1 No recomendar como seguro lo no verificado
- Ninguna fuente con estado `pending_verification` o `outdated` puede presentarse como recomendacion segura.
- Las fuentes `partially_confirmed` deben mostrarse con advertencia visible.
- Ninguna cifra sin fuente primaria o institucional clara puede presentarse como definitiva.

### 3.2 Separar fuente de financiacion, incentivo fiscal, coproduccion y canal corporativo
- `public_grant`, `tax_incentive`, `coproduction_framework` y `broadcaster`/`platform` son tipos distintos.
- No mezclar naturaleza juridica (subvencion) con mecanismo de entrada (convocatoria, preventa, acuerdo corporativo).
- Un canal corporativo sin via publica verificada debe marcarse como `corporate_access` en riesgos.

### 3.3 Diferenciar linea concreta frente a institucion
- ICAA no es una fuente: es un organismo que gestiona multiples lineas independientes.
- Creative Europe MEDIA no es una fuente: es un paraguas de programas/calls.
- Ibermedia no es una fuente: es una familia de lineas (codesarrollo, coproduccion, distribucion, formacion).
- Eurimages es una fuente delimitada (fondo de coproduccion) con reglamento propio.

### 3.4 Mantener trazabilidad de fuente oficial
- Toda fuente debe incluir URL oficial o indicacion de por que no esta disponible.
- Las cifras deben ir acompanadas de su fuente (norma, institucion, organismo).
- Si la fuente no fue accesible en la sesion de investigacion, marcarlo explicitamente.

## 4. Clasificacion principal

| source_type | Descripcion | Ejemplos de la investigacion |
|---|---|---|
| `public_grant` | Subvencion competitiva o nominativa de organismo publico | ICAA generales, ICAA selectivas, ICAA cortometrajes, ICAA distribucion, ICAA guiones, ayudas autonomicas |
| `tax_incentive` | Deduccion, rebate o credito fiscal estatal o foral | Art. 36 IS (Espana), Canarias REF, Navarra arts. 65.1/65.2/65 bis |
| `european_fund` | Fondo o programa supranacional europeo | Eurimages (fondo coproduccion), Creative Europe MEDIA (familia de calls) |
| `iberoamerican_fund` | Fondo o programa del espacio iberoamericano | Ibermedia (codesarrollo, coproduccion, distribucion, formacion, ayudas complementarias) |
| `coproduction_framework` | Marco de elegibilidad que habilita acceso a fuentes, no fuente directa | Coproduccion europea, corredores ES-FR/ES-IT/ES-DE/ES-PT, coproduccion Espana-Latinoamerica |
| `broadcaster` | Participacion, preventa, adquisicion o coproduccion de television | RTVE, Atresmedia Cine, Mediaset/Telecinco Cinema, EITB |
| `platform` | Adquisicion, commissioning, originales o participacion de plataforma | Movistar Plus+ |
| `presale` | Preventa territorial o por ventana a distribuidor, broadcaster o plataforma | No documentado como via publica independiente en esta investigacion; PENDIENTE DE VERIFICACION |
| `private_equity` | Capital privado o inversor industrial | No documentado como fuente independiente en esta investigacion; PENDIENTE DE VERIFICACION |
| `gap_financing` | Cobertura del hueco financiero restante tras fuentes confirmadas | No documentado como via independiente en esta investigacion; PENDIENTE DE VERIFICACION |
| `regional_support` | Apoyo institucional territorial no estrictamente fiscal | Film commissions, ayudas al rodaje, promocion territorial |

Nota: `presale`, `private_equity` y `gap_financing` se incluyen en la taxonomia como tipos conceptuales pero no tienen fuentes documentadas en la investigacion actual. No deben presentarse como opciones disponibles sin verificacion adicional.

## 5. Campos minimos para FundingSource

| Campo | Tipo | Obligatorio | Descripcion |
|---|---|---|---|
| `source_id` | string | si | Identificador unico CID para la fuente |
| `source_name` | string | si | Nombre completo de la fuente |
| `source_type` | enum | si | Tipo segun clasificacion principal (seccion 4) |
| `institution` | string | si | Organismo, entidad o empresa que gestiona la fuente |
| `territory` | string | si | Ambito territorial: estatal, autonomico, foral, europeo, iberoamericano, multilateral |
| `country` | string | si | Pais principal (ES, FR, IT, DE, PT, multilateral, etc.) |
| `region` | string | no | Region o comunidad autonoma si aplica (Canarias, Navarra, Madrid, Cataluna, etc.) |
| `project_format` | array<enum> | si | Formatos elegibles segun taxonomia de formatos (seccion 10) |
| `project_stage` | array<enum> | si | Fases del proyecto segun taxonomia de fases (seccion 11) |
| `eligible_budget_type` | string | no | Tipo de gasto elegible (produccion, distribucion, desarrollo, etc.) |
| `official_url` | string | si | URL oficial de la fuente o PENDIENTE DE VERIFICACION si no accesible |
| `verification_status` | enum | si | Estado segun taxonomia de verificacion (seccion 12) |
| `confidence_level` | enum | si | Nivel de confianza segun seccion 13 |

Nota: `region` y `eligible_budget_type` son opcionales porque no todas las fuentes tienen ambito regional o un tipo de gasto definido publicamente.

## 6. Campos para EligibilityRule

Cada `EligibilityRule` modela una condicion de encaje preliminar entre proyecto y fuente.

### 6.1 Campos

| Campo | Tipo | Obligatorio | Descripcion |
|---|---|---|---|
| `rule_id` | string | si | Identificador unico de la regla |
| `funding_source_id` | string | si | Referencia a la fuente que impone la regla |
| `rule_type` | enum | si | Tipo de condicion (ver 6.2) |
| `rule_label` | string | si | Descripcion legible de la regla |
| `operator` | enum | no | Operador de comparacion (eq, gte, lte, in, contains, boolean) |
| `expected_value` | any | no | Valor esperado para cumplir la regla |
| `mandatory` | boolean | si | true si es condicion eliminatoria, false si es deseable |
| `verification_level` | enum | si | Nivel de verificacion de esta regla (verified, institutional, pending) |
| `notes` | string | no | Notas libres para contextos o excepciones |
| `source_reference` | string | no | Referencia a la fuente normativa o documento donde se recoge la regla |

### 6.2 Tipos de regla recomendados

- `territory` — pais/region donde debe establecerse el solicitante o realizarse el gasto
- `project_stage` — fase del proyecto requerida
- `project_format` — formato elegible
- `applicant_type` — tipo de entidad solicitante (persona fisica, productora, agrupacion)
- `minimum_spend` — gasto minimo elegible
- `local_spend` — porcentaje o importe minimo de gasto local
- `cultural_certificate` — exige certificado de nacionalidad o culturalidad
- `icaa_registration` — exige registro en ICAA
- `language` — idioma o lenguas oficiales
- `coproduction_required` — exige estructura de coproduccion
- `coproduction_minimum_partners` — numero minimo de coproductores
- `coproduction_maximum_share` — porcentaje maximo de participacion mayoritaria
- `coproduction_minimum_share` — porcentaje minimo de participacion minoritaria
- `exploitation_window` — ventana de explotacion requerida
- `budget_limit` — limite presupuestario del proyecto
- `maximum_aid_intensity` — intensidad maxima de ayuda acumulada
- `de_minimis_check` — sujeta a regla de minimis
- `independence_test` — exige productora independiente de prestador audiovisual

### 6.3 Ejemplos

ICAA distribucion `051850`:
- `rule_type`: territory
- `operator`: eq
- `expected_value`: ES (o pais comunitario/iberoamericano segun la linea)
- `mandatory`: true
- `verification_level`: verified

Eurimages:
- `rule_type`: coproduction_required
- `operator`: boolean
- `expected_value`: true
- `mandatory`: true
- `verification_level`: verified

Navarra art. 65.1:
- `rule_type`: local_spend
- `operator`: gte
- `expected_value`: 40 (porcentaje de gasto en territorio navarro)
- `mandatory`: true
- `verification_level`: verified

## 7. Campos para FundingCompatibility

Cada `FundingCompatibility` describe si dos fuentes pueden combinarse sin conflicto preliminar conocido.

### 7.1 Campos

| Campo | Tipo | Obligatorio | Descripcion |
|---|---|---|---|
| `compatibility_id` | string | si | Identificador unico |
| `source_a_id` | string | si | Primera fuente |
| `source_b_id` | string | si | Segunda fuente |
| `compatibility_level` | enum | si | conceptual, conditional, incompatible, pending_verification |
| `conditions` | string | no | Condiciones conocidas para que sea compatible |
| `risk_note` | string | no | Riesgo documentado de la combinacion |
| `verification_status` | enum | si | verified / institutional / pending |
| `source_reference` | string | no | Documento o norma que sustenta la compatibilidad |

### 7.2 Niveles de compatibilidad

- `conceptual` — no hay conflicto evidente, pero no se ha verificado en fuente oficial
- `conditional` — compatible si se cumplen condiciones concretas documentadas
- `incompatible` — conflicto conocido (exclusividad, doble computo, intensidad maxima)
- `pending_verification` — no se ha podido determinar en la investigacion actual

Regla: ningun par de fuentes debe marcarse como `conceptual` sin incluir la nota de que requiere validacion legal/fiscal.

## 8. Campos para FundingEstimate

Cada `FundingEstimate` representa el impacto financiero potencial de una fuente sobre un proyecto concreto.

### 8.1 Campos

| Campo | Tipo | Obligatorio | Descripcion |
|---|---|---|---|
| `estimate_id` | string | si | Identificador unico |
| `funding_source_id` | string | si | Fuente evaluada |
| `scenario` | enum | si | conservative / base_case / optimistic |
| `eligible_spend` | number | no | Base de gasto elegible estimada |
| `estimated_amount` | number | no | Importe estimado (null si PENDIENTE DE VERIFICACION) |
| `estimated_percentage` | number | no | Porcentaje o intensidad estimada (null si PENDIENTE DE VERIFICACION) |
| `currency` | string | si | EUR, USD u otras |
| `assumptions` | string | si | Supuestos utilizados para la estimacion |
| `confidence_level` | enum | si | high / medium / low / blocked |
| `verification_status` | enum | si | Estado de la fuente en el momento de la estimacion |
| `blocked_by` | array<string> | no | Lista de factores que bloquean la estimacion (falta de convocatoria, cambio normativo, etc.) |

### 8.2 Reglas de estimacion

- Si la fuente no tiene cuantia verificada, `estimated_amount` debe ser `null`.
- Ningun escenario `optimistic` puede mostrarse como prevision sin marcar los supuestos.
- No mezclar escenarios de distintas fuentes en una misma cuenta de resultados sin desglose.

### 8.3 Ejemplo conceptual

ICAA generales (produccion largometraje, 2,5M EUR):
- `scenario`: base_case
- `estimated_amount`: PENDIENTE DE VERIFICACION (la cuantia por proyecto no esta publicada; solo se conoce la dotacion total 32M EUR)
- `confidence_level`: medium
- `verification_status`: partially_confirmed

## 9. Campos para RiskFlag

Cada `RiskFlag` senala un riesgo documentado o potencial de una fuente o combinacion.

### 9.1 Campos

| Campo | Tipo | Obligatorio | Descripcion |
|---|---|---|---|
| `risk_id` | string | si | Identificador unico |
| `funding_source_id` | string | si | Fuente asociada al riesgo |
| `risk_type` | enum | si | legal, fiscal, calendar, documentation, competition, corporate_access, verification, coproduction |
| `risk_level` | enum | si | high, medium, low, blocked |
| `risk_summary` | string | si | Descripcion del riesgo |
| `mitigation_hint` | string | no | Accion sugerida para mitigar |
| `requires_professional_review` | boolean | si | true si requiere abogado, asesor fiscal o financiero |
| `verification_status` | enum | si | verified / institutional / pending |

### 9.2 Tipos de riesgo

- `legal` — duda de elegibilidad normativa
- `fiscal` — estructura societaria, territorializacion, limites o compatibilidades fiscales
- `calendar` — fuera de convocatoria, ventana cerrada o hitos temporales incompatibles
- `documentation` — falta de certificados, registros, contratos o anexos
- `competition` — ayuda competitiva con baja previsibilidad por numero de solicitantes
- `corporate_access` — broadcaster/plataforma sin via publica clara de acceso
- `verification` — fuente no confirmada o desactualizada
- `coproduction` — riesgo especifico de estructura de coproduccion (reparto, derechos, aprobacion)

### 9.3 Ejemplos

RTVE:
- `risk_type`: corporate_access
- `risk_level`: high
- `risk_summary`: No se ha localizado via publica concluyente de entrada para productores
- `requires_professional_review`: true
- `verification_status`: pending

ICAA selectivas:
- `risk_type`: calendar
- `risk_level`: high
- `risk_summary`: Convocatoria 2026 no verificada; la referencia disponible es de 2025
- `requires_professional_review`: false
- `verification_status`: pending

Canarias:
- `risk_type`: fiscal
- `risk_level`: medium
- `risk_summary`: Cifras institucionales (hasta 54%) pendientes de contraste con fuente normativa primaria
- `mitigation_hint`: Solicitar validation fiscal antes de modelar cifras definitivas
- `requires_professional_review`: true
- `verification_status`: partially_confirmed

## 10. Taxonomia de formatos

| project_format | Descripcion | Ejemplos de la investigacion |
|---|---|---|
| `feature_film` | Largometraje cinematografico (duracion >= 60 min) | ICAA generales, ICAA selectivas, Eurimages, Ibermedia coproduccion |
| `short_film` | Cortometraje (duracion < 60 min) | ICAA cortometrajes sobre proyecto, ICAA cortometrajes realizados |
| `documentary` | Obra documental | ICAA (si cumple formato), Eurimages, Ibermedia, Navarra categoria especial |
| `animation` | Obra de animacion | ICAA (si cumple formato), Eurimages, Ibermedia, incentivos con gasto minimo reducido (200.000 EUR animacion service) |
| `series` | Serie audiovisual (episodica) | Art. 36 IS (10M EUR por episodio), Ibermedia codesarrollo series, Movistar Plus+ originales |
| `script_development` | Proyecto de guion en fase de escritura | ICAA guiones, Ibermedia codesarrollo, Creative Europe MEDIA desarrollo |
| `distribution` | Distribucion de obra terminada | ICAA distribucion 051850, Ibermedia distribucion/circulacion, Creative Europe MEDIA distribucion |
| `festival` | Participacion u organizacion de festivales | ICAA organizacion festivales, ICAA participacion festivales |

## 11. Taxonomia de fases

| project_stage | Descripcion | Fuentes tipicas |
|---|---|---|
| `idea` | Concepto inicial sin desarrollo | No documentada como fase elegible en fuentes verificadas |
| `script` | Escritura de guion | ICAA guiones, Ibermedia codesarrollo, Creative Europe MEDIA desarrollo |
| `development` | Preparacion de produccion (memoria, buscar financiacion, diseno) | Ibermedia codesarrollo, Creative Europe MEDIA desarrollo, ayudas autonomicas al desarrollo |
| `financing` | Cierre de financiacion y estructura | Financiador fiscal Navarra art. 65 bis, tax incentive planning, preventas |
| `production` | Rodaje y ejecucion de la obra | ICAA generales, ICAA selectivas, Art. 36 IS, Canarias REF, Navarra arts. 65.1/65.2, Eurimages |
| `postproduction` | Montaje, etalonaje, sonido, VFX | No documentada como fase independiente en fuentes verificadas (suele integrarse en produccion) |
| `distribution` | Lanzamiento comercial, copias, promocion | ICAA distribucion 051850, Ibermedia distribucion/circulacion, Creative Europe MEDIA distribucion |
| `festival_release` | Presentacion en festivales, promocion internacional | ICAA participacion festivales, ICAA organizacion festivales |

Nota: Las fases `idea` y `postproduction` se incluyen en la taxonomia por completitud pero no tienen fuentes documentadas como fase independiente elegible en la investigacion actual.

## 12. Estados de verificacion

| verification_status | Descripcion | Puede mostrarse como recomendacion segura |
|---|---|---|
| `verified_primary_source` | Fuente primaria oficial accesible y verificada (norma, BOE, convocatoria, ficha oficial) | Si, con cautela |
| `verified_institutional_source` | Fuente institucional secundaria verificada (organismo oficial, film commission, ente sectorial) | Si, con advertencia de que requiere validacion legal/fiscal final |
| `partially_confirmed` | Parte de los datos confirmados, parte pendientes | No; debe mostrarse con warning |
| `pending_verification` | No se ha podido verificar en la investigacion actual | No |
| `outdated` | Verificado en su momento pero con posible desfase normative o de convocatoria | No; requiere re-verificacion |

### 12.1 Mapa desde la investigacion

| verification_status | Fuentes que lo usan |
|---|---|
| `verified_primary_source` | ICAA realizados 051780, ICAA distribucion 051850, ICAA guiones (parcial), Art. 36 IS, Navarra arts. 65.1/65.2/65 bis, Eurimages (reglamento 2026) |
| `verified_institutional_source` | Spain Film Commission (incentivos), Canary Islands Film (portal), Navarra Film Industry / Cultura Navarra, Creative Europe MEDIA (pagina institucional), Ibermedia (marco legal y convocatorias) |
| `partially_confirmed` | ICAA generales (pagina accesible, ficha pendiente), Canarias (cifras pendientes de contraste normativo), Atresmedia Cine, Movistar Plus+, ayudas autonomicas (Madrid, Cataluna, Andalucia, Galicia, C. Valenciana) |
| `pending_verification` | ICAA selectivas (convocatoria 2026), ICAA festivales, RTVE (via de entrada), Mediaset/Telecinco Cinema, corredores bilaterales ES-FR/ES-IT/ES-DE/ES-PT, presale, private_equity, gap_financing |
| `outdated` | ICAA selectivas (ficha 2025 localizada, no 2026) |

## 13. Niveles de confianza

| confidence_level | Descripcion |Cuando aplica |
|---|---|---|
| `high` | Datos confirmados con fuente primaria oficial accesible y sin contradicciones | ICAA distribucion 051850, Art. 36 IS, Navarra arts. 65.1/65.2/65 bis, Eurimages reglamento 2026 |
| `medium` | Datos confirmados con fuente institucional o parcialmente verificados, sin contradicciones mayores | ICAA generales (pagina accesible, ficha pendiente), Canarias (institucional, pendiente normativa), Creative Europe MEDIA (institucional, detalle por call pendiente), Ibermedia (institucional, detalle por linea pendiente) |
| `low` | Fuente identificada pero con datos pendientes de confirmar, o via de acceso no verificada | ICAA selectivas, RTVE, Mediaset, corredores bilaterales, presale, private_equity, gap_financing |
| `blocked` | Imposibilidad tecnica de verificar en la investigacion actual | Ninguna fuente marcada como blocked en v1; reservado para casos futuros de bloqueo permanente |

## 14. Ejemplos normalizados

Cada ejemplo muestra una entrada `FundingSource` completa segun los campos de la seccion 5.

### 14.1 ICAA ayudas generales largometraje

- `source_id`: ES-ICAA-GENERALES-2026
- `source_name`: Ayudas generales para la produccion de largometrajes sobre proyecto
- `source_type`: public_grant
- `institution`: Instituto de la Cinematografia y de las Artes Audiovisuales (ICAA) / Ministerio de Cultura
- `territory`: estatal
- `country`: ES
- `region`: null
- `project_format`: [feature_film]
- `project_stage`: [production]
- `eligible_budget_type`: produccion
- `official_url`: https://www.cultura.gob.es/cultura/areas/cine/ayudas/produccion/generales.html
- `verification_status`: partially_confirmed
- `confidence_level`: medium

Notas:
- Pagina oficial 2026 accesible.
- Codigo administrativo y ficha de catalogo concreta: PENDIENTE DE VERIFICACION.
- Dotacion total conocida: 32M EUR (convocatoria 2026).
- Cuantia por proyecto: PENDIENTE DE VERIFICACION.
- Dos procedimientos en 2026 (mayo-junio, junio-septiembre).

### 14.2 ICAA distribucion

- `source_id`: ES-ICAA-DISTRIBUCION-051850-2026
- `source_name`: Ayudas para la distribucion de peliculas de largometraje y conjuntos de cortometrajes, espanoles, comunitarios e iberoamericanos
- `source_type`: public_grant
- `institution`: ICAA / Ministerio de Cultura
- `territory`: estatal
- `country`: ES
- `region`: null
- `project_format`: [feature_film, short_film]
- `project_stage`: [distribution]
- `eligible_budget_type`: distribucion
- `official_url`: https://www.cultura.gob.es/servicios-a-la-ciudadania/catalogo/general/05/051850/ficha/051850-2026.html
- `verification_status`: verified_primary_source
- `confidence_level`: high

Notas:
- Codigo administrativo: 051850.
- Convocatoria 2026 verificada con ficha oficial accesible.
- Importe total: 4.000.000 EUR.
- Limite individual: 150.000 EUR.
- Intensidad maxima: 50% de determinados costes de distribucion.
- Aplica a cine espanol, comunitario e iberoamericano.

### 14.3 ICAA guiones

- `source_id`: ES-ICAA-GUIONES-2026
- `source_name`: Ayudas al desarrollo de guiones para peliculas de largometraje
- `source_type`: public_grant
- `institution`: ICAA / Ministerio de Cultura
- `territory`: estatal
- `country`: ES
- `region`: null
- `project_format`: [script_development]
- `project_stage`: [script]
- `eligible_budget_type`: escritura de guion
- `official_url`: https://www.cultura.gob.es/servicios-a-la-ciudadania/catalogo/general/05/051860/ficha/051860-2026.html (URL pendiente de confirmar, ficha 2026 accesible en el momento de la investigacion con codigo 015860-2026)
- `verification_status`: verified_primary_source
- `confidence_level`: medium

Notas:
- Convocatoria 2026 verificada con ficha oficial accesible.
- Plazo: 03 julio - 23 julio 2026.
- BDNS: 26-05-2026, BOE: 28-05-2026.
- Cuantia por proyecto: PENDIENTE DE VERIFICACION.
- Codigo administrativo: PENDIENTE DE VERIFICACION (referencia de catalogo 051860).
- URL verificada en el momento de la investigacion; discrepancia entre codigo de carpeta (051860) y ficha (015860-2026) pendiente de confirmacion.

### 14.4 Eurimages

- `source_id`: EU-EURIMAGES-COPRO-2026
- `source_name`: Eurimages Co-production Support
- `source_type`: european_fund
- `institution`: Council of Europe / Eurimages
- `territory`: europeo (multilateral)
- `country`: multilateral (Estados miembros del Council of Europe + estados no miembros con participacion limitada)
- `region`: null
- `project_format`: [feature_film, documentary, animation]
- `project_stage`: [production]
- `eligible_budget_type`: coproduccion (produccion)
- `official_url`: PENDIENTE DE VERIFICACION (portal oficial bloqueado 403 en la investigacion; reglamento 2026 verificado como PDF)
- `verification_status`: verified_primary_source (reglamento 2026 verificado)
- `confidence_level`: medium

Notas:
- Reglamento 2026 verificado como fuente primaria.
- Apoyo maximo: 500.000 EUR.
- <= 150.000 EUR: subvencion no reembolsable.
- > 150.000 EUR: anticipo sobre ingresos.
- 3 convocatorias por ano. Presupuesto anual aproximado: 30M EUR.
- Exige coproduccion (minimo 2 productores independientes de distintos estados miembros).
- Coproduccion bilateral: mayoritario max 80%, minoritario min 20%.
- Coproduccion multilateral: mayoritario max 70%, cada minoritario min 10%.
- Deadlines concretos de cada call: PENDIENTE DE VERIFICACION.
- Compatibilidad exacta con fuentes espanolas: PENDIENTE DE VERIFICACION.

### 14.5 Creative Europe MEDIA

- `source_id`: EU-MEDIA-2026
- `source_name`: Creative Europe MEDIA strand
- `source_type`: european_fund
- `institution`: European Commission
- `territory`: europeo
- `country`: multilateral (Estados miembros UE + paises asociados)
- `region`: null
- `project_format`: [feature_film, documentary, animation, series, distribution, festival]
- `project_stage`: [script, development, production, distribution, festival_release]
- `eligible_budget_type`: multiple segun call (desarrollo, distribucion, promocion, innovacion, audiencias, formacion)
- `official_url`: https://culture.ec.europa.eu/creative-europe/creative-europe-media-strand
- `verification_status`: verified_institutional_source
- `confidence_level`: medium

Notas:
- MEDIA es un paraguas de programas/calls, no una fuente homogenea.
- Cada call debe modelarse como subfuente independiente.
- Elegibilidad, calendario, intensidad y compatibilidad: dependen de la call concreta.
- Ninguna recomendacion segura sin revisar la convocatoria especifica.

### 14.6 Ibermedia

- `source_id`: IBERMEDIA-2026
- `source_name`: Programa Ibermedia (fondo iberoamericano)
- `source_type`: iberoamerican_fund
- `institution`: Programa Ibermedia
- `territory`: iberoamericano
- `country`: multilateral (paises miembros iberoamericanos)
- `region`: null
- `project_format`: [feature_film, documentary, animation, series, script_development, distribution]
- `project_stage`: [script, development, production, distribution]
- `eligible_budget_type`: codesarrollo, coproduccion, distribucion/circulacion, formacion
- `official_url`: https://www.programaibermedia.com/
- `verification_status`: verified_institutional_source
- `confidence_level`: medium

Notas:
- Ibermedia es una familia de lineas, no una fuente unica.
- Lineas documentadas: codesarrollo largometrajes, codesarrollo series, coproduccion, distribucion/circulacion, formacion, ayudas complementarias.
- Convocatoria 2026 localizada: 30 enero - 30 marzo 2026.
- Compatibilidad exacta por linea con ICAA y fuentes espanolas: PENDIENTE DE VERIFICACION.

### 14.7 Navarra tax incentive

- `source_id`: ES-NAVARRA-INCENTIVO-65
- `source_name`: Incentivo fiscal audiovisual de Navarra (arts. 65.1, 65.2 y 65 bis)
- `source_type`: tax_incentive
- `institution`: Gobierno de Navarra / Departamento de Cultura
- `territory`: foral
- `country`: ES
- `region`: Navarra
- `project_format`: [feature_film, short_film, documentary, animation, series]
- `project_stage`: [production, financing]
- `eligible_budget_type`: produccion, service production, financiacion fiscal
- `official_url`: https://www.culturanavarra.es/es/informacion-general / https://www.navarrafilmindustry.com/es/ven-a-navarra/incentivo-fiscal-audiovisual-en-navarra/
- `verification_status`: verified_primary_source
- `confidence_level`: high

Notas:
- Produccion espanola: 45% general, 50% especial (tres primeros millones).
- Service: 35% gastos en territorio navarro.
- Financiador fiscal: 1,20x el desembolso (art. 65 bis).
- Limite: 5M EUR por produccion.
- Gasto local minimo: 40% para produccion espanola.
- Minimo una semana de rodaje en Navarra para services.

### 14.8 Canarias tax incentive

- `source_id`: ES-CANARIAS-INCENTIVO-REF
- `source_name`: Incentivo fiscal audiovisual de Canarias (REF)
- `source_type`: tax_incentive
- `institution`: Gobierno de Canarias / Canary Islands Film
- `territory`: autonomico / REF
- `country`: ES
- `region`: Canarias
- `project_format`: [feature_film, short_film, documentary, animation, series]
- `project_stage`: [production]
- `eligible_budget_type`: produccion, service production
- `official_url`: https://canaryislandsfilm.com/
- `verification_status`: partially_confirmed
- `confidence_level`: medium

Notas:
- Fuente institucional sectorial localizada: Canary Islands Film.
- Hasta 54% publicado en portal institucional para producciones espanolas y extranjeras.
- Compatibilidad con 4% IS mencionada en texto institucional.
- Cifras pendientes de contraste con fuente normativa primaria.
- Gasto minimo local: 1M EUR para producciones extranjeras.
- Certificado de Obra Audiovisual Canaria para producciones espanolas.
- No modelar cifras definitivas sin validacion fiscal profesional.

## 15. Matriz de compatibilidad conceptual

Todas las entradas de esta matriz son conceptuales. Ninguna combinacion debe darse por segura sin revision legal/fiscal.

| Fuente A | Fuente B | Compatibilidad | Condiciones conocidas | Riesgo documentado |
|---|---|---|---|---|
| ICAA generales | Art. 36 IS | conditional | Acumulacion sujeta a limites de intensidad de ayuda; no superar maximos legales | Doble computo de gasto; intensidad maxima |
| ICAA generales | ICAA selectivas | incompatible | Ayudas incompatibles entre si para un mismo proyecto en la misma fase | Exclusividad de linea |
| ICAA generales | Navarra tax incentive | conditional | ICAA y deduccion foral pueden coexistir si se cumplen requisitos de gasto e intensidad | Limite de acumulacion; gasto local navarro |
| ICAA generales | Canarias tax incentive | conditional | Posible si el proyecto cumple requisitos canarios y nacionales | Doble territorializacion; certificado canario |
| ICAA distribucion | Ibermedia distribucion | conceptual | No hay conflicto evidente, no verificado en fuente oficial | Doble ayuda en distribucion |
| Art. 36 IS | Navarra tax incentive | conditional | Posible si la estructura fiscal lo permite y no se superan limites | Fiscalidad foral vs estatal |
| Art. 36 IS | Canarias tax incentive | conditional | Canarias REF menciona compatibilidad con 4% IS; detalle PENDIENTE DE VERIFICACION | Doble computo; normativa canaria pendiente |
| Eurimages | ICAA generales | conceptual | Posible si el proyecto cumple coproduccion europea y convocatoria ICAA | Nacionalidad de obra; aprobacion coproduccion |
| Eurimages | Art. 36 IS | conceptual | Posible si la obra mantiene nacionalidad espanola y cumple territorializacion | Doble computo de gasto; requisito 50% financiacion confirmada Eurimages |
| Eurimages | Navarra tax incentive | conceptual | Posible si el coproductor navarro cumple gasto local e intensidad | Acumulacion multi-pais; limites de ayuda |
| Creative Europe MEDIA | ICAA generales | conceptual | Depende de la call MEDIA concreta y la convocatoria ICAA | Doble financiacion; elegibilidad por call |
| Creative Europe MEDIA | Ibermedia | conceptual | Posible si el proyecto encaja en ambos marcos | Doble financiacion; coordinacion de calendarios |
| Ibermedia | ICAA generales | conceptual | Posible si la obra mantiene nacionalidad espanola y cumple requisitos Ibermedia | Nacionalidad de obra; doble ayuda |
| Ibermedia | Art. 36 IS | conceptual | Posible si se cumplen requisitos fiscales estatales | Doble computo; estructura de coproduccion |
| RTVE | ICAA generales | conceptual | Posible si no hay clausula de exclusividad | Exclusividad editorial; ventanas |
| Movistar Plus+ | Art. 36 IS | conceptual | Posible si la plataforma no interfiere con requisitos fiscales | Exclusividad de ventana; acceso corporativo |

Toda combinacion marcada como `conceptual` debe entenderse como: "no hay contradiccion evidente, pero CID no puede confirmar compatibilidad sin verificacion legal/fiscal especifica para el proyecto concreto."

## 16. Reglas de recomendacion

Cada fuente puede tener una recomendacion global que determina como debe presentarse al productor.

| rule | Descripcion | Cuando aplica |
|---|---|---|
| `safe_to_recommend` | Fuente verificada, sin riesgos graves conocidos, con via de acceso publica | verified_primary_source con confidence_level high |
| `recommend_with_warning` | Fuente verificada pero con condiciones, limites o riesgos que requieren atencion | verified_primary_source con restrictions, o verified_institutional_source |
| `research_required` | Fuente identificada pero con datos pendientes de confirmar o via de acceso no clara | partially_confirmed o pending_verification |
| `not_applicable` | Fuente no recomendable para el perfil de proyecto o sin documentacion suficiente | outdated, o incompatible con formato/fase/territorio |

### 16.1 Mapa desde la investigacion

| Fuente | Recomendacion | Motivo |
|---|---|---|
| ICAA distribucion 051850 | safe_to_recommend | Ficha 2026 verificada, importes e intensidad conocidos |
| Navarra arts. 65.1/65.2/65 bis | safe_to_recommend | Normativa y procedimiento verificados |
| Art. 36 IS | safe_to_recommend | BOE consolidado verificado |
| Eurimages | recommend_with_warning | Reglamento verificado, pero deadlines y compatibilidad pendientes |
| ICAA generales | recommend_with_warning | Pagina accesible, pero codigo y ficha pendientes |
| ICAA guiones | recommend_with_warning | Convocatoria verificada, cuantia pendiente |
| ICAA cortometrajes realizados 051780 | safe_to_recommend | Ficha 2026 verificada |
| ICAA cortometrajes sobre proyecto | recommend_with_warning | Pagina accesible, ficha pendiente |
| Ibermedia | recommend_with_warning | Marco institucional verificado, detalle por linea pendiente |
| Creative Europe MEDIA | research_required | Fuente institucional verificada, pero detalle por call pendiente |
| Canarias | research_required | Cifras institucionales pendientes de contraste normativo |
| ICAA selectivas | research_required | Convocatoria 2026 no verificada |
| RTVE | research_required | Via de acceso no verificada |
| Mediaset / Telecinco Cinema | research_required | Fuente corporativa no localizada |
| private_equity | not_applicable | Sin fuentes documentadas en la investigacion actual |
| gap_financing | not_applicable | Sin fuentes documentadas en la investigacion actual |

## 17. Ejemplos de salida para productor

Cada ejemplo muestra como CID presentaria una recomendacion estructurada a un productor. Todos los datos mostrados proceden exclusivamente de fuentes documentadas en los informes de investigacion.

### 17.1 Largometraje espanol independiente 2,5M EUR

Perfil:
- pais: Espana
- formato: largometraje ficcion
- fase: produccion
- presupuesto: 2,5M EUR
- empresa: productora independiente registrada en ICAA

Recomendacion CID:

Prioridad alta (safe_to_recommend):
- Art. 36 IS produccion espanola (30% primer millon + 25% exceso; hasta 20M EUR por produccion)
- ICAA ayudas generales largometraje si convocatoria vigente (PENDIENTE cuantia por proyecto)
- ICAA distribucion si aplica en fase de salida (150.000 EUR limite; intensidad 50%)

Prioridad media (recommend_with_warning):
- Ayuda autonomica segun territorio (verificar convocatoria y compatibilidad)
- Navarra tax incentive si el proyecto puede cumplir 40% gasto navarro

Requiere investigacion (research_required):
- RTVE / broadcaster si se localiza via de entrada
- Movistar Plus+ si el perfil editorial encaja

Riesgos:
- Doble computo de gasto entre Art. 36 e ICAA
- Intensidad maxima de ayudas acumuladas
- ICAA generales sin cuantia por proyecto verificada

### 17.2 Coproduccion Espana-Francia 3,5M EUR

Perfil:
- coproduccion bilateral ES-FR
- formato: largometraje ficcion
- fase: produccion
- presupuesto: 3,5M EUR

Recomendacion CID:

Prioridad alta:
- Art. 36 IS (parte espanola; 30/25%; hasta 20M EUR)
- Incentivo fiscal frances equivalente (CID no ha investigado Francia en esta fase)
- ICAA generales si el proyecto mantiene nacionalidad espanola y cumple requisitos

Prioridad media:
- Eurimages (hasta 500.000 EUR; exige >= 2 productores independientes de distintos estados miembros)
- Coproduccion europea como marco habilitante

Requiere investigacion:
- Creative Europe MEDIA si hay call compatible
- Corredor ES-FR como marco bilateral (tratado no verificado en esta investigacion)

Riesgos:
- Nacionalidad de obra e implicaciones en ayudas nacionales
- Aprobacion formal de coproduccion ante autoridades competentes
- Reparto de porcentajes y elegibilidad por territorio
- Compatibilidad Eurimages con fuentes espanolas PENDIENTE DE VERIFICACION

### 17.3 Documental 300K EUR

Perfil:
- formato: documental
- fase: desarrollo/produccion
- presupuesto: 300K EUR

Recomendacion CID:

Prioridad alta:
- ICAA guiones si esta en fase de escritura (cuantia por proyecto PENDIENTE DE VERIFICACION)
- Ayudas autonomicas al desarrollo / produccion documental segun territorio

Prioridad media:
- Ibermedia codesarrollo si hay coproductor iberoamericano
- Creative Europe MEDIA desarrollo si hay call compatible

Requiere investigacion:
- RTVE / broadcaster cultural si encaja editorialmente
- Ibermedia coproduccion si hay socio iberoamericano

Riesgos:
- Presupuesto pequeno puede no justificar costes de compliance de fondos europeos
- Ayudas ICAA para documental no verificadas como linea separada (depende de convocatoria general)
- Acceso a broadcaster cultural no verificado

### 17.4 Serie 6x50 con aspiracion iberoamericana

Perfil:
- formato: serie 6 episodios 50 min
- fase: desarrollo
- presupuesto: PENDIENTE DE VERIFICACION

Recomendacion CID:

Prioridad alta:
- Art. 36 IS (hasta 10M EUR por episodio si cumple requisitos)
- Ibermedia codesarrollo series (convocatoria 2026 localizada; requiere empresas de >= 2 paises iberoamericanos)

Prioridad media:
- Creative Europe MEDIA desarrollo / distribucion si hay call compatible
- Movistar Plus+ originales si el perfil editorial encaja

Requiere investigacion:
- ICAA (depende de formato y convocatoria; series no estan explicitamente cubiertas en las lineas generales verificadas)
- Broadcasters internacionales
- Corredores de coproduccion

Riesgos:
- ICAA no verificado para series como linea independiente
- Acceso a plataforma sin via publica verificada
- Ibermedia requiere socio iberoamericano

## 18. Campos pendientes de verificacion

Los siguientes campos no tienen datos suficientes en la investigacion actual y deben marcarse como PENDIENTE DE VERIFICACION en cualquier implementacion futura:

- `FundingSource.eligible_budget_type` cuando no se ha localizado desglose oficial
- `FundingEstimate.estimated_amount` para fuentes sin cuantia publicada
- `FundingEstimate.estimated_percentage` para fuentes sin intensidad oficial
- `FundingCompatibility.compatibility_level` cuando no hay fuente oficial que confirme la combinacion
- `EligibilityRule.expected_value` cuando el valor exacto no aparece en la fuente oficial accesible
- `RiskFlag.mitigation_hint` cuando no se ha documentado una accion concreta de mitigacion

Ademas, las siguientes fuentes no tienen datos suficientes en la investigacion actual:
- RTVE — via publica de entrada para productores
- Mediaset / Telecinco Cinema — via corporativa estable
- Atresmedia Cine — criterios de acceso publicos
- Movistar Plus+ — criterios de commissioning para externos
- private_equity — fuentes especificas para audiovisual espanol
- gap_financing — instrumentos documentados para cine espanol
- presale — mercado y practicas estandar no documentadas en esta investigacion

## 19. Proxima fase sugerida: CID.FINANCE.INTELLIGENCE.DATASET.SPEC.1

Con la taxonomia definida y las fuentes de Espana, Europa e Iberoamerica clasificadas, la siguiente fase logica es:

CID.FINANCE.INTELLIGENCE.DATASET.SPEC.1

Objetivo:
- Disenar el dataset base CID con las fuentes documentadas, siguiendo los campos de FundingSource (seccion 5).
- Incluir tabla de EligibilityRules asociadas a cada fuente.
- Incluir tabla de RiskFlags por fuente.
- Incluir tabla de FundingCompatibility entre pares de fuentes.
- Version 1 del dataset debe contener solo fuentes con verification_status >= partially_confirmed.
- Fuentes pending_verification y outdated se incorporan en versiones posteriores cuando se verifiquen.

Formato de entrega: CSV o JSON con estructura plana (una fila por fuente), mas tablas auxiliares para reglas, riesgos y compatibilidades.

El dataset debe permitir:
- Filtrar fuentes por pais, formato, fase, tipo.
- Obtener reglas de elegibilidad de una fuente.
- Obtener riesgos de una fuente.
- Consultar compatibilidad entre dos fuentes.
- Estimar cobertura financiera potencial con escenarios conservative, base_case y optimistic.

No incluir:
- Implementacion de endpoints ni codigo de backend.
- Motor de reglas ejecutable.
- Conexion con base de datos.
- Interfaz de usuario.

Apendice A. Origen de datos por seccion

| Seccion | Origen | verification_status |
|---|---|---|
| 14.1 ICAA generales | spain_funding_sources_research_v1.md tabla 3.1 | partially_confirmed |
| 14.2 ICAA distribucion | spain_funding_sources_research_v1.md tabla 3.1 | verified_primary_source |
| 14.3 ICAA guiones | spain_funding_sources_research_v1.md tabla 3.1 | verified_primary_source |
| 14.4 Eurimages | europe_funding_sources_research_v1.md seccion 3 | verified_primary_source |
| 14.5 Creative Europe MEDIA | europe_funding_sources_research_v1.md seccion 4 | verified_institutional_source |
| 14.6 Ibermedia | europe_funding_sources_research_v1.md seccion 5 | verified_institutional_source |
| 14.7 Navarra | spain_funding_sources_research_v1.md seccion 6 | verified_primary_source |
| 14.8 Canarias | spain_funding_sources_research_v1.md seccion 5 | partially_confirmed |
| 15 Matriz compatibilidad | spain_funding_sources_research_v1.md seccion 3.5 + europe_funding_sources_research_v1.md seccion 10 | conceptual / pending_verification |
| 16 Reglas recomendacion | cid_funding_intelligence_data_model_v1.md seccion 14 | basado en verification_status |
| 17 Ejemplos productor | spain + europe + data model documents | conceptual / PENDIENTE DE VERIFICACION |
