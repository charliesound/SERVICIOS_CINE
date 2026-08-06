# CID Local Media Agent - Windows Host Drive Controlled Own Real Material Single Scan Sanitized Execution Record v1

## 1. Titulo

CID Local Media Agent - Windows Host Drive Controlled Own Real Material Single Scan Sanitized Execution Record v1

This record persists a sanitized summary of one authorized read-only metadata-only scan execution over a controlled own real material folder reached through the WSL Windows host drive bridge.

This record stores only sanitized aggregated evidence.

This record does not store real media content.

This record does not store real folder paths.

This record does not store real file names.

This record does not store real subdirectory names.

This record does not store media hashes.

## 2. Identidad de fase

RECORD_PHASE=

CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.COMMERCIAL_ALIAS.WINDOWS_HOST_DRIVE.CONTROLLED_OWN_REAL_MATERIAL.SINGLE_SCAN.SANITIZED_EXECUTION.RECORD.V1

RECORD_RESULT=

CID_LOCAL_MEDIA_AGENT_CONTROLLED_OWN_REAL_MATERIAL_SINGLE_SCAN_SANITIZED_EXECUTION_RECORD_V1_COMPLETED

## 3. Resultado formal

RECORD_DATE=2026-08-06

EXECUTION_GATE_RESULT=

CID_LOCAL_MEDIA_AGENT_WINDOWS_HOST_DRIVE_CONTROLLED_OWN_REAL_MATERIAL_SINGLE_METADATA_ONLY_SCAN_EXECUTION_GATE_V1_COMPLETED

RESULTS_REVIEW_CLOSURE_RESULT=

CID_LOCAL_MEDIA_AGENT_WINDOWS_HOST_DRIVE_CONTROLLED_OWN_REAL_MATERIAL_SINGLE_METADATA_ONLY_SCAN_RESULTS_REVIEW_CLOSURE_GATE_V1_COMPLETED

REAL_MATERIAL_SINGLE_SCAN_RESULTS_REVIEW_APPROVED=True

READINESS_GATE_RESULT=

CID_LOCAL_MEDIA_AGENT_CONTROLLED_OWN_REAL_MATERIAL_SANITIZED_EXECUTION_EVIDENCE_PERSISTENCE_READINESS_GATE_V1_COMPLETED

## 4. Alcance del registro

This record documents the persistence gate evidence of one real material scan.

This record is documentation plus test only.

This record does not modify production runtime.

This record does not modify existing repository files.

This record does not create a JSON artifact.

This record does not store raw output.

This record does not store the full scan JSON.

This record does not store example real paths.

This record does not re-execute the scan.

## 5. Autorizacion consumida

ORIGINAL_SCAN_AUTHORIZATION_CONSUMED=True

ADDITIONAL_SCAN_AUTHORIZED=False

SCAN_REEXECUTION_ALLOWED=False

The original scan authorization was consumed by the single real material execution gate.

No additional scan was authorized.

No scan re-execution is allowed.

This record is persisted under the sanitized execution evidence persistence implementation gate authorization.

## 6. Identidad estable del codigo

STABLE_COMMIT_SHA=

e97cd06f2e2fa84b01e64cac16cae8fe62ab3d74

STABLE_TREE_SHA=

299c402c9ca64864c3cae49ca1b7e97613c3de66

STABLE_PARENT_SHA=

34a0dc2f6da8701ec70785c4dbc7be206b79823b

STABLE_COMMIT_SUBJECT=

feat: add CID Local Media Agent Windows host path portability

STABLE_TAG=

cid-dev-stable-local-media-agent-read-only-folder-scanner-commercial-alias-windows-host-drive-path-portability-v1-20260806

Code hashes persisted:

SCANNER_SHA256=1d0dc95cff6d69cf973780452eea3087cc86af0ff5b07a63595157d77f3722c7

SCANNER_CLI_SHA256=1d8df7aeaf9a94df112f7f55ffcbdf95564188c9bafcf5dc1359aebffa49a2f6

HOST_PATH_ADAPTER_SHA256=255cc5630a9bf2f32b20bdfb91fd498396624d8c064d708af53be5bc1d12fe59

CID_CLI_SHA256=f48ce145afef969a2fc2866ce1b40f50cd699f3ea3d2bfa96d1454337de399b2

INSTALLED_CID_SHA256=ed0909b210356d4861fdf2781f8305ddbe83ce056bceb185d1bfbd505af63855

## 7. Evidencia fuente sanitizada

SOURCE_EXECUTION_EVIDENCE=SANITIZED_TEMP_EXECUTION_EVIDENCE

SOURCE_RESULTS_REVIEW_EVIDENCE=SANITIZED_TEMP_RESULTS_REVIEW_EVIDENCE

RECORD_CONTAINS_REAL_MEDIA_PATH=False

RECORD_CONTAINS_REAL_FILE_NAMES=False

RECORD_CONTAINS_MEDIA_HASHES=False

The source evidence remains outside the repository in sanitized temporary evidence locations.

The repository record intentionally stores only the sanitized aggregated summary.

The repository record must not store the original authorized root value.

The repository record must not store real file or subdirectory names.

## 8. Resumen de ejecucion

SCAN_STATUS=READ_ONLY_FOLDER_SCAN_COMPLETED

SCAN_SCHEMA_VERSION=cid.local_media_agent.read_only_folder_scanner.v1

SCAN_INPUT_LABEL=SANITIZED_LOCAL_FOLDER_INPUT

SCAN_EXECUTION_COUNT=1

SCAN_EXIT_CODE=0

WSL_REAL_FILESYSTEM_BRIDGE_EMPIRICALLY_EXECUTED=True

CONTROLLED_WINDOWS_HOST_PATH_ACCEPTED=True

CONTROLLED_WINDOWS_HOST_PATH_TRANSLATED=True

CONTROLLED_REAL_FOLDER_ENUMERATED=True

CONTROLLED_REAL_FILESYSTEM_METADATA_READ=True

The scan input is represented exclusively as SANITIZED_LOCAL_FOLDER_INPUT.

The test input root is represented only as SANITIZED_CLIENT_SELECTED_LOCAL_ROOT.

The test volume is represented only as SANITIZED_HOST_VOLUME.

## 9. Conteos agregados

FILES_SEEN=249

DIRECTORIES_SEEN=146

MEDIA_CANDIDATES=160

VIDEO_FILES=16

AUDIO_FILES=136

IMAGE_FILES=8

NON_MEDIA_FILES=89

ERROR_COUNT=0

WARNING_COUNT=0

## 10. Validacion aritmetica

FILES_ACCOUNTING_FORMULA=249=160+89

MEDIA_ACCOUNTING_FORMULA=160=16+136+8

TOTAL_CLASSIFICATION_FORMULA=249=16+136+8+89

FILES_ACCOUNTING_VALID=True

MEDIA_ACCOUNTING_VALID=True

TOTAL_CLASSIFICATION_VALID=True

## 11. Limites y profundidad

MAX_FILES=5000

MAX_DEPTH=8

MAX_ERRORS=100

MAX_OBSERVED_DEPTH=7

TRUNCATED=False

MAX_FILES_REACHED=False

MAX_DEPTH_REACHED=False

MAX_ERRORS_REACHED=False

## 12. Errores, warnings y stderr

ERROR_COUNT=0

WARNING_COUNT=0

SCAN_STDERR_BYTES=0

The scan completed without errors.

The scan completed without warnings.

The scan produced no stderr.

No truncation occurred.

No configured limit was reached.

## 13. Privacidad

PRIVACY_FILE_CONTENTS_OPENED=False

PRIVACY_CONTENT_HASHES_COMPUTED=False

PRIVACY_FFPROBE_EXECUTED=False

PRIVACY_FFMPEG_EXECUTED=False

PRIVACY_NETWORK_USED=False

PRIVACY_DATABASE_USED=False

PRIVACY_SUBPROCESS_USED=False

PRIVACY_ORIGINAL_MEDIA_MODIFIED=False

PRIVACY_SAAS_USED=False

PRIVACY_ARTIFACT_WRITTEN=False

READ_ONLY_CONTRACT_PRESERVED=True

METADATA_ONLY_CONTRACT_PRESERVED=True

PRIVACY_CONTRACT_VALID=True

No media content was opened.

No content hashes were computed.

No ffprobe execution occurred.

No ffmpeg execution occurred.

No network access occurred.

No database access occurred.

No subprocess execution occurred.

No original media was modified.

No SaaS was used.

No artifact was written during the scan itself.

## 14. Contrato metadata-only y read-only

The scan executed under a read-only metadata-only contract.

The scanner did not open media file contents.

The scanner did not read media payloads.

The scanner read filesystem metadata only.

The scanner did not modify any original file.

The scanner did not create any artifact inside the authorized root.

The scanner did not enumerate other drives.

The scanner did not access the drive root itself.

The scanner did not scan the parent directory.

The scanner did not scan sibling directories.

The scanner did not receive a direct /mnt input.

## 15. Alcance de raiz

AUTHORIZED_ROOT_ONLY=True

OTHER_DRIVES_ENUMERATED=False

DRIVE_ROOT_ACCESSED=False

PARENT_DIRECTORY_SCANNED=False

SIBLING_DIRECTORY_SCANNED=False

DIRECT_MNT_INPUT_USED=False

The scan scope was limited to the authorized folder only.

The authorized folder is represented only as SANITIZED_CLIENT_SELECTED_LOCAL_ROOT.

## 15.b Politica comercial de ruta (volume agnostic)

CLIENT_SELECTED_LOCAL_ROOT_REQUIRED=True

CLIENT_SELECTED_LOCAL_VOLUME_SUPPORTED=True

CLIENT_SELECTED_ROOT_ONLY=True

AUTOMATIC_DRIVE_ENUMERATION=False

PARENT_DIRECTORY_ENUMERATION=False

SIBLING_DIRECTORY_ENUMERATION=False

OTHER_VOLUME_ENUMERATION=False

WINDOWS_DRIVE_LETTER_HARD_CODED=False

DEFAULT_WINDOWS_DRIVE_REQUIRED=False

SPECIFIC_WINDOWS_DRIVE_REQUIRED=False

WINDOWS_NATIVE_RUNTIME_EXPECTS_DIRECT_HOST_PATH=True

WSL_DEVELOPMENT_BRIDGE_ONLY=True

WSL_REQUIRED_FOR_CUSTOMERS=False

CUSTOMER_MEDIA_COPY_REQUIRED=False

CLIENT_SELECTED_LOCAL_ROOT_ACCEPTED=True

CLIENT_SELECTED_LOCAL_ROOT_ENUMERATED=True

CLIENT_SELECTED_LOCAL_ROOT_METADATA_READ=True

TEST_EXECUTION_HOST_VOLUME_REDACTED=True

TEST_EXECUTION_USED_ONE_REDACTED_LOCAL_VOLUME=True

TEST_EXECUTION_VOLUME_IS_NOT_PRODUCT_DEFAULT=True

TEST_EXECUTION_PATH_IS_NOT_PRODUCT_DEFAULT=True

COMMERCIAL_PRODUCT_SUPPORTS_CLIENT_SELECTED_LOCAL_ROOT=True

COMMERCIAL_PATH_POLICY_IS_VOLUME_AGNOSTIC=True

COMMERCIAL_PATH_POLICY_IS_CROSS_PLATFORM=True

The volume and the folder used in the real execution belong only to one concrete controlled test.

They are not the product default volume.

They are not the only supported volume.

They are not a commercial restriction.

They are not a required client configuration.

They are not a value to be persisted in documentation or tests.

The commercial product must support a concrete local root selected by the client on any authorized local volume compatible with the operating system.

The test input is represented only as SANITIZED_CLIENT_SELECTED_LOCAL_ROOT.

The test volume is represented only as SANITIZED_HOST_VOLUME.

This test demonstrates that one selected Windows host path can be received and translated through the development WSL bridge.

This test does not demonstrate or imply that the product is limited to one volume letter.

This test does not demonstrate or imply that the client must use the same volume used in the test.

This test does not demonstrate or imply that WSL is required in production.

This test does not demonstrate or imply that the client must copy their media.

This test does not demonstrate or imply that CID automatically enumerates all volumes.

## 16. Alcance tecnico demostrado

WSL_REAL_FILESYSTEM_BRIDGE_EMPIRICALLY_EXECUTED=True

CONTROLLED_WINDOWS_HOST_PATH_ACCEPTED=True

CONTROLLED_WINDOWS_HOST_PATH_TRANSLATED=True

CONTROLLED_REAL_FOLDER_ENUMERATED=True

CONTROLLED_REAL_FILESYSTEM_METADATA_READ=True

WINDOWS_NATIVE_RUNTIME_EMPIRICALLY_EXECUTED=False

WINDOWS_NATIVE_INSTALLER_VALIDATED=False

WINDOWS_NATIVE_CI_REQUIRED_LATER=True

UNC_SUPPORT_VALIDATED=False

NETWORK_SHARE_SUPPORT_VALIDATED=False

CUSTOMER_WSL_REQUIREMENT_INFERRED=False

CUSTOMER_MEDIA_COPY_REQUIREMENT_INFERRED=False

This execution empirically validates the WSL bridge against one real folder reached through the Windows host drive.

This execution does not prove native Windows runtime execution.

This execution does not prove Windows installer validation.

This execution does not prove Windows CI readiness.

This execution does not prove UNC or network share support.

The customer WSL requirement is not inferred.

The customer media copy requirement is not inferred.

## 17. Evidencia de tests

PORTABILITY_TESTS_PASSED=64

SCANNER_DOMAIN_TESTS_PASSED=272

HISTORICAL_TESTS_PASSED=179

ALIAS_TESTS_PASSED=27

SYNTHETIC_E2E_TESTS_PASSED=1

COMBINED_TESTS_PASSED=243

TEST_EVIDENCE_REUSED_FROM_CONTROLLED_STAGING=True

TESTED_BLOB_SET_MATCH=True

pytest was not executed during the results review.

pytest was not executed during the readiness phase.

## 18. Limitaciones y non-claims

This record must not be presented as:

- native Windows runtime validation
- Windows installer validation
- Windows CI completion
- UNC support validation
- network share support validation
- customer WSL requirement proof
- customer media copy requirement proof
- production commercial Windows runtime readiness
- client installation readiness
- installer creation readiness
- public demo readiness
- sales demo readiness
- SaaS integration readiness
- database integration readiness

This record does not prove the commercial Windows runtime is equivalent to the WSL bridge execution.

This record does not claim that the final customer requires WSL.

## 19. Inmutabilidad

RECORD_CONTAINS_REAL_MEDIA_PATH=False

RECORD_CONTAINS_REAL_FILE_NAMES=False

RECORD_CONTAINS_MEDIA_HASHES=False

The record does not contain the original authorized root value.

The record does not contain real file names.

The record does not contain real subdirectory names.

The record does not contain media hashes.

The record does not contain the raw scan JSON.

The record does not contain temporary evidence paths.

The record does not contain individual file sizes.

The record does not contain individual file timestamps.

The record does not contain individual file permissions.

The record does not contain individual file inodes.

## 20. Cierre

This sanitized execution record closes with a documentation plus test implementation.

This record is validated by its dedicated unit test.

This record is closed by the sanitized execution evidence persistence QA gate.

This record does not open any new scan.

This record does not open staging.

This record does not open commit.

This record does not open push.

NEXT_AUTHORIZED_PHASE=NONE
