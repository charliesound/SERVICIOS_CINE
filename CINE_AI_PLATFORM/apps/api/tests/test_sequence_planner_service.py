from __future__ import annotations

import unittest

from pydantic import ValidationError

from src.schemas.sequence_plan import SequencePlanRequest
from src.services.sequence_planner_service import SequencePlannerService


class SequencePlannerServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.service = SequencePlannerService()

    def test_plan_sequence_with_narrative_text(self) -> None:
        payload = SequencePlanRequest(
            script_text=(
                "INT. CASA - NOCHE. ANA entra con prisa y deja las llaves en la mesa. "
                "LUIS la observa en silencio y finalmente le pregunta que paso afuera."
            ),
            project_id="project_001",
            sequence_id="seq_001",
            style_profile="neo noir still",
            continuity_mode="strict",
        )

        result = self.service.plan_sequence(payload)

        self.assertTrue(result["ok"])
        self.assertGreaterEqual(len(result["beats"]), 2)
        self.assertGreaterEqual(len(result["shots"]), 2)

    def test_plan_sequence_with_brief_text(self) -> None:
        payload = SequencePlanRequest(script_text="ANA observa la calle en silencio.")

        result = self.service.plan_sequence(payload)

        self.assertTrue(result["ok"])
        self.assertGreaterEqual(len(result["beats"]), 1)
        self.assertGreaterEqual(len(result["shots"]), 1)

    def test_plan_sequence_rejects_empty_script_text(self) -> None:
        with self.assertRaises(ValidationError):
            SequencePlanRequest(script_text="   ")

        invalid_payload = SequencePlanRequest.model_construct(script_text="   ")
        with self.assertRaises(ValueError):
            self.service.plan_sequence(invalid_payload)

    def test_plan_sequence_minimum_output_structure(self) -> None:
        payload = SequencePlanRequest(script_text="EXT. CALLE - DIA. ANA camina y mira su telefono.")

        result = self.service.plan_sequence(payload)

        self.assertIn("ok", result)
        self.assertIn("sequence_summary", result)
        self.assertIn("beats", result)
        self.assertIn("shots", result)
        self.assertIn("characters_detected", result)
        self.assertIn("locations_detected", result)
        self.assertIn("continuity_notes", result)
        self.assertIn("render_inputs", result)

    def test_plan_sequence_shots_and_render_inputs_contract(self) -> None:
        payload = SequencePlanRequest(
            script_text=(
                "INT. OFICINA - TARDE. ANA se acerca al ventanal. "
                "LUIS responde sin mirarla y la tension crece."
            ),
            continuity_mode="strict",
        )

        result = self.service.plan_sequence(payload)

        shots = result["shots"]
        self.assertGreater(len(shots), 0)
        for shot in shots:
            self.assertIn("shot_id", shot)
            self.assertTrue(shot["shot_id"])
            self.assertIn("shot_type", shot)
            self.assertTrue(shot["shot_type"])
            self.assertIn("prompt", shot)
            self.assertTrue(shot["prompt"])
            self.assertIn("negative_prompt", shot)
            self.assertTrue(shot["negative_prompt"])
            self.assertIn("continuity", shot)
            self.assertTrue(shot["continuity"])

        self.assertEqual(result["render_inputs"]["target_endpoint"], "/api/render/jobs")


if __name__ == "__main__":
    unittest.main()
