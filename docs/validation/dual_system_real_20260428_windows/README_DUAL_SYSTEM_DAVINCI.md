# Dual-System DaVinci Import Guide - Windows

## Package Overview
This package contains FCPXML exports for testing dual-system audio sync in DaVinci Resolve.

## Files Structure

```
C:\CID_Dual_System_Validation_20260428\
├── fcpxml\
│   ├── assembly_conservative_windows.fcpxml
│   └── assembly_linked_audio_experimental_windows.fcpxml
├── media\
│   ├── A001_0101_001.mov    (video)
│   ├── A001_0102_001.mov    (video)
│   ├── S001_0101_001.WAV    (audio)
│   └── S002_0102_001.WAV    (audio)
├── reports\
│   └── media_relink_report_windows.json
└── validation_log_windows.md
```

## Media Setup

**IMPORTANT**: Create the media folder and place dummy/test media files:

```
C:\CID_Dual_System_Validation_20260428\media\
```

Copy video files:
- A001_0101_001.mov
- A001_0102_001.mov

Copy audio files:
- S001_0101_001.WAV
- S002_0102_001.WAV

## Validación en DaVinci Resolve

### Test 1: Conservative (Safe Baseline)
1. Abrir DaVinci Resolve
2. Crear nuevo proyecto: `CID_Dual_System_Validation_20260428`
3. File > Import > Timeline > Import AAF, EDL, XML...
4. Seleccionar: `fcpxml/assembly_conservative_windows.fcpxml`
5. **Verificar**:
   - [ ] Timeline carga sin error
   - [ ] Clips de video aparecen en timeline
   - [ ] Notas muestran audio externo
   - [ ] Duración correcta (~20 segundos)

### Test 2: Experimental (Linked Audio)
1. File > Import > Timeline > Import AAF, EDL, XML...
2. Seleccionar: `fcpxml/assembly_linked_audio_experimental.fcpxml`
3. **Verificar**:
   - [ ] Timeline carga sin error
   - [ ] Clips de video aparecen
   - [ ] Pista "Linked Audio" aparece
   - [ ] Audio sincronizado con video
   - [ ] Duración correcta

## Checklist de Validación

| Criterion | Conservative | Experimental |
|-----------|--------------|--------------|
| Import succeeds | PASS / FAIL | PASS / FAIL |
| Timeline loads | PASS / FAIL | PASS / FAIL |
| Video visible | PASS / FAIL | PASS / FAIL |
| Audio visible | N/A | PASS / FAIL |
| Audio synced | N/A | PASS / FAIL |
| Duration correct | PASS / FAIL | PASS / FAIL |
| No offline clips | PASS / FAIL | PASS / FAIL |

## Decision Logic

If Conservative = PASS and Experimental = PASS:
- **Decision**: LINKED AUDIO CANDIDATE VALIDATED

If Conservative = PASS and Experimental = PARTIAL:
- **Decision**: CONSERVATIVE ONLY / EXPERIMENTAL PARTIAL

If Conservative = PASS and Experimental = FAIL:
- **Decision**: CONSERVATIVE ONLY

If Conservative = FAIL:
- **Decision**: NO-GO (report issue immediately)

## Report Results

After testing, update:
1. `validation_log_windows.md` with results
2. `DUAL_SYSTEM_GO_NO_GO_REPORT.md` with final decision

## Questions?
Report issues: https://github.com/anomalyco/opencode/issues