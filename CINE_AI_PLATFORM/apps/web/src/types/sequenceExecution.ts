export type RenderJobStatus = "queued" | "running" | "succeeded" | "failed" | "timeout" | string;

export interface SequencePlanAndRenderRequest {
  script_text: string;
  project_id?: string;
  sequence_id?: string;
  style_profile?: string;
  continuity_mode?: string;
  semantic_prompt_enrichment_enabled?: boolean;
  semantic_prompt_enrichment_max_chars?: number;
}

export interface SequenceShotPlan {
  shot_id: string;
  beat_id: string;
  index: number;
  shot_type: string;
  camera: string;
  motion: string;
  prompt: string;
  prompt_base: string;
  negative_prompt: string;
  continuity: string;
}

export interface SequencePlanSemanticContextError {
  code: string;
  message: string;
  details?: Record<string, unknown> | null;
}

export interface SequencePlanSemanticContextItem {
  point_id?: string | null;
  score?: number | null;
  project_id?: string | null;
  sequence_id?: string | null;
  scene_id?: string | null;
  shot_id?: string | null;
  entity_type?: string | null;
  title?: string | null;
  content?: string | null;
  content_excerpt?: string | null;
  tags: string[];
  source?: string | null;
  created_at?: string | null;
}

export interface SequencePlanSemanticContextQuery {
  text?: string | null;
  project_id?: string | null;
  sequence_id?: string | null;
  scene_id?: string | null;
  shot_id?: string | null;
  limit: number;
}

export interface SequencePlanSemanticContext {
  enabled: boolean;
  query: SequencePlanSemanticContextQuery;
  count: number;
  entity_types: string[];
  summary_text: string;
  continuity_hints: string[];
  items: SequencePlanSemanticContextItem[];
  error?: SequencePlanSemanticContextError | null;
}

export interface SequencePlanSemanticPromptEnrichment {
  enabled: boolean;
  max_chars: number;
}

export interface SequenceRenderPromptComparisonJob {
  shot_id: string;
  prompt_base: string;
  prompt_enriched: string;
  semantic_summary_used?: string | null;
  semantic_enrichment_applied: boolean;
  request_payload?: Record<string, unknown>;
  render_context?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface SequencePromptComparisonMetrics {
  total: number;
  enriched: number;
  not_enriched: number;
  retries: number;
  enrichment_ratio: number;
  unique_shots: number;
  shots_with_retries: number;
  shots_with_enrichment: number;
  sources: Record<string, number>;
}

export interface SequencePlanData {
  ok: boolean;
  sequence_summary: string;
  beats: Array<Record<string, unknown>>;
  shots: SequenceShotPlan[];
  characters_detected: string[];
  locations_detected: string[];
  continuity_notes: string[];
  semantic_context?: SequencePlanSemanticContext;
  semantic_prompt_enrichment?: SequencePlanSemanticPromptEnrichment;
  render_inputs: {
    target_endpoint: string;
    workflow_key: string;
    jobs: SequenceRenderPromptComparisonJob[];
  };
}

export interface RenderJobFailure {
  code: string;
  message: string;
  details?: Record<string, unknown> | null;
}

export interface RenderJobData {
  job_id: string;
  created_at: string;
  updated_at: string;
  status: RenderJobStatus;
  request_payload: Record<string, unknown>;
  parent_job_id?: string | null;
  comfyui_prompt_id?: string | null;
  result?: Record<string, unknown> | null;
  error?: RenderJobFailure | null;
  duration_ms?: number | null;
}

export interface SequenceShotJobLink {
  shot_id: string;
  job_id: string;
  request_id?: string | null;
  parent_job_id?: string | null;
  retry_index?: number | null;
  reason?: string | null;
}

export interface SequenceStatusSummary {
  total_jobs: number;
  by_status: Record<string, number>;
  terminal_jobs: number;
}

export type SequenceExecutionRecentStatus = "queued" | "running" | "succeeded" | "failed" | "timeout";
export type SequenceExecutionRecentRanking = "most_stable" | "most_problematic" | "most_retries" | "highest_success_ratio";
export type SequenceExecutionReviewStatus = "pending_review" | "approved" | "rejected";
export type SequenceCollectionHealthStatus = "green" | "yellow" | "red";
export type SequenceNotificationSeverity = "info" | "warning" | "critical";
export type SequenceWebhookAuthMode = "none" | "bearer" | "hmac_sha256";
export type SequenceWebhookPayloadTemplateMode = "default" | "compact" | "custom";

export interface SequenceExecutionRecentFilters {
  q?: string;
  project_id?: string;
  sequence_id?: string;
  status?: SequenceExecutionRecentStatus;
  is_favorite?: boolean;
  tag?: string;
  collection_id?: string;
  ranking?: SequenceExecutionRecentRanking;
  limit?: number;
}

export interface SequenceExecutionRecentItem {
  request_id: string;
  created_at: string;
  updated_at: string;
  sequence_summary: string;
  job_count: number;
  success_ratio: number;
  total_retries: number;
  status_summary: SequenceStatusSummary;
  sequence_id?: string | null;
  project_id?: string | null;
  is_favorite: boolean;
  tags: string[];
  note: string;
  review_status: SequenceExecutionReviewStatus;
  review_note: string;
  reviewed_at?: string | null;
  ranking_score?: number | null;
  ranking_reason?: string | null;
  collection_candidate?: boolean;
  collection_added_at?: string | null;
  collection_best?: boolean;
}

export interface SequenceExecutionRecentListResponse {
  ok: boolean;
  executions: SequenceExecutionRecentItem[];
  limit: number;
  count: number;
}

export interface SequencePlanAndRenderExecution {
  ok: boolean;
  request_id: string;
  request_payload: Record<string, unknown>;
  plan: SequencePlanData;
  prompt_comparisons?: SequenceRenderPromptComparisonJob[];
  prompt_comparison_metrics?: SequencePromptComparisonMetrics;
  created_jobs: RenderJobData[];
  job_count: number;
  job_ids: string[];
  shot_job_links: SequenceShotJobLink[];
  status_summary: SequenceStatusSummary;
  is_favorite: boolean;
  tags: string[];
  note: string;
  review_status: SequenceExecutionReviewStatus;
  review_note: string;
  reviewed_at?: string | null;
  review_history_summary: SequenceExecutionReviewHistorySummary;
  collections: SequenceExecutionCollectionMembership[];
}

export interface SequenceExecutionCollectionMembership {
  collection_id: string;
  name: string;
  is_highlighted: boolean;
  is_best: boolean;
  added_at: string;
}

export interface SequenceExecutionReviewHistorySummary {
  history_count: number;
  latest_created_at?: string | null;
}

export interface SequenceExecutionReviewHistoryEntry {
  history_id: string;
  request_id: string;
  previous_review_status: SequenceExecutionReviewStatus;
  new_review_status: SequenceExecutionReviewStatus;
  review_note: string;
  created_at: string;
}

export interface SequenceExecutionMetaUpdateRequest {
  is_favorite?: boolean;
  tags?: string[];
  note?: string;
}

export interface SequenceExecutionReviewUpdateRequest {
  review_status?: SequenceExecutionReviewStatus;
  review_note?: string;
}

export interface SequenceCollectionItem {
  collection_id: string;
  request_id: string;
  is_highlighted: boolean;
  added_at: string;
}

export interface SequenceExecutionCollection {
  collection_id: string;
  name: string;
  description: string;
  editorial_note: string;
  color: string;
  is_archived: boolean;
  best_request_id?: string | null;
  created_at: string;
  updated_at: string;
  item_count: number;
  highlighted_count: number;
  health_status: SequenceCollectionHealthStatus;
  alerts: string[];
  items: SequenceCollectionItem[];
}

export interface SequenceExecutionCollectionResponse {
  ok: boolean;
  collection: SequenceExecutionCollection;
}

export interface SequenceExecutionCollectionListResponse {
  ok: boolean;
  collections: SequenceExecutionCollection[];
  limit: number;
  count: number;
}

export interface SequenceExecutionCollectionsDashboardItem {
  collection_id: string;
  name: string;
  health_status: SequenceCollectionHealthStatus;
  alerts: string[];
  item_count: number;
  total_executions: number;
  total_retries: number;
  pending_review_count: number;
  best_request_id?: string | null;
  success_ratio: number;
  updated_at: string;
}

export interface SequenceExecutionCollectionsDashboardResponse {
  ok: boolean;
  total_collections: number;
  collections_green: number;
  collections_yellow: number;
  collections_red: number;
  top_collections_by_executions: SequenceExecutionCollectionsDashboardItem[];
  top_collections_by_retries: SequenceExecutionCollectionsDashboardItem[];
  collections_without_best_execution: SequenceExecutionCollectionsDashboardItem[];
  collections_with_pending_review: SequenceExecutionCollectionsDashboardItem[];
  highlighted_collections: SequenceExecutionCollectionsDashboardItem[];
}

export interface SequenceExecutionNotification {
  notification_id: string;
  collection_id: string;
  type: string;
  severity: SequenceNotificationSeverity;
  message: string;
  created_at: string;
  is_read: boolean;
}

export interface SequenceExecutionNotificationsListResponse {
  ok: boolean;
  notifications: SequenceExecutionNotification[];
  limit: number;
  count: number;
}

export interface SequenceExecutionNotificationResponse {
  ok: boolean;
  notification: SequenceExecutionNotification;
}

export interface SequenceExecutionNotificationPreferences {
  notifications_enabled: boolean;
  min_severity: SequenceNotificationSeverity;
  enabled_types: string[];
  show_only_unread_by_default: boolean;
  updated_at: string;
}

export interface SequenceExecutionNotificationPreferencesResponse {
  ok: boolean;
  preferences: SequenceExecutionNotificationPreferences;
}

export interface SequenceExecutionNotificationPreferencesUpdateRequest {
  notifications_enabled?: boolean;
  min_severity?: SequenceNotificationSeverity;
  enabled_types?: string[];
  show_only_unread_by_default?: boolean;
}

export interface SequenceExecutionWebhook {
  webhook_id: string;
  name: string;
  url: string;
  is_enabled: boolean;
  auth_mode: SequenceWebhookAuthMode;
  has_secret_token: boolean;
  min_severity: SequenceNotificationSeverity;
  enabled_types: string[];
  custom_headers: Record<string, string>;
  payload_template_mode: SequenceWebhookPayloadTemplateMode;
  payload_template?: Record<string, unknown> | null;
  health_status: SequenceCollectionHealthStatus;
  alerts: string[];
  created_at: string;
  updated_at: string;
}

export interface SequenceExecutionWebhooksListResponse {
  ok: boolean;
  webhooks: SequenceExecutionWebhook[];
  limit: number;
  count: number;
}

export interface SequenceExecutionWebhookResponse {
  ok: boolean;
  webhook: SequenceExecutionWebhook;
}

export interface SequenceExecutionWebhooksDashboardItem {
  webhook_id: string;
  name: string;
  is_enabled: boolean;
  health_status: SequenceCollectionHealthStatus;
  alerts: string[];
  total_deliveries: number;
  sent_deliveries: number;
  failed_deliveries: number;
  pending_deliveries: number;
  exhausted_deliveries: number;
  total_retries: number;
  failure_ratio: number;
  last_delivery_at?: string | null;
}

export interface SequenceExecutionWebhooksDashboardErrorItem {
  delivery_id: string;
  webhook_id: string;
  webhook_name: string;
  notification_id: string;
  collection_id: string;
  error_message: string;
  attempt_count: number;
  max_attempts: number;
  is_test: boolean;
  auth_mode: SequenceWebhookAuthMode;
  payload_template_mode: SequenceWebhookPayloadTemplateMode;
  created_at: string;
  last_attempt_at?: string | null;
}

export interface SequenceExecutionWebhooksDashboardAlertItem {
  webhook_id: string;
  name: string;
  health_status: SequenceCollectionHealthStatus;
  alerts: string[];
  failed_deliveries: number;
  exhausted_deliveries: number;
  failure_ratio: number;
}

export interface SequenceExecutionWebhooksDashboardResponse {
  ok: boolean;
  total_webhooks: number;
  active_webhooks: number;
  inactive_webhooks: number;
  webhooks_green: number;
  webhooks_yellow: number;
  webhooks_red: number;
  total_deliveries: number;
  sent_deliveries: number;
  failed_deliveries: number;
  pending_deliveries: number;
  top_webhooks_by_volume: SequenceExecutionWebhooksDashboardItem[];
  top_webhooks_by_failures: SequenceExecutionWebhooksDashboardItem[];
  top_webhooks_by_retries: SequenceExecutionWebhooksDashboardItem[];
  active_alerts: SequenceExecutionWebhooksDashboardAlertItem[];
  recent_delivery_errors: SequenceExecutionWebhooksDashboardErrorItem[];
}

export interface SequenceExecutionWebhookHealthSignal {
  code: string;
  severity: SequenceNotificationSeverity;
  message: string;
  observed_at?: string | null;
}

export interface SequenceExecutionWebhookOperationalSummary {
  total_deliveries: number;
  sent_deliveries: number;
  failed_deliveries: number;
  pending_deliveries: number;
  exhausted_deliveries: number;
  total_retries: number;
  failure_ratio: number;
  recent_deliveries: number;
  recent_failed_deliveries: number;
  last_delivery_at?: string | null;
  last_success_at?: string | null;
  last_failure_at?: string | null;
}

export interface SequenceExecutionWebhookHealthResponse {
  ok: boolean;
  webhook: SequenceExecutionWebhook;
  operational_summary: SequenceExecutionWebhookOperationalSummary;
  health_status: SequenceCollectionHealthStatus;
  alerts: string[];
  recent_signals: SequenceExecutionWebhookHealthSignal[];
}

export interface SequenceExecutionWebhookCreateRequest {
  name: string;
  url: string;
  is_enabled?: boolean;
  auth_mode?: SequenceWebhookAuthMode;
  secret_token?: string;
  min_severity?: SequenceNotificationSeverity;
  enabled_types?: string[];
  custom_headers?: Record<string, string>;
  payload_template_mode?: SequenceWebhookPayloadTemplateMode;
  payload_template?: Record<string, unknown>;
}

export interface SequenceExecutionWebhookUpdateRequest {
  name?: string;
  url?: string;
  is_enabled?: boolean;
  auth_mode?: SequenceWebhookAuthMode;
  secret_token?: string;
  min_severity?: SequenceNotificationSeverity;
  enabled_types?: string[];
  custom_headers?: Record<string, string>;
  payload_template_mode?: SequenceWebhookPayloadTemplateMode;
  payload_template?: Record<string, unknown>;
}

export interface SequenceExecutionWebhookPreviewRequest {
  event_type?: string;
  sample_data?: Record<string, unknown>;
}

export interface SequenceExecutionWebhookPreviewResponse {
  ok: boolean;
  webhook_id: string;
  auth_mode: SequenceWebhookAuthMode;
  payload_template_mode: SequenceWebhookPayloadTemplateMode;
  rendered_payload: Record<string, unknown>;
  rendered_headers: Record<string, string>;
  signature_preview?: string | null;
}

export interface SequenceExecutionWebhookStructuredDiff {
  added: Record<string, unknown>;
  removed: Record<string, unknown>;
  changed: Record<string, { left: unknown; right: unknown }>;
  unchanged_count: number;
}

export interface SequenceExecutionWebhookDeliveriesCompareResponse {
  ok: boolean;
  left_delivery_id: string;
  right_delivery_id: string;
  auth_mode_left: SequenceWebhookAuthMode;
  auth_mode_right: SequenceWebhookAuthMode;
  payload_template_mode_left: SequenceWebhookPayloadTemplateMode;
  payload_template_mode_right: SequenceWebhookPayloadTemplateMode;
  payload_diff: SequenceExecutionWebhookStructuredDiff;
  headers_diff: SequenceExecutionWebhookStructuredDiff;
}

export type SequenceWebhookDeliveryStatus = "pending" | "sent" | "failed";
export type SequenceNotificationChannelType = "webhook" | "slack" | "telegram";

export interface SequenceExecutionWebhookDelivery {
  delivery_id: string;
  webhook_id: string;
  notification_id: string;
  collection_id: string;
  routing_rule_id?: string | null;
  routing_rule_name?: string | null;
  payload: Record<string, unknown>;
  delivery_status: SequenceWebhookDeliveryStatus;
  attempt_count: number;
  max_attempts: number;
  last_attempt_at?: string | null;
  next_retry_at?: string | null;
  final_failure_at?: string | null;
  is_test: boolean;
  template_mode: SequenceWebhookPayloadTemplateMode;
  auth_mode: SequenceWebhookAuthMode;
  request_headers: Record<string, string>;
  signature_timestamp?: string | null;
  response_status_code?: number | null;
  response_body?: string | null;
  error_message?: string | null;
  created_at: string;
  delivered_at?: string | null;
}

export interface SequenceExecutionWebhookDeliveryResponse {
  ok: boolean;
  delivery: SequenceExecutionWebhookDelivery;
}

export interface SequenceExecutionWebhookDeliveriesListResponse {
  ok: boolean;
  deliveries: SequenceExecutionWebhookDelivery[];
  limit: number;
  count: number;
}

export interface SequenceExecutionWebhookDeliveriesProcessRetriesResponse {
  ok: boolean;
  processed_count: number;
  sent_count: number;
  failed_count: number;
  exhausted_count: number;
  deliveries: SequenceExecutionWebhookDelivery[];
}

export interface SequenceExecutionNotificationChannel {
  channel_id: string;
  channel_type: SequenceNotificationChannelType;
  name: string;
  is_enabled: boolean;
  config: Record<string, unknown>;
  min_severity: SequenceNotificationSeverity;
  enabled_types: string[];
  created_at: string;
  updated_at: string;
}

export interface SequenceExecutionNotificationChannelsListResponse {
  ok: boolean;
  channels: SequenceExecutionNotificationChannel[];
  limit: number;
  count: number;
}

export interface SequenceExecutionNotificationChannelResponse {
  ok: boolean;
  channel: SequenceExecutionNotificationChannel;
}

export interface SequenceExecutionNotificationChannelCreateRequest {
  channel_type: SequenceNotificationChannelType;
  name: string;
  is_enabled?: boolean;
  config?: Record<string, unknown>;
  min_severity?: SequenceNotificationSeverity;
  enabled_types?: string[];
}

export interface SequenceExecutionNotificationChannelUpdateRequest {
  name?: string;
  is_enabled?: boolean;
  config?: Record<string, unknown>;
  min_severity?: SequenceNotificationSeverity;
  enabled_types?: string[];
}

export interface SequenceExecutionNotificationChannelDelivery {
  delivery_id: string;
  channel_id: string;
  channel_type: SequenceNotificationChannelType;
  notification_id: string;
  collection_id: string;
  routing_rule_id?: string | null;
  routing_rule_name?: string | null;
  payload: Record<string, unknown>;
  message_text: string;
  delivery_status: SequenceWebhookDeliveryStatus;
  attempt_count: number;
  max_attempts: number;
  last_attempt_at?: string | null;
  next_retry_at?: string | null;
  final_failure_at?: string | null;
  is_test: boolean;
  response_status_code?: number | null;
  response_body?: string | null;
  error_message?: string | null;
  created_at: string;
  delivered_at?: string | null;
}

export interface SequenceExecutionNotificationChannelDeliveryResponse {
  ok: boolean;
  delivery: SequenceExecutionNotificationChannelDelivery;
}

export interface SequenceExecutionNotificationChannelDeliveriesListResponse {
  ok: boolean;
  deliveries: SequenceExecutionNotificationChannelDelivery[];
  limit: number;
  count: number;
}

export interface SequenceExecutionNotificationChannelDeliveriesProcessRetriesResponse {
  ok: boolean;
  processed_count: number;
  sent_count: number;
  failed_count: number;
  exhausted_count: number;
  deliveries: SequenceExecutionNotificationChannelDelivery[];
}

export interface SequenceExecutionAlertRoutingRule {
  rule_id: string;
  name: string;
  is_enabled: boolean;
  target_channel_id: string;
  target_channel_kind: "notification_channel" | "webhook";
  target_name?: string | null;
  target_channel_type?: string | null;
  target_exists: boolean;
  match_types: string[];
  min_severity: SequenceNotificationSeverity;
  match_collection_id?: string | null;
  match_health_status?: "green" | "yellow" | "red" | null;
  created_at: string;
  updated_at: string;
}

export interface SequenceExecutionAlertRoutingRulesListResponse {
  ok: boolean;
  rules: SequenceExecutionAlertRoutingRule[];
  limit: number;
  count: number;
}

export interface SequenceExecutionAlertRoutingRuleResponse {
  ok: boolean;
  rule: SequenceExecutionAlertRoutingRule;
}

export interface SequenceExecutionAlertRoutingRuleCreateRequest {
  name: string;
  is_enabled?: boolean;
  target_channel_id: string;
  target_channel_kind?: "notification_channel" | "webhook";
  match_types?: string[];
  min_severity?: SequenceNotificationSeverity;
  match_collection_id?: string;
  match_health_status?: "green" | "yellow" | "red";
}

export interface SequenceExecutionAlertRoutingRuleUpdateRequest {
  name?: string;
  is_enabled?: boolean;
  target_channel_id?: string;
  target_channel_kind?: "notification_channel" | "webhook";
  match_types?: string[];
  min_severity?: SequenceNotificationSeverity;
  match_collection_id?: string;
  match_health_status?: "green" | "yellow" | "red";
}

export interface SequenceExecutionAlertRoutingRuleDeleteResponse {
  ok: boolean;
  rule_id: string;
  deleted: boolean;
}

export interface SequenceExecutionCollectionDeleteResponse {
  ok: boolean;
  collection_id: string;
  deleted: boolean;
}

export interface SequenceExecutionCollectionReviewResponse {
  ok: boolean;
  collection: SequenceExecutionCollection;
  executions: SequenceExecutionRecentItem[];
  limit: number;
  count: number;
  summary: Record<string, number>;
}

export interface SequenceExecutionCollectionAuditSuccessRatioSummary {
  succeeded_jobs: number;
  total_jobs: number;
  ratio: number;
}

export interface SequenceExecutionCollectionAuditEditorialSummary {
  total_executions: number;
  approved_count: number;
  rejected_count: number;
  pending_review_count: number;
  favorite_count: number;
  executions_without_review: number;
}

export interface SequenceExecutionCollectionAuditOperationalSummary {
  total_jobs: number;
  total_retries: number;
  failed_count: number;
  timeout_count: number;
  success_ratio_summary: SequenceExecutionCollectionAuditSuccessRatioSummary;
}

export interface SequenceExecutionCollectionAuditSignal {
  code: string;
  severity: "info" | "warning" | "critical";
  message: string;
}

export interface SequenceExecutionCollectionAuditResponse {
  ok: boolean;
  collection_id: string;
  total_executions: number;
  approved_count: number;
  rejected_count: number;
  pending_review_count: number;
  favorite_count: number;
  total_retries: number;
  total_jobs: number;
  timeout_count: number;
  failed_count: number;
  success_ratio_summary: SequenceExecutionCollectionAuditSuccessRatioSummary;
  best_request_id?: string | null;
  executions_without_review: number;
  health_status: SequenceCollectionHealthStatus;
  alerts: string[];
  editorial_summary: SequenceExecutionCollectionAuditEditorialSummary;
  operational_summary: SequenceExecutionCollectionAuditOperationalSummary;
  signals: SequenceExecutionCollectionAuditSignal[];
}

export interface SequenceExecutionReviewHistoryResponse {
  ok: boolean;
  request_id: string;
  history: SequenceExecutionReviewHistoryEntry[];
  limit: number;
  count: number;
}

export interface RetryShotRequest {
  shot_id: string;
  override_prompt?: string;
  override_negative_prompt?: string;
  override_render_context?: Record<string, unknown>;
  reason?: string;
}

export interface RetryShotResponse {
  ok: boolean;
  request_id: string;
  shot_id: string;
  parent_job_id: string;
  new_job_id: string;
  retry_index: number;
  status: RenderJobStatus;
}
