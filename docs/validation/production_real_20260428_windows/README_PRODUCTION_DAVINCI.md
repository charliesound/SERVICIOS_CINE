# CID Production Synthetic Validation - DaVinci Import

**Fixture Type:** SYNTHETIC PRODUCTION FIXTURE

This is a synthetic fixture for validation testing, NOT real footage.

## Instructions

1. Extract ZIP to: `C:\CID_Production_Synthetic_Validation_20260428\`
2. Open DaVinci Resolve
3. Create new project: `CID_Production_Synthetic_Validation_20260428`
4. File → Import → `C:\CID_Production_Synthetic_Validation_20260428\fcpxml\assembly_windows.fcpxml`

## Expected Behavior

- FCPXML should import without errors
- Timeline should appear with 6 clips (3 scenes x 2 shots minimum)
- Video track with clips
- Audio track with sound
- Media should be online

## Media Location

```
C:\CID_Production_Synthetic_Validation_20260428\media\
├── S01_SH01_TK01_CAM.mov
├── S01_SH01_TK01_SOUND.wav
├── S01_SH02_TK01_CAM.mov
├── S01_SH02_TK01_SOUND.wav
├── S01_SH02_TK02_CAM.mov
├── S01_SH02_TK02_SOUND.wav
├── S02_SH01_TK01_CAM.mov
├── S02_SH01_TK01_SOUND.wav
├── S02_SH01_TK02_CAM.mov
└── S02_SH01_TK02_SOUND.wav
```

## Validation Criteria

| Criterion | Status |
|-----------|--------|
| FCPXML imports | [ ] |
| Timeline appears | [ ] |
| Video clips visible | [ ] |
| Audio clips visible | [ ] |
| Media online | [ ] |
| Duration coherent | [ ] |
| Editable | [ ] |

## Notes

This is a SYNTHETIC PRODUCTION FIXTURE:
- Media files are synthetic, not real footage
- Used for pipeline validation
- Tests the full editorial flow