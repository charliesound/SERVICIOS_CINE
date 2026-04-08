import sqlite3
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class SQLiteShotsStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS shots (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    prompt TEXT,
                    raw_prompt TEXT,
                    negative_prompt TEXT,
                    camera_preset TEXT,
                    nominal_ratio TEXT,
                    scene_id TEXT,
                    sequence_id TEXT,
                    status TEXT,
                    tags TEXT NOT NULL,
                    "references" TEXT NOT NULL,
                    layers TEXT NOT NULL,
                    render_inputs TEXT NOT NULL,
                    structured_prompt TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def _row_to_shot(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "title": row["title"],
            "prompt": row["prompt"],
            "raw_prompt": row["raw_prompt"],
            "negative_prompt": row["negative_prompt"],
            "camera_preset": row["camera_preset"],
            "nominal_ratio": row["nominal_ratio"],
            "scene_id": row["scene_id"],
            "sequence_id": row["sequence_id"],
            "status": row["status"],
            "tags": json.loads(row["tags"] or "[]"),
            "references": json.loads(row["references"] or "[]"),
            "layers": json.loads(row["layers"] or "[]"),
            "render_inputs": json.loads(row["render_inputs"] or "{}"),
            "structured_prompt": json.loads(row["structured_prompt"] or "{}"),
            "metadata": json.loads(row["metadata"] or "{}"),
            "updated_at": row["updated_at"],
            "created_at": row["created_at"],
        }

    def list_shots(self) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM shots
                ORDER BY created_at ASC
                """
            ).fetchall()
        return [self._row_to_shot(row) for row in rows]

    def get_shot(self, shot_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM shots WHERE id = ?
                """,
                (shot_id,),
            ).fetchone()
        return self._row_to_shot(row) if row else None

    def create_shot(self, shot: Dict[str, Any]) -> Dict[str, Any]:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO shots (
                    id, title, prompt, raw_prompt, negative_prompt, camera_preset,
                    nominal_ratio, scene_id, sequence_id, status, tags, "references",
                    layers, render_inputs, structured_prompt, metadata, updated_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    shot["id"],
                    shot.get("title"),
                    shot.get("prompt"),
                    shot.get("raw_prompt"),
                    shot.get("negative_prompt"),
                    shot.get("camera_preset"),
                    shot.get("nominal_ratio"),
                    shot.get("scene_id"),
                    shot.get("sequence_id"),
                    shot.get("status"),
                    json.dumps(shot.get("tags", []), ensure_ascii=False),
                    json.dumps(shot.get("references", []), ensure_ascii=False),
                    json.dumps(shot.get("layers", []), ensure_ascii=False),
                    json.dumps(shot.get("render_inputs", {}), ensure_ascii=False),
                    json.dumps(shot.get("structured_prompt", {}), ensure_ascii=False),
                    json.dumps(shot.get("metadata", {}), ensure_ascii=False),
                    shot["updated_at"],
                    shot["created_at"],
                ),
            )
            conn.commit()
        return shot

    def replace_shot(self, shot_id: str, shot: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                UPDATE shots
                SET
                    title = ?,
                    prompt = ?,
                    raw_prompt = ?,
                    negative_prompt = ?,
                    camera_preset = ?,
                    nominal_ratio = ?,
                    scene_id = ?,
                    sequence_id = ?,
                    status = ?,
                    tags = ?,
                    "references" = ?,
                    layers = ?,
                    render_inputs = ?,
                    structured_prompt = ?,
                    metadata = ?,
                    updated_at = ?,
                    created_at = ?
                WHERE id = ?
                """,
                (
                    shot.get("title"),
                    shot.get("prompt"),
                    shot.get("raw_prompt"),
                    shot.get("negative_prompt"),
                    shot.get("camera_preset"),
                    shot.get("nominal_ratio"),
                    shot.get("scene_id"),
                    shot.get("sequence_id"),
                    shot.get("status"),
                    json.dumps(shot.get("tags", []), ensure_ascii=False),
                    json.dumps(shot.get("references", []), ensure_ascii=False),
                    json.dumps(shot.get("layers", []), ensure_ascii=False),
                    json.dumps(shot.get("render_inputs", {}), ensure_ascii=False),
                    json.dumps(shot.get("structured_prompt", {}), ensure_ascii=False),
                    json.dumps(shot.get("metadata", {}), ensure_ascii=False),
                    shot["updated_at"],
                    shot["created_at"],
                    shot_id,
                ),
            )
            conn.commit()

        if cursor.rowcount == 0:
            return None
        return shot

    def delete_shot(self, shot_id: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                DELETE FROM shots WHERE id = ?
                """,
                (shot_id,),
            )
            conn.commit()
        return cursor.rowcount > 0