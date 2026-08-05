# CID Local Media Agent — read-only folder scanner package entrypoint controlled implementation V1

## Phase

`CID_LAPTOP_LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_PACKAGE_ENTRYPOINT_CONTROLLED_IMPLEMENTATION_V1`

## Objective

Expose the existing CID Local Media Agent read-only folder scanner CLI as a third installed package entry point, without modifying either the scanner runtime or its CLI implementation.

## Authorized files

### Authorized existing file to modify

- `pyproject.toml`

### Authorized new files to create

- `tests/unit/test_cid_local_media_agent_read_only_folder_scanner_package_entrypoint_controlled_implementation_v1.py`
- `docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_package_entrypoint_controlled_implementation_v1.md`

### All other files are out of scope

## Exact new entry point

Inside the existing `[project.scripts]` section, the two current entries are preserved exactly and this third entry was added:

```toml
cid-local-media-agent-read-only-folder-scanner = "scripts.local_media_agent.read_only_folder_scanner_cli:main"
```

The two pre-existing entries remain exactly:

```toml
cid-local-media-agent-visible-report-write-enabled-export = "scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli:main"
cid-local-media-agent-controlled-local-demo-runner = "scripts.local_media_agent.cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner:main"
```

## Frozen runtime hashes

The following frozen runtime files must not be modified. Expected SHA256 values:

| File | SHA256 |
| --- | --- |
| `scripts/local_media_agent/read_only_folder_scanner.py` | `16a4fc52f3fa57b6469bb36ed30400ec26468a9435aad244582a0892fa810a05` |
| `scripts/local_media_agent/read_only_folder_scanner_cli.py` | `ec9f4714597cd96d2f79640bff51110844bcb4c9106a07e58359e286a99cff6d` |

## Scope boundaries

- Modify packaging metadata only, limited to adding the exact third `[project.scripts]` entry.
- Add the focused static test file.
- Add this gate document.
- No other files are touched.

## Prohibited operations

- Modifying either frozen scanner source file.
- Modifying existing tests or documents.
- Touching `.env` files.
- Accessing, modifying or restoring any database.
- Using SQLite.
- Running Docker.
- Running Alembic.
- Touching backend, frontend, SaaS, auth, Stripe, AI Jobs or ledger.
- Installing or updating dependencies.
- Creating build, dist or egg-info artifacts.
- Scanning media, creating fixtures, writing project output, using network.
- Committing, tagging, pushing or staging files.

## Static QA command

```bash
/opt/SERVICIOS_CINE/.venv/bin/python -m pytest -q tests/unit/test_cid_local_media_agent_read_only_folder_scanner_package_entrypoint_controlled_implementation_v1.py
```

The full test suite, the scanner, package reinstallation, the new launcher and real media are explicitly out of scope for QA.

## Implementation result

- `pyproject.toml`: modified to add the exact third `[project.scripts]` entry; the two pre-existing entries were preserved exactly.
- New static pytest file created covering: exact three-entry `[project.scripts]` section, exact pre-existing mappings, exact new mapping, and the two frozen runtime SHA256 values.
- Frozen runtime hashes confirmed unchanged after implementation.

## Explicit statement

Installation, installed-launcher smoke, commit, tag and push are NOT part of this OpenCode step.
