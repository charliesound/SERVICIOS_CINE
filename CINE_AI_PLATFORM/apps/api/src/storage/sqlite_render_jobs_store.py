import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


class SQLiteRenderJobsStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS render_jobs (
                    job_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    request_payload TEXT NOT NULL,
                    parent_job_id TEXT,
                    comfyui_prompt_id TEXT,
                    result TEXT,
                    error TEXT,
                    duration_ms INTEGER
                )
                """
            )
            self._ensure_column(conn, "parent_job_id", "TEXT")
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_render_jobs_created_at
                ON render_jobs (created_at)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_render_jobs_parent_job_id
                ON render_jobs (parent_job_id)
                """
            )
            conn.commit()

    def _ensure_column(self, conn: sqlite3.Connection, column_name: str, column_type: str) -> None:
        rows = conn.execute("PRAGMA table_info(render_jobs)").fetchall()
        current_columns = {row[1] for row in rows}
        if column_name in current_columns:
            return

        conn.execute(f"ALTER TABLE render_jobs ADD COLUMN {column_name} {column_type}")

    def _row_to_job(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "job_id": row["job_id"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "status": row["status"],
            "request_payload": json.loads(row["request_payload"] or "{}"),
            "parent_job_id": row["parent_job_id"],
            "comfyui_prompt_id": row["comfyui_prompt_id"],
            "result": json.loads(row["result"]) if row["result"] else None,
            "error": json.loads(row["error"]) if row["error"] else None,
            "duration_ms": row["duration_ms"],
        }

    def create_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO render_jobs (
                    job_id,
                    created_at,
                    updated_at,
                    status,
                    request_payload,
                    parent_job_id,
                    comfyui_prompt_id,
                    result,
                    error,
                    duration_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job["job_id"],
                    job["created_at"],
                    job["updated_at"],
                    job["status"],
                    json.dumps(job.get("request_payload", {}), ensure_ascii=False),
                    job.get("parent_job_id"),
                    job.get("comfyui_prompt_id"),
                    json.dumps(job.get("result"), ensure_ascii=False) if job.get("result") is not None else None,
                    json.dumps(job.get("error"), ensure_ascii=False) if job.get("error") is not None else None,
                    job.get("duration_ms"),
                ),
            )
            conn.commit()
        return job

    def list_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM render_jobs
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (max(1, min(limit, 200)),),
            ).fetchall()
        return [self._row_to_job(row) for row in rows]

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM render_jobs
                WHERE job_id = ?
                """,
                (job_id,),
            ).fetchone()
        return self._row_to_job(row) if row else None

    def update_job(self, job_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        allowed_fields = {
            "updated_at",
            "status",
            "request_payload",
            "comfyui_prompt_id",
            "result",
            "error",
            "duration_ms",
        }

        set_clauses: List[str] = []
        values: List[Any] = []

        for key, value in updates.items():
            if key not in allowed_fields:
                continue

            set_clauses.append(f"{key} = ?")

            if key in {"request_payload", "result", "error"}:
                if value is None:
                    values.append(None)
                else:
                    values.append(json.dumps(value, ensure_ascii=False))
            else:
                values.append(value)

        if not set_clauses:
            return self.get_job(job_id)

        values.append(job_id)

        with self._connect() as conn:
            cursor = conn.execute(
                f"""
                UPDATE render_jobs
                SET {", ".join(set_clauses)}
                WHERE job_id = ?
                """,
                tuple(values),
            )
            conn.commit()

        if cursor.rowcount == 0:
            return None

        return self.get_job(job_id)
