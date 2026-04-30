# Funding Opportunities Dashboard MVP

## Objetivo

Construir la primera interfaz operativa para consumir visualmente el matcher financiero enriquecido por proyecto sin romper matcher clasico, budget, dossier ni presentation.

## Decisiones cerradas

- La pagina principal reutiliza la ruta existente de funding por proyecto y pasa a priorizar oportunidades enriquecidas.
- Se conserva acceso a financiacion privada existente dentro de la misma pantalla para no romper el flujo previo.
- El dashboard consume `matches-rag`, `checklist`, `profile`, `matcher-status` y `evidence` ya disponibles.
- Se amplian `matches` y `matches-rag` con filtros, ordenacion y paginacion opcional sin alterar el contrato antiguo cuando no se envian parametros.

## Contrato visual MVP

- Resumen superior con proyecto, funding gap y conteos por fit.
- Barra de filtros con busqueda, fit level, region, orden y paginacion.
- Lista de oportunidades con score, fit level, resumen corto y CTA de detalle.
- Panel lateral o modal con rationale, blockers, faltantes, acciones y evidencia.
- Boton stub de tracking sin workflow real.

## Restricciones activas

- No activar conectores privados ni automation.
- No abrir billing, reporting ni matcher v3.
- No recalcular automaticamente al entrar; solo boton explicito de refresco.
- Mantener tenant isolation estricta en dashboard y evidencia.
