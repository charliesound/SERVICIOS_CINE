# CID Local Media Agent - Read-Only Folder Scanner Commercial Alias Implementation Gate V1

## Phase

`CID_LAPTOP_LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_COMMERCIAL_ALIAS_IMPLEMENTATION_GATE_V1`

## Expected result

`CID_LAPTOP_LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_COMMERCIAL_ALIAS_IMPLEMENTATION_GATE_V1_COMPLETED_AND_VERIFIED`

## Stable base

- Repository: `/opt/SERVICIOS_CINE`
- Branch: `main`
- Base commit: `b8f4d11d574ff2edc12ba7ccd995c8d27cc61af4`
- Base tree: `3fa695445beff33cffc0e6b8fd7ad3e5ce818a45`
- Stable tag: `cid-dev-stable-local-media-agent-read-only-folder-scanner-commercial-alias-readiness-gate-v1-20260805`

## Authorized changes

This implementation gate changes exactly four paths.

Modified:

- `pyproject.toml`

Created:

- `scripts/local_media_agent/cid_cli.py`
- `docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_commercial_alias_implementation_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_read_only_folder_scanner_commercial_alias_implementation_gate_v1.py`

No other path is authorized.

## Packaging contract

The installed commercial entrypoint is exactly:

```toml
cid = "scripts.local_media_agent.cid_cli:main"
```

The project contains exactly four installed scripts after this implementation.

## Commercial command

The canonical command is:

```bash
cid scan --input-root ABSOLUTE_LOCAL_LINUX_FOLDER
```

Only the `scan` subcommand is implemented.

## Umbrella help

`cid --help` returns exit code 0 and writes exactly:

```text
Usage: cid COMMAND [OPTIONS]
Commands:
  scan    Scan one absolute local Linux folder in read-only mode.
Options:
  --help
```

It does not delegate to the scanner.

## Scan help

`cid scan --help` returns exit code 0 and writes exactly:

```text
Usage: cid scan --input-root ABSOLUTE_LOCAL_LINUX_FOLDER
Options:
  --input-root ABSOLUTE_LOCAL_LINUX_FOLDER
  --help
```

It does not delegate to the scanner.

## Delegation

Any non-help invocation beginning with `scan` removes only that initial token and delegates the remaining arguments without transformation to:

```text
scripts.local_media_agent.read_only_folder_scanner_cli.run_cli
```

The same stdout and stderr streams are forwarded.

The delegated exit code is returned unchanged.

The adapter does not inspect, resolve, normalize or validate the input path.

## Umbrella rejection

Invalid umbrella invocations write only:

```text
CID_CLI_ARGUMENTS_REJECTED
```

to stderr with a single newline, keep stdout empty and return exit code 2.

## Controlled internal failure

An unexpected adapter or delegation exception writes only:

```text
CID_CLI_INTERNAL_FAILURE
```

to stderr with a single newline and returns exit code 1.

## Frozen scanner files

The implementation does not modify:

- `scripts/local_media_agent/read_only_folder_scanner.py`
- `scripts/local_media_agent/read_only_folder_scanner_cli.py`
- the commercial alias readiness document;
- the commercial alias readiness static test.

## Operational boundaries

This implementation does not add:

- filesystem inspection to the umbrella adapter;
- ffprobe or ffmpeg;
- subprocess or shell execution;
- network or database access;
- SaaS integration;
- logging, cache or writes;
- additional subcommands;
- dynamic command discovery;
- licensing or activation.

The existing scanner CLI remains the sole owner of scanner parsing, validation, manifest serialization, stdout, stderr and exit status semantics.

## Verification performed

This implementation gate runs only the targeted implementation unit test.

It does not install the package, build artifacts or execute the scanner.

It does not stage, commit, tag or push.

## Next authorized phase

`CID_LAPTOP_LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_COMMERCIAL_ALIAS_IMPLEMENTATION_GATE_CONTROLLED_QA_V1`
