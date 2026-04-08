from __future__ import annotations

import unittest

from src.schemas.render_context import RenderContextFlags
from src.services.render_request_context import apply_render_context_to_request_payload


class RenderRequestContextTest(unittest.TestCase):
    def test_case_without_new_flags(self) -> None:
        payload = {
            "prompt": {
                "1": {
                    "class_type": "KSampler",
                    "inputs": {},
                }
            }
        }

        result = apply_render_context_to_request_payload(payload, None)

        self.assertEqual(result, payload)
        self.assertNotIn("metadata", result)

    def test_case_with_character_id(self) -> None:
        payload = {"prompt": {}}
        context = RenderContextFlags(character_id=" char_001 ")

        result = apply_render_context_to_request_payload(payload, context)

        self.assertEqual(result["metadata"]["render_context"]["character_id"], "char_001")

    def test_case_with_scene_id(self) -> None:
        payload = {"prompt": {}}
        context = RenderContextFlags(scene_id=" scene_001 ")

        result = apply_render_context_to_request_payload(payload, context)

        self.assertEqual(result["metadata"]["render_context"]["scene_id"], "scene_001")

    def test_case_with_use_ipadapter(self) -> None:
        payload = {"prompt": {}}
        context = RenderContextFlags(character_id="char_010", use_ipadapter=True)

        result = apply_render_context_to_request_payload(payload, context)

        self.assertIs(result["metadata"]["render_context"]["use_ipadapter"], True)

    def test_case_fallback_if_data_is_missing(self) -> None:
        payload = {"prompt": {}}
        context = RenderContextFlags(use_ipadapter=True)

        result = apply_render_context_to_request_payload(payload, context)

        self.assertIs(result["metadata"]["render_context"]["use_ipadapter"], False)
        self.assertNotIn("character_id", result["metadata"]["render_context"])


if __name__ == "__main__":
    unittest.main()
