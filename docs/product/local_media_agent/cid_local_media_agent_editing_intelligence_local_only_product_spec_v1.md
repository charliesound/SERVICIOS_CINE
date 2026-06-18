# CID Local Media Agent — Editing Intelligence Local-Only Product Spec v1

## 1. Phase

`CID.LOCAL_MEDIA_AGENT.EDITING_INTELLIGENCE.LOCAL_ONLY.PRODUCT.SPEC.V1`

## 2. Objective

This document defines the product and architecture contract for **CID Local Media Agent**, the local app/CLI used by **CID Editing Intelligence** to process audiovisual material on the client's controlled system.

The module must scan locally ingested media, synchronize video and audio, transcribe multilingual dialogue, generate Spanish translated working subtitles, summarize relevant content, and prepare a rough-cut package for DaVinci Resolve.

This phase is product/specification only. It does not implement the media scanner, sync engine, transcription engine, translation engine, DaVinci exporter, licensing server, installer, payment gateway, iLok integration, user interface, backend routes, database models, migrations, Docker configuration, or real media processing.

## 3. Core principle: media never leaves the client system

CID Local Media Agent must be designed around a strict local-only media policy.

The following files must never be uploaded, copied to CID SaaS, transmitted to external services, or moved outside the client's controlled system by default:

- original camera media;
- original sound files;
- video files;
- audio files;
- proxies;
- extracted WAV files;
- generated analysis audio;
- thumbnails;
- still frames;
- DaVinci project media;
- source subtitles;
- source transcripts, unless explicitly authorized;
- translated subtitles, unless explicitly authorized;
- editorial summaries, unless explicitly authorized.

The app may work in two modes:

1. **Fully local mode**: no CID SaaS connection is required for processing.
2. **CID-connected mode**: CID can coordinate jobs, validate licenses, and receive only explicitly authorized metadata or reports.

In both modes, the original audiovisual media remains local.

## 4. Product positioning

Public product line:

- **CID Editing Intelligence**

Local executable component:

- **CID Local Media Agent**

Commercial promise:

> From raw local media to a synchronized, transcribed, summarized, Spanish-subtitled rough-cut package for DaVinci Resolve, without uploading client media.

The module is assistive. It does not replace the editor, director, sound team, assistant editor, translator, or postproduction supervisor.

## 5. Target users

The system is intended for:

- producers;
- postproduction supervisors;
- assistant editors;
- editors;
- documentary teams;
- sound postproduction teams;
- multilingual productions;
- production companies with internal employees and external freelancers;
- projects where source media privacy is critical.

## 6. Supported operating systems

CID Local Media Agent must be designed for installation on:

- Windows;
- macOS;
- Linux.

The app must not require the client to manually install Python.

The installer or preflight process must verify required local dependencies and either bundle them, install them safely, or provide controlled installation instructions depending on licensing and platform constraints.

## 7. Local dependency policy

The app must detect or provide access to:

- FFmpeg;
- ffprobe;
- optional local transcription models;
- optional translation models;
- optional GPU acceleration;
- DaVinci Resolve if installed.

DaVinci Resolve must not be installed by CID Local Media Agent. It may only be detected and used when already installed by the client.

The app must not silently install heavy dependencies without user approval.

## 8. Preflight check

Before processing any media, the app/CLI must run a preflight check covering:

- operating system;
- CPU architecture;
- available disk space;
- read permission for input folder;
- write permission for output folder;
- FFmpeg availability;
- ffprobe availability;
- optional model availability;
- DaVinci Resolve detection;
- license status;
- privacy mode;
- local-only guarantee;
- output directory safety.

A failed preflight must not modify original media.

## 9. Local scan requirements

The scanner must read a user-selected local folder, disk, RAID, SSD, or NAS path.

It must identify candidate media such as:

- `.mov`;
- `.mp4`;
- `.mxf`;
- `.wav`;
- `.bwf`;
- `.aif`;
- `.aiff`;
- `.flac`, when allowed;
- sidecar metadata files, when supported.

The scanner must generate a local media catalog with:

- asset identifier;
- local relative path or sanitized path;
- media type;
- duration;
- codec;
- frame rate;
- sample rate;
- channel count;
- timecode if present;
- file size;
- container format;
- creation/modification timestamps;
- detected audio/video streams;
- privacy status.

The scanner must not rename, move, delete, or rewrite original media.

## 10. Synchronization requirements

The synchronization engine must attempt matching in this priority order:

1. timecode;
2. scene/take/roll/name metadata;
3. waveform;
4. clap/slate detection;
5. manual review.

Each synchronization result must include:

- video asset id;
- audio asset id;
- sync method;
- offset;
- confidence level;
- warnings;
- human review requirement;
- reason for decision.

Confidence levels:

- `high`;
- `medium`;
- `low`;
- `failed`;
- `manual_review_required`.

The system must never pretend that an uncertain sync is final.

## 11. Timecode sync

When valid timecode is available in video and audio assets, the sync engine should prefer timecode matching.

The system must detect:

- missing timecode;
- mismatched frame rate;
- drift risk;
- duplicated timecode;
- ambiguous matches;
- camera/audio clock mismatch.

Ambiguous timecode matches must be sent to human review.

## 12. Waveform sync

When camera scratch audio and external production sound are available, the system may extract temporary local audio analysis files and estimate sync offset by waveform correlation.

Temporary analysis files must remain local and be stored only in the configured output/work directory.

Waveform sync must report:

- estimated offset;
- confidence score;
- possible drift;
- match quality;
- review requirement.

## 13. Clap/slate fallback

Clap/slate detection is a fallback, not the primary sync method.

The module may attempt clap/slate detection using:

- strong audio transients;
- visual change near slate action;
- metadata clues;
- scene/take labels.

The system must flag slate-based sync as reviewable unless confidence is high and corroborated by other data.

## 14. Multilingual transcription

The transcription engine must support multilingual productions.

It must:

- detect language per clip, segment, or speaker when possible;
- preserve original-language transcript;
- generate timestamped transcript segments;
- support speaker labeling when available;
- mark uncertain language or transcript regions;
- avoid overwriting the original dialogue with translation.

The original transcript is the source record.

## 15. Spanish translated subtitles

The module must generate Spanish translated working subtitles from multilingual source material.

It must preserve separately:

- original transcript;
- original-language subtitles;
- Spanish translated working subtitles;
- optional bilingual subtitles.

Spanish translated subtitles are working subtitles unless validated by a human reviewer.

The output must clearly mark:

- source language;
- target language `es`;
- translation confidence if available;
- human review requirement;
- whether the subtitle is final or working.

The system must not claim automatic subtitles are final delivery subtitles without human validation.

## 16. Editorial summary

The module must generate local editorial summaries such as:

- per-clip summary;
- global summary of all processed clips;
- important moments;
- strong dialogue lines;
- possible selects;
- technical problems;
- translation/subtitle review needs;
- clips useful for teaser or promotion;
- clips requiring manual review.

Summaries may be generated locally. If a connected model or CID service is later used, the client must explicitly authorize what text metadata may leave the local system. Media must still remain local.

## 17. DaVinci Resolve rough-cut package

The module must prepare a DaVinci Resolve-friendly package.

Initial outputs may include:

- Spanish `.srt` subtitles;
- marker CSV;
- selects CSV;
- rough-cut metadata JSON;
- OpenTimelineIO timeline;
- EDL/FCPXML when supported;
- import instructions;
- sync report;
- editorial summary.

The first production-ready promise must be a **selects timeline / rough-cut assist**, not an automatically finished edit.

The module assists the editor. It does not replace the editor.

## 18. Avid and other NLEs

Avid Media Composer, Premiere Pro, and other NLE integrations are future adapters.

The first MVP target is DaVinci Resolve because it is suitable for a controlled rough-cut package and common in postproduction workflows.

Future Avid support may include ALE, EDL, AAF-related workflows, or metadata handoff, but this phase does not implement Avid integration.

## 19. Licensing model

CID Local Media Agent must support commercial licensing.

Required license concepts:

- monthly subscription;
- yearly subscription;
- trial license;
- project-based license;
- organization account;
- named users;
- seats;
- device activation limit;
- activation and deactivation;
- offline grace period;
- feature entitlements;
- license audit logs.

The buyer and the real user may be different people. The license model must assume productoras may have employees, assistants, editors, freelancers, or interns using the tool.

## 20. Anti-piracy requirements

The anti-piracy model must protect the software without violating client privacy.

Allowed protections:

- signed installer;
- signed app binary;
- account activation;
- organization license;
- named user activation;
- device binding;
- seat limits;
- offline signed token;
- feature gating;
- server-side subscription validation;
- local license cache;
- remote deactivation of software access;
- safe license telemetry.

Forbidden protections:

- spyware behavior;
- rootkit behavior;
- screen monitoring;
- copying client media;
- uploading client media;
- blocking client media;
- deleting client media;
- encrypting client media;
- scanning unrelated folders;
- sending complete local paths without permission;
- sending transcripts without permission;
- requiring permanent internet connection for normal professional use.

## 21. iLok/PACE feasibility

The product should evaluate iLok/PACE as an optional high-security licensing method.

Potential activation models:

- CID account and device activation;
- iLok USB hardware key;
- iLok Cloud;
- computer activation;
- organization license plus iLok protection for professional plans.

iLok/PACE should be considered especially for postproduction, sound, and professional editing environments where dongle-based licensing is already familiar.

iLok/PACE must not compromise the local-only media policy.

This phase does not implement iLok/PACE. It only records it as a required feasibility line.

## 22. Offline mode

The system must support offline work.

Recommended behavior:

- initial activation online;
- signed offline license token;
- offline grace period;
- clear expiry date;
- non-destructive expiry behavior.

When a license expires, the app may block new processing jobs but should not prevent the client from accessing previously generated local results.

## 23. Privacy-safe telemetry

In connected mode, the app may report only license and operational metadata when authorized or required by the license agreement.

Acceptable examples:

- license validation event;
- activated user;
- activated device hash;
- feature used;
- job started;
- job completed;
- number of processed clips;
- error category.

Forbidden by default:

- videos;
- audios;
- frames;
- thumbnails;
- transcripts;
- subtitles;
- full local paths;
- project names;
- personal dialogue;
- private editorial summaries.

## 24. Suggested MVP sequence

The recommended implementation path is:

1. product spec;
2. data contract;
3. local scanner CLI;
4. ffprobe adapter;
5. local output folder contract;
6. timecode/name sync prototype;
7. waveform sync prototype;
8. multilingual transcription prototype;
9. Spanish translated working subtitles;
10. editorial summary;
11. DaVinci rough-cut package;
12. license mock;
13. organization/users/devices licensing spec;
14. cross-platform installer spec;
15. iLok/PACE feasibility study;
16. commercial demo pack.

## 25. Local Media Agent phase isolation

All Local Media Agent work must remain separated by explicit phases.

The Local Media Agent product line must not touch CID SaaS runtime, backend routes, database models, Alembic migrations, Docker configuration, frontend code, Stripe/payment code, AI Jobs runtime, credits, ledger, workers, production configuration, or integration code until a future phase explicitly authorizes SaaS integration.

Before that explicit integration phase exists, Local Media Agent work may only create isolated product documentation, tests, local-only contracts, local CLI prototypes, demo fixtures, and local output contracts that do not modify the operational SaaS.

This isolation rule protects the current CID SaaS while allowing the Local Media Agent product line to advance safely.

## 26. Explicit non-goals of this phase

This phase does not:

- process real client media;
- read private disks;
- create a GUI;
- create a DaVinci project;
- call DaVinci Resolve;
- install FFmpeg;
- install models;
- implement licensing;
- implement Stripe;
- implement iLok;
- implement transcription;
- implement translation;
- implement waveform sync;
- modify CID SaaS runtime;
- touch database models;
- touch Alembic;
- touch Docker;
- touch `.env`;
- touch frontend;
- commit or tag code.

## 27. Product decision

CID Local Media Agent is a local execution layer for CID Editing Intelligence.

The correct commercial framing is:

> The software is installed in the client's system, reads locally ingested material, synchronizes video and audio, transcribes multilingual dialogue, generates Spanish working subtitles, summarizes content, and prepares a DaVinci Resolve rough-cut package. Original media remains under the client's control and never leaves the local system.
