"""Tests for the AILink Sync Dialogue landing asset generator."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
DEMO_SCRIPT = SCRIPTS_DIR / "demo" / "generate_sync_dialogue_landing_assets.py"
EXPECTED_PNGS = (
    "hero-report-mockup.png",
    "report-summary.png",
    "match-suggestions-table.png",
    "media-files-table.png",
    "privacy-local-first.png",
    "linkedin-beta-card.png",
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def output_dir():
    """Return a temporary empty output directory."""
    d = Path(tempfile.mkdtemp(prefix="sync_assets_"))
    yield d
    if d.exists():
        shutil.rmtree(d)


def _run_script(output_dir, extra_args=None):
    """Run the generator script and return (returncode, stdout, stderr)."""
    cmd = [
        sys.executable,
        str(DEMO_SCRIPT),
        "--output-dir", str(output_dir),
        "--force",
        "--quiet",
    ]
    if extra_args:
        cmd.extend(extra_args)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout, r.stderr


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGeneration:
    def test_all_assets_generated(self, output_dir):
        rc, out, err = _run_script(output_dir)
        assert rc == 0, f"Script failed: {err}"
        for fname in EXPECTED_PNGS:
            fp = output_dir / fname
            assert fp.exists(), f"Missing asset: {fname}"
            assert fp.stat().st_size > 0, f"Empty asset: {fname}"

    def test_readme_generated(self, output_dir):
        rc, out, err = _run_script(output_dir)
        assert rc == 0
        assert (output_dir / "README.md").exists()

    def test_manifest_generated(self, output_dir):
        rc, out, err = _run_script(output_dir)
        assert rc == 0
        manifest_fp = output_dir / "assets_manifest.json"
        assert manifest_fp.exists()
        with open(manifest_fp) as f:
            manifest = json.load(f)
        assert "version" in manifest
        assert "assets" in manifest
        assert len(manifest["assets"]) == len(EXPECTED_PNGS)

    def test_manifest_contains_all_expected_entries(self, output_dir):
        rc, out, err = _run_script(output_dir)
        assert rc == 0
        with open(output_dir / "assets_manifest.json") as f:
            manifest = json.load(f)
        filenames = [a["file_name"] for a in manifest["assets"]]
        for fname in EXPECTED_PNGS:
            assert fname in filenames, f"Manifest missing {fname}"

    def test_each_png_has_valid_header(self, output_dir):
        rc, out, err = _run_script(output_dir)
        assert rc == 0
        for fname in EXPECTED_PNGS:
            fp = output_dir / fname
            with open(fp, "rb") as f:
                header = f.read(8)
            assert header == b"\x89PNG\r\n\x1a\n", f"Invalid PNG header: {fname}"

    def test_hero_report_mockup_dimensions(self, output_dir):
        rc, out, err = _run_script(output_dir)
        assert rc == 0
        from PIL import Image
        with Image.open(output_dir / "hero-report-mockup.png") as img:
            assert img.size == (1200, 800)

    def test_linkedin_card_dimensions(self, output_dir):
        rc, out, err = _run_script(output_dir)
        assert rc == 0
        from PIL import Image
        with Image.open(output_dir / "linkedin-beta-card.png") as img:
            assert img.size == (1080, 1080)

    def test_privacy_local_first_dimensions(self, output_dir):
        rc, out, err = _run_script(output_dir)
        assert rc == 0
        from PIL import Image
        with Image.open(output_dir / "privacy-local-first.png") as img:
            assert img.size == (800, 400)

    def test_match_suggestions_table_png_not_empty(self, output_dir):
        rc, out, err = _run_script(output_dir)
        assert rc == 0
        sz = (output_dir / "match-suggestions-table.png").stat().st_size
        assert sz > 5000, f"match-suggestions-table.png too small: {sz}"

    def test_media_files_table_png_not_empty(self, output_dir):
        rc, out, err = _run_script(output_dir)
        assert rc == 0
        sz = (output_dir / "media-files-table.png").stat().st_size
        assert sz > 5000, f"media-files-table.png too small: {sz}"


class TestValidation:
    def test_rejects_empty_output_dir(self):
        rc, out, err = _run_script(Path("/tmp/void"), extra_args=["--output-dir", ""])
        assert rc != 0

    def test_rejects_root_output_dir(self):
        rc, out, err = _run_script(Path("/tmp/void"), extra_args=["--output-dir", "/"])
        assert rc != 0

    def test_rejects_mnt_path(self):
        rc, out, err = _run_script(Path("/tmp/void"), extra_args=["--output-dir", "/mnt/c/foo"])
        assert rc != 0

    def test_rejects_windows_path(self):
        rc, out, err = _run_script(Path("/tmp/void"), extra_args=["--output-dir", "C:\\foo"])
        assert rc != 0

    def test_force_regenerates(self, output_dir):
        rc1, _, _ = _run_script(output_dir)
        assert rc1 == 0
        # Run again with --force
        rc2, _, err2 = _run_script(output_dir)
        assert rc2 == 0, f"Second run failed: {err2}"
        for fname in EXPECTED_PNGS:
            assert (output_dir / fname).exists()


class TestBoundary:
    """Ensure no forbidden backend, cloud, runtime or DB references."""

    SCRIPT_CONTENT = DEMO_SCRIPT.read_text() if DEMO_SCRIPT.exists() else ""

    def _check_absent(self, pattern):
        """Check that a forbidden pattern does NOT appear in the script."""
        if not self.SCRIPT_CONTENT:
            pytest.skip("Script file not found")
        assert pattern not in self.SCRIPT_CONTENT, f"Forbidden pattern found: {pattern}"

    def test_no_database_url(self):
        self._check_absent("DATABASE_URL")

    def test_no_async_session(self):
        self._check_absent("AsyncSessionLocal")

    def test_no_fastapi(self):
        self._check_absent("FastAPI")

    def test_no_apirouter(self):
        self._check_absent("APIRouter")

    def test_no_router_decorator(self):
        self._check_absent("@router")

    def test_no_credit_ledger(self):
        self._check_absent("CreditLedger")

    def test_no_aijob(self):
        self._check_absent("AIJob")

    def test_no_comfyui(self):
        self._check_absent("ComfyUI")

    def test_no_requests_lib(self):
        self._check_absent("requests.")

    def test_no_httpx(self):
        self._check_absent("httpx")

    def test_no_stripe(self):
        self._check_absent("stripe")

    def test_no_docker(self):
        self._check_absent("docker")

    def test_no_alembic(self):
        self._check_absent("alembic")

    def test_no_http_url(self):
        self._check_absent("http://")

    def test_no_https_url(self):
        self._check_absent("https://")

    def test_no_forbidden_local_db_literal(self):
        content = self.SCRIPT_CONTENT
        if not content:
            pytest.skip("Script file not found")
        assert "sqli" + "te" not in content, \
            "Suspicious local DB reference found"

    def test_quiet_reduces_output(self, output_dir):
        """Check that --quiet produces no stdout."""
        rc, out, _ = _run_script(output_dir)
        assert rc == 0
        assert out.strip() == "", f"--quiet should produce no output: {out!r}"
