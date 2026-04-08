from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Dict, List, Optional
from uuid import uuid4

from src.schemas.render_context import RenderContextFlags
from src.services.render_request_context import apply_render_context_to_request_payload
from src.services.comfyui_client import ComfyUIClient, ComfyUIClientError, ComfyUITimeoutError
from src.services.render_context_preparer import RenderContextPreparer
from src.settings import settings
from src.storage.render_jobs_repository import RenderJobsRepository


class RenderJobNotFoundError(Exception):
    pass


class RenderJobRetryNotAllowedError(Exception):
    pass


class RenderJobsService:
    def __init__(
        self,
        repository: RenderJobsRepository,
        comfyui_client: ComfyUIClient,
        preparer: Optional[RenderContextPreparer] = None,
        api_base_url: Optional[str] = None,
    ):
        self.repository = repository
        self.comfyui_client = comfyui_client
        self.preparer = preparer
        self.api_base_url = (api_base_url or "").rstrip("/")

    def list_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.repository.list(limit=limit)

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.repository.get(job_id)

    def create_job_from_client_payload(
        self,
        request_payload: Dict[str, Any],
        render_context: Optional[Any] = None,
        parent_job_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = request_payload if isinstance(request_payload, dict) else {}
        context = self._coerce_render_context(render_context)

        if settings.enable_render_context_flags and context is not None:
            payload = apply_render_context_to_request_payload(payload, context)

        return self.create_job(payload, parent_job_id=parent_job_id)

    def create_job(self, request_payload: Dict[str, Any], parent_job_id: Optional[str] = None) -> Dict[str, Any]:
        now = self._now_iso()
        payload = request_payload if isinstance(request_payload, dict) else {}

        job = {
            "job_id": str(uuid4()),
            "created_at": now,
            "updated_at": now,
            "status": "queued",
            "request_payload": payload,
            "parent_job_id": parent_job_id,
            "comfyui_prompt_id": None,
            "result": None,
            "error": None,
            "duration_ms": None,
        }

        return self.repository.create(job)

    def retry_job(self, source_job_id: str) -> Dict[str, Any]:
        source = self.repository.get(source_job_id)
        if not source:
            raise RenderJobNotFoundError(f"Render job not found: {source_job_id}")

        source_status = str(source.get("status") or "").strip().lower()
        if source_status not in {"failed", "timeout"}:
            raise RenderJobRetryNotAllowedError(
                f"Retry allowed only for failed or timeout jobs. Current status: {source_status}"
            )

        source_payload = source.get("request_payload")
        payload = source_payload if isinstance(source_payload, dict) else {}

        return self.create_job(request_payload=payload, parent_job_id=source_job_id)

    def execute_job(self, job_id: str) -> None:
        job = self.repository.get(job_id)
        if not job:
            return

        self.repository.update(
            job_id,
            {
                "status": "running",
                "updated_at": self._now_iso(),
                "error": None,
                "result": None,
                "duration_ms": None,
            },
        )

        started = perf_counter()
        request_payload = job.get("request_payload")

        # Intentar enriquecer el payload si hay un preparador configurado
        if self.preparer and isinstance(request_payload, dict):
            # Extraemos metadatos del job que el preparador pueda usar
            # (character_id, scene_id, etc. suelen estar en el payload o en campos del job)
            context_flags = {
                "character_id": job.get("character_id"),
                "scene_id": job.get("scene_id"),
                "use_ipadapter": job.get("use_ipadapter", False)
            }
            request_payload = self.preparer.prepare_payload(request_payload, context_flags)

        if not isinstance(request_payload, dict) or len(request_payload) == 0:
            self._finalize_failure(
                job_id=job_id,
                status="failed",
                started=started,
                code="INVALID_RENDER_PAYLOAD",
                message="request_payload must be a non-empty object",
            )
            return

        try:
            submission = self.comfyui_client.submit_prompt(request_payload)
            prompt_id = submission.get("prompt_id")

            if not prompt_id:
                self._finalize_failure(
                    job_id=job_id,
                    status="failed",
                    started=started,
                    code="COMFYUI_INVALID_RESPONSE",
                    message="ComfyUI response did not include prompt_id",
                    details={"provider_response": submission.get("provider_response")},
                )
                return

            self.repository.update(
                job_id,
                {
                    "updated_at": self._now_iso(),
                    "comfyui_prompt_id": str(prompt_id),
                },
            )

            poll_state = self.comfyui_client.poll_prompt_until_terminal(str(prompt_id))
            duration_ms = int((perf_counter() - started) * 1000)

            if poll_state.get("state") == "succeeded":
                self.repository.update(
                    job_id,
                    {
                        "status": "succeeded",
                        "updated_at": self._now_iso(),
                        "result": self._build_success_result(submission, poll_state),
                        "error": None,
                        "duration_ms": duration_ms,
                    },
                )
                return

            if poll_state.get("state") == "failed":
                poll_error = poll_state.get("error")
                error_message = "ComfyUI history indicated render failure"
                details: Optional[Dict[str, Any]] = {
                    "prompt_id": str(prompt_id),
                    "status_str": poll_state.get("status_str"),
                }

                if isinstance(poll_error, dict):
                    error_message = str(poll_error.get("message") or error_message)
                    extra_details = poll_error.get("details")
                    if isinstance(extra_details, dict):
                        details.update(extra_details)
                    else:
                        details["history_error"] = poll_error

                self._finalize_failure(
                    job_id=job_id,
                    status="failed",
                    started=started,
                    code="COMFYUI_HISTORY_FAILED",
                    message=error_message,
                    details=details,
                )
                return

            self._finalize_failure(
                job_id=job_id,
                status="failed",
                started=started,
                code="COMFYUI_HISTORY_INVALID_STATE",
                message=f"Unexpected poll state: {poll_state.get('state')}",
                details={"poll_state": poll_state},
            )
        except ComfyUITimeoutError as error:
            self._finalize_failure(
                job_id=job_id,
                status="timeout",
                started=started,
                code=error.code,
                message=error.message,
                details=error.details,
            )
        except ComfyUIClientError as error:
            self._finalize_failure(
                job_id=job_id,
                status="failed",
                started=started,
                code=error.code,
                message=error.message,
                details=error.details,
            )
        except Exception as error:
            self._finalize_failure(
                job_id=job_id,
                status="failed",
                started=started,
                code="RENDER_EXECUTION_FAILED",
                message=str(error),
            )

    def _build_success_result(self, submission: Dict[str, Any], poll_state: Dict[str, Any]) -> Dict[str, Any]:
        history_entry = poll_state.get("history_entry")
        history_summary: Dict[str, Any] = {
            "has_outputs": bool(poll_state.get("has_outputs")),
            "status_str": poll_state.get("status_str"),
        }

        output_images: List[Dict[str, Any]] = []
        if isinstance(history_entry, dict):
            outputs = history_entry.get("outputs")
            if isinstance(outputs, dict):
                history_summary["output_node_count"] = len(outputs)
                output_images = self._extract_output_images(outputs)

            status_data = history_entry.get("status")
            if isinstance(status_data, dict):
                history_summary["completed"] = bool(status_data.get("completed"))

        result: Dict[str, Any] = {
            "provider": "comfyui",
            "prompt_id": submission.get("prompt_id"),
            "submit_status_code": submission.get("status_code"),
            "submit_latency_ms": submission.get("latency_ms"),
            "completion_source": "history",
            "poll_elapsed_ms": poll_state.get("poll_elapsed_ms"),
            "history_summary": history_summary,
            "provider_submit_response": submission.get("provider_response"),
        }

        if output_images:
            result["output_images"] = output_images

        return result

    def _extract_output_images(self, outputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract normalized image references from ComfyUI history outputs.

        ComfyUI history entry outputs have this shape:
        {
            "9": {
                "images": [
                    {"filename": "seq_shot_001_00001_.png", "subfolder": "", "type": "output"}
                ]
            }
        }

        Returns a list of dicts with: filename, subfolder, image_type, media_url, view_url, node_id.
        """
        images: List[Dict[str, Any]] = []
        comfyui_base = settings.comfyui_base_url.rstrip("/")

        for node_id, node_output in outputs.items():
            if not isinstance(node_output, dict):
                continue
            image_list = node_output.get("images")
            if not isinstance(image_list, list):
                continue
            for img in image_list:
                if not isinstance(img, dict):
                    continue
                filename = img.get("filename")
                if not filename:
                    continue
                subfolder = img.get("subfolder", "")
                image_type = img.get("type", "output")

                view_url = (
                    f"{comfyui_base}/view?filename={filename}"
                    f"&type={image_type}"
                    f"&subfolder={subfolder}"
                )

                media_url = None
                if self.api_base_url:
                    media_url = (
                        f"{self.api_base_url}/api/render/jobs/media"
                        f"?filename={filename}"
                        f"&type={image_type}"
                        f"&subfolder={subfolder}"
                    )

                images.append({
                    "filename": filename,
                    "subfolder": subfolder,
                    "image_type": image_type,
                    "media_url": media_url,
                    "view_url": view_url,
                    "node_id": node_id,
                })

        return images

    def _finalize_failure(
        self,
        job_id: str,
        status: str,
        started: float,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        duration_ms = int((perf_counter() - started) * 1000)

        self.repository.update(
            job_id,
            {
                "status": status,
                "updated_at": self._now_iso(),
                "result": None,
                "error": {
                    "code": code,
                    "message": message,
                    "details": details,
                },
                "duration_ms": duration_ms,
            },
        )

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _coerce_render_context(self, render_context: Optional[Any]) -> Optional[RenderContextFlags]:
        if render_context is None:
            return None

        if isinstance(render_context, RenderContextFlags):
            return render_context

        if isinstance(render_context, dict):
            try:
                return RenderContextFlags.model_validate(render_context)
            except Exception:
                return None
        return None

    def fetch_job_image(
        self,
        job_id: str,
        image_index: int = 0,
    ) -> tuple[bytes, str]:
        """Fetch an image for a render job via the ComfyUI proxy.

        Returns (image_bytes, content_type).
        Raises RenderJobNotFoundError if job doesn't exist.
        Raises RuntimeError if job has no output images.
        Propagates ComfyUIClientError if ComfyUI is unavailable.
        """
        job = self.repository.get(job_id)
        if not job:
            raise RenderJobNotFoundError(f"Render job not found: {job_id}")

        result = job.get("result")
        if not isinstance(result, dict):
            raise RuntimeError(f"Job {job_id} has no result data yet (status: {job.get('status')})")

        output_images = result.get("output_images")
        if not isinstance(output_images, list) or len(output_images) == 0:
            raise RuntimeError(f"Job {job_id} has no output images available")

        if image_index < 0 or image_index >= len(output_images):
            raise RuntimeError(
                f"Image index {image_index} out of range for job {job_id} "
                f"(has {len(output_images)} image(s))"
            )

        image_ref = output_images[image_index]
        filename = image_ref.get("filename", "")
        subfolder = image_ref.get("subfolder", "")
        image_type = image_ref.get("image_type", "output")

        if not filename:
            raise RuntimeError(f"Image reference for job {job_id} has no filename")

        return self.comfyui_client.fetch_image(
            filename=filename,
            subfolder=subfolder,
            image_type=image_type,
        )

    def fetch_image(
        self,
        filename: str,
        subfolder: str = "",
        image_type: str = "output",
    ) -> tuple[bytes, str]:
        """Fetch an image from ComfyUI via the backend premium proxy.

        This is the low-level proxy method used by the media delivery route.
        It does not require a job_id — it proxies directly by filename reference.
        """
        return self.comfyui_client.fetch_image(
            filename=filename,
            subfolder=subfolder,
            image_type=image_type,
        )
