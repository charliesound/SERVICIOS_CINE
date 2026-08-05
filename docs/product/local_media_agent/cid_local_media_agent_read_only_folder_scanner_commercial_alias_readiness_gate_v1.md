# CID Local Media Agent - Read-Only Folder Scanner Commercial Alias Readiness Gate V1

## Phase

`CID_LAPTOP_LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_COMMERCIAL_ALIAS_READINESS_GATE_V1`

## Expected closure result

`CID_LAPTOP_LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_COMMERCIAL_ALIAS_READINESS_GATE_V1_CLOSED`

## Objective

Create exclusively the documentary readiness gate and its static QA to define the future contract of the commercial umbrella command:

```bash
cid scan --input-root ABSOLUTE_LOCAL_LINUX_FOLDER
```

This phase does NOT implement the `cid` command.

This phase does NOT modify packaging.

This phase does NOT execute the scanner.

## Base state

- Repository: `/opt/SERVICIOS_CINE`
- Branch: `main`
- HEAD: `46602631609558ba81eb7f00a1c0c15a435e17b2`
- Tree: `4e9489d60be18226754133b22dfe2ec9d3730d35`
- Parent: `1113c81c7bd7ca60cfe06f1794000bd7c23939d7`
- `origin/main`: `46602631609558ba81eb7f00a1c0c15a435e17b2`
- Stable base tag: `cid-dev-stable-local-media-agent-read-only-folder-scanner-package-entrypoint-v1-20260805`

The repository must be clean before starting.

## Scope

This phase is readiness-only, documentation-only and static-QA-only.

This phase creates exactly two new files:

- `docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_commercial_alias_readiness_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_read_only_folder_scanner_commercial_alias_readiness_gate_v1.py`

This phase does not modify any existing file.

This phase does not create any other file.

## Current packaging state

`pyproject.toml` currently contains exactly three installed scripts:

| Script | Mapping |
| --- | --- |
| `cid-local-media-agent-visible-report-write-enabled-export` | `scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli:main` |
| `cid-local-media-agent-controlled-local-demo-runner` | `scripts.local_media_agent.cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner:main` |
| `cid-local-media-agent-read-only-folder-scanner` | `scripts.local_media_agent.read_only_folder_scanner_cli:main` |

## Current absence of cid

Currently there is no:

- `[project.scripts]` entry named `cid`;
- `scripts/local_media_agent/cid_cli.py`;
- installed command `cid`;
- commercial subcommand `cid scan`.

The commercial alias was explicitly deferred in the prior readiness and CLI implementation phases of the read-only folder scanner.

## Frozen files

The following files are frozen and must not be modified:

| File | SHA256 |
| --- | --- |
| `pyproject.toml` | `5fbbe0668ce9ad6e64fa28325dd0208a9e2c739c1cd1dc43000716c9c5e301b4` |
| `scripts/local_media_agent/read_only_folder_scanner.py` | `16a4fc52f3fa57b6469bb36ed30400ec26468a9435aad244582a0892fa810a05` |
| `scripts/local_media_agent/read_only_folder_scanner_cli.py` | `ec9f4714597cd96d2f79640bff51110844bcb4c9106a07e58359e286a99cff6d` |

## Future cid contract

The future entrypoint must be exactly:

```toml
cid = "scripts.local_media_agent.cid_cli:main"
```

The future module must be exactly:

```text
scripts/local_media_agent/cid_cli.py
```

The canonical commercial invocation must be:

```bash
cid scan --input-root ABSOLUTE_LOCAL_LINUX_FOLDER
```

The future Python interface must expose:

```python
def run_cli(
    argv: Sequence[str] | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    ...

def main() -> int:
    ...
```

The future module must have exactly this protection:

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

## Umbrella command contract

Only one subcommand is authorized initially:

- `scan`

These are NOT authorized yet:

- `export`;
- `demo`;
- `transcribe`;
- `sync`;
- `report`;
- `inspect`;
- `metadata`;
- `install`;
- `login`;
- `activate`;
- `license`;
- SaaS;
- cloud;
- multiple folders;
- configuration;
- plugins;
- dynamic commands.

## Umbrella help contract

The invocation `cid --help` must:

- return exit code 0;
- not execute the scanner;
- write exclusively a fixed commercial help;
- not contain private paths;
- not write files.

The future umbrella help must be exactly:

```text
Usage: cid COMMAND [OPTIONS]
Commands:
  scan    Scan one absolute local Linux folder in read-only mode.
Options:
  --help
```

## Scan help contract

The invocation `cid scan --help` must:

- return exit code 0;
- not execute the scanner;
- write exclusively a fixed subcommand help;
- use the commercial syntax `cid scan`;
- not show the internal `python -m` invocation;
- not contain private paths;
- not write files.

The future scan help must be exactly:

```text
Usage: cid scan --input-root ABSOLUTE_LOCAL_LINUX_FOLDER
Options:
  --input-root ABSOLUTE_LOCAL_LINUX_FOLDER
  --help
```

## Delegation contract

For a scan invocation different from help:

```bash
cid scan <arguments>
```

the future umbrella module must delegate to:

```text
scripts.local_media_agent.read_only_folder_scanner_cli.run_cli
```

The future umbrella module must NOT call directly:

```text
scan_read_only_folder
```

The umbrella adapter must remove only the initial `scan` token and pass the remaining arguments without transformation to the existing `run_cli`.

Example:

```bash
cid scan --input-root /absolute/local/folder
```

must delegate exactly as:

```python
read_only_folder_scanner_cli.run_cli(
    ["--input-root", "/absolute/local/folder"],
    stdout=stdout,
    stderr=stderr,
)
```

The umbrella adapter must NOT:

- resolve paths;
- normalize paths;
- convert to `Path`;
- expand `~`;
- expand globs;
- inspect the filesystem;
- check existence;
- duplicate validation;
- read environment variables;
- change the current directory;
- alter stdout;
- alter stderr;
- alter the manifest;
- alter the exit code.

## Preservation of the existing contract

For delegated executions, these must be preserved without changes:

- scanner CLI parser;
- JSON manifest;
- serialization;
- stdout;
- stderr;
- exit codes;
- privacy;
- sanitization;
- fail-closed limits;
- read-only behavior.

Delegated exit codes must be propagated exactly:

- 0 for completed or completed with warnings;
- 2 for rejected arguments or rejected scan;
- 3 for truncated scan;
- 1 for controlled internal failure of the existing CLI.

## Umbrella errors

Invalid umbrella invocations must be rejected before delegation:

- `cid` without arguments;
- `cid -h`;
- `cid unknown`;
- `cid --unknown`;
- any subcommand other than `scan`;
- umbrella help combined with additional tokens.

For those future errors:

- the scanner CLI must not be executed;
- stdout must remain empty;
- stderr must contain exclusively:

```text
CID_CLI_ARGUMENTS_REJECTED
```

followed by a single newline;

- exit code 2;
- no traceback;
- the rejected argument must not be reproduced.

An unexpected failure inside the future umbrella adapter must:

- keep stdout empty;
- write exclusively:

```text
CID_CLI_INTERNAL_FAILURE
```

followed by a single newline;

- return exit code 1;
- show no traceback, exception, argument or path.

## Privacy and security

The future adapter contract must preserve:

- local Linux execution;
- read-only;
- no modification of material;
- no reading of file contents;
- no media hashes;
- no MIME;
- no magic bytes;
- no ffprobe;
- no ffmpeg;
- no subprocess;
- no shell;
- no network;
- no database;
- no SaaS;
- no writes;
- no logs;
- no cache;
- no private paths in messages;
- no private names in errors;
- no symlink following;
- no acceptance of Windows, UNC, `/mnt` or `wsl.localhost` paths;
- no overwriting;
- no parallel processing.

## Prohibited operations

This phase does not authorize creating:

- `scripts/local_media_agent/cid_cli.py`;
- the `cid` entrypoint;
- any runtime module;
- any installer;
- any commercial configuration;
- any license;
- any external integration.

This phase does not authorize modifying:

- `pyproject.toml`;
- `read_only_folder_scanner.py`;
- `read_only_folder_scanner_cli.py`;
- any existing test;
- any existing document.

This phase does not authorize touching:

- `.env`;
- databases;
- PostgreSQL;
- SQLite;
- Docker;
- Alembic;
- backend;
- frontend;
- SaaS;
- Stripe;
- auth;
- AI Jobs;
- ledger;
- installers;
- licenses;
- real media;
- client folders.

This phase does not authorize running:

- the scanner;
- the installed launcher;
- ffprobe;
- ffmpeg;
- external subprocess;
- shell from Python;
- network;
- fetch;
- pull;
- push;
- commit;
- tag;
- staging;
- package install;
- build;
- full pytest.

This phase does not authorize creating:

- `build/`;
- `dist/`;
- `*.egg-info`;
- caches;
- logs;
- media manifests;
- product outputs.

## Acceptance criteria

This readiness gate is accepted only when:

- the phase identity is exact;
- the expected closure result is exact;
- the base state is fully documented;
- the scope is limited to the two authorized new files;
- the current three entrypoints and their exact mappings are documented;
- the current absence of `cid` is documented;
- the future `cid` contract is exact;
- the scan subcommand contract is exact;
- both help contracts are fixed exactly;
- the delegation contract is exact;
- stdout, stderr and exit code propagation is exact;
- umbrella errors are sanitized;
- privacy and security boundaries are explicit;
- prohibited operations are explicit;
- the next allowed phase is exactly `CID_LAPTOP_LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_COMMERCIAL_ALIAS_IMPLEMENTATION_GATE_V1`;
- this phase does not grant implementation permission.

## Next allowed phase

The only next phase allowed by this readiness gate is:

`CID_LAPTOP_LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_COMMERCIAL_ALIAS_IMPLEMENTATION_GATE_V1`

That future implementation gate must remain minimal, isolated, reversible, read-only, stdout-only, and covered by targeted unit tests.

## Explicit statement

This phase is readiness-only, documentation-only and static-QA-only.

This phase does NOT grant implementation permission.

Implementation of `cid`, `scripts/local_media_agent/cid_cli.py`, packaging changes and any runtime change require a separate future authorized phase.
