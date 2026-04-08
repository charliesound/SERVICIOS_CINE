from __future__ import annotations

import unittest
from copy import deepcopy
from typing import Any, Dict, List, Optional

from src.services.shots_service import ShotsService


class InMemoryShotsStore:
    def __init__(self) -> None:
        self._shots: List[Dict[str, Any]] = []

    def list_shots(self) -> List[Dict[str, Any]]:
        return [deepcopy(shot) for shot in self._shots]

    def get_shot(self, shot_id: str) -> Optional[Dict[str, Any]]:
        for shot in self._shots:
            if str(shot.get("id")) == shot_id:
                return deepcopy(shot)
        return None

    def create_shot(self, shot: Dict[str, Any]) -> Dict[str, Any]:
        self._shots.append(deepcopy(shot))
        return deepcopy(shot)

    def replace_shot(self, shot_id: str, shot: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for index, current in enumerate(self._shots):
            if str(current.get("id")) == shot_id:
                self._shots[index] = deepcopy(shot)
                return deepcopy(shot)
        return None

    def delete_shot(self, shot_id: str) -> bool:
        before = len(self._shots)
        self._shots = [shot for shot in self._shots if str(shot.get("id")) != shot_id]
        return len(self._shots) < before


class ShotsServiceRenderFlagsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryShotsStore()
        self.service = ShotsService(self.store)

    def test_case_without_new_flags(self) -> None:
        shot = self.service.create_shot({"title": "Plano base", "prompt": "Prompt base"})

        self.assertEqual(shot["render_inputs"], {})

    def test_case_with_character_id(self) -> None:
        shot = self.service.create_shot(
            {
                "title": "Plano con personaje",
                "prompt": "Prompt personaje",
                "render_inputs": {"character_id": "char_001"},
            }
        )

        self.assertEqual(shot["render_inputs"].get("character_id"), "char_001")

    def test_case_with_scene_id(self) -> None:
        shot = self.service.create_shot(
            {
                "title": "Plano con escena",
                "prompt": "Prompt escena",
                "render_inputs": {"scene_id": "scene_002"},
            }
        )

        self.assertEqual(shot["render_inputs"].get("scene_id"), "scene_002")

    def test_case_with_use_ipadapter(self) -> None:
        shot = self.service.create_shot(
            {
                "title": "Plano con ipadapter",
                "prompt": "Prompt ipadapter",
                "render_inputs": {"use_ipadapter": True},
            }
        )

        self.assertIs(shot["render_inputs"].get("use_ipadapter"), True)

    def test_case_fallback_when_data_is_missing(self) -> None:
        created = self.service.create_shot(
            {
                "title": "Plano inicial",
                "prompt": "Prompt inicial",
                "render_inputs": {
                    "character_id": "char_010",
                    "scene_id": "scene_010",
                    "use_ipadapter": True,
                },
            }
        )

        patched = self.service.patch_shot(created["id"], {"prompt": "Prompt actualizado"})

        self.assertIsNotNone(patched)
        assert patched is not None
        self.assertEqual(
            patched["render_inputs"],
            {
                "character_id": "char_010",
                "scene_id": "scene_010",
                "use_ipadapter": True,
            },
        )


if __name__ == "__main__":
    unittest.main()
