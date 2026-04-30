#!/usr/bin/env python3
"""
Check UI labels for media scan vs document ingestion terminology.
Fails if ambiguous terms like "Ingestar media" are found in user-facing UI.
"""

import re
import sys
from pathlib import Path

FRONTEND_SRC = Path("/opt/SERVICIOS_CINE/src_frontend/src")

AMBIGUOUS_TERMS = [
    r"Ingestar media",
    r"Ingesta de media",
    r"Subir material",
    r"Cargar clips",
    r"Media ingest",
    r"Ingest scans",
    r"ingested",
    r"Assets ingeridos",
    r"Material ingestido",
]

ALLOWED_CONTEXTS = [
    r"Ingesta de clips",
    r"Escaneo de media",
    r"Media scan",
    r"indexed",
    r"ingest scan",
    r"ingestScan",
    r"IngestScan",
    r"ingest_",
    r"/ingest/",
    r"useIngest",
    r"useIngestScan",
    r"listIngestScans",
    r"launchIngest",
    r"IngestEvent",
    r"document ingestion",
    r"report ingestion",
    r"ingesta documental",
]

def check_file(file_path: Path) -> list[str]:
    errors = []
    content = file_path.read_text(encoding="utf-8")
    lines = content.split("\n")
    
    for i, line in enumerate(lines, 1):
        if "//" in line or "/*" in line:
            continue
            
        for term in AMBIGUOUS_TERMS:
            if re.search(term, line, re.IGNORECASE):
                is_allowed = False
                for allowed in ALLOWED_CONTEXTS:
                    if re.search(allowed, line, re.IGNORECASE):
                        is_allowed = True
                        break
                if not is_allowed:
                    errors.append(f"{file_path.name}:{i}: Found ambiguous term: {term}")
    
    return errors

def main():
    print("Checking UI labels for media scan vs document ingestion...")
    
    tsx_files = list(FRONTEND_SRC.glob("pages/*.tsx"))
    tsx_files.extend(list(FRONTEND_SRC.glob("components/*.tsx")))
    
    all_errors = []
    for f in tsx_files:
        errs = check_file(f)
        all_errors.extend(errs)
    
    if all_errors:
        print("\nFAILED: Found ambiguous UI labels:")
        for e in all_errors:
            print(f"  {e}")
        return 1
    
    print("PASSED: No ambiguous media ingestion labels found in UI.")
    return 0

if __name__ == "__main__":
    sys.exit(main())