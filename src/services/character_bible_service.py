from __future__ import annotations

from datetime import datetime, timezone
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
    def __init__(self) -> None:
        self._store: dict[str, dict[str, CharacterBibleEntry]] = {}
        self._resolver = CharacterBibleResolver()

    def _key(self, project_id: str, character_id: str) -> str:
        return f"{project_id}::{character_id}"

    def get_entry(self, project_id: str, character_id: str) -> CharacterBibleEntry | None:
        return self._store.get(project_id, {}).get(character_id)

    def list_entries(self, project_id: str) -> list[CharacterBibleEntry]:
        return list(self._store.get(project_id, {}).values())

    def create_or_update_entry(
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
        return entry

    def update_entry(
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
        return entry

    def add_look_variant(
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
        return variant

    def add_reference(
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
        return ref

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

    def _validate_asset_id_format(self, asset_id: str) -> bool:
        if not asset_id or not asset_id.strip():
            return False
        if any(p in asset_id for p in ("/", "\\", "..", "/opt/", "/mnt/", "C:")):
            return False
        return True


character_bible_service = CharacterBibleService()
