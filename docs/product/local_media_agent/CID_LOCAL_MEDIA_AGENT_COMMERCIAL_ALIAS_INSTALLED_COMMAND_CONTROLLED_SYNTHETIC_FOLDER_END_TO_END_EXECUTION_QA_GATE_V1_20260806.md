# CID — QA Gate V1: Alias instalado `cid scan` E2E sobre carpeta sintética controlada

Fecha: 2026-08-06
Rama: `main`
Fase: QA Gate V1 (revalidación de la línea Readiness → Implementation → QA)

## 1. Objetivo

Revalidar formalmente, en una fase de QA independiente, el test E2E único autorizado que
ejecuta el alias instalado `/opt/SERVICIOS_CINE/.venv/bin/cid scan --input-root <carpeta>`
contra una carpeta sintética controlada de ficheros zero-byte bajo `/tmp`, verificando el
contrato completo del scanner read-only sin efectos secundarios y sin fugas de rutas o nombres.

## 2. Baseline verificado (preflight)

```text
BASELINE_BRANCH=main
BASELINE_HEAD=51a78e4015c6f87438448e1c5cc541af3feb7f98
BASELINE_ORIGIN_MAIN=51a78e4015c6f87438448e1c5cc541af3feb7f98
BASELINE_TREE=39a786964c2f9689cccdc1039711eaa15e20bf83
BASELINE_PARENT=a9aa5b7bdc4b177e3d2f46039d05667b39992e24
BASELINE_AHEAD_COUNT=0
BASELINE_BEHIND_COUNT=0
BASELINE_WORKTREE_CLEAN=True
BASELINE_INDEX_CLEAN=True
BASELINE_UNTRACKED_FILE_COUNT=1 (solo el test E2E nuevo)
BASELINE_DIFF_CHECK_CLEAN=True
```

Tag vigente (lightweight, apuntando al baseline):
`cid-dev-stable-local-media-agent-read-only-folder-scanner-commercial-alias-installed-command-qa-reopened-revalidation-v1-20260805`

## 3. Identidad del test bajo QA

Archivo único autorizado (no se modifica en esta fase):

```text
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_commercial_alias_installed_command_controlled_synthetic_folder_end_to_end_execution_gate_v1.py
```

```text
TEST_FILE_LINES=192
TEST_FILE_BYTES=4973
TEST_FILE_SHA256=aa587b4f733b1ab23abde7f39ce0d4bf9c31e8445d48458240a3fc20d450a93d
```

Nota de trazabilidad: el encargo de fase declaraba `TEST_FILE_LINES=194` y
`TEST_FILE_BYTES=5019` como metadatos esperados. La medición canónica de esta fase
(`wc -l`/`wc -c` sobre el archivo con SHA-256 exactamente igual al hash obligatorio
`aa587b4f…`) devuelve 192 líneas y 4973 bytes. El hash es la identidad autoritativa y
coincide byte a byte; los conteos de líneas/bytes del encargo eran metadatos erróneos
arrastrados de la fase Implementation. No se modifica el archivo: cualquier cambio de
líneas/bytes alteraría el hash aprobado.

## 4. Revisión estructural del test

```text
IMPORTS= ['__future__', 'json', 'os', 'pathlib', 'shutil', 'subprocess'] (solo stdlib)
FUNC_COUNT= 4 (3 helpers + 1 test)
HELPERS= ['_build_synthetic_tree', '_run_installed_cid', '_remove_synthetic_tree']
TEST_FUNCS= ['test_installed_cid_scan_runs_end_to_end_on_controlled_synthetic_folder']
TEST_FUNC_COUNT_OK= True
STDLIB_ONLY= True
SUBPROCESS_RUN_COUNT= 1
SUBPROCESS_CALLS= [{'shell': False, 'cwd': '/tmp', 'timeout': 30}]
SUBPROCESS_CONTRACT_OK= True
RM_TREE_PRESENT= True
OWNERSHIP_MARKER_USED= 1 (.cid_test_owned)
HAS_FINALLY= True
HAS_PREEXISTING_ROOT_GUARD= True ("pre-existing synthetic root must not be removed")
HAS_RM_GUARD= True ("refusing to remove an unexpected path")
PYTHONDONTWRITEBYTECODE_IN_ENV= True
FORBIDDEN_MODULES_IMPORTED= False
```

Guardas de seguridad verificadas en el código:
- El test aborta si la raíz sintética ya existía antes de empezar (nunca elimina datos ajenos).
- `_remove_synthetic_tree` solo elimina si `created_by_test=True` y tras validar que la ruta es exactamente `/tmp/cid-synthetic-folder-e2e-v1`.
- `subprocess.run` único, `shell=False`, `cwd=/tmp`, `timeout=30`, entorno saneado.
- No se importan módulos de producción ni de terceros.

## 5. Carpetas sintéticas de control

```text
SYNTHETIC_ROOT=/tmp/cid-synthetic-folder-e2e-v1
SYNTHETIC_DIRECTORIES=8 subdirectorios (video, audio, image, mixed, empty, nested, nested/level01, nested/level01/level02)
SYNTHETIC_FILES=10 (MOV, mp4, WAV, flac, JPG, dng, txt, xml, no_extension, mxf)
SYNTHETIC_FILES_ALL_ZERO_BYTE=True
SYNTHETIC_FILES_REAL_MEDIA=False
SYNTHETIC_SYMLINKS=0
```

Justificación zero-byte: el scanner solo lee metadatos de filesystem (`lstat`), nunca abre
contenidos (`file_contents_opened=False`); los ficheros zero-byte son suficientes y evitan
usar material real.

## 6. Ejecución dirigida del test E2E

Comando:

```text
PYTHONPATH=src /opt/SERVICIOS_CINE/.venv/bin/python -m pytest -v -s --tb=long \
  tests/unit/test_cid_local_media_agent_read_only_folder_scanner_commercial_alias_installed_command_controlled_synthetic_folder_end_to_end_execution_gate_v1.py
```

Resultado:

```text
SYNTHETIC_ROOT_EXISTS_BEFORE=NO
1 passed, 1 warning in 0.25s
SYNTHETIC_ROOT_EXISTS_AFTER=NO
```

Warning pre-existente no bloqueante (`PytestConfigWarning: Unknown config option: asyncio_mode`).

## 7. Salida exacta emitida por el alias instalado

Capturada dentro del propio test entre marcadores `E2E_STDOUT_BEGIN`/`E2E_STDOUT_END`
(871 bytes, una sola línea, `\n` final único):

```json
{"depth_summary":{"direct_child_depth":1,"max_depth":8,"max_observed_depth":4,"root_depth":0},"errors":[],"extension_summary":{".dng":1,".flac":1,".jpg":1,".mov":1,".mp4":1,".mxf":1,".txt":1,".wav":1,".xml":1},"input_label":"SANITIZED_LOCAL_FOLDER_INPUT","privacy":{"artifact_written":false,"content_hashes_computed":false,"database_used":false,"ffmpeg_executed":false,"ffprobe_executed":false,"file_contents_opened":false,"network_used":false,"original_media_modified":false,"saas_used":false,"subprocess_used":false},"scanner_summary":{"directories_seen":9,"files_seen":10,"max_depth":8,"max_errors":100,"max_files":5000,"max_observed_depth":4,"media_candidates":7,"non_media_files":3,"symlinks_rejected":0,"total_bytes":0,"truncated":false},"schema_version":"cid.local_media_agent.read_only_folder_scanner.v1","status":"READ_ONLY_FOLDER_SCAN_COMPLETED","warnings":[]}
```

Fidelidad confirmada: el JSON capturado en esta QA es **byte-idéntico** al emitido en la
fase Implementation (`diff` sin diferencias; SHA-256 `85a783c04f134e7d0e612350e8bb1598b20dd72bb39af1757c6be04e71bd3047`).
El propio test además aserta igualdad exacta de bytes (`result.stdout == json.dumps(..., sort_keys=True, separators=(",",":")) + "\n"`).

## 8. Contrato de salida verificado

```text
STATUS=READ_ONLY_FOLDER_SCAN_COMPLETED
EXIT_CODE=0
STDERR_EMPTY=True
OUTPUT_ONE_LINE=True
OUTPUT_TRAILING_NEWLINE=exactamente 1
OUTPUT_SORT_KEYS=True
OUTPUT_SEPARATORS=(",",":")
SCHEMA_VERSION=cid.local_media_agent.read_only_folder_scanner.v1
INPUT_LABEL=SANITIZED_LOCAL_FOLDER_INPUT (nunca la ruta real)
```

Manifest coincidente con el contrato:
- `scanner_summary`: files_seen=10, directories_seen=9, media_candidates=7, non_media_files=3, symlinks_rejected=0, total_bytes=0, truncated=False, max_depth=8, max_errors=100, max_files=5000, max_observed_depth=4.
- `depth_summary`: root_depth=0, direct_child_depth=1, max_depth=8, max_observed_depth=4.
- `extension_summary` ordenada: .dng .flac .jpg .mov .mp4 .mxf .txt .wav .xml, cada una con conteo 1.
- `warnings=[]`, `errors=[]`.
- Extensiones en mayúsculas (.MOV .WAV .JPG) reconocidas vía `suffix.lower()`.

## 9. Seguridad y privacidad

```text
original_media_modified=false
file_contents_opened=false
content_hashes_computed=false
ffprobe_executed=false
ffmpeg_executed=false
subprocess_used=false
network_used=false
database_used=false
saas_used=false
artifact_written=false
```

Ausencia de fugas verificada dentro del test: la ruta absoluta `/tmp/cid-synthetic-folder-e2e-v1`
y todos los nombres de fichero sintéticos (`shot01.MOV`, `shot02.mp4`, `recorder01.WAV`,
`ambience.flac`, `still01.JPG`, `raw01.dng`, `notes.txt`, `project.xml`, `no_extension`,
`nested_clip.mxf`) NO aparecen en stdout ni stderr.

## 10. QA ampliada (lista cerrada de 9 archivos)

Mismo set de la fase Implementation: la lista cerrada de 8 archivos del dominio
read-only folder scanner documentada en el QA Gate V1 anterior (20260805), más el nuevo
test E2E. Comando y resultado:

```text
1 passed, 1 warning in 0.25s   (E2E dirigido, ver sección 6)
179 passed, 1 warning in 1.85s (QA ampliada, 9 archivos)
27 passed, 1 warning in 0.27s  (contrato vigente del alias comercial)
```

Archivos de la QA ampliada:

```text
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_commercial_alias_implementation_gate_v1.py
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_commercial_alias_readiness_gate_v1.py
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_cli_implementation_gate_v1.py
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_cli_readiness_gate_v1.py
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_implementation_gate_v1.py
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_package_entrypoint_controlled_implementation_v1.py
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_qa_gate_v1.py
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_readiness_gate_v1.py
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_commercial_alias_installed_command_controlled_synthetic_folder_end_to_end_execution_gate_v1.py
```

## 11. Inmutabilidad post-ejecución

Hashes recalculados tras todas las pruebas (idénticos a los registrados antes de la QA y
en fases anteriores):

```text
scripts/local_media_agent/cid_cli.py                          f48ce145afef969a2fc2866ce1b40f50cd699f3ea3d2bfa96d1454337de399b2
scripts/local_media_agent/read_only_folder_scanner_cli.py     ec9f4714597cd96d2f79640bff51110844bcb4c9106a07e58359e286a99cff6d
scripts/local_media_agent/read_only_folder_scanner.py         16a4fc52f3fa57b6469bb36ed30400ec26468a9435aad244582a0892fa810a05
.venv/bin/cid                                                  ed0909b210356d4861fdf2781f8305ddbe83ce056bceb185d1bfbd505af63855
tests/unit/.../...controlled_synthetic_folder_end_to_end_execution_gate_v1.py  aa587b4f733b1ab23abde7f39ce0d4bf9c31e8445d48458240a3fc20d450a93d
```

Estado Git final de esta fase (sin staging, sin commit):

```text
git status --porcelain=v1:
?? tests/unit/test_cid_local_media_agent_read_only_folder_scanner_commercial_alias_installed_command_controlled_synthetic_folder_end_to_end_execution_gate_v1.py
?? docs/product/local_media_agent/CID_LOCAL_MEDIA_AGENT_COMMERCIAL_ALIAS_INSTALLED_COMMAND_CONTROLLED_SYNTHETIC_FOLDER_END_TO_END_EXECUTION_QA_GATE_V1_20260806.md

UNTRACKED_FILE_COUNT=2 (test E2E + este documento)
MODIFIED_FILES=0
INDEX_CHANGES=0
DIFF_CHECK_CLEAN=True
HEAD=51a78e4015c6f87438448e1c5cc541af3feb7f98 (inalterado)
```

## 12. Incidencias fuera de alcance (preexistentes, no modificadas)

- La suite completa de `tests/unit` no colecta por `ModuleNotFoundError: No module named 'sqlalchemy'`
  en esta `.venv` (106 collection errors). Preexistente, ajena a esta línea.
- 75 fallos en tests write-enabled-export por comandos instalados ausentes en esta `.venv`
  (`command_path is None`). Preexistentes, no relacionados.
- `PytestConfigWarning: Unknown config option: asyncio_mode` (preexistente, no bloqueante).

## 13. Evidencia en `/tmp`

```text
/tmp/cid-controlled-synthetic-folder-e2e-readiness-v1-1786000387/   (Readiness Gate V1)
/tmp/cid-controlled-synthetic-folder-e2e-implementation-v1-1786001611/  (Implementation Gate V1)
/tmp/cid-controlled-synthetic-folder-e2e-qa-v1-1786002172/          (QA Gate V1)
```

## 14. Conclusión

La línea completa (Readiness → Implementation → QA) queda revalidada:

- El alias instalado `cid scan` ejecuta el scan completo sobre carpeta sintética zero-byte
  y devuelve el manifest exacto esperado (exit 0, stderr vacío, una línea JSON compacta).
- Sin efectos secundarios ni fugas de rutas/nombres.
- Sin cambios de producción, de tests existentes ni de la `.venv` (hashes idénticos).
- Raíz sintética ausente tras cada ejecución (`SYNTHETIC_ROOT_EXISTS_AFTER_GATE=False`).
- Estado Git final: solo 2 archivos untracked (test + este documento), HEAD inalterado.

QA_GATE_COMPLETED=CID_LOCAL_MEDIA_AGENT_CONTROLLED_SYNTHETIC_FOLDER_E2E_EXECUTION_QA_GATE_V1_COMPLETED
