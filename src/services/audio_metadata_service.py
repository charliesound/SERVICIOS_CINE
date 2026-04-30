from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import struct
import wave
from xml.etree import ElementTree as ET

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.storage import MediaAsset, MediaAssetType, StorageSource
from services.media_path_resolver_service import media_path_resolver_service


@dataclass
class AudioMetadataResult:
    status: str
    filename: str
    asset_id: str | None = None
    sample_rate: int | None = None
    channels: int | None = None
    duration_seconds: float | None = None
    bit_depth: int | None = None
    codec: str | None = None
    file_size: int | None = None
    timecode: str | None = None
    time_reference_samples: int | None = None
    time_reference_seconds: float | None = None
    fps: float | None = None
    scene: str | None = None
    shot: str | None = None
    take: str | None = None
    sound_roll: str | None = None
    circled: bool | None = None
    notes: str | None = None
    warnings: list[str] = field(default_factory=list)
    raw_bext: dict | None = None
    raw_ixml: dict | None = None
    reason: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


class AudioMetadataService:
    def get_audio_metadata(
        self,
        asset: MediaAsset,
        *,
        storage_source: StorageSource | None = None,
    ) -> AudioMetadataResult:
        metadata = media_path_resolver_service._parse_metadata(getattr(asset, "metadata_json", None))
        result = AudioMetadataResult(
            status="partial",
            asset_id=str(getattr(asset, "id", "") or "") or None,
            filename=str(getattr(asset, "file_name", None) or metadata.get("filename") or "audio_asset"),
            sample_rate=self._int_value(metadata.get("sample_rate")),
            channels=self._int_value(metadata.get("channels")),
            duration_seconds=self._float_value(metadata.get("duration_seconds"), metadata.get("duration")),
            bit_depth=self._int_value(metadata.get("bit_depth")),
            codec=self._text_value(metadata.get("codec"), metadata.get("format")),
            file_size=self._int_value(getattr(asset, "file_size", None), metadata.get("file_size")),
            timecode=self._text_value(
                metadata.get("possible_timecode"),
                metadata.get("timecode"),
                metadata.get("start_timecode"),
            ),
            time_reference_samples=self._int_value(metadata.get("time_reference_samples")),
            fps=self._float_value(metadata.get("fps"), metadata.get("audio_fps")),
            scene=self._text_value(metadata.get("scene"), metadata.get("scene_number")),
            shot=self._text_value(metadata.get("shot"), metadata.get("shot_number")),
            take=self._text_value(metadata.get("take"), metadata.get("take_number")),
            sound_roll=self._text_value(metadata.get("sound_roll"), metadata.get("roll"), metadata.get("tape")),
            circled=self._bool_value(metadata.get("circled"), metadata.get("audio_circled")),
            notes=self._text_value(metadata.get("notes"), metadata.get("note")),
            reason="metadata_fallback",
        )

        if str(getattr(asset, "asset_type", "")) != MediaAssetType.AUDIO:
            result.status = "unsupported"
            result.reason = "non_audio_asset"
            return result

        resolved = media_path_resolver_service.resolve_asset(asset, storage_source=storage_source)
        if resolved.get("status") != "resolved":
            result.reason = str(resolved.get("reason") or "unresolved_audio_path")
            result.warnings.append("audio_path_unresolved")
            self._finalize_result(result)
            return result

        resolved_path = Path(str(resolved.get("resolved_path") or ""))
        result.file_size = result.file_size or self._safe_file_size(resolved_path)
        if resolved_path.suffix.lower() != ".wav":
            result.status = "unsupported"
            result.reason = "riff_parser_supported_only_for_wav"
            self._finalize_result(result)
            return result

        try:
            self._parse_wave_basics(resolved_path, result)
        except Exception as exc:
            result.status = "error"
            result.reason = f"wave_parse_failed:{exc.__class__.__name__}"
            result.warnings.append("wave_parse_failed")
            self._finalize_result(result)
            return result

        try:
            self._parse_riff_chunks(resolved_path, result)
        except Exception as exc:
            result.warnings.append(f"riff_chunk_parse_failed:{exc.__class__.__name__}")

        self._merge_metadata_fallbacks(result, metadata)
        self._finalize_result(result)
        return result

    async def scan_project_audio_metadata(
        self,
        db: AsyncSession,
        *,
        project_id: str,
    ) -> list[AudioMetadataResult]:
        assets_result = await db.execute(
            select(MediaAsset).where(MediaAsset.project_id == project_id, MediaAsset.asset_type == MediaAssetType.AUDIO)
        )
        assets = list(assets_result.scalars().all())
        source_ids = {str(asset.storage_source_id) for asset in assets if getattr(asset, "storage_source_id", None)}
        sources_by_id: dict[str, StorageSource] = {}
        if source_ids:
            source_result = await db.execute(select(StorageSource).where(StorageSource.id.in_(source_ids)))
            sources_by_id = {str(source.id): source for source in source_result.scalars().all()}
        return [
            self.get_audio_metadata(
                asset,
                storage_source=sources_by_id.get(str(asset.storage_source_id)) if getattr(asset, "storage_source_id", None) else None,
            )
            for asset in assets
        ]

    def _parse_wave_basics(self, path: Path, result: AudioMetadataResult) -> None:
        with wave.open(str(path), "rb") as wav_file:
            frame_count = wav_file.getnframes()
            sample_rate = wav_file.getframerate() or None
            sample_width = wav_file.getsampwidth() or None
            result.sample_rate = sample_rate or result.sample_rate
            result.channels = wav_file.getnchannels() or result.channels
            result.duration_seconds = (frame_count / sample_rate) if sample_rate else result.duration_seconds
            result.bit_depth = (sample_width * 8) if sample_width else result.bit_depth
            result.codec = result.codec or "PCM"

    def _parse_riff_chunks(self, path: Path, result: AudioMetadataResult) -> None:
        with path.open("rb") as handle:
            if handle.read(4) != b"RIFF":
                result.warnings.append("riff_header_missing")
                return
            _file_size = handle.read(4)
            if handle.read(4) != b"WAVE":
                result.warnings.append("wave_header_missing")
                return

            while True:
                chunk_id = handle.read(4)
                if len(chunk_id) < 4:
                    break
                chunk_size_bytes = handle.read(4)
                if len(chunk_size_bytes) < 4:
                    break
                chunk_size = struct.unpack("<I", chunk_size_bytes)[0]
                chunk_data = handle.read(chunk_size)
                if chunk_size % 2 == 1:
                    handle.read(1)
                if chunk_id == b"bext":
                    result.raw_bext = self._parse_bext_chunk(chunk_data)
                elif chunk_id == b"iXML":
                    result.raw_ixml = self._parse_ixml_chunk(chunk_data)

        bext = result.raw_bext or {}
        if bext:
            result.time_reference_samples = result.time_reference_samples or self._int_value(bext.get("time_reference_samples"))
            result.notes = result.notes or self._text_value(bext.get("description"))

        ixml = result.raw_ixml or {}
        if ixml:
            result.scene = result.scene or self._text_value(ixml.get("scene"))
            result.shot = result.shot or self._text_value(ixml.get("shot"))
            result.take = result.take or self._text_value(ixml.get("take"))
            result.sound_roll = result.sound_roll or self._text_value(ixml.get("tape"), ixml.get("roll"))
            result.circled = result.circled if result.circled is not None else self._bool_value(ixml.get("circled"))
            result.notes = self._text_value(result.notes, ixml.get("note"))
            result.timecode = result.timecode or self._text_value(ixml.get("start_timecode"))
            result.fps = result.fps or self._float_value(ixml.get("fps"), ixml.get("frame_rate"))

    def _parse_bext_chunk(self, chunk_data: bytes) -> dict:
        def clean_text(raw: bytes) -> str | None:
            text = raw.split(b"\x00", 1)[0].decode("utf-8", errors="ignore").strip()
            return text or None

        if len(chunk_data) < 346:
            return {"warning": "bext_chunk_too_small"}
        time_reference_samples = struct.unpack("<Q", chunk_data[338:346])[0]
        return {
            "description": clean_text(chunk_data[0:256]),
            "originator": clean_text(chunk_data[256:288]),
            "originator_reference": clean_text(chunk_data[288:320]),
            "origination_date": clean_text(chunk_data[320:330]),
            "origination_time": clean_text(chunk_data[330:338]),
            "time_reference_samples": time_reference_samples,
            "umid": clean_text(chunk_data[348:412]) if len(chunk_data) >= 412 else None,
        }

    def _parse_ixml_chunk(self, chunk_data: bytes) -> dict:
        xml_text = chunk_data.decode("utf-8", errors="ignore").strip("\x00\n\r\t ")
        if not xml_text:
            return {"warning": "ixml_empty"}
        try:
            root = ET.fromstring(xml_text)
        except Exception:
            return {"raw_xml": xml_text, "warning": "ixml_parse_failed"}

        data = {
            "project": self._xml_text(root, ".//PROJECT"),
            "scene": self._xml_text(root, ".//SCENE"),
            "shot": self._xml_text(root, ".//SHOT"),
            "take": self._xml_text(root, ".//TAKE"),
            "tape": self._xml_text(root, ".//TAPE"),
            "roll": self._xml_text(root, ".//ROLL"),
            "circled": self._xml_text(root, ".//CIRCLED"),
            "note": self._xml_text(root, ".//NOTE"),
            "start_timecode": self._xml_text(root, ".//TIMECODE/RATE/TIMECODE") or self._xml_text(root, ".//START_TIMECODE"),
            "fps": self._xml_text(root, ".//TIMECODE/RATE/FRAME_RATE") or self._xml_text(root, ".//FRAME_RATE"),
            "raw_xml": xml_text,
        }
        return data

    def _merge_metadata_fallbacks(self, result: AudioMetadataResult, metadata: dict) -> None:
        if result.time_reference_samples is not None and result.sample_rate:
            result.time_reference_seconds = result.time_reference_samples / float(result.sample_rate)
        elif result.time_reference_seconds is None:
            result.time_reference_seconds = self._float_value(metadata.get("time_reference_seconds"))

        result.scene = result.scene or self._text_value(metadata.get("audio_scene"), metadata.get("scene_number"), metadata.get("scene"))
        result.shot = result.shot or self._text_value(metadata.get("audio_shot"), metadata.get("shot_number"), metadata.get("shot"))
        result.take = result.take or self._text_value(metadata.get("audio_take"), metadata.get("take_number"), metadata.get("take"))
        result.sound_roll = result.sound_roll or self._text_value(metadata.get("sound_roll"), metadata.get("roll"), metadata.get("tape"))
        result.timecode = result.timecode or self._text_value(metadata.get("possible_timecode"), metadata.get("start_timecode"))
        result.notes = result.notes or self._text_value(metadata.get("notes"), metadata.get("description"))
        if result.circled is None:
            result.circled = self._bool_value(metadata.get("circled"), metadata.get("audio_circled"))

    def _finalize_result(self, result: AudioMetadataResult) -> None:
        if result.time_reference_seconds is None and result.time_reference_samples is not None and result.sample_rate:
            result.time_reference_seconds = result.time_reference_samples / float(result.sample_rate)
        if result.status == "error":
            return
        has_rich = bool(result.raw_bext or result.raw_ixml)
        has_basics = any(
            value is not None
            for value in (result.sample_rate, result.channels, result.duration_seconds, result.bit_depth, result.timecode)
        )
        if has_rich and has_basics:
            result.status = "parsed"
            result.reason = result.reason or "riff_bext_ixml"
        elif has_basics:
            result.status = "partial"
            result.reason = result.reason or "wave_basics_only"
        elif result.status != "unsupported":
            result.status = "partial"
            result.reason = result.reason or "metadata_only"

    def _xml_text(self, root: ET.Element, path: str) -> str | None:
        node = root.find(path)
        if node is None or node.text is None:
            return None
        text = node.text.strip()
        return text or None

    def _safe_file_size(self, path: Path) -> int | None:
        try:
            return path.stat().st_size
        except Exception:
            return None

    def _int_value(self, *values: object) -> int | None:
        for value in values:
            if value is None:
                continue
            try:
                return int(value)
            except Exception:
                continue
        return None

    def _float_value(self, *values: object) -> float | None:
        for value in values:
            if value is None:
                continue
            try:
                return float(value)
            except Exception:
                continue
        return None

    def _text_value(self, *values: object) -> str | None:
        for value in values:
            if value is None:
                continue
            text = str(value).strip()
            if text:
                return text
        return None

    def _bool_value(self, *values: object) -> bool | None:
        for value in values:
            if value is None:
                continue
            if isinstance(value, bool):
                return value
            text = str(value).strip().lower()
            if text in {"1", "true", "yes", "y", "circled"}:
                return True
            if text in {"0", "false", "no", "n", "not_circled"}:
                return False
        return None


audio_metadata_service = AudioMetadataService()
