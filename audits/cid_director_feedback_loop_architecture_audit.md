# CID Director Feedback Loop — Architecture Audit

## 1. What Already Exists

### Services
| Service | File | Relevance |
|---|---|---|
| `StoryboardService` | `src/services/storyboard_service.py` | Versioned generation, metadata_json storage, `_next_generation_version()`, `_deactivate_scope_shots()`. Handles legacy + cinematic intelligence paths. |
| `PromptConstructionService` | `src/services/prompt_construction_service.py` | Builds `PromptSpec` from `CinematicIntent`. Integrates `DirectorialIntent`, `MontageIntent`, `StyleReferenceProfile`, `EnrichedVisualIntent`. |
| `CinematicIntentService` | `src/services/cinematic_intent_service.py` | Builds `CinematicIntent` from scene + director lens + montage profile. |
| `ScriptVisualAlignmentService` | `src/services/script_visual_alignment_service.py` | Aligns script excerpt with reference profile. Produces `EnrichedVisualIntent` with `non_negotiable_story_elements`, `non_negotiable_visual_elements`. |
| `VisualReferenceAnalysisService` | `src/services/visual_reference_analysis_service.py` | Stub analysis. Returns `StyleReferenceProfile` with `prompt_modifiers`, `negative_constraints`, `transferable_traits`. |
| `ContinuityMemoryService` | `src/services/continuity_memory_service.py` | Builds continuity anchors and project visual bible across scenes. |
| `SemanticPromptValidationService` | `src/services/semantic_prompt_validation_service.py` | Validates prompt against intent. |
| `SequenceStoryboardPlanningService` | `src/services/sequence_storyboard_planning_service.py` | Shot-level planning with continuity rules, visual style guidance. |

### Schemas
| Schema | File | Fields |
|---|---|---|
| `CinematicIntent` | `cid_script_to_prompt_schema.py` | subject, action, environment, dramatic_intent, framing, shot_size, camera_angle, lens, lighting, color_palette, composition, movement, mood, director_lens_id, directorial_intent, montage_intent, editorial_beats, shot_editorial_purpose, continuity_anchors, required_elements, forbidden_elements |
| `PromptSpec` | `cid_script_to_prompt_schema.py` | positive_prompt, negative_prompt, model_hint, width, height, seed_hint, continuity_anchors, semantic_anchors, editorial_purpose, montage_intent, validation_status, validation_errors |
| `DirectorialIntent` | `cid_script_to_prompt_schema.py` | mise_en_scene, blocking, camera_strategy, suspense_or_emotion_strategy, rhythm_strategy, performance_notes, editorial_notes, coverage_strategy, edit_sensitive_prompt_guidance |
| `StoryboardShot` | `models/storyboard.py` | metadata_json (JSON text field, stores serialized intent/prompt/reference) |
| `EnrichedVisualIntent` | `cid_visual_reference_schema.py` | merged_intent_summary, non_negotiable_story_elements, non_negotiable_visual_elements, negative_guidance |

### Routes
| Route | File | Purpose |
|---|---|---|
| `POST /{project_id}/storyboard/sequences/{sequence_id}/regenerate` | `storyboard_routes.py` | Regenerates with overwrite=True. Returns `StoryboardGenerationAuditResponse`. |

### Frontend
| Component | File | Purpose |
|---|---|---|
| `DirectorVisualReferencePanel` | `src_frontend/src/components/storyboard/DirectorVisualReferencePanel.tsx` | Upload/link reference image, extract profile, script alignment, enriched intent. |
| `StoryboardBuilderPage` | `src_frontend/src/pages/StoryboardBuilderPage.tsx` | 3-tab builder with shot grid, metadata display, DirtyShot tracking. |

## 2. What Can Be Reused

| Component | Reuse Strategy |
|---|---|
| `PromptConstructionService.build_prompt_spec()` | Call with modified intent after revision. |
| `ScriptVisualAlignmentService.align()` | Reuse to detect conflicts between director note and script/reference. |
| `EnrichedVisualIntent.non_negotiable_story_elements` | Protect these elements from being changed. |
| `EnrichedVisualIntent.non_negotiable_visual_elements` | Protect these from being changed. |
| `StoryboardService._next_generation_version()` | Reuse versioning strategy for revisions. |
| `CinematicIntent` fields (lighting, camera_angle, shot_size, etc.) | Target fields for director note interpretation. |
| `metadata_json` on `StoryboardShot` | Store revision history without separate table. |
| `DirectorVisualReferencePanel` UI | Can be extended for director feedback input. |

## 3. What Must NOT Be Duplicated

- **Prompt construction logic** must not be reimplemented — always go through `PromptConstructionService`.
- **Cinematic intent building** must not be reimplemented — use `CinematicIntentService.build_intent()`.
- **Script parsing** must not be reimplemented — use `cid_script_scene_parser_service.parse_script()`.
- **Sequence planning** must not be reimplemented — use `SequenceStoryboardPlanningService`.
- **Visual reference alignment** must not be reimplemented — use `ScriptVisualAlignmentService`.
- **Version tracking** must not be reimplemented — extend `_next_generation_version`.

## 4. Where Director Feedback Fits

```
Director Note
    │
    ▼
DirectorFeedbackInterpretationService
    ├── Reads note, category, severity
    ├── Reads original PromptSpec from StoryboardShot.metadata_json
    ├── Reads CinematicIntent / DirectorialIntent from metadata_json
    ├── Reads EnrichedVisualIntent / non_negotiable elements from metadata_json
    ├── Reads visual reference profile from metadata_json
    ├── Interprets: what is requested vs what is protected
    └── Returns DirectorFeedbackInterpretation
            │
            ▼
    PromptRevisionService
        ├── Takes interpretation + original PromptSpec
        ├── Applies: lighting changes, camera changes, tone changes, etc.
        ├── Protects: non_negotiable_story_elements, non_negotiable_visual_elements
        ├── Preserves: continuity_anchors, required_elements, character actions
        ├── Returns PromptRevisionPatch
        │
        ▼
    StoryboardService.revise_storyboard_shot_with_feedback()
        ├── Creates new metadata_json with revision_parent
        ├── Preserves ALL original metadata
        ├── Stores revision history inside metadata_json
        └── Returns StoryboardRevisionResult
```

## 5. What Models Are Missing

| Missing Model | Reason |
|---|---|
| `DirectorFeedbackNote` | Structured representation of a director's note. |
| `DirectorFeedbackInterpretation` | CID's interpretation of the note against original context. |
| `PromptRevisionPatch` | Original vs revised prompts with change tracking. |
| `StoryboardRevisionPlan` | Scope of regeneration (single shot, selected shots, sequence). |
| `StoryboardRevisionResult` | API response for a revision operation. |

## 6. What Endpoints Are Missing

| Missing Endpoint | Reason |
|---|---|
| `POST /{project_id}/storyboard/shots/{shot_id}/feedback` | Submit director feedback for a single shot. |
| `POST /{project_id}/storyboard/sequences/{sequence_id}/feedback` | Submit director feedback for a sequence. |
| `GET /{project_id}/storyboard/shots/{shot_id}/revisions` | Get revision history for a shot. |

## 7. What Tests Are Missing

| Missing Test | Reason |
|---|---|
| `test_director_feedback_interpretation_service.py` | Test interpretation of notes about lighting, camera, tone, script conflicts. |
| `test_prompt_revision_service.py` | Test that prompts are revised correctly and protected elements preserved. |
| `test_storyboard_director_feedback_revision.py` | Test integration with StoryboardService, metadata preservation, revision history. |

## 8. Architecture Principles (Not To Break)

1. **Sequence-First Storyboard Planning**: Storyboard must always go through sequence selection. FULL_SCRIPT is not allowed for direct generation.
2. **Script-Visual Alignment**: Reference enriches but does NOT replace script truth.
3. **Visual Reference Pipeline**: Reference profiles guide without being copied literally.
4. **Landing V5**: Not related to this feature.
5. **Non-destructive revision**: Original metadata is ALWAYS preserved. Revisions are additive.
6. **Continuity anchors**: Must be preserved across revisions.
