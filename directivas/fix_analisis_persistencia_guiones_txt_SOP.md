# SOP: Fix Análisis y Persistencia de Guiones (TXT)

## 1. Objetivo
Asegurar que los guiones en formato TXT sean clasificados correctamente como `script`, evitando falsos positivos como `operator_note`, y garantizando que el texto se persista correctamente en `ProductionBreakdown` con el límite de 10,000 caracteres.

## 2. Diagnóstico de Clasificación Errónea
El sistema actual clasifica como `operator_note` si:
1.  `is_probable_screenplay` devuelve un score < 0.55.
2.  El texto contiene palabras clave como "department" u "operator".

**Problema:** La palabra "department" es ubicua en guiones (Art Department, Production Department), lo que causa que guiones cortos o con pocos encabezados de escena sean mal clasificados.

## 3. Plan de Acción

### 3.1 Refinamiento de Heurísticas de Guion (`src/services/script_document_classifier.py`)
-   Aumentar la sensibilidad de `is_probable_screenplay`.
-   Incluir variaciones de encabezados de escena (ej. "INTERIOR", "EXTERIOR" en español).
-   Ajustar pesos para que la longitud del texto y la presencia de personajes tengan más relevancia en guiones cortos.

### 3.2 Limpieza de Reglas de Clasificación (`src/services/document_understanding_service.py`)
-   Eliminar "department" de `DOC_TYPE_RULES["operator_note"]`. Es demasiado genérico.
-   Hacer las palabras clave de `operator_note` más específicas (ej. "camera operator", "sound operator").

### 3.3 Verificación de Persistencia (`src/services/script_intake_service.py`)
-   Confirmar que `run_analysis` trunca correctamente a 10,000 caracteres antes de guardar en `ProductionBreakdown.script_text`.
-   Asegurar que el `breakdown_json` se genere incluso si el script es corto.

### 3.4 Validación via Tests de Integración
-   Ejecutar `tests/integration/test_project_script_analysis_flow.py`.
-   Añadir un caso de prueba para un guion corto que mencione "department" para asegurar que NO se clasifique como `operator_note`.

## 4. Restricciones y Casos Borde
-   No modificar archivos en `OLD/` ni documentación histórica.
-   Mantener compatibilidad con SQLite (usado en el entorno de pruebas).
-   El límite de 10,000 caracteres es estricto para evitar problemas de rendimiento en la base de datos de producción.
