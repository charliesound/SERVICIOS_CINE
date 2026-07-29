# CID Local Media Agent - Read Only Folder Scanner CLI Implementation Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.CLI.IMPLEMENTATION.GATE.V1`

## Expected closure result

`LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_CLI_IMPLEMENTATION_GATE_V1_CLOSED`

## Base state

Branch:

`main`

HEAD:

`bc303c43bd10ce153b49514990ee2e6e0579ab62`

Previous stable tag:

`cid-dev-stable-local-media-agent-read-only-folder-scanner-cli-readiness-gate-v1-20260729`

Stable runtime:

`scripts/local_media_agent/read_only_folder_scanner.py`

Runtime SHA256:

`16a4fc52f3fa57b6469bb36ed30400ec26468a9435aad244582a0892fa810a05`

Readiness contract:

`CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.CLI.READINESS.GATE.V1`

## Scope

This phase implements only the isolated Python CLI wrapper for the stable read-only folder scanner runtime.

This phase is limited to exactly three files:

- `docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_cli_implementation_gate_v1.md`
- `scripts/local_media_agent/read_only_folder_scanner_cli.py`
- `tests/unit/test_cid_local_media_agent_read_only_folder_scanner_cli_implementation_gate_v1.py`

This phase does not modify `scripts/local_media_agent/read_only_folder_scanner.py`.

This phase does not modify the CLI readiness gate.

This phase does not modify `pyproject.toml`.

This phase does not create entrypoints, packaging, or the commercial alias `cid scan`.

This phase does not execute on real media material.

This phase does not create output paths, write manifests, write artifacts, read file contents, use ffprobe, use ffmpeg, use subprocess, use shell execution, use network, use DB, use SaaS, or read environment variables.

This phase does not touch backend, frontend, Docker, Alembic, Stripe, auth, AI Jobs, or ledger.

## Implemented module and invocation

Implemented module:

`scripts/local_media_agent/read_only_folder_scanner_cli.py`

Implemented invocation:

```bash
python -m scripts.local_media_agent.read_only_folder_scanner_cli --input-root /absolute/local/linux/folder
```

The commercial alias `cid scan` remains absent and deferred to a future packaging and entrypoints phase.

## Implemented API

The module exposes:

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

Direct execution is protected by:

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

Importing the module does not execute the CLI.

## Parser implementation

The parser is manual, minimal, and sanitized.

It does not use argparse.

Valid scan syntax is exactly:

`--input-root VALUE`

Valid help syntax is exactly:

`--help`

The parser rejects missing input root, duplicated input root, unknown arguments, positional arguments, `-h`, `--input-root=/private/path`, combined help, extra tokens, and non-string input values passed through the Python API.

Parser errors return `CLI_ARGUMENTS_REJECTED` without echoing the rejected argument or path.

## Delegation

The CLI delegates valid scan requests exactly once to:

`scan_read_only_folder(input_root)`

The input value is passed through without `Path`, `resolve`, `absolute`, `expanduser`, `exists`, `is_dir`, `lstat`, `iterdir`, `os.path`, glob expansion, duplicated sanitization, or duplicated path validation.

The CLI does not import pathlib.

## Stdout and stderr

For recognized runtime statuses, the CLI serializes with `manifest_to_json(manifest)` and writes exactly:

`payload + "\n"`

stdout contains exactly one JSON object and one final newline.

stderr is empty for normal runtime results.

Argument errors write exactly `CLI_ARGUMENTS_REJECTED\n` to stderr and keep stdout empty.

Unexpected wrapper failures write exactly `CLI_INTERNAL_FAILURE\n` to stderr and keep stdout empty.

No traceback, exception type, exception text, path, argument, partial manifest, log, or extra text is emitted.

## Exit code mapping

- `READ_ONLY_FOLDER_SCAN_COMPLETED` -> `0`
- `READ_ONLY_FOLDER_SCAN_COMPLETED_WITH_WARNINGS` -> `0`
- `READ_ONLY_FOLDER_SCAN_REJECTED` -> `2`
- `READ_ONLY_FOLDER_SCAN_TRUNCATED` -> `3`
- argument rejection -> `2`
- wrapper internal failure -> `1`

Unknown, absent, or non-string status is treated as `CLI_INTERNAL_FAILURE` with exit code `1`.

## Privacy and isolation

The CLI preserves local Linux only, read-only, stdlib-only, no byte reads, no hashes, no MIME detection, no magic-byte inspection, no ffprobe, no ffmpeg, no subprocess, no shell execution, no network, no DB, no SaaS, no file writes, no private paths in stdout or stderr, no duplicated validation, and fail-closed runtime limits inherited from the runtime.

## Validation

This gate validates:

- parser behavior;
- help behavior;
- delegation behavior;
- status and exit code mapping;
- JSON serialization;
- internal failure handling;
- static absence of forbidden imports and filesystem inspection;
- controlled `tmp_path` regression only.

## Next allowed phase

`CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.CLI.QA.GATE.V1`

## Acceptance criteria

This implementation gate can close only if:

- the phase identity is exact;
- the expected closure result is exact;
- the base HEAD, previous tag, and runtime SHA are documented;
- exactly the three authorized files are changed;
- no runtime, readiness, pyproject, packaging, or entrypoint file is modified;
- the public API and execution guard are implemented;
- parser, stdout, stderr, exit codes, privacy, and delegation match the readiness contract;
- `cid scan` remains absent;
- next phase is exactly `CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.CLI.QA.GATE.V1`.
