from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ApprovedAssetType(str, Enum):
    FACE_SHEET = "face_sheet"
    WARDROBE_SHEET = "wardrobe_sheet"
    FULL_BODY = "full_body"
    HAIR_MAKEUP = "hair_makeup"
    PROP_REFERENCE = "prop_reference"
    EXPRESSION_SHEET = "expression_sheet"
    POSE_SHEET = "pose_sheet"
    ACTION_STILL = "action_still"
    MOOD_BOARD = "mood_board"
    CONCEPT_ART = "concept_art"


class ApprovedReferenceAsset(BaseModel):
    asset_id: str
    asset_type: ApprovedAssetType
    asset_api_url: str | None = None
    asset_file_name: str | None = None
    reference_id: str | None = None
    description: str | None = None
    is_primary: bool = False
    sort_order: int = 0
    approved_by_user_id: str | None = None
    approved_at: str | None = None
    notes: str | None = None


class CharacterLookVariant(BaseModel):
    look_id: str
    look_name: str
    narrative_phase: str | None = None
    approved_references: list[ApprovedReferenceAsset] = Field(default_factory=list)
    wardrobe_notes: str | None = None
    hair_makeup_notes: str | None = None
    key_props: list[str] = Field(default_factory=list)
    continuity_rules: list[str] = Field(default_factory=list)
    negative_constraints: list[str] = Field(default_factory=list)
    scene_ids: list[str] = Field(default_factory=list)


class CharacterBibleEntry(BaseModel):
    character_id: str
    project_id: str = ""
    character_name: str
    approved_reference_asset_id: str | None = None
    secondary_reference_asset_ids: list[str] = Field(default_factory=list)
    approved_references: list[ApprovedReferenceAsset] = Field(default_factory=list)
    look_variants: list[CharacterLookVariant] = Field(default_factory=list)
    default_look_id: str | None = None
    wardrobe_notes: str | None = None
    hair_makeup_notes: str | None = None
    key_props: list[str] = Field(default_factory=list)
    continuity_rules: list[str] = Field(default_factory=list)
    negative_constraints: list[str] = Field(default_factory=list)
    notes: str | None = None
    version: int = 1
    created_at: str | None = None
    updated_at: str | None = None


class ShotCharacterReference(BaseModel):
    project_id: str = ""
    shot_number: int
    sequence_id: str | None = None
    character_id: str
    applied_look_id: str | None = None
    applied_reference_asset_ids: list[str] = Field(default_factory=list)
    wardrobe_confirmed: bool = False
    hair_makeup_confirmed: bool = False
    props_confirmed: bool = False
    continuity_verified: bool = False
    tracking_note: str | None = None


class CharacterBibleResolveRequest(BaseModel):
    project_id: str
    character_id: str
    look_id: str | None = None
    narrative_phase: str | None = None
    scene_id: str | None = None


class CharacterBibleResolveResult(BaseModel):
    project_id: str = ""
    character_id: str
    character_name: str
    resolved_look: CharacterLookVariant | None = None
    primary_reference: ApprovedReferenceAsset | None = None
    secondary_references: list[ApprovedReferenceAsset] = Field(default_factory=list)
    prompt_lock_block: str | None = None
    prompt_negative_block: str | None = None
    continuity_block: str | None = None
    applied_reference_ids: list[str] = Field(default_factory=list)
    unresolved_props: list[str] = Field(default_factory=list)
