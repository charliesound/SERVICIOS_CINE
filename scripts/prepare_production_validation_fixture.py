#!/usr/bin/env python3
"""
Prepare production validation fixture.
Creates synthetic production media if no real paths provided.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

VALIDATION_DIR = Path("/opt/SERVICIOS_CINE/docs/validation/production_real_20260428")
MEDIA_ROOTS = VALIDATION_DIR / "media_roots"
REPORTS_DIR = VALIDATION_DIR / "reports"
SCRIPT_DIR = VALIDATION_DIR / "script"
LOGS_DIR = VALIDATION_DIR / "logs"
EXPORTS_DIR = VALIDATION_DIR / "exports"

FIXTURE_TYPE = "SYNTHETIC_PRODUCTION_FIXTURE"

CAMERA_TAKES = [
    "S01_SH01_TK01_CAM.mov",
    "S01_SH01_TK02_CAM.mov",
    "S01_SH02_TK01_CAM.mov",
    "S01_SH02_TK02_CAM.mov",
    "S02_SH01_TK01_CAM.mov",
    "S02_SH01_TK02_CAM.mov",
]

SOUND_TAKES = [
    "S01_SH01_TK01_SOUND.wav",
    "S01_SH01_TK02_SOUND.wav",
    "S01_SH02_TK01_SOUND.wav",
    "S01_SH02_TK02_SOUND.wav",
    "S02_SH01_TK01_SOUND.wav",
    "S02_SH01_TK02_SOUND.wav",
]

def check_ffmpeg():
    """Check if ffmpeg is available."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def create_mov(path: Path, duration_sec: float = 4.0):
    """Create a synthetic MOV file using ffmpeg."""
    if not check_ffmpeg():
        path.touch()
        path.write_bytes(b"\x00" * 1024)
        return
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=black:s=1920x1080:r=24:d={duration_sec}",
        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
        "-c:v", "prores_ks",
        "-profile:v", "2",
        "-c:a", "pcm_s16le",
        "-t", str(duration_sec),
        str(path),
    ]
    try:
        subprocess.run(cmd, capture_output=True, timeout=30)
    except Exception:
        path.touch()
        path.write_bytes(b"\x00" * 1024)

def create_wav(path: Path, duration_sec: float = 4.0, sample_rate: int = 48000):
    """Create a synthetic WAV file."""
    if not check_ffmpeg():
        path.touch()
        path.write_bytes(b"\x00" * 1024)
        return
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"anullsrc=r={sample_rate}:cl=stereo",
        "-c:a", "pcm_s16le",
        "-ar", str(sample_rate),
        "-t", str(duration_sec),
        str(path),
    ]
    try:
        subprocess.run(cmd, capture_output=True, timeout=30)
    except Exception:
        path.touch()
        path.write_bytes(b"\x00" * 1024)

def create_camera_report():
    """Create camera report CSV."""
    content = """reel,scene,shot,take,filmroll,camera,lens,rate,fps,circular,notes
R001,01,01,01,A001,cam1,35mm,24,24,NG,Focus issue
R001,01,01,02,A001,cam1,35mm,24,24,OK,Good take
R001,01,02,01,A001,cam1,35mm,24,24,OK,Good take
R001,01,02,02,A001,cam1,35mm,24,24,NG,Frame out
R001,02,01,01,A002,cam1,35mm,24,24,OK,Good take
R001,02,01,02,A002,cam1,35mm,24,24,OK,Good take
"""
    (REPORTS_DIR / "camera_report.csv").write_text(content)

def create_sound_report():
    """Create sound report CSV."""
    content = """reel,scene,shot,take,roll,circular,notes,sync
S001,01,01,01,001,OK,Good sound,Slate
S001,01,01,02,001,OK,Good sound,Slate
S001,01,02,01,001,OK,Good sound,Slate
S001,01,02,02,001,Noisy,Background noise,Slate
S001,02,01,01,002,OK,Good sound,Slate
S001,02,01,02,002,OK,Good sound,Slate
"""
    (REPORTS_DIR / "sound_report.csv").write_text(content)

def create_script_notes():
    """Create script notes CSV."""
    content = """scene,shot,description,action,dialogue,notes
01,01,INT. OFFICE - DAY,John enters the office,Hello?,
01,02,INT. OFFICE - DAY,John sits at desk,Sit down please,
02,01,EXT. STREET - DAY,John walks down street,Walking,
"""
    (REPORTS_DIR / "script_notes.csv").write_text(content)

def create_director_notes():
    """Create director notes markdown."""
    content = """# Director Notes

## Scene 1
- SH01: Wide shot, establish office
- SH02: Close-up on John's face

## Scene 2
- SH01: Tracking shot, follow John

## General
- Prefers natural lighting
- Keep audio clean
- Watch for background noise
"""
    (REPORTS_DIR / "director_notes.md").write_text(content)

def create_test_script():
    """Create test script."""
    content = """FADE IN:

INT. OFFICE - DAY

JOHN enters the room. He looks around, surprised.

                    JOHN
          (surprised)
          Hello?

He sits at the desk.

                    JOHN
          (sitting)
          Mind if I sit?

CUT TO:

EXT. STREET - DAY

JOHN walks down the street, deep in thought.

                    JOHN
          (thinking)
          Where am I going?

FADE OUT.

THE END
"""
    (SCRIPT_DIR / "test_script.txt").write_text(content)

def main():
    print(f"Preparing production validation fixture: {FIXTURE_TYPE}")
    
    camera_root = MEDIA_ROOTS / "camera"
    sound_root = MEDIA_ROOTS / "sound"
    
    camera_root.mkdir(parents=True, exist_ok=True)
    sound_root.mkdir(parents=True, exist_ok=True)
    
    print("Creating camera media...")
    for take in CAMERA_TAKES:
        path = camera_root / take
        if not path.exists():
            create_mov(path)
        print(f"  Created: {take}")
    
    print("Creating sound media...")
    for take in SOUND_TAKES:
        path = sound_root / take
        if not path.exists():
            create_wav(path)
        print(f"  Created: {take}")
    
    print("Creating reports...")
    create_camera_report()
    create_sound_report()
    create_script_notes()
    create_director_notes()
    print("  Reports created")
    
    print("Creating script...")
    create_test_script()
    print("  Script created")
    
    (MEDIA_ROOTS / "camera_path.txt").write_text(str(camera_root))
    (MEDIA_ROOTS / "sound_path.txt").write_text(str(sound_root))
    
    result = {
        "fixture_type": FIXTURE_TYPE,
        "camera_root": str(camera_root),
        "sound_root": str(sound_root),
        "camera_takes": len(CAMERA_TAKES),
        "sound_takes": len(SOUND_TAKES),
        "camera_path_file": str(MEDIA_ROOTS / "camera_path.txt"),
        "sound_path_file": str(MEDIA_ROOTS / "sound_path.txt"),
    }
    
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    (LOGS_DIR / "fixture_preparation.json").write_text(json.dumps(result, indent=2))
    
    print(f"\nFixture prepared: {FIXTURE_TYPE}")
    print(f"Camera: {len(CAMERA_TAKES)} takes")
    print(f"Sound: {len(SOUND_TAKES)} takes")
    print(f"Reports: camera, sound, script, director")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())