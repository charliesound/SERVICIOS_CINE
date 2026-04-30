import asyncio
import os
import sys
import json
import uuid
from datetime import datetime

os.environ["DATABASE_URL"] = (
    "sqlite+aiosqlite:///C:/Users/Charliesound/AppData/Local/frozen_presets_test.db"
)
os.environ["QUEUE_PERSISTENCE_MODE"] = "memory"

for m in list(sys.modules.keys()):
    if any(x in m for x in ["services", "models", "database"]):
        del sys.modules[m]

from database import init_db, AsyncSessionLocal
from models.storage import MediaAsset
from sqlalchemy import select, func


async def group_assets_by_sequence(project_id: str) -> dict:
    """Group assets by sequence_id from metadata_json"""

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(MediaAsset)
            .where(MediaAsset.project_id == project_id)
            .where(MediaAsset.asset_type == "image")
            .order_by(
                func.json_extract(MediaAsset.metadata_json, "$.sequence_id").asc(),
                func.json_extract(MediaAsset.metadata_json, "$.shot_order").asc(),
            )
        )
        assets = result.scalars().all()

        groups = {}
        for asset in assets:
            meta = json.loads(asset.metadata_json or "{}")
            seq_id = meta.get("sequence_id", "unknown")

            if seq_id not in groups:
                groups[seq_id] = {
                    "sequence_id": seq_id,
                    "shots": [],
                    "visual_modes": set(),
                }

            groups[seq_id]["shots"].append(
                {
                    "shot_order": meta.get("shot_order"),
                    "shot_type": meta.get("shot_type", "unknown"),
                    "visual_mode": meta.get("visual_mode", "unknown"),
                    "filename": asset.file_name,
                    "content_ref": asset.content_ref,
                    "asset_id": asset.id,
                }
            )
            groups[seq_id]["visual_modes"].add(meta.get("visual_mode", "unknown"))

        # Convert sets to lists for JSON
        for seq in groups.values():
            seq["visual_modes"] = list(seq["visual_modes"])

        return groups


async def run():
    await init_db()

    print("=" * 60)
    print("SEQUENCE GROUPING TEST")
    print("=" * 60)

    # Get some test project with assets
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(MediaAsset.asset_type, MediaAsset.project_id)
            .group_by(MediaAsset.project_id)
            .limit(5)
        )
        projects = result.all()

        print(f"\nFound projects with assets:")
        for p in projects:
            print(f"  {p[1]}")

    if projects:
        test_project = projects[0][1]
        print(f"\n=== Testing grouping for: {test_project} ===")

        groups = await group_assets_by_sequence(test_project)

        print(
            f"\nGrouped {sum(len(g['shots']) for g in groups.values())} assets into {len(groups)} sequences:"
        )

        for seq_id, data in sorted(groups.items()):
            print(f"\n  Sequence {seq_id}:")
            print(f"    Visual modes: {data['visual_modes']}")
            for shot in data["shots"]:
                print(
                    f"    - Shot {shot['shot_order']} ({shot['shot_type']}) [{shot['visual_mode']}]"
                )
                print(f"      {shot['filename']}")

    print("\n" + "=" * 60)
    print("STRUCTURE READY FOR REVIEW UI")
    print("=" * 60)
    print("""
Frontend can use:
  GET /api/ingest/assets?project_id=xxx
  
Response includes metadata_json with:
  - sequence_id
  - shot_order
  - shot_type
  - visual_mode

Backend grouping available via:
  group_assets_by_sequence(project_id) -> {
    "A": { sequence_id: "A", shots: [...], visual_modes: ["realistic"] },
    "B": { sequence_id: "B", shots: [...], visual_modes: ["flux"] },
  }
""")


if __name__ == "__main__":
    asyncio.run(run())
