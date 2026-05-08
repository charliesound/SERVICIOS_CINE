# CID Storyboard Sequence-First Architecture Audit

**Date:** 2026-05-08  
**Auditor:** Principal Architect + Lead Product Engineer  
**Scope:** Full CID codebase — storyboard generation flow  

---

## 1. Executive Summary

The current CID architecture allows generating a storyboard from a **full unprocessed script in a single API call**, bypassing any semantic analysis, sequence detection, or shot planning. This produces:

- Generic shots with no dramatic grounding  
- Broken continuity across unrelated scenes  
- Mixed locations, characters, and lighting in the same batch  
- No shot progression logic (establishing → medium → close-up → detail)  
- No guard against "generate everything at once"

---

## 2. Where Full-Script Storyboard Is Permitted

### 2.1. Backend — `storyboard_service.py` (line 699)

```python
if normalized_mode == StoryboardGenerationMode.FULL_SCRIPT:
    return scenes[:max_scenes] if max_scenes and max_scenes > 0 else scenes
```

This returns **every scene in the project** when mode is `FULL_SCRIPT`.  
The `_build_scene_shots()` method then generates `shots_per_scene` generic shots per scene with no shot progression logic.

### 2.2. Backend — `storyboard_routes.py` (line 67)

```python
mode=(payload.generation_mode or payload.mode or StoryboardGenerationMode.FULL_SCRIPT).upper()
```

**Default mode is `FULL_SCRIPT`**. If the frontend omits `generation_mode` and `mode`, the backend defaults to full-script generation.

### 2.3. Backend — `cid_script_to_prompt_routes.py` (line 42)

```python
@router.post("/run", response_model=ScriptToPromptRunResponse)
async def run_script_to_prompt(payload: ScriptToPromptRunRequest) -> ScriptToPromptRunResponse:
    return await run_script_to_prompt_pipeline(...)
```

Accepts full `script_text` and processes ALL scenes without requiring sequence_id.

### 2.4. Frontend — `StoryboardBuilderPage.tsx` (line 64)

```typescript
const [selectedMode, setSelectedMode] = useState<StoryboardSelectionMode>('FULL_SCRIPT')
```

Default mode is `FULL_SCRIPT`. Button at line 463 says `"Generar storyboard completo"`.

### 2.5. Payloads That Activate It

| Entry Point | Payload Field | Value | Effect |
|---|---|---|---|
| `POST /{project_id}/storyboard/generate` | `mode` | `"FULL_SCRIPT"` | Generates shots for all scenes |
| `POST /{project_id}/storyboard/generate` | `generation_mode` | `"FULL_SCRIPT"` | Same, overrides `mode` |
| `POST /{project_id}/storyboard/generate` | (both omitted) | defaults to `FULL_SCRIPT` | Same |
| `POST /api/cid/script-to-prompt/run` | `script_text` | (full script) | Processes all scenes |
| `POST /{project_id}/storyboard/sequences/{seq}/regenerate` | — | `SEQUENCE` mode | Correctly scoped ✅ |

---

## 3. Risk Analysis

| Risk | Severity | Description |
|---|---|---|
| Generic output | **High** | `_build_scene_shots()` uses `<action_text> (style_preset)` as prompt — no shot logic |
| Continuity loss | **High** | Each scene processed independently; no cross-scene continuity |
| Dramatic disconnect | **High** | No dramatic arc, no emotional progression across shots |
| Over-generation | **Medium** | Default mode processes entire script without user intent |
| UX confusion | **Medium** | "Generar storyboard completo" feels correct to users but produces poor results |
| No shot planning | **High** | `_build_cinematic_storyboard_shot()` cycles through a fixed `[shot_size, CU, MS, WS, OTS]` pool regardless of scene content |

---

## 4. Required: Sequence-First Architecture

### 4.1. New Two-Level Flow

```
Full Script
  │
  ▼
LEVEL 1: Full-Script Analysis
  ├── Synopsis (logline, premise, theme)
  ├── Sequence map (all detected sequences)
  ├── Character & location map
  ├── Production breakdown
  └── Recommended sequences for storyboard
  │
  ▼
User selects one or more sequences
  │
  ▼
LEVEL 2: Sequence Storyboard
  ├── Read sequence excerpt
  ├── Analyze dramatic action
  ├── Propose shot breakdown
  ├── Order shots with cinematic logic
  ├── Maintain continuity (characters, location, axis, light)
  ├── Generate individual prompts per shot
  └── Validate each prompt against script text
```

### 4.2. Changes Needed

#### Backend
1. **New models**: `ScriptSynopsisResult`, `ScriptSequenceMap`, `SequenceStoryboardPlan`, `PlannedStoryboardShot`
2. **New services**: `ScriptSynopsisService`, `ScriptSequenceMappingService`, `SequenceStoryboardPlanningService`
3. **Modified `cid_script_to_prompt_pipeline_service.py`**: Three modes — `analyze_full_script()`, `prepare_sequence_storyboard()`, `generate_prompt_for_planned_shot()`
4. **Modified `storyboard_routes.py`**: New endpoints + guard on existing generate
5. **Modified `storyboard_service.py`**: Require `sequence_id` for generation; block `FULL_SCRIPT` mode

#### Frontend
6. **Modified `StoryboardBuilderPage.tsx`**: Two-step UX — analyze → select sequence → plan → generate
7. **Modified `storyboard.ts`**: New types for sequence plan, full analysis

### 4.3. What Must Be Maintained for Backward Compatibility
- `POST /api/cid/script-to-prompt/run` — individual prompt construction (not full storyboard)
- `POST /{project_id}/storyboard/sequences/{seq}/regenerate` — already sequence-scoped ✅
- `GET /{project_id}/storyboard/sequences` — already returns sequence blocks ✅
- `GET /{project_id}/storyboard` — already filters by sequence_id ✅
- `POST /{project_id}/storyboard/comfyui/*` — rendering pipeline ✅

---

## 5. Implementation Plan

| Phase | What | Files |
|---|---|---|
| 2 | New models | `cid_script_to_prompt_schema.py`, `storyboard_schema.py` |
| 3 | Synopsis + sequence mapping | `script_synopsis_service.py`, `script_sequence_mapping_service.py` |
| 4 | Sequence storyboard planning | `sequence_storyboard_planning_service.py` |
| 5 | Pipeline refactor (3 modes) | `cid_script_to_prompt_pipeline_service.py` |
| 6 | Endpoints | `storyboard_routes.py`, `cid_script_to_prompt_routes.py` |
| 7 | Frontend UX | `StoryboardBuilderPage.tsx`, `storyboard.ts` |
| 8 | Metadata enrichment | `storyboard_service.py` |
| 9 | Tests | 4 new test files |
| 10 | Smoke | `smoke_cid_sequence_first_storyboard_contract.py` |
| 11 | Validations | py_compile, pytest, npm build |
| 12 | Git guard | `guard_no_db_commit.sh` |

---

## 6. Summary

| Aspect | Current | Target |
|---|---|---|
| Script analysis | None | Full synopsis + sequence map |
| Shot generation | Per-scene generic | Per-sequence planned |
| Shot progression | Fixed pool rotation | Dramatic logic (establishing → medium → CU → detail) |
| Continuity | None across scenes | Tracked per sequence |
| Mode default | `FULL_SCRIPT` | Requires sequence selection |
| UX flow | One-click generate | Analyze → Select → Plan → Confirm → Generate |
