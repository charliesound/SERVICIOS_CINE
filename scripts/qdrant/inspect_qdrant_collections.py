#!/usr/bin/env python3
"""
inspect_qdrant_collections.py — Dry-run audit of Qdrant collections.

Usage:
    export QDRANT_URL=http://127.0.0.1:6333   # (default)
    python scripts/qdrant/inspect_qdrant_collections.py

This script is READ-ONLY. It never creates, modifies, or deletes any
Qdrant collection or point. It only queries metadata and schema info.
"""

import os
import sys
import json
from urllib.request import urlopen, Request
from urllib.error import URLError

QDRANT_URL = os.getenv("QDRANT_URL", "http://127.0.0.1:6333").rstrip("/")


def _get(path: str) -> dict:
    url = f"{QDRANT_URL}{path}"
    with urlopen(url, timeout=10) as resp:
        return json.loads(resp.read())


def _post(path: str, body: dict) -> dict:
    url = f"{QDRANT_URL}{path}"
    data = json.dumps(body).encode()
    req = Request(url, data=data, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def main():
    print(f"Qdrant URL: {QDRANT_URL}")
    print("=" * 60)

    # 1. Server info
    info = _get("/")
    print(f"\nServer: {info.get('title')} v{info.get('version')}")
    print(f"Commit: {info.get('commit', 'N/A')}")

    # 2. List collections
    cols = _get("/collections")
    names = [c["name"] for c in cols.get("result", {}).get("collections", [])]
    print(f"\nCollections ({len(names)}):")
    for name in names:
        print(f"  - {name}")

    # 3. Per-collection detail
    for name in names:
        print(f"\n{'─' * 50}")
        print(f"Collection: {name}")
        print(f"{'─' * 50}")
        detail = _get(f"/collections/{name}")
        r = detail.get("result", {})

        # Status
        print(f"  Status:         {r.get('status', '?')}")
        print(f"  Optimizer:      {r.get('optimizer_status', '?')}")
        print(f"  Points:         {r.get('points_count', '?')}")
        print(f"  Segments:       {r.get('segments_count', '?')}")
        print(f"  Indexed vecs:   {r.get('indexed_vectors_count', '?')}")

        # Vector config
        config = r.get("config", {})
        params = config.get("params", {})
        vec_cfg = params.get("vectors", {})
        if isinstance(vec_cfg, dict):
            print(f"  Vector size:    {vec_cfg.get('size', '?')}")
            print(f"  Distance:       {vec_cfg.get('distance', '?')}")
        else:
            print(f"  Vectors:        {vec_cfg}")
        print(f"  Shards:         {params.get('shard_number', '?')}")
        print(f"  Replication:    {params.get('replication_factor', '?')}")
        print(f"  On-disk payload:{params.get('on_disk_payload', '?')}")

        # HNSW
        hnsw = config.get("hnsw_config", {})
        print(f"  HNSW m/ef:      {hnsw.get('m')}/{hnsw.get('ef_construct')}")
        print(f"  HNSW threshold: {hnsw.get('full_scan_threshold')}")

        # Optimizer
        opt = config.get("optimizer_config", {})
        print(f"  Index threshold:{opt.get('indexing_threshold')}")
        print(f"  Flush interval: {opt.get('flush_interval_sec')}s")

        # Payload schema
        ps = r.get("payload_schema", {})
        if ps:
            print(f"\n  Payload schema ({len(ps)} fields):")
            for fname, finfo in ps.items():
                dtype = finfo.get("data_type", "?")
                print(f"    {fname}: {dtype}")
        else:
            print(f"\n  Payload schema: none (free-form)")

        # Sample points (scroll 2)
        sample = _post(f"/collections/{name}/points/scroll", {
            "limit": 2,
            "with_payload": True,
            "with_vector": False,
        })
        points = sample.get("result", {}).get("points", [])
        if points:
            print(f"\n  Sample payload keys ({len(points)} points):")
            seen_keys = set()
            for p in points:
                seen_keys.update(p.get("payload", {}).keys())
            for k in sorted(seen_keys):
                val = str(points[0].get("payload", {}).get(k, ""))[:80]
                print(f"    {k}: {val}")

        # Cluster info
        try:
            cluster = _get(f"/collections/{name}/cluster")
            lshards = cluster.get("result", {}).get("local_shards", [])
            if lshards:
                print(f"\n  Shards: {len(lshards)} local, Active")
        except Exception:
            pass

    print(f"\n{'=' * 60}")
    print("Audit complete — no changes were made to Qdrant.")


if __name__ == "__main__":
    main()
