# CID Local Media Agent controlled non-customer fixture pack v1

Status: CREATED_CONTROLLED_NON_CUSTOMER_FIXTURE_PACK

Phase: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.CREATION.GATE.V1`

This fixture pack is intentionally tiny, deterministic, and non-customer.
It is not a media sample pack. It exists only to provide a safe root for
fixture integrity checks before any later read-only single-file metadata chain.

## Included files

- `manifest.controlled.json`
- `media/controlled_plain_text_marker.txt`

## Boundary

Allowed:

- local repository tests;
- deterministic SHA256 and byte-size validation;
- future read-only planning against this controlled fixture root.

Prohibited:

- customer material;
- personal data;
- real production assets;
- generated video or audio;
- external tool execution;
- scanner traversal outside this root;
- network access;
- runtime product behavior;
- SaaS or database coupling.

Next allowed gate: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.INTEGRITY.QA.GATE.V1`
