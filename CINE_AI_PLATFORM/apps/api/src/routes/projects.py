from fastapi import APIRouter
from src.schemas.project import Project

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("", response_model=list[Project])
def list_projects():
    return [
        {
            "id": "project_001",
            "title": "Demo pelicula",
            "description": "Proyecto de prueba"
        },
        {
            "id": "project_002",
            "title": "Storyboard IA",
            "description": "Sistema de continuidad cinematografica"
        }
    ]
