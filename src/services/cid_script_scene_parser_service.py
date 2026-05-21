from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from schemas.cid_script_to_prompt_schema import ScriptScene, ScriptSequence
from services.script_intake_service import script_intake_service


SCENE_HEADING_RE = re.compile(
    r"^\s*(?:(?P<number>\d{1,4})\s*[\.:\)-]?\s+)?(?P<int_ext>INT\.?\s*/\s*EXT\.?|EXT\.?\s*/\s*INT\.?|INT\.?|EXT\.?|INTERIOR|EXTERIOR)\s+(?P<body>.+?)\s*$",
    re.IGNORECASE,
)

SEQUENCE_HEADING_RE = re.compile(
    r"^\s*(?P<seq_prefix>Secuencia|Sec|Seq)[.\s]+(?P<seq_number>\d+)\s+(?P<rest>.+?)\s*$",
    re.IGNORECASE,
)
CHARACTER_CUE_RE = re.compile(r"^[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ0-9\s\.'\-]{1,40}$")
TIME_OF_DAY_CUES = [
    "NIGHT",
    "DAY",
    "MORNING",
    "EVENING",
    "AFTERNOON",
    "DAWN",
    "DUSK",
    "LATER",
    "CONTINUOUS",
    "NOCHE",
    "DIA",
    "DÍA",
    "MANANA",
    "MAÑANA",
    "TARDE",
    "AMANECER",
    "ATARDECER",
]
PRODUCTION_KEYWORDS = {
    "storyboard": ["storyboard", "shot list", "shotlist", "plano", "planta"],
    "pantallas": ["monitor", "pantalla", "screen", "display"],
    "documentos": ["script", "guion", "nota", "documento", "pagina", "página"],
    "atrezzo": ["mesa", "ordenador", "tablet", "portatil", "laptop", "camara", "cámara"],
    "produccion": ["equipo", "productor", "directora", "director", "produccion", "producción"],
}
CONFLICT_WORDS = ["pero", "sin embargo", "espera", "discute", "duda", "conflicto", "tension", "tensión"]
EMOTION_WORDS = {
    "tension": ["tension", "tensión", "espera", "duda", "presion", "presión"],
    "urgency": ["urgente", "corre", "rapido", "rápido", "inmediato"],
    "calm": ["calma", "silencio", "sereno"],
}


@dataclass
class ParsedSceneBlock:
    scene_number: int
    heading: str
    int_ext: str | None
    location: str | None
    time_of_day: str | None
    lines: list[str]
    sequence_number: int | None = None
    sequence_label: str | None = None


class CIDScriptSceneParserService:
    """Parse screenplay text into canonical scenes and lightweight sequences.

    Future versions should persist multi-tenant parse state and sequence memory,
    but this first implementation stays pure and DB-free.
    """

    STRONG_TRANSITION_MARKERS = (
        "CORTE A",
        "FUNDIDO",
        "MONTAJE",
        "DÍAS DESPUÉS",
        "DIAS DESPUES",
        "SEMANAS DESPUÉS",
        "SEMANAS DESPUES",
        "MESES DESPUÉS",
        "MESES DESPUES",
    )

    def parse_script(self, script_text: str) -> tuple[list[ScriptSequence], list[ScriptScene], list[str]]:
        warnings: list[str] = []
        normalized_text = (script_text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
        if not normalized_text:
            return [], [], ["empty_script_text"]

        blocks = self._detect_scene_blocks(normalized_text)
        if not blocks:
            warnings.append("regex_scene_detection_failed_using_fallback")
            fallback_blocks = self._fallback_blocks(normalized_text)
            blocks = fallback_blocks

        scenes = [self._build_scene(block) for block in blocks]
        if not scenes:
            warnings.append("no_scenes_built_from_script")
            return [], [], warnings

        sequences = self._build_sequences(scenes)
        return sequences, scenes, warnings

    def _detect_scene_blocks(self, script_text: str) -> list[ParsedSceneBlock]:
        lines = script_text.split("\n")
        blocks: list[ParsedSceneBlock] = []
        current: ParsedSceneBlock | None = None

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current is not None:
                    current.lines.append("")
                continue

            heading_data = self._parse_heading(stripped)
            if heading_data is not None:
                if current is not None:
                    blocks.append(current)
                current = ParsedSceneBlock(
                    scene_number=heading_data["scene_number"],
                    heading=heading_data["heading"],
                    int_ext=heading_data["int_ext"],
                    location=heading_data["location"],
                    time_of_day=heading_data["time_of_day"],
                    lines=[],
                    sequence_number=heading_data.get("sequence_number"),
                    sequence_label=heading_data.get("sequence_label"),
                )
                continue

            if current is None:
                continue
            current.lines.append(stripped)

        if current is not None:
            blocks.append(current)
        return blocks

    def _fallback_blocks(self, script_text: str) -> list[ParsedSceneBlock]:
        parsed = script_intake_service.parse_script(script_text)
        if parsed:
            blocks: list[ParsedSceneBlock] = []
            for index, scene in enumerate(parsed, start=1):
                action_lines = [str(line).strip() for line in scene.get("action_blocks", []) if str(line).strip()]
                dialogue_lines = []
                for block in scene.get("dialogue_blocks", []):
                    character = str(block.get("character", "")).strip()
                    text = str(block.get("text", "")).strip()
                    if character:
                        dialogue_lines.append(character)
                    if text:
                        dialogue_lines.append(text)
                blocks.append(
                    ParsedSceneBlock(
                        scene_number=int(scene.get("scene_number") or index),
                        heading=str(scene.get("heading") or f"SCENE {index}"),
                        int_ext=scene.get("int_ext"),
                        location=scene.get("location"),
                        time_of_day=scene.get("time_of_day"),
                        lines=action_lines + dialogue_lines,
                    )
                )
            return blocks

        return [
            ParsedSceneBlock(
                scene_number=1,
                heading="SCENE 1",
                int_ext=None,
                location=None,
                time_of_day=None,
                lines=[line.strip() for line in script_text.split("\n") if line.strip()],
            )
        ]

    def _parse_heading(self, line: str) -> dict[str, str | int | None] | None:
        seq_heading = self._parse_sequence_heading(line)
        if seq_heading is not None:
            return seq_heading

        match = SCENE_HEADING_RE.match(line)
        if not match:
            return None

        raw_number = match.group("number")
        raw_int_ext = (match.group("int_ext") or "").upper().replace(" ", "")
        body = (match.group("body") or "").strip().rstrip(".")

        scene_number = int(raw_number) if raw_number and raw_number.isdigit() else 0
        int_ext = raw_int_ext.replace("INTERIOR", "INT").replace("EXTERIOR", "EXT")
        int_ext = int_ext.replace("INT./EXT.", "INT/EXT").replace("EXT./INT.", "EXT/INT")
        int_ext = int_ext.replace("INT.", "INT").replace("EXT.", "EXT")

        location = body
        time_of_day: str | None = None
        for cue in TIME_OF_DAY_CUES:
            cue_match = re.search(rf"(?:^|[\s\.-]){re.escape(cue)}\.?$", body, re.IGNORECASE)
            if not cue_match:
                continue
            location = body[:cue_match.start()].rstrip(" .-") or body
            time_of_day = cue.upper()
            break

        return {
            "scene_number": scene_number,
            "heading": line,
            "int_ext": int_ext,
            "location": location or None,
            "time_of_day": time_of_day,
            "sequence_number": None,
            "sequence_label": None,
        }

    def _parse_sequence_heading(self, line: str) -> dict[str, str | int | None] | None:
        seq_match = SEQUENCE_HEADING_RE.match(line)
        if not seq_match:
            return None
        seq_prefix = (seq_match.group("seq_prefix") or "").strip().lower()
        seq_number = int(seq_match.group("seq_number"))
        rest = seq_match.group("rest").strip()
        seq_label = f"Sec {seq_number}"

        scene_match = SCENE_HEADING_RE.match(rest)
        if not scene_match:
            return {
                "scene_number": seq_number,
                "heading": line,
                "int_ext": None,
                "location": None,
                "time_of_day": None,
                "sequence_number": seq_number,
                "sequence_label": seq_label,
            }

        raw_int_ext = (scene_match.group("int_ext") or "").upper().replace(" ", "")
        body = (scene_match.group("body") or "").strip().rstrip(".")
        int_ext = raw_int_ext.replace("INTERIOR", "INT").replace("EXTERIOR", "EXT")
        int_ext = int_ext.replace("INT./EXT.", "INT/EXT").replace("EXT./INT.", "EXT/INT")
        int_ext = int_ext.replace("INT.", "INT").replace("EXT.", "EXT")

        location = body
        time_of_day: str | None = None
        for cue in TIME_OF_DAY_CUES:
            cue_match = re.search(rf"(?:^|[\s\.-]){re.escape(cue)}\.?$", body, re.IGNORECASE)
            if not cue_match:
                continue
            location = body[:cue_match.start()].rstrip(" .-") or body
            time_of_day = cue.upper()
            break

        return {
            "scene_number": seq_number,
            "heading": line,
            "int_ext": int_ext,
            "location": location or None,
            "time_of_day": time_of_day,
            "sequence_number": seq_number,
            "sequence_label": seq_label,
        }

    def _build_scene(self, block: ParsedSceneBlock) -> ScriptScene:
        action_lines, dialogue_lines, characters = self._extract_scene_layers(block.lines)
        raw_text = "\n".join(line for line in block.lines if line.strip())
        action_summary = self._summarize_action(action_lines or block.lines)
        dialogue_summary = self._summarize_dialogue(dialogue_lines)
        props = self._extract_production_elements(raw_text)
        production_needs = self._build_production_needs(block, characters, props, raw_text)
        emotional_tone = self._infer_emotional_tone(raw_text, dialogue_summary)
        dramatic_objective = self._infer_dramatic_objective(action_summary, dialogue_summary, block.location)
        conflict = self._infer_conflict(raw_text, dialogue_summary)
        visual_anchors = self._build_visual_anchors(block, characters, props, emotional_tone)
        forbidden_elements = self._build_forbidden_elements(block, action_summary)

        return ScriptScene(
            scene_id=f"scene_{(block.scene_number or 0) if block.scene_number else 0:03d}" if block.scene_number else f"scene_{abs(hash(block.heading)) % 1000:03d}",
            scene_number=block.scene_number or 1,
            heading=block.heading,
            int_ext=block.int_ext,
            location=block.location,
            time_of_day=block.time_of_day,
            raw_text=raw_text or block.heading,
            action_summary=action_summary,
            dialogue_summary=dialogue_summary,
            characters=characters,
            props=props,
            production_needs=production_needs,
            dramatic_objective=dramatic_objective,
            conflict=conflict,
            visual_anchors=visual_anchors,
            forbidden_elements=forbidden_elements,
            sequence_number=block.sequence_number,
            sequence_label=block.sequence_label,
        )

    def _extract_scene_layers(self, lines: Iterable[str]) -> tuple[list[str], list[str], list[str]]:
        action_lines: list[str] = []
        dialogue_lines: list[str] = []
        characters: list[str] = []
        seen_characters: set[str] = set()
        current_character: str | None = None

        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                current_character = None
                continue
            if CHARACTER_CUE_RE.match(line) and len(line.split()) <= 5 and not line.startswith(("INT", "EXT")):
                current_character = line
                if line not in seen_characters:
                    seen_characters.add(line)
                    characters.append(line)
                continue
            if current_character:
                dialogue_lines.append(f"{current_character}: {line}")
                continue
            action_lines.append(line)

        return action_lines, dialogue_lines, characters

    def _summarize_action(self, lines: Iterable[str]) -> str:
        candidates = [line.strip() for line in lines if line and line.strip()]
        if not candidates:
            return "No action summary available."
        return " ".join(candidates[:2])[:320]

    def _summarize_dialogue(self, lines: Iterable[str]) -> str | None:
        candidates = [line.strip() for line in lines if line and line.strip()]
        if not candidates:
            return None
        return " ".join(candidates[:2])[:240]

    def _extract_production_elements(self, raw_text: str) -> list[str]:
        lowered = raw_text.lower()
        props: list[str] = []
        for label, keywords in PRODUCTION_KEYWORDS.items():
            if any(keyword in lowered for keyword in keywords):
                props.append(label)
        return props

    def _build_production_needs(
        self,
        block: ParsedSceneBlock,
        characters: list[str],
        props: list[str],
        raw_text: str,
    ) -> list[str]:
        needs: list[str] = []
        if characters:
            needs.append(f"cast:{len(characters)}")
        if props:
            needs.extend(f"prop:{prop}" for prop in props)
        if block.int_ext:
            needs.append(f"setting:{block.int_ext.lower()}")
        if block.time_of_day:
            needs.append(f"time:{block.time_of_day.lower()}")
        lowered = raw_text.lower()
        if any(word in lowered for word in ["mesa", "table"]):
            needs.append("set_dressing:table")
        if any(word in lowered for word in ["pantalla", "monitor", "screen"]):
            needs.append("tech_surface:monitor")
        if any(word in lowered for word in ["nota", "notas", "notes"]):
            needs.append("paperwork:notes")
        return needs

    def _infer_emotional_tone(self, raw_text: str, dialogue_summary: str | None) -> str:
        combined = f"{raw_text} {dialogue_summary or ''}".lower()
        for tone, keywords in EMOTION_WORDS.items():
            if any(keyword in combined for keyword in keywords):
                return tone
        if dialogue_summary:
            return "dialogue_tension"
        return "focused_professional"

    def _infer_dramatic_objective(self, action_summary: str, dialogue_summary: str | None, location: str | None) -> str:
        combined = f"{action_summary} {dialogue_summary or ''}".lower()
        if any(word in combined for word in ["decide", "decision", "version", "revisa", "review"]):
            return "decision_and_review"
        if any(word in combined for word in ["presenta", "explica", "muestra"]):
            return "presentation_of_information"
        if location and "reunion" in location.lower():
            return "collaborative_alignment"
        return "advance_story_information"

    def _infer_conflict(self, raw_text: str, dialogue_summary: str | None) -> str | None:
        combined = f"{raw_text} {dialogue_summary or ''}".lower()
        if any(word in combined for word in CONFLICT_WORDS):
            return "latent_tension_or_decision_pressure"
        if dialogue_summary:
            return "dialogue_driven_uncertainty"
        return None

    def _build_visual_anchors(
        self,
        block: ParsedSceneBlock,
        characters: list[str],
        props: list[str],
        emotional_tone: str,
    ) -> list[str]:
        anchors: list[str] = []
        if block.location:
            anchors.append(f"location:{block.location}")
        if block.time_of_day:
            anchors.append(f"time_of_day:{block.time_of_day.lower()}")
        if block.int_ext:
            anchors.append(f"int_ext:{block.int_ext.lower()}")
        anchors.extend(f"character:{character.lower()}" for character in characters[:3])
        anchors.extend(f"prop:{prop.lower()}" for prop in props[:4])
        anchors.append(f"mood:{emotional_tone}")
        return anchors

    def _build_forbidden_elements(self, block: ParsedSceneBlock, action_summary: str) -> list[str]:
        forbidden = [
            "generic_futuristic_interface",
            "meaningless_abstract_shapes",
            "unrelated_characters",
            "wrong_location",
        ]
        if block.int_ext == "INT" and block.time_of_day in {"NIGHT", "NOCHE"}:
            forbidden.append("flat_daylight_exterior")
        if "storyboard" in action_summary.lower() or "guion" in action_summary.lower():
            forbidden.append("empty_visual_without_documents")
        return forbidden

    def _build_sequences(self, scenes: list[ScriptScene]) -> list[ScriptSequence]:
        sequences: list[ScriptSequence] = []
        groups: list[list[ScriptScene]] = []
        current: list[ScriptScene] = []
        previous: ScriptScene | None = None

        for scene in scenes:
            if not current:
                current = [scene]
                previous = scene
                continue
            if self._starts_new_sequence(previous, scene, current):
                groups.append(current)
                current = [scene]
            else:
                current.append(scene)
            previous = scene
        if current:
            groups.append(current)

        for chunk in groups:
            first = chunk[0]
            raw_seq_number = first.sequence_number
            sequence_number = raw_seq_number if raw_seq_number is not None else len(sequences) + 1
            sequences.append(
                ScriptSequence(
                    sequence_id=f"seq_{sequence_number:03d}",
                    sequence_number=sequence_number,
                    title=first.location or first.heading,
                    summary="; ".join(scene.heading for scene in chunk)[:280],
                    scene_numbers=[scene.scene_number for scene in chunk],
                    dramatic_purpose=first.dramatic_objective,
                    emotional_arc=self._build_sequence_arc(chunk),
                    continuity_notes=self._build_sequence_continuity_notes(chunk),
                )
            )
        return sequences

    def _starts_new_sequence(
        self,
        previous: ScriptScene | None,
        current: ScriptScene,
        current_group: list[ScriptScene],
    ) -> bool:
        if previous is None:
            return False
        if len(current_group) >= 5:
            return True
        heading = (current.heading or "").upper()
        raw = (current.raw_text or "").upper()
        if any(marker in heading or marker in raw for marker in self.STRONG_TRANSITION_MARKERS):
            return True
        prev_loc = (previous.location or "").strip().lower()
        curr_loc = (current.location or "").strip().lower()
        prev_goal = (previous.dramatic_objective or "").strip().lower()
        curr_goal = (current.dramatic_objective or "").strip().lower()
        prev_time = (previous.time_of_day or "").strip().lower()
        curr_time = (current.time_of_day or "").strip().lower()
        location_changed = bool(prev_loc and curr_loc and prev_loc != curr_loc)
        objective_changed = bool(prev_goal and curr_goal and prev_goal != curr_goal)
        time_jump = bool(prev_time and curr_time and prev_time != curr_time and curr_time not in {"continuous", "continuo"})
        return (location_changed and objective_changed) or (time_jump and objective_changed)

    def _build_sequence_arc(self, scenes: list[ScriptScene]) -> str:
        tones = [scene.emotional_tone for scene in scenes if scene.emotional_tone]
        if not tones:
            return "steady_progression"
        if len(set(tones)) == 1:
            return f"stable_{tones[0]}"
        return f"{tones[0]}_to_{tones[-1]}"

    def _build_sequence_continuity_notes(self, scenes: list[ScriptScene]) -> list[str]:
        notes: list[str] = []
        first_scene = scenes[0]
        if first_scene.location:
            notes.append(f"maintain_location:{first_scene.location}")
        if first_scene.time_of_day:
            notes.append(f"maintain_time_of_day:{first_scene.time_of_day}")
        recurring_characters = sorted({character for scene in scenes for character in scene.characters})
        if recurring_characters:
            notes.append("maintain_character_identity")
        if any("storyboard" in scene.raw_text.lower() for scene in scenes):
            notes.append("keep_storyboard_materials_consistent")
        return notes


cid_script_scene_parser_service = CIDScriptSceneParserService()
