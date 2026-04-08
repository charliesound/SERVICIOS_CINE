# Estrategia de Embeddings (CINE AI PLATFORM)

## Contexto y Requisitos
- **Colección Qdrant:** `cine_project_context`
- **Dimensión requerida:** `384`
- **Uso Crítico:** Notes de proyecto, referencias de estilo, continuidad narrativa de secuencias y shots.
- **Restricción:** Solución local, cero latencia externa, mantenible sin ensuciar la infraestructura dockerizada (no más contenedores si no es estrictamente necesario).

## Evaluación de Opciones

1. **Microservicio Local Separado (ej. Ollama o contenedor Text-Embeddings-Inference):**
   - *Pros:* Desacopla la computación del backend puro.
   - *Contras:* Rompe la restricción de "No rehacer el stack privado". Añade un contenedor que monopoliza VRAM o CPU y exige mantener una imagen Docker nueva.

2. **Cálculo nativo en n8n:**
   - *Pros:* N8n gestiona el flujo del pipeline (ingest webhook y llamado a Qdrant).
   - *Contras:* N8n no puede correr modelos de ML directamente sin depender de nodos externos tipo Langchain contra Ollama/HuggingFace, lo que lleva al punto 1.

3. **Cálculo nativo en el Backend (FastAPI / FastEmbed) -> DECISIÓN TOMADA**
   - *Pros:* La API ya está programada en Python. Se puede integrar una librería ultraligera como `fastembed` (basada en ONNX) que no requiere compilar PyTorch ni dependencias CUDA masivas. Produce vectores estandarizados (ej. `BAAI/bge-small-en-v1.5` = 384 dimensiones) en milisegundos en CPU.
   - *Flujo:* Frontend -> Backend (Genera Vector ONNX) -> Llama al Webhook N8n enviando `vector[]` pre-calculado -> N8n ingesta en Qdrant.

## Tecnologías Elegidas
- **Librería Python:** `fastembed` (Ligero, rápido, cacheo local transparente en `storage/api/data/embeddings`).
- **Modelo de Lenguaje:** `BAAI/bge-small-en-v1.5` (Dimension: 384, Distancia: Cosine). Excelente para retrieval asimétrico (Queries cortas vs Notas largas).

## Artefactos Derivados Recomendados (Siguiente Bloque en OpenCode)
1. Inclusión de `fastembed` en `apps/api/requirements.txt` (o similar gestor de dependencias).
2. Un servicio de utilidad en `apps/api/src/services/embedder.py` o análogo, que exponga una función de unificación textual `embed_text(text: str) -> list[float]`.
3. Inyección lógica en el controlador de edición de notas de plano/secuencia:
   - Al hacer POST de la nota: Se genera embedding localmente.
   - Se despacha HTTP `POST` a n8n (o directo a qdrant, pero el mandato sugiere que N8n es el encargado del Ingest de `vector[]`).

## Estructura de Payload a Enviar a N8n

```json
{
  "project_id": "project-001",
  "sequence_id": "seq-010",
  "scene_id": "scene-020",
  "shot_id": "shot-030",
  "entity_type": "shot_note",
  "title": "Tensión narrativa",
  "content": "Plano que muestra la respiración contenida",
  "tags": ["tension", "close-up"],
  "source": "editorial_note",
  "created_at": "2026-04-03T20:15:00Z",
  "vector": [0.045, -0.012, 0.993, ..., 0.123] // Array flotante de len=384 generado por FastEmbed
}
```
