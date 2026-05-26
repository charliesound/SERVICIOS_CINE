from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from schemas.character_bible_schema import (
    ApprovedReferenceAsset,
    CharacterBibleEntry,
    CharacterBibleEntryCreate,
    CharacterBibleEntryUpdate,
    CharacterBibleResolveRequest,
    CharacterBibleResolveResult,
    CharacterLookVariant,
    LookVariantCreate,
    ReferenceAssetCreate,
)
from services.character_bible_resolver_service import CharacterBibleResolver


_logger = logging.getLogger(__name__)

DEFAULT_DATA_DIR = Path("data/character_bible")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sanitize_asset_url(url: str | None) -> str | None:
    if url is None:
        return None
    url = url.replace("\\", "/")
    if any(p in url for p in ("/opt/", "/mnt/", "C:", "storage_path", "canonical_path")):
        return None
    return url


class CharacterBibleService:
    def __init__(self, data_dir: Path | None = None) -> None:
        self._store: dict[str, dict[str, CharacterBibleEntry]] = {}
        self._resolver = CharacterBibleResolver()
        self._data_dir = data_dir or DEFAULT_DATA_DIR
        self._lock = asyncio.Lock()
        self._load_all()

    # ------------------------------------------------------------------
    # File-backed persistence
    # ------------------------------------------------------------------

    def _path_for(self, project_id: str) -> Path:
        return self._data_dir / f"{project_id}.json"

    def _load_all(self) -> None:
        if not self._data_dir.exists():
            return
        for f in sorted(self._data_dir.glob("*.json")):
            try:
                raw = f.read_text("utf-8")
                data = json.loads(raw)
                for char_id, entry_data in data.items():
                    entry = CharacterBibleEntry(**entry_data)
                    self._store.setdefault(entry.project_id, {})[char_id] = entry
            except Exception:
                _logger.exception("Failed to load character bible data from %s", f)

    async def _save(self, project_id: str) -> None:
        async with self._lock:
            entries = self._store.get(project_id, {})
            data = {
                char_id: entry.model_dump(mode="json")
                for char_id, entry in entries.items()
            }
            path = self._path_for(project_id)
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")
            tmp.replace(path)

    # ------------------------------------------------------------------
    # Read operations (sync)
    # ------------------------------------------------------------------

    def get_entry(self, project_id: str, character_id: str) -> CharacterBibleEntry | None:
        return self._store.get(project_id, {}).get(character_id)

    def list_entries(self, project_id: str) -> list[CharacterBibleEntry]:
        return list(self._store.get(project_id, {}).values())

    def resolve(
        self,
        project_id: str,
        character_id: str,
        resolve_request: CharacterBibleResolveRequest,
    ) -> CharacterBibleResolveResult | None:
        entry = self.get_entry(project_id, character_id)
        if not entry:
            return None
        return self._resolver._resolve_single(entry, resolve_request)

    def get_trace(self, project_id: str, character_id: str) -> dict[str, Any] | None:
        entry = self.get_entry(project_id, character_id)
        if not entry:
            return None
        default_req = CharacterBibleResolveRequest(
            project_id=project_id, character_id=character_id,
        )
        result = self._resolver._resolve_single(entry, default_req)
        return {
            "character_id": character_id,
            "character_name": entry.character_name,
            "trace_metadata": result.trace_metadata,
        }

    # ------------------------------------------------------------------
    # Write operations (async — persist to disk)
    # ------------------------------------------------------------------

    async def create_or_update_entry(
        self,
        project_id: str,
        payload: CharacterBibleEntryCreate,
    ) -> CharacterBibleEntry:
        existing = self.get_entry(project_id, payload.character_id)
        now = _now()

        if existing:
            entry = existing.model_copy(update={
                "character_name": payload.character_name,
                "approved_reference_asset_id": payload.approved_reference_asset_id,
                "wardrobe_notes": payload.wardrobe_notes,
                "hair_makeup_notes": payload.hair_makeup_notes,
                "key_props": payload.key_props,
                "continuity_rules": payload.continuity_rules,
                "negative_constraints": payload.negative_constraints,
                "notes": payload.notes,
                "version": existing.version + 1,
                "updated_at": now,
            })
        else:
            entry = CharacterBibleEntry(
                character_id=payload.character_id,
                project_id=project_id,
                character_name=payload.character_name,
                approved_reference_asset_id=payload.approved_reference_asset_id,
                wardrobe_notes=payload.wardrobe_notes,
                hair_makeup_notes=payload.hair_makeup_notes,
                key_props=payload.key_props,
                continuity_rules=payload.continuity_rules,
                negative_constraints=payload.negative_constraints,
                notes=payload.notes,
                version=1,
                created_at=now,
                updated_at=now,
            )

        self._store.setdefault(project_id, {})[payload.character_id] = entry
        await self._save(project_id)
        return entry

    async def update_entry(
        self,
        project_id: str,
        character_id: str,
        payload: CharacterBibleEntryUpdate,
    ) -> CharacterBibleEntry | None:
        existing = self.get_entry(project_id, character_id)
        if not existing:
            return None

        updates: dict[str, Any] = {"version": existing.version + 1, "updated_at": _now()}
        for field in ("character_name", "approved_reference_asset_id", "wardrobe_notes",
                       "hair_makeup_notes", "notes"):
            val = getattr(payload, field, None)
            if val is not None:
                updates[field] = val
        for field in ("key_props", "continuity_rules", "negative_constraints"):
            val = getattr(payload, field, None)
            if val is not None:
                updates[field] = val

        entry = existing.model_copy(update=updates)
        self._store[project_id][character_id] = entry
        await self._save(project_id)
        return entry

    async def add_look_variant(
        self,
        project_id: str,
        character_id: str,
        payload: LookVariantCreate,
    ) -> CharacterLookVariant | None:
        entry = self.get_entry(project_id, character_id)
        if not entry:
            return None

        for existing in entry.look_variants:
            if existing.look_id == payload.look_id:
                return existing

        variant = CharacterLookVariant(
            look_id=payload.look_id,
            look_name=payload.look_name,
            narrative_phase=payload.narrative_phase,
            wardrobe_notes=payload.wardrobe_notes,
            hair_makeup_notes=payload.hair_makeup_notes,
            key_props=payload.key_props,
            continuity_rules=payload.continuity_rules,
            negative_constraints=payload.negative_constraints,
            scene_ids=payload.scene_ids,
        )

        updated = entry.model_copy(update={
            "look_variants": [*entry.look_variants, variant],
            "version": entry.version + 1,
            "updated_at": _now(),
        })
        self._store[project_id][character_id] = updated
        await self._save(project_id)
        return variant

    async def add_reference(
        self,
        project_id: str,
        character_id: str,
        payload: ReferenceAssetCreate,
    ) -> ApprovedReferenceAsset | None:
        entry = self.get_entry(project_id, character_id)
        if not entry:
            return None

        ref = ApprovedReferenceAsset(
            asset_id=payload.asset_id,
            asset_type=payload.asset_type,
            asset_api_url=_sanitize_asset_url(payload.asset_api_url),
            asset_file_name=payload.asset_file_name,
            reference_id=payload.reference_id,
            description=payload.description,
            is_primary=payload.is_primary,
            sort_order=payload.sort_order,
            notes=payload.notes,
        )

        updated = entry.model_copy(update={
            "approved_references": [*entry.approved_references, ref],
            "version": entry.version + 1,
            "updated_at": _now(),
        })
        self._store[project_id][character_id] = updated
        await self._save(project_id)
        return ref

    # ------------------------------------------------------------------
    # Testing / lifecycle
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Clear all in-memory entries. Used for test isolation."""
        self._store.clear()

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def _validate_asset_id_format(self, asset_id: str) -> bool:
        if not asset_id or not asset_id.strip():
            return False
        if any(p in asset_id for p in ("/", "\\", "..", "/opt/", "/mnt/", "C:")):
            return False
        return True


character_bible_service = CharacterBibleService()
