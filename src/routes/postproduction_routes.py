from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/postproduction", tags=["postproduction"])


@router.get("/status")
async def get_postproduction_status():
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "module": "postproduction",
            "enabled": False,
            "production_ready": False,
            "message": (
                "Postproduction remains a stub and is intentionally disabled by default "
                "for production candidate deployments."
            ),
        },
    )
