# CID Local Media Agent — Scanner CLI ffprobe Synthetic Fixtures Manifest Contract v1

## Phase

CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.SYNTHETIC.FIXTURES.MANIFEST.CONTRACT.V1

## Objective

This phase defines the contract for the future fixture_manifest.json used by synthetic ffprobe fixture tests.

This phase is documentation-only and test-only.

It does not create fixture_manifest.json.

It does not create fixture folders.

It does not create media fixtures.

It does not create video files.

It does not create audio files.

It does not execute ffprobe.

It does not execute ffmpeg.

It does not modify scanner runtime.

It does not add subprocess execution.

It does not inspect real media.

## Current baseline

The previous phase defined the future synthetic fixture policy.

This phase narrows the future manifest schema before any future implementation creates fixtures, probes fixtures or writes technical metadata.

The scanner must remain unchanged in this phase.

## Future manifest path

A later explicit implementation phase may create the manifest at:

tests/fixtures/local_media_agent/ffprobe_synthetic/fixture_manifest.json

This contract phase must not create that file.

This contract phase must not create the tests/fixtures/local_media_agent/ffprobe_synthetic/ folder.

## Manifest purpose

The future fixture manifest must describe each synthetic fixture without exposing local machine details or private project details.

The manifest must allow tests to verify that every fixture is:

- synthetic
- intentionally included
- small enough
- privacy safe
- reproducible or explicitly committed
- expected to produce controlled ffprobe behavior
- human reviewed

## Required manifest top-level fields

The future manifest must be a JSON object with these top-level fields:

- manifest_version
- phase
- manifest_scope
- generated_by
- fixture_root
- path_policy
- privacy_policy
- size_policy
- human_review_policy
- fixtures

## Required top-level values

The future manifest must use:

- manifest_version: 1
- phase: CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.SYNTHETIC.FIXTURES.MANIFEST.V1
- manifest_scope: synthetic_ffprobe_fixtures_only
- generated_by: local_media_agent_test_fixture_contract
- fixture_root: tests/fixtures/local_media_agent/ffprobe_synthetic
- path_policy: relative_paths_only
- privacy_policy: no_private_metadata_no_real_media
- size_policy: tiny_fixtures_only
- human_review_policy: required_before_commit

## Fixture list

The fixtures field must be a list.

Every fixture entry must be a JSON object.

Every fixture entry must include:

- fixture_id
- relative_path
- fixture_category
- media_kind
- synthetic_origin
- expected_probe_status
- expected_has_video
- expected_has_audio
- expected_duration_policy
- expected_size_policy
- expected_privacy_safe
- human_reviewed
- commit_allowed
- notes

## Fixture identifiers

fixture_id must be stable, lowercase and descriptive.

fixture_id must not include:

- client names
- project names
- people names
- production company names
- real locations
- shoot dates
- camera roll names
- sound roll names
- drive names
- local user names

Allowed fixture_id examples:

- synthetic_video_minimal
- synthetic_audio_minimal
- synthetic_video_with_audio_minimal
- synthetic_unsupported_media_placeholder
- synthetic_invalid_media_placeholder
- synthetic_permission_denied_placeholder

## Relative paths

relative_path must be relative to tests/fixtures/local_media_agent/ffprobe_synthetic.

relative_path must not be absolute.

relative_path must not contain:

- ..
- leading slash
- drive letters
- home directory paths
- user names
- network paths
- cloud paths
- backslashes
- environment variable syntax

## Fixture categories

Allowed fixture_category values:

- synthetic_video_minimal
- synthetic_audio_minimal
- synthetic_video_with_audio_minimal
- synthetic_unsupported_media_placeholder
- synthetic_corrupt_or_invalid_media_placeholder
- synthetic_permission_denied_placeholder

No other fixture_category value is allowed without a later explicit phase.

## Media kinds

Allowed media_kind values:

- video
- audio
- video_with_audio
- unsupported_placeholder
- invalid_placeholder
- permission_placeholder

## Synthetic origin

synthetic_origin must describe how the fixture was created or why it is safe.

Allowed synthetic_origin values:

- generated_by_test_command
- committed_synthetic_binary
- committed_text_placeholder
- committed_invalid_placeholder
- permission_scenario_placeholder

Synthetic origin must not refer to real media, client media, downloaded stock media, online videos, mobile phone clips, drone clips, screen recordings or private pilot material.

## Expected probe statuses

Allowed expected_probe_status values:

- available
- unsupported_media
- invalid_json
- permission_denied
- probe_failed
- privacy_redacted

The missing ffprobe status is handled by availability preflight and must not require a fixture.

Timeout behavior should be tested through mocked execution in a later phase and must not require large fixture media.

## Expected boolean fields

The following fields must be booleans:

- expected_has_video
- expected_has_audio
- expected_privacy_safe
- human_reviewed
- commit_allowed

human_reviewed must be true before committing binary fixtures.

commit_allowed must be true before committing binary fixtures.

## Duration and size policies

expected_duration_policy must use one of:

- not_applicable
- less_than_or_equal_2_seconds
- placeholder_no_duration

expected_size_policy must use one of:

- less_than_or_equal_512_kib
- placeholder_tiny_file
- manifest_only_no_file

The future fixture folder must not exceed 2 MiB total without a separate approval phase.

## Privacy restrictions

The manifest must not contain:

- absolute input paths
- absolute output paths
- local user names
- home directory paths
- drive labels
- network paths
- cloud paths
- GPS coordinates
- real location names
- real shoot dates
- project names
- client names
- production company names
- camera serial numbers
- lens serial numbers
- device serial numbers
- raw ffprobe JSON
- raw stdout
- raw stderr
- shell commands
- full argv

## Output restrictions

The future manifest must only describe source fixtures.

Future probe outputs must still be written under --output-root.

The manifest must not authorize outputs beside fixture source files.

The manifest must not authorize modifying fixture source files.

## Human review

The manifest must require human review before fixture acceptance.

Human review must confirm:

- the fixture is synthetic
- the fixture is not derived from real production material
- the fixture contains no private metadata
- the fixture is small enough
- the fixture is safe to commit if binary
- the fixture has a documented purpose
- the fixture does not create product claims

## Real media remains blocked

Real media probing remains blocked after this contract.

A future real media phase must be explicit and separate.

The project must pass manifest contract, fixture creation validation, synthetic probe validation and privacy validation before considering any real media probing.

## Non-goals

This phase does not implement ffprobe probing.
This phase does not implement fixture generation.
This phase does not add fixture binary files.
This phase does not add fixture_manifest.json.
This phase does not add real media.
This phase does not call ffprobe.
This phase does not call ffmpeg.
This phase does not add subprocess runtime.
This phase does not modify scripts/cid_media_agent_scan.py.
This phase does not create technical_metadata output.
This phase does not touch SaaS runtime.
This phase does not touch DB, models, Alembic, Docker, frontend, Stripe, AI Jobs, credits or ledger.

## Acceptance criteria

This contract is accepted when tests verify:

- phase name is present
- documentation-only and test-only scope is explicit
- future manifest path is documented but not created
- future fixture folder is documented but not created
- required top-level manifest fields are documented
- required fixture entry fields are documented
- allowed fixture categories are documented
- allowed media kinds are documented
- allowed expected probe statuses are documented
- relative path rules are documented
- privacy restrictions are documented
- human review requirements are documented
- real media remains blocked
- scanner runtime is not modified
