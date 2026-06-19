# CID Local Media Agent — CLI Synthetic Visible Report Preflight Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.CONTRACT.V1`

## Objective

This phase defines the contract for a future preflight check for the synthetic visible report CLI command.

This is a documentation and test-only phase. It does not implement preflight runtime behavior.

## Current audited command

The currently implemented development CLI wrapper is:

- `scripts/cid_local_media_agent_synthetic_visible_report_cli.py`

The current command is:

`synthetic-visible-report`

The current allowed arguments remain:

- `--fixture`
- `--output-dir`
- `--allow-overwrite`
- `--format markdown`

The current allowed generated file remains:

- `cid_local_media_agent_synthetic_visible_report_v1.md`

## Future preflight purpose

A future preflight command or mode may check whether a synthetic visible report can be generated safely before generation.

The future preflight must be local-only, deterministic, and side-effect-light.

It must validate only the readiness of the synthetic demo workflow.

It must not analyze real media.

It must not call external media probing binaries.

It must not contact network services.

It must not upload client material.

It must not integrate with SaaS, backend, frontend, database runtime, Docker, Alembic, scanner, installer, licensing, subtitle export, or NLE export.

## Allowed future preflight checks

A future preflight may validate:

1. The fixture argument is present.
2. The fixture path exists.
3. The fixture path points to the approved synthetic fixture contract or a future explicitly approved synthetic fixture.
4. The fixture can be parsed as JSON.
5. The fixture contains the minimum fields required by the synthetic Markdown renderer.
6. The output directory argument is present.
7. The output directory exists or can be created according to the approved future behavior.
8. The output directory is a directory, not a file.
9. The output filename is exactly `cid_local_media_agent_synthetic_visible_report_v1.md`.
10. The output file does not already exist unless overwrite is explicitly allowed.
11. The requested format is exactly `markdown`.
12. The renderer script exists.
13. The scanner script is not imported or executed.
14. No real media path is accepted.
15. No subtitle, NLE, SaaS, cloud, database, installer, or licensing operation is triggered.

## Future preflight output contract

A future preflight may produce terminal output only.

Allowed successful summary:

- command name
- `PREFLIGHT_PASS`
- expected output filename
- synthetic/local-first notice
- human review notice

Allowed failure summary:

- `PREFLIGHT_FAIL`
- short stable reason code
- safe user-facing message

The future preflight must not print:

- absolute local paths
- raw fixture JSON
- stack traces
- environment variables
- secrets
- client media paths
- personal data
- database connection information
- network endpoint details

## Future preflight exit codes

A future preflight should reserve these exit codes:

- `0`: preflight passed
- `2`: user input or contract validation failed
- `3`: safe local environment validation failed
- `4`: output safety validation failed
- `1`: unexpected controlled failure

The future implementation may refine reason codes, but it must keep deterministic user-facing behavior.

## Explicitly not authorized in this phase

This contract does not authorize:

- implementing the preflight command
- adding CLI arguments
- changing the current CLI wrapper
- changing the renderer
- changing the scanner
- adding packaging
- adding installable entry point wiring
- adding backend or frontend integration
- adding database runtime behavior
- adding Docker or Alembic changes
- calling external media probing binaries
- reading real media files
- synchronizing audio and video
- transcribing audio
- translating dialogue
- generating subtitle files
- exporting to NLE formats
- adding installer behavior
- adding licensing behavior
- uploading client files

## Human review

Any future generated report remains a synthetic demo artifact requiring human review.

CID remains assistive and does not replace the producer, editor, assistant editor, post supervisor, or human reviewer.

## Verdict

`PREFLIGHT_CONTRACT_DEFINED_FOR_FUTURE_SYNTHETIC_VISIBLE_REPORT_ONLY`

No runtime implementation is authorized by this contract.
