import { api } from "./api";

import type {
  SequenceExecutionCollectionsDashboardResponse,
  SequenceExecutionCollectionAuditResponse,
  SequenceExecutionCollectionDeleteResponse,
  SequenceExecutionCollectionListResponse,
  SequenceExecutionWebhookCreateRequest,
  SequenceExecutionWebhookDeliveriesCompareResponse,
  SequenceExecutionWebhookDeliveryResponse,
  SequenceExecutionWebhookDeliveriesListResponse,
  SequenceExecutionWebhookDeliveriesProcessRetriesResponse,
  SequenceExecutionWebhookPreviewRequest,
  SequenceExecutionWebhookPreviewResponse,
  SequenceExecutionWebhookResponse,
  SequenceExecutionWebhookUpdateRequest,
  SequenceExecutionWebhooksDashboardResponse,
  SequenceExecutionWebhookHealthResponse,
  SequenceExecutionNotificationChannelCreateRequest,
  SequenceExecutionNotificationChannelDeliveriesListResponse,
  SequenceExecutionNotificationChannelDeliveryResponse,
  SequenceExecutionNotificationChannelDeliveriesProcessRetriesResponse,
  SequenceExecutionNotificationChannelResponse,
  SequenceExecutionNotificationChannelsListResponse,
  SequenceExecutionNotificationChannelUpdateRequest,
  SequenceExecutionAlertRoutingRuleCreateRequest,
  SequenceExecutionAlertRoutingRuleDeleteResponse,
  SequenceExecutionAlertRoutingRuleResponse,
  SequenceExecutionAlertRoutingRulesListResponse,
  SequenceExecutionAlertRoutingRuleUpdateRequest,
  SequenceExecutionWebhooksListResponse,
  SequenceExecutionNotificationPreferencesResponse,
  SequenceExecutionNotificationPreferencesUpdateRequest,
  SequenceExecutionNotificationResponse,
  SequenceExecutionNotificationsListResponse,
  SequenceExecutionCollectionResponse,
  SequenceExecutionCollectionReviewResponse,
  SequenceExecutionRecentFilters,
  SequenceExecutionMetaUpdateRequest,
  SequenceExecutionReviewHistoryResponse,
  SequenceExecutionReviewUpdateRequest,
  RetryShotRequest,
  RetryShotResponse,
  SequenceExecutionRecentListResponse,
  SequencePlanAndRenderExecution,
  SequencePlanAndRenderRequest,
} from "../types/sequenceExecution";


function normalizeOptionalText(value: string | undefined): string | undefined {
  if (value === undefined) {
    return undefined;
  }

  const trimmed = value.trim();
  return trimmed === "" ? undefined : trimmed;
}


function normalizeTags(value: string[] | undefined): string[] | undefined {
  if (!value) {
    return undefined;
  }

  const seen = new Set<string>();
  const normalized: string[] = [];
  for (const item of value) {
    if (typeof item !== "string") {
      continue;
    }
    const trimmed = item.trim();
    if (!trimmed) {
      continue;
    }
    const lowered = trimmed.toLowerCase();
    if (seen.has(lowered)) {
      continue;
    }
    seen.add(lowered);
    normalized.push(trimmed);
  }

  return normalized;
}


function normalizeCustomHeaders(
  value: Record<string, string> | undefined
): Record<string, string> | undefined {
  if (!value || typeof value !== "object") {
    return undefined;
  }

  const normalized: Record<string, string> = {};
  for (const [rawKey, rawValue] of Object.entries(value)) {
    if (typeof rawKey !== "string") {
      continue;
    }
    const key = rawKey.trim();
    if (!key) {
      continue;
    }

    const valueText = typeof rawValue === "string" ? rawValue.trim() : String(rawValue).trim();
    if (!valueText) {
      continue;
    }

    normalized[key] = valueText;
  }

  return normalized;
}


function normalizePayloadTemplate(
  value: Record<string, unknown> | undefined
): Record<string, unknown> | undefined {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return undefined;
  }

  const normalized: Record<string, unknown> = {};
  for (const [rawKey, rawValue] of Object.entries(value)) {
    if (typeof rawKey !== "string") {
      continue;
    }
    const key = rawKey.trim();
    if (!key) {
      continue;
    }
    normalized[key] = rawValue;
  }

  return Object.keys(normalized).length > 0 ? normalized : undefined;
}


export async function createSequencePlanAndRender(
  payload: SequencePlanAndRenderRequest
): Promise<SequencePlanAndRenderExecution> {
  const body: SequencePlanAndRenderRequest = {
    script_text: payload.script_text.trim(),
    project_id: normalizeOptionalText(payload.project_id),
    sequence_id: normalizeOptionalText(payload.sequence_id),
    style_profile: normalizeOptionalText(payload.style_profile),
    continuity_mode: normalizeOptionalText(payload.continuity_mode),
    semantic_prompt_enrichment_enabled:
      typeof payload.semantic_prompt_enrichment_enabled === "boolean"
        ? payload.semantic_prompt_enrichment_enabled
        : undefined,
    semantic_prompt_enrichment_max_chars:
      typeof payload.semantic_prompt_enrichment_max_chars === "number"
        ? Math.max(0, Math.min(Math.trunc(payload.semantic_prompt_enrichment_max_chars), 2000))
        : undefined,
  };

  const response = await api.post<SequencePlanAndRenderExecution>("/api/sequence/plan-and-render", body);
  return response.data;
}


export async function getSequencePlanAndRender(requestId: string): Promise<SequencePlanAndRenderExecution> {
  const normalizedRequestId = requestId.trim();
  const response = await api.get<SequencePlanAndRenderExecution>(
    `/api/sequence/plan-and-render/${encodeURIComponent(normalizedRequestId)}`
  );
  return response.data;
}


export async function retrySequenceShot(
  requestId: string,
  payload: RetryShotRequest
): Promise<RetryShotResponse> {
  const normalizedRequestId = requestId.trim();
  const body: RetryShotRequest = {
    shot_id: payload.shot_id.trim(),
    override_prompt: normalizeOptionalText(payload.override_prompt),
    override_negative_prompt: normalizeOptionalText(payload.override_negative_prompt),
    override_render_context: payload.override_render_context,
    reason: normalizeOptionalText(payload.reason),
  };

  const response = await api.post<RetryShotResponse>(
    `/api/sequence/plan-and-render/${encodeURIComponent(normalizedRequestId)}/retry-shot`,
    body
  );
  return response.data;
}


export async function listRecentSequenceExecutions(
  filters: SequenceExecutionRecentFilters = {}
): Promise<SequenceExecutionRecentListResponse> {
  const normalizedLimit = Math.max(1, Math.min(Math.trunc(filters.limit ?? 20), 200));
  const params = new URLSearchParams();
  params.set("limit", String(normalizedLimit));

  const q = normalizeOptionalText(filters.q);
  if (q) {
    params.set("q", q);
  }

  const projectId = normalizeOptionalText(filters.project_id);
  if (projectId) {
    params.set("project_id", projectId);
  }

  const sequenceId = normalizeOptionalText(filters.sequence_id);
  if (sequenceId) {
    params.set("sequence_id", sequenceId);
  }

  if (filters.status) {
    params.set("status", filters.status);
  }

  if (typeof filters.is_favorite === "boolean") {
    params.set("is_favorite", filters.is_favorite ? "true" : "false");
  }

  const tag = normalizeOptionalText(filters.tag);
  if (tag) {
    params.set("tag", tag);
  }

  if (filters.ranking) {
    params.set("ranking", filters.ranking);
  }

  const collectionId = normalizeOptionalText(filters.collection_id);
  if (collectionId) {
    params.set("collection_id", collectionId);
  }

  const response = await api.get<SequenceExecutionRecentListResponse>(
    `/api/sequence/plan-and-render?${params.toString()}`
  );
  return response.data;
}


export async function updateSequencePlanAndRenderMeta(
  requestId: string,
  payload: SequenceExecutionMetaUpdateRequest
): Promise<SequencePlanAndRenderExecution> {
  const normalizedRequestId = requestId.trim();
  const body: SequenceExecutionMetaUpdateRequest = {};

  if (typeof payload.is_favorite === "boolean") {
    body.is_favorite = payload.is_favorite;
  }

  if (payload.tags !== undefined) {
    body.tags = normalizeTags(payload.tags) ?? [];
  }

  if (payload.note !== undefined) {
    body.note = payload.note.trim();
  }

  const response = await api.patch<SequencePlanAndRenderExecution>(
    `/api/sequence/plan-and-render/${encodeURIComponent(normalizedRequestId)}/meta`,
    body
  );
  return response.data;
}


export async function updateSequencePlanAndRenderReview(
  requestId: string,
  payload: SequenceExecutionReviewUpdateRequest
): Promise<SequencePlanAndRenderExecution> {
  const normalizedRequestId = requestId.trim();
  const body: SequenceExecutionReviewUpdateRequest = {};

  if (payload.review_status !== undefined) {
    body.review_status = payload.review_status;
  }

  if (payload.review_note !== undefined) {
    body.review_note = payload.review_note.trim();
  }

  const response = await api.patch<SequencePlanAndRenderExecution>(
    `/api/sequence/plan-and-render/${encodeURIComponent(normalizedRequestId)}/review`,
    body
  );
  return response.data;
}


export async function getSequencePlanAndRenderReviewHistory(
  requestId: string,
  limit = 200
): Promise<SequenceExecutionReviewHistoryResponse> {
  const normalizedRequestId = requestId.trim();
  const normalizedLimit = Math.max(1, Math.min(Math.trunc(limit), 500));
  const response = await api.get<SequenceExecutionReviewHistoryResponse>(
    `/api/sequence/plan-and-render/${encodeURIComponent(normalizedRequestId)}/review-history?limit=${normalizedLimit}`
  );
  return response.data;
}


export async function createSequenceExecutionCollection(payload: {
  name: string;
  description?: string;
  editorial_note?: string;
  color?: string;
}): Promise<SequenceExecutionCollectionResponse> {
  const response = await api.post<SequenceExecutionCollectionResponse>("/api/sequence/collections", {
    name: payload.name.trim(),
    description: normalizeOptionalText(payload.description),
    editorial_note: normalizeOptionalText(payload.editorial_note),
    color: normalizeOptionalText(payload.color),
  });
  return response.data;
}


export async function listSequenceExecutionCollections(
  limit = 100,
  includeArchived = false
): Promise<SequenceExecutionCollectionListResponse> {
  const normalizedLimit = Math.max(1, Math.min(Math.trunc(limit), 500));
  const params = new URLSearchParams();
  params.set("limit", String(normalizedLimit));
  params.set("include_archived", includeArchived ? "true" : "false");

  const response = await api.get<SequenceExecutionCollectionListResponse>(
    `/api/sequence/collections?${params.toString()}`
  );
  return response.data;
}


export async function getSequenceExecutionCollectionsDashboard(
  params: {
    limit?: number;
    include_archived?: boolean;
    top_limit?: number;
  } = {}
): Promise<SequenceExecutionCollectionsDashboardResponse> {
  const query = new URLSearchParams();
  const normalizedLimit = Math.max(1, Math.min(Math.trunc(params.limit ?? 200), 500));
  const normalizedTopLimit = Math.max(1, Math.min(Math.trunc(params.top_limit ?? 5), 20));
  query.set("limit", String(normalizedLimit));
  query.set("top_limit", String(normalizedTopLimit));
  if (typeof params.include_archived === "boolean") {
    query.set("include_archived", params.include_archived ? "true" : "false");
  }

  const response = await api.get<SequenceExecutionCollectionsDashboardResponse>(
    `/api/sequence/collections/dashboard?${query.toString()}`
  );
  return response.data;
}


export async function listSequenceNotifications(
  params: {
    collection_id?: string;
    is_read?: boolean;
    limit?: number;
  } = {}
): Promise<SequenceExecutionNotificationsListResponse> {
  const query = new URLSearchParams();
  const normalizedLimit = Math.max(1, Math.min(Math.trunc(params.limit ?? 50), 200));
  query.set("limit", String(normalizedLimit));

  const collectionId = normalizeOptionalText(params.collection_id);
  if (collectionId) {
    query.set("collection_id", collectionId);
  }

  if (typeof params.is_read === "boolean") {
    query.set("is_read", params.is_read ? "true" : "false");
  }

  const response = await api.get<SequenceExecutionNotificationsListResponse>(
    `/api/sequence/notifications?${query.toString()}`
  );
  return response.data;
}


export async function markSequenceNotificationRead(
  notificationId: string,
  isRead = true
): Promise<SequenceExecutionNotificationResponse> {
  const response = await api.patch<SequenceExecutionNotificationResponse>(
    `/api/sequence/notifications/${encodeURIComponent(notificationId.trim())}/read`,
    { is_read: isRead }
  );
  return response.data;
}


export async function getSequenceNotificationPreferences(): Promise<SequenceExecutionNotificationPreferencesResponse> {
  const response = await api.get<SequenceExecutionNotificationPreferencesResponse>(
    "/api/sequence/notification-preferences"
  );
  return response.data;
}


export async function updateSequenceNotificationPreferences(
  payload: SequenceExecutionNotificationPreferencesUpdateRequest
): Promise<SequenceExecutionNotificationPreferencesResponse> {
  const body: SequenceExecutionNotificationPreferencesUpdateRequest = {};

  if (typeof payload.notifications_enabled === "boolean") {
    body.notifications_enabled = payload.notifications_enabled;
  }
  if (payload.min_severity !== undefined) {
    body.min_severity = payload.min_severity;
  }
  if (payload.enabled_types !== undefined) {
    body.enabled_types = payload.enabled_types
      .filter((item) => typeof item === "string")
      .map((item) => item.trim())
      .filter((item) => item !== "");
  }
  if (typeof payload.show_only_unread_by_default === "boolean") {
    body.show_only_unread_by_default = payload.show_only_unread_by_default;
  }

  const response = await api.patch<SequenceExecutionNotificationPreferencesResponse>(
    "/api/sequence/notification-preferences",
    body
  );
  return response.data;
}


export async function listSequenceNotificationWebhooks(
  params: {
    limit?: number;
    include_disabled?: boolean;
  } = {}
): Promise<SequenceExecutionWebhooksListResponse> {
  const query = new URLSearchParams();
  const normalizedLimit = Math.max(1, Math.min(Math.trunc(params.limit ?? 100), 500));
  query.set("limit", String(normalizedLimit));
  query.set("include_disabled", params.include_disabled === false ? "false" : "true");

  const response = await api.get<SequenceExecutionWebhooksListResponse>(
    `/api/sequence/webhooks?${query.toString()}`
  );
  return response.data;
}


export async function getSequenceWebhooksDashboard(
  params: {
    top_limit?: number;
    errors_limit?: number;
  } = {}
): Promise<SequenceExecutionWebhooksDashboardResponse> {
  const query = new URLSearchParams();
  const normalizedTopLimit = Math.max(1, Math.min(Math.trunc(params.top_limit ?? 5), 20));
  const normalizedErrorsLimit = Math.max(1, Math.min(Math.trunc(params.errors_limit ?? 10), 50));
  query.set("top_limit", String(normalizedTopLimit));
  query.set("errors_limit", String(normalizedErrorsLimit));

  const response = await api.get<SequenceExecutionWebhooksDashboardResponse>(
    `/api/sequence/webhooks/dashboard?${query.toString()}`
  );
  return response.data;
}


export async function getSequenceWebhookHealth(
  webhookId: string,
  params: {
    recent_limit?: number;
    signals_limit?: number;
  } = {}
): Promise<SequenceExecutionWebhookHealthResponse> {
  const normalizedWebhookId = webhookId.trim();
  const query = new URLSearchParams();
  const normalizedRecentLimit = Math.max(5, Math.min(Math.trunc(params.recent_limit ?? 30), 200));
  const normalizedSignalsLimit = Math.max(1, Math.min(Math.trunc(params.signals_limit ?? 10), 50));
  query.set("recent_limit", String(normalizedRecentLimit));
  query.set("signals_limit", String(normalizedSignalsLimit));

  const response = await api.get<SequenceExecutionWebhookHealthResponse>(
    `/api/sequence/webhooks/${encodeURIComponent(normalizedWebhookId)}/health?${query.toString()}`
  );
  return response.data;
}


export async function createSequenceNotificationWebhook(
  payload: SequenceExecutionWebhookCreateRequest
): Promise<SequenceExecutionWebhookResponse> {
  const body: SequenceExecutionWebhookCreateRequest = {
    name: payload.name.trim(),
    url: payload.url.trim(),
    is_enabled: payload.is_enabled ?? true,
    auth_mode: payload.auth_mode ?? "none",
    secret_token: payload.secret_token?.trim(),
    min_severity: payload.min_severity ?? "info",
    enabled_types: (payload.enabled_types ?? [])
      .filter((item) => typeof item === "string")
      .map((item) => item.trim())
      .filter((item) => item !== ""),
    custom_headers: normalizeCustomHeaders(payload.custom_headers) ?? {},
    payload_template_mode: payload.payload_template_mode ?? "default",
    payload_template: normalizePayloadTemplate(payload.payload_template),
  };

  const response = await api.post<SequenceExecutionWebhookResponse>("/api/sequence/webhooks", body);
  return response.data;
}


export async function updateSequenceNotificationWebhook(
  webhookId: string,
  payload: SequenceExecutionWebhookUpdateRequest
): Promise<SequenceExecutionWebhookResponse> {
  const body: SequenceExecutionWebhookUpdateRequest = {};

  if (payload.name !== undefined) {
    body.name = payload.name.trim();
  }
  if (payload.url !== undefined) {
    body.url = payload.url.trim();
  }
  if (typeof payload.is_enabled === "boolean") {
    body.is_enabled = payload.is_enabled;
  }
  if (payload.auth_mode !== undefined) {
    body.auth_mode = payload.auth_mode;
  }
  if (payload.secret_token !== undefined) {
    body.secret_token = payload.secret_token.trim();
  }
  if (payload.min_severity !== undefined) {
    body.min_severity = payload.min_severity;
  }
  if (payload.enabled_types !== undefined) {
    body.enabled_types = payload.enabled_types
      .filter((item) => typeof item === "string")
      .map((item) => item.trim())
      .filter((item) => item !== "");
  }
  if (payload.custom_headers !== undefined) {
    body.custom_headers = normalizeCustomHeaders(payload.custom_headers) ?? {};
  }
  if (payload.payload_template_mode !== undefined) {
    body.payload_template_mode = payload.payload_template_mode;
  }
  if (payload.payload_template !== undefined) {
    body.payload_template = normalizePayloadTemplate(payload.payload_template);
  }

  const response = await api.patch<SequenceExecutionWebhookResponse>(
    `/api/sequence/webhooks/${encodeURIComponent(webhookId.trim())}`,
    body
  );
  return response.data;
}


export async function listSequenceWebhookDeliveries(
  params: {
    webhook_id?: string;
    collection_id?: string;
    notification_id?: string;
    is_test?: boolean;
    limit?: number;
  } = {}
): Promise<SequenceExecutionWebhookDeliveriesListResponse> {
  const query = new URLSearchParams();
  const normalizedLimit = Math.max(1, Math.min(Math.trunc(params.limit ?? 100), 500));
  query.set("limit", String(normalizedLimit));

  const webhookId = normalizeOptionalText(params.webhook_id);
  if (webhookId) {
    query.set("webhook_id", webhookId);
  }

  const collectionId = normalizeOptionalText(params.collection_id);
  if (collectionId) {
    query.set("collection_id", collectionId);
  }

  const notificationId = normalizeOptionalText(params.notification_id);
  if (notificationId) {
    query.set("notification_id", notificationId);
  }

  if (typeof params.is_test === "boolean") {
    query.set("is_test", params.is_test ? "true" : "false");
  }

  const response = await api.get<SequenceExecutionWebhookDeliveriesListResponse>(
    `/api/sequence/webhook-deliveries?${query.toString()}`
  );
  return response.data;
}


export async function retrySequenceWebhookDelivery(
  deliveryId: string
): Promise<SequenceExecutionWebhookDeliveryResponse> {
  const response = await api.post<SequenceExecutionWebhookDeliveryResponse>(
    `/api/sequence/webhook-deliveries/${encodeURIComponent(deliveryId.trim())}/retry`
  );
  return response.data;
}


export async function sendSequenceWebhookTestEvent(
  webhookId: string
): Promise<SequenceExecutionWebhookDeliveryResponse> {
  const response = await api.post<SequenceExecutionWebhookDeliveryResponse>(
    `/api/sequence/webhooks/${encodeURIComponent(webhookId.trim())}/test`
  );
  return response.data;
}


export async function previewSequenceWebhookPayload(
  webhookId: string,
  payload: SequenceExecutionWebhookPreviewRequest = {}
): Promise<SequenceExecutionWebhookPreviewResponse> {
  const body: SequenceExecutionWebhookPreviewRequest = {
    event_type: normalizeOptionalText(payload.event_type),
    sample_data:
      payload.sample_data && typeof payload.sample_data === "object" && !Array.isArray(payload.sample_data)
        ? payload.sample_data
        : undefined,
  };

  const response = await api.post<SequenceExecutionWebhookPreviewResponse>(
    `/api/sequence/webhooks/${encodeURIComponent(webhookId.trim())}/preview`,
    body
  );
  return response.data;
}


export async function compareSequenceWebhookDeliveries(
  leftDeliveryId: string,
  rightDeliveryId: string
): Promise<SequenceExecutionWebhookDeliveriesCompareResponse> {
  const leftId = leftDeliveryId.trim();
  const rightId = rightDeliveryId.trim();
  const query = new URLSearchParams();
  query.set("left_delivery_id", leftId);
  query.set("right_delivery_id", rightId);

  const response = await api.get<SequenceExecutionWebhookDeliveriesCompareResponse>(
    `/api/sequence/webhook-deliveries/compare?${query.toString()}`
  );
  return response.data;
}


export async function processSequenceWebhookDeliveryRetries(
  params: {
    webhook_id?: string;
    collection_id?: string;
    limit?: number;
  } = {}
): Promise<SequenceExecutionWebhookDeliveriesProcessRetriesResponse> {
  const query = new URLSearchParams();
  const normalizedLimit = Math.max(1, Math.min(Math.trunc(params.limit ?? 100), 500));
  query.set("limit", String(normalizedLimit));

  const webhookId = normalizeOptionalText(params.webhook_id);
  if (webhookId) {
    query.set("webhook_id", webhookId);
  }

  const collectionId = normalizeOptionalText(params.collection_id);
  if (collectionId) {
    query.set("collection_id", collectionId);
  }

  const response = await api.post<SequenceExecutionWebhookDeliveriesProcessRetriesResponse>(
    `/api/sequence/webhook-deliveries/process-retries?${query.toString()}`
  );
  return response.data;
}


export async function listSequenceNotificationChannels(
  params: {
    limit?: number;
    include_disabled?: boolean;
    channel_type?: "webhook" | "slack" | "telegram";
  } = {}
): Promise<SequenceExecutionNotificationChannelsListResponse> {
  const query = new URLSearchParams();
  const normalizedLimit = Math.max(1, Math.min(Math.trunc(params.limit ?? 100), 500));
  query.set("limit", String(normalizedLimit));
  query.set("include_disabled", params.include_disabled === false ? "false" : "true");
  if (params.channel_type) {
    query.set("channel_type", params.channel_type);
  }

  const response = await api.get<SequenceExecutionNotificationChannelsListResponse>(
    `/api/sequence/notification-channels?${query.toString()}`
  );
  return response.data;
}


export async function createSequenceNotificationChannel(
  payload: SequenceExecutionNotificationChannelCreateRequest
): Promise<SequenceExecutionNotificationChannelResponse> {
  const body: SequenceExecutionNotificationChannelCreateRequest = {
    channel_type: payload.channel_type,
    name: payload.name.trim(),
    is_enabled: payload.is_enabled ?? true,
    config:
      payload.config && typeof payload.config === "object" && !Array.isArray(payload.config)
        ? payload.config
        : {},
    min_severity: payload.min_severity ?? "info",
    enabled_types: (payload.enabled_types ?? [])
      .filter((item) => typeof item === "string")
      .map((item) => item.trim())
      .filter((item) => item !== ""),
  };

  const response = await api.post<SequenceExecutionNotificationChannelResponse>(
    "/api/sequence/notification-channels",
    body
  );
  return response.data;
}


export async function updateSequenceNotificationChannel(
  channelId: string,
  payload: SequenceExecutionNotificationChannelUpdateRequest
): Promise<SequenceExecutionNotificationChannelResponse> {
  const body: SequenceExecutionNotificationChannelUpdateRequest = {};
  if (payload.name !== undefined) {
    body.name = payload.name.trim();
  }
  if (typeof payload.is_enabled === "boolean") {
    body.is_enabled = payload.is_enabled;
  }
  if (payload.config !== undefined) {
    body.config =
      payload.config && typeof payload.config === "object" && !Array.isArray(payload.config)
        ? payload.config
        : {};
  }
  if (payload.min_severity !== undefined) {
    body.min_severity = payload.min_severity;
  }
  if (payload.enabled_types !== undefined) {
    body.enabled_types = payload.enabled_types
      .filter((item) => typeof item === "string")
      .map((item) => item.trim())
      .filter((item) => item !== "");
  }

  const response = await api.patch<SequenceExecutionNotificationChannelResponse>(
    `/api/sequence/notification-channels/${encodeURIComponent(channelId.trim())}`,
    body
  );
  return response.data;
}


export async function sendSequenceNotificationChannelTestEvent(
  channelId: string
): Promise<SequenceExecutionNotificationChannelDeliveryResponse> {
  const response = await api.post<SequenceExecutionNotificationChannelDeliveryResponse>(
    `/api/sequence/notification-channels/${encodeURIComponent(channelId.trim())}/test`
  );
  return response.data;
}


export async function listSequenceNotificationChannelDeliveries(
  params: {
    channel_id?: string;
    collection_id?: string;
    notification_id?: string;
    channel_type?: "webhook" | "slack" | "telegram";
    is_test?: boolean;
    limit?: number;
  } = {}
): Promise<SequenceExecutionNotificationChannelDeliveriesListResponse> {
  const query = new URLSearchParams();
  const normalizedLimit = Math.max(1, Math.min(Math.trunc(params.limit ?? 100), 500));
  query.set("limit", String(normalizedLimit));

  const channelId = normalizeOptionalText(params.channel_id);
  if (channelId) {
    query.set("channel_id", channelId);
  }

  const collectionId = normalizeOptionalText(params.collection_id);
  if (collectionId) {
    query.set("collection_id", collectionId);
  }

  const notificationId = normalizeOptionalText(params.notification_id);
  if (notificationId) {
    query.set("notification_id", notificationId);
  }

  if (params.channel_type) {
    query.set("channel_type", params.channel_type);
  }

  if (typeof params.is_test === "boolean") {
    query.set("is_test", params.is_test ? "true" : "false");
  }

  const response = await api.get<SequenceExecutionNotificationChannelDeliveriesListResponse>(
    `/api/sequence/notification-channel-deliveries?${query.toString()}`
  );
  return response.data;
}


export async function retrySequenceNotificationChannelDelivery(
  deliveryId: string
): Promise<SequenceExecutionNotificationChannelDeliveryResponse> {
  const response = await api.post<SequenceExecutionNotificationChannelDeliveryResponse>(
    `/api/sequence/notification-channel-deliveries/${encodeURIComponent(deliveryId.trim())}/retry`
  );
  return response.data;
}


export async function processSequenceNotificationChannelDeliveryRetries(
  params: {
    channel_id?: string;
    collection_id?: string;
    channel_type?: "webhook" | "slack" | "telegram";
    limit?: number;
  } = {}
): Promise<SequenceExecutionNotificationChannelDeliveriesProcessRetriesResponse> {
  const query = new URLSearchParams();
  const normalizedLimit = Math.max(1, Math.min(Math.trunc(params.limit ?? 100), 500));
  query.set("limit", String(normalizedLimit));

  const channelId = normalizeOptionalText(params.channel_id);
  if (channelId) {
    query.set("channel_id", channelId);
  }

  const collectionId = normalizeOptionalText(params.collection_id);
  if (collectionId) {
    query.set("collection_id", collectionId);
  }

  if (params.channel_type) {
    query.set("channel_type", params.channel_type);
  }

  const response = await api.post<SequenceExecutionNotificationChannelDeliveriesProcessRetriesResponse>(
    `/api/sequence/notification-channel-deliveries/process-retries?${query.toString()}`
  );
  return response.data;
}


export async function listSequenceAlertRoutingRules(
  params: {
    limit?: number;
    include_disabled?: boolean;
    target_channel_id?: string;
  } = {}
): Promise<SequenceExecutionAlertRoutingRulesListResponse> {
  const query = new URLSearchParams();
  const normalizedLimit = Math.max(1, Math.min(Math.trunc(params.limit ?? 100), 500));
  query.set("limit", String(normalizedLimit));
  query.set("include_disabled", params.include_disabled === false ? "false" : "true");

  const targetChannelId = normalizeOptionalText(params.target_channel_id);
  if (targetChannelId) {
    query.set("target_channel_id", targetChannelId);
  }

  const response = await api.get<SequenceExecutionAlertRoutingRulesListResponse>(
    `/api/sequence/alert-routing-rules?${query.toString()}`
  );
  return response.data;
}


export async function createSequenceAlertRoutingRule(
  payload: SequenceExecutionAlertRoutingRuleCreateRequest
): Promise<SequenceExecutionAlertRoutingRuleResponse> {
  const body: SequenceExecutionAlertRoutingRuleCreateRequest = {
    name: payload.name.trim(),
    is_enabled: payload.is_enabled ?? true,
    target_channel_id: payload.target_channel_id.trim(),
    target_channel_kind: payload.target_channel_kind,
    match_types: (payload.match_types ?? [])
      .filter((item) => typeof item === "string")
      .map((item) => item.trim())
      .filter((item) => item !== ""),
    min_severity: payload.min_severity ?? "info",
    match_collection_id: normalizeOptionalText(payload.match_collection_id),
    match_health_status: payload.match_health_status,
  };

  const response = await api.post<SequenceExecutionAlertRoutingRuleResponse>(
    "/api/sequence/alert-routing-rules",
    body
  );
  return response.data;
}


export async function updateSequenceAlertRoutingRule(
  ruleId: string,
  payload: SequenceExecutionAlertRoutingRuleUpdateRequest
): Promise<SequenceExecutionAlertRoutingRuleResponse> {
  const body: SequenceExecutionAlertRoutingRuleUpdateRequest = {};
  if (payload.name !== undefined) {
    body.name = payload.name.trim();
  }
  if (typeof payload.is_enabled === "boolean") {
    body.is_enabled = payload.is_enabled;
  }
  if (payload.target_channel_id !== undefined) {
    body.target_channel_id = payload.target_channel_id.trim();
  }
  if (payload.target_channel_kind !== undefined) {
    body.target_channel_kind = payload.target_channel_kind;
  }
  if (payload.match_types !== undefined) {
    body.match_types = payload.match_types
      .filter((item) => typeof item === "string")
      .map((item) => item.trim())
      .filter((item) => item !== "");
  }
  if (payload.min_severity !== undefined) {
    body.min_severity = payload.min_severity;
  }
  if (payload.match_collection_id !== undefined) {
    body.match_collection_id = payload.match_collection_id.trim();
  }
  if (payload.match_health_status !== undefined) {
    body.match_health_status = payload.match_health_status;
  }

  const response = await api.patch<SequenceExecutionAlertRoutingRuleResponse>(
    `/api/sequence/alert-routing-rules/${encodeURIComponent(ruleId.trim())}`,
    body
  );
  return response.data;
}


export async function deleteSequenceAlertRoutingRule(
  ruleId: string
): Promise<SequenceExecutionAlertRoutingRuleDeleteResponse> {
  const response = await api.delete<SequenceExecutionAlertRoutingRuleDeleteResponse>(
    `/api/sequence/alert-routing-rules/${encodeURIComponent(ruleId.trim())}`
  );
  return response.data;
}


export async function getSequenceExecutionCollection(
  collectionId: string
): Promise<SequenceExecutionCollectionResponse> {
  const response = await api.get<SequenceExecutionCollectionResponse>(
    `/api/sequence/collections/${encodeURIComponent(collectionId.trim())}`
  );
  return response.data;
}


export async function updateSequenceExecutionCollection(
  collectionId: string,
  payload: {
    name?: string;
    description?: string;
    editorial_note?: string;
    color?: string;
    is_archived?: boolean;
  }
): Promise<SequenceExecutionCollectionResponse> {
  const body: Record<string, unknown> = {};
  if (payload.name !== undefined) {
    body.name = payload.name.trim();
  }
  if (payload.description !== undefined) {
    body.description = payload.description.trim();
  }
  if (payload.editorial_note !== undefined) {
    body.editorial_note = payload.editorial_note.trim();
  }
  if (payload.color !== undefined) {
    body.color = payload.color.trim();
  }
  if (payload.is_archived !== undefined) {
    body.is_archived = payload.is_archived;
  }

  const response = await api.patch<SequenceExecutionCollectionResponse>(
    `/api/sequence/collections/${encodeURIComponent(collectionId.trim())}`,
    body
  );
  return response.data;
}


export async function deleteSequenceExecutionCollection(
  collectionId: string
): Promise<SequenceExecutionCollectionDeleteResponse> {
  const response = await api.delete<SequenceExecutionCollectionDeleteResponse>(
    `/api/sequence/collections/${encodeURIComponent(collectionId.trim())}`
  );
  return response.data;
}


export async function addSequenceExecutionCollectionItems(
  collectionId: string,
  requestIds: string[]
): Promise<SequenceExecutionCollectionResponse> {
  const response = await api.post<SequenceExecutionCollectionResponse>(
    `/api/sequence/collections/${encodeURIComponent(collectionId.trim())}/items`,
    { request_ids: requestIds.map((item) => item.trim()).filter((item) => item !== "") }
  );
  return response.data;
}


export async function removeSequenceExecutionCollectionItem(
  collectionId: string,
  requestId: string
): Promise<SequenceExecutionCollectionResponse> {
  const response = await api.delete<SequenceExecutionCollectionResponse>(
    `/api/sequence/collections/${encodeURIComponent(collectionId.trim())}/items/${encodeURIComponent(requestId.trim())}`
  );
  return response.data;
}


export async function setSequenceExecutionCollectionItemHighlight(
  collectionId: string,
  requestId: string,
  isHighlighted: boolean
): Promise<SequenceExecutionCollectionResponse> {
  const response = await api.patch<SequenceExecutionCollectionResponse>(
    `/api/sequence/collections/${encodeURIComponent(collectionId.trim())}/items/${encodeURIComponent(requestId.trim())}/highlight`,
    { is_highlighted: isHighlighted }
  );
  return response.data;
}


export async function setSequenceExecutionCollectionBest(
  collectionId: string,
  requestId: string | null
): Promise<SequenceExecutionCollectionResponse> {
  const response = await api.patch<SequenceExecutionCollectionResponse>(
    `/api/sequence/collections/${encodeURIComponent(collectionId.trim())}/best`,
    {
      request_id: requestId && requestId.trim() !== "" ? requestId.trim() : null,
    }
  );
  return response.data;
}


export async function getSequenceExecutionCollectionReview(
  collectionId: string,
  params: {
    ranking?: "most_stable" | "most_problematic" | "most_retries" | "highest_success_ratio";
    limit?: number;
  } = {}
): Promise<SequenceExecutionCollectionReviewResponse> {
  const query = new URLSearchParams();
  const normalizedLimit = Math.max(1, Math.min(Math.trunc(params.limit ?? 200), 500));
  query.set("limit", String(normalizedLimit));
  if (params.ranking) {
    query.set("ranking", params.ranking);
  }

  const response = await api.get<SequenceExecutionCollectionReviewResponse>(
    `/api/sequence/collections/${encodeURIComponent(collectionId.trim())}/review?${query.toString()}`
  );
  return response.data;
}


export async function getSequenceExecutionCollectionAudit(
  collectionId: string
): Promise<SequenceExecutionCollectionAuditResponse> {
  const response = await api.get<SequenceExecutionCollectionAuditResponse>(
    `/api/sequence/collections/${encodeURIComponent(collectionId.trim())}/audit`
  );
  return response.data;
}
