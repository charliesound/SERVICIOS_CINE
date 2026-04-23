# SOP: Ingesta Federada + Document Understanding en AILinkCinema

## 1. Misión y Objetivo
Establecer un sistema de orquestación de datos que indexe el almacenamiento local/remoto del cliente (Ingesta Federada) y extraiga información estructurada de documentos de producción (Document Understanding) sin centralizar binarios pesados, manteniendo la soberanía de los datos en la infraestructura del cliente.

---

## 2. Arquitectura de Ingesta Federada

### 2.1 Componentes de Almacenamiento
- **StorageSource**: Punto de entrada (Local Path, SMB, SFTP). Define *cómo* conectarse.
- **StorageAuthorization**: Registro de consentimiento con scopes de tiempo y ruta. Mínimo privilegio.
- **WatchPath**: Sub-directorios específicos dentro del Source que son monitoreados.

### 2.2 Motor de Escaneo (Scan Engine)
- Operaciones idempotentes: No re-indexa archivos sin cambios (uso de hashes de tamaño/modificación).
- Descubrimiento asíncrono: Los escaneos se ejecutan en segundo plano para no bloquear la API.
- Trazabilidad: Cada hallazgo se registra como un `MediaAsset` o `DocumentAsset`.

---

## 3. Arquitectura de Document Understanding (DU)

### 3.1 Pipeline de Procesamiento
1. **Detección**: Identificación del tipo de archivo (Imagen, PDF, Excel).
2. **Extracción Raw**: 
   - Imágenes/PDF Escaneado -> OCR (Tesseract / Ollama Vision).
   - PDF Nativo/Word -> Text Extraction.
   - Excel/CSV -> Tabular Parsing (Pandas).
3. **Clasificación**: Motor heurístico o LLM que identifica si es un `camera_report`, `sound_report`, etc.
4. **Estructuración**: Mapeo de campos extraídos a un payload JSON estandarizado.
5. **Human-in-the-Loop (HITL)**: Interfaz de validación donde el operador confirma o corrige la interpretación.

### 3.2 Relaciones de Dominio
Los datos extraídos deben vincularse automáticamente a:
`PROJECT` -> `SHOOTING_DAY` -> `SEQUENCE` -> `SCENE` -> `SHOT` -> `ASSET`

---

## 4. Estrategia de Conectividad Universal

### 4.1 Abstracción de Proveedores
- Uso de una interfaz `StorageProvider`.
- **MVP**: Soporte para rutas montadas en el S.O. (Windows Drive Letters o Linux Mount Points).
- **Fase 2**: Implementaciones nativas de protocolos (SMB, SFTP) para evitar dependencias de montajes externos.

### 4.2 Gestión de Secretos
- Credenciales almacenadas de forma segura (encriptadas o vía variables de entorno).
- Nunca almacenar contraseñas de NAS en texto plano en la DB.

---

## 5. Estados Críticos

### Authorization States
`PENDING` -> `ACTIVE` -> `EXPIRED` -> `REVOKED`

### Asset States
`DISCOVERED` -> `PROCESSING` -> `INDEXED` -> `ARCHIVED`

### Document Review States
`UNPROCESSED` -> `SUGGESTED` -> `VALIDATED` -> `REJECTED`

---

## 6. Restricciones y Trampas Conocidas (LECCIONES APRENDIDAS)

> [!WARNING]
> - **OCR imperfecto**: Nunca automatizar la consolidación de datos de un parte de cámara sin revisión humana. El OCR fallará en letra manuscrita o fotocopias de baja calidad.
> - **Rendimiento**: Escanear un NAS de 100TB puede tumbar el sistema si no se limita el paralelismo y la profundidad de escaneo.
> - **Binarios Pesados**: NO copiar binarios al servidor de AILinkCinema a menos que se solicite un proxy o miniatura (thumbnail) para visualización.
> - **Conectividad**: Las conexiones SMB en redes inestables (Tailscale/VPN) pueden causar timeouts. Implementar reintentos con backoff exponencial.

---

## 7. Flujo Operativo Consolidado
1. Admin de Organización registra `StorageSource`.
2. Propietario del Storage otorga `Authorization`.
3. Sistema escanea `WatchPaths`.
4. Sistema detecta archivos nuevos -> Crea `Asset`.
5. Si es Documento -> Dispara `DU Task`.
6. Usuario revisa `Extraction` en el Dashboard.
7. Al validar -> El sistema actualiza los modelos de `Scene/Shot` con los nuevos datos (ej. "Mejor Toma").
