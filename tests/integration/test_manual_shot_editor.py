from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, "/opt/SERVICIOS_CINE/src")

DB_PATH = Path(
    os.environ.get("PRESENTATION_VISUAL_DB_PATH", "/opt/SERVICIOS_CINE/ailinkcinema_s2.db")
).resolve()
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{DB_PATH}")
os.environ.setdefault("QUEUE_AUTO_START_SCHEDULER", "0")

from fastapi.testclient import TestClient
from pypdf import PdfReader

from app import app
from routes.auth_routes import create_access_token
from scripts.seed_presentation_visual_smoke import ensure_visual_smoke_assets


PROJECT_ID = "32fb858f66ef4569a7bc12db3b5ef2fd"
ORGANIZATION_ID = "db4d7a5dadc9457ebaa2993a30d48201"
STORAGE_SOURCE_ID = "d7fac025-fa34-487d-a83a-d81ce2aadcac"


def _auth_headers(user_id: str, email: str) -> dict[str, str]:
    token = create_access_token({"sub": user_id, "email": email})
    return {"Authorization": f"Bearer {token}"}


def _extract_pdf_text(pdf_bytes: bytes) -> str:
    pdf_path = Path("/tmp/test_manual_shot_editor.pdf")
    pdf_path.write_bytes(pdf_bytes)
    reader = PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _cleanup_storyboard_shots() -> None:
    connection = sqlite3.connect(str(DB_PATH))
    try:
        connection.execute(
            "DELETE FROM storyboard_shots WHERE project_id = ?",
            (PROJECT_ID,),
        )
        connection.commit()
    finally:
        connection.close()


class ManualShotEditorIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{DB_PATH}")
        os.environ.setdefault("QUEUE_AUTO_START_SCHEDULER", "0")
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            check=True,
            env={**os.environ, "DATABASE_URL": f"sqlite+aiosqlite:///{DB_PATH}"},
        )
        ensure_visual_smoke_assets(
            db_path=DB_PATH,
            project_id=PROJECT_ID,
            organization_id=ORGANIZATION_ID,
            storage_source_id=STORAGE_SOURCE_ID,
        )
        _cleanup_storyboard_shots()

        cls.tenant_a_headers = _auth_headers(
            "4b153c715f76428b9e299698e5ab5561", "smoke_tenant_a@example.com"
        )
        cls.tenant_b_headers = _auth_headers(
            "54c10f417b714c558dc6da6015a96cc2", "smoke_tenant_b@example.com"
        )
        cls.asset_ids = [
            "157c1828-990c-44e8-91c9-610fa3f12bf5",
            "05f375ba-53d8-40dc-a2b9-d82d40e08a67",
        ]

    def test_manual_shot_editor_full_loop(self) -> None:
        _cleanup_storyboard_shots()
        with TestClient(app) as client:
            first = client.post(
                f"/api/projects/{PROJECT_ID}/shots",
                headers=self.tenant_a_headers,
                json={
                    "sequence_id": "SEQ_EDIT",
                    "sequence_order": 1,
                    "narrative_text": "Editorial shot one",
                    "asset_id": self.asset_ids[0],
                    "shot_type": "wide",
                    "visual_mode": "storyboard",
                },
            )
            second = client.post(
                f"/api/projects/{PROJECT_ID}/shots",
                headers=self.tenant_a_headers,
                json={
                    "sequence_id": "SEQ_EDIT",
                    "sequence_order": 2,
                    "narrative_text": "Editorial shot two",
                    "asset_id": self.asset_ids[1],
                    "shot_type": "close_up",
                    "visual_mode": "storyboard",
                },
            )
            self.assertEqual(first.status_code, 201)
            self.assertEqual(second.status_code, 201)
            first_id = first.json()["id"]
            second_id = second.json()["id"]

            listed = client.get(
                f"/api/projects/{PROJECT_ID}/shots",
                headers=self.tenant_a_headers,
            )
            self.assertEqual(listed.status_code, 200)
            self.assertEqual(len(listed.json()["shots"]), 2)

            updated = client.put(
                f"/api/projects/{PROJECT_ID}/shots/{second_id}",
                headers=self.tenant_a_headers,
                json={"narrative_text": "Updated editorial note on second shot"},
            )
            self.assertEqual(updated.status_code, 200)

            reordered = client.put(
                f"/api/projects/{PROJECT_ID}/shots/bulk-reorder",
                headers=self.tenant_a_headers,
                json={
                    "shots": [
                        {"shot_id": second_id, "sequence_order": 1, "sequence_id": "SEQ_EDIT"},
                        {"shot_id": first_id, "sequence_order": 2, "sequence_id": "SEQ_EDIT"},
                    ]
                },
            )
            self.assertEqual(reordered.status_code, 200)

            dto = client.get(
                f"/api/projects/{PROJECT_ID}/presentation/filmstrip",
                headers=self.tenant_a_headers,
            )
            self.assertEqual(dto.status_code, 200)
            dto_json = dto.json()
            sequence = next(item for item in dto_json["sequences"] if item["sequence_id"] == "SEQ_EDIT")
            self.assertEqual(sequence["shots"][0]["asset_id"], self.asset_ids[1])
            self.assertEqual(
                sequence["shots"][0]["prompt_summary"],
                "Updated editorial note on second shot",
            )

            pdf = client.get(
                f"/api/projects/{PROJECT_ID}/presentation/export/pdf",
                headers=self.tenant_a_headers,
            )
            self.assertEqual(pdf.status_code, 200)
            pdf_text = _extract_pdf_text(pdf.content)
            self.assertIn("Updated editorial note on second shot", pdf_text)

            persisted = client.post(
                f"/api/projects/{PROJECT_ID}/presentation/export/pdf/persist",
                headers=self.tenant_a_headers,
            )
            self.assertEqual(persisted.status_code, 201)
            persisted_id = persisted.json()["id"]

            denied_read = client.get(
                f"/api/projects/{PROJECT_ID}/shots",
                headers=self.tenant_b_headers,
            )
            denied_write = client.post(
                f"/api/projects/{PROJECT_ID}/shots",
                headers=self.tenant_b_headers,
                json={"sequence_id": "X", "sequence_order": 1},
            )
            denied_download = client.get(
                f"/api/delivery/deliverables/{persisted_id}/download",
                headers=self.tenant_b_headers,
            )
            self.assertEqual(denied_read.status_code, 403)
            self.assertEqual(denied_write.status_code, 403)
            self.assertEqual(denied_download.status_code, 404)

            deleted = client.delete(
                f"/api/projects/{PROJECT_ID}/shots/{first_id}",
                headers=self.tenant_a_headers,
            )
            self.assertEqual(deleted.status_code, 204)
        _cleanup_storyboard_shots()


if __name__ == "__main__":
    unittest.main()
