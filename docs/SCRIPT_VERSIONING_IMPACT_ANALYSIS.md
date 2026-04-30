# Script Versioning + Impact Analysis

## Overview

CID now supports script versioning to track changes across project iterations and analyze production impact.

## Why Script Versioning?

When a user uploads a new version of their script:
- Old versions are preserved (not overwritten)
- Changes are detected (scenes added/removed/modified)
- Impact on downstream modules is analyzed
- Users can decide what to regenerate

## Data Models

### ScriptVersion
- `id`, `project_id`, `organization_id`
- `version_number` (V1, V2, V3...)
- `title`, `source_filename`
- `script_text`, `content_hash` (SHA256)
- `word_count`, `scene_count`
- `status` (active/archived)
- `notes`, `created_at`

### ScriptChangeReport
- `from_version_id`, `to_version_id`
- `summary` (e.g., "+3 scenes, -1 scene")
- `added_scenes_json`, `removed_scenes_json`, `modified_scenes_json`
- `added_characters_json`, `removed_characters_json`
- `production_impact_json`
- `budget_impact_json`
- `storyboard_impact_json`
- `recommended_actions_json`

### ProjectModuleStatus
- `module_name` (storyboard/budget/funding/etc)
- `status` (updated/needs_review/partial_outdated/unchanged)
- `affected_by_change_report_id`

## Services

### ScriptVersionService
- `create_initial_version()` - First script (V1)
- `create_new_version()` - Subsequent versions (V2+)
- `list_versions()` - Version history
- `activate_version()` - Switch active version
- `get_module_statuses()` - Get module impact statuses
- `update_module_status()` - Mark module affected

### ScriptChangeAnalysisService
- `compare_versions()` - Generate change report
- `extract_scenes()` - Parse INT./EXT. headers
- `extract_characters()` - Extract CHARACTER names
- `extract_locations()` - Extract locations
- `analyze_production_impact()` - Night exteriors, new locations
- `analyze_budget_impact()` - Estimated cost change
- `analyze_storyboard_impact()` - Frames to regenerate

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/projects/{id}/script/versions` | GET | List versions |
| `/projects/{id}/script/versions` | POST | Create new version |
| `/projects/{id}/script/versions/{version_id}` | GET | Get version detail |
| `/projects/{id}/script/versions/{version_id}/activate` | POST | Switch active version |
| `/projects/{id}/script/versions/compare` | POST | Compare two versions |
| `/projects/{id}/script/change-reports` | GET | List change reports |
| `/projects/{id}/module-status` | GET | Get module impacts |

## Impact Analysis

When script V2 is uploaded vs V1:

**Detection:**
- Added scenes
- Removed scenes
- Modified scenes
- New locations
- New characters

**Impact on Modules:**

| Module | Default Impact | Action |
|-------|----------------|--------|
| script | updated | Auto |
| analysis | needs_review | Manual review |
| breakdown | needs_review | Recalculate |
| storyboard | partial_outdated | Review affected scenes |
| budget | needs_review | Recalculate |
| funding | needs_review | Check eligibility |
| producer_pack | needs_review | Update dossier |
| distribution | needs_review | Update pitch |

## Recommended Actions

Generated automatically based on changes:

```json
[
  {
    "module": "storyboard",
    "action": "review_affected_scenes",
    "priority": "high",
    "reason": "5 scenes modified"
  },
  {
    "module": "budget",
    "action": "recalculate", 
    "priority": "medium",
    "reason": "Night exteriors added"
  }
]
```

## Usage Flow

1. **Project has Script V1** (active)
2. **User uploads new script** (V2)
3. **System detects change** (if hash differs)
4. **Creates ScriptVersion V2** (archived V1)
5. **Generates ScriptChangeReport**
6. **Marks modules as needs_review/partial_outdated**
7. **User sees recommendations** in Dashboard
8. **User decides what to regenerate**

## What's NOT Done

- Full frontend UI for version comparison (basic existing)
- Automatic regeneration (user controls)
- Budget estimator integration (future sprint)
- Full distribution pitch (future sprint)