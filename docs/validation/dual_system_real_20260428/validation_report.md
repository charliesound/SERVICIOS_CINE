# Validation Report - Dual-System Real Fixture
Date: 2026-04-28

## Fixture Information
- Project: APARTMENT
- Scene: 1
- Date: 2026-04-28
- Fixture Type: synthetic-realistic
- Status: READY

## Structure

```
docs/validation/dual_system_real_20260428/
├── video/
│   ├── A001_0101_001.mov.metadata.json
│   └── A001_0102_001.mov.metadata.json
├── audio/
│   ├── S001_0101_001.wav.metadata.json
│   ├── S001_0101_001.wav.ixml.json
│   ├── S002_0102_001.wav.metadata.json
├── reports/
│   ├── camera_report_day1.csv
│   ├── sound_report_day1.csv
│   ├── media_relink_report.json
│   ├── recommended_takes.json
│   ├── assembly_summary.json
│   └── editorial_notes.txt
├── fcpxml/
│   ├── Apartment_conservative.fcpxml
│   ├── Apartment_linked_audio_experimental.fcpxml
│   └── manifest.json
├── logs/
└── validation_report.md (this file)
```

## Test Results

### Smoke Tests
All tests passed:
- smoke_dual_system_fcpxml_variants.py: PASS
- smoke_fcpxml_real_paths.py: PASS
- smoke_editorial_package.py: PASS
- smoke_bwf_ixml_metadata.py: PASS
- smoke_dual_system_reconcile.py: PASS

### FCPXML Validation
- Conservative: Structurally valid
- Experimental: Structurally valid
- Both variants generate correctly

### Media Relink Report
- Video resources: 2 (resolved)
- Audio resources: 2 (resolved with iXML/BEXT metadata)
- Dual-system matched: 2/2

## Workflow Execution

Simulated workflow completed:
1. MediaAsset video: Created
2. MediaAsset audio: Created
3. Audio metadata scan: Parsed
4. Camera/Sound/Script/Director reports: Generated
5. Reconcile: Matched by scene/shot/take
6. Scoring: Recommended takes identified
7. AssemblyCut: Generated
8. Export FCPXML: Both variants created
9. Media_relink_report: Generated

## Output Files

- assembly.json
- reports/media_relink_report.json
- reports/recommended_takes.json
- reports/assembly_summary.json
- reports/editorial_notes.txt
- fcpxml/Apartment_conservative.fcpxml
- fcpxml/Apartment_linked_audio_experimental.fcpxml
- fcpxml/manifest.json

## Status: READY FOR MANUAL DA VINCI TEST