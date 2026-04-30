#!/usr/bin/env python3
"""
Execute media scan/index for production validation.
Scans camera and sound roots and indexes them as MediaAssets.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

VALIDATION_DIR = Path("/opt/SERVICIOS_CINE/docs/validation/production_real_20260428")
MEDIA_ROOTS = VALIDATION_DIR / "media_roots"
LOGS_DIR = VALIDATION_DIR / "logs"

CAMERA_EXTENSIONS = {".mp4", ".mov", ".mxf", ".avi", ".mkv", ".webm"}
SOUND_EXTENSIONS = {".wav", ".mp3", ".aac", ".flac", ".aif", ".aiff", ".m4a"}

def scan_directory(root_path: Path, extensions: set, asset_type: str):
    """Scan directory for files with given extensions."""
    assets = []
    if not root_path.exists():
        return assets
    
    for root, _dirs, files in os.walk(root_path):
        for file_name in files:
            file_ext = Path(file_name).suffix.lower()
            if file_ext in extensions:
                full_path = os.path.join(root, file_name)
                try:
                    stat = os.stat(full_path)
                    assets.append({
                        "file_name": file_name,
                        "full_path": full_path,
                        "relative_path": os.path.relpath(full_path, root_path),
                        "canonical_path": full_path,
                        "file_size": stat.st_size,
                        "asset_type": asset_type,
                        "discovered_at": datetime.now(timezone.utc).isoformat(),
                    })
                except OSError:
                    pass
    return assets

def main():
    print("Executing media scan/index...")
    
    camera_path_file = MEDIA_ROOTS / "camera_path.txt"
    sound_path_file = MEDIA_ROOTS / "sound_path.txt"
    
    if not camera_path_file.exists() or not sound_path_file.exists():
        print("ERROR: Path files not found")
        return 1
    
    camera_root = Path(camera_path_file.read_text().strip())
    sound_root = Path(sound_path_file.read_text().strip())
    
    print(f"Scanning camera: {camera_root}")
    camera_assets = scan_directory(camera_root, CAMERA_EXTENSIONS, "video")
    print(f"  Found: {len(camera_assets)} camera assets")
    
    print(f"Scanning sound: {sound_root}")
    sound_assets = scan_directory(sound_root, SOUND_EXTENSIONS, "audio")
    print(f"  Found: {len(sound_assets)} sound assets")
    
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "camera_root": str(camera_root),
        "sound_root": str(sound_root),
        "camera_assets_count": len(camera_assets),
        "sound_assets_count": len(sound_assets),
        "camera_assets": camera_assets,
        "sound_assets": sound_assets,
        "criteria": {
            "min_camera_assets": 6,
            "min_sound_assets": 6,
            "files_moved": 0,
            "files_copied": 0,
            "files_renamed": 0,
        },
    }
    
    (LOGS_DIR / "media_scan_result.json").write_text(json.dumps(result, indent=2))
    
    print(f"\nMedia scan result:")
    print(f"  Camera: {len(camera_assets)} assets")
    print(f"  Sound: {len(sound_assets)} assets")
    print(f"  Files moved: 0")
    print(f"  Files copied: 0")
    print(f"  Files renamed: 0")
    
    passed = len(camera_assets) >= 6 and len(sound_assets) >= 6
    print(f"\n{'PASS' if passed else 'FAIL'}: Media scan/index")
    
    return 0 if passed else 1

if __name__ == "__main__":
    sys.exit(main())