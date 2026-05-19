from __future__ import annotations

from fastapi import APIRouter, HTTPException

from schemas.cinematic_taxonomy_schema import (
    CinematicPreset,
    CinematicTaxonomyResponse,
    EnrichPromptRequest,
    EnrichPromptResponse,
    TaxonomyElement,
)
from services.cinematic_taxonomy_service import (
    CategoryNotFoundError,
    CinematicTaxonomyError,
    CinematicTaxonomyService,
    PresetNotFoundError,
)

cinematic_taxonomy_service = CinematicTaxonomyService()

router = APIRouter(prefix="/api/cinematic-taxonomy", tags=["cinematic-taxonomy"])


def _serialize_element(el) -> TaxonomyElement:
    return TaxonomyElement(
        id=el.id,
        name=el.name,
        category=el.category,
        description=el.description,
        prompt_tags=el.prompt_tags,
        negative_prompt_tags=el.negative_prompt_tags,
        use_cases=el.use_cases,
    )


def _serialize_preset(p) -> CinematicPreset:
    return CinematicPreset(
        id=p.id,
        name=p.name,
        description=p.description,
        shot_types=p.shot_types,
        composition=p.composition,
        camera_movements=p.camera_movements,
        visual_styles=p.visual_styles,
        modern_cameras=p.modern_cameras,
        analog_cameras=p.analog_cameras,
        film_stocks=p.film_stocks,
        lighting_styles=p.lighting_styles,
        color_grading=p.color_grading,
        narrative_styles=p.narrative_styles,
        prompt_tags=p.prompt_tags,
        negative_prompt_tags=p.negative_prompt_tags,
    )


@router.get("", response_model=CinematicTaxonomyResponse)
async def get_full_taxonomy():
    service = CinematicTaxonomyService()
    raw = service.get_full_taxonomy()
    categories = {
        cat: [_serialize_element(el) for el in elements]
        for cat, elements in raw.items()
    }
    total = sum(len(v) for v in categories.values())
    return CinematicTaxonomyResponse(categories=categories, total_elements=total)


@router.get("/presets", response_model=list[CinematicPreset])
async def get_presets():
    service = CinematicTaxonomyService()
    presets = service.get_presets()
    return [_serialize_preset(p) for p in presets]


@router.get("/presets/{preset_id}", response_model=CinematicPreset)
async def get_preset(preset_id: str):
    service = CinematicTaxonomyService()
    try:
        preset = service.get_preset(preset_id)
    except PresetNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except CinematicTaxonomyError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _serialize_preset(preset)


@router.get("/{category}", response_model=list[TaxonomyElement])
async def get_category(category: str):
    service = CinematicTaxonomyService()
    try:
        elements = service.get_category(category)
    except CategoryNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except CinematicTaxonomyError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return [_serialize_element(el) for el in elements]


@router.post("/enrich-prompt", response_model=EnrichPromptResponse)
async def enrich_prompt(payload: EnrichPromptRequest):
    service = CinematicTaxonomyService()
    try:
        result = service.enrich_prompt(
            base_prompt=payload.base_prompt,
            preset_id=payload.preset_id,
            selected_tags=payload.selected_tags,
        )
    except (PresetNotFoundError, CategoryNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except CinematicTaxonomyError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return result
