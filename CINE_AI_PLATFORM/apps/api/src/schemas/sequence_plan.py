from typing import Any, Dict, List, Literal, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator

from src.schemas.render_job import RenderJobData


class SequencePlanRequest(BaseModel):
    script_text: str = Field(min_length=1)
    project_id: Optional[str] = None
    sequence_id: Optional[str] = None
    style_profile: Optional[str] = None
    continuity_mode: Optional[str] = None
    semantic_prompt_enrichment_enabled: Optional[bool] = None
    semantic_prompt_enrichment_max_chars: Optional[int] = Field(default=None, ge=0, le=2000)

    @field_validator("script_text")
    @classmethod
    def _normalize_script_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("script_text must be a non-empty string")
        return normalized

    @field_validator("project_id", "sequence_id", "style_profile", "continuity_mode", mode="before")
    @classmethod
    def _normalize_optional_text(cls, value: object) -> Optional[str]:
        if isinstance(value, str):
            trimmed = value.strip()
            return trimmed or None
        return None

    @field_validator("semantic_prompt_enrichment_max_chars", mode="before")
    @classmethod
    def _normalize_optional_max_chars(cls, value: object) -> Optional[int]:
        if value is None or value == "":
            return None
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            trimmed = value.strip()
            if not trimmed:
                return None
            return int(trimmed)
        return None


class SequenceBeat(BaseModel):
    beat_id: str
    index: int
    summary: str
    text: str
    intent: Literal["action", "dialogue", "emotion", "setup", "progression"]
    beat_type: Optional[str] = None
    shot_intent: Optional[str] = None
    motivation: Optional[str] = None


class SequenceShot(BaseModel):
    shot_id: str
    beat_id: str
    index: int
    shot_type: Literal[
        "establishing_wide",
        "wide_action",
        "medium",
        "close_up",
        "close_up_emotion",
        "extreme_close_up",
        "over_shoulder_dialogue",
        "low_angle",
        "long_shot"
    ]
    camera: str
    motion: str
    prompt: str
    prompt_base: str
    negative_prompt: str
    continuity: str


class SequenceRenderJobInput(BaseModel):
    shot_id: str
    prompt_base: str = ""
    prompt_enriched: str = ""
    semantic_summary_used: Optional[str] = None
    semantic_enrichment_applied: bool = False
    request_payload: Dict[str, Any] = Field(default_factory=dict)
    render_context: Dict[str, Any] = Field(default_factory=dict)


class SequenceRenderInputs(BaseModel):
    target_endpoint: str = "/api/render/jobs"
    workflow_key: str = "still_sdxl_base_v1"
    jobs: List[SequenceRenderJobInput] = Field(default_factory=list)


class ParsedDialogueBlock(BaseModel):
    character: str
    text: str


class ParsedScene(BaseModel):
    scene_id: str
    heading: str
    location: Optional[str] = None
    time_of_day: Optional[str] = None
    action_blocks: List[str] = Field(default_factory=list)
    dialogue_blocks: List[ParsedDialogueBlock] = Field(default_factory=list)
    characters_detected: List[str] = Field(default_factory=list)


class SceneBreakdown(BaseModel):
    scene_id: str
    heading: str
    location: Optional[str] = None
    time_of_day: Optional[str] = None
    characters_present: List[str] = Field(default_factory=list)
    speaking_characters: List[str] = Field(default_factory=list)
    key_actions: List[str] = Field(default_factory=list)
    props_detected: List[str] = Field(default_factory=list)
    visual_elements: List[str] = Field(default_factory=list)
    moving_elements: List[str] = Field(default_factory=list)
    semi_moving_elements: List[str] = Field(default_factory=list)


class SequencePlanResponse(BaseModel):
    ok: bool = True
    sequence_summary: str
    parsed_scenes: List[ParsedScene] = Field(default_factory=list)
    scene_breakdowns: List[SceneBreakdown] = Field(default_factory=list)
    beats: List[SequenceBeat] = Field(default_factory=list)
    shots: List[SequenceShot] = Field(default_factory=list)
    characters_detected: List[str] = Field(default_factory=list)
    locations_detected: List[str] = Field(default_factory=list)
    continuity_notes: List[str] = Field(default_factory=list)
    semantic_context: Dict[str, Any] = Field(default_factory=dict)
    semantic_prompt_enrichment: Dict[str, Any] = Field(default_factory=dict)
    render_inputs: SequenceRenderInputs


class SequenceShotJobLink(BaseModel):
    shot_id: str
    job_id: str
    request_id: Optional[str] = None
    parent_job_id: Optional[str] = None
    retry_index: Optional[int] = None
    reason: Optional[str] = None


class SequenceRetryShotRequest(BaseModel):
    shot_id: str = Field(min_length=1)
    override_prompt: Optional[str] = None
    override_negative_prompt: Optional[str] = None
    override_render_context: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None

    @field_validator("shot_id", "override_prompt", "override_negative_prompt", "reason", mode="before")
    @classmethod
    def _normalize_optional_text(cls, value: object) -> Optional[str]:
        if isinstance(value, str):
            trimmed = value.strip()
            return trimmed or None
        return None


class SequenceRetryShotResponse(BaseModel):
    ok: bool = True
    request_id: str
    shot_id: str
    parent_job_id: str
    new_job_id: str
    retry_index: int
    status: str


class SequencePlanAndRenderMetaUpdateRequest(BaseModel):
    is_favorite: Optional[bool] = None
    tags: Optional[List[str]] = None
    note: Optional[str] = None

    @field_validator("tags", mode="before")
    @classmethod
    def _normalize_tags(cls, value: object) -> Optional[List[str]]:
        if value is None:
            return None
        if not isinstance(value, list):
            raise ValueError("tags must be an array of strings")

        normalized: List[str] = []
        seen = set()
        for item in value:
            if not isinstance(item, str):
                continue
            trimmed = item.strip()
            if not trimmed:
                continue
            lowered = trimmed.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            normalized.append(trimmed)

        return normalized

    @field_validator("note", mode="before")
    @classmethod
    def _normalize_note(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            return value.strip()
        raise ValueError("note must be a string")


class SequencePlanAndRenderReviewUpdateRequest(BaseModel):
    review_status: Optional[Literal["pending_review", "approved", "rejected"]] = None
    review_note: Optional[str] = None

    @field_validator("review_note", mode="before")
    @classmethod
    def _normalize_review_note(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            return value.strip()
        raise ValueError("review_note must be a string")


class SequenceCollectionCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    description: Optional[str] = None
    editorial_note: Optional[str] = None
    color: Optional[str] = None

    @field_validator("name", "description", "editorial_note", "color", mode="before")
    @classmethod
    def _normalize_collection_text(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            trimmed = value.strip()
            return trimmed
        return None


class SequenceCollectionUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    editorial_note: Optional[str] = None
    color: Optional[str] = None
    is_archived: Optional[bool] = None

    @field_validator("name", "description", "editorial_note", "color", mode="before")
    @classmethod
    def _normalize_collection_text(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            return value.strip()
        return None


class SequenceCollectionBestUpdateRequest(BaseModel):
    request_id: Optional[str] = None

    @field_validator("request_id", mode="before")
    @classmethod
    def _normalize_request_id(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            trimmed = value.strip()
            return trimmed or None
        return None


class SequenceCollectionItemsUpdateRequest(BaseModel):
    request_ids: List[str] = Field(default_factory=list)

    @field_validator("request_ids", mode="before")
    @classmethod
    def _normalize_request_ids(cls, value: object) -> List[str]:
        if not isinstance(value, list):
            return []

        normalized: List[str] = []
        seen = set()
        for item in value:
            if not isinstance(item, str):
                continue
            trimmed = item.strip()
            if not trimmed:
                continue
            if trimmed in seen:
                continue
            seen.add(trimmed)
            normalized.append(trimmed)

        return normalized


class SequenceCollectionItemHighlightRequest(BaseModel):
    is_highlighted: bool


class SequenceCollectionItem(BaseModel):
    collection_id: str
    request_id: str
    is_highlighted: bool = False
    added_at: str


class SequenceCollectionSummary(BaseModel):
    collection_id: str
    name: str
    description: str = ""
    editorial_note: str = ""
    color: str = ""
    is_archived: bool = False
    best_request_id: Optional[str] = None
    created_at: str
    updated_at: str
    item_count: int = 0
    highlighted_count: int = 0
    health_status: Literal["green", "yellow", "red"] = "green"
    alerts: List[str] = Field(default_factory=list)
    items: List[SequenceCollectionItem] = Field(default_factory=list)


class SequenceCollectionResponse(BaseModel):
    ok: bool = True
    collection: SequenceCollectionSummary


class SequenceCollectionListResponse(BaseModel):
    ok: bool = True
    collections: List[SequenceCollectionSummary] = Field(default_factory=list)
    limit: int = 100
    count: int = 0


class SequenceCollectionsDashboardItem(BaseModel):
    collection_id: str
    name: str
    health_status: Literal["green", "yellow", "red"] = "green"
    alerts: List[str] = Field(default_factory=list)
    item_count: int = 0
    total_executions: int = 0
    total_retries: int = 0
    pending_review_count: int = 0
    best_request_id: Optional[str] = None
    success_ratio: float = 0.0
    updated_at: str


class SequenceCollectionsDashboardResponse(BaseModel):
    ok: bool = True
    total_collections: int = 0
    collections_green: int = 0
    collections_yellow: int = 0
    collections_red: int = 0
    top_collections_by_executions: List[SequenceCollectionsDashboardItem] = Field(default_factory=list)
    top_collections_by_retries: List[SequenceCollectionsDashboardItem] = Field(default_factory=list)
    collections_without_best_execution: List[SequenceCollectionsDashboardItem] = Field(default_factory=list)
    collections_with_pending_review: List[SequenceCollectionsDashboardItem] = Field(default_factory=list)
    highlighted_collections: List[SequenceCollectionsDashboardItem] = Field(default_factory=list)


class SequenceNotification(BaseModel):
    notification_id: str
    collection_id: str
    type: str
    severity: Literal["info", "warning", "critical"] = "info"
    message: str
    created_at: str
    is_read: bool = False


class SequenceNotificationsListResponse(BaseModel):
    ok: bool = True
    notifications: List[SequenceNotification] = Field(default_factory=list)
    limit: int = 50
    count: int = 0


class SequenceNotificationReadUpdateRequest(BaseModel):
    is_read: bool = True


class SequenceNotificationResponse(BaseModel):
    ok: bool = True
    notification: SequenceNotification


class SequenceNotificationPreferences(BaseModel):
    notifications_enabled: bool = True
    min_severity: Literal["info", "warning", "critical"] = "info"
    enabled_types: List[str] = Field(default_factory=list)
    show_only_unread_by_default: bool = False
    updated_at: str = ""


class SequenceNotificationPreferencesResponse(BaseModel):
    ok: bool = True
    preferences: SequenceNotificationPreferences


class SequenceNotificationPreferencesUpdateRequest(BaseModel):
    notifications_enabled: Optional[bool] = None
    min_severity: Optional[Literal["info", "warning", "critical"]] = None
    enabled_types: Optional[List[str]] = None
    show_only_unread_by_default: Optional[bool] = None

    @field_validator("enabled_types", mode="before")
    @classmethod
    def _normalize_enabled_types(cls, value: object) -> Optional[List[str]]:
        if value is None:
            return None
        if not isinstance(value, list):
            raise ValueError("enabled_types must be an array of strings")

        normalized: List[str] = []
        seen = set()
        for item in value:
            if not isinstance(item, str):
                continue
            trimmed = item.strip()
            if not trimmed:
                continue
            if trimmed in seen:
                continue
            seen.add(trimmed)
            normalized.append(trimmed)

        return normalized


class SequenceNotificationWebhook(BaseModel):
    webhook_id: str
    name: str
    url: str
    is_enabled: bool = True
    auth_mode: Literal["none", "bearer", "hmac_sha256"] = "none"
    has_secret_token: bool = False
    min_severity: Literal["info", "warning", "critical"] = "info"
    enabled_types: List[str] = Field(default_factory=list)
    custom_headers: Dict[str, str] = Field(default_factory=dict)
    payload_template_mode: Literal["default", "compact", "custom"] = "default"
    payload_template: Optional[Dict[str, Any]] = None
    health_status: Literal["green", "yellow", "red"] = "green"
    alerts: List[str] = Field(default_factory=list)
    created_at: str
    updated_at: str


class SequenceNotificationWebhookResponse(BaseModel):
    ok: bool = True
    webhook: SequenceNotificationWebhook


class SequenceNotificationWebhooksListResponse(BaseModel):
    ok: bool = True
    webhooks: List[SequenceNotificationWebhook] = Field(default_factory=list)
    limit: int = 100
    count: int = 0


class SequenceNotificationWebhookCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    url: str = Field(min_length=1)
    is_enabled: bool = True
    auth_mode: Literal["none", "bearer", "hmac_sha256"] = "none"
    secret_token: Optional[str] = None
    min_severity: Literal["info", "warning", "critical"] = "info"
    enabled_types: List[str] = Field(default_factory=list)
    custom_headers: Dict[str, str] = Field(default_factory=dict)
    payload_template_mode: Literal["default", "compact", "custom"] = "default"
    payload_template: Optional[Dict[str, Any]] = None

    @field_validator("name", "url", mode="before")
    @classmethod
    def _normalize_required_text(cls, value: object) -> str:
        if isinstance(value, str):
            trimmed = value.strip()
            if trimmed:
                return trimmed
        raise ValueError("name/url must be non-empty strings")

    @field_validator("url")
    @classmethod
    def _validate_url(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("url must be a valid http/https URL")
        return value

    @field_validator("secret_token", mode="before")
    @classmethod
    def _normalize_secret_token(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            trimmed = value.strip()
            return trimmed or None
        raise ValueError("secret_token must be a string")

    @field_validator("enabled_types", mode="before")
    @classmethod
    def _normalize_enabled_types(cls, value: object) -> List[str]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("enabled_types must be an array of strings")

        normalized: List[str] = []
        seen = set()
        for item in value:
            if not isinstance(item, str):
                continue
            trimmed = item.strip()
            if not trimmed:
                continue
            if trimmed in seen:
                continue
            seen.add(trimmed)
            normalized.append(trimmed)

        return normalized

    @field_validator("custom_headers", mode="before")
    @classmethod
    def _normalize_custom_headers(cls, value: object) -> Dict[str, str]:
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise ValueError("custom_headers must be an object")

        normalized: Dict[str, str] = {}
        for raw_key, raw_value in value.items():
            if not isinstance(raw_key, str):
                continue
            key = raw_key.strip()
            if not key:
                continue
            if isinstance(raw_value, str):
                val = raw_value.strip()
            else:
                val = str(raw_value).strip()
            if not val:
                continue
            normalized[key] = val

        return normalized

    @field_validator("payload_template", mode="before")
    @classmethod
    def _normalize_payload_template(cls, value: object) -> Optional[Dict[str, Any]]:
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError("payload_template must be an object")
        return value


class SequenceNotificationWebhookUpdateRequest(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    is_enabled: Optional[bool] = None
    auth_mode: Optional[Literal["none", "bearer", "hmac_sha256"]] = None
    secret_token: Optional[str] = None
    min_severity: Optional[Literal["info", "warning", "critical"]] = None
    enabled_types: Optional[List[str]] = None
    custom_headers: Optional[Dict[str, str]] = None
    payload_template_mode: Optional[Literal["default", "compact", "custom"]] = None
    payload_template: Optional[Dict[str, Any]] = None

    @field_validator("name", "url", mode="before")
    @classmethod
    def _normalize_optional_text(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            trimmed = value.strip()
            return trimmed or None
        return None

    @field_validator("url")
    @classmethod
    def _validate_optional_url(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("url must be a valid http/https URL")
        return value

    @field_validator("secret_token", mode="before")
    @classmethod
    def _normalize_optional_secret_token(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            return value.strip()
        raise ValueError("secret_token must be a string")

    @field_validator("enabled_types", mode="before")
    @classmethod
    def _normalize_enabled_types(cls, value: object) -> Optional[List[str]]:
        if value is None:
            return None
        if not isinstance(value, list):
            raise ValueError("enabled_types must be an array of strings")

        normalized: List[str] = []
        seen = set()
        for item in value:
            if not isinstance(item, str):
                continue
            trimmed = item.strip()
            if not trimmed:
                continue
            if trimmed in seen:
                continue
            seen.add(trimmed)
            normalized.append(trimmed)

        return normalized

    @field_validator("custom_headers", mode="before")
    @classmethod
    def _normalize_optional_custom_headers(cls, value: object) -> Optional[Dict[str, str]]:
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError("custom_headers must be an object")

        normalized: Dict[str, str] = {}
        for raw_key, raw_value in value.items():
            if not isinstance(raw_key, str):
                continue
            key = raw_key.strip()
            if not key:
                continue
            if isinstance(raw_value, str):
                val = raw_value.strip()
            else:
                val = str(raw_value).strip()
            if not val:
                continue
            normalized[key] = val

        return normalized

    @field_validator("payload_template", mode="before")
    @classmethod
    def _normalize_optional_payload_template(cls, value: object) -> Optional[Dict[str, Any]]:
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError("payload_template must be an object")
        return value


class SequenceWebhookPreviewRequest(BaseModel):
    event_type: Optional[str] = None
    sample_data: Optional[Dict[str, Any]] = None

    @field_validator("event_type", mode="before")
    @classmethod
    def _normalize_optional_event_type(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            trimmed = value.strip()
            return trimmed or None
        return None

    @field_validator("sample_data", mode="before")
    @classmethod
    def _normalize_optional_sample_data(cls, value: object) -> Optional[Dict[str, Any]]:
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError("sample_data must be an object")
        return value


class SequenceWebhookPreviewResponse(BaseModel):
    ok: bool = True
    webhook_id: str
    auth_mode: Literal["none", "bearer", "hmac_sha256"] = "none"
    payload_template_mode: Literal["default", "compact", "custom"] = "default"
    rendered_payload: Dict[str, Any] = Field(default_factory=dict)
    rendered_headers: Dict[str, str] = Field(default_factory=dict)
    signature_preview: Optional[str] = None


class SequenceWebhookDeliveryStructuredDiff(BaseModel):
    added: Dict[str, Any] = Field(default_factory=dict)
    removed: Dict[str, Any] = Field(default_factory=dict)
    changed: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    unchanged_count: int = 0


class SequenceWebhookDeliveriesCompareResponse(BaseModel):
    ok: bool = True
    left_delivery_id: str
    right_delivery_id: str
    auth_mode_left: Literal["none", "bearer", "hmac_sha256"] = "none"
    auth_mode_right: Literal["none", "bearer", "hmac_sha256"] = "none"
    payload_template_mode_left: Literal["default", "compact", "custom"] = "default"
    payload_template_mode_right: Literal["default", "compact", "custom"] = "default"
    payload_diff: SequenceWebhookDeliveryStructuredDiff = Field(default_factory=SequenceWebhookDeliveryStructuredDiff)
    headers_diff: SequenceWebhookDeliveryStructuredDiff = Field(default_factory=SequenceWebhookDeliveryStructuredDiff)


class SequenceWebhookDelivery(BaseModel):
    delivery_id: str
    webhook_id: str
    notification_id: str
    collection_id: str
    routing_rule_id: Optional[str] = None
    routing_rule_name: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    delivery_status: Literal["pending", "sent", "failed"] = "pending"
    attempt_count: int = 1
    max_attempts: int = 4
    last_attempt_at: Optional[str] = None
    next_retry_at: Optional[str] = None
    final_failure_at: Optional[str] = None
    is_test: bool = False
    template_mode: Literal["default", "compact", "custom"] = "default"
    auth_mode: Literal["none", "bearer", "hmac_sha256"] = "none"
    request_headers: Dict[str, str] = Field(default_factory=dict)
    signature_timestamp: Optional[str] = None
    response_status_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str
    delivered_at: Optional[str] = None


class SequenceWebhookDeliveriesListResponse(BaseModel):
    ok: bool = True
    deliveries: List[SequenceWebhookDelivery] = Field(default_factory=list)
    limit: int = 100
    count: int = 0


class SequenceWebhookDeliveryResponse(BaseModel):
    ok: bool = True
    delivery: SequenceWebhookDelivery


class SequenceWebhookDeliveriesProcessRetriesResponse(BaseModel):
    ok: bool = True
    processed_count: int = 0
    sent_count: int = 0
    failed_count: int = 0
    exhausted_count: int = 0
    deliveries: List[SequenceWebhookDelivery] = Field(default_factory=list)


class SequenceNotificationChannel(BaseModel):
    channel_id: str
    channel_type: Literal["webhook", "slack", "telegram"] = "webhook"
    name: str
    is_enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)
    min_severity: Literal["info", "warning", "critical"] = "info"
    enabled_types: List[str] = Field(default_factory=list)
    created_at: str
    updated_at: str


class SequenceNotificationChannelResponse(BaseModel):
    ok: bool = True
    channel: SequenceNotificationChannel


class SequenceNotificationChannelsListResponse(BaseModel):
    ok: bool = True
    channels: List[SequenceNotificationChannel] = Field(default_factory=list)
    limit: int = 100
    count: int = 0


class SequenceNotificationChannelCreateRequest(BaseModel):
    channel_type: Literal["webhook", "slack", "telegram"]
    name: str = Field(min_length=1)
    is_enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)
    min_severity: Literal["info", "warning", "critical"] = "info"
    enabled_types: List[str] = Field(default_factory=list)

    @field_validator("name", mode="before")
    @classmethod
    def _normalize_required_name(cls, value: object) -> str:
        if isinstance(value, str):
            trimmed = value.strip()
            if trimmed:
                return trimmed
        raise ValueError("name must be a non-empty string")

    @field_validator("config", mode="before")
    @classmethod
    def _normalize_config(cls, value: object) -> Dict[str, Any]:
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise ValueError("config must be an object")
        return value

    @field_validator("enabled_types", mode="before")
    @classmethod
    def _normalize_enabled_types(cls, value: object) -> List[str]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("enabled_types must be an array of strings")

        normalized: List[str] = []
        seen = set()
        for item in value:
            if not isinstance(item, str):
                continue
            trimmed = item.strip()
            if not trimmed or trimmed in seen:
                continue
            seen.add(trimmed)
            normalized.append(trimmed)

        return normalized


class SequenceNotificationChannelUpdateRequest(BaseModel):
    name: Optional[str] = None
    is_enabled: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
    min_severity: Optional[Literal["info", "warning", "critical"]] = None
    enabled_types: Optional[List[str]] = None

    @field_validator("name", mode="before")
    @classmethod
    def _normalize_optional_name(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            trimmed = value.strip()
            return trimmed or None
        return None

    @field_validator("config", mode="before")
    @classmethod
    def _normalize_optional_config(cls, value: object) -> Optional[Dict[str, Any]]:
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError("config must be an object")
        return value

    @field_validator("enabled_types", mode="before")
    @classmethod
    def _normalize_optional_enabled_types(cls, value: object) -> Optional[List[str]]:
        if value is None:
            return None
        if not isinstance(value, list):
            raise ValueError("enabled_types must be an array of strings")

        normalized: List[str] = []
        seen = set()
        for item in value:
            if not isinstance(item, str):
                continue
            trimmed = item.strip()
            if not trimmed or trimmed in seen:
                continue
            seen.add(trimmed)
            normalized.append(trimmed)

        return normalized


class SequenceNotificationChannelDelivery(BaseModel):
    delivery_id: str
    channel_id: str
    channel_type: Literal["webhook", "slack", "telegram"] = "webhook"
    notification_id: str
    collection_id: str
    routing_rule_id: Optional[str] = None
    routing_rule_name: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    message_text: str = ""
    delivery_status: Literal["pending", "sent", "failed"] = "pending"
    attempt_count: int = 0
    max_attempts: int = 4
    last_attempt_at: Optional[str] = None
    next_retry_at: Optional[str] = None
    final_failure_at: Optional[str] = None
    is_test: bool = False
    response_status_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str
    delivered_at: Optional[str] = None


class SequenceNotificationChannelDeliveryResponse(BaseModel):
    ok: bool = True
    delivery: SequenceNotificationChannelDelivery


class SequenceNotificationChannelDeliveriesListResponse(BaseModel):
    ok: bool = True
    deliveries: List[SequenceNotificationChannelDelivery] = Field(default_factory=list)
    limit: int = 100
    count: int = 0


class SequenceNotificationChannelDeliveriesProcessRetriesResponse(BaseModel):
    ok: bool = True
    processed_count: int = 0
    sent_count: int = 0
    failed_count: int = 0
    exhausted_count: int = 0
    deliveries: List[SequenceNotificationChannelDelivery] = Field(default_factory=list)


class SequenceAlertRoutingRule(BaseModel):
    rule_id: str
    name: str
    is_enabled: bool = True
    target_channel_id: str
    target_channel_kind: Literal["notification_channel", "webhook"] = "notification_channel"
    target_name: Optional[str] = None
    target_channel_type: Optional[str] = None
    target_exists: bool = True
    match_types: List[str] = Field(default_factory=list)
    min_severity: Literal["info", "warning", "critical"] = "info"
    match_collection_id: Optional[str] = None
    match_health_status: Optional[Literal["green", "yellow", "red"]] = None
    created_at: str
    updated_at: str


class SequenceAlertRoutingRuleResponse(BaseModel):
    ok: bool = True
    rule: SequenceAlertRoutingRule


class SequenceAlertRoutingRulesListResponse(BaseModel):
    ok: bool = True
    rules: List[SequenceAlertRoutingRule] = Field(default_factory=list)
    limit: int = 100
    count: int = 0


class SequenceAlertRoutingRuleCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    is_enabled: bool = True
    target_channel_id: str = Field(min_length=1)
    target_channel_kind: Optional[Literal["notification_channel", "webhook"]] = None
    match_types: List[str] = Field(default_factory=list)
    min_severity: Literal["info", "warning", "critical"] = "info"
    match_collection_id: Optional[str] = None
    match_health_status: Optional[Literal["green", "yellow", "red"]] = None

    @field_validator("name", "target_channel_id", mode="before")
    @classmethod
    def _normalize_required_text(cls, value: object) -> str:
        if isinstance(value, str):
            trimmed = value.strip()
            if trimmed:
                return trimmed
        raise ValueError("name/target_channel_id must be non-empty strings")

    @field_validator("match_collection_id", mode="before")
    @classmethod
    def _normalize_optional_text(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            trimmed = value.strip()
            return trimmed or None
        return None

    @field_validator("match_types", mode="before")
    @classmethod
    def _normalize_match_types(cls, value: object) -> List[str]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("match_types must be an array of strings")

        normalized: List[str] = []
        seen = set()
        for item in value:
            if not isinstance(item, str):
                continue
            trimmed = item.strip()
            if not trimmed or trimmed in seen:
                continue
            seen.add(trimmed)
            normalized.append(trimmed)

        return normalized


class SequenceAlertRoutingRuleUpdateRequest(BaseModel):
    name: Optional[str] = None
    is_enabled: Optional[bool] = None
    target_channel_id: Optional[str] = None
    target_channel_kind: Optional[Literal["notification_channel", "webhook"]] = None
    match_types: Optional[List[str]] = None
    min_severity: Optional[Literal["info", "warning", "critical"]] = None
    match_collection_id: Optional[str] = None
    match_health_status: Optional[Literal["green", "yellow", "red"]] = None

    @field_validator("name", "target_channel_id", "match_collection_id", mode="before")
    @classmethod
    def _normalize_optional_text(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            trimmed = value.strip()
            return trimmed or None
        return None

    @field_validator("match_types", mode="before")
    @classmethod
    def _normalize_optional_match_types(cls, value: object) -> Optional[List[str]]:
        if value is None:
            return None
        if not isinstance(value, list):
            raise ValueError("match_types must be an array of strings")

        normalized: List[str] = []
        seen = set()
        for item in value:
            if not isinstance(item, str):
                continue
            trimmed = item.strip()
            if not trimmed or trimmed in seen:
                continue
            seen.add(trimmed)
            normalized.append(trimmed)

        return normalized


class SequenceAlertRoutingRuleDeleteResponse(BaseModel):
    ok: bool = True
    rule_id: str
    deleted: bool = True


class SequenceWebhooksDashboardItem(BaseModel):
    webhook_id: str
    name: str
    is_enabled: bool = True
    health_status: Literal["green", "yellow", "red"] = "green"
    alerts: List[str] = Field(default_factory=list)
    total_deliveries: int = 0
    sent_deliveries: int = 0
    failed_deliveries: int = 0
    pending_deliveries: int = 0
    exhausted_deliveries: int = 0
    total_retries: int = 0
    failure_ratio: float = 0.0
    last_delivery_at: Optional[str] = None


class SequenceWebhooksDashboardErrorItem(BaseModel):
    delivery_id: str
    webhook_id: str
    webhook_name: str
    notification_id: str
    collection_id: str
    error_message: str
    attempt_count: int = 0
    max_attempts: int = 0
    is_test: bool = False
    auth_mode: Literal["none", "bearer", "hmac_sha256"] = "none"
    payload_template_mode: Literal["default", "compact", "custom"] = "default"
    created_at: str
    last_attempt_at: Optional[str] = None


class SequenceWebhooksDashboardAlertItem(BaseModel):
    webhook_id: str
    name: str
    health_status: Literal["green", "yellow", "red"] = "green"
    alerts: List[str] = Field(default_factory=list)
    failed_deliveries: int = 0
    exhausted_deliveries: int = 0
    failure_ratio: float = 0.0


class SequenceWebhooksDashboardResponse(BaseModel):
    ok: bool = True
    total_webhooks: int = 0
    active_webhooks: int = 0
    inactive_webhooks: int = 0
    webhooks_green: int = 0
    webhooks_yellow: int = 0
    webhooks_red: int = 0
    total_deliveries: int = 0
    sent_deliveries: int = 0
    failed_deliveries: int = 0
    pending_deliveries: int = 0
    top_webhooks_by_volume: List[SequenceWebhooksDashboardItem] = Field(default_factory=list)
    top_webhooks_by_failures: List[SequenceWebhooksDashboardItem] = Field(default_factory=list)
    top_webhooks_by_retries: List[SequenceWebhooksDashboardItem] = Field(default_factory=list)
    active_alerts: List[SequenceWebhooksDashboardAlertItem] = Field(default_factory=list)
    recent_delivery_errors: List[SequenceWebhooksDashboardErrorItem] = Field(default_factory=list)


class SequenceWebhookHealthSignal(BaseModel):
    code: str
    severity: Literal["info", "warning", "critical"] = "info"
    message: str
    observed_at: Optional[str] = None


class SequenceWebhookHealthOperationalSummary(BaseModel):
    total_deliveries: int = 0
    sent_deliveries: int = 0
    failed_deliveries: int = 0
    pending_deliveries: int = 0
    exhausted_deliveries: int = 0
    total_retries: int = 0
    failure_ratio: float = 0.0
    recent_deliveries: int = 0
    recent_failed_deliveries: int = 0
    last_delivery_at: Optional[str] = None
    last_success_at: Optional[str] = None
    last_failure_at: Optional[str] = None


class SequenceWebhookHealthResponse(BaseModel):
    ok: bool = True
    webhook: SequenceNotificationWebhook
    operational_summary: SequenceWebhookHealthOperationalSummary = Field(
        default_factory=SequenceWebhookHealthOperationalSummary
    )
    health_status: Literal["green", "yellow", "red"] = "green"
    alerts: List[str] = Field(default_factory=list)
    recent_signals: List[SequenceWebhookHealthSignal] = Field(default_factory=list)


class SequenceCollectionDeleteResponse(BaseModel):
    ok: bool = True
    collection_id: str
    deleted: bool = True


class SequencePlanAndRenderStatusSummary(BaseModel):
    total_jobs: int = 0
    by_status: Dict[str, int] = Field(default_factory=dict)
    terminal_jobs: int = 0


class SequencePlanAndRenderCollectionRef(BaseModel):
    collection_id: str
    name: str
    is_highlighted: bool = False
    is_best: bool = False
    added_at: str


class SequencePlanAndRenderReviewHistorySummary(BaseModel):
    history_count: int = 0
    latest_created_at: Optional[str] = None


class SequencePlanAndRenderReviewHistoryEntry(BaseModel):
    history_id: str
    request_id: str
    previous_review_status: Literal["pending_review", "approved", "rejected"] = "pending_review"
    new_review_status: Literal["pending_review", "approved", "rejected"] = "pending_review"
    review_note: str = ""
    created_at: str


class SequencePromptComparisonEntry(BaseModel):
    request_id: str
    shot_id: str
    job_id: str
    retry_index: int = 0
    prompt_base: str = ""
    prompt_enriched: str = ""
    semantic_summary_used: Optional[str] = None
    semantic_enrichment_applied: bool = False
    source: str = "initial"


class SequencePromptComparisonMetrics(BaseModel):
    total: int = 0
    enriched: int = 0
    not_enriched: int = 0
    retries: int = 0
    enrichment_ratio: float = 0.0
    unique_shots: int = 0
    shots_with_retries: int = 0
    shots_with_enrichment: int = 0
    sources: Dict[str, int] = Field(default_factory=dict)


class SequencePlanAndRenderResponse(BaseModel):
    ok: bool = True
    request_id: str
    request_payload: Dict[str, Any] = Field(default_factory=dict)
    plan: SequencePlanResponse
    prompt_comparisons: List[SequencePromptComparisonEntry] = Field(default_factory=list)
    prompt_comparison_metrics: SequencePromptComparisonMetrics = Field(default_factory=SequencePromptComparisonMetrics)
    created_jobs: List[RenderJobData] = Field(default_factory=list)
    job_count: int = 0
    job_ids: List[str] = Field(default_factory=list)
    shot_job_links: List[SequenceShotJobLink] = Field(default_factory=list)
    status_summary: SequencePlanAndRenderStatusSummary
    is_favorite: bool = False
    tags: List[str] = Field(default_factory=list)
    note: str = ""
    review_status: Literal["pending_review", "approved", "rejected"] = "pending_review"
    review_note: str = ""
    reviewed_at: Optional[str] = None
    review_history_summary: SequencePlanAndRenderReviewHistorySummary = Field(
        default_factory=SequencePlanAndRenderReviewHistorySummary
    )
    collections: List[SequencePlanAndRenderCollectionRef] = Field(default_factory=list)


class SequencePlanAndRenderRecentItem(BaseModel):
    request_id: str
    created_at: str
    updated_at: str
    sequence_summary: str
    job_count: int = 0
    success_ratio: float = 0.0
    total_retries: int = 0
    status_summary: SequencePlanAndRenderStatusSummary
    sequence_id: Optional[str] = None
    project_id: Optional[str] = None
    is_favorite: bool = False
    tags: List[str] = Field(default_factory=list)
    note: str = ""
    review_status: Literal["pending_review", "approved", "rejected"] = "pending_review"
    review_note: str = ""
    reviewed_at: Optional[str] = None
    ranking_score: Optional[float] = None
    ranking_reason: Optional[str] = None
    collection_candidate: bool = False
    collection_added_at: Optional[str] = None
    collection_best: bool = False


class SequencePlanAndRenderRecentListResponse(BaseModel):
    ok: bool = True
    executions: List[SequencePlanAndRenderRecentItem] = Field(default_factory=list)
    limit: int = 20
    count: int = 0


class SequencePlanAndRenderReviewHistoryResponse(BaseModel):
    ok: bool = True
    request_id: str
    history: List[SequencePlanAndRenderReviewHistoryEntry] = Field(default_factory=list)
    limit: int = 200
    count: int = 0


class SequenceCollectionReviewResponse(BaseModel):
    ok: bool = True
    collection: SequenceCollectionSummary
    executions: List[SequencePlanAndRenderRecentItem] = Field(default_factory=list)
    limit: int = 200
    count: int = 0
    summary: Dict[str, int] = Field(default_factory=dict)


class SequenceCollectionAuditSuccessRatioSummary(BaseModel):
    succeeded_jobs: int = 0
    total_jobs: int = 0
    ratio: float = 0.0


class SequenceCollectionAuditEditorialSummary(BaseModel):
    total_executions: int = 0
    approved_count: int = 0
    rejected_count: int = 0
    pending_review_count: int = 0
    favorite_count: int = 0
    executions_without_review: int = 0


class SequenceCollectionAuditOperationalSummary(BaseModel):
    total_jobs: int = 0
    total_retries: int = 0
    failed_count: int = 0
    timeout_count: int = 0
    success_ratio_summary: SequenceCollectionAuditSuccessRatioSummary = Field(
        default_factory=SequenceCollectionAuditSuccessRatioSummary
    )


class SequenceCollectionAuditSignal(BaseModel):
    code: str
    severity: Literal["info", "warning", "critical"] = "info"
    message: str


class SequenceCollectionAuditResponse(BaseModel):
    ok: bool = True
    collection_id: str
    total_executions: int = 0
    approved_count: int = 0
    rejected_count: int = 0
    pending_review_count: int = 0
    favorite_count: int = 0
    total_retries: int = 0
    total_jobs: int = 0
    timeout_count: int = 0
    failed_count: int = 0
    success_ratio_summary: SequenceCollectionAuditSuccessRatioSummary = Field(
        default_factory=SequenceCollectionAuditSuccessRatioSummary
    )
    best_request_id: Optional[str] = None
    executions_without_review: int = 0
    health_status: Literal["green", "yellow", "red"] = "green"
    alerts: List[str] = Field(default_factory=list)
    editorial_summary: SequenceCollectionAuditEditorialSummary = Field(
        default_factory=SequenceCollectionAuditEditorialSummary
    )
    operational_summary: SequenceCollectionAuditOperationalSummary = Field(
        default_factory=SequenceCollectionAuditOperationalSummary
    )
    signals: List[SequenceCollectionAuditSignal] = Field(default_factory=list)


class SequencePlanError(BaseModel):
    code: str
    message: str


class SequencePlanErrorResponse(BaseModel):
    ok: bool = False
    error: SequencePlanError
