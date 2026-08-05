# CID Local Media Agent — Commercial Alias Installed Command QA Gate V1

## 1. Identificación de la fase

```text
CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.COMMERCIAL_ALIAS.INSTALLED_COMMAND.QA.GATE.V1
```

Este documento cubre también la reapertura formal de la QA bloqueada:

```text
CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.COMMERCIAL_ALIAS.INSTALLED_COMMAND.QA.REOPENED.REVALIDATION.GATE.V1
```

## 2. Fecha

```text
2026-08-05
```

## 3. Baseline Git completo

```text
HEAD      = a9aa5b7bdc4b177e3d2f46039d05667b39992e24
origin/main = a9aa5b7bdc4b177e3d2f46039d05667b39992e24
Tree      = 6b1c49b049776dc29a82ebd2e6d7c51953fc45e6
Parent    = b8f4d11d574ff2edc12ba7ccd995c8d27cc61af4
WORKTREE_CLEAN=True
INDEX_CLEAN=True
LOCAL_MAIN_AHEAD_COUNT=0
LOCAL_MAIN_BEHIND_COUNT=0
LOCAL_MAIN_SYNCHRONIZED=True
```

### 3a. Estado del worktree durante la revalidación

La revalidación partió deliberadamente de un worktree no limpio con exactamente siete archivos tracked modificados (los seis tests reconciliados más el contrato vigente tras el rebase) y tres grupos no rastreados autorizados:

```text
TRACKED_MODIFIED_FILE_COUNT = 7
INDEX_CLEAN                 = True
DIFF_CHECK_CLEAN            = True
```

Tests tracked modificados:

```text
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_cli_implementation_gate_v1.py
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_cli_readiness_gate_v1.py
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_commercial_alias_implementation_gate_v1.py
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_commercial_alias_readiness_gate_v1.py
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_implementation_gate_v1.py
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_package_entrypoint_controlled_implementation_v1.py
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_qa_gate_v1.py
```

Grupos no rastreados permitidos:

```text
docs/product/local_media_agent/CID_LOCAL_MEDIA_AGENT_COMMERCIAL_ALIAS_INSTALLED_COMMAND_QA_GATE_V1_20260805.md
tests/fixtures/local_media_agent/historical_contracts/
tests/unit/_cid_historical_contract_snapshot.py
```

Fixtures históricos bajo `tests/fixtures/local_media_agent/historical_contracts/`:

```text
HISTORICAL_FIXTURE_DIRECTORY_COUNT = 6
HISTORICAL_FIXTURE_FILE_COUNT      = 11
```

Commits fuente de los fixtures:

```text
b8f4d11d574ff2edc12ba7ccd995c8d27cc61af4
1113c81c7bd7ca60cfe06f1794000bd7c23939d7
bc303c43bd10ce153b49514990ee2e6e0579ab62
d53da68a49c853a343b2f5ba41aa7408944bd4e7
46602631609558ba81eb7f00a1c0c15a435e17b2
fb8b82eb375370d7aca271846ac181cf9736ba9b
```

## 4. Entorno Python y pip

```text
Canonical Python = /opt/SERVICIOS_CINE/.venv/bin/python
PYTHON_VERSION   = 3.12.3
PIP_VERSION      = 26.2
VENV_CONFIRMED   = True
  sys.executable = /opt/SERVICIOS_CINE/.venv/bin/python
  sys.prefix     = /opt/SERVICIOS_CINE/.venv
  sys.base_prefix= /usr
pip check (PIP_NO_INDEX=1) = exit 0, "No broken requirements found."
```

## 5. Estado de la distribución editable

```text
DISTRIBUTION_NAME      = cid-local-media-agent
DISTRIBUTION_VERSION   = 0.1.0
EDITABLE_SOURCE        = file:///opt/SERVICIOS_CINE
DISTRIBUTION_METADATA_PATH = /opt/SERVICIOS_CINE/.venv/lib/python3.12/site-packages/cid_local_media_agent-0.1.0.dist-info
CONSOLE_SCRIPT_COUNT   = 4
CID_ENTRYPOINT_PRESENT = True
CID_ENTRYPOINT_VALUE   = scripts.local_media_agent.cid_cli:main
EXISTING_ENTRYPOINTS_PRESERVED = True
```

## 6. Tabla de los cuatro console scripts

| # | Console script | Entrypoint (valor registrado) |
|---|----------------|-------------------------------|
| 1 | `cid` | `scripts.local_media_agent.cid_cli:main` |
| 2 | `cid-local-media-agent-controlled-local-demo-runner` | `scripts.local_media_agent.cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner:main` |
| 3 | `cid-local-media-agent-read-only-folder-scanner` | `scripts.local_media_agent.read_only_folder_scanner_cli:main` |
| 4 | `cid-local-media-agent-visible-report-write-enabled-export` | `scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli:main` |

Los tres entrypoints anteriores mantienen exactamente los valores registrados antes de la implementación del alias.

## 7. Ruta, shebang, propietario, entrypoint y SHA-256 de cada script

Todos los scripts están en `/opt/SERVICIOS_CINE/.venv/bin/`, son archivos regulares, ejecutables, propietario `harliesound` (uid 1000) y shebang `#!/opt/SERVICIOS_CINE/.venv/bin/python`.

| Script | Path | Entrypoint importado | SHA-256 |
|--------|------|----------------------|---------|
| `cid` | `/opt/SERVICIOS_CINE/.venv/bin/cid` | `scripts.local_media_agent.cid_cli:main` | `ed0909b210356d4861fdf2781f8305ddbe83ce056bceb185d1bfbd505af63855` |
| `cid-local-media-agent-controlled-local-demo-runner` | `/opt/SERVICIOS_CINE/.venv/bin/cid-local-media-agent-controlled-local-demo-runner` | `scripts.local_media_agent.cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner:main` | `e00560e48ec8f392df0ee70009f7ba027d5d2dcef26a5e725d8df4b63fd71170` |
| `cid-local-media-agent-read-only-folder-scanner` | `/opt/SERVICIOS_CINE/.venv/bin/cid-local-media-agent-read-only-folder-scanner` | `scripts.local_media_agent.read_only_folder_scanner_cli:main` | `4a2581540b325b84202f7ea3e86af6fc4b1c44d5fb8ac546616adc54897af2dc` |
| `cid-local-media-agent-visible-report-write-enabled-export` | `/opt/SERVICIOS_CINE/.venv/bin/cid-local-media-agent-visible-report-write-enabled-export` | `scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli:main` | `e54cfeb9364e422eafd9a0ae569675e6e2912e267bdf1d4121a15df4f75abf47` |

El script `cid` generado termina con el patrón `sys.exit(main())` y no fue modificado durante la QA.

## 8. Resolución en shell limpia

Shell efímera `env -i` con PATH estándar y `source /opt/SERVICIOS_CINE/.venv/bin/activate`:

```text
VIRTUAL_ENV = /opt/SERVICIOS_CINE/.venv
PATH       = /opt/SERVICIOS_CINE/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
command -v cid = /opt/SERVICIOS_CINE/.venv/bin/cid
type -a cid    = cid is /opt/SERVICIOS_CINE/.venv/bin/cid
```

No existe ningún otro comando `cid` resuelto. No se instaló ni enlazó nada globalmente.

## 9. Resultado de `cid --help`

```text
CID_HELP_EXIT_CODE        = 0
CID_HELP_STDERR_EMPTY     = True
CID_HELP_STDOUT_EXACT_MATCH = True (igual a UMBRELLA_HELP_TEXT de scripts/local_media_agent/cid_cli.py)
```

```text
Usage: cid COMMAND [OPTIONS]
Commands:
  scan    Scan one absolute local Linux folder in read-only mode.
Options:
  --help
```

## 10. Resultado de `cid scan --help`

```text
CID_SCAN_HELP_EXIT_CODE        = 0
CID_SCAN_HELP_STDERR_EMPTY     = True
CID_SCAN_HELP_STDOUT_EXACT_MATCH = True (igual a SCAN_HELP_TEXT de scripts/local_media_agent/cid_cli.py)
```

```text
Usage: cid scan --input-root ABSOLUTE_LOCAL_LINUX_FOLDER
Options:
  --input-root ABSOLUTE_LOCAL_LINUX_FOLDER
  --help
```

Ambas ayudas retornan antes de delegar al scanner (sin filesystem, sin ffprobe, sin ffmpeg).

Validación desde shell activada (`source /opt/SERVICIOS_CINE/.venv/bin/activate`):

```text
ACTIVATED_CID_PATH                  = /opt/SERVICIOS_CINE/.venv/bin/cid
ACTIVATED_CID_HELP_EXIT_CODE        = 0
ACTIVATED_CID_SCAN_HELP_EXIT_CODE   = 0
ACTIVATED_OUTPUTS_MATCH_ABSOLUTE_PATH_OUTPUTS = True
```

Regresión de ayuda de los cuatro console scripts (solo `--help`, ramas verificadas como seguras antes de ejecutar):

```text
cid                                     --help -> exit 0, stderr vacío, stdout no vacío
cid-local-media-agent-controlled-local-demo-runner --help -> exit 0, stderr vacío, stdout 598 bytes
cid-local-media-agent-read-only-folder-scanner --help -> exit 0, stderr vacío, stdout 174 bytes
cid-local-media-agent-visible-report-write-enabled-export --help -> exit 0, stderr vacío, stdout 967 bytes
```

Ninguna ejecución de `--help` procesó medios, usó `--input-root` ni delegó a `ffprobe`/`ffmpeg`/scanner real.

## 11. Resultado de las tres pruebas negativas

| Invocación | Exit | stdout vacío | stderr |
|------------|------|--------------|--------|
| `/opt/SERVICIOS_CINE/.venv/bin/cid` | 2 | True | `CID_CLI_ARGUMENTS_REJECTED` |
| `/opt/SERVICIOS_CINE/.venv/bin/cid --bogus` | 2 | True | `CID_CLI_ARGUMENTS_REJECTED` |
| `/opt/SERVICIOS_CINE/.venv/bin/cid foo --help` | 2 | True | `CID_CLI_ARGUMENTS_REJECTED` |

En las tres, el rechazo ocurre en `cid_cli.py` antes de delegar al scanner (`SCANNER_DELEGATION_OCCURRED=False`).

## 12. Archivos de test ejecutados

Lista cerrada (dominio read-only folder scanner; sin SaaS/PostgreSQL/Docker/frontend/Stripe/auth/AI Jobs/ledger):

```text
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_commercial_alias_implementation_gate_v1.py
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_commercial_alias_readiness_gate_v1.py
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_cli_implementation_gate_v1.py
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_cli_readiness_gate_v1.py
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_implementation_gate_v1.py
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_package_entrypoint_controlled_implementation_v1.py
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_qa_gate_v1.py
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_readiness_gate_v1.py
```

## 13. Primera ejecución (bloqueada)

La primera ejecución de la lista cerrada terminó bloqueada. No era un estado final válido:

```text
INITIAL_QA_TESTS_COLLECTED = 178
INITIAL_QA_TESTS_PASSED    = 167
INITIAL_QA_TESTS_SKIPPED   = 0
INITIAL_QA_TESTS_FAILED    = 11
INITIAL_QA_TESTS_ERRORS    = 0
INITIAL_QA_TEST_EXIT_CODE  = 1
INITIAL_QA_RESULT          = BLOCKED_BY_LEGACY_FROZEN_TESTS
```

## 14. Causa de los 11 fallos

Los 11 fallos corresponden a tests de fases previas congelados que verifican el estado **anterior** a la implementación del alias comercial y del entrypoint del scanner en `pyproject.toml`. Inspeccionaban el HEAD actual con expectativas históricas y afirmaban la ausencia de lo que el commit baseline añadió deliberadamente:

- `commercial_alias_readiness_gate_v1.py`: `cid` no debe estar en scripts, `cid_cli.py` no debe existir, exactamente 3 entradas, hash congelado del `pyproject.toml` previo (5 fallos).
- `read_only_folder_scanner_cli_implementation_gate_v1.py`: hash runtime y ausencia de `read_only_folder_scanner_cli` en pyproject (1 fallo).
- `read_only_folder_scanner_cli_readiness_gate_v1.py`: el futuro CLI no debe existir (1 fallo).
- `read_only_folder_scanner_implementation_gate_v1.py`: `read_only_folder_scanner` no debe estar en pyproject (1 fallo).
- `read_only_folder_scanner_package_entrypoint_controlled_implementation_v1.py`: exactamente 3 entradas / mapeo exacto previo (2 fallos).
- `read_only_folder_scanner_qa_gate_v1.py`: `read_only_folder_scanner` no debe estar en pyproject (1 fallo).

Estos fallos no eran regresiones del alias instalado. Eran expectativas históricas congeladas apuntando al HEAD actual.

## 15. Reconciliación de los 11 tests históricos

Los 11 tests históricos fueron reconciliados sin invertir sus expectativas y sin tocarlos durante la QA original:

- Retargeteados a snapshots históricos byte-exact extraídos de los commits fuente (ver sección 3a).
- Cada snapshot es byte-exact contra el objeto Git correspondiente (verificado con `cmp`).
- El runtime de los tests no depende del historial Git: lee los fixtures del árbol de trabajo.
- No se invirtió ninguna expectativa histórica.
- No se añadió `skip` ni `xfail`.
- No se modificó código de producción, `pyproject.toml` ni la `.venv`.

Helper de snapshot:

```text
tests/unit/_cid_historical_contract_snapshot.py
```

Node IDs históricos reconciliados (11):

```text
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_commercial_alias_readiness_gate_v1.py::test_current_pyproject_scripts_has_no_cid_entry
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_commercial_alias_readiness_gate_v1.py::test_cid_cli_module_is_absent_on_disk
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_commercial_alias_readiness_gate_v1.py::test_current_pyproject_scripts_has_exactly_three_entries
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_commercial_alias_readiness_gate_v1.py::test_current_pyproject_scripts_mappings_are_exact
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_commercial_alias_readiness_gate_v1.py::test_frozen_pyproject_hash_is_exact
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_cli_implementation_gate_v1.py::test_runtime_sha_pyproject_and_no_entrypoint_alias
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_cli_readiness_gate_v1.py::test_files_exist_and_future_cli_does_not_exist
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_implementation_gate_v1.py::test_pyproject_is_not_modified_with_read_only_folder_scanner_entrypoint
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_package_entrypoint_controlled_implementation_v1.py::test_project_scripts_section_contains_exactly_three_entries
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_package_entrypoint_controlled_implementation_v1.py::test_project_scripts_entries_match_expected_exact_mapping
tests/unit/test_cid_local_media_agent_read_only_folder_scanner_qa_gate_v1.py::test_pyproject_has_no_cli_packaging_for_scanner
```

## 16. Rebase del hash protegido

El contrato vigente del alias congelaba el SHA-256 del archivo de readiness reconciliado. Tras la reconciliación, el hash legítimo cambió y se rebaseó una única constante:

```text
Archivo: tests/unit/test_cid_local_media_agent_read_only_folder_scanner_commercial_alias_implementation_gate_v1.py
Constante: EXPECTED_READINESS_TEST_SHA256
```

```text
Valor anterior:
aeca61cafb75102e2ba3e7bf3207b85f111604dfd432edd419e2c711b7795220
```
```text
Valor nuevo:
3aa6a5c3bfcc8512f422020c48e46db2effb7b0ec847a51b0e2f69ea10c20447
```

El rebase afectó exactamente una línea (una sola constante), sin cambios de formato, imports, node IDs ni otras aserciones. El diff del archivo protegido fue:

```text
-    "aeca61cafb75102e2ba3e7bf3207b85f111604dfd432edd419e2c711b7795220"
+    "3aa6a5c3bfcc8512f422020c48e46db2effb7b0ec847a51b0e2f69ea10c20447"
```

Hashes del contrato vigente:

```text
EXPECTED_READINESS_TEST_SHA256 (post-rebase) = 3aa6a5c3bfcc8512f422020c48e46db2effb7b0ec847a51b0e2f69ea10c20447
```

## 17. Revalidación final

### 17a. Tests históricos dirigidos (11)

```text
HISTORICAL_TESTS_COLLECTED = 11
HISTORICAL_TESTS_PASSED    = 11
HISTORICAL_TESTS_FAILED    = 0
HISTORICAL_TESTS_ERRORS    = 0
HISTORICAL_TESTS_SKIPPED   = 0
HISTORICAL_TESTS_XFAILED   = 0
HISTORICAL_TESTS_EXIT_CODE = 0
```

### 17b. Lista cerrada QA (8 archivos / 178)

```text
QA_TEST_FILE_COUNT = 8
QA_TESTS_COLLECTED = 178
QA_TESTS_PASSED    = 178
QA_TESTS_FAILED    = 0
QA_TESTS_ERRORS    = 0
QA_TESTS_SKIPPED   = 0
QA_TESTS_XFAILED   = 0
QA_TEST_EXIT_CODE  = 0
```

### 17c. Contrato vigente del alias (27)

```text
CURRENT_ALIAS_TESTS_COLLECTED = 27
CURRENT_ALIAS_TESTS_PASSED    = 27
CURRENT_ALIAS_TESTS_FAILED    = 0
CURRENT_ALIAS_TESTS_ERRORS    = 0
CURRENT_ALIAS_TESTS_SKIPPED   = 0
CURRENT_ALIAS_TESTS_XFAILED   = 0
CURRENT_ALIAS_TESTS_EXIT_CODE = 0
```

### 17d. Alias instalado

```text
CID_HELP_EXIT_CODE         = 0
CID_HELP_STDERR_EMPTY      = True
CID_HELP_STDOUT_EXACT_MATCH = True
CID_SCAN_HELP_EXIT_CODE    = 0
CID_SCAN_HELP_STDERR_EMPTY = True
CID_SCAN_HELP_STDOUT_EXACT_MATCH = True
```

## 18. Warning preexistente de pytest (asyncio_mode)

```text
ASYNCIO_MODE_WARNING_PRESENT = True
ASYNCIO_MODE_WARNING_BLOCKING = False
```

`pytest` emitirá `PytestConfigWarning: Unknown config option: asyncio_mode` en cada ejecución. Es un warning preexistente de configuración:

- no afecta a los resultados;
- no es una regresión de esta fase;
- no se corrigió en esta fase;
- queda fuera del alcance.

No se modificó la configuración de pytest para ocultarlo.

## 19. Comparación de hashes pre-QA / post-QA

Hashes de scripts y metadatos capturados antes y después de la QA y de la revalidación. Idénticos:

```text
entry_points.txt 0e2ba644e2aa2a0df1829e2e4dee4c0c22bff34e57d22e7b9de8b7507812ba88
METADATA         d4b102e58a252840454d59a5489d83392b242343b21b0ecc5209e0dcfa8bc414
direct_url.json   d9f85beb4b25469cab8f696cc2feff8a165ffc169fd7d5b0d4726b5b72a239cf
__editable__.cid_local_media_agent-0.1.0.pth ebfce7134865d7ac9f438eda5b8f12afdd7ba01c979d7c926499bc3c6a4b3403
__editable___cid_local_media_agent_0_1_0_finder.py ff7a1957f3dd57d6f64659f2ee651844245c64776782d66e61fdae86b4bc8e26

cid  ed0909b210356d4861fdf2781f8305ddbe83ce056bceb185d1bfbd505af63855
cid-local-media-agent-controlled-local-demo-runner e00560e48ec8f392df0ee70009f7ba027d5d2dcef26a5e725d8df4b63fd71170
cid-local-media-agent-read-only-folder-scanner 4a2581540b325b84202f7ea3e86af6fc4b1c44d5fb8ac546616adc54897af2dc
cid-local-media-agent-visible-report-write-enabled-export e54cfeb9364e422eafd9a0ae569675e6e2912e267bdf1d4121a15df4f75abf47
```

```text
QA_DID_NOT_MODIFY_VENV = True
```

Inmutabilidad revalidada tras ejecutar todos los tests:

```text
TEST_FILES_MODIFIED_DURING_QA               = False
HISTORICAL_HELPER_MODIFIED_DURING_QA        = False
HISTORICAL_FIXTURES_MODIFIED_DURING_QA      = False
PYPROJECT_MODIFIED_DURING_QA                = False
PRODUCTION_CODE_MODIFIED_DURING_QA          = False
VENV_MODIFIED_DURING_QA                     = False
CONSOLE_SCRIPT_METADATA_MODIFIED_DURING_QA  = False
```

## 20. Ausencia de escaneo de medios

Ninguna ejecución de esta QA usó rutas reales, temporales o sintéticas como `--input-root`. Solo se ejecutaron opciones de ayuda (`--help`) y pruebas negativas que retornan antes de delegar. `MEDIA_SCAN_EXECUTED=False`.

## 21. Ausencia de ffprobe y ffmpeg

Ningún comando de esta QA invocó `ffprobe` ni `ffmpeg`, ni procesos audiovisuales, ni subprocess sobre medios. Los módulos que referencian ffprobe/ffmpeg en su código fueron inspeccionados y sus ramas de `--help` retornan antes de cualquier uso. `FFPROBE_EXECUTED=False`, `FFMPEG_EXECUTED=False`.

## 22. Ausencia de red

No se ejecutó ninguna operación de instalación, descarga ni acceso a índices Python. `pip check` se ejecutó con `PIP_NO_INDEX=1`. `NETWORK_ACCESSED=False`.

## 23. La `.venv` no fue modificada

La instalación editable no se repitió ni regeneró. Los hashes pre/post de los cuatro scripts, `entry_points.txt`, `METADATA`, `direct_url.json`, `.pth` y finder editable son idénticos (sección 19). `PIP_INSTALL_EXECUTED=False`, `PIP_UNINSTALL_EXECUTED=False`, `VENV_MODIFIED=False`.

## 24. Riesgos residuales

1. La reconciliación de los 11 tests históricos usa fixtures byte-exact bajo `tests/fixtures/local_media_agent/historical_contracts/`. Cualquier futura regeneración debe mantener la correspondencia byte-exact con los objetos Git fuente (sección 3a) y conservar las expectativas históricas sin inversión.
2. El rebase de `EXPECTED_READINESS_TEST_SHA256` (sección 16) quedó verificado con 178/178 y 27/27. Un cambio no autorizado en el archivo de readiness reconciliado volvería a romper el contrato vigente.
3. La resolución de `cid` solo es válida dentro de la `.venv` canónica; no existe ni se ha creado un comando global. Cualquier uso fuera de WSL/venv no está soportado.
4. Los cuatro console scripts de `cid-local-media-agent` dependen de la instalación editable anclada a `/opt/SERVICIOS_CINE`; no deben regenerarse sin seguir las fases de packaging controladas.
5. El warning preexistente de `asyncio_mode` (sección 18) sigue presente y queda fuera de alcance.

## 25. Resultado formal

La primera ejecución estuvo bloqueada; la causa fue reconciliada; la revalidación posterior pasó por completo; el resultado final vigente es satisfactorio.

```text
CID_LOCAL_MEDIA_AGENT_COMMERCIAL_ALIAS_INSTALLED_COMMAND_QA_GATE_V1_COMPLETED
```

```text
CID_LOCAL_MEDIA_AGENT_COMMERCIAL_ALIAS_INSTALLED_COMMAND_QA_REOPENED_REVALIDATION_GATE_V1_COMPLETED
```

```text
Baseline idéntico; comando cid persistente y correcto; cuatro console scripts registrados con los tres previos preservados; cid --help y cid scan --help exit 0 con texto exacto; negativas rechazadas antes de delegar; 11 tests históricos reconciliados a snapshots byte-exact y 11/11; lista cerrada 178/178; contrato vigente del alias 27/27; rebase de una única constante (EXPECTED_READINESS_TEST_SHA256); hashes de instalación idénticos pre/post QA; sin escaneo de medios; sin ffprobe/ffmpeg; sin red; .venv sin modificar; warning asyncio_mode preexistente no bloqueante; única evidencia documental actualizada (este archivo); sin staging, commit, tag ni push.
```
