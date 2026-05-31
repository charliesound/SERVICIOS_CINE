# CID.RAG.ANSWER.ENDPOINT.DESIGN.1

## Objetivo
Diseñar el endpoint POST /api/projects/{project_id}/memory/answer para proporcionar respuestas basadas en recuperación (RAG) utilizando el contexto de los embeddings de memoria del CID.

## Flujo
1. El usuario envía una pregunta (question)
2. El sistema genera un embedding de la pregunta usando rag_embedding_service
3. Busca en la memoria vectorial (cid_memory) usando memory/search filtrado por organization_id y project_id
4. Recupera los fragmentos más relevantes como contexto
5. Envía el contexto + pregunta a Ollama con el modelo Qwen para generar una respuesta
6. Devuelve la respuesta con las fuentes utilizadas y metadatos

## Request propuesto
```json
{
  "question": "string (requerido, min_length=1, max_length=2000)",
  "limit": "integer (opcional, default=10, ge=1, le=50)",
  "source_types": "array[string] (opcional, valores permitidos: ['script_text', 'storyboard_shot', 'production_breakdown'])",
  "temperature": "float (opcional, default=0.7, ge=0.0, le=2.0)",
  "include_sources": "boolean (opcional, default=true)"
}
```

## Response propuesto
```json
{
  "answer": "string",
  "project_id": "string",
  "organization_id": "string",
  "model": "string",
  "sources": [
    {
      "id": "string",
      "score": "float",
      "source_type": "string",
      "source_id": "string",
      "source_table": "string",
      "title": "string",
      "text": "string",
      "chunk_index": "integer",
      "tags": "array[string]"
    }
  ],
  "usage": {
    "prompt_tokens": "integer",
    "completion_tokens": "integer",
    "total_tokens": "integer"
  }
}
```

## Seguridad
- organization_id se extrae del JWT (no se acepta del request) mediante la API de login del proyecto, no usando TEST_JWT
- project_id se obtiene de la ruta del endpoint
- Todos los filtros de búsqueda incluyen obligatoriamente organization_id + project_id
- Prohibida la búsqueda global sin filtros de tenant
- Prohibida la búsqueda cross-project sin privilegios administrativos específicos (no implementado en MVP)
- Validación de acceso al proyecto antes de procesar la request

## LLM MVP
- Modelo por defecto: qwen2.5:14B (equilibrio entre calidad y rendimiento)
- Alternativa: qwen2.5:32B (mayor calidad, mayor consumo de recursos)
- No usar por defecto: qwen2.5-coder:32B (especializado en código, no óptimo para respuestas narrativas)

## Prompt de sistema
```
Eres un asistente especializado en análisis cinematográfico y de guiones. Tu tarea es responder preguntas basándote exclusivamente en el contexto proporcionado.

Reglas:
1. Responde ÚNICAMENTE con la información del contexto proporcionado
2. NO inventes, supongas o agregues información externa
3. Diferencia claramente entre:
   - guion (texto completo del script)
   - storyboard (viñetas con imágenes y notas de dirección)
   - breakdown (desglose de producción con elementos técnicos)
4. Si el contexto no contiene suficiente información para responder, indica claramente: "No hay suficiente información en la memoria proporcionada para responder a esta pregunta."
5. Siempre cita las fuentes relevantes en tu respuesta cuando sea apropiado
6. Mantén un tono técnico pero accesible
```

## Servicios propuestos
- CIDRAGAnswerService: Orquesta el flujo completo RAG
- OllamaLLMService: Wrapper para interacción con Ollama (generación de respuestas)
- rag_embedding_service: Reutilizado para generar embeddings de preguntas
- qdrant_memory_service: Reutilizado para búsqueda en memoria vectorial

## Manejo de errores
- Sin memoria indexada para el proyecto: devolver 404 con mensaje indicativo
- Sin resultados relevantes en búsqueda: devolver respuesta indicando falta de contexto
- Ollama no disponible: devolver 503 con mensaje de servicio no disponible
- Timeout en generación: devolver 504 con mensaje de timeout
- Prompt demasiado largo (excede límite de modelo): devolver 400 con sugerencia de reducir limit

## Tests propuestos
- Construcción correcta del prompt con contexto y pregunta
- Inclusión correcta de fuentes en respuesta cuando include_sources=true
- Verificación de filtros tenant (organization_id + project_id) en búsquedas
- Mock de servicio Ollama para testing sin dependencia externa
- Comportamiento cuando no hay resultados de búsqueda suficientes
- Manejo de errores de conexión y timeout con Ollama

## Validación real
Proyecto QA para pruebas: 22e145780c004e4e848df9a8ffbea3d0
Pregunta de ejemplo: "¿Qué ocurre en la escena de la casa abandonada y qué planos de storyboard la representan?"
Validación mediante login API (no TEST_JWT) y despliegue con:
docker compose -f compose.base.yml -f compose.home.yml -f compose.data.yml --profile with-qdrant up -d --build backend

## GO/NO-GO para pasar a implementación
**GO** si:
- El diseño cumple con todos los requisitos funcionales y de seguridad
- Los flujos de datos son claros y no presentan cuellos de botella identificables
- El manejo de errores cubre los casos de fallo esperados
- Los servicios propuestos reutilizan componentes existentes cuando es apropiado
- El prompt de sistema garantiza respuestas basadas únicamente en contexto

**NO-GO** si:
- Existen riesgos de seguridad no mitigados (filtros tenant insuficientes)
- El flujo introduce dependencias circulares o complejidad innecesaria
- El manejo de errores es insuficiente para escenarios de producción
- El diseño viola principios de separación de responsabilidad
