from __future__ import annotations

import os
import json
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


def _count_pdf_images(pdf_path: Path) -> int:
    reader = PdfReader(str(pdf_path))
    total = 0
    for page in reader.pages:
        resources = page.get("/Resources")
        if not resources:
            continue
        xobject = resources.get("/XObject") if hasattr(resources, "get") else None
        if not xobject:
            continue
        for obj in xobject.get_object().values():
            resolved = obj.get_object()
            if resolved.get("/Subtype") == "/Image":
                total += 1
    return total


def _cleanup_storyboard_shots() -> None:
    connection = sqlite3.connect(str(DB_PATH))
    try:
        connection.execute(
            "DELETE FROM storyboard_shots WHERE project_id = ?",
            (PROJECT_ID,),
        )
        connection.commit()
    except sqlite3.OperationalError:
        connection.rollback()
    finally:
        connection.close()


class PresentationVisualValidationIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{DB_PATH}")
        os.environ.setdefault("QUEUE_AUTO_START_SCHEDULER", "0")
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            check=True,
            env={**os.environ, "DATABASE_URL": f"sqlite+aiosqlite:///{DB_PATH}"},
        )
        _cleanup_storyboard_shots()
        cls.seeded_assets = ensure_visual_smoke_assets(
            db_path=DB_PATH,
            project_id=PROJECT_ID,
            organization_id=ORGANIZATION_ID,
            storage_source_id=STORAGE_SOURCE_ID,
        )
        cls.asset_ids = [asset["asset_id"] for asset in cls.seeded_assets]
        cls.tenant_a_headers = _auth_headers(
            "4b153c715f76428b9e299698e5ab5561", "smoke_tenant_a@example.com"
        )
        cls.tenant_b_headers = _auth_headers(
            "54c10f417b714c558dc6da6015a96cc2", "smoke_tenant_b@example.com"
        )
        cls.admin_headers = _auth_headers(
            "dd66db71cbe643eb9494abd8616d3f64", "smoke_admin@example.com"
        )

    def test_visual_validation_flow(self) -> None:
        _cleanup_storyboard_shots()
        with TestClient(app) as client:
            existing_shots = client.get(
                f"/api/projects/{PROJECT_ID}/shots",
                headers=self.tenant_a_headers,
            )
            if existing_shots.status_code == 200:
                for shot in existing_shots.json().get("shots", []):
                    client.delete(
                        f"/api/projects/{PROJECT_ID}/shots/{shot['id']}",
                        headers=self.tenant_a_headers,
                    )

            dto = client.get(
                f"/api/projects/{PROJECT_ID}/presentation/filmstrip",
                headers=self.tenant_a_headers,
            )
            self.assertEqual(dto.status_code, 200)
            dto_json = dto.json()
            self.assertGreaterEqual(len(dto_json["sequences"]), 1)
            self.assertEqual(dto_json["sequences"][0]["sequence_id"], "SEQ_A")

            html = client.get(
                f"/api/projects/{PROJECT_ID}/presentation/filmstrip.html",
                headers=self.tenant_a_headers,
            )
            self.assertEqual(html.status_code, 200)
            for asset_id in self.asset_ids:
                self.assertIn(asset_id, html.text)

            for asset_id in self.asset_ids:
                preview = client.get(
                    f"/api/projects/{PROJECT_ID}/presentation/assets/{asset_id}/preview",
                    headers=self.tenant_a_headers,
                )
                self.assertEqual(preview.status_code, 200)
                self.assertEqual(preview.headers.get("content-type"), "image/png")
                self.assertEqual(preview.content[:8], b"\x89PNG\r\n\x1a\n")

            sync_pdf = client.get(
                f"/api/projects/{PROJECT_ID}/presentation/export/pdf",
                headers=self.tenant_a_headers,
            )
            self.assertEqual(sync_pdf.status_code, 200)
            self.assertEqual(sync_pdf.headers.get("content-type"), "application/pdf")
            self.assertEqual(sync_pdf.content[:8], b"%PDF-1.7")
            sync_pdf_path = Path("/tmp/test_presentation_visual_sync.pdf")
            sync_pdf_path.write_bytes(sync_pdf.content)
            self.assertGreaterEqual(_count_pdf_images(sync_pdf_path), 2)

            persisted = client.post(
                f"/api/projects/{PROJECT_ID}/presentation/export/pdf/persist",
                headers=self.tenant_a_headers,
            )
            self.assertEqual(persisted.status_code, 201)
            persisted_json = persisted.json()
            deliverable_id = persisted_json["id"]
            manifest = persisted_json["delivery_payload"].get("manifest_summary")
            self.assertIsInstance(manifest, dict)
            self.assertEqual(manifest["project_id"], PROJECT_ID)
            self.assertEqual(manifest["organization_id"], ORGANIZATION_ID)
            self.assertEqual(manifest["sequence_ids"], ["SEQ_A"])
            self.assertEqual(manifest["pdf_mime_type"], "application/pdf")
            self.assertIn(self.asset_ids[0], manifest["asset_ids"])
            self.assertIn(self.asset_ids[1], manifest["asset_ids"])

            manifest_file_path = Path(
                persisted_json["delivery_payload"]["manifest_file_path"]
            )
            self.assertTrue(manifest_file_path.exists())
            self.assertEqual(
                persisted_json["delivery_payload"]["manifest_mime_type"],
                "application/json",
            )
            manifest_disk = json.loads(manifest_file_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest_disk["project_id"], PROJECT_ID)
            self.assertEqual(manifest_disk["pdf_file_name"], manifest["pdf_file_name"])

            listed = client.get(
                f"/api/delivery/projects/{PROJECT_ID}/deliverables?format_type=PRESENTATION_PDF",
                headers=self.tenant_a_headers,
            )
            self.assertEqual(listed.status_code, 200)
            listed_json = listed.json()
            self.assertGreaterEqual(len(listed_json["deliverables"]), 1)
            matching = next(
                item for item in listed_json["deliverables"] if item["id"] == deliverable_id
            )
            self.assertEqual(
                matching["delivery_payload"]["manifest_summary"]["sequence_ids"], ["SEQ_A"]
            )

            persisted_download = client.get(
                f"/api/delivery/deliverables/{deliverable_id}/download",
                headers=self.tenant_a_headers,
            )
            self.assertEqual(persisted_download.status_code, 200)
            self.assertEqual(
                persisted_download.headers.get("content-type"), "application/pdf"
            )
            persisted_pdf_path = Path("/tmp/test_presentation_visual_persisted.pdf")
            persisted_pdf_path.write_bytes(persisted_download.content)
            self.assertGreaterEqual(_count_pdf_images(persisted_pdf_path), 2)

            denied_preview = client.get(
                f"/api/projects/{PROJECT_ID}/presentation/assets/{self.asset_ids[0]}/preview",
                headers=self.tenant_b_headers,
            )
            denied_export = client.get(
                f"/api/projects/{PROJECT_ID}/presentation/export/pdf",
                headers=self.tenant_b_headers,
            )
            denied_download = client.get(
                f"/api/delivery/deliverables/{deliverable_id}/download",
                headers=self.tenant_b_headers,
            )
            denied_list = client.get(
                f"/api/delivery/projects/{PROJECT_ID}/deliverables?format_type=PRESENTATION_PDF",
                headers=self.tenant_b_headers,
            )
            admin_list = client.get(
                f"/api/delivery/projects/{PROJECT_ID}/deliverables?format_type=PRESENTATION_PDF",
                headers=self.admin_headers,
            )
            self.assertEqual(denied_preview.status_code, 403)
            self.assertEqual(denied_export.status_code, 403)
            self.assertEqual(denied_download.status_code, 404)
            self.assertEqual(denied_list.status_code, 404)
            self.assertEqual(admin_list.status_code, 200)


if __name__ == "__main__":
    unittest.main()
