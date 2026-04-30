# CID Target Data Model

## 1. Entities Overview

| Entity | Status | Notes |
|--------|--------|-------|
| Project | EXISTS | Central entity |
| Script | EXISTS | For analysis |
| Scene | EXISTS | Narrative model |
| Character | EXISTS | In narrative |
| Location | STUB | Partial |
| ProductionBreakdown | MISSING | Needs development |
| BudgetEstimate | EXISTS | Budget estimator |
| BudgetLine | MISSING | Needs definition |
| FundingOpportunity | EXISTS | funding_routes |
| GrantApplication | STUB | Partial |
| ProducerContact | STUB | producer_catalog |
| DistributorContact | MISSING | Needs development |
| CinemaContact | MISSING | Needs development |
| PlatformContact | MISSING | Needs development |
| SalesOpportunity | STUB | demo_service partial |
| PitchDeck | PARTIAL | presentation_service |
| Dossier | PARTIAL | project_document |
| StoryboardShot | EXISTS | storyboard model |
| MediaAsset | EXISTS | ingest model |
| DocumentAsset | EXISTS | document model |
| CameraReport | EXISTS | ingest model |
| SoundReport | EXISTS | ingest model |
| ScriptNote | EXISTS | DocumentAsset |
| DirectorNote | EXISTS | DocumentAsset |
| Take | EXISTS | editorial model |
| AssemblyCut | EXISTS | editorial model |
| Deliverable | EXISTS | delivery model |

## 2. Existing Entities

### Project
- `models/core.py` / `models/narrative.py`
- Central entity for all operations

### Script
- `models/narrative.py`
- Stores script content and analysis results

### Scene
- `models/narrative.py`
- Scene breakdown with characters, locations

### Character
- `models/narrative.py`
- Character analysis

### Location
- `models/narrative.py` (STUB)
- Partial location support

### MediaAsset
- `models/ingest_scan.py`
- Indexed media files (references, not copies)

### DocumentAsset
- `models/ingest_document.py`
- Ingested documents

### IngestScan
- `models/ingest_scan.py`
- Scan execution records

### StoryboardShot
- `models/storyboard.py`
- Individual storyboard frames

### AssemblyCut
- `models/editorial.py`
- Assembly edit result

### Take
- `models/editorial.py`
- Recommended take with metadata

### Deliverable
- `models/delivery.py`
- Export deliverables

## 3. Partial Entities (Need Extension)

### FundingOpportunity
- Basic exists in `funding_routes.py`
- Needs: scoring, alerts, deadlines

### GrantApplication
- Partial in demo_service
- Needs: full application flow

### ProducerContact
- Partial in `producer_catalog.py`
- Needs: CRM integration

### PitchDeck
- Partial in `presentation_service`
- Needs: templates

### Dossier
- Partial in `project_document_service`
- Needs: full document generation

## 4. Missing Entities (Need Development)

### ProductionBreakdown
- Full breakdown model not exists
- Should include:
  - scene_requirements
  - location_requirements
  - cast_requirements
  - VFX_requirements
  - sound_requirements
  - art_requirements
  - complexity_score

### BudgetLine
- Budget lines not modeled
- Should include:
  - category
  - description
  - estimated_cost
  - actual_cost
  - contingency

### DistributorContact
- Not modeled
- Should include:
  - company_name
  - contact_name
  - email
  - territory
  - genres
  - status

### CinemaContact
- Not modeled
- Should include:
  - cinema_name
  - address
  - capacity
  - contact_name
  - email

### PlatformContact
- Not modeled
- Should include:
  - platform_name
  - contact_name
  - email
  - content_type
  - region

### SalesOpportunity
- Partial in demo_service
- Complete needed:
  - project_id
  - contact_type
  - contact_id
  - stage
  - next_action
  - notes
  - created_at
  - updated_at

## 5. Legacy / Duplicate Check

### Routes Duplication
- `funding_routes.py` vs `project_funding_routes.py` vs `funding_catalog_routes.py`
- Check if consolidation needed

### Service Duplication
- Multiple funding_* services
- Check overlap

## 6. Recommendations

### High Priority
1. Create ProductionBreakdown model
2. Consolidate funding services
3. Create SalesOpportunity model

### Medium Priority
1. Create DistributorContact model
2. Create CinemaContact model
3. Create PlatformContact model

### Low Priority
1. Extend BudgetLine model
2. Create PitchDeck templates

## 7. Not Creating Migrations

This document is for planning purposes only.
No migrations should be created without:
- Full audit of existing models
-确认 de schema final
- Sprint dedicated to data model changes