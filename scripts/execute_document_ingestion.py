#!/usr/bin/env python3
"""
Execute document ingestion for production validation.
Ingests camera report, sound report, script notes, and director notes.
"""

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

VALIDATION_DIR = Path("/opt/SERVICIOS_CINE/docs/validation/production_real_20260428")
REPORTS_DIR = VALIDATION_DIR / "reports"
LOGS_DIR = VALIDATION_DIR / "logs"

def parse_camera_report(csv_path: Path):
    """Parse camera report CSV."""
    entries = []
    if not csv_path.exists():
        return entries
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append({
                "type": "camera_report",
                "reel": row.get("reel", ""),
                "scene": row.get("scene", ""),
                "shot": row.get("shot", ""),
                "take": row.get("take", ""),
                "filmroll": row.get("filmroll", ""),
                "camera": row.get("camera", ""),
                "lens": row.get("lens", ""),
                "rate": row.get("rate", ""),
                "fps": row.get("fps", ""),
                "circular": row.get("circular", ""),
                "notes": row.get("notes", ""),
            })
    return entries

def parse_sound_report(csv_path: Path):
    """Parse sound report CSV."""
    entries = []
    if not csv_path.exists():
        return entries
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append({
                "type": "sound_report",
                "reel": row.get("reel", ""),
                "scene": row.get("scene", ""),
                "shot": row.get("shot", ""),
                "take": row.get("take", ""),
                "roll": row.get("roll", ""),
                "circular": row.get("circular", ""),
                "notes": row.get("notes", ""),
                "sync": row.get("sync", ""),
            })
    return entries

def parse_script_notes(csv_path: Path):
    """Parse script notes CSV."""
    entries = []
    if not csv_path.exists():
        return entries
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append({
                "type": "script_note",
                "scene": row.get("scene", ""),
                "shot": row.get("shot", ""),
                "description": row.get("description", ""),
                "action": row.get("action", ""),
                "dialogue": row.get("dialogue", ""),
                "notes": row.get("notes", ""),
            })
    return entries

def parse_director_notes(md_path: Path):
    """Parse director notes markdown (simple extraction)."""
    if not md_path.exists():
        return []
    
    content = md_path.read_text(encoding="utf-8")
    lines = content.split("\n")
    
    entries = []
    current_scene = ""
    current_shot = ""
    
    for line in lines:
        line = line.strip()
        if line.startswith("## Scene"):
            parts = line.split()
            if len(parts) >= 2:
                current_scene = parts[1].replace("0", "")
        elif line.startswith("- SH"):
            parts = line.split()
            if len(parts) >= 1:
                current_shot = parts[0].replace("-", "").replace("SH", "")
            note = line.replace("- " + current_shot + ":", "").strip()
            entries.append({
                "type": "director_note",
                "scene": current_scene,
                "shot": current_shot,
                "note": note,
            })
        elif line.startswith("# General"):
            entries.append({
                "type": "director_note",
                "scene": "",
                "shot": "",
                "note": "General notes follow",
            })
    
    return entries

def main():
    print("Executing document ingestion...")
    
    camera_report = parse_camera_report(REPORTS_DIR / "camera_report.csv")
    sound_report = parse_sound_report(REPORTS_DIR / "sound_report.csv")
    script_notes = parse_script_notes(REPORTS_DIR / "script_notes.csv")
    director_notes = parse_director_notes(REPORTS_DIR / "director_notes.md")
    
    print(f"  Camera report: {len(camera_report)} entries")
    print(f"  Sound report: {len(sound_report)} entries")
    print(f"  Script notes: {len(script_notes)} entries")
    print(f"  Director notes: {len(director_notes)} entries")
    
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "camera_report": {
            "file": str(REPORTS_DIR / "camera_report.csv"),
            "entries_count": len(camera_report),
            "entries": camera_report,
        },
        "sound_report": {
            "file": str(REPORTS_DIR / "sound_report.csv"),
            "entries_count": len(sound_report),
            "entries": sound_report,
        },
        "script_notes": {
            "file": str(REPORTS_DIR / "script_notes.csv"),
            "entries_count": len(script_notes),
            "entries": script_notes,
        },
        "director_notes": {
            "file": str(REPORTS_DIR / "director_notes.md"),
            "entries_count": len(director_notes),
            "entries": director_notes,
        },
        "criteria": {
            "camera_report_imported": len(camera_report) > 0,
            "sound_report_imported": len(sound_report) > 0,
            "script_notes_imported": len(script_notes) > 0,
            "director_notes_imported": len(director_notes) > 0,
        },
    }
    
    (LOGS_DIR / "document_ingestion_result.json").write_text(json.dumps(result, indent=2))
    
    passed = (
        len(camera_report) > 0
        and len(sound_report) > 0
        and len(script_notes) > 0
        and len(director_notes) > 0
    )
    
    print(f"\n{'PASS' if passed else 'FAIL'}: Document ingestion")
    
    return 0 if passed else 1

if __name__ == "__main__":
    sys.exit(main())