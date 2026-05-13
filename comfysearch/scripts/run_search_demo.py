#!/usr/bin/env python3
"""
run_search_demo.py — Demo interactiva de búsqueda semántica en terminal.

Uso:
  python scripts/run_search_demo.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "api"))

import yaml
from services.embedder import Embedder
from services.qdrant_store import QdrantStore


def main():
    settings_path = "config/settings.yaml"
    with open(settings_path, "r", encoding="utf-8") as f:
        settings = yaml.safe_load(f)

    embedder = Embedder(
        provider=settings["embedding"]["provider"],
        model=settings["embedding"]["model"],
    )
    store = QdrantStore(
        host=settings["qdrant"]["host"],
        port=settings["qdrant"]["port"],
        collection=settings["qdrant"]["collection"],
    )

    count = store.count()
    print(f"\n🔍 ComfySearch Demo ({count} workflows indexados})\n")

    while True:
        try:
            query = input("🎬 Busca: ").strip()
            if not query or query.lower() in ("exit", "quit", "salir"):
                break

            results = store.search(query, embedder, top_k=5)
            print(f"\nResultados ({len(results)}):\n")

            for i, r in enumerate(results, 1):
                print(f"  {i}. {r['name']}  (score: {r['score']})")
                print(f"     Backend: {r['backend']} | Tags: {', '.join(r['tags'][:6])}")
                print(f"     {r['summary'][:120]}")
                print(f"     Ruta: {r['path']}")
                if r.get('cinema_use_case'):
                    print(f"     🎬 {r['cinema_use_case'][:120]}")
                print()

        except KeyboardInterrupt:
            break

    print("Adiós.")


if __name__ == "__main__":
    main()
