from pathlib import Path
from typing import Any, Dict
import sqlite3

from src.services.comfyui_client import ComfyUIClient


class HealthService:
    def __init__(
        self,
        store_backend: str,
        json_file: Path,
        sqlite_file: Path,
        comfyui_client: ComfyUIClient | None = None,
    ):
        self.store_backend = store_backend
        self.json_file = json_file
        self.sqlite_file = sqlite_file
        self.comfyui_client = comfyui_client

    def get_details(self) -> Dict[str, Any]:
        checks = {
            "json": self._check_json(),
            "sqlite": self._check_sqlite(),
        }

        active_check = checks["sqlite"] if self.store_backend == "sqlite" else checks["json"]

        return {
            "ok": bool(active_check["ok"]),
            "health": {
                "active_backend": self.store_backend,
                "checks": checks,
                "integrations": {
                    "comfyui": self._check_comfyui_optional(),
                },
            },
        }

    def _check_comfyui_optional(self) -> Dict[str, Any]:
        if self.comfyui_client is None:
            return {
                "optional": True,
                "configured": False,
                "reachable": False,
                "message": "ComfyUI client is not configured",
            }

        status = self.comfyui_client.check_availability()
        status["optional"] = True
        return status

    def _check_json(self) -> Dict[str, Any]:
        try:
            exists = self.json_file.exists()
            is_file = self.json_file.is_file()
            readable = False
            writable = False
            size = 0

            if exists and is_file:
                content = self.json_file.read_text(encoding="utf-8")
                readable = True
                size = len(content.encode("utf-8"))

                test_file = self.json_file.parent / f"{self.json_file.name}.write_test.tmp"
                test_file.write_text("ok", encoding="utf-8")
                test_file.unlink(missing_ok=True)
                writable = True

            return {
                "ok": exists and is_file and readable and writable,
                "path": str(self.json_file),
                "exists": exists,
                "is_file": is_file,
                "readable": readable,
                "writable": writable,
                "size_bytes": size,
            }
        except Exception as error:
            return {
                "ok": False,
                "path": str(self.json_file),
                "error": str(error),
            }

    def _check_sqlite(self) -> Dict[str, Any]:
        try:
            exists = self.sqlite_file.exists()
            is_file = self.sqlite_file.is_file() if exists else False

            with sqlite3.connect(self.sqlite_file) as conn:
                conn.execute("SELECT 1")
                cursor = conn.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE type='table' AND name='shots'
                    """
                )
                has_shots_table = cursor.fetchone() is not None

            size = self.sqlite_file.stat().st_size if self.sqlite_file.exists() else 0

            return {
                "ok": self.sqlite_file.exists() and has_shots_table,
                "path": str(self.sqlite_file),
                "exists": self.sqlite_file.exists(),
                "is_file": self.sqlite_file.is_file(),
                "readable": True,
                "writable": True,
                "has_shots_table": has_shots_table,
                "size_bytes": size,
            }
        except Exception as error:
            return {
                "ok": False,
                "path": str(self.sqlite_file),
                "error": str(error),
            }
    
