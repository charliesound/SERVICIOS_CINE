# CID Local Media Agent - Read Only Folder Scanner CLI Readiness Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.CLI.READINESS.GATE.V1`

## Expected closure result

`LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_CLI_READINESS_GATE_V1_CLOSED`

## Base state

Branch:

`main`

HEAD:

`685dedcfd8808dd1294d6e1a864c48f3728bdac7`

Previous stable tag:

`cid-dev-stable-local-media-agent-read-only-folder-scanner-qa-closure-review-gate-v1-20260729`

Stable runtime:

`scripts/local_media_agent/read_only_folder_scanner.py`

Runtime SHA256:

`16a4fc52f3fa57b6469bb36ed30400ec26468a9435aad244582a0892fa810a05`

Previous phase:

`CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.QA.CLOSURE.REVIEW.GATE.V1`

## Scope

This phase is readiness-only, documentation-only, and contract-only.

This phase defines the future isolated CLI contract for the closed read-only folder scanner runtime.

This phase does not implement the CLI.

This phase is limited to exactly two new files:

- `docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_cli_readiness_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_read_only_folder_scanner_cli_readiness_gate_v1.py`

This phase does not modify `scripts/local_media_agent/read_only_folder_scanner.py`.

This phase does not create `scripts/local_media_agent/read_only_folder_scanner_cli.py`.

This phase does not modify `pyproject.toml`.

This phase does not create entrypoints, packaging, or the commercial alias `cid scan`.

This phase does not execute on real media material.

This phase does not read file contents, use ffprobe, use ffmpeg, use subprocess, use shell execution, use network, use DB, use SaaS, or write manifests or artifacts to disk.

This phase does not touch backend, frontend, Docker, Alembic, Stripe, auth, AI Jobs, or ledger.

## Future CLI module

The future CLI module, not created in this phase, is:

`scripts/local_media_agent/read_only_folder_scanner_cli.py`

The canonical future invocation is:

```bash
python -m scripts.local_media_agent.read_only_folder_scanner_cli --input-root /absolute/local/linux/folder
```

The commercial alias `cid scan` is expressly deferred to a future packaging and entrypoints phase.

## V1 arguments

Required argument:

- `--input-root ABSOLUTE_LOCAL_LINUX_FOLDER`

Allowed option:

- `--help`

V1 must not add:

- positional arguments;
- multiple folders;
- stdin;
- output path;
- alternate output format;
- pretty print;
- configuration through environment variables;
- configuration files;
- exclusions;
- filters;
- configurable depth;
- configurable limits;
- symlink following;
- network;
- parallel execution.

## Delegation contract

The future CLI must delegate validation and traversal exclusively to:

`scan_read_only_folder(input_root)`

The future CLI must not duplicate runtime path validation.

The future CLI must not resolve, normalize, inspect, traverse, or call `lstat` by itself.

Unsafe paths such as Windows drive paths, UNC paths, `/mnt` paths, and `wsl.localhost` paths remain runtime rejections, not duplicated CLI validation.

## Future API

The future CLI module must expose:

```python
def run_cli(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    ...

def main() -> int:
    ...
```

The future module must be testable through injected `argv`, `stdout`, and `stderr` streams.

The future direct execution guard must be:

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

The future module must not execute during import.

## Stdout contract

When CLI arguments are valid and the runtime is invoked, stdout must contain exclusively the manifest produced by the runtime.

The future CLI must use `manifest_to_json` or `emit_manifest_json`.

The future CLI must write exactly one JSON object.

The future CLI stdout must end with exactly one newline.

The future CLI must not prepend messages, append messages, include logs, include additional paths, modify the manifest, or write artifacts.

## Stderr contract

For normal runtime results, stderr must be empty.

For CLI argument errors, the future CLI must not execute the runtime and must emit only:

`CLI_ARGUMENTS_REJECTED`

The future CLI must not show the full `--input-root` value, private paths, or raw argparse messages that could reproduce private arguments.

For unexpected internal wrapper failures, stdout must be empty and stderr must emit only:

`CLI_INTERNAL_FAILURE`

The future CLI must not show tracebacks, `repr(exception)`, `str(exception)`, paths, or raw exception text.

## Exit code contract

Exit code `0` means one of:

- `READ_ONLY_FOLDER_SCAN_COMPLETED`
- `READ_ONLY_FOLDER_SCAN_COMPLETED_WITH_WARNINGS`
- `--help`

Exit code `2` means one of:

- missing, duplicated, unknown, or invalid CLI arguments;
- `READ_ONLY_FOLDER_SCAN_REJECTED`

Exit code `3` means:

- `READ_ONLY_FOLDER_SCAN_TRUNCATED`

Exit code `1` means:

- controlled unexpected internal failure of the CLI wrapper.

The future CLI must not transform `READ_ONLY_FOLDER_SCAN_REJECTED` or `READ_ONLY_FOLDER_SCAN_TRUNCATED` into success.

## Argument behavior contract

Missing `--input-root`:

- no runtime;
- stdout empty;
- stderr fixed to `CLI_ARGUMENTS_REJECTED`;
- exit `2`.

Repeated `--input-root`:

- no runtime;
- stdout empty;
- stderr fixed to `CLI_ARGUMENTS_REJECTED`;
- exit `2`.

Unknown argument:

- no runtime;
- stdout empty;
- stderr fixed to `CLI_ARGUMENTS_REJECTED`;
- exit `2`.

Positional argument:

- no runtime;
- stdout empty;
- stderr fixed to `CLI_ARGUMENTS_REJECTED`;
- exit `2`.

`--help`:

- no runtime;
- exit `0`;
- help text contains no private paths;
- no files are written.

Input accepted by parser but rejected by runtime:

- emit the runtime rejected manifest to stdout;
- stderr empty;
- exit `2`.

Completed with warnings:

- emit the runtime manifest to stdout;
- stderr empty;
- exit `0`.

Truncated result:

- emit the runtime manifest to stdout;
- stderr empty;
- exit `3`.

Unexpected wrapper exception:

- stdout empty;
- stderr fixed to `CLI_INTERNAL_FAILURE`;
- exit `1`;
- no traceback.

## Privacy and security contract

The future CLI must preserve all runtime guarantees:

- local Linux only;
- read-only;
- stdlib-only;
- no symlink following;
- no byte reads;
- no hashes;
- no MIME detection;
- no magic-byte inspection;
- no ffprobe;
- no ffmpeg;
- no subprocess;
- no shell execution;
- no network;
- no DB;
- no SaaS;
- no writes;
- no private paths or private names in stdout or stderr;
- sanitized manifest;
- fail-closed limits.

The future CLI must not expand globs, expand `~`, read environment variables, change the working directory, write cache, create folders, create logs, or accept Windows, UNC, `/mnt`, or `wsl.localhost` paths as CLI-level exceptions.

## Next allowed phase

`CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.CLI.IMPLEMENTATION.GATE.V1`

## Acceptance criteria

This readiness gate can close only if:

- the phase identity is exact;
- the expected closure result is exact;
- the base HEAD, previous tag, runtime SHA, and previous phase are documented;
- the future module, invocation, API, arguments, stdout, stderr, exit codes, and privacy contract are documented;
- `cid scan` remains expressly deferred;
- `scripts/local_media_agent/read_only_folder_scanner_cli.py` does not exist in this phase;
- runtime, `pyproject.toml`, packaging, entrypoints, backend, frontend, DB, SaaS, Docker, Alembic, Stripe, auth, AI Jobs, and ledger remain untouched;
- next phase is exactly `CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.CLI.IMPLEMENTATION.GATE.V1`.
