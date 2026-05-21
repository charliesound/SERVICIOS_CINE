from services.cid_script_scene_parser_service import cid_script_scene_parser_service


def _parse(text: str):
    sequences, scenes, warnings = cid_script_scene_parser_service.parse_script(text)
    return sequences, scenes, warnings


class TestSequenceHeaderDetection:

    def test_detects_sec_1_int(self):
        text = "Sec 1 INT. CASA ABANDONADA - NOCHE\nMarta entra con una linterna."
        _seqs, scenes, _warnings = _parse(text)
        assert len(scenes) >= 1
        s = scenes[0]
        assert s.sequence_number == 1
        assert s.sequence_label == "Sec 1"
        assert s.int_ext == "INT"
        assert s.location == "CASA ABANDONADA"
        assert s.time_of_day == "NOCHE"

    def test_detects_sec_3_ext(self):
        text = "Sec 3 EXT. BOSQUE - NOCHE\nMarta sale corriendo."
        _seqs, scenes, _warnings = _parse(text)
        s = scenes[0]
        assert s.sequence_number == 3
        assert s.sequence_label == "Sec 3"
        assert s.int_ext == "EXT"

    def test_detects_seq_prefix(self):
        text = "Seq 2 INT. HABITACION - DIA\nTexto."
        _seqs, scenes, _warnings = _parse(text)
        s = scenes[0]
        assert s.sequence_number == 2
        assert s.sequence_label == "Sec 2"

    def test_detects_secuencia_prefix(self):
        text = "Secuencia 05 EXT. PLAYA - ATARDECER\nTexto."
        _seqs, scenes, _warnings = _parse(text)
        s = scenes[0]
        assert s.sequence_number == 5
        assert s.sequence_label == "Sec 5"

    def test_does_not_renumber_sec_3_as_sec_2(self):
        text = (
            "Sec 1 INT. CASA - NOCHE\nMarta entra.\n\n"
            "Sec 3 EXT. BOSQUE - NOCHE\nMarta sale."
        )
        _seqs, scenes, _warnings = _parse(text)
        nums = [s.sequence_number for s in scenes]
        assert 1 in nums
        assert 3 in nums
        assert nums == [1, 3]

    def test_regular_int_ext_still_works(self):
        text = "INT. OFICINA - DIA\nJuan trabaja."
        _seqs, scenes, _warnings = _parse(text)
        assert len(scenes) >= 1
        s = scenes[0]
        assert s.sequence_label is None
        assert s.int_ext == "INT"
        assert s.location == "OFICINA"

    def test_unit_type_uses_sequences(self):
        text = "Sec 1 INT. CASA - NOCHE\nMarta entra."
        _seqs, scenes, _warnings = _parse(text)
        s = scenes[0]
        assert s.sequence_label is not None
        assert "Sec" in s.sequence_label


class TestShotPlanner:

    def _run_planner(self, raw_text: str, action_summary: str = "", dialogue: str | None = None):
        from schemas.cid_script_to_prompt_schema import ScriptScene
        scene = ScriptScene(
            scene_id="test_001",
            scene_number=1,
            heading="INT. CASA - NOCHE",
            int_ext="INT",
            location="CASA",
            time_of_day="NOCHE",
            raw_text=raw_text,
            action_summary=action_summary or raw_text,
            dialogue_summary=dialogue,
            characters=["MARTA"],
            sequence_number=1,
            sequence_label="Sec 1",
        )
        from services.storyboard_shot_planner_service import storyboard_shot_planner_service
        return storyboard_shot_planner_service.plan_sequence_shots(scene, mode="auto_cinematic")

    def test_sec_1_generates_at_least_5_shots(self):
        text = (
            "Marta entra con una linterna. La casa está en silencio. "
            "El suelo cruje bajo sus pies. Marta pregunta: ¿Hay alguien ahí? "
            "Una sombra cruza al fondo del pasillo. Marta se queda quieta."
        )
        shots = self._run_planner(text)
        assert len(shots) >= 5, f"Expected >= 5 shots, got {len(shots)}"

    def test_sec_1_includes_sound_detail_beat(self):
        text = "El suelo cruje bajo sus pies."
        shots = self._run_planner(text)
        types = [s["beat_type"] for s in shots]
        assert "sound_detail" in types, f"Expected sound_detail beat in {types}"

    def test_sec_1_includes_shadow_reveal(self):
        text = "Una sombra cruza al fondo del pasillo."
        shots = self._run_planner(text)
        types = [s["beat_type"] for s in shots]
        assert "shadow_reveal" in types, f"Expected shadow_reveal in {types}"

    def test_sec_1_includes_character_entry(self):
        text = "Marta entra con una linterna."
        shots = self._run_planner(text)
        types = [s["beat_type"] for s in shots]
        assert "character_entry" in types, f"Expected character_entry in {types}"

    def test_sec_1_includes_reaction_closeup(self):
        text = "Marta se queda quieta con terror contenido."
        shots = self._run_planner(text)
        types = [s["beat_type"] for s in shots]
        assert "reaction_closeup" in types, f"Expected reaction_closeup in {types}"

    def test_sec_3_generates_at_least_4_shots(self):
        text = (
            "Marta sale corriendo de la casa. "
            "La linterna parpadea. "
            "Detrás de ella, una figura aparece en la puerta."
        )
        shots = self._run_planner(text)
        assert len(shots) >= 4, f"Expected >= 4 shots, got {len(shots)}"

    def test_sec_3_includes_character_exit(self):
        text = "Marta sale corriendo de la casa."
        shots = self._run_planner(text)
        types = [s["beat_type"] for s in shots]
        assert "character_exit" in types, f"Expected character_exit in {types}"

    def test_sec_3_includes_figure_reveal(self):
        text = "Una figura aparece en la puerta."
        shots = self._run_planner(text)
        types = [s["beat_type"] for s in shots]
        assert "figure_reveal" in types, f"Expected figure_reveal in {types}"

    def test_each_shot_has_dramatic_intent(self):
        text = "Marta entra. El suelo cruje. Pregunta: ¿Hay alguien ahí?"
        shots = self._run_planner(text)
        for i, s in enumerate(shots):
            assert s.get("dramatic_intent"), f"Shot {i+1} missing dramatic_intent"
            assert s.get("dramatic_intent_es"), f"Shot {i+1} missing dramatic_intent_es"

    def test_each_shot_has_camera_angle_and_lens(self):
        text = "Marta entra."
        shots = self._run_planner(text)
        for i, s in enumerate(shots):
            assert s.get("camera_angle"), f"Shot {i+1} missing camera_angle"
            assert s.get("lens"), f"Shot {i+1} missing lens"

    def test_dialogue_beat_detected(self):
        text = "Marta pregunta: ¿Hay alguien ahí?"
        shots = self._run_planner(text)
        types = [s["beat_type"] for s in shots]
        assert "dialogue" in types, f"Expected dialogue beat in {types}"

    def test_display_description_included(self):
        text = "Marta entra."
        shots = self._run_planner(text)
        for i, s in enumerate(shots):
            assert s.get("display_description_en"), f"Shot {i+1} missing display_description_en"
            assert s.get("display_description_es"), f"Shot {i+1} missing display_description_es"
