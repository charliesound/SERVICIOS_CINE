#!/usr/bin/env python3
"""
ingest_to_qdrant.py — Indexa workflows escaneados en Qdrant.

Uso:
  python scripts/ingest_to_qdrant.py [--manifest data/manifests/workflows.json]
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "api"))

import yaml
from services.embedder import Embedder
from services.qdrant_store import QdrantStore


def main():
    manifest_path = sys.argv[1] if len(sys.argv) > 1 else "data/manifests/workflows.json"
    settings_path = sys.argv[2] if len(sys.argv) > 2 else "config/settings.yaml"

    with open(settings_path, "r", encoding="utf-8") as f:
        settings = yaml.safe_load(f)

    with open(manifest_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    embedder = Embedder(
        provider=settings["embedding"]["provider"],
        model=settings["embedding"]["model"],
    )
    store = QdrantStore(
        host=settings["qdrant"]["host"],
        port=settings["qdrant"]["port"],
        collection=settings["qdrant"]["collection"],
    )

    count = store.ingest(items, embedder)
    print(f"Indexados {count} workflows en Qdrant ({settings['qdrant']['collection']})")


if __name__ == "__main__":
    main()
