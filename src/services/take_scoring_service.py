from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.postproduction import Take


class TakeScoringService:
    async def score_project_takes(self, db: AsyncSession, *, project_id: str) -> dict[str, Any]:
        result = await db.execute(
            select(Take).where(Take.project_id == project_id).order_by(Take.scene_number.asc(), Take.shot_number.asc(), Take.take_number.asc())
        )
        takes = list(result.scalars().all())
        grouped: dict[tuple[int | None, int | None], list[Take]] = defaultdict(list)
        warnings: list[str] = []
        for take in takes:
            take.score = self._score_take(take)
            take.is_recommended = False
            grouped[(take.scene_number, take.shot_number)].append(take)
            conflict_flags = self._conflict_flags(take)
            if conflict_flags:
                warnings.extend(conflict_flags)

        recommended_groups = 0
        for _group_key, group_takes in grouped.items():
            if not group_takes:
                continue
            recommended = sorted(
                group_takes,
                key=lambda item: (
                    item.score,
                    1 if item.is_best else 0,
                    1 if item.is_circled else 0,
                    -int(item.take_number or 9999),
                ),
                reverse=True,
            )[0]
            recommended.is_recommended = True
            recommended.recommended_reason = self._recommended_reason(recommended)
            recommended_groups += 1

        await db.commit()
        return {
            "project_id": project_id,
            "takes_scored": len(takes),
            "recommended_groups": recommended_groups,
            "warnings": sorted(set(warnings)),
        }

    def _score_take(self, take: Take) -> float:
        score = 0.0
        if take.script_status in {"circled", "good"}:
            score += 15
        if take.script_status == "best":
            score += 30
        if take.director_status in {"preferred", "best"}:
            score += 25
        if take.sound_status == "clean":
            score += 12
        if take.audio_circled:
            score += 8
        if take.audio_metadata_status == "parsed":
            score += 6
        elif take.audio_metadata_status == "partial":
            score += 2
        if take.camera_status == "ok":
            score += 10
        if take.is_circled:
            score += 10
        if take.is_best:
            score += 15

        note_text = (take.notes or "").lower()
        if take.script_status == "ng" or take.director_status == "ng":
            score -= 20
        if any(token in note_text for token in ("focus issue", "soft focus", "out of focus")):
            score -= 12
        if any(token in note_text for token in ("noise", "distortion", "rf", "dropout")):
            score -= 12
        if take.reconciliation_status == "conflict":
            score -= 18
        if take.reconciliation_status == "partial":
            score -= 6
        if take.dual_system_status == "conflict":
            score -= 20
        elif take.dual_system_status in {"metadata_warning", "partial"}:
            score -= 6
        if not take.camera_media_asset_id:
            score -= 8
        if not take.sound_media_asset_id:
            score -= 10
        if take.sync_confidence is not None:
            if take.sync_confidence >= 0.9:
                score += 8
            elif take.sync_confidence >= 0.75:
                score += 4
            elif take.sync_confidence < 0.5:
                score -= 8
        elif take.sound_media_asset_id:
            score -= 3
        return score

    def _recommended_reason(self, take: Take) -> str:
        reasons: list[str] = []
        if take.script_status == "best":
            reasons.append("script marks best take")
        elif take.script_status in {"circled", "good"}:
            reasons.append("script continuity positive")
        if take.director_status in {"preferred", "best"}:
            reasons.append("director preference")
        if take.camera_status == "ok":
            reasons.append("camera ok")
        if take.sound_status == "clean":
            reasons.append("clean sound")
        if take.audio_circled:
            reasons.append("iXML circled")
        if take.audio_metadata_status == "parsed":
            reasons.append("audio metadata parsed")
        elif take.audio_metadata_status == "partial":
            reasons.append("audio metadata partial")
        if take.sync_method:
            sync_label = take.sync_method.replace("_", " ")
            if take.sync_confidence is not None:
                reasons.append(f"sync {sync_label} ({take.sync_confidence:.2f})")
            else:
                reasons.append(f"sync {sync_label}")
        if take.dual_system_status == "matched":
            reasons.append("dual-system linked")
        conflict_flags = self._conflict_flags(take)
        if conflict_flags:
            reasons.append(f"warnings: {', '.join(conflict_flags)}")
        if not reasons:
            reasons.append("highest available score in shot group")
        return "; ".join(reasons)

    def _conflict_flags(self, take: Take) -> list[str]:
        if not take.conflict_flags_json:
            return []
        try:
            data = json.loads(take.conflict_flags_json)
            if isinstance(data, list):
                return [str(item) for item in data]
        except Exception:
            return []
        return []


take_scoring_service = TakeScoringService()
