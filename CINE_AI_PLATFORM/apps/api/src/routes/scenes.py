from fastapi import APIRouter
from src.schemas.scene import Scene

router = APIRouter(prefix="/scenes", tags=["scenes"])

@router.get("", response_model=list[Scene])
def list_scenes():
    return [
        {
            "id": "scene_001",
            "project_id": "project_001",
            "title": "Discusion en la cocina",
            "dramatic_purpose": "Presentar tension entre Ana y Luis"
        },
        {
            "id": "scene_002",
            "project_id": "project_001",
            "title": "Mirada en silencio",
            "dramatic_purpose": "Subrayar distancia emocional"
        },
        {
            "id": "scene_003",
            "project_id": "project_002",
            "title": "Entrada al cafe",
            "dramatic_purpose": "Introducir el espacio y el tono"
        }
    ]
