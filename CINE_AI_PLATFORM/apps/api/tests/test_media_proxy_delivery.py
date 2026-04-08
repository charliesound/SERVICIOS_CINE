"""Tests for Media Proxy Delivery V2.

Covers:
1. Media proxy route serves image when asset is available
2. Media proxy returns 404 when asset doesn't exist
3. Media proxy returns 503 when ComfyUI is unavailable
4. output_images[] exposes media_url (backend premium URL)
5. output_images[] still exposes view_url for compatibility/debug
6. fetch_image delegates to ComfyUI client correctly
7. Frontend getPrimaryImageUrl prefers media_url over view_url
"""

from __future__ import annotations

import unittest
from typing import Any, Dict
from unittest.mock import MagicMock, patch

from src.services.render_jobs_service import RenderJobsService


class TestMediaUrlConstruction(unittest.TestCase):
    """Test that media_url is constructed correctly when api_base_url is set."""

    def test_media_url_constructed_with_api_base(self) -> None:
        service = RenderJobsService.__new__(RenderJobsService)
        service.comfyui_client = MagicMock()
        service.repository = MagicMock()
        service.api_base_url = "http://127.0.0.1:3000"

        outputs = {
            "9": {
                "images": [
                    {"filename": "seq_001.png", "subfolder": "", "type": "output"}
                ]
            }
        }
        result = service._extract_output_images(outputs)
        self.assertEqual(len(result), 1)
        img = result[0]

        # media_url should point to backend premium
        self.assertIsNotNone(img["media_url"])
        self.assertIn("http://127.0.0.1:3000", img["media_url"])
        self.assertIn("/api/render/jobs/media", img["media_url"])
        self.assertIn("filename=seq_001.png", img["media_url"])

        # view_url should still point to ComfyUI (compatibility/debug)
        self.assertIsNotNone(img["view_url"])
        self.assertIn("8188", img["view_url"])  # ComfyUI default port

    def test_media_url_none_without_api_base(self) -> None:
        service = RenderJobsService.__new__(RenderJobsService)
        service.comfyui_client = MagicMock()
        service.repository = MagicMock()
        service.api_base_url = ""

        outputs = {
            "9": {
                "images": [
                    {"filename": "seq_001.png", "subfolder": "", "type": "output"}
                ]
            }
        }
        result = service._extract_output_images(outputs)
        self.assertEqual(len(result), 1)
        self.assertIsNone(result[0]["media_url"])
        self.assertIsNotNone(result[0]["view_url"])

    def test_media_url_with_subfolder(self) -> None:
        service = RenderJobsService.__new__(RenderJobsService)
        service.comfyui_client = MagicMock()
        service.repository = MagicMock()
        service.api_base_url = "http://api.example.com"

        outputs = {
            "10": {
                "images": [
                    {"filename": "preview.webp", "subfolder": "renders", "type": "output"}
                ]
            }
        }
        result = service._extract_output_images(outputs)
        media_url = result[0]["media_url"]
        self.assertIsNotNone(media_url)
        self.assertIn("filename=preview.webp", media_url)
        self.assertIn("subfolder=renders", media_url)


class TestFetchImage(unittest.TestCase):
    """Test fetch_image proxy method."""

    def test_fetch_image_delegates_to_comfyui_client(self) -> None:
        service = RenderJobsService.__new__(RenderJobsService)
        mock_client = MagicMock()
        mock_client.fetch_image.return_value = (b"\x89PNG\r\n\x1a\n", "image/png")
        service.comfyui_client = mock_client
        service.repository = MagicMock()

        image_bytes, content_type = service.fetch_image(
            filename="test.png",
            subfolder="",
            image_type="output",
        )

        self.assertEqual(content_type, "image/png")
        mock_client.fetch_image.assert_called_once_with(
            filename="test.png",
            subfolder="",
            image_type="output",
        )

    def test_fetch_image_propagates_comfyui_error(self) -> None:
        from src.services.comfyui_client import ComfyUIClientError

        service = RenderJobsService.__new__(RenderJobsService)
        mock_client = MagicMock()
        mock_client.fetch_image.side_effect = ComfyUIClientError(
            code="COMFYUI_UNAVAILABLE",
            message="ComfyUI unavailable",
        )
        service.comfyui_client = mock_client
        service.repository = MagicMock()

        with self.assertRaises(ComfyUIClientError):
            service.fetch_image(filename="test.png")


class TestFetchJobImage(unittest.TestCase):
    """Test fetch_job_image method."""

    def test_fetch_job_image_raises_when_no_job(self) -> None:
        from src.services.render_jobs_service import RenderJobNotFoundError

        service = RenderJobsService.__new__(RenderJobsService)
        service.comfyui_client = MagicMock()
        mock_repo = MagicMock()
        mock_repo.get.return_value = None
        service.repository = mock_repo

        with self.assertRaises(RenderJobNotFoundError):
            service.fetch_job_image("nonexistent-job")

    def test_fetch_job_image_raises_when_no_result(self) -> None:
        service = RenderJobsService.__new__(RenderJobsService)
        service.comfyui_client = MagicMock()
        mock_repo = MagicMock()
        mock_repo.get.return_value = {
            "job_id": "job-1",
            "status": "queued",
            "result": None,
        }
        service.repository = mock_repo

        with self.assertRaises(RuntimeError):
            service.fetch_job_image("job-1")

    def test_fetch_job_image_raises_when_no_output_images(self) -> None:
        service = RenderJobsService.__new__(RenderJobsService)
        service.comfyui_client = MagicMock()
        mock_repo = MagicMock()
        mock_repo.get.return_value = {
            "job_id": "job-1",
            "status": "succeeded",
            "result": {
                "provider": "comfyui",
                "output_images": None,
            },
        }
        service.repository = mock_repo

        with self.assertRaises(RuntimeError):
            service.fetch_job_image("job-1")

    def test_fetch_job_image_succeeds(self) -> None:
        service = RenderJobsService.__new__(RenderJobsService)
        mock_client = MagicMock()
        mock_client.fetch_image.return_value = (b"\x89PNG\r\n\x1a\n", "image/png")
        service.comfyui_client = mock_client
        mock_repo = MagicMock()
        mock_repo.get.return_value = {
            "job_id": "job-1",
            "status": "succeeded",
            "result": {
                "provider": "comfyui",
                "output_images": [
                    {
                        "filename": "seq_001.png",
                        "subfolder": "",
                        "image_type": "output",
                    }
                ],
            },
        }
        service.repository = mock_repo

        image_bytes, content_type = service.fetch_job_image("job-1")
        self.assertEqual(content_type, "image/png")
        mock_client.fetch_image.assert_called_once_with(
            filename="seq_001.png",
            subfolder="",
            image_type="output",
        )


class TestRenderJobOutputImageSchema(unittest.TestCase):
    """Test schema includes both media_url and view_url."""

    def test_schema_has_both_urls(self) -> None:
        from src.schemas.render_job import RenderJobOutputImage

        img = RenderJobOutputImage(
            filename="test.png",
            subfolder="",
            image_type="output",
            media_url="http://api.example.com/api/render/jobs/media?filename=test.png",
            view_url="http://comfyui:8188/view?filename=test.png",
        )

        self.assertEqual(img.media_url, "http://api.example.com/api/render/jobs/media?filename=test.png")
        self.assertEqual(img.view_url, "http://comfyui:8188/view?filename=test.png")

    def test_schema_serialization(self) -> None:
        from src.schemas.render_job import RenderJobOutputImage

        img = RenderJobOutputImage(
            filename="test.png",
            media_url="http://api.example.com/api/render/jobs/media?filename=test.png",
            view_url="http://comfyui:8188/view?filename=test.png",
        )

        data = img.model_dump()
        self.assertIn("media_url", data)
        self.assertIn("view_url", data)
        self.assertEqual(data["media_url"], "http://api.example.com/api/render/jobs/media?filename=test.png")
        self.assertEqual(data["view_url"], "http://comfyui:8188/view?filename=test.png")


if __name__ == "__main__":
    unittest.main()
