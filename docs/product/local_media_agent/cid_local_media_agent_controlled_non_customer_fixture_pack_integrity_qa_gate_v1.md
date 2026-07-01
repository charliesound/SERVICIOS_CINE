# CID Local Media Agent — Controlled Non-Customer Fixture Pack Integrity QA Gate V1

Phase: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.INTEGRITY.QA.GATE.V1`

Status: `INTEGRITY_QA_GATE_DEFINED`

Result when closed: `LOCAL_MEDIA_AGENT_CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_INTEGRITY_QA_GATE_V1_CLOSED`

Predecessor phase: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.CREATION.GATE.V1`

Predecessor result: `LOCAL_MEDIA_AGENT_CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_CREATION_GATE_V1_CLOSED`

## Purpose

This gate verifies that the controlled non-customer fixture pack created in the previous gate remains stable, deterministic, small, local, and safe before any later read-only single-file metadata chain is considered.

The gate is intentionally limited to repository fixture integrity. It does not authorize external tool execution, scanner traversal, runtime product behavior, real media processing, customer material, installation, pilot execution, SaaS coupling, backend work, frontend work, or packaging work.

## Fixture pack under audit

Pack ID: `controlled_non_customer_fixture_pack_v1`

Fixture root:

```text
/tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1
```

Repository-relative root:

```text
tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1
```

Expected files:

```text
tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/README.md
tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/manifest.controlled.json
tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt
```

## Expected fixture entry

Fixture ID: `controlled_plain_text_marker_v1`

Relative path:

```text
media/controlled_plain_text_marker.txt
```

Encoding: `utf-8`

MIME type: `text/plain`

Expected bytes: `239`

Expected SHA256:

```text
a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a
```

## Integrity checks required

The QA gate requires all of the following checks to pass:

1. The fixture root exists exactly at the approved repository-relative path.
2. The pack README exists and declares the pack as controlled, non-customer, tiny, deterministic, and not a media sample pack.
3. The manifest exists and is valid JSON.
4. The manifest uses schema version `cid.local_media_agent.controlled_non_customer_fixture_pack.v1`.
5. The manifest pack ID is `controlled_non_customer_fixture_pack_v1`.
6. The manifest contains exactly one fixture entry.
7. The fixture entry uses fixture ID `controlled_plain_text_marker_v1`.
8. The fixture entry points only to `media/controlled_plain_text_marker.txt`.
9. The fixture byte count is exactly `239`.
10. The fixture SHA256 is exactly `a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a`.
11. Boundary flags remain closed for customer material, personal data, real production assets, generated video or audio, external tool execution, scanner execution, network access, runtime behavior, and SaaS coupling.
12. The next allowed technical move remains a separate read-only single-file metadata readiness chain, not a scanner or media-processing chain.

## Explicit non-goals

This gate does not:

- create new fixtures;
- alter existing fixtures;
- run ffprobe;
- run FFmpeg;
- run a scanner;
- decode media;
- inspect real production material;
- inspect customer material;
- create video;
- create audio;
- touch runtime product behavior;
- touch packaging or installers;
- touch backend or frontend surfaces;
- couple fixture logic to SaaS or persistence layers.

## Allowed next gate

If this gate closes successfully, the next safe phase may be:

```text
CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.READ_ONLY.SINGLE_FILE.METADATA.READINESS.GATE.V1
```

That future gate may prepare a read-only single-file metadata chain against the controlled text marker or a later approved fixture, but it must still avoid external tool execution unless a later explicit implementation gate authorizes it.

## Closure decision

Closure decision:

```text
FIXTURE_PACK_INTEGRITY_VERIFIED_FOR_READ_ONLY_SINGLE_FILE_METADATA_PREP
```

Closure result:

```text
LOCAL_MEDIA_AGENT_CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_INTEGRITY_QA_GATE_V1_CLOSED
```
