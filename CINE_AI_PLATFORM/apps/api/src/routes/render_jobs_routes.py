from fastapi import APIRouter, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse, Response

from src.auth.dependencies import require_roles
from src.schemas.render_job import (
    RenderJobCreateRequest,
    RenderJobErrorResponse,
    RenderJobItemResponse,
    RenderJobListResponse,
)
from src.services.render_jobs_service import RenderJobNotFoundError, RenderJobRetryNotAllowedError, RenderJobsService


def create_render_jobs_router(service: RenderJobsService) -> APIRouter:
    router = APIRouter(prefix="/api/render/jobs", tags=["render-jobs"])

    @router.post(
        "",
        status_code=201,
        response_model=RenderJobItemResponse,
        responses={400: {"model": RenderJobErrorResponse}, 500: {"model": RenderJobErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def create_render_job(payload: RenderJobCreateRequest, background_tasks: BackgroundTasks):
        try:
            job = service.create_job_from_client_payload(
                request_payload=payload.request_payload,
                render_context=payload.render_context,
            )
            background_tasks.add_task(service.execute_job, job["job_id"])
            return {"ok": True, "job": job}
        except Exception as error:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "RENDER_JOB_CREATE_FAILED",
                        "message": str(error),
                    },
                },
            )

    @router.post(
        "/{job_id}/retry",
        status_code=201,
        response_model=RenderJobItemResponse,
        responses={404: {"model": RenderJobErrorResponse}, 409: {"model": RenderJobErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def retry_render_job(job_id: str, background_tasks: BackgroundTasks):
        try:
            new_job = service.retry_job(job_id)
            background_tasks.add_task(service.execute_job, new_job["job_id"])
            return {"ok": True, "job": new_job}
        except RenderJobNotFoundError:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "JOB_NOT_FOUND",
                        "message": f"Render job not found: {job_id}",
                    },
                },
            )
        except RenderJobRetryNotAllowedError as error:
            return JSONResponse(
                status_code=409,
                content={
                    "ok": False,
                    "error": {
                        "code": "JOB_RETRY_NOT_ALLOWED",
                        "message": str(error),
                    },
                },
            )

    @router.get("", response_model=RenderJobListResponse)
    def list_render_jobs(limit: int = Query(default=50, ge=1, le=200)):
        jobs = service.list_jobs(limit=limit)
        return {
            "ok": True,
            "jobs": jobs,
            "count": len(jobs),
        }

    @router.get(
        "/{job_id}",
        response_model=RenderJobItemResponse,
        responses={404: {"model": RenderJobErrorResponse}},
    )
    def get_render_job(job_id: str):
        job = service.get_job(job_id)
        if not job:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "JOB_NOT_FOUND",
                        "message": f"Render job not found: {job_id}",
                    },
                },
            )

        return {
            "ok": True,
            "job": job,
        }

    @router.get("/media")
    def get_render_media(
        filename: str = Query(..., description="Image filename"),
        subfolder: str = Query(default="", description="Subfolder within ComfyUI output"),
        type: str = Query(default="output", description="Image type (output, temp, input)"),
    ):
        """Serve a rendered image through the backend premium proxy.

        The browser never talks to ComfyUI directly. This endpoint fetches
        the image from ComfyUI internally and returns it to the client.
        """
        try:
            image_bytes, content_type = service.fetch_image(
                filename=filename,
                subfolder=subfolder,
                image_type=type,
            )
            return Response(content=image_bytes, media_type=content_type)
        except RenderJobNotFoundError:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "IMAGE_NOT_FOUND",
                        "message": "Image not found",
                    },
                },
            )
        except Exception as error:
            error_msg = str(error)
            status_code = 502
            if "not found" in error_msg.lower() or "no output" in error_msg.lower():
                status_code = 404
            elif "timeout" in error_msg.lower():
                status_code = 504
            elif "unavailable" in error_msg.lower() or "not configured" in error_msg.lower():
                status_code = 503

            return JSONResponse(
                status_code=status_code,
                content={
                    "ok": False,
                    "error": {
                        "code": "MEDIA_DELIVERY_FAILED",
                        "message": error_msg,
                    },
                },
            )

    return router
