from __future__ import annotations

import re
from typing import Any
from xml.etree import ElementTree as ET


class FCPXMLValidationService:
    DURATION_PATTERN = re.compile(r"^(\d+/\d+|\d+(?:\.\d+)?)s$")

    def validate(self, fcpxml_payload: bytes | str) -> dict[str, Any]:
        errors: list[str] = []
        warnings: list[str] = []
        root = None

        try:
            root = ET.fromstring(fcpxml_payload)
        except ET.ParseError as exc:
            return {
                "valid": False,
                "errors": [f"xml_not_well_formed:{exc}"],
                "warnings": [],
                "clip_count": 0,
                "asset_count": 0,
                "fps": None,
            }

        if root.tag != "fcpxml":
            errors.append("missing_fcpxml_root")

        resources = root.find("resources")
        library = root.find("library")
        event = library.find("event") if library is not None else None
        project = event.find("project") if event is not None else None
        sequence = project.find("sequence") if project is not None else None
        spine = sequence.find("spine") if sequence is not None else None

        if resources is None:
            errors.append("missing_resources")
        if library is None:
            errors.append("missing_library")
        if event is None:
            errors.append("missing_event")
        if project is None:
            errors.append("missing_project")
        if sequence is None:
            errors.append("missing_sequence")
        if spine is None:
            errors.append("missing_spine")

        assets: dict[str, ET.Element] = {}
        if resources is not None:
            for asset in resources.findall("asset"):
                asset_id = (asset.get("id") or "").strip()
                if not asset_id:
                    warnings.append("asset_without_id")
                    continue
                assets[asset_id] = asset
                src = (asset.get("src") or "").strip()
                if not src:
                    errors.append(f"asset_missing_src:{asset_id}")
                duration = (asset.get("duration") or "").strip()
                if not self._is_valid_duration(duration):
                    errors.append(f"asset_invalid_duration:{asset_id}")

        fps = None
        if resources is not None:
            first_format = resources.find("format")
            if first_format is not None:
                frame_duration = (first_format.get("frameDuration") or "").strip()
                fps = self._fps_from_frame_duration(frame_duration)
                if fps is None or fps <= 0:
                    errors.append("invalid_fps")

        clip_count = 0
        if spine is not None:
            for clip in spine.findall("asset-clip"):
                clip_count += 1
                ref = (clip.get("ref") or "").strip()
                if not ref or ref not in assets:
                    errors.append(f"asset_clip_missing_asset_ref:{clip.get('name') or clip_count}")
                duration = (clip.get("duration") or "").strip()
                if not duration:
                    errors.append(f"clip_missing_duration:{clip.get('name') or clip_count}")
                elif not self._is_valid_duration(duration):
                    errors.append(f"clip_invalid_duration:{clip.get('name') or clip_count}")

        sequence_duration = (sequence.get("duration") or "").strip() if sequence is not None else ""
        if sequence is not None and not self._is_valid_duration(sequence_duration):
            errors.append("sequence_invalid_duration")

        return {
            "valid": not errors,
            "errors": errors,
            "warnings": warnings,
            "clip_count": clip_count,
            "asset_count": len(assets),
            "fps": fps,
        }

    def _is_valid_duration(self, value: str) -> bool:
        if not value:
            return False
        return bool(self.DURATION_PATTERN.match(value))

    def _fps_from_frame_duration(self, value: str) -> float | None:
        match = re.match(r"^(\d+)/(\d+)s$", value)
        if not match:
            return None
        numerator = int(match.group(1))
        denominator = int(match.group(2))
        if numerator <= 0 or denominator <= 0:
            return None
        return denominator / numerator


fcpxml_validation_service = FCPXMLValidationService()
