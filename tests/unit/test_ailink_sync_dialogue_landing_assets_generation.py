"""Tests for the AILink Sync Dialogue landing asset generator."""

import hashlib
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

EXPECTED_FILES = EXPECTED_PNGS + ("README.md", "assets_manifest.json")

EXPECTED_DIMENSIONS = {
    "hero-report-mockup.png": (1200, 800),
    "report-summary.png": (800, 500),
    "match-suggestions-table.png": (800, 600),
    "media-files-table.png": (800, 600),
    "privacy-local-first.png": (800, 400),
    "linkedin-beta-card.png": (1080, 1080),
}


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


def _run_script(output_dir, extra_args=None, *, force=True, quiet=True):
    """Run the generator script and return (returncode, stdout, stderr)."""
    cmd = [
        sys.executable,
        str(DEMO_SCRIPT),
        "--output-dir", str(output_dir),
    ]
    if force:
        cmd.append("--force")
    if quiet:
        cmd.append("--quiet")
    if extra_args:
        cmd.extend(extra_args)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout, r.stderr


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_manifest(output_dir: Path) -> dict:
    return json.loads((output_dir / "assets_manifest.json").read_text(encoding="utf-8"))


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


class TestGatingAudit:
    """Hardening checks before using the assets publicly."""

    def test_generated_pack_contains_only_expected_top_level_files(self, output_dir):
        rc, out, err = _run_script(output_dir)
        assert rc == 0, err
        generated = {p.name for p in output_dir.iterdir()}
        assert generated == set(EXPECTED_FILES)

    def test_demo_temp_directory_is_removed_after_success(self, output_dir):
        rc, out, err = _run_script(output_dir)
        assert rc == 0, err
        assert not (output_dir.parent / ".sync_demo_tmp").exists()

    def test_force_preserves_unrelated_files_and_subdirectories(self, output_dir):
        sentinel = output_dir / "do-not-delete.txt"
        nested = output_dir / "manual_notes"
        nested.mkdir()
        nested_sentinel = nested / "keep.txt"
        sentinel.write_text("manual note", encoding="utf-8")
        nested_sentinel.write_text("nested note", encoding="utf-8")
        (output_dir / "hero-report-mockup.png").write_bytes(b"stale")

        rc, out, err = _run_script(output_dir)
        assert rc == 0, err

        assert sentinel.read_text(encoding="utf-8") == "manual note"
        assert nested_sentinel.read_text(encoding="utf-8") == "nested note"
        assert (output_dir / "hero-report-mockup.png").read_bytes().startswith(
            b"\x89PNG\r\n\x1a\n"
        )

    def test_without_force_rejects_existing_dir_before_temp_generation(self, output_dir):
        sentinel = output_dir / "existing.txt"
        sentinel.write_text("preserve me", encoding="utf-8")

        rc, out, err = _run_script(output_dir, force=False)

        assert rc != 0
        assert "Use --force" in err
        assert sentinel.read_text(encoding="utf-8") == "preserve me"
        assert not (output_dir.parent / ".sync_demo_tmp").exists()

    def test_manifest_matches_generated_pngs_exactly(self, output_dir):
        rc, out, err = _run_script(output_dir)
        assert rc == 0, err

        manifest = _load_manifest(output_dir)
        manifest_names = {asset["file_name"] for asset in manifest["assets"]}
        disk_pngs = {p.name for p in output_dir.glob("*.png")}

        assert manifest_names == set(EXPECTED_PNGS)
        assert disk_pngs == set(EXPECTED_PNGS)

    def test_manifest_dimensions_match_all_pngs(self, output_dir):
        rc, out, err = _run_script(output_dir)
        assert rc == 0, err

        from PIL import Image

        manifest = _load_manifest(output_dir)
        for asset in manifest["assets"]:
            fname = asset["file_name"]
            with Image.open(output_dir / fname) as img:
                assert img.size == EXPECTED_DIMENSIONS[fname]
                assert asset["width"] == img.size[0]
                assert asset["height"] == img.size[1]

    def test_manifest_public_safety_contract(self, output_dir):
        rc, out, err = _run_script(output_dir)
        assert rc == 0, err

        manifest = _load_manifest(output_dir)
        assert manifest["version"] == 1
        for asset in manifest["assets"]:
            assert asset["public_safe"] is True
            assert "No real media" in asset["notes"]
            assert "no personal data" in asset["notes"]
            assert "no client names" in asset["notes"]
            assert "Controlled demo only" in asset["notes"]
            assert asset["purpose"].strip()
            assert asset["source"].strip()

    def test_readme_lists_every_manifest_asset_once(self, output_dir):
        rc, out, err = _run_script(output_dir)
        assert rc == 0, err

        readme = (output_dir / "README.md").read_text(encoding="utf-8")
        manifest = _load_manifest(output_dir)
        for asset in manifest["assets"]:
            assert readme.count(f"`{asset['file_name']}`") == 1

    def test_generated_text_outputs_have_no_forbidden_public_strings(self, output_dir):
        rc, out, err = _run_script(output_dir)
        assert rc == 0, err

        combined = "\n".join(
            [
                (output_dir / "README.md").read_text(encoding="utf-8"),
                (output_dir / "assets_manifest.json").read_text(encoding="utf-8"),
            ]
        )
        forbidden = [
            "/mnt/",
            "\\wsl.localhost",
            "C:",
            "DATABASE_URL",
            "TEST_DATABASE_URL",
            "FastAPI",
            "APIRouter",
            "CreditLedger",
            "AIJob",
            "ComfyUI",
            "Docker",
            "Alembic",
            "Stripe",
            "http://",
            "https://",
            "sqli" + "te",
            "cid_test",
        ]
        for pattern in forbidden:
            assert pattern not in combined, f"Forbidden public string found: {pattern}"

    def test_assets_regenerate_reproducibly(self, output_dir):
        first = output_dir / "first"
        second = output_dir / "second"

        rc1, out1, err1 = _run_script(first)
        rc2, out2, err2 = _run_script(second)

        assert rc1 == 0, err1
        assert rc2 == 0, err2

        first_hashes = {name: _hash_file(first / name) for name in EXPECTED_FILES}
        second_hashes = {name: _hash_file(second / name) for name in EXPECTED_FILES}
        assert first_hashes == second_hashes


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
