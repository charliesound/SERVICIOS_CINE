from pathlib import Path
import json

from src.storage.sqlite_shots_store import SQLiteShotsStore

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SHOTS_FILE = DATA_DIR / "shots.json"
SHOTS_DB_FILE = DATA_DIR / "shots.db"

store = SQLiteShotsStore(SHOTS_DB_FILE)

if not SHOTS_FILE.exists():
    print("No existe shots.json")
    raise SystemExit(0)

shots = json.loads(SHOTS_FILE.read_text(encoding="utf-8"))
if not isinstance(shots, list):
    raise RuntimeError("shots.json debe contener un array")

existing_ids = {shot["id"] for shot in store.list_shots()}

migrated = 0
for shot in shots:
    shot_id = shot.get("id")
    if not shot_id or shot_id in existing_ids:
        continue
    store.create_shot(shot)
    migrated += 1

print(f"Migrados: {migrated}")