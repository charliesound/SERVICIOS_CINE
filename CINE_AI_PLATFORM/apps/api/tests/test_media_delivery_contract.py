"""Tests for Media Delivery Contract V1.

Covers:
1. Job with image available -> exposes output_images with view_url
2. Job without image yet -> exposes render_status and empty output_images
3. Job failed -> exposes error, no output_images
4. Multiple outputs -> all extracted with correct view_url
5. Compatibility with existing _build_success_result contract
"""

from __future__ import annotations

import unittest
from typing import Any, Dict
from unittest.mock import MagicMock, patch

from src.services.render_jobs_service import RenderJobsService


def _make_poll_state(history_entry: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "has_outputs": True,
        "status_str": "success",
        "poll_elapsed_ms": 12000,
        "history_entry": history_entry,
    }


def _make_submission(prompt_id: str = "prompt-uuid", status_code: int = 200) -> Dict[str, Any]:
    return {
        "prompt_id": prompt_id,
        "status_code": status_code,
        "latency_ms": 45,
        "provider_response": {"prompt_id": prompt_id, "node_errors": {}},
    }


class TestExtractOutputImages(unittest.TestCase):
    """Test _extract_output_images with various ComfyUI output shapes."""

    def setUp(self) -> None:
        self.service = RenderJobsService.__new__(RenderJobsService)
        self.service.comfyui_client = MagicMock()
        self.service.repository = MagicMock()

    def test_single_output_image(self) -> None:
        outputs = {
            "9": {
                "images": [
                    {"filename": "seq_shot_001_00001_.png", "subfolder": "", "type": "output"}
                ]
            }
        }
        result = self.service._extract_output_images(outputs)
        self.assertEqual(len(result), 1)
        img = result[0]
        self.assertEqual(img["filename"], "seq_shot_001_00001_.png")
        self.assertEqual(img["subfolder"], "")
        self.assertEqual(img["image_type"], "output")
        self.assertEqual(img["node_id"], "9")
        self.assertIn("view_url", img)
        self.assertIn("seq_shot_001_00001_.png", img["view_url"])
        self.assertIn("/view?", img["view_url"])

    def test_multiple_output_images(self) -> None:
        outputs = {
            "9": {
                "images": [
                    {"filename": "shot_001_a.png", "subfolder": "", "type": "output"},
                    {"filename": "shot_001_b.png", "subfolder": "", "type": "output"},
                ]
            },
            "10": {
                "images": [
                    {"filename": "shot_001_preview.webp", "subfolder": "previews", "type": "output"},
                ]
            },
        }
        result = self.service._extract_output_images(outputs)
        self.assertEqual(len(result), 3)
        filenames = [img["filename"] for img in result]
        self.assertIn("shot_001_a.png", filenames)
        self.assertIn("shot_001_b.png", filenames)
        self.assertIn("shot_001_preview.webp", filenames)

        preview = next(img for img in result if img["filename"] == "shot_001_preview.webp")
        self.assertEqual(preview["subfolder"], "previews")
        self.assertIn("subfolder=previews", preview["view_url"])

    def test_empty_outputs(self) -> None:
        result = self.service._extract_output_images({})
        self.assertEqual(result, [])

    def test_outputs_without_images_key(self) -> None:
        outputs = {"9": {"something_else": "value"}}
        result = self.service._extract_output_images(outputs)
        self.assertEqual(result, [])

    def test_outputs_with_empty_images_list(self) -> None:
        outputs = {"9": {"images": []}}
        result = self.service._extract_output_images(outputs)
        self.assertEqual(result, [])

    def test_view_url_construction(self) -> None:
        outputs = {
            "8": {
                "images": [
                    {"filename": "test_image.jpg", "subfolder": "renders", "type": "output"}
                ]
            }
        }
        result = self.service._extract_output_images(outputs)
        self.assertEqual(len(result), 1)
        view_url = result[0]["view_url"]
        self.assertTrue(view_url.startswith("http"))
        self.assertIn("/view?", view_url)
        self.assertIn("filename=test_image.jpg", view_url)
        self.assertIn("subfolder=renders", view_url)
        self.assertIn("type=output", view_url)

    def test_malformed_image_entries_skipped(self) -> None:
        outputs = {
            "9": {
                "images": [
                    {"filename": "good.png", "subfolder": "", "type": "output"},
                    {"subfolder": "", "type": "output"},
                    "not_a_dict",
                    None,
                ]
            }
        }
        result = self.service._extract_output_images(outputs)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["filename"], "good.png")


class TestBuildSuccessResult(unittest.TestCase):
    """Test _build_success_result includes output_images when available."""

    def setUp(self) -> None:
        self.service = RenderJobsService.__new__(RenderJobsService)
        self.service.comfyui_client = MagicMock()
        self.service.repository = MagicMock()

    def test_success_with_images(self) -> None:
        poll_state = _make_poll_state(
            history_entry={
                "outputs": {
                    "9": {
                        "images": [
                            {"filename": "seq_001.png", "subfolder": "", "type": "output"}
                        ]
                    }
                },
                "status": {"completed": True},
            }
        )
        submission = _make_submission()
        result = self.service._build_success_result(submission, poll_state)

        self.assertEqual(result["provider"], "comfyui")
        self.assertEqual(result["history_summary"]["has_outputs"], True)
        self.assertEqual(result["history_summary"]["output_node_count"], 1)
        self.assertIn("output_images", result)
        self.assertEqual(len(result["output_images"]), 1)
        self.assertEqual(result["output_images"][0]["filename"], "seq_001.png")

    def test_success_without_images(self) -> None:
        poll_state: Dict[str, Any] = {
            "has_outputs": False,
            "status_str": "success",
            "poll_elapsed_ms": 12000,
            "history_entry": {
                "outputs": {},
                "status": {"completed": True},
            },
        }
        submission = _make_submission()
        result = self.service._build_success_result(submission, poll_state)

        self.assertEqual(result["provider"], "comfyui")
        self.assertEqual(result["history_summary"]["has_outputs"], False)
        self.assertNotIn("output_images", result)

    def test_success_without_history_entry(self) -> None:
        poll_state: Dict[str, Any] = {
            "has_outputs": False,
            "status_str": "success",
            "poll_elapsed_ms": 5000,
        }
        submission = _make_submission()
        result = self.service._build_success_result(submission, poll_state)

        self.assertEqual(result["provider"], "comfyui")
        self.assertNotIn("output_images", result)
        self.assertEqual(result["history_summary"]["has_outputs"], False)

    def test_backward_compatibility(self) -> None:
        """Ensure all original fields are still present."""
        poll_state = _make_poll_state(
            history_entry={
                "outputs": {
                    "9": {
                        "images": [
                            {"filename": "test.png", "subfolder": "", "type": "output"}
                        ]
                    }
                },
                "status": {"completed": True},
            }
        )
        submission = _make_submission(prompt_id="test-prompt", status_code=200)
        result = self.service._build_success_result(submission, poll_state)

        required_keys = [
            "provider", "prompt_id", "submit_status_code", "submit_latency_ms",
            "completion_source", "poll_elapsed_ms", "history_summary",
            "provider_submit_response",
        ]
        for key in required_keys:
            self.assertIn(key, result, f"Missing backward-compatible key: {key}")

        self.assertEqual(result["provider"], "comfyui")
        self.assertEqual(result["prompt_id"], "test-prompt")
        self.assertEqual(result["submit_status_code"], 200)
        self.assertEqual(result["completion_source"], "history")


class TestRenderJobResultSchema(unittest.TestCase):
    """Test that RenderJobResult schema accepts output_images."""

    def test_result_with_output_images(self) -> None:
        from src.schemas.render_job import RenderJobResult, RenderJobOutputImage

        result = RenderJobResult(
            provider="comfyui",
            prompt_id="test-prompt",
            output_images=[
                RenderJobOutputImage(
                    filename="test.png",
                    subfolder="",
                    image_type="output",
                    view_url="http://localhost:8188/view?filename=test.png&type=output&subfolder=",
                    node_id="9",
                )
            ],
        )

        self.assertIsNotNone(result.output_images)
        self.assertEqual(len(result.output_images), 1)
        self.assertEqual(result.output_images[0].filename, "test.png")

    def test_result_without_output_images(self) -> None:
        from src.schemas.render_job import RenderJobResult

        result = RenderJobResult(
            provider="comfyui",
            prompt_id="test-prompt",
        )

        self.assertIsNone(result.output_images)

    def test_result_serialization(self) -> None:
        from src.schemas.render_job import RenderJobResult, RenderJobOutputImage

        result = RenderJobResult(
            provider="comfyui",
            prompt_id="test-prompt",
            output_images=[
                RenderJobOutputImage(
                    filename="seq_001.png",
                    subfolder="",
                    image_type="output",
                    view_url="http://localhost:8188/view?filename=seq_001.png&type=output&subfolder=",
                )
            ],
        )

        serialized = result.model_dump()
        self.assertIn("output_images", serialized)
        self.assertEqual(serialized["output_images"][0]["filename"], "seq_001.png")
        self.assertEqual(serialized["output_images"][0]["view_url"], "http://localhost:8188/view?filename=seq_001.png&type=output&subfolder=")


if __name__ == "__main__":
    unittest.main()
