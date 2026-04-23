# Sprint 3 Locking Specification: Visual Engine V1

## 1. Objetivo del Sprint
Conectar la estructura narrativa (S2) con la capacidad de ejecución técnica (S1) para permitir la **previsualización visual trazable**, permitiendo al usuario generar, gestionar y seleccionar activos visuales vinculados a cada escena del proyecto.

## 2. Alcance Exacto
### Entra:
- **Jerarquía Visual:** Relación funcional `Scene -> Shot -> Asset`.
- **Scene Visual Workspace:** Interfaz dividida para ver el guion de la escena y su galería de activos simultáneamente.
- **Shot Management:** Creación de planos (Shots) dentro de una escena como contenedores de renders.
- **Generación Real (Still):** Integración con el Core Orchestrator para lanzar renders de imagen fija basados en la descripción del Shot.
- **Selección de Referencia:** Acción de marcar un Asset como "Key Visual" o "Favorito".

### No Entra:
- **Video Production:** No hay generación de vídeo ni secuencias temporales.
- **Consistencia Multiphase:** No hay re-renderizado automático para mantener consistencia (eso es S4).
- **Control de Cámara Avanzado:** No hay manipuladores 3D ni control de nodos manual.

## 3. Vistas Finales
1.  **Visual Pipeline Overview:** Tablero de producción que muestra el estado visual de todas las escenas del proyecto (miniaturas de favoritos).
2.  **Scene Visual Workspace:** Vista principal de trabajo. Lado izquierdo: Guion y Personajes. Lado derecho: Área de Renders y Galería de Shots.
3.  **Shot Drawer/List:** Lista lateral o inferior de planos definidos para la escena activa.
4.  **Asset Gallery:** Rejilla de todos los resultados generados para un Shot específico.
5.  **Asset Detail Card:** Vista ampliada de un activo con metadatos técnicos (Model, Seed, Time, Backend).

## 4. Acciones del Usuario por Vista
- **Visual Pipeline Overview:** Ver de un vistazo qué escenas ya tienen imagen de referencia y cuáles están vacías.
- **Scene Visual Workspace:** Crear un "New Shot", escribir el "Visual Prompt" (derivado del guion), elegir un Workflow base y lanzar "Render".
- **Shot Gallery:** Comparar múltiples versiones (Assets) de un mismo Shot y marcar la mejor como "Referencia".
- **Asset Detail:** Descargar imagen, ver detalles técnicos del render.

## 5. Nivel de Control (MVP)
- **Generación:** El usuario pulsa "Render" -> El sistema usa el CI Orchestrator -> El Asset aparece en la galería del Shot con estado "Running" (vía S1 Queue).
- **Selección:** Un click para marcar como "Favorite". Este activo es el que se mostrará en el *Project Overview*.

## 6. Datos Demo Obligatorios
- **Scene Demo:** "La llegada al planeta" (Escena 02 de *The Robot's Journey*).
- **Shots Demo:** Al menos 3 planos pre-creados (Wide Shot, Close-up Robot, Arrival Landscape).
- **Assets Demo:** Al menos 2 variaciones visuales por plano para demostrar la capacidad de selección.

## 7. Estados Vacíos / Placeholders
- **Empty Shot:** "No visual assets generated yet. Click Render to start."
- **Asset Detail Placeholder:** Mostrar campos de "Cost/Credits" (Visual solo, S4 logic).
- **Composition Tool Placeholder:** Icono deshabilitado de "Frame Control" (Coming soon).

## 8. Percepción del Producto
- **Continuidad:** El productor siente que la imagen que está viendo pertenece *a esa línea de guion*.
- **Control:** El usuario "manda" renders al backend sin salir de su flujo creativo.
- **Trazabilidad:** Cada imagen tiene "DNI": sabe a qué proyecto, escena y plano pertenece.

## 9. Criterios de Terminado (DoD)
- [ ] El modelo de datos soporta `Scene -> Shot -> Asset`.
- [ ] La vista "Scene Visual Workspace" integra el editor de guion con el lanzador de renders.
- [ ] El lanzador de renders envía la tarea correctamente a la cola de S1 y recibe el Asset.
- [ ] Se puede marcar un Asset como "Favorite" y esto actualiza el visual del Pipeline Overview.
- [ ] La demo externa es estable: "Crear un plano, renderizarlo y seleccionarlo como favorito en menos de 2 minutos".

## 10. Decisiones Congeladas
1.  **Shot Container:** Se bloquea que la unidad básica de generación es el "Shot".
2.  **Workflow Simplificado:** La selección de workflow en S3 es por dropdown de "Presets" (Still Portrait, Still Landscape, Concept Art). No se abren parámetros complejos de nodos.
3.  **Local Storage focus:** Los activos se almacenan y sirven localmente desde el servidor de orquestación.
