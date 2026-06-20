# CID Local Media Agent — Product Semantics Decision Record v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.PRODUCT.SEMANTICS.DECISION.RECORD.V1`

## Objective

Document the explicit product semantics decision for non-media files observed in the second controlled scenario.

This decision record selects the product semantics for `.txt` and `.exe` observations.

This phase is documentation-only.

It does not authorize implementation.

## Required prior authorization gate

This phase depends on:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.PRODUCT.SEMANTICS.DECISION.AUTHORIZATION.GATE.V1`

Required prior authorization result:

`PRODUCT_SEMANTICS_DECISION_AUTHORIZATION_GATE_PASS_WITH_NO_PRODUCT_BEHAVIOR_SELECTED`

## Product semantics decision

- `decision_record_status`: `PRODUCT_SEMANTICS_DECISION_RECORD_FILLED`
- `decision_status`: `PRODUCT_SEMANTICS_DECISION_SELECTED`
- `selected_product_semantics`: `NON_MEDIA_REJECTED`
- `selected_product_behavior`: `NON_MEDIA_REJECTED`
- `selected_product_behavior_scope`: `DOCUMENTED_ONLY_NOT_IMPLEMENTED`
- `client_facing_classification_claim`: `NONE`
- `clean_classification_pass_claim`: `NONE`
- `runtime_change_authorized`: `false`
- `scanner_change_authorized`: `false`
- `report_change_authorized`: `false`
- `cli_change_authorized`: `false`

## Decision rationale

The controlled scenario evidence classified `.txt` and `.exe` as rejected.

This decision preserves the observed evidence instead of rewriting it as ignored.

For CID Local Media Agent, `.txt` and `.exe` are not selected media inputs in this controlled scenario.

The chosen product semantics is therefore:

`NON_MEDIA_REJECTED`

This means non-media files are treated as outside the selected media set and rejected by the product semantics for this scenario.

## Observation preserved

The controlled scenario evidence remains:

- `.txt` and `.exe` are classified as rejected
- `.txt` and `.exe` are not classified as ignored
- `accepted_extension_counts=.mov:1,.wav:1`
- `rejected_extension_counts=.exe:1,.txt:1`
- `ignored_extension_counts={}`

## Options not selected

The following options were evaluated as available but are not selected in this decision record:

- `NON_MEDIA_IGNORED`
- `NON_MEDIA_SEPARATE_CATEGORY`
- `NON_MEDIA_POLICY_CONFIGURABLE`
- `OTHER_NAMED_PRODUCT_BEHAVIOR`

## Explicitly still blocked

This decision record does not authorize:

- clean classification PASS claims
- client-facing claims
- scanner behavior changes
- runtime behavior changes
- report behavior changes
- CLI behavior changes
- scanner execution
- ffprobe execution
- ffmpeg execution
- media probing
- media decoding
- report generation
- transcription
- translation
- subtitles
- sync
- NLE export
- SaaS backend changes
- SaaS frontend changes
- database changes
- Docker changes
- Alembic changes
- Stripe changes
- AI Jobs changes
- credits changes
- ledger changes

## Scope boundary

This phase is docs/test-only.

No runtime code, scanner code, report code, CLI code, SaaS code, database code, infrastructure code, or media-processing code may be changed by this phase.

## Gate result

`PASS_WITH_PRODUCT_SEMANTICS_DOCUMENTED_ONLY`

Final product semantics for this controlled scenario are documented as `NON_MEDIA_REJECTED`.

Implementation remains unauthorized.

Client-facing claims remain unauthorized.

Clean classification PASS claims remain unauthorized.
