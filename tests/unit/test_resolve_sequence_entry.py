from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
os.environ.setdefault("AUTH_SECRET_KEY", "AilinkCinemaAuthRuntimeValue987654321XYZ")
os.environ.setdefault("APP_SECRET_KEY", "AilinkCinemaAppRuntimeValue987654321XYZ")
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from schemas.cid_sequence_first_schema import (
    ScriptSequenceMap,
    ScriptSequenceMapEntry,
    resolve_sequence_entry,
)


def _make_entry(seq_id: str, seq_number: int) -> ScriptSequenceMapEntry:
    return ScriptSequenceMapEntry(
        sequence_id=seq_id,
        sequence_number=seq_number,
        title=f"Sequence {seq_number}",
    )


SEQ_MAP = ScriptSequenceMap(
    sequences=[
        _make_entry("seq_001", 1),
        _make_entry("seq_002", 2),
        _make_entry("seq_003", 3),
    ],
    total_sequences=3,
)


def test_exact_match() -> None:
    """seq_001 should match seq_001 exactly."""
    result = resolve_sequence_entry(SEQ_MAP, "seq_001")
    assert result is not None
    assert result.sequence_id == "seq_001"
    assert result.sequence_number == 1


def test_seq_01_resolves_to_seq_001() -> None:
    """seq_01 (2-digit public ID) should resolve to seq_001 (3-digit internal ID)."""
    result = resolve_sequence_entry(SEQ_MAP, "seq_01")
    assert result is not None
    assert result.sequence_id == "seq_001"
    assert result.sequence_number == 1


def test_plain_number_resolves() -> None:
    """'1' should resolve to sequence_number=1."""
    result = resolve_sequence_entry(SEQ_MAP, "1")
    assert result is not None
    assert result.sequence_number == 1
    assert result.sequence_id == "seq_001"


def test_zero_padded_number_resolves() -> None:
    """'01' should resolve to sequence_number=1."""
    result = resolve_sequence_entry(SEQ_MAP, "01")
    assert result is not None
    assert result.sequence_number == 1


def test_sequence_01_resolves() -> None:
    """'sequence_01' should resolve to sequence_number=1."""
    result = resolve_sequence_entry(SEQ_MAP, "sequence_01")
    assert result is not None
    assert result.sequence_number == 1


def test_sequence_001_resolves() -> None:
    """'sequence_001' should resolve to sequence_number=1."""
    result = resolve_sequence_entry(SEQ_MAP, "sequence_001")
    assert result is not None
    assert result.sequence_number == 1


def test_seq_002_resolves_to_second_entry() -> None:
    """seq_002 should resolve to sequence_number=2."""
    result = resolve_sequence_entry(SEQ_MAP, "seq_002")
    assert result is not None
    assert result.sequence_number == 2


def test_seq_02_resolves_to_second_entry() -> None:
    """seq_02 should resolve to sequence_number=2."""
    result = resolve_sequence_entry(SEQ_MAP, "seq_02")
    assert result is not None
    assert result.sequence_number == 2


def test_number_2_resolves() -> None:
    result = resolve_sequence_entry(SEQ_MAP, "2")
    assert result is not None
    assert result.sequence_number == 2


def test_nonexistent_returns_none() -> None:
    result = resolve_sequence_entry(SEQ_MAP, "seq_999")
    assert result is None


def test_invalid_string_returns_none() -> None:
    result = resolve_sequence_entry(SEQ_MAP, "not-a-sequence")
    assert result is None


def test_empty_map_returns_none() -> None:
    empty_map = ScriptSequenceMap(sequences=[], total_sequences=0)
    result = resolve_sequence_entry(empty_map, "seq_01")
    assert result is None
