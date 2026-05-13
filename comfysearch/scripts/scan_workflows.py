#!/usr/bin/env python3
"""
scan_workflows.py — Escanea carpetas de workflows JSON y genera manifest.

Uso:
  python scripts/scan_workflows.py [--roots config/workflow_roots.yaml] [--output data/manifests/workflows.json]
"""

import json
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "api"))
from services.workflow_parser import parse_workflow

import yaml

def main():
    roots_path = sys.argv[1] if len(sys.argv) > 1 else "config/workflow_roots.yaml"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "data/manifests/workflows.json"

    with open(roots_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    roots = cfg.get("roots", [])
    ignore = cfg.get("ignore", [])
    exts = tuple(cfg.get("extensions", [".json"]))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    items = []
    seen = set()

    for root in roots:
        root_path = Path(root.strip())
        if not root_path.exists():
            print(f"[WARN] Root no encontrado: {root}")
            continue
        for fpath in root_path.rglob("*"):
            if not str(fpath).endswith(exts):
                continue
            if any(p in str(fpath) for p in ignore):
                continue
            if str(fpath) in seen:
                continue
            seen.add(str(fpath))

            parsed = parse_workflow(str(fpath))
            if parsed:
                items.append(parsed)
                print(f"  ✓ {parsed['name']}  ({len(parsed['nodes'])} nodos)")
            else:
                print(f"  ✗ {fpath.name} — no válido")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"\nTotal: {len(items)} workflows indexados → {output_path}")


if __name__ == "__main__":
    main()
