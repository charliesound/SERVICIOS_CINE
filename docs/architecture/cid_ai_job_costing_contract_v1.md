# CID AI Job Costing Contract v1

Version: 1.0
Status: SPEC / ARCHITECTURE
Date: 2026-06-09
Owners: CID Architecture / CID Product / CID Business
Scope: canonical contract for AI job credit estimation, reservation, consumption, release, and audit traceability in CID SaaS
Companion docs:
- `docs/business/cid_pricing_canonical_v1.md`
- `docs/architecture/cid_billing_models_v1.md`
- `docs/architecture/cid_saas_model_contract_v1.md`
- `docs/architecture/cid_plans_modules_matrix_v1.md`
- `docs/architecture/cid_roles_permissions_matrix_v1.md`
- `src/services/credit_ledger_service.py`
- `src/services/credit_gate_service.py`

## 1. Purpose

This contract defines how CID estimates, reserves, consumes, releases, and audits credits for costly AI jobs. Its purpose is to ensure that:

- no costly AI execution starts without prior credit estimation;
- no costly AI execution starts without prior credit reservation;
- credit consumption happens only after a successful result or an accepted partial result;
- reserved credits are released when the job fails, is cancelled, or is not executed;
- every AI-credit decision is traceable by tenant, project, user, job, and operation type;
- CID remains the source of truth for credit accounting regardless of whether the runtime is an external API, on-demand GPU, ComfyUI workflow, or future local agent.

This phase is contractual and documentary. It does not introduce new code, routes, migrations, or provider integrations.

## 2. Principles

- No costly AI job runs without prior estimation.
- No costly AI job runs without prior reservation.
- Consumption happens only after success or accepted partial completion.
- Release happens after failure, timeout, user cancellation, or execution abort.
- Every credit-relevant action must be traceable by `organization_id`, `project_id`, `user_id`, `job_id`, and `operation_type`.
- The customer pays AI, GPU, provider, and orchestration costs through credits.
- CID does not expose internal provider complexity to the customer; it exposes clear job status, clear credit cost, and clear usage audit.
- CID does not assume fixed owned GPU in the initial phase. Heavy AI may run on external APIs, GPU-on-demand, ComfyUI, or future local agents, but all of them must fit the same credit contract.
- Current credit values may be placeholder or initial canonical values and may later be adjusted by pricing/versioned policy without breaking the lifecycle contract.

## 3. Relationship with Existing Services

### 3.1 `CreditLedgerService`

`CreditLedgerService` is the accounting layer. It owns:

- available credit calculation;
- bucket ordering and bucket debit rules;
- `grant`, `reserve`, `release`, and `consume`;
- idempotency enforcement at ledger-entry level;
- append-only ledger traceability.

The ledger is the final authority on balance mutation.

### 3.2 `CreditGateService`

`CreditGateService` is the internal gating facade for future AI jobs. It currently provides:

- `estimate_credit_cost(...)`
- `check_credit_availability(...)`
- `reserve_credits_for_operation(...)`
- `consume_reserved_credits_for_operation(...)`
- `release_reserved_credits_for_operation(...)`

Its responsibility is to normalize `operation_type`, derive or validate estimated cost, preserve canonical metadata, and delegate the actual accounting mutation to `CreditLedgerService`.

### 3.3 Contract Boundary

- The ledger decides how credits move.
- The gate decides whether a job may start and how much must be reserved.
- Future job runners, worker queues, provider adapters, ComfyUI pipelines, DaVinci Bridge tasks, and local agents must call the gate before they execute any costly action.

## 4. Canonical Lifecycle

The canonical lifecycle for a credit-gated AI job is:

### 4.1 Estimate

Determine `operation_type` and estimated credits before execution. Estimation may come from:

- canonical per-operation constants;
- deterministic formula from known input units;
- explicit approved cost passed by the caller.

If the operation is unknown and no explicit cost exists, the job must not proceed.

### 4.2 Check

Check credit availability for the organization before any costly runtime work starts. The check is advisory and preflight-oriented; it does not mutate balance.

### 4.3 Reserve

Reserve the estimated credits before execution begins. Reservation creates the accounting hold that prevents overspending and establishes the audit trail for the future job.

### 4.4 Execute

Execute the AI job only after successful reservation. Execution may happen in:

- external API provider;
- GPU-on-demand worker;
- versioned ComfyUI workflow;
- DaVinci Bridge assistant workflow;
- future local agent runtime.

### 4.5 Consume

Consume the reservation when the job finishes successfully or when a partial result is explicitly accepted by product policy or user action. Consumption is the point at which the reservation becomes real usage.

### 4.6 Release

Release the reservation when execution does not produce a billable result, including failure before processing, cancellation, timeout without accepted result, or explicit operator abort.

### 4.7 Audit

Persist and expose traceability of estimate, reserve, consume, and release through canonical metadata and ledger entries. Audit must explain what ran, for whom, with which provider/workflow/model, at what estimated cost, and with what final outcome.

## 5. Canonical `operation_type`

### 5.1 Current aligned set

These values must stay aligned with `src/services/credit_gate_service.py`:

| `operation_type` | Current canonical initial cost | Family |
|---|---:|---|
| `script_analysis` | 1 | text / LLM |
| `storyboard_generation` | 12 | image / planning |
| `image_generation` | 8 | image |
| `video_generation` | 40 | video |
| `transcription` | 3 | audio / transcription |
| `sound_sync` | 6 | audio / sync |
| `davinci_bridge_package` | 10 | sync / DaVinci Bridge |

These costs are current canonical initial values for backend alignment. They are allowed to evolve in future pricing versions.

### 5.2 Future planned set

Future operation types may include:

- `comfyui_workflow_run`
- `ai_video_generation`
- `ai_vfx_cleanup`
- `ai_subtitle_generation`
- `ai_dubbing_assist`
- `ai_pitch_deck_generation`
- `ai_distribution_analysis`

No future operation type should go live without:

- deterministic estimation rule;
- canonical metadata definition;
- consume/release rule;
- pricing sign-off if it changes effective customer cost.

## 6. Per-Operation Rules

### 6.1 `script_analysis`

- Description: structured analysis of screenplay/script text using LLM or rule-assisted AI.
- Cost unit: per analysis run.
- Estimation method: fixed canonical cost per run or explicit override for future advanced modes.
- What is reserved: the full estimated credits for the requested run.
- When it is consumed: after analysis payload is produced and accepted as usable output.
- When it is released: if analysis never starts, fails before usable output, times out, or is cancelled.
- Minimum metadata: source script/project reference, mode, prompt version, provider type, model name, output asset ids if any.
- Risks: repeated submission of same script, prompt-version drift, provider retries generating double execution.

### 6.2 `storyboard_generation`

- Description: generation of storyboard planning assets, often combining script understanding and image generation.
- Cost unit: per storyboard job or per approved generation batch.
- Estimation method: canonical fixed estimate now; future deterministic formula may include scenes, shots, or coverage count.
- What is reserved: total estimate for the storyboard operation before image generation starts.
- When it is consumed: when storyboard outputs are generated and attached as usable assets.
- When it is released: if generation is aborted before valid outputs are produced.
- Minimum metadata: scene count, shot count, style preset, provider type, model or workflow id, output asset ids.
- Risks: number of shots may grow during processing; future split between planning and rendering stages.

### 6.3 `image_generation`

- Description: generation or transformation of still images.
- Cost unit: per image batch or per accepted rendering request.
- Estimation method: fixed canonical cost now; future formula may depend on image count, resolution tier, variation count, or control assets.
- What is reserved: full image job estimate before provider submission.
- When it is consumed: when the accepted outputs are delivered or stored.
- When it is released: when the provider call never completes successfully or user cancels before accepted output.
- Minimum metadata: prompt or workflow reference, image count, resolution tier, input asset ids, output asset ids, provider/workflow/model.
- Risks: variation explosion, hidden provider-side retries, multiple output branches for one request.

### 6.4 `video_generation`

- Description: generation or transformation of moving-image assets.
- Cost unit: per video job.
- Estimation method: fixed canonical cost now; future formula may depend on duration, resolution, fps, clips, iterations, or render stage.
- What is reserved: total estimated credits required for the entire planned run.
- When it is consumed: when final or accepted partial video output is available.
- When it is released: when no accepted output exists or the job is cancelled/fails before usable result.
- Minimum metadata: target duration, fps, resolution class, provider/workflow/model, input and output asset ids.
- Risks: expensive provider retries, long-running GPU jobs, partial renders that may or may not be customer-acceptable.

### 6.5 `transcription`

- Description: speech-to-text processing of uploaded or captured audio/video.
- Cost unit: per transcription job.
- Estimation method: fixed canonical cost now; future formula may depend on minutes of media or language complexity.
- What is reserved: the expected transcription cost for the input media.
- When it is consumed: when transcript output is produced and stored.
- When it is released: when transcription fails, is cancelled, or no transcript is accepted.
- Minimum metadata: media duration, language, provider, model, input asset ids, transcript output id.
- Risks: media duration mismatch, partial transcript acceptance, reprocessing after format correction.

### 6.6 `sound_sync`

- Description: synchronization-oriented audio processing such as alignment by waveform, transcript, timecode, or future clapboard/timecode assist.
- Cost unit: per sync job.
- Estimation method: fixed canonical cost now; future formula may depend on clip count, track count, and sync strategy.
- What is reserved: full expected synchronization cost.
- When it is consumed: when sync artifacts or aligned outputs are generated and accepted.
- When it is released: when sync job fails or user cancels before usable result.
- Minimum metadata: clip ids, audio ids, sync method, provider or local engine, output ids.
- Risks: ambiguous sync confidence, clip mismatch, downstream DaVinci packaging retries.

### 6.7 `davinci_bridge_package`

- Description: packaging, analysis, or synchronization work prepared for DaVinci Bridge workflows.
- Cost unit: per package/export/analysis job.
- Estimation method: fixed canonical cost now; future formula may depend on sequence count, clip count, audio assets, export depth, or analysis mode.
- What is reserved: the entire expected package cost before costly processing starts.
- When it is consumed: when the package or analysis is successfully generated and attached to the project.
- When it is released: when package generation is aborted, cancelled, or fails without accepted artifact.
- Minimum metadata: project id, clip ids, audio ids, sequence ids, package type, future sync mode.
- Risks: partial exports, expensive retries, mismatch between package request and actual project state.

### 6.8 Future `comfyui_workflow_run`

- Description: execution of a versioned ComfyUI workflow as a reproducible pipeline.
- Cost unit: per workflow run, not per prompt string.
- Estimation method: deterministic formula from workflow class, node graph, model pack, batch size, iterations, and runtime tier.
- What is reserved: total workflow estimate before queue submission.
- When it is consumed: when output assets are produced and stored.
- When it is released: when workflow never reaches accepted output.
- Minimum metadata: workflow id, workflow version, workflow hash, model pack, custom nodes, input/output asset ids.
- Risks: environment drift, hidden custom-node cost, mismatched workflow versions.

### 6.9 Future operation families

- `ai_video_generation`: variant of video generation for more granular provider classes.
- `ai_vfx_cleanup`: VFX cleanup, rotoscoping, or enhancement.
- `ai_subtitle_generation`: subtitle generation, timing, and QC.
- `ai_dubbing_assist`: dubbing support such as line segmentation, guide timing, or reference voice prep.
- `ai_pitch_deck_generation`: AI generation of commercial pitch/deck assets.
- `ai_distribution_analysis`: AI analysis of markets, festivals, or distribution opportunities.

Each future operation must define the same seven fields before activation.

## 7. Runtime and Provider Categories

CID must distinguish the following runtime families:

### 7.1 Text / LLM

- Typical operations: `script_analysis`, future `ai_distribution_analysis`, future `ai_pitch_deck_generation`.
- Typical drivers: token usage, prompt class, number of artifacts.
- Default contract: fixed estimate now, formula later if needed.

### 7.2 Image

- Typical operations: `storyboard_generation`, `image_generation`, future `ai_vfx_cleanup`.
- Typical drivers: image count, resolution, style/workflow complexity, iterations.

### 7.3 Video

- Typical operations: `video_generation`, future `ai_video_generation`.
- Typical drivers: duration, fps, resolution, variation count, render pipeline depth.

### 7.4 Audio / Transcription

- Typical operations: `transcription`, future `ai_subtitle_generation`, future `ai_dubbing_assist`.
- Typical drivers: media minutes, speakers, language, cleanup complexity.

### 7.5 Sync / DaVinci Bridge

- Typical operations: `sound_sync`, `davinci_bridge_package`.
- Typical drivers: clips, tracks, package contents, analysis mode.

### 7.6 ComfyUI Local

- Must be treated as versioned workflow execution, not as free-form prompts.
- Workflow graph, hash, nodes, required models, and outputs must be traceable.

### 7.7 External API

- CID hides provider complexity from the customer.
- Provider-specific pricing may change internally, but customer credit charge must still be governed by CID’s canonical contract.

### 7.8 GPU-on-demand

- Treat as a costly runtime like any external provider.
- Jobs must still estimate and reserve before provisioning compute.

### 7.9 Future Local Agent

- A local agent may eventually execute some AI tasks on user-side or edge-side runtime.
- Even in that model, if the feature is productized and credit-billed, the same estimate/reserve/consume/release contract applies.

## 8. Overrun Policy

- Default rule: do not execute beyond the reserved amount.
- If an overrun is predicted before execution continues, create a new estimate and a new reservation rather than silently consuming more than planned.
- Avoid negative balances.
- Negative balance is forbidden unless a future explicit Enterprise override contract is introduced and audited.
- A partial accepted result may consume only the amount covered by the accepted scope if product policy defines such granularity later.

## 9. Failures, Cancellations, and Retries

### 9.1 Failure before execution

If the job fails before provider/workflow execution starts, release the reservation in full.

### 9.2 Partial failure

If the job produces a partial result:

- consume if the partial result is accepted by explicit product rule or user action;
- otherwise release.

### 9.3 Timeout

- If timeout occurs before accepted output, release.
- If timeout happens after an externally billable partial result is recovered and accepted, consume according to accepted result policy.

### 9.4 User cancellation

- Cancel before execution: release.
- Cancel during execution: release unless accepted result exists and policy says consume.

### 9.5 Provider charged even though job failed

This is a real operational risk. The contract says:

- customer-facing consumption still follows CID accepted-result policy;
- provider-side loss is an operational cost incident unless future policy explicitly maps it to customer charge;
- such incidents must remain auditable.

### 9.6 Retries

- Retries must be idempotent where possible.
- A retry must not double-consume the same reservation.
- If the retry changes scope materially, create a new estimate and reservation.

## 10. Canonical Metadata

Minimum canonical metadata fields:

- `operation_type`
- `estimated_credits`
- `consumed_credits`
- `provider_type`
- `provider_name` optional
- `workflow_id` optional
- `workflow_version` optional
- `model_name` optional
- `input_asset_ids`
- `output_asset_ids`
- `job_status`
- `failure_reason`
- `reservation_entry_id`
- `consume_entry_id`
- `release_entry_id`

Additional recommended metadata:

- `idempotency_key`
- `prompt_version`
- `workflow_hash`
- `runtime_family`
- `attempt_number`
- `accepted_partial_result`
- `duration_seconds`
- `resolution_tier`

Metadata rules:

- canonical internal fields must not be overwritten by external caller payload;
- metadata must preserve enough context to reconstruct why credits were reserved, consumed, or released;
- asset lists may be empty during preflight but should be filled when outputs exist.

## 11. ComfyUI Rules

- Workflows must be versioned.
- Each workflow should have a stable hash.
- Required models and custom nodes must be identified as part of the runtime contract.
- Cost must be estimated before execution.
- Outputs must be traceable to workflow id/version/hash and to the originating reservation.
- ComfyUI must not be treated as an unstructured prompt box; it must be treated as a reproducible pipeline.

## 12. DaVinci Bridge Rules

- No costly DaVinci Bridge operation runs without reservation.
- Costing may be per package, export, sync pass, or analysis job depending on future breakdown.
- Metadata must capture project, clip, sequence, and audio references.
- Future synchronization modes may include timecode, clapboard/slate, transcript-guided sync, or hybrid methods.
- Packaging and synchronization artifacts must remain auditable like any other AI-costed operation.

## 13. Relationship with Plans, Modules, and Permissions

- Plan or module gates may allow the user to see a feature.
- Credits allow the user to execute the costly operation behind that feature.
- Roles and permissions determine who may launch, approve, retry, or cancel AI jobs.

This means three dimensions must pass together:

1. The plan and module matrix allows access to the capability.
2. The user has role/permission authority to perform the action.
3. The organization has sufficient credits and an allowed billing state.

Examples:

- A plan may expose storyboard generation, but execution still fails if credits are insufficient.
- A user may see billing usage but may not have permission to launch a job.
- A suspended organization may still see historical data but must not launch new costly jobs.

## 14. Edge Cases

- Insufficient credits: reject before execution, no job run starts.
- Duplicate `idempotency_key`: reject duplicate reserve/consume/release mutation.
- Repeated job submission: treat as retry or duplicate according to idempotency and job identity rules.
- Double consume: forbidden; must be blocked by idempotency and job-state checks.
- Unknown operation: reject unless explicit approved cost is provided.
- Deleted or archived project: block execution or require explicit recovery flow.
- User without permissions: block before reservation.
- Suspended organization: block new costly jobs.
- Beta/demo/trial entitlements: may allow feature visibility or limited usage, but still need explicit credit and entitlement policy.

## 15. Implementation Roadmap

- AI job costing backend constants/service alignment
- job reservation wrapper
- AI job table/status integration
- credit usage API
- frontend billing/usage UI
- provider adapters
- ComfyUI workflow registry
- local agent costing
- Stripe/payment integration later

## 16. Final Rule

The final rule of this contract is simple:

- if the operation is costly, estimate first;
- if it may execute, reserve first;
- if it succeeds, consume;
- if it does not produce accepted value, release;
- if it happened, audit it.

CID remains the credit authority. Providers remain replaceable execution layers.
