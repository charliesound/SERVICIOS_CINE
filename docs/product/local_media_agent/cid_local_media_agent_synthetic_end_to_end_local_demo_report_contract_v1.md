# CID Local Media Agent — Synthetic End-to-End Local Demo Report Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.CONTRACT.V1`

## Objective

This contract defines the first visible synthetic end-to-end local demo report for CID Local Media Agent.

The goal is to move from internal contracts toward a demonstrable local report that can be shown to producers, editors, assistant editors, DITs, post supervisors, and trusted early customers.

This phase is contract-only.

It does not implement the report generator.

It does not execute ffprobe.

It does not execute ffmpeg.

It does not add external command execution.

It does not scan real client media.

It does not read real video files.

It does not read real audio files.

It does not modify scanner runtime.

It does not modify SaaS runtime.

It does not create an installer.

It does not create licensing or activation logic.

## Current audited baseline

Current stable HEAD before this contract:

`541278a`

Previous audit decision:

`CONTINUE_BUT_PIVOT_TOWARD_VISIBLE_SYNTHETIC_DEMO`

The audit concluded that CID Local Media Agent has a strong architecture, privacy, contract, and QA foundation, but does not yet have a functional local demo or commercial beta.

This contract starts the visible demo track without weakening local-only privacy constraints.

## Demo positioning

The demo should communicate this simple idea:

"CID Local Media Agent analiza una carpeta local de material audiovisual sin subir vídeos ni audios a la nube y genera una radiografía técnica y editorial para preparar montaje, sonido, subtítulos y postproducción."

The first demo report must be synthetic. It must be believable for audiovisual professionals but must not contain real client material, real titles, real filenames, real folder paths, or real metadata extracted from media.

## Intended demo audience

The report must be understandable by:

- producer
- director
- assistant director
- editor
- assistant editor
- DIT
- postproduction supervisor
- sound editor
- subtitle coordinator
- school or training coordinator
- trusted early commercial contact

The report must not require the reader to understand internal test doubles, command wrappers, fixtures, or failure path contracts.

## Demo promise

The synthetic demo report should show what the future tool will feel like when a user points it to a local project folder.

It should show:

- local input folder label
- local output report label
- detected media-like items
- synthetic technical metadata
- synthetic warnings
- suggested folder organization
- editorial preparation notes
- postproduction preparation notes
- privacy confirmation
- zero cloud upload confirmation
- next-step recommendations

## Required report formats

A future implementation may generate these local artifacts:

- JSON report
- Markdown report
- HTML report

The initial visible demo should prioritize Markdown and HTML because they are easier to show to non-technical stakeholders.

The JSON report should remain useful for future automated tests and future tool integration.

## Required report sections

The synthetic demo report must contain these sections:

1. Executive summary
2. Local-only privacy notice
3. Input folder summary
4. Detected media-like inventory
5. Synthetic technical metadata summary
6. Clip grouping proposal
7. Audio and video relationship hints
8. Potential sync preparation notes
9. Editorial preparation notes
10. Postproduction risk warnings
11. Suggested folder organization
12. Subtitle and transcription readiness notes
13. DaVinci Resolve future export readiness notes
14. Items requiring human review
15. Next recommended actions
16. Report limitations

## Required local-only privacy statements

The report must clearly state:

- no video file was uploaded
- no audio file was uploaded
- no client media left the local machine
- no cloud analysis was required
- synthetic demo metadata was used
- private absolute paths are hidden
- raw filenames may be replaced by safe labels
- human review is required before production decisions

## Required synthetic input model

The synthetic demo may use a conceptual input folder label such as:

`LOCAL_PROJECT_INPUT_SYNTHETIC`

It may contain synthetic items such as:

- `CAM_A_SYNTHETIC_CLIP_001`
- `CAM_A_SYNTHETIC_CLIP_002`
- `CAM_B_SYNTHETIC_CLIP_001`
- `AUDIO_SYNTHETIC_TAKE_001`
- `AUDIO_SYNTHETIC_TAKE_002`
- `STILLS_SYNTHETIC_REFERENCE_001`
- `DOC_SYNTHETIC_NOTES_001`

These labels are placeholders only. They must not imply real client filenames.

## Required synthetic media categories

The report should classify synthetic items into:

- video
- audio
- still image
- production document
- unknown or unsupported
- ignored non-media item

## Required synthetic metadata fields

For each media-like item, the future report model should support:

- `safe_item_id`
- `safe_display_label`
- `category`
- `container_hint`
- `codec_hint`
- `duration_hint`
- `frame_rate_hint`
- `resolution_hint`
- `audio_channels_hint`
- `sample_rate_hint`
- `timecode_hint`
- `camera_or_recorder_hint`
- `shooting_day_hint`
- `scene_or_block_hint`
- `sync_candidate_group`
- `language_hint`
- `transcription_readiness`
- `subtitle_readiness`
- `human_review_required`
- `warning_codes`

All values must remain synthetic until a later authorized real metadata phase.

## Required warning vocabulary

The synthetic report should be able to show warnings such as:

- `MISSING_AUDIO_PAIR`
- `POSSIBLE_DOUBLE_SYSTEM_SOUND`
- `POSSIBLE_CAMERA_SPLIT`
- `MISSING_TIMECODE`
- `FRAME_RATE_MISMATCH`
- `SAMPLE_RATE_MISMATCH`
- `LOW_AUDIO_CHANNEL_INFORMATION`
- `UNSUPPORTED_CONTAINER_HINT`
- `UNKNOWN_MEDIA_TYPE`
- `NEEDS_HUMAN_REVIEW`
- `READY_FOR_EDITOR_REVIEW`
- `READY_FOR_DIT_REVIEW`
- `READY_FOR_SOUND_REVIEW`

The report must distinguish warnings from confirmed errors.

## Suggested folder organization

The report should suggest a safe local organization such as:

- `01_VIDEO`
- `02_AUDIO`
- `03_STILLS`
- `04_DOCUMENTS`
- `05_REPORTS`
- `06_REVIEW_NEEDED`
- `07_EXPORTS_FOR_EDIT`

This is only a suggestion. The demo must not move, rename, delete, or modify files.

## Editorial preparation notes

The report should translate technical findings into editor-friendly language.

Examples of allowed synthetic conclusions:

- this group looks like a camera and sound candidate pair
- this item may need timecode review
- this item may need waveform sync in a future phase
- this group may be ready for assistant editor review
- this item may require DIT verification
- this audio item may need sound department review

The report must avoid pretending that real sync, real transcription, or real metadata extraction has happened.

## Postproduction risk warnings

The report should include risks that matter in real postproduction:

- missing or uncertain audio pair
- mixed frame-rate hints
- missing timecode hints
- unclear shooting day grouping
- unclear scene or block grouping
- unsupported item type
- material requiring human verification
- transcription not yet performed
- subtitle generation not yet performed
- DaVinci export not yet generated

## Human review model

The report must include a section called:

`Items requiring human review`

This section must make clear that CID Local Media Agent supports postproduction preparation but does not replace assistant editor, DIT, sound, or post supervisor judgment.

## Demo limitations

The report must explicitly say:

- this is a synthetic demo
- no actual client media was analyzed
- no real technical metadata was extracted
- no waveform sync was performed
- no timecode sync was performed
- no slate detection was performed
- no transcription was performed
- no translation was performed
- no DaVinci Resolve timeline was exported
- no production decision should be made from the synthetic report alone

## Future implementation constraints

A future implementation must keep the first synthetic report generator:

- local-only
- deterministic
- safe-label based
- fixture-driven
- free from real media reads
- free from external binary execution
- free from cloud calls
- free from database writes
- free from SaaS runtime coupling
- suitable for unit tests
- suitable for stakeholder demo screenshots

## Acceptance criteria for this contract

This contract is accepted only if:

- the phase remains documentation/test-only
- only this document and its unit test are changed
- no scanner runtime file is modified
- no SaaS runtime file is modified
- no external command execution is introduced
- no real media processing is introduced
- no installer logic is introduced
- no licensing or activation logic is introduced
- the report sections are fully defined
- the privacy statements are explicit
- the synthetic metadata fields are complete
- the warning vocabulary is complete
- the limitations are explicit
- the next phase remains gated

## Next recommended phase

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.CONTRACT.QA.GATE.V1`

After that, the implementation path should be:

1. synthetic demo report contract QA
2. synthetic demo report fixture contract
3. synthetic demo report generator implementation readiness gate
4. synthetic demo report generator minimal implementation
5. synthetic demo report QA
6. stakeholder-readable demo report package

## Final contract decision

Contract decision:

`SYNTHETIC_END_TO_END_LOCAL_DEMO_REPORT_CONTRACT_READY_FOR_QA`

This phase authorizes QA of the contract only.

It does not authorize implementation.
