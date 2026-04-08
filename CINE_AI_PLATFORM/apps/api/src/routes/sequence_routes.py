from fastapi import APIRouter, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse
from typing import Literal, Optional

from src.schemas.sequence_plan import (
    SequenceCollectionCreateRequest,
    SequenceCollectionDeleteResponse,
    SequenceCollectionAuditResponse,
    SequenceCollectionBestUpdateRequest,
    SequenceNotificationWebhookCreateRequest,
    SequenceNotificationWebhookResponse,
    SequenceNotificationWebhookUpdateRequest,
    SequenceNotificationWebhooksListResponse,
    SequenceWebhookDeliveriesCompareResponse,
    SequenceWebhooksDashboardResponse,
    SequenceWebhookHealthResponse,
    SequenceWebhookPreviewRequest,
    SequenceWebhookPreviewResponse,
    SequenceWebhookDeliveryResponse,
    SequenceWebhookDeliveriesListResponse,
    SequenceWebhookDeliveriesProcessRetriesResponse,
    SequenceNotificationChannelCreateRequest,
    SequenceNotificationChannelResponse,
    SequenceNotificationChannelUpdateRequest,
    SequenceNotificationChannelsListResponse,
    SequenceNotificationChannelDeliveryResponse,
    SequenceNotificationChannelDeliveriesListResponse,
    SequenceNotificationChannelDeliveriesProcessRetriesResponse,
    SequenceAlertRoutingRuleCreateRequest,
    SequenceAlertRoutingRuleDeleteResponse,
    SequenceAlertRoutingRuleResponse,
    SequenceAlertRoutingRuleUpdateRequest,
    SequenceAlertRoutingRulesListResponse,
    SequenceNotificationPreferencesResponse,
    SequenceNotificationPreferencesUpdateRequest,
    SequenceNotificationReadUpdateRequest,
    SequenceNotificationResponse,
    SequenceNotificationsListResponse,
    SequenceCollectionItemHighlightRequest,
    SequenceCollectionItemsUpdateRequest,
    SequenceCollectionListResponse,
    SequenceCollectionsDashboardResponse,
    SequenceCollectionResponse,
    SequenceCollectionReviewResponse,
    SequenceCollectionUpdateRequest,
    SequencePlanAndRenderRecentListResponse,
    SequencePlanAndRenderMetaUpdateRequest,
    SequencePlanAndRenderReviewHistoryResponse,
    SequencePlanAndRenderReviewUpdateRequest,
    SequencePlanAndRenderResponse,
    SequencePlanErrorResponse,
    SequencePlanRequest,
    SequenceRetryShotRequest,
    SequenceRetryShotResponse,
    SequencePlanResponse,
)
from src.services.sequence_plan_render_service import (
    SequenceCollectionNotFoundError,
    SequenceNotificationNotFoundError,
    SequencePlanRenderService,
    SequencePlanRunNotFoundError,
    SequenceShotNotFoundError,
    SequenceWebhookDeliveryNotFoundError,
    SequenceWebhookNotFoundError,
    SequenceNotificationChannelNotFoundError,
    SequenceNotificationChannelDeliveryNotFoundError,
    SequenceAlertRoutingRuleNotFoundError,
)
from src.services.sequence_planner_service import SequencePlannerService
from src.auth.dependencies import require_roles


RecentStatusFilter = Literal["queued", "running", "succeeded", "failed", "timeout"]
RecentRankingFilter = Literal["most_stable", "most_problematic", "most_retries", "highest_success_ratio"]


def create_sequence_router(
    planner_service: SequencePlannerService,
    plan_render_service: SequencePlanRenderService,
) -> APIRouter:
    router = APIRouter(prefix="/api/sequence", tags=["sequence-planner"])

    @router.post(
        "/plan",
        response_model=SequencePlanResponse,
        responses={400: {"model": SequencePlanErrorResponse}, 500: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def plan_sequence(payload: SequencePlanRequest):
        try:
            return planner_service.plan_sequence(payload)
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_SEQUENCE_PLAN_REQUEST",
                        "message": str(error),
                    },
                },
            )
        except Exception as error:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "SEQUENCE_PLAN_FAILED",
                        "message": str(error),
                    },
                },
            )

    @router.post(
        "/plan-and-render",
        status_code=201,
        response_model=SequencePlanAndRenderResponse,
        responses={400: {"model": SequencePlanErrorResponse}, 500: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def plan_and_render(payload: SequencePlanRequest, background_tasks: BackgroundTasks):
        try:
            result = plan_render_service.plan_and_create_jobs(payload)
            for job_id in result.get("job_ids", []):
                if isinstance(job_id, str) and job_id.strip():
                    background_tasks.add_task(plan_render_service.execute_job, job_id)
            return result
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_SEQUENCE_PLAN_REQUEST",
                        "message": str(error),
                    },
                },
            )
        except Exception as error:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "SEQUENCE_PLAN_AND_RENDER_FAILED",
                        "message": str(error),
                    },
                },
            )

    @router.get(
        "/plan-and-render",
        response_model=SequencePlanAndRenderRecentListResponse,
    )
    def list_recent_plan_and_render(
        q: Optional[str] = Query(default=None),
        project_id: Optional[str] = Query(default=None),
        sequence_id: Optional[str] = Query(default=None),
        status: Optional[RecentStatusFilter] = Query(default=None),
        is_favorite: Optional[bool] = Query(default=None),
        tag: Optional[str] = Query(default=None),
        ranking: Optional[RecentRankingFilter] = Query(default=None),
        collection_id: Optional[str] = Query(default=None),
        limit: int = Query(default=20, ge=1, le=200),
    ):
        try:
            return plan_render_service.list_recent_requests(
                limit=limit,
                q=q,
                project_id=project_id,
                sequence_id=sequence_id,
                status=status,
                is_favorite=is_favorite,
                tag=tag,
                ranking=ranking,
                collection_id=collection_id,
            )
        except SequenceCollectionNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "COLLECTION_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_SEQUENCE_PLAN_AND_RENDER_LIST_FILTER",
                        "message": str(error),
                    },
                },
            )

    @router.post(
        "/collections",
        status_code=201,
        response_model=SequenceCollectionResponse,
        responses={400: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def create_collection(payload: SequenceCollectionCreateRequest):
        try:
            return plan_render_service.create_collection(
                name=payload.name,
                description=payload.description,
                editorial_note=payload.editorial_note,
                color=payload.color,
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_COLLECTION_REQUEST",
                        "message": str(error),
                    },
                },
            )

    @router.get(
        "/collections",
        response_model=SequenceCollectionListResponse,
    )
    def list_collections(
        limit: int = Query(default=100, ge=1, le=500),
        include_archived: bool = Query(default=False),
    ):
        return plan_render_service.list_collections(limit=limit, include_archived=include_archived)

    @router.get(
        "/notifications",
        response_model=SequenceNotificationsListResponse,
        responses={400: {"model": SequencePlanErrorResponse}},
    )
    def list_notifications(
        collection_id: Optional[str] = Query(default=None),
        is_read: Optional[bool] = Query(default=None),
        limit: int = Query(default=50, ge=1, le=200),
    ):
        try:
            return plan_render_service.list_notifications(
                limit=limit,
                collection_id=collection_id,
                is_read=is_read,
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_NOTIFICATIONS_REQUEST",
                        "message": str(error),
                    },
                },
            )

    @router.get(
        "/notification-preferences",
        response_model=SequenceNotificationPreferencesResponse,
    )
    def get_notification_preferences():
        return plan_render_service.get_notification_preferences()

    @router.patch(
        "/notification-preferences",
        response_model=SequenceNotificationPreferencesResponse,
        responses={400: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def patch_notification_preferences(payload: SequenceNotificationPreferencesUpdateRequest):
        try:
            return plan_render_service.update_notification_preferences(
                notifications_enabled=payload.notifications_enabled,
                min_severity=payload.min_severity,
                enabled_types=payload.enabled_types,
                show_only_unread_by_default=payload.show_only_unread_by_default,
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_NOTIFICATION_PREFERENCES_UPDATE",
                        "message": str(error),
                    },
                },
            )

    @router.get(
        "/webhooks",
        response_model=SequenceNotificationWebhooksListResponse,
        responses={400: {"model": SequencePlanErrorResponse}},
    )
    def list_webhooks(
        limit: int = Query(default=100, ge=1, le=500),
        include_disabled: bool = Query(default=True),
    ):
        try:
            return plan_render_service.list_webhooks(limit=limit, include_disabled=include_disabled)
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_WEBHOOKS_REQUEST",
                        "message": str(error),
                    },
                },
            )

    @router.get(
        "/webhooks/dashboard",
        response_model=SequenceWebhooksDashboardResponse,
        responses={400: {"model": SequencePlanErrorResponse}},
    )
    def get_webhooks_dashboard(
        top_limit: int = Query(default=5, ge=1, le=20),
        errors_limit: int = Query(default=10, ge=1, le=50),
    ):
        try:
            return plan_render_service.get_webhooks_dashboard(
                top_limit=top_limit,
                errors_limit=errors_limit,
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_WEBHOOKS_DASHBOARD_REQUEST",
                        "message": str(error),
                    },
                },
            )

    @router.get(
        "/webhooks/{webhook_id}/health",
        response_model=SequenceWebhookHealthResponse,
        responses={400: {"model": SequencePlanErrorResponse}, 404: {"model": SequencePlanErrorResponse}},
    )
    def get_webhook_health(
        webhook_id: str,
        recent_limit: int = Query(default=30, ge=5, le=200),
        signals_limit: int = Query(default=10, ge=1, le=50),
    ):
        try:
            return plan_render_service.get_webhook_health(
                webhook_id=webhook_id,
                recent_limit=recent_limit,
                signals_limit=signals_limit,
            )
        except SequenceWebhookNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "WEBHOOK_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_WEBHOOK_HEALTH_REQUEST",
                        "message": str(error),
                    },
                },
            )

    @router.post(
        "/webhooks",
        status_code=201,
        response_model=SequenceNotificationWebhookResponse,
        responses={400: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def create_webhook(payload: SequenceNotificationWebhookCreateRequest):
        try:
            return plan_render_service.create_webhook(
                name=payload.name,
                url=payload.url,
                is_enabled=payload.is_enabled,
                auth_mode=payload.auth_mode,
                secret_token=payload.secret_token,
                min_severity=payload.min_severity,
                enabled_types=payload.enabled_types,
                custom_headers=payload.custom_headers,
                payload_template_mode=payload.payload_template_mode,
                payload_template=payload.payload_template,
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_WEBHOOK_REQUEST",
                        "message": str(error),
                    },
                },
            )

    @router.patch(
        "/webhooks/{webhook_id}",
        response_model=SequenceNotificationWebhookResponse,
        responses={400: {"model": SequencePlanErrorResponse}, 404: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def patch_webhook(webhook_id: str, payload: SequenceNotificationWebhookUpdateRequest):
        try:
            return plan_render_service.update_webhook(
                webhook_id=webhook_id,
                name=payload.name,
                url=payload.url,
                is_enabled=payload.is_enabled,
                auth_mode=payload.auth_mode,
                secret_token=payload.secret_token,
                min_severity=payload.min_severity,
                enabled_types=payload.enabled_types,
                custom_headers=payload.custom_headers,
                payload_template_mode=payload.payload_template_mode,
                payload_template=payload.payload_template,
            )
        except SequenceWebhookNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "WEBHOOK_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_WEBHOOK_UPDATE",
                        "message": str(error),
                    },
                },
            )

    @router.post(
        "/webhooks/{webhook_id}/test",
        response_model=SequenceWebhookDeliveryResponse,
        responses={400: {"model": SequencePlanErrorResponse}, 404: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def send_webhook_test_event(webhook_id: str):
        try:
            return plan_render_service.send_test_webhook_event(webhook_id)
        except SequenceWebhookNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "WEBHOOK_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_WEBHOOK_TEST_EVENT",
                        "message": str(error),
                    },
                },
            )

    @router.post(
        "/webhooks/{webhook_id}/preview",
        response_model=SequenceWebhookPreviewResponse,
        responses={400: {"model": SequencePlanErrorResponse}, 404: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def preview_webhook_payload(webhook_id: str, payload: Optional[SequenceWebhookPreviewRequest] = None):
        try:
            return plan_render_service.preview_webhook_payload(
                webhook_id=webhook_id,
                event_type=payload.event_type if payload is not None else None,
                sample_data=payload.sample_data if payload is not None else None,
            )
        except SequenceWebhookNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "WEBHOOK_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_WEBHOOK_PREVIEW_REQUEST",
                        "message": str(error),
                    },
                },
            )

    @router.get(
        "/webhook-deliveries",
        response_model=SequenceWebhookDeliveriesListResponse,
        responses={400: {"model": SequencePlanErrorResponse}},
    )
    def list_webhook_deliveries(
        webhook_id: Optional[str] = Query(default=None),
        collection_id: Optional[str] = Query(default=None),
        notification_id: Optional[str] = Query(default=None),
        is_test: Optional[bool] = Query(default=None),
        limit: int = Query(default=100, ge=1, le=500),
    ):
        try:
            return plan_render_service.list_webhook_deliveries(
                limit=limit,
                webhook_id=webhook_id,
                collection_id=collection_id,
                notification_id=notification_id,
                is_test=is_test,
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_WEBHOOK_DELIVERIES_REQUEST",
                        "message": str(error),
                    },
                },
            )

    @router.get(
        "/webhook-deliveries/compare",
        response_model=SequenceWebhookDeliveriesCompareResponse,
        responses={400: {"model": SequencePlanErrorResponse}, 404: {"model": SequencePlanErrorResponse}},
    )
    def compare_webhook_deliveries(
        left_delivery_id: str = Query(min_length=1),
        right_delivery_id: str = Query(min_length=1),
    ):
        try:
            return plan_render_service.compare_webhook_deliveries(
                left_delivery_id=left_delivery_id,
                right_delivery_id=right_delivery_id,
            )
        except SequenceWebhookDeliveryNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "WEBHOOK_DELIVERY_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_WEBHOOK_DELIVERY_COMPARE_REQUEST",
                        "message": str(error),
                    },
                },
            )

    @router.post(
        "/webhook-deliveries/{delivery_id}/retry",
        response_model=SequenceWebhookDeliveryResponse,
        responses={400: {"model": SequencePlanErrorResponse}, 404: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def retry_webhook_delivery(delivery_id: str):
        try:
            return plan_render_service.retry_webhook_delivery(delivery_id)
        except SequenceWebhookDeliveryNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "WEBHOOK_DELIVERY_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except SequenceWebhookNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "WEBHOOK_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_WEBHOOK_DELIVERY_RETRY",
                        "message": str(error),
                    },
                },
            )

    @router.post(
        "/webhook-deliveries/process-retries",
        response_model=SequenceWebhookDeliveriesProcessRetriesResponse,
        responses={400: {"model": SequencePlanErrorResponse}},
    )
    def process_webhook_delivery_retries(
        limit: int = Query(default=100, ge=1, le=500),
        webhook_id: Optional[str] = Query(default=None),
        collection_id: Optional[str] = Query(default=None),
    ):
        try:
            return plan_render_service.process_webhook_delivery_retries(
                limit=limit,
                webhook_id=webhook_id,
                collection_id=collection_id,
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_WEBHOOK_DELIVERY_RETRY_PROCESS",
                        "message": str(error),
                    },
                },
            )

    @router.get(
        "/notification-channels",
        response_model=SequenceNotificationChannelsListResponse,
        responses={400: {"model": SequencePlanErrorResponse}},
    )
    def list_notification_channels(
        limit: int = Query(default=100, ge=1, le=500),
        include_disabled: bool = Query(default=True),
        channel_type: Optional[Literal["webhook", "slack", "telegram"]] = Query(default=None),
    ):
        try:
            return plan_render_service.list_notification_channels(
                limit=limit,
                include_disabled=include_disabled,
                channel_type=channel_type,
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_NOTIFICATION_CHANNELS_REQUEST",
                        "message": str(error),
                    },
                },
            )

    @router.post(
        "/notification-channels",
        status_code=201,
        response_model=SequenceNotificationChannelResponse,
        responses={400: {"model": SequencePlanErrorResponse}},
    )
    def create_notification_channel(payload: SequenceNotificationChannelCreateRequest):
        try:
            return plan_render_service.create_notification_channel(
                channel_type=payload.channel_type,
                name=payload.name,
                is_enabled=payload.is_enabled,
                config=payload.config,
                min_severity=payload.min_severity,
                enabled_types=payload.enabled_types,
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_NOTIFICATION_CHANNEL_REQUEST",
                        "message": str(error),
                    },
                },
            )

    @router.patch(
        "/notification-channels/{channel_id}",
        response_model=SequenceNotificationChannelResponse,
        responses={400: {"model": SequencePlanErrorResponse}, 404: {"model": SequencePlanErrorResponse}},
    )
    def patch_notification_channel(channel_id: str, payload: SequenceNotificationChannelUpdateRequest):
        try:
            return plan_render_service.update_notification_channel(
                channel_id=channel_id,
                name=payload.name,
                is_enabled=payload.is_enabled,
                config=payload.config,
                min_severity=payload.min_severity,
                enabled_types=payload.enabled_types,
            )
        except SequenceNotificationChannelNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "NOTIFICATION_CHANNEL_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_NOTIFICATION_CHANNEL_UPDATE",
                        "message": str(error),
                    },
                },
            )

    @router.post(
        "/notification-channels/{channel_id}/test",
        response_model=SequenceNotificationChannelDeliveryResponse,
        responses={400: {"model": SequencePlanErrorResponse}, 404: {"model": SequencePlanErrorResponse}},
    )
    def send_notification_channel_test_event(channel_id: str):
        try:
            return plan_render_service.send_test_notification_channel_event(channel_id)
        except SequenceNotificationChannelNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "NOTIFICATION_CHANNEL_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_NOTIFICATION_CHANNEL_TEST_EVENT",
                        "message": str(error),
                    },
                },
            )

    @router.get(
        "/notification-channel-deliveries",
        response_model=SequenceNotificationChannelDeliveriesListResponse,
        responses={400: {"model": SequencePlanErrorResponse}},
    )
    def list_notification_channel_deliveries(
        channel_id: Optional[str] = Query(default=None),
        collection_id: Optional[str] = Query(default=None),
        notification_id: Optional[str] = Query(default=None),
        channel_type: Optional[Literal["webhook", "slack", "telegram"]] = Query(default=None),
        is_test: Optional[bool] = Query(default=None),
        limit: int = Query(default=100, ge=1, le=500),
    ):
        try:
            return plan_render_service.list_notification_channel_deliveries(
                limit=limit,
                channel_id=channel_id,
                collection_id=collection_id,
                notification_id=notification_id,
                channel_type=channel_type,
                is_test=is_test,
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_NOTIFICATION_CHANNEL_DELIVERIES_REQUEST",
                        "message": str(error),
                    },
                },
            )

    @router.post(
        "/notification-channel-deliveries/{delivery_id}/retry",
        response_model=SequenceNotificationChannelDeliveryResponse,
        responses={400: {"model": SequencePlanErrorResponse}, 404: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def retry_notification_channel_delivery(delivery_id: str):
        try:
            return plan_render_service.retry_notification_channel_delivery(delivery_id)
        except SequenceNotificationChannelDeliveryNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "NOTIFICATION_CHANNEL_DELIVERY_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except SequenceNotificationChannelNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "NOTIFICATION_CHANNEL_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_NOTIFICATION_CHANNEL_DELIVERY_RETRY",
                        "message": str(error),
                    },
                },
            )

    @router.post(
        "/notification-channel-deliveries/process-retries",
        response_model=SequenceNotificationChannelDeliveriesProcessRetriesResponse,
        responses={400: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def process_notification_channel_delivery_retries(
        limit: int = Query(default=100, ge=1, le=500),
        channel_id: Optional[str] = Query(default=None),
        collection_id: Optional[str] = Query(default=None),
        channel_type: Optional[Literal["webhook", "slack", "telegram"]] = Query(default=None),
    ):
        try:
            return plan_render_service.process_notification_channel_delivery_retries(
                limit=limit,
                channel_id=channel_id,
                collection_id=collection_id,
                channel_type=channel_type,
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_NOTIFICATION_CHANNEL_DELIVERY_RETRY_PROCESS",
                        "message": str(error),
                    },
                },
            )

    @router.get(
        "/alert-routing-rules",
        response_model=SequenceAlertRoutingRulesListResponse,
        responses={400: {"model": SequencePlanErrorResponse}},
    )
    def list_alert_routing_rules(
        limit: int = Query(default=100, ge=1, le=500),
        include_disabled: bool = Query(default=True),
        target_channel_id: Optional[str] = Query(default=None),
    ):
        try:
            return plan_render_service.list_alert_routing_rules(
                limit=limit,
                include_disabled=include_disabled,
                target_channel_id=target_channel_id,
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_ALERT_ROUTING_RULES_REQUEST",
                        "message": str(error),
                    },
                },
            )

    @router.post(
        "/alert-routing-rules",
        status_code=201,
        response_model=SequenceAlertRoutingRuleResponse,
        responses={400: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def create_alert_routing_rule(payload: SequenceAlertRoutingRuleCreateRequest):
        try:
            return plan_render_service.create_alert_routing_rule(
                name=payload.name,
                is_enabled=payload.is_enabled,
                target_channel_id=payload.target_channel_id,
                target_channel_kind=payload.target_channel_kind,
                match_types=payload.match_types,
                min_severity=payload.min_severity,
                match_collection_id=payload.match_collection_id,
                match_health_status=payload.match_health_status,
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_ALERT_ROUTING_RULE_REQUEST",
                        "message": str(error),
                    },
                },
            )

    @router.patch(
        "/alert-routing-rules/{rule_id}",
        response_model=SequenceAlertRoutingRuleResponse,
        responses={400: {"model": SequencePlanErrorResponse}, 404: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def patch_alert_routing_rule(rule_id: str, payload: SequenceAlertRoutingRuleUpdateRequest):
        try:
            return plan_render_service.update_alert_routing_rule(
                rule_id=rule_id,
                name=payload.name,
                is_enabled=payload.is_enabled,
                target_channel_id=payload.target_channel_id,
                target_channel_kind=payload.target_channel_kind,
                match_types=payload.match_types,
                min_severity=payload.min_severity,
                match_collection_id=payload.match_collection_id,
                match_health_status=payload.match_health_status,
            )
        except SequenceAlertRoutingRuleNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "ALERT_ROUTING_RULE_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_ALERT_ROUTING_RULE_UPDATE",
                        "message": str(error),
                    },
                },
            )

    @router.delete(
        "/alert-routing-rules/{rule_id}",
        response_model=SequenceAlertRoutingRuleDeleteResponse,
        responses={400: {"model": SequencePlanErrorResponse}, 404: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def delete_alert_routing_rule(rule_id: str):
        try:
            return plan_render_service.delete_alert_routing_rule(rule_id)
        except SequenceAlertRoutingRuleNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "ALERT_ROUTING_RULE_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_ALERT_ROUTING_RULE_DELETE",
                        "message": str(error),
                    },
                },
            )

    @router.patch(
        "/notifications/{notification_id}/read",
        response_model=SequenceNotificationResponse,
        responses={404: {"model": SequencePlanErrorResponse}, 400: {"model": SequencePlanErrorResponse}},
    )
    def patch_notification_read(notification_id: str, payload: SequenceNotificationReadUpdateRequest):
        try:
            return plan_render_service.mark_notification_read(
                notification_id=notification_id,
                is_read=payload.is_read,
            )
        except SequenceNotificationNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "NOTIFICATION_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_NOTIFICATION_UPDATE",
                        "message": str(error),
                    },
                },
            )

    @router.get(
        "/collections/dashboard",
        response_model=SequenceCollectionsDashboardResponse,
    )
    def get_collections_dashboard(
        limit: int = Query(default=200, ge=1, le=500),
        include_archived: bool = Query(default=False),
        top_limit: int = Query(default=5, ge=1, le=20),
    ):
        return plan_render_service.get_collections_dashboard(
            limit=limit,
            include_archived=include_archived,
            top_limit=top_limit,
        )

    @router.get(
        "/collections/{collection_id}",
        response_model=SequenceCollectionResponse,
        responses={404: {"model": SequencePlanErrorResponse}},
    )
    def get_collection(collection_id: str):
        result = plan_render_service.get_collection(collection_id)
        if result is None:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "COLLECTION_NOT_FOUND",
                        "message": f"Sequence collection not found: {collection_id}",
                    },
                },
            )
        return result

    @router.patch(
        "/collections/{collection_id}",
        response_model=SequenceCollectionResponse,
        responses={400: {"model": SequencePlanErrorResponse}, 404: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def patch_collection(collection_id: str, payload: SequenceCollectionUpdateRequest):
        try:
            return plan_render_service.update_collection(
                collection_id=collection_id,
                name=payload.name,
                description=payload.description,
                editorial_note=payload.editorial_note,
                color=payload.color,
                is_archived=payload.is_archived,
            )
        except SequenceCollectionNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "COLLECTION_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_COLLECTION_UPDATE",
                        "message": str(error),
                    },
                },
            )

    @router.delete(
        "/collections/{collection_id}",
        response_model=SequenceCollectionDeleteResponse,
        responses={404: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def delete_collection(collection_id: str):
        try:
            return plan_render_service.delete_collection(collection_id)
        except SequenceCollectionNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "COLLECTION_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )

    @router.post(
        "/collections/{collection_id}/items",
        response_model=SequenceCollectionResponse,
        responses={400: {"model": SequencePlanErrorResponse}, 404: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def add_collection_items(collection_id: str, payload: SequenceCollectionItemsUpdateRequest):
        try:
            return plan_render_service.add_collection_items(collection_id=collection_id, request_ids=payload.request_ids)
        except SequenceCollectionNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "COLLECTION_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except SequencePlanRunNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "REQUEST_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_COLLECTION_ITEMS_REQUEST",
                        "message": str(error),
                    },
                },
            )

    @router.delete(
        "/collections/{collection_id}/items/{request_id}",
        response_model=SequenceCollectionResponse,
        responses={404: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def delete_collection_item(collection_id: str, request_id: str):
        try:
            return plan_render_service.remove_collection_item(collection_id=collection_id, request_id=request_id)
        except SequenceCollectionNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "COLLECTION_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except SequencePlanRunNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "REQUEST_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )

    @router.patch(
        "/collections/{collection_id}/items/{request_id}/highlight",
        response_model=SequenceCollectionResponse,
        responses={404: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def patch_collection_item_highlight(
        collection_id: str,
        request_id: str,
        payload: SequenceCollectionItemHighlightRequest,
    ):
        try:
            result = plan_render_service.set_collection_item_highlight(
                collection_id=collection_id,
                request_id=request_id,
                is_highlighted=payload.is_highlighted,
            )
            return {
                "ok": result.get("ok", True),
                "collection": result.get("collection", {}),
            }
        except SequenceCollectionNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "COLLECTION_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except SequencePlanRunNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "REQUEST_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )

    @router.patch(
        "/collections/{collection_id}/best",
        response_model=SequenceCollectionResponse,
        responses={404: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def patch_collection_best(
        collection_id: str,
        payload: SequenceCollectionBestUpdateRequest,
    ):
        try:
            return plan_render_service.set_collection_best_request(
                collection_id=collection_id,
                request_id=payload.request_id,
            )
        except SequenceCollectionNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "COLLECTION_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except SequencePlanRunNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "REQUEST_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )

    @router.get(
        "/collections/{collection_id}/audit",
        response_model=SequenceCollectionAuditResponse,
        responses={404: {"model": SequencePlanErrorResponse}, 500: {"model": SequencePlanErrorResponse}},
    )
    def get_collection_audit(collection_id: str):
        try:
            return plan_render_service.get_collection_audit(collection_id)
        except SequenceCollectionNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "COLLECTION_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except Exception as error:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "SEQUENCE_COLLECTION_AUDIT_FAILED",
                        "message": str(error),
                    },
                },
            )

    @router.get(
        "/collections/{collection_id}/review",
        response_model=SequenceCollectionReviewResponse,
        responses={404: {"model": SequencePlanErrorResponse}, 400: {"model": SequencePlanErrorResponse}},
    )
    def get_collection_review(
        collection_id: str,
        ranking: Optional[RecentRankingFilter] = Query(default=None),
        limit: int = Query(default=200, ge=1, le=500),
    ):
        try:
            return plan_render_service.get_collection_review(
                collection_id=collection_id,
                ranking=ranking,
                limit=limit,
            )
        except SequenceCollectionNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "COLLECTION_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_COLLECTION_REVIEW_REQUEST",
                        "message": str(error),
                    },
                },
            )
        except Exception as error:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "SEQUENCE_PLAN_AND_RENDER_LIST_FAILED",
                        "message": str(error),
                    },
                },
            )

    @router.get(
        "/plan-and-render/{request_id}/review-history",
        response_model=SequencePlanAndRenderReviewHistoryResponse,
        responses={404: {"model": SequencePlanErrorResponse}, 400: {"model": SequencePlanErrorResponse}},
    )
    def get_plan_and_render_review_history(
        request_id: str,
        limit: int = Query(default=200, ge=1, le=500),
    ):
        try:
            return plan_render_service.list_run_review_history(request_id=request_id, limit=limit)
        except SequencePlanRunNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "REQUEST_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_SEQUENCE_PLAN_AND_RENDER_REVIEW_HISTORY",
                        "message": str(error),
                    },
                },
            )
        except Exception as error:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "SEQUENCE_PLAN_AND_RENDER_REVIEW_HISTORY_FAILED",
                        "message": str(error),
                    },
                },
            )

    @router.get(
        "/plan-and-render/{request_id}",
        response_model=SequencePlanAndRenderResponse,
        responses={404: {"model": SequencePlanErrorResponse}},
    )
    def get_plan_and_render_request(request_id: str):
        result = plan_render_service.get_plan_and_render_request(request_id)
        if result is None:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "REQUEST_NOT_FOUND",
                        "message": f"Sequence plan-and-render request not found: {request_id}",
                    },
                },
            )

        return result

    @router.post(
        "/plan-and-render/{request_id}/retry-shot",
        status_code=201,
        response_model=SequenceRetryShotResponse,
        responses={400: {"model": SequencePlanErrorResponse}, 404: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def retry_plan_and_render_shot(
        request_id: str,
        payload: SequenceRetryShotRequest,
        background_tasks: BackgroundTasks,
    ):
        try:
            result = plan_render_service.retry_shot(
                request_id=request_id,
                shot_id=payload.shot_id,
                override_prompt=payload.override_prompt,
                override_negative_prompt=payload.override_negative_prompt,
                override_render_context=payload.override_render_context,
                reason=payload.reason,
            )

            new_job_id = str(result.get("new_job_id") or "")
            if new_job_id:
                background_tasks.add_task(plan_render_service.execute_job, new_job_id)

            return result
        except SequencePlanRunNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "REQUEST_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except SequenceShotNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "SHOT_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_RETRY_SHOT_REQUEST",
                        "message": str(error),
                    },
                },
            )
        except Exception as error:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "SEQUENCE_RETRY_SHOT_FAILED",
                        "message": str(error),
                    },
                },
            )

    @router.patch(
        "/plan-and-render/{request_id}/meta",
        response_model=SequencePlanAndRenderResponse,
        responses={400: {"model": SequencePlanErrorResponse}, 404: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor"))],
    )
    def patch_plan_and_render_meta(request_id: str, payload: SequencePlanAndRenderMetaUpdateRequest):
        try:
            return plan_render_service.update_run_meta(
                request_id=request_id,
                is_favorite=payload.is_favorite,
                tags=payload.tags,
                note=payload.note,
            )
        except SequencePlanRunNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "REQUEST_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_SEQUENCE_PLAN_AND_RENDER_META",
                        "message": str(error),
                    },
                },
            )
        except Exception as error:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "SEQUENCE_PLAN_AND_RENDER_META_UPDATE_FAILED",
                        "message": str(error),
                    },
                },
            )

    @router.patch(
        "/plan-and-render/{request_id}/review",
        response_model=SequencePlanAndRenderResponse,
        responses={400: {"model": SequencePlanErrorResponse}, 404: {"model": SequencePlanErrorResponse}},
        dependencies=[Depends(require_roles("admin", "editor", "reviewer"))],
    )
    def patch_plan_and_render_review(request_id: str, payload: SequencePlanAndRenderReviewUpdateRequest):
        try:
            return plan_render_service.update_run_review(
                request_id=request_id,
                review_status=payload.review_status,
                review_note=payload.review_note,
            )
        except SequencePlanRunNotFoundError as error:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "REQUEST_NOT_FOUND",
                        "message": str(error),
                    },
                },
            )
        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "INVALID_SEQUENCE_PLAN_AND_RENDER_REVIEW",
                        "message": str(error),
                    },
                },
            )
        except Exception as error:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "SEQUENCE_PLAN_AND_RENDER_REVIEW_UPDATE_FAILED",
                        "message": str(error),
                    },
                },
            )

    return router
