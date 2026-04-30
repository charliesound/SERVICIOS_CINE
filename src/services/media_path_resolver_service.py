from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from models.storage import MediaAsset, StorageSource


class MediaPathResolverService:
    def resolve_asset(
        self,
        asset: MediaAsset,
        *,
        storage_source: StorageSource | None = None,
    ) -> dict[str, Any]:
        metadata = self._parse_metadata(getattr(asset, "metadata_json", None))
        filename = self._first_text(
            getattr(asset, "file_name", None),
            metadata.get("original_filename"),
            metadata.get("filename"),
        ) or "media_asset"

        candidates: list[tuple[str, str]] = []
        seen: set[str] = set()

        def add_candidate(raw_value: Any, reason: str) -> None:
            normalized = self._normalize_candidate(raw_value)
            if not normalized or normalized in seen:
                return
            seen.add(normalized)
            candidates.append((normalized, reason))

        add_candidate(getattr(asset, "canonical_path", None), "canonical_path")
        add_candidate(metadata.get("file_path"), "metadata.file_path")
        add_candidate(metadata.get("local_path"), "metadata.local_path")
        add_candidate(metadata.get("storage_path"), "metadata.storage_path")
        add_candidate(metadata.get("path"), "metadata.path")
        add_candidate(metadata.get("source_uri"), "metadata.source_uri")
        add_candidate(getattr(asset, "content_ref", None), "content_ref")

        relative_path = self._first_text(
            getattr(asset, "relative_path", None),
            metadata.get("relative_path"),
        )
        mount_path = self._first_text(
            getattr(storage_source, "mount_path", None),
            metadata.get("project_root"),
            metadata.get("root_path"),
            metadata.get("mount_path"),
        )
        if relative_path and mount_path:
            add_candidate(str(Path(mount_path) / relative_path), "storage_source.mount_path + relative_path")
        if relative_path:
            add_candidate(relative_path, "relative_path")

        for candidate, reason in candidates:
            path = Path(candidate)
            if path.is_file():
                resolved_path = str(path.resolve())
                return {
                    "asset_id": str(asset.id),
                    "filename": filename,
                    "resolved_path": resolved_path,
                    "fcpxml_uri": Path(resolved_path).as_uri(),
                    "status": "resolved",
                    "reason": reason,
                    "candidates": [item for item, _ in candidates],
                }

        offline_path = str((Path("/tmp") / filename).resolve())
        return {
            "asset_id": str(asset.id),
            "filename": filename,
            "resolved_path": offline_path,
            "fcpxml_uri": Path(offline_path).as_uri(),
            "status": "offline" if candidates else "missing",
            "reason": candidates[0][1] if candidates else "no_path_candidates",
            "candidates": [item for item, _ in candidates],
        }

    def _parse_metadata(self, metadata_json: Any) -> dict[str, Any]:
        if not metadata_json:
            return {}
        if isinstance(metadata_json, dict):
            return metadata_json
        try:
            parsed = json.loads(metadata_json)
        except Exception:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def _normalize_candidate(self, raw_value: Any) -> str | None:
        text = self._first_text(raw_value)
        if not text:
            return None
        if text.startswith("file://"):
            return text[7:]
        return text

    def _first_text(self, *values: Any) -> str | None:
        for value in values:
            if value is None:
                continue
            text = str(value).strip()
            if text:
                return text
        return None


media_path_resolver_service = MediaPathResolverService()
