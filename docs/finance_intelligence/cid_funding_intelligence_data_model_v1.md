# CID Funding Intelligence — Data Model v1

## 1. Resumen ejecutivo
CID Funding Intelligence v0 se plantea como un motor documental y de decision asistida para identificar, clasificar y priorizar fuentes de financiacion audiovisual compatibles con un proyecto concreto.

Su objetivo no es sustituir asesoria legal, fiscal o financiera, sino:
- estructurar informacion dispersa
- filtrar fuentes potenciales por encaje
- separar datos confirmados de datos pendientes
- estimar cobertura financiera potencial
- visibilizar riesgos antes de recomendar una combinacion de fuentes

Esta v1 se apoya en la investigacion base de Espana y propone un modelo conceptual interoperable para evolucionar hacia datasets, scoring y endpoints futuros.

## 2. Objetivo del motor de financiación
El motor CID Funding Intelligence debe permitir:
- mapear fuentes publicas, fiscales, corporativas y privadas
- determinar elegibilidad preliminar por proyecto
- estimar potencial de cobertura financiera
- marcar compatibilidades e incompatibilidades
- separar financiacion confirmada, potencial y no verificable
- priorizar fuentes segun encaje legal, territorial, documental y estrategico
- producir salidas comprensibles para productores, ejecutivos y equipos de desarrollo de negocio

Resultado esperado en v0:
- una recomendacion estructurada, no automatica ni vinculante
- un estado claro de verificacion
- una lista de riesgos y pendientes antes de cualquier decision
- ninguna conclusion legal, fiscal o financiera definitiva sin revision humana especializada

## 3. Inputs necesarios del proyecto

### 3.1 Campos base
- `country`
- `region`
- `budget`
- `genre`
- `format`
- `duration`
- `language`
- `project_phase`
- `production_company`
- `coproduction`
- `planned_eligible_spend`
- `attached_talent`
- `exploitation_windows`

### 3.2 Descripción funcional de cada input
- `country`
  - pais principal del proyecto o de la estructura de produccion
- `region`
  - comunidad autonoma, territorio foral o area de rodaje principal
- `budget`
  - presupuesto total estimado del proyecto
- `genre`
  - ficcion, documental, animacion, entretenimiento u otro formato elegible
- `format`
  - largometraje, cortometraje, serie, miniserie, documental unitario, etc.
- `duration`
  - metraje o estructura episodica
- `language`
  - idioma original o idiomas principales
- `project_phase`
  - desarrollo, produccion, postproduccion, distribucion, promocion, service production
- `production_company`
  - empresa productora principal y datos de elegibilidad basica
- `coproduction`
  - existencia, paises implicados y tipo de coproduccion
- `planned_eligible_spend`
  - gasto elegible previsto, desglosado por territorio si es posible
- `attached_talent`
  - talento vinculado relevante para elegibilidad o atractivo editorial
- `exploitation_windows`
  - cine, TV, plataforma, ventas internacionales, festivales, educativo, etc.

### 3.3 Campos complementarios recomendados
- `production_type`
- `shooting_territories`
- `tax_residence_of_vehicle`
- `icaa_registration_status`
- `cultural_certificate_status`
- `expected_shoot_dates`
- `expected_delivery_date`
- `financing_already_closed`
- `requested_sources`

## 4. Tipos de fuentes
El modelo debe contemplar, como minimo, los siguientes `source_type`:
- `public_grant`
- `tax_incentive`
- `broadcaster`
- `platform`
- `coproduction`
- `private_equity`
- `presale`
- `gap_financing`
- `regional_support`
- `european_fund`

### 4.1 Notas de uso
- `public_grant`: ayudas competitivas o nominativas de organismos publicos
- `tax_incentive`: deducciones, rebates o creditos fiscales
- `broadcaster`: participacion de televisiones
- `platform`: adquisicion, commissioning o participacion de plataformas
- `coproduction`: aportacion derivada de coproductor elegible
- `private_equity`: capital privado o inversor industrial
- `presale`: preventa territorial o por ventana
- `gap_financing`: cobertura del hueco financiero restante
- `regional_support`: apoyos institucionales territoriales no estrictamente fiscales
- `european_fund`: programas europeos o multilaterales

## 5. Entidad FundingSource

### 5.1 Definición conceptual
`FundingSource` representa una fuente concreta de financiacion o incentivo que CID puede mostrar, evaluar y relacionar con un proyecto.

### 5.2 Campos propuestos
- `id`
- `name`
- `country`
- `region`
- `source_type`
- `subtype`
- `project_phases`
- `eligible_formats`
- `eligible_applicants`
- `estimated_min_amount`
- `estimated_max_amount`
- `estimated_percentage`
- `currency`
- `requirements_summary`
- `required_documents_summary`
- `official_sources`
- `verification_status`
- `notes_for_cid`
- `active_status`

### 5.3 Reglas
- una `FundingSource` no debe contener cifras inventadas
- si no hay cifra confirmada, usar:
  - `null`
  - o `PENDIENTE DE VERIFICACIÓN` en capa documental
- `official_sources` debe aceptar varias URLs

## 6. Entidad EligibilityRule

### 6.1 Definición conceptual
`EligibilityRule` modela una condicion de encaje preliminar entre proyecto y fuente.

### 6.2 Tipos de regla recomendados
- territorio
- fase
- formato
- empresa solicitante
- gasto minimo
- gasto local
- certificado cultural
- registro ICAA
- idioma
- coproduccion
- ventana de explotacion
- limite presupuestario

### 6.3 Campos propuestos
- `id`
- `funding_source_id`
- `rule_type`
- `rule_label`
- `operator`
- `expected_value`
- `mandatory`
- `verification_level`
- `notes`

### 6.4 Ejemplos
- `rule_type: territory_fit`
- `operator: gte`
- `expected_value: 1000000`
- `mandatory: true`

## 7. Entidad VerificationStatus

### 7.1 Definición conceptual
`VerificationStatus` separa fuentes seguras, parciales y pendientes. Es critica para no inducir a error.

### 7.2 Estados mínimos
- `confirmed_primary_official`
- `confirmed_institutional_secondary`
- `partially_verified`
- `pending_verification`
- `outdated_possible_review_required`

### 7.3 Campos propuestos
- `code`
- `label`
- `description`
- `recommended_for_safe_output`
- `requires_human_review`

### 7.4 Política recomendada
- solo `confirmed_primary_official` y, con cautela, `confirmed_institutional_secondary` pueden aparecer como fuentes de alta confianza
- `partially_verified` debe llevar disclaimer
- `pending_verification` no debe aparecer como recomendacion segura

## 8. Entidad FundingEstimate

### 8.1 Definición conceptual
`FundingEstimate` es la estimacion CID de impacto financiero potencial de una fuente sobre un proyecto concreto.

### 8.2 Campos propuestos
- `project_id`
- `funding_source_id`
- `scenario`
- `eligible_spend`
- `estimated_amount`
- `estimated_percentage`
- `assumptions`
- `confidence_level`
- `verification_status`
- `blocked_by`

### 8.3 Escenarios recomendados
- `conservative`
- `base_case`
- `optimistic`

## 9. Entidad RiskAssessment

### 9.1 Definición conceptual
`RiskAssessment` sintetiza por que una fuente puede parecer atractiva pero no ser recomendable todavia.

### 9.2 Campos propuestos
- `project_id`
- `funding_source_id`
- `risk_type`
- `risk_level`
- `risk_summary`
- `mitigation_hint`
- `requires_professional_review`
- `verification_status`

### 9.3 Tipos mínimos
- `legal`
- `fiscal`
- `calendar`
- `documentation`
- `competition`
- `corporate_access`
- `verification`

## 10. Matriz de compatibilidad

### 10.1 Objetivo
La matriz debe ayudar a estimar si varias fuentes pueden convivir sin conflicto preliminar.

### 10.2 Compatibilidades orientativas

| Fuente A | Fuente B | Compatibilidad conceptual | Nota |
|---|---|---|---|
| public_grant | tax_incentive | posible | depende de limites de acumulacion |
| public_grant | broadcaster | posible | revisar exclusividades y ventanas |
| public_grant | platform | posible | revisar condiciones editoriales y territoriales |
| tax_incentive | tax_financier | posible | requiere estructura valida |
| coproduction | public_grant | posible | depende de convocatoria y territorio |
| presale | broadcaster | posible | puede coincidir o ser la misma familia de fuente |
| private_equity | gap_financing | posible | revisar prioridad de retorno |
| regional_support | european_fund | posible | revisar doble financiacion y elegibilidad |

### 10.3 Incompatibilidades o alertas frecuentes
- dos fuentes que exijan exclusividad editorial o de ventana
- combinaciones que superen intensidad maxima de ayudas
- financiadores vinculados no elegibles en estructuras fiscales
- gastos no compatibles entre territorio y naturaleza de incentivo

## 11. Scoring de encaje

### 11.1 Componentes mínimos
- `legal_fit`
- `project_fit`
- `budget_fit`
- `territory_fit`
- `timing_fit`
- `documentation_fit`
- `strategic_fit`

### 11.2 Descripción de cada componente
- `legal_fit`
  - si el proyecto parece cumplir la base normativa conocida
- `project_fit`
  - si la fuente encaja con fase, formato, genero y estructura del proyecto
- `budget_fit`
  - si el tamaño del proyecto encaja con la fuente
- `territory_fit`
  - si pais/region/gasto local encajan
- `timing_fit`
  - si el calendario del proyecto encaja con convocatoria o ventana
- `documentation_fit`
  - si el proyecto parece poder reunir la documentacion necesaria
- `strategic_fit`
  - si la fuente aporta valor real al plan financiero o comercial

### 11.3 Escala sugerida
- 0 a 100 por dimension
- score global ponderado

### 11.4 Ponderación inicial sugerida
- `legal_fit`: 25%
- `territory_fit`: 20%
- `project_fit`: 15%
- `documentation_fit`: 15%
- `timing_fit`: 10%
- `budget_fit`: 10%
- `strategic_fit`: 5%

### 11.5 Regla de bloqueo
Si `legal_fit` o `verification_status` estan por debajo de umbral minimo, la fuente no debe aparecer como recomendacion fuerte aunque el score agregado sea alto.

## 12. Cálculo de cobertura financiera

### 12.1 Campos mínimos
- `confirmed_financing`
- `potential_financing`
- `eligible_spend`
- `estimated_rebate`
- `funding_gap`

### 12.2 Definiciones
- `confirmed_financing`
  - financiacion ya cerrada o contractualmente confirmada
- `potential_financing`
  - suma prudente de fuentes elegibles no confirmadas
- `eligible_spend`
  - gasto que podria activar ayudas o incentivos
- `estimated_rebate`
  - estimacion de incentivo fiscal si hay base suficiente
- `funding_gap`
  - presupuesto total menos financiacion confirmada menos financiacion potencial prudente

### 12.3 Fórmula conceptual
`funding_gap = total_budget - confirmed_financing - conservative_potential_financing`

### 12.4 Reglas de prudencia
- no sumar dos veces la misma base elegible
- no considerar como cobertura segura una fuente `pending_verification`
- no mezclar escenarios optimistas con cobertura confirmada

## 13. Riesgos

### 13.1 Tipos mínimos
- `legal`
- `fiscal`
- `calendar`
- `documentation`
- `competition`
- `corporate_access`
- `verification`

### 13.2 Descripción
- `legal`
  - dudas de elegibilidad normativa
- `fiscal`
  - estructura societaria, territorializacion, limites o compatibilidades
- `calendar`
  - fuera de convocatoria o hitos temporales incompatibles
- `documentation`
  - falta de certificados, registros, auditorias o anexos
- `competition`
  - ayuda competitiva con baja previsibilidad
- `corporate_access`
  - broadcaster/plataforma sin via publica clara de acceso
- `verification`
  - fuente no confirmada o desactualizada

## 14. Reglas para no recomendar fuentes no verificadas como seguras
- una fuente `pending_verification` no debe recibir estado de “segura”
- una fuente `partially_verified` debe mostrarse con warning visible
- ninguna cifra sin fuente primaria o institucional clara puede presentarse como definitiva
- cualquier corporate source sin via publica o criterios verificables debe marcarse como `corporate_access risk`
- si una ayuda depende de convocatoria no verificada, el sistema debe decir:
  - `requiere validacion con convocatoria vigente`
- si una cifra viene de sintesis sectorial y no de norma primaria, debe indicarse:
  - `confirmada institucionalmente, pendiente de validacion legal/fiscal final`

## 15. Ejemplos de salida

Nota: los siguientes ejemplos son salidas conceptuales de producto. No implican elegibilidad legal o fiscal definitiva y no sustituyen verificacion profesional.

### 15.1 Largometraje español 2,5M€
- Perfil:
  - pais: España
  - formato: largometraje
  - fase: produccion
  - presupuesto: 2,5M EUR
- Salida conceptual CID:
  - prioridad alta:
    - incentivo fiscal estatal art. 36
    - ayudas ICAA produccion si convocatoria vigente lo permite
    - ayudas autonómicas segun territorio
  - prioridad media:
    - broadcaster / platform
    - financiador fiscal
  - riesgo:
    - compatibilidad de intensidad de ayudas
    - verificacion ICAA pendiente

### 15.2 Documental 300K€
- Perfil:
  - formato: documental
  - presupuesto: 300K EUR
- Salida conceptual CID:
  - prioridad alta:
    - desarrollo/produccion documental via ayudas publicas
    - incentivos fiscales si la estructura lo justifica
  - prioridad media:
    - coproduccion TV / cultural broadcasters
  - riesgo:
    - sobredimensionar costes de compliance para un proyecto pequeño

### 15.3 Coproducción España-Francia 3M€
- Perfil:
  - coproduccion internacional
  - 3M EUR
- Salida conceptual CID:
  - prioridad alta:
    - incentivo fiscal estatal espanol
    - fuente nacional y autonómica española compatible
    - componente coproductor extranjero
  - prioridad media:
    - broadcaster / platform
  - riesgo:
    - aprobacion formal de coproduccion
    - reparto de porcentajes y elegibilidad por territorio

### 15.4 Serie 6x50
- Perfil:
  - serie audiovisual
  - 6 episodios de 50 min
- Salida conceptual CID:
  - prioridad alta:
    - incentivo fiscal estatal por episodio
    - platform / broadcaster
  - prioridad media:
    - ayudas selectivas o territoriales si aplican
  - riesgo:
    - ventanas de explotacion y acceso corporativo

## 16. Propuesta futura de JSON schema

```json
{
  "project": {
    "country": "string",
    "region": "string",
    "budget": "number",
    "genre": "string",
    "format": "string",
    "duration": "string",
    "language": ["string"],
    "project_phase": "string",
    "production_company": "string",
    "coproduction": {
      "enabled": true,
      "countries": ["string"]
    },
    "planned_eligible_spend": "number",
    "attached_talent": ["string"],
    "exploitation_windows": ["string"]
  },
  "funding_sources": [
    {
      "id": "string",
      "name": "string",
      "source_type": "string",
      "verification_status": "string",
      "eligibility_rules": [],
      "estimate": {},
      "risks": []
    }
  ]
}
```

## 17. Propuesta futura de endpoints

Solo conceptual, sin codigo:

- `POST /funding-intelligence/evaluate-project`
  - recibe inputs del proyecto
  - devuelve fuentes potenciales, score y riesgos

- `GET /funding-intelligence/sources`
  - lista catalogo de fuentes

- `GET /funding-intelligence/sources/:id`
  - detalle de una fuente

- `POST /funding-intelligence/compatibility-check`
  - evalua combinacion preliminar de varias fuentes

- `POST /funding-intelligence/coverage-estimate`
  - calcula cobertura confirmada, potencial y gap

- `GET /funding-intelligence/verification-status`
  - devuelve estados y reglas de presentacion segura

## 18. Campos marcados como PENDIENTE DE VERIFICACIÓN
- importes exactos de lineas ICAA por convocatoria vigente
- calendarios y ventanas de solicitud ICAA
- criterios editoriales y vias publicas de acceso de RTVE
- criterios editoriales y vias publicas de acceso de Mediaset / Telecinco Cinema
- criterios de entrada verificables de Atresmedia Cine
- criterios de entrada verificables de Movistar Plus+
- intensidades territoriales fuera de Canarias y Navarra cuando no haya fuente primaria o institucional suficiente
- limites de acumulacion concretos por combinacion de ayudas en casos reales
- requisitos documentales finos de cada convocatoria autonómica

## Apéndice A. Principios operativos para CID
- no presentar una fuente como “segura” si no esta verificada
- no mostrar cifras cerradas sin fuente clara
- mantener separadas fuente, regla, estimacion y riesgo
- permitir lectura para productor y para asesor especializado
- priorizar prudencia sobre exuberancia comercial

## Apéndice B. Dependencias futuras del sistema
- dataset oficial versionado por pais/region
- motor de reglas editable
- capa de verificacion documental
- trazabilidad por fuente y fecha de consulta
- versionado de convocatorias y marcos fiscales
