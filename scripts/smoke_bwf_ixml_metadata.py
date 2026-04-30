from __future__ import annotations

import json
import os
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from models.storage import MediaAsset, MediaAssetType
from services.audio_metadata_service import audio_metadata_service


def _chunk(chunk_id: bytes, payload: bytes) -> bytes:
    data = chunk_id + struct.pack("<I", len(payload)) + payload
    if len(payload) % 2 == 1:
        data += b"\x00"
    return data


def _pcm_wav_bytes(*, sample_rate: int = 48000, channels: int = 2, seconds: int = 1, bext: bytes | None = None, ixml: str | None = None) -> bytes:
    bits_per_sample = 16
    block_align = channels * (bits_per_sample // 8)
    byte_rate = sample_rate * block_align
    frame_count = sample_rate * seconds
    data_payload = b"\x00\x00" * channels * frame_count
    fmt_payload = struct.pack("<HHIIHH", 1, channels, sample_rate, byte_rate, block_align, bits_per_sample)
    chunks = [_chunk(b"fmt ", fmt_payload)]
    if bext is not None:
        chunks.append(_chunk(b"bext", bext))
    if ixml is not None:
        chunks.append(_chunk(b"iXML", ixml.encode("utf-8")))
    chunks.append(_chunk(b"data", data_payload))
    riff_payload = b"WAVE" + b"".join(chunks)
    return b"RIFF" + struct.pack("<I", len(riff_payload)) + riff_payload


def _bext_payload() -> bytes:
    description = b"CID dual-system test".ljust(256, b"\x00")
    originator = b"CID".ljust(32, b"\x00")
    originator_ref = b"CID-ROLL-01".ljust(32, b"\x00")
    date = b"2026-04-28"
    time = b"12:00:00"
    time_ref = struct.pack("<Q", 48000)
    version = struct.pack("<H", 1)
    umid = b"CID-UMID-0001".ljust(64, b"\x00")
    reserved = b"\x00" * 190
    coding_history = b"A=PCM,F=48000,W=16,M=stereo\x00"
    return description + originator + originator_ref + date + time + time_ref + version + umid + reserved + coding_history


def main() -> None:
    smoke_dir = ROOT / "tmp" / "smoke_bwf_ixml_metadata"
    smoke_dir.mkdir(parents=True, exist_ok=True)
    plain_wav = smoke_dir / "plain.wav"
    rich_wav = smoke_dir / "rich.wav"
    fake_mp3 = smoke_dir / "audio.mp3"

    plain_wav.write_bytes(_pcm_wav_bytes())
    rich_wav.write_bytes(
        _pcm_wav_bytes(
            bext=_bext_payload(),
            ixml=(
                "<BWFXML><PROJECT>CID</PROJECT><SCENE>1</SCENE><SHOT>1</SHOT><TAKE>2</TAKE>"
                "<TAPE>ROLL_A</TAPE><CIRCLED>TRUE</CIRCLED><NOTE>clean lav</NOTE>"
                "<START_TIMECODE>01:00:00:00</START_TIMECODE><FRAME_RATE>24</FRAME_RATE></BWFXML>"
            ),
        )
    )
    fake_mp3.write_bytes(b"ID3")

    plain_asset = MediaAsset(
        id="plain-audio",
        organization_id="org",
        project_id="project",
        storage_source_id=None,
        watch_path_id=None,
        ingest_scan_id=None,
        file_name=plain_wav.name,
        relative_path=plain_wav.name,
        canonical_path=str(plain_wav),
        content_ref=plain_wav.as_uri(),
        file_extension="wav",
        asset_type=MediaAssetType.AUDIO,
        metadata_json=json.dumps({"sample_rate": 48000, "channels": 2}),
        file_size=plain_wav.stat().st_size,
    )
    rich_asset = MediaAsset(
        id="rich-audio",
        organization_id="org",
        project_id="project",
        storage_source_id=None,
        watch_path_id=None,
        ingest_scan_id=None,
        file_name=rich_wav.name,
        relative_path=rich_wav.name,
        canonical_path=str(rich_wav),
        content_ref=rich_wav.as_uri(),
        file_extension="wav",
        asset_type=MediaAssetType.AUDIO,
        metadata_json=json.dumps({}),
        file_size=rich_wav.stat().st_size,
    )
    unsupported_asset = MediaAsset(
        id="mp3-audio",
        organization_id="org",
        project_id="project",
        storage_source_id=None,
        watch_path_id=None,
        ingest_scan_id=None,
        file_name=fake_mp3.name,
        relative_path=fake_mp3.name,
        canonical_path=str(fake_mp3),
        content_ref=fake_mp3.as_uri(),
        file_extension="mp3",
        asset_type=MediaAssetType.AUDIO,
        metadata_json=json.dumps({}),
        file_size=fake_mp3.stat().st_size,
    )

    plain = audio_metadata_service.get_audio_metadata(plain_asset)
    rich = audio_metadata_service.get_audio_metadata(rich_asset)
    unsupported = audio_metadata_service.get_audio_metadata(unsupported_asset)

    assert plain.status == "partial", plain.to_dict()
    assert plain.sample_rate == 48000, plain.to_dict()
    assert plain.channels == 2, plain.to_dict()
    assert plain.duration_seconds and plain.duration_seconds > 0, plain.to_dict()

    assert rich.status == "parsed", rich.to_dict()
    assert rich.sample_rate == 48000, rich.to_dict()
    assert rich.channels == 2, rich.to_dict()
    assert rich.scene == "1", rich.to_dict()
    assert rich.take == "2", rich.to_dict()
    assert rich.circled is True, rich.to_dict()
    assert rich.raw_bext and rich.raw_ixml, rich.to_dict()

    assert unsupported.status == "unsupported", unsupported.to_dict()

    print(
        json.dumps(
            {
                "status": "PASS",
                "plain": plain.to_dict(),
                "rich": rich.to_dict(),
                "unsupported": unsupported.to_dict(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
