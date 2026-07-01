# CID Local Media Agent — Controlled Non-Customer Fixture Pack Creation Gate V1

## Gate identity

- Phase: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.CREATION.GATE.V1`
- Result token: `LOCAL_MEDIA_AGENT_CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_CREATION_GATE_V1_CLOSED`
- Status: `CREATED_CONTROLLED_NON_CUSTOMER_FIXTURE_PACK`
- Decision: `CONTROLLED_FIXTURE_PACK_CREATED_WITH_TEXT_ONLY_DETERMINISTIC_BOUNDARIES`
- Previous gate required: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.CREATION.READINESS.GATE.V1`
- Next allowed gate: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.INTEGRITY.QA.GATE.V1`

## Purpose

This gate creates the first controlled non-customer fixture pack for CID Local Media Agent.
The pack is intentionally minimal and text-only. It is designed to validate fixture-root
integrity before any later metadata chain, visible report chain, or scanner-limited chain.

This is not a product runtime feature and not a customer pilot action.

## Created files

The gate creates exactly these fixture-pack files in addition to this document and its unit test:

- `tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/README.md`
- `tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/manifest.controlled.json`
- `tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt`

## Fixture inventory

| Fixture ID | Relative path | Type | Expected bytes | Expected SHA256 |
|---|---|---:|---:|---|
| `controlled_plain_text_marker_v1` | `media/controlled_plain_text_marker.txt` | text/plain | `239` | `a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a` |

## Boundaries

Allowed in this gate:

- creation of a small deterministic text fixture;
- creation of a controlled JSON manifest;
- creation of a fixture README;
- repository-local test validation of bytes and SHA256;
- documentation of future allowed and blocked gates.

Explicitly not allowed in this gate:

- customer material;
- personal data;
- real production material;
- video or audio fixture files;
- external tool execution;
- scanner execution;
- scanner traversal outside the fixture root;
- runtime product behavior;
- pyproject changes;
- installer changes;
- backend or frontend changes;
- SaaS or database coupling;
- network access.

## Manifest contract

The manifest must be committed with deterministic content and must include:

- `schema_version = cid.local_media_agent.controlled_non_customer_fixture_pack.v1`
- `pack_id = controlled_non_customer_fixture_pack_v1`
- `status = CREATED_CONTROLLED_NON_CUSTOMER_FIXTURE_PACK`
- the exact gate phase;
- the fixture root;
- one fixture record for `controlled_plain_text_marker_v1`;
- byte count and SHA256 for the marker fixture;
- explicit false flags for customer material, personal data, external tool execution, scanner execution, runtime behavior, network access, and SaaS/database coupling.

## Acceptance criteria

This gate is accepted only if:

1. exactly the expected five files are staged by the apply script;
2. the fixture pack root exists at the planned path;
3. the manifest is valid JSON;
4. the marker fixture byte count equals `239`;
5. the marker fixture SHA256 equals `a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a`;
6. the manifest values match the actual marker file;
7. no video or audio extensions are present in the fixture pack;
8. no customer, personal, production, runtime, scanner, backend, frontend, installer, pyproject, SaaS, or database file is modified;
9. prior gate tests still pass;
10. repository guards pass before commit;
11. the commit and tag are pushed only after validation.

## Closure statement

When closed, this gate means only that a tiny controlled non-customer fixture pack exists.
It does not authorize metadata extraction, external tool usage, scanner execution, customer
material, pilot usage, installation outside the development repository, or product runtime behavior.
