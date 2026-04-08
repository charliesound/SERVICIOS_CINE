import { useCallback, useEffect, useMemo, useState, type CSSProperties } from "react";

import {
  createSequenceAlertRoutingRule,
  createSequenceNotificationChannel,
  compareSequenceWebhookDeliveries,
  createSequenceNotificationWebhook,
  deleteSequenceAlertRoutingRule,
  getSequenceWebhookHealth,
  getSequenceWebhooksDashboard,
  listSequenceAlertRoutingRules,
  listSequenceNotificationChannelDeliveries,
  listSequenceNotificationChannels,
  listSequenceNotificationWebhooks,
  listSequenceWebhookDeliveries,
  processSequenceNotificationChannelDeliveryRetries,
  previewSequenceWebhookPayload,
  processSequenceWebhookDeliveryRetries,
  retrySequenceNotificationChannelDelivery,
  sendSequenceNotificationChannelTestEvent,
  sendSequenceWebhookTestEvent,
  retrySequenceWebhookDelivery,
  updateSequenceAlertRoutingRule,
  updateSequenceNotificationChannel,
  updateSequenceNotificationWebhook,
} from "../services/sequenceApi";
import type {
  SequenceExecutionAlertRoutingRule,
  SequenceNotificationChannelType,
  SequenceWebhookAuthMode,
  SequenceWebhookPayloadTemplateMode,
  SequenceExecutionNotificationChannel,
  SequenceExecutionNotificationChannelDelivery,
  SequenceExecutionWebhook,
  SequenceExecutionWebhookDelivery,
  SequenceExecutionWebhookDeliveriesCompareResponse,
  SequenceExecutionWebhookHealthResponse,
  SequenceExecutionWebhookPreviewResponse,
  SequenceExecutionWebhooksDashboardResponse,
  SequenceNotificationSeverity,
} from "../types/sequenceExecution";


type SequenceWebhooksPanelProps = {
  className?: string;
};


function getBackendErrorMessage(error: unknown): string {
  if (error && typeof error === "object") {
    const maybeResponse = error as {
      response?: {
        data?: {
          error?: {
            message?: unknown;
          };
          detail?: unknown;
        };
      };
      message?: unknown;
    };

    const backendMessage = maybeResponse.response?.data?.error?.message;
    if (typeof backendMessage === "string" && backendMessage.trim() !== "") {
      return backendMessage.trim();
    }

    const detail = maybeResponse.response?.data?.detail;
    if (Array.isArray(detail) && detail.length > 0) {
      const firstItem = detail[0];
      if (firstItem && typeof firstItem === "object" && "msg" in firstItem) {
        const msg = (firstItem as { msg?: unknown }).msg;
        if (typeof msg === "string" && msg.trim() !== "") {
          return msg.trim();
        }
      }
    }

    if (typeof maybeResponse.message === "string" && maybeResponse.message.trim() !== "") {
      return maybeResponse.message.trim();
    }
  }

  return "Error en la operacion";
}


function parseTypesInput(rawValue: string): string[] {
  const seen = new Set<string>();
  const values: string[] = [];

  rawValue
    .split("\n")
    .flatMap((line) => line.split(","))
    .map((item) => item.trim())
    .forEach((item) => {
      if (!item) {
        return;
      }
      if (seen.has(item)) {
        return;
      }
      seen.add(item);
      values.push(item);
    });

  return values;
}


function parseRoutingTargetRef(value: string): {
  target_channel_kind: "notification_channel" | "webhook";
  target_channel_id: string;
} | null {
  const normalized = value.trim();
  if (!normalized) {
    return null;
  }

  const separatorIndex = normalized.indexOf(":");
  if (separatorIndex <= 0) {
    return null;
  }

  const kind = normalized.slice(0, separatorIndex).trim();
  const id = normalized.slice(separatorIndex + 1).trim();
  if (!id) {
    return null;
  }
  if (kind !== "notification_channel" && kind !== "webhook") {
    return null;
  }

  return {
    target_channel_kind: kind,
    target_channel_id: id,
  };
}


const TEMPLATE_TOKEN_REGEX = /{{\s*([a-zA-Z0-9_]+)\s*}}/g;

const PREVIEW_SAMPLE_VALUES: Record<string, string> = {
  notification_id: "notif_preview_001",
  collection_id: "collection_preview_001",
  collection_name: "Preview Collection",
  type: "HEALTH_STATUS_CHANGED",
  severity: "warning",
  message: "Collection health changed from green to yellow.",
  created_at: "2026-01-01T10:00:00+00:00",
  health_status: "yellow",
  webhook_id: "webhook_preview_001",
  webhook_name: "Preview Webhook",
  webhook_url: "https://example.test/webhook",
};

const DEFAULT_CUSTOM_TEMPLATE: Record<string, unknown> = {
  event: "{{type}}",
  level: "{{severity}}",
  notification_id: "{{notification_id}}",
  collection_id: "{{collection_id}}",
  message: "{{message}}",
};


function buildDefaultPreviewPayload(values: Record<string, string>): Record<string, string> {
  return {
    notification_id: values.notification_id,
    collection_id: values.collection_id,
    type: values.type,
    severity: values.severity,
    message: values.message,
    created_at: values.created_at,
    collection_name: values.collection_name,
    health_status: values.health_status,
  };
}


function buildCompactPreviewPayload(values: Record<string, string>): Record<string, string> {
  return {
    notification_id: values.notification_id,
    collection_id: values.collection_id,
    type: values.type,
    severity: values.severity,
    message: values.message,
    created_at: values.created_at,
    health_status: values.health_status,
  };
}


function renderCustomTemplatePreviewValue(
  value: unknown,
  templateValues: Record<string, string>
): unknown {
  if (Array.isArray(value)) {
    return value.map((item) => renderCustomTemplatePreviewValue(item, templateValues));
  }

  if (value && typeof value === "object") {
    const rendered: Record<string, unknown> = {};
    for (const [rawKey, rawValue] of Object.entries(value)) {
      if (typeof rawKey !== "string") {
        continue;
      }
      const key = rawKey.trim();
      if (!key) {
        continue;
      }
      rendered[key] = renderCustomTemplatePreviewValue(rawValue, templateValues);
    }
    return rendered;
  }

  if (typeof value === "string") {
    const trimmed = value.trim();
    const exactMatch = trimmed.match(/^{{\s*([a-zA-Z0-9_]+)\s*}}$/);
    if (exactMatch) {
      return templateValues[exactMatch[1]] ?? "";
    }

    return value.replace(TEMPLATE_TOKEN_REGEX, (_, key: string) => templateValues[key] ?? "");
  }

  return value;
}


function getSeverityStyle(severity: SequenceNotificationSeverity): CSSProperties {
  if (severity === "critical") {
    return { background: "#fef2f2", color: "#991b1b", border: "1px solid #fecaca" };
  }
  if (severity === "warning") {
    return { background: "#fffbeb", color: "#92400e", border: "1px solid #fde68a" };
  }
  return { background: "#eff6ff", color: "#1d4ed8", border: "1px solid #bfdbfe" };
}


function getDeliveryStatusStyle(status: SequenceExecutionWebhookDelivery["delivery_status"]): CSSProperties {
  if (status === "sent") {
    return { background: "#ecfdf3", color: "#166534", border: "1px solid #86efac" };
  }
  if (status === "failed") {
    return { background: "#fef2f2", color: "#991b1b", border: "1px solid #fecaca" };
  }
  return { background: "#f3f4f6", color: "#374151", border: "1px solid #d1d5db" };
}


function getWebhookHealthStyle(
  healthStatus: SequenceExecutionWebhook["health_status"]
): CSSProperties {
  if (healthStatus === "red") {
    return { background: "#fef2f2", color: "#991b1b", border: "1px solid #fecaca" };
  }
  if (healthStatus === "yellow") {
    return { background: "#fffbeb", color: "#92400e", border: "1px solid #fde68a" };
  }
  return { background: "#ecfdf3", color: "#166534", border: "1px solid #86efac" };
}


function formatWebhookHealthLabel(
  healthStatus: SequenceExecutionWebhook["health_status"]
): string {
  if (healthStatus === "red") {
    return "RED";
  }
  if (healthStatus === "yellow") {
    return "YELLOW";
  }
  return "GREEN";
}


function formatTimestamp(value: string | null | undefined): string {
  if (!value) {
    return "-";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}


export default function SequenceWebhooksPanel({ className }: SequenceWebhooksPanelProps) {
  const [webhooks, setWebhooks] = useState<SequenceExecutionWebhook[]>([]);
  const [webhooksLoading, setWebhooksLoading] = useState(false);
  const [webhooksError, setWebhooksError] = useState("");
  const [webhooksDashboard, setWebhooksDashboard] = useState<SequenceExecutionWebhooksDashboardResponse | null>(null);
  const [webhooksDashboardLoading, setWebhooksDashboardLoading] = useState(false);
  const [webhooksDashboardError, setWebhooksDashboardError] = useState("");

  const [deliveries, setDeliveries] = useState<SequenceExecutionWebhookDelivery[]>([]);
  const [deliveriesLoading, setDeliveriesLoading] = useState(false);
  const [deliveriesError, setDeliveriesError] = useState("");
  const [deliveriesWebhookFilter, setDeliveriesWebhookFilter] = useState("");
  const [deliveriesTypeFilter, setDeliveriesTypeFilter] = useState<"all" | "notification" | "test">("all");
  const [selectedDeliveryId, setSelectedDeliveryId] = useState<string | null>(null);
  const [compareLeftDeliveryId, setCompareLeftDeliveryId] = useState("");
  const [compareRightDeliveryId, setCompareRightDeliveryId] = useState("");
  const [compareLoading, setCompareLoading] = useState(false);
  const [compareError, setCompareError] = useState("");
  const [compareResponse, setCompareResponse] = useState<SequenceExecutionWebhookDeliveriesCompareResponse | null>(null);

  const [editingWebhookId, setEditingWebhookId] = useState<string | null>(null);
  const [webhookNameInput, setWebhookNameInput] = useState("");
  const [webhookUrlInput, setWebhookUrlInput] = useState("");
  const [webhookEnabledInput, setWebhookEnabledInput] = useState(true);
  const [webhookAuthModeInput, setWebhookAuthModeInput] = useState<SequenceWebhookAuthMode>("none");
  const [webhookSecretTokenInput, setWebhookSecretTokenInput] = useState("");
  const [webhookSeverityInput, setWebhookSeverityInput] = useState<SequenceNotificationSeverity>("info");
  const [webhookTemplateModeInput, setWebhookTemplateModeInput] = useState<SequenceWebhookPayloadTemplateMode>("default");
  const [webhookTemplateInput, setWebhookTemplateInput] = useState("");
  const [webhookTypesInput, setWebhookTypesInput] = useState("");
  const [webhookSaving, setWebhookSaving] = useState(false);
  const [webhookActionId, setWebhookActionId] = useState<string | null>(null);
  const [testWebhookId, setTestWebhookId] = useState<string | null>(null);
  const [previewWebhookId, setPreviewWebhookId] = useState<string | null>(null);
  const [previewResponse, setPreviewResponse] = useState<SequenceExecutionWebhookPreviewResponse | null>(null);
  const [previewError, setPreviewError] = useState("");
  const [selectedWebhookHealthId, setSelectedWebhookHealthId] = useState<string | null>(null);
  const [webhookHealthLoading, setWebhookHealthLoading] = useState(false);
  const [webhookHealthError, setWebhookHealthError] = useState("");
  const [webhookHealthResponse, setWebhookHealthResponse] = useState<SequenceExecutionWebhookHealthResponse | null>(null);
  const [retryDeliveryId, setRetryDeliveryId] = useState<string | null>(null);
  const [processingRetries, setProcessingRetries] = useState(false);
  const [formError, setFormError] = useState("");
  const [info, setInfo] = useState("");

  const [channels, setChannels] = useState<SequenceExecutionNotificationChannel[]>([]);
  const [channelsLoading, setChannelsLoading] = useState(false);
  const [channelsError, setChannelsError] = useState("");
  const [editingChannelId, setEditingChannelId] = useState<string | null>(null);
  const [channelTypeInput, setChannelTypeInput] = useState<SequenceNotificationChannelType>("slack");
  const [channelNameInput, setChannelNameInput] = useState("");
  const [channelEnabledInput, setChannelEnabledInput] = useState(true);
  const [channelMinSeverityInput, setChannelMinSeverityInput] = useState<SequenceNotificationSeverity>("info");
  const [channelTypesInput, setChannelTypesInput] = useState("");
  const [channelSlackWebhookInput, setChannelSlackWebhookInput] = useState("");
  const [channelTelegramTokenInput, setChannelTelegramTokenInput] = useState("");
  const [channelTelegramChatIdInput, setChannelTelegramChatIdInput] = useState("");
  const [channelSaving, setChannelSaving] = useState(false);
  const [channelActionId, setChannelActionId] = useState<string | null>(null);
  const [channelTestId, setChannelTestId] = useState<string | null>(null);

  const [channelDeliveries, setChannelDeliveries] = useState<SequenceExecutionNotificationChannelDelivery[]>([]);
  const [channelDeliveriesLoading, setChannelDeliveriesLoading] = useState(false);
  const [channelDeliveriesError, setChannelDeliveriesError] = useState("");
  const [channelDeliveriesFilter, setChannelDeliveriesFilter] = useState("");
  const [channelRetryId, setChannelRetryId] = useState<string | null>(null);
  const [processingChannelRetries, setProcessingChannelRetries] = useState(false);

  const [routingRules, setRoutingRules] = useState<SequenceExecutionAlertRoutingRule[]>([]);
  const [routingRulesLoading, setRoutingRulesLoading] = useState(false);
  const [routingRulesError, setRoutingRulesError] = useState("");
  const [editingRoutingRuleId, setEditingRoutingRuleId] = useState<string | null>(null);
  const [ruleNameInput, setRuleNameInput] = useState("");
  const [ruleEnabledInput, setRuleEnabledInput] = useState(true);
  const [ruleTargetRefInput, setRuleTargetRefInput] = useState("");
  const [ruleTypesInput, setRuleTypesInput] = useState("");
  const [ruleMinSeverityInput, setRuleMinSeverityInput] = useState<SequenceNotificationSeverity>("info");
  const [ruleMatchCollectionIdInput, setRuleMatchCollectionIdInput] = useState("");
  const [ruleMatchHealthStatusInput, setRuleMatchHealthStatusInput] = useState<"all" | "green" | "yellow" | "red">("all");
  const [ruleSaving, setRuleSaving] = useState(false);
  const [ruleActionId, setRuleActionId] = useState<string | null>(null);

  const webhookNameById = useMemo(() => {
    return new Map(webhooks.map((item) => [item.webhook_id, item.name]));
  }, [webhooks]);

  const routingTargetOptions = useMemo(() => {
    const options: Array<{ key: string; label: string }> = [];

    for (const channel of channels) {
      const key = `notification_channel:${channel.channel_id}`;
      options.push({
        key,
        label: `[channel:${channel.channel_type}] ${channel.name}`,
      });
    }

    for (const webhook of webhooks) {
      const key = `webhook:${webhook.webhook_id}`;
      options.push({
        key,
        label: `[webhook] ${webhook.name}`,
      });
    }

    return options;
  }, [channels, webhooks]);

  const selectedDelivery = useMemo(() => {
    if (!selectedDeliveryId) {
      return null;
    }
    return deliveries.find((item) => item.delivery_id === selectedDeliveryId) ?? null;
  }, [deliveries, selectedDeliveryId]);

  const webhookTemplatePreview = useMemo(() => {
    if (webhookTemplateModeInput === "default") {
      return JSON.stringify(buildDefaultPreviewPayload(PREVIEW_SAMPLE_VALUES), null, 2);
    }

    if (webhookTemplateModeInput === "compact") {
      return JSON.stringify(buildCompactPreviewPayload(PREVIEW_SAMPLE_VALUES), null, 2);
    }

    const trimmed = webhookTemplateInput.trim();
    if (!trimmed) {
      return "{}";
    }

    try {
      const parsed = JSON.parse(trimmed);
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
        return "payload_template debe ser un objeto JSON.";
      }
      return JSON.stringify(renderCustomTemplatePreviewValue(parsed, PREVIEW_SAMPLE_VALUES), null, 2);
    } catch {
      return "payload_template no es JSON valido.";
    }
  }, [webhookTemplateInput, webhookTemplateModeInput]);

  const loadWebhooks = useCallback(async (silent = false) => {
    if (!silent) {
      setWebhooksLoading(true);
    }
    setWebhooksError("");

    try {
      const response = await listSequenceNotificationWebhooks({
        limit: 200,
        include_disabled: true,
      });
      setWebhooks(response.webhooks);

      if (
        deliveriesWebhookFilter &&
        !response.webhooks.some((item) => item.webhook_id === deliveriesWebhookFilter)
      ) {
        setDeliveriesWebhookFilter("");
      }
    } catch (error) {
      setWebhooksError(getBackendErrorMessage(error));
      setWebhooks([]);
    } finally {
      if (!silent) {
        setWebhooksLoading(false);
      }
    }
  }, [deliveriesWebhookFilter]);

  const loadWebhooksDashboard = useCallback(async (silent = false) => {
    if (!silent) {
      setWebhooksDashboardLoading(true);
    }
    setWebhooksDashboardError("");

    try {
      const response = await getSequenceWebhooksDashboard({
        top_limit: 5,
        errors_limit: 20,
      });
      setWebhooksDashboard(response);
    } catch (error) {
      setWebhooksDashboardError(getBackendErrorMessage(error));
      setWebhooksDashboard(null);
    } finally {
      if (!silent) {
        setWebhooksDashboardLoading(false);
      }
    }
  }, []);

  const loadWebhookHealth = useCallback(async (webhookId: string, silent = false) => {
    const normalizedWebhookId = webhookId.trim();
    if (!normalizedWebhookId) {
      return;
    }

    setSelectedWebhookHealthId(normalizedWebhookId);
    setWebhookHealthError("");
    if (!silent) {
      setWebhookHealthLoading(true);
    }

    try {
      const response = await getSequenceWebhookHealth(normalizedWebhookId, {
        recent_limit: 40,
        signals_limit: 12,
      });
      setWebhookHealthResponse(response);
    } catch (error) {
      setWebhookHealthError(getBackendErrorMessage(error));
      setWebhookHealthResponse(null);
    } finally {
      if (!silent) {
        setWebhookHealthLoading(false);
      }
    }
  }, []);

  const loadDeliveries = useCallback(async (silent = false) => {
    if (!silent) {
      setDeliveriesLoading(true);
    }
    setDeliveriesError("");

    try {
      const isTestFilter =
        deliveriesTypeFilter === "all"
          ? undefined
          : deliveriesTypeFilter === "test";
      const response = await listSequenceWebhookDeliveries({
        limit: 100,
        webhook_id: deliveriesWebhookFilter || undefined,
        is_test: isTestFilter,
      });
      setDeliveries(response.deliveries);
    } catch (error) {
      setDeliveriesError(getBackendErrorMessage(error));
      setDeliveries([]);
    } finally {
      if (!silent) {
        setDeliveriesLoading(false);
      }
    }
  }, [deliveriesTypeFilter, deliveriesWebhookFilter]);

  const loadChannels = useCallback(async (silent = false) => {
    if (!silent) {
      setChannelsLoading(true);
    }
    setChannelsError("");

    try {
      const response = await listSequenceNotificationChannels({
        limit: 200,
        include_disabled: true,
      });
      setChannels(response.channels);
      if (
        channelDeliveriesFilter &&
        !response.channels.some((item) => item.channel_id === channelDeliveriesFilter)
      ) {
        setChannelDeliveriesFilter("");
      }
    } catch (error) {
      setChannelsError(getBackendErrorMessage(error));
      setChannels([]);
    } finally {
      if (!silent) {
        setChannelsLoading(false);
      }
    }
  }, [channelDeliveriesFilter]);

  const loadChannelDeliveries = useCallback(async (silent = false) => {
    if (!silent) {
      setChannelDeliveriesLoading(true);
    }
    setChannelDeliveriesError("");

    try {
      const response = await listSequenceNotificationChannelDeliveries({
        limit: 100,
        channel_id: channelDeliveriesFilter || undefined,
      });
      setChannelDeliveries(response.deliveries);
    } catch (error) {
      setChannelDeliveriesError(getBackendErrorMessage(error));
      setChannelDeliveries([]);
    } finally {
      if (!silent) {
        setChannelDeliveriesLoading(false);
      }
    }
  }, [channelDeliveriesFilter]);

  const loadRoutingRules = useCallback(async (silent = false) => {
    if (!silent) {
      setRoutingRulesLoading(true);
    }
    setRoutingRulesError("");

    try {
      const response = await listSequenceAlertRoutingRules({
        limit: 300,
        include_disabled: true,
      });
      setRoutingRules(response.rules);
    } catch (error) {
      setRoutingRulesError(getBackendErrorMessage(error));
      setRoutingRules([]);
    } finally {
      if (!silent) {
        setRoutingRulesLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    void loadWebhooks(false);
  }, [loadWebhooks]);

  useEffect(() => {
    void loadWebhooksDashboard(false);
  }, [loadWebhooksDashboard]);

  useEffect(() => {
    void loadDeliveries(false);
  }, [loadDeliveries]);

  useEffect(() => {
    void loadChannels(false);
  }, [loadChannels]);

  useEffect(() => {
    void loadChannelDeliveries(false);
  }, [loadChannelDeliveries]);

  useEffect(() => {
    void loadRoutingRules(false);
  }, [loadRoutingRules]);

  useEffect(() => {
    if (!ruleTargetRefInput && routingTargetOptions.length > 0) {
      setRuleTargetRefInput(routingTargetOptions[0].key);
    }
  }, [routingTargetOptions, ruleTargetRefInput]);

  useEffect(() => {
    if (
      selectedWebhookHealthId &&
      !webhooks.some((item) => item.webhook_id === selectedWebhookHealthId)
    ) {
      setSelectedWebhookHealthId(null);
      setWebhookHealthResponse(null);
      setWebhookHealthError("");
    }

    if (selectedDeliveryId && !deliveries.some((item) => item.delivery_id === selectedDeliveryId)) {
      setSelectedDeliveryId(null);
    }

    if (compareLeftDeliveryId && !deliveries.some((item) => item.delivery_id === compareLeftDeliveryId)) {
      setCompareLeftDeliveryId("");
      setCompareResponse(null);
    }

    if (compareRightDeliveryId && !deliveries.some((item) => item.delivery_id === compareRightDeliveryId)) {
      setCompareRightDeliveryId("");
      setCompareResponse(null);
    }
  }, [
    compareLeftDeliveryId,
    compareRightDeliveryId,
    deliveries,
    selectedDeliveryId,
    selectedWebhookHealthId,
    webhooks,
  ]);

  function resetForm() {
    setEditingWebhookId(null);
    setWebhookNameInput("");
    setWebhookUrlInput("");
    setWebhookEnabledInput(true);
    setWebhookAuthModeInput("none");
    setWebhookSecretTokenInput("");
    setWebhookSeverityInput("info");
    setWebhookTemplateModeInput("default");
    setWebhookTemplateInput("");
    setWebhookTypesInput("");
    setFormError("");
  }

  function startEditWebhook(webhook: SequenceExecutionWebhook) {
    setEditingWebhookId(webhook.webhook_id);
    setWebhookNameInput(webhook.name);
    setWebhookUrlInput(webhook.url);
    setWebhookEnabledInput(webhook.is_enabled);
    setWebhookAuthModeInput(webhook.auth_mode);
    setWebhookSecretTokenInput("");
    setWebhookSeverityInput(webhook.min_severity);
    setWebhookTemplateModeInput(webhook.payload_template_mode ?? "default");
    setWebhookTemplateInput(
      webhook.payload_template && typeof webhook.payload_template === "object"
        ? JSON.stringify(webhook.payload_template, null, 2)
        : ""
    );
    setWebhookTypesInput(webhook.enabled_types.join(", "));
    setFormError("");
  }

  async function saveWebhook() {
    const normalizedName = webhookNameInput.trim();
    const normalizedUrl = webhookUrlInput.trim();
    const normalizedSecretToken = webhookSecretTokenInput.trim();
    if (!normalizedName || !normalizedUrl) {
      setFormError("name y url son obligatorios.");
      return;
    }

    if (!editingWebhookId && webhookAuthModeInput !== "none" && !normalizedSecretToken) {
      setFormError("secret_token es obligatorio para bearer y hmac_sha256.");
      return;
    }

    let normalizedPayloadTemplate: Record<string, unknown> | undefined;
    if (webhookTemplateModeInput === "custom") {
      const templateText = webhookTemplateInput.trim();
      if (!templateText) {
        setFormError("payload_template es obligatorio cuando payload_template_mode es custom.");
        return;
      }

      try {
        const parsedTemplate = JSON.parse(templateText);
        if (!parsedTemplate || typeof parsedTemplate !== "object" || Array.isArray(parsedTemplate)) {
          setFormError("payload_template debe ser un objeto JSON.");
          return;
        }
        normalizedPayloadTemplate = parsedTemplate as Record<string, unknown>;
      } catch {
        setFormError("payload_template no es JSON valido.");
        return;
      }
    }

    setWebhookSaving(true);
    setFormError("");
    setInfo("");

    try {
      const payload = {
        name: normalizedName,
        url: normalizedUrl,
        is_enabled: webhookEnabledInput,
        auth_mode: webhookAuthModeInput,
        secret_token: normalizedSecretToken === "" ? undefined : normalizedSecretToken,
        min_severity: webhookSeverityInput,
        enabled_types: parseTypesInput(webhookTypesInput),
        payload_template_mode: webhookTemplateModeInput,
        payload_template: normalizedPayloadTemplate,
      };

      if (editingWebhookId) {
        await updateSequenceNotificationWebhook(editingWebhookId, payload);
        setInfo("Webhook actualizado.");
      } else {
        await createSequenceNotificationWebhook(payload);
        setInfo("Webhook creado.");
      }

      await loadWebhooks(true);
      await loadDeliveries(true);
      await loadWebhooksDashboard(true);
      await loadRoutingRules(true);
      if (selectedWebhookHealthId) {
        await loadWebhookHealth(selectedWebhookHealthId, true);
      }
      resetForm();
    } catch (error) {
      setFormError(getBackendErrorMessage(error));
    } finally {
      setWebhookSaving(false);
    }
  }

  async function toggleWebhookEnabled(webhook: SequenceExecutionWebhook) {
    setWebhookActionId(webhook.webhook_id);
    setWebhooksError("");
    setInfo("");

    try {
      await updateSequenceNotificationWebhook(webhook.webhook_id, {
        is_enabled: !webhook.is_enabled,
      });
      setInfo(`Webhook ${webhook.is_enabled ? "deshabilitado" : "habilitado"}.`);
      await loadWebhooks(true);
      await loadWebhooksDashboard(true);
      await loadRoutingRules(true);
      if (selectedWebhookHealthId === webhook.webhook_id) {
        await loadWebhookHealth(webhook.webhook_id, true);
      }
    } catch (error) {
      setWebhooksError(getBackendErrorMessage(error));
    } finally {
      setWebhookActionId(null);
    }
  }

  async function sendTestEvent(webhook: SequenceExecutionWebhook) {
    const webhookId = webhook.webhook_id.trim();
    if (!webhookId) {
      return;
    }

    setTestWebhookId(webhookId);
    setDeliveriesError("");
    setInfo("");

    try {
      const response = await sendSequenceWebhookTestEvent(webhookId);
      const status = response.delivery.delivery_status;
      const attempt = response.delivery.attempt_count;
      setInfo(`Test event enviado (${status}). attempt_count=${attempt}.`);
      await loadWebhooks(true);
      await loadDeliveries(true);
      await loadWebhooksDashboard(true);
      await loadWebhookHealth(webhookId, true);
    } catch (error) {
      setDeliveriesError(getBackendErrorMessage(error));
    } finally {
      setTestWebhookId(null);
    }
  }

  async function previewPayload(webhook: SequenceExecutionWebhook) {
    const webhookId = webhook.webhook_id.trim();
    if (!webhookId) {
      return;
    }

    setPreviewWebhookId(webhookId);
    setPreviewError("");
    setInfo("");

    try {
      const response = await previewSequenceWebhookPayload(webhookId, {
        event_type: "test_event",
      });
      setPreviewResponse(response);
      setInfo("Preview generado.");
    } catch (error) {
      setPreviewResponse(null);
      setPreviewError(getBackendErrorMessage(error));
    } finally {
      setPreviewWebhookId(null);
    }
  }

  async function compareSelectedDeliveries() {
    const leftId = compareLeftDeliveryId.trim();
    const rightId = compareRightDeliveryId.trim();
    if (!leftId || !rightId) {
      setCompareError("Selecciona left y right delivery para comparar.");
      return;
    }

    setCompareLoading(true);
    setCompareError("");
    setInfo("");

    try {
      const response = await compareSequenceWebhookDeliveries(leftId, rightId);
      setCompareResponse(response);
      setInfo("Diff de deliveries generado.");
    } catch (error) {
      setCompareResponse(null);
      setCompareError(getBackendErrorMessage(error));
    } finally {
      setCompareLoading(false);
    }
  }

  async function retryDelivery(delivery: SequenceExecutionWebhookDelivery) {
    const deliveryId = delivery.delivery_id.trim();
    if (!deliveryId) {
      return;
    }

    setRetryDeliveryId(deliveryId);
    setDeliveriesError("");
    setInfo("");

    try {
      const response = await retrySequenceWebhookDelivery(deliveryId);
      const nextStatus = response.delivery.delivery_status;
      const nextAttemptCount = response.delivery.attempt_count;
      setInfo(`Reintento ejecutado (${nextStatus}). attempt_count=${nextAttemptCount}.`);
      await loadWebhooks(true);
      await loadDeliveries(true);
      await loadWebhooksDashboard(true);
      if (selectedWebhookHealthId === delivery.webhook_id) {
        await loadWebhookHealth(delivery.webhook_id, true);
      }
    } catch (error) {
      setDeliveriesError(getBackendErrorMessage(error));
    } finally {
      setRetryDeliveryId(null);
    }
  }

  async function processPendingRetries() {
    setProcessingRetries(true);
    setDeliveriesError("");
    setInfo("");

    try {
      const response = await processSequenceWebhookDeliveryRetries({
        limit: 100,
        webhook_id: deliveriesWebhookFilter || undefined,
      });
      setInfo(
        `Retries procesados=${response.processed_count}, sent=${response.sent_count}, failed=${response.failed_count}, exhausted=${response.exhausted_count}.`
      );
      await loadWebhooks(true);
      await loadDeliveries(true);
      await loadWebhooksDashboard(true);
      if (selectedWebhookHealthId) {
        await loadWebhookHealth(selectedWebhookHealthId, true);
      }
    } catch (error) {
      setDeliveriesError(getBackendErrorMessage(error));
    } finally {
      setProcessingRetries(false);
    }
  }

  function resetChannelForm() {
    setEditingChannelId(null);
    setChannelTypeInput("slack");
    setChannelNameInput("");
    setChannelEnabledInput(true);
    setChannelMinSeverityInput("info");
    setChannelTypesInput("");
    setChannelSlackWebhookInput("");
    setChannelTelegramTokenInput("");
    setChannelTelegramChatIdInput("");
  }

  function startEditChannel(channel: SequenceExecutionNotificationChannel) {
    setEditingChannelId(channel.channel_id);
    setChannelTypeInput(channel.channel_type);
    setChannelNameInput(channel.name);
    setChannelEnabledInput(channel.is_enabled);
    setChannelMinSeverityInput(channel.min_severity);
    setChannelTypesInput((channel.enabled_types ?? []).join(", "));
    const config = channel.config ?? {};
    setChannelSlackWebhookInput(
      typeof config.webhook_url === "string" ? config.webhook_url : ""
    );
    setChannelTelegramTokenInput("");
    setChannelTelegramChatIdInput(
      typeof config.chat_id === "string" ? config.chat_id : ""
    );
  }

  async function saveChannel() {
    const normalizedName = channelNameInput.trim();
    if (!normalizedName) {
      setChannelsError("name es obligatorio para el canal.");
      return;
    }

    const config: Record<string, unknown> = {};
    if (channelTypeInput === "slack") {
      const webhookUrl = channelSlackWebhookInput.trim();
      if (!webhookUrl) {
        setChannelsError("config.webhook_url es obligatorio para slack.");
        return;
      }
      config.webhook_url = webhookUrl;
    }
    if (channelTypeInput === "telegram") {
      const botToken = channelTelegramTokenInput.trim();
      const chatId = channelTelegramChatIdInput.trim();
      if (!editingChannelId && !botToken) {
        setChannelsError("config.bot_token es obligatorio para telegram.");
        return;
      }
      if (!chatId) {
        setChannelsError("config.chat_id es obligatorio para telegram.");
        return;
      }
      if (botToken) {
        config.bot_token = botToken;
      }
      config.chat_id = chatId;
    }

    setChannelSaving(true);
    setChannelsError("");
    setInfo("");

    try {
      const payload = {
        name: normalizedName,
        is_enabled: channelEnabledInput,
        min_severity: channelMinSeverityInput,
        enabled_types: parseTypesInput(channelTypesInput),
        config,
      };

      if (editingChannelId) {
        await updateSequenceNotificationChannel(editingChannelId, payload);
        setInfo("Canal de notificacion actualizado.");
      } else {
        await createSequenceNotificationChannel({
          channel_type: channelTypeInput,
          ...payload,
        });
        setInfo("Canal de notificacion creado.");
      }

      await loadChannels(true);
      await loadChannelDeliveries(true);
      await loadRoutingRules(true);
      resetChannelForm();
    } catch (error) {
      setChannelsError(getBackendErrorMessage(error));
    } finally {
      setChannelSaving(false);
    }
  }

  async function toggleChannelEnabled(channel: SequenceExecutionNotificationChannel) {
    setChannelActionId(channel.channel_id);
    setChannelsError("");
    setInfo("");
    try {
      await updateSequenceNotificationChannel(channel.channel_id, {
        is_enabled: !channel.is_enabled,
      });
      setInfo(`Canal ${channel.is_enabled ? "deshabilitado" : "habilitado"}.`);
      await loadChannels(true);
      await loadRoutingRules(true);
    } catch (error) {
      setChannelsError(getBackendErrorMessage(error));
    } finally {
      setChannelActionId(null);
    }
  }

  async function sendChannelTestEvent(channel: SequenceExecutionNotificationChannel) {
    setChannelTestId(channel.channel_id);
    setChannelDeliveriesError("");
    setInfo("");

    try {
      const response = await sendSequenceNotificationChannelTestEvent(channel.channel_id);
      setInfo(
        `Test de canal enviado (${response.delivery.delivery_status}). attempt_count=${response.delivery.attempt_count}.`
      );
      await loadChannels(true);
      await loadChannelDeliveries(true);
    } catch (error) {
      setChannelDeliveriesError(getBackendErrorMessage(error));
    } finally {
      setChannelTestId(null);
    }
  }

  async function retryChannelDelivery(delivery: SequenceExecutionNotificationChannelDelivery) {
    setChannelRetryId(delivery.delivery_id);
    setChannelDeliveriesError("");
    setInfo("");
    try {
      const response = await retrySequenceNotificationChannelDelivery(delivery.delivery_id);
      setInfo(
        `Reintento de canal ejecutado (${response.delivery.delivery_status}). attempt_count=${response.delivery.attempt_count}.`
      );
      await loadChannelDeliveries(true);
    } catch (error) {
      setChannelDeliveriesError(getBackendErrorMessage(error));
    } finally {
      setChannelRetryId(null);
    }
  }

  async function processChannelPendingRetries() {
    setProcessingChannelRetries(true);
    setChannelDeliveriesError("");
    setInfo("");

    try {
      const response = await processSequenceNotificationChannelDeliveryRetries({
        limit: 100,
        channel_id: channelDeliveriesFilter || undefined,
      });
      setInfo(
        `Channel retries procesados=${response.processed_count}, sent=${response.sent_count}, failed=${response.failed_count}, exhausted=${response.exhausted_count}.`
      );
      await loadChannelDeliveries(true);
    } catch (error) {
      setChannelDeliveriesError(getBackendErrorMessage(error));
    } finally {
      setProcessingChannelRetries(false);
    }
  }

  function resetRoutingRuleForm() {
    setEditingRoutingRuleId(null);
    setRuleNameInput("");
    setRuleEnabledInput(true);
    setRuleTargetRefInput(routingTargetOptions[0]?.key ?? "");
    setRuleTypesInput("");
    setRuleMinSeverityInput("info");
    setRuleMatchCollectionIdInput("");
    setRuleMatchHealthStatusInput("all");
  }

  function startEditRoutingRule(rule: SequenceExecutionAlertRoutingRule) {
    setEditingRoutingRuleId(rule.rule_id);
    setRuleNameInput(rule.name);
    setRuleEnabledInput(rule.is_enabled);
    setRuleTargetRefInput(`${rule.target_channel_kind}:${rule.target_channel_id}`);
    setRuleTypesInput((rule.match_types ?? []).join(", "));
    setRuleMinSeverityInput(rule.min_severity);
    setRuleMatchCollectionIdInput(rule.match_collection_id ?? "");
    setRuleMatchHealthStatusInput(rule.match_health_status ?? "all");
    setRoutingRulesError("");
  }

  async function saveRoutingRule() {
    const normalizedName = ruleNameInput.trim();
    if (!normalizedName) {
      setRoutingRulesError("name es obligatorio para la regla.");
      return;
    }

    const parsedTarget = parseRoutingTargetRef(ruleTargetRefInput);
    if (!parsedTarget) {
      setRoutingRulesError("Selecciona un destino valido para la regla.");
      return;
    }

    setRuleSaving(true);
    setRoutingRulesError("");
    setInfo("");

    try {
      const payload = {
        name: normalizedName,
        is_enabled: ruleEnabledInput,
        target_channel_id: parsedTarget.target_channel_id,
        target_channel_kind: parsedTarget.target_channel_kind,
        match_types: parseTypesInput(ruleTypesInput),
        min_severity: ruleMinSeverityInput,
        match_collection_id: ruleMatchCollectionIdInput.trim() || undefined,
        match_health_status: ruleMatchHealthStatusInput === "all" ? undefined : ruleMatchHealthStatusInput,
      };

      if (editingRoutingRuleId) {
        await updateSequenceAlertRoutingRule(editingRoutingRuleId, payload);
        setInfo("Regla de ruteo actualizada.");
      } else {
        await createSequenceAlertRoutingRule(payload);
        setInfo("Regla de ruteo creada.");
      }

      await loadRoutingRules(true);
      resetRoutingRuleForm();
    } catch (error) {
      setRoutingRulesError(getBackendErrorMessage(error));
    } finally {
      setRuleSaving(false);
    }
  }

  async function toggleRoutingRule(rule: SequenceExecutionAlertRoutingRule) {
    setRuleActionId(rule.rule_id);
    setRoutingRulesError("");
    setInfo("");
    try {
      await updateSequenceAlertRoutingRule(rule.rule_id, {
        is_enabled: !rule.is_enabled,
      });
      setInfo(`Regla ${rule.is_enabled ? "deshabilitada" : "habilitada"}.`);
      await loadRoutingRules(true);
    } catch (error) {
      setRoutingRulesError(getBackendErrorMessage(error));
    } finally {
      setRuleActionId(null);
    }
  }

  async function removeRoutingRule(rule: SequenceExecutionAlertRoutingRule) {
    setRuleActionId(rule.rule_id);
    setRoutingRulesError("");
    setInfo("");
    try {
      await deleteSequenceAlertRoutingRule(rule.rule_id);
      setInfo("Regla de ruteo eliminada.");
      if (editingRoutingRuleId === rule.rule_id) {
        resetRoutingRuleForm();
      }
      await loadRoutingRules(true);
    } catch (error) {
      setRoutingRulesError(getBackendErrorMessage(error));
    } finally {
      setRuleActionId(null);
    }
  }

  return (
    <div className={`p-4 rounded-xl border border-gray-200 bg-white ${className ?? ""}`}>
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <div className="text-xs font-semibold text-gray-600">Webhooks de alertas</div>
          <div className="text-xs text-gray-500">
            Integracion externa para enviar alertas de coleccion a sistemas externos.
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            disabled={webhooksLoading}
            onClick={() => void loadWebhooks(false)}
            className="px-3 py-1 text-xs font-semibold rounded border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
          >
            {webhooksLoading ? "Actualizando..." : "Recargar webhooks"}
          </button>
          <button
            type="button"
            disabled={deliveriesLoading}
            onClick={() => void loadDeliveries(false)}
            className="px-3 py-1 text-xs font-semibold rounded border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
          >
            {deliveriesLoading ? "Actualizando..." : "Recargar entregas"}
          </button>
          <button
            type="button"
            disabled={webhooksDashboardLoading}
            onClick={() => void loadWebhooksDashboard(false)}
            className="px-3 py-1 text-xs font-semibold rounded border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
          >
            {webhooksDashboardLoading ? "Actualizando..." : "Recargar dashboard"}
          </button>
        </div>
      </div>

      {info ? (
        <div className="mt-3 px-2 py-2 rounded border border-green-200 bg-green-50 text-[11px] text-green-700">{info}</div>
      ) : null}
      {webhooksError ? (
        <div className="mt-3 px-2 py-2 rounded border border-red-200 bg-red-50 text-[11px] text-red-700">{webhooksError}</div>
      ) : null}
      {deliveriesError ? (
        <div className="mt-3 px-2 py-2 rounded border border-red-200 bg-red-50 text-[11px] text-red-700">{deliveriesError}</div>
      ) : null}
      {webhooksDashboardError ? (
        <div className="mt-3 px-2 py-2 rounded border border-red-200 bg-red-50 text-[11px] text-red-700">{webhooksDashboardError}</div>
      ) : null}
      {previewError ? (
        <div className="mt-3 px-2 py-2 rounded border border-red-200 bg-red-50 text-[11px] text-red-700">{previewError}</div>
      ) : null}
      {compareError ? (
        <div className="mt-3 px-2 py-2 rounded border border-red-200 bg-red-50 text-[11px] text-red-700">{compareError}</div>
      ) : null}
      {webhookHealthError ? (
        <div className="mt-3 px-2 py-2 rounded border border-red-200 bg-red-50 text-[11px] text-red-700">{webhookHealthError}</div>
      ) : null}
      {channelsError ? (
        <div className="mt-3 px-2 py-2 rounded border border-red-200 bg-red-50 text-[11px] text-red-700">{channelsError}</div>
      ) : null}
      {channelDeliveriesError ? (
        <div className="mt-3 px-2 py-2 rounded border border-red-200 bg-red-50 text-[11px] text-red-700">{channelDeliveriesError}</div>
      ) : null}
      {routingRulesError ? (
        <div className="mt-3 px-2 py-2 rounded border border-red-200 bg-red-50 text-[11px] text-red-700">{routingRulesError}</div>
      ) : null}

      {webhooksDashboardLoading ? (
        <div className="mt-3 text-[11px] text-gray-500">Cargando dashboard global de integraciones...</div>
      ) : webhooksDashboard ? (
        <div className="mt-3 p-3 rounded border border-gray-200 bg-gray-50 space-y-2">
          <div className="text-[11px] font-semibold text-gray-600">Dashboard global de integraciones</div>
          <div className="grid grid-cols-2 md:grid-cols-6 gap-2 text-[11px]">
            <div className="px-2 py-1 rounded border border-gray-200 bg-white">
              <div className="text-gray-500">total_webhooks</div>
              <div className="font-semibold text-gray-800">{webhooksDashboard.total_webhooks}</div>
            </div>
            <div className="px-2 py-1 rounded border border-gray-200 bg-white">
              <div className="text-gray-500">active_webhooks</div>
              <div className="font-semibold text-gray-800">{webhooksDashboard.active_webhooks}</div>
            </div>
            <div className="px-2 py-1 rounded border border-gray-200 bg-white">
              <div className="text-gray-500">inactive_webhooks</div>
              <div className="font-semibold text-gray-800">{webhooksDashboard.inactive_webhooks}</div>
            </div>
            <div className="px-2 py-1 rounded border border-green-200 bg-green-50">
              <div className="text-green-700">webhooks_green</div>
              <div className="font-semibold text-green-800">{webhooksDashboard.webhooks_green}</div>
            </div>
            <div className="px-2 py-1 rounded border border-amber-200 bg-amber-50">
              <div className="text-amber-700">webhooks_yellow</div>
              <div className="font-semibold text-amber-800">{webhooksDashboard.webhooks_yellow}</div>
            </div>
            <div className="px-2 py-1 rounded border border-red-200 bg-red-50">
              <div className="text-red-700">webhooks_red</div>
              <div className="font-semibold text-red-800">{webhooksDashboard.webhooks_red}</div>
            </div>
          </div>

          <div className="text-[11px] text-gray-600">
            deliveries total={webhooksDashboard.total_deliveries} | sent={webhooksDashboard.sent_deliveries} | failed={webhooksDashboard.failed_deliveries} | pending={webhooksDashboard.pending_deliveries}
          </div>

          <div>
            <div className="text-[11px] font-semibold text-gray-600">Alertas activas</div>
            {webhooksDashboard.active_alerts.length > 0 ? (
              <div className="mt-1 space-y-1 max-h-40 overflow-auto pr-1">
                {webhooksDashboard.active_alerts.map((item) => (
                  <button
                    key={`webhook-alert-${item.webhook_id}`}
                    type="button"
                    onClick={() => void loadWebhookHealth(item.webhook_id, false)}
                    className="w-full text-left px-2 py-1 rounded border border-gray-200 bg-white"
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-semibold text-gray-700 truncate">{item.name}</span>
                      <span className="px-2 py-0.5 rounded border text-[10px]" style={getWebhookHealthStyle(item.health_status)}>
                        {formatWebhookHealthLabel(item.health_status)}
                      </span>
                      <span className="text-[10px] text-gray-500">
                        failed={item.failed_deliveries} | exhausted={item.exhausted_deliveries} | ratio={(item.failure_ratio * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="mt-0.5 text-[11px] text-amber-700">
                      {item.alerts[0] ?? "Sin detalle de alerta"}
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="mt-1 text-[11px] text-green-700">Sin alertas activas relevantes.</div>
            )}
          </div>
        </div>
      ) : null}

      <div className="mt-3 grid grid-cols-1 xl:grid-cols-2 gap-3">
        <div className="p-3 rounded border border-gray-200 bg-gray-50">
          <div className="text-[11px] font-semibold text-gray-600">Destinos configurados</div>
          {webhooksLoading ? (
            <div className="mt-2 text-[11px] text-gray-500">Cargando webhooks...</div>
          ) : webhooks.length > 0 ? (
            <div className="mt-2 space-y-2 max-h-72 overflow-auto pr-1">
              {webhooks.map((webhook) => (
                <div key={webhook.webhook_id} className="p-2 rounded border border-gray-200 bg-white">
                  <div className="flex items-center gap-2">
                    <div className="font-semibold text-xs text-gray-700 truncate">{webhook.name}</div>
                    <span className="px-2 py-0.5 rounded border text-[10px]" style={getWebhookHealthStyle(webhook.health_status)}>
                      {formatWebhookHealthLabel(webhook.health_status)}
                    </span>
                    <span
                      className={`ml-auto px-2 py-0.5 rounded border text-[10px] ${webhook.is_enabled ? "border-green-300 bg-green-50 text-green-700" : "border-gray-300 bg-gray-100 text-gray-600"}`}
                    >
                      {webhook.is_enabled ? "enabled" : "disabled"}
                    </span>
                  </div>
                  <div className="mt-1 text-[11px] text-gray-500 break-all">{webhook.url}</div>
                  <div className="mt-1 flex flex-wrap gap-1 text-[10px]">
                    <span className="px-2 py-0.5 rounded border border-gray-300 bg-gray-100 text-gray-700">
                      auth: {webhook.auth_mode}
                    </span>
                    <span className="px-2 py-0.5 rounded border border-gray-300 bg-gray-100 text-gray-700">
                      template: {webhook.payload_template_mode}
                    </span>
                    <span className="px-2 py-0.5 rounded border border-gray-300 bg-gray-100 text-gray-700">
                      secret: {webhook.has_secret_token ? "configurado" : "no"}
                    </span>
                    <span className="px-2 py-0.5 rounded border" style={getSeverityStyle(webhook.min_severity)}>
                      min: {webhook.min_severity}
                    </span>
                    <span className="px-2 py-0.5 rounded border border-gray-300 bg-gray-100 text-gray-600">
                      tipos: {webhook.enabled_types.length > 0 ? webhook.enabled_types.join(", ") : "todos"}
                    </span>
                  </div>
                  {webhook.alerts.length > 0 ? (
                    <div className="mt-1 text-[11px] text-amber-700">alerta: {webhook.alerts[0]}</div>
                  ) : (
                    <div className="mt-1 text-[11px] text-green-700">sin alertas activas</div>
                  )}
                  <div className="mt-2 flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => startEditWebhook(webhook)}
                      className="px-2 py-0.5 rounded border border-gray-300 bg-white text-[11px] text-gray-700"
                    >
                      Editar
                    </button>
                    <button
                      type="button"
                      disabled={webhookActionId === webhook.webhook_id}
                      onClick={() => void toggleWebhookEnabled(webhook)}
                      className="px-2 py-0.5 rounded border border-gray-300 bg-white text-[11px] text-gray-700 disabled:opacity-50"
                    >
                      {webhookActionId === webhook.webhook_id
                        ? "Guardando..."
                        : webhook.is_enabled
                          ? "Deshabilitar"
                          : "Habilitar"}
                    </button>
                    <button
                      type="button"
                      disabled={webhookHealthLoading && selectedWebhookHealthId === webhook.webhook_id}
                      onClick={() => void loadWebhookHealth(webhook.webhook_id, false)}
                      className="px-2 py-0.5 rounded border border-gray-300 bg-white text-[11px] text-gray-700 disabled:opacity-50"
                    >
                      {webhookHealthLoading && selectedWebhookHealthId === webhook.webhook_id
                        ? "Cargando salud..."
                        : "Ver salud"}
                    </button>
                    <button
                      type="button"
                      disabled={testWebhookId === webhook.webhook_id}
                      onClick={() => void sendTestEvent(webhook)}
                      className="px-2 py-0.5 rounded border border-gray-300 bg-white text-[11px] text-gray-700 disabled:opacity-50"
                    >
                      {testWebhookId === webhook.webhook_id ? "Enviando..." : "Send test event"}
                    </button>
                    <button
                      type="button"
                      disabled={previewWebhookId === webhook.webhook_id}
                      onClick={() => void previewPayload(webhook)}
                      className="px-2 py-0.5 rounded border border-gray-300 bg-white text-[11px] text-gray-700 disabled:opacity-50"
                    >
                      {previewWebhookId === webhook.webhook_id ? "Generando..." : "Preview payload"}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="mt-2 text-[11px] text-gray-500">No hay webhooks configurados.</div>
          )}
        </div>

        <div className="p-3 rounded border border-gray-200 bg-gray-50 space-y-2">
          <div className="text-[11px] font-semibold text-gray-600">
            {editingWebhookId ? "Editar webhook" : "Crear webhook"}
          </div>
          <input
            type="text"
            value={webhookNameInput}
            onChange={(event) => setWebhookNameInput(event.target.value)}
            placeholder="name"
            className="w-full px-2 py-1 text-xs rounded border border-gray-300 bg-white"
          />
          <input
            type="text"
            value={webhookUrlInput}
            onChange={(event) => setWebhookUrlInput(event.target.value)}
            placeholder="https://example.com/webhook"
            className="w-full px-2 py-1 text-xs rounded border border-gray-300 bg-white"
          />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px]">
            <label className="inline-flex items-center gap-2 text-gray-700">
              <input
                type="checkbox"
                checked={webhookEnabledInput}
                onChange={(event) => setWebhookEnabledInput(event.target.checked)}
              />
              is_enabled
            </label>
            <label className="text-gray-700">
              auth_mode
              <select
                value={webhookAuthModeInput}
                onChange={(event) => setWebhookAuthModeInput(event.target.value as SequenceWebhookAuthMode)}
                className="mt-1 w-full px-2 py-1 rounded border border-gray-300 bg-white"
              >
                <option value="none">none</option>
                <option value="bearer">bearer</option>
                <option value="hmac_sha256">hmac_sha256</option>
              </select>
            </label>
            <label className="text-gray-700 md:col-span-2">
              secret_token
              <input
                type="password"
                value={webhookSecretTokenInput}
                onChange={(event) => setWebhookSecretTokenInput(event.target.value)}
                placeholder={editingWebhookId ? "(opcional) actualizar secreto" : "token/secreto"}
                className="mt-1 w-full px-2 py-1 rounded border border-gray-300 bg-white"
              />
              <div className="mt-1 text-[10px] text-gray-500">
                {webhookAuthModeInput === "none"
                  ? "none: no agrega cabeceras de autenticacion."
                  : webhookAuthModeInput === "bearer"
                    ? "bearer: envia Authorization: Bearer <token>."
                    : "hmac_sha256: envia X-Webhook-Timestamp, X-Webhook-Signature y X-Webhook-Id."}
              </div>
            </label>
            <label className="text-gray-700">
              min_severity
              <select
                value={webhookSeverityInput}
                onChange={(event) => setWebhookSeverityInput(event.target.value as SequenceNotificationSeverity)}
                className="mt-1 w-full px-2 py-1 rounded border border-gray-300 bg-white"
              >
                <option value="info">info</option>
                <option value="warning">warning</option>
                <option value="critical">critical</option>
              </select>
            </label>
            <label className="text-gray-700">
              payload_template_mode
              <select
                value={webhookTemplateModeInput}
                onChange={(event) => {
                  const nextMode = event.target.value as SequenceWebhookPayloadTemplateMode;
                  setWebhookTemplateModeInput(nextMode);
                  if (nextMode === "custom" && webhookTemplateInput.trim() === "") {
                    setWebhookTemplateInput(JSON.stringify(DEFAULT_CUSTOM_TEMPLATE, null, 2));
                  }
                }}
                className="mt-1 w-full px-2 py-1 rounded border border-gray-300 bg-white"
              >
                <option value="default">default</option>
                <option value="compact">compact</option>
                <option value="custom">custom</option>
              </select>
            </label>
          </div>
          <label className="text-[11px] text-gray-700 block">
            enabled_types (coma o salto de linea)
            <textarea
              value={webhookTypesInput}
              onChange={(event) => setWebhookTypesInput(event.target.value)}
              rows={3}
              className="mt-1 w-full px-2 py-1 rounded border border-gray-300 bg-white"
            />
          </label>

          {webhookTemplateModeInput === "custom" ? (
            <label className="text-[11px] text-gray-700 block">
              payload_template (JSON)
              <textarea
                value={webhookTemplateInput}
                onChange={(event) => setWebhookTemplateInput(event.target.value)}
                rows={6}
                className="mt-1 w-full px-2 py-1 rounded border border-gray-300 bg-white font-mono text-[11px]"
              />
            </label>
          ) : null}

          <label className="text-[11px] text-gray-700 block">
            preview payload
            <textarea
              value={webhookTemplatePreview}
              readOnly
              rows={6}
              className="mt-1 w-full px-2 py-1 rounded border border-gray-200 bg-gray-100 font-mono text-[11px] text-gray-700"
            />
          </label>

          {formError ? (
            <div className="px-2 py-2 rounded border border-red-200 bg-red-50 text-[11px] text-red-700">{formError}</div>
          ) : null}

          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              disabled={webhookSaving}
              onClick={() => void saveWebhook()}
              className="px-3 py-1 text-xs font-semibold rounded border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
            >
              {webhookSaving ? "Guardando..." : editingWebhookId ? "Guardar cambios" : "Crear webhook"}
            </button>
            <button
              type="button"
              disabled={webhookSaving}
              onClick={resetForm}
              className="px-3 py-1 text-xs font-semibold rounded border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
            >
              Limpiar formulario
            </button>
          </div>
        </div>
      </div>

      {previewResponse ? (
        <div className="mt-3 p-3 rounded border border-gray-200 bg-gray-50 space-y-2">
          <div className="flex flex-wrap items-center gap-2 justify-between">
            <div className="text-[11px] font-semibold text-gray-600">Preview webhook payload</div>
            <button
              type="button"
              onClick={() => setPreviewResponse(null)}
              className="px-2 py-0.5 rounded border border-gray-300 bg-white text-[11px] text-gray-700"
            >
              Cerrar preview
            </button>
          </div>
          <div className="flex flex-wrap gap-1 text-[10px]">
            <span className="px-2 py-0.5 rounded border border-gray-300 bg-gray-100 text-gray-700">
              webhook: {previewResponse.webhook_id}
            </span>
            <span className="px-2 py-0.5 rounded border border-gray-300 bg-gray-100 text-gray-700">
              auth: {previewResponse.auth_mode}
            </span>
            <span className="px-2 py-0.5 rounded border border-gray-300 bg-gray-100 text-gray-700">
              template: {previewResponse.payload_template_mode}
            </span>
          </div>
          <label className="text-[11px] text-gray-700 block">
            rendered_payload
            <textarea
              value={JSON.stringify(previewResponse.rendered_payload, null, 2)}
              readOnly
              rows={8}
              className="mt-1 w-full px-2 py-1 rounded border border-gray-200 bg-gray-100 font-mono text-[11px] text-gray-700"
            />
          </label>
          <label className="text-[11px] text-gray-700 block">
            rendered_headers
            <textarea
              value={JSON.stringify(previewResponse.rendered_headers, null, 2)}
              readOnly
              rows={6}
              className="mt-1 w-full px-2 py-1 rounded border border-gray-200 bg-gray-100 font-mono text-[11px] text-gray-700"
            />
          </label>
          <div className="text-[11px] text-gray-600 break-all">
            signature_preview: {previewResponse.signature_preview ?? "-"}
          </div>
        </div>
      ) : null}

      {webhookHealthLoading && !webhookHealthResponse ? (
        <div className="mt-3 text-[11px] text-gray-500">Cargando diagnóstico del webhook...</div>
      ) : null}

      {webhookHealthResponse ? (
        <div className="mt-3 p-3 rounded border border-gray-200 bg-gray-50 space-y-2">
          <div className="flex flex-wrap items-center gap-2 justify-between">
            <div className="text-[11px] font-semibold text-gray-600">Detalle ampliado del webhook</div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => void loadWebhookHealth(webhookHealthResponse.webhook.webhook_id, false)}
                className="px-2 py-0.5 rounded border border-gray-300 bg-white text-[11px] text-gray-700"
              >
                Refrescar salud
              </button>
              <button
                type="button"
                onClick={() => {
                  setSelectedWebhookHealthId(null);
                  setWebhookHealthResponse(null);
                  setWebhookHealthError("");
                }}
                className="px-2 py-0.5 rounded border border-gray-300 bg-white text-[11px] text-gray-700"
              >
                Cerrar detalle
              </button>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span className="px-2 py-0.5 rounded border border-gray-300 bg-white text-[11px] text-gray-700">
              webhook: {webhookHealthResponse.webhook.name}
            </span>
            <span className="px-2 py-0.5 rounded border text-[10px]" style={getWebhookHealthStyle(webhookHealthResponse.health_status)}>
              {formatWebhookHealthLabel(webhookHealthResponse.health_status)}
            </span>
            <span className="px-2 py-0.5 rounded border border-gray-300 bg-white text-[11px] text-gray-700">
              enabled: {webhookHealthResponse.webhook.is_enabled ? "true" : "false"}
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-[11px]">
            <div className="px-2 py-1 rounded border border-gray-200 bg-white">total={webhookHealthResponse.operational_summary.total_deliveries}</div>
            <div className="px-2 py-1 rounded border border-green-200 bg-green-50">sent={webhookHealthResponse.operational_summary.sent_deliveries}</div>
            <div className="px-2 py-1 rounded border border-red-200 bg-red-50">failed={webhookHealthResponse.operational_summary.failed_deliveries}</div>
            <div className="px-2 py-1 rounded border border-amber-200 bg-amber-50">pending={webhookHealthResponse.operational_summary.pending_deliveries}</div>
            <div className="px-2 py-1 rounded border border-red-200 bg-red-50">exhausted={webhookHealthResponse.operational_summary.exhausted_deliveries}</div>
            <div className="px-2 py-1 rounded border border-gray-200 bg-white">retries={webhookHealthResponse.operational_summary.total_retries}</div>
            <div className="px-2 py-1 rounded border border-gray-200 bg-white">ratio={(webhookHealthResponse.operational_summary.failure_ratio * 100).toFixed(1)}%</div>
            <div className="px-2 py-1 rounded border border-gray-200 bg-white">recent_failed={webhookHealthResponse.operational_summary.recent_failed_deliveries}</div>
          </div>

          <div className="text-[11px] text-gray-600">
            last_delivery_at: {formatTimestamp(webhookHealthResponse.operational_summary.last_delivery_at)} | last_success_at: {formatTimestamp(webhookHealthResponse.operational_summary.last_success_at)} | last_failure_at: {formatTimestamp(webhookHealthResponse.operational_summary.last_failure_at)}
          </div>

          <div>
            <div className="text-[11px] font-semibold text-gray-600">Alertas activas</div>
            {webhookHealthResponse.alerts.length > 0 ? (
              <ul className="mt-1 space-y-1 text-[11px] text-amber-700">
                {webhookHealthResponse.alerts.map((alert, index) => (
                  <li key={`webhook-health-alert-${index}`}>{alert}</li>
                ))}
              </ul>
            ) : (
              <div className="mt-1 text-[11px] text-green-700">Sin alertas activas.</div>
            )}
          </div>

          <div>
            <div className="text-[11px] font-semibold text-gray-600">Últimas señales relevantes</div>
            {webhookHealthResponse.recent_signals.length > 0 ? (
              <div className="mt-1 space-y-1 max-h-40 overflow-auto pr-1">
                {webhookHealthResponse.recent_signals.map((signal, index) => (
                  <div key={`webhook-signal-${index}`} className="px-2 py-1 rounded border border-gray-200 bg-white">
                    <div className="flex flex-wrap items-center gap-2 text-[10px] text-gray-600">
                      <span className="px-2 py-0.5 rounded border border-gray-300 bg-gray-100">{signal.code}</span>
                      <span className="px-2 py-0.5 rounded border" style={getSeverityStyle(signal.severity)}>{signal.severity}</span>
                      <span>{formatTimestamp(signal.observed_at)}</span>
                    </div>
                    <div className="mt-1 text-[11px] text-gray-700 break-words">{signal.message}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="mt-1 text-[11px] text-gray-500">Sin señales recientes.</div>
            )}
          </div>
        </div>
      ) : null}

      <div className="mt-3 p-3 rounded border border-gray-200 bg-gray-50">
        <div className="flex flex-wrap items-center gap-2 justify-between">
          <div className="text-[11px] font-semibold text-gray-600">Entregas recientes</div>
          <div className="flex items-center gap-2 text-[11px]">
            <button
              type="button"
              disabled={processingRetries || deliveriesLoading}
              onClick={() => void processPendingRetries()}
              className="px-2 py-1 rounded border border-gray-300 bg-white text-[11px] text-gray-700 disabled:opacity-50"
            >
              {processingRetries ? "Procesando..." : "Procesar retries pendientes"}
            </button>
            <label className="text-gray-600">Filtrar webhook</label>
            <select
              value={deliveriesWebhookFilter}
              onChange={(event) => setDeliveriesWebhookFilter(event.target.value)}
              className="px-2 py-1 rounded border border-gray-300 bg-white text-[11px]"
            >
              <option value="">Todos</option>
              {webhooks.map((webhook) => (
                <option key={`delivery-filter-${webhook.webhook_id}`} value={webhook.webhook_id}>
                  {webhook.name}
                </option>
              ))}
            </select>
            <label className="text-gray-600">Tipo</label>
            <select
              value={deliveriesTypeFilter}
              onChange={(event) => setDeliveriesTypeFilter(event.target.value as "all" | "notification" | "test")}
              className="px-2 py-1 rounded border border-gray-300 bg-white text-[11px]"
            >
              <option value="all">Todos</option>
              <option value="notification">notification</option>
              <option value="test">test</option>
            </select>
          </div>
        </div>

        <div className="mt-2 grid grid-cols-1 md:grid-cols-[1fr_1fr_auto] gap-2 items-end text-[11px]">
          <label className="text-gray-700">
            left delivery
            <select
              value={compareLeftDeliveryId}
              onChange={(event) => setCompareLeftDeliveryId(event.target.value)}
              className="mt-1 w-full px-2 py-1 rounded border border-gray-300 bg-white"
            >
              <option value="">Seleccionar...</option>
              {deliveries.map((delivery) => (
                <option key={`compare-left-${delivery.delivery_id}`} value={delivery.delivery_id}>
                  {delivery.delivery_id} ({delivery.is_test ? "test" : "notification"})
                </option>
              ))}
            </select>
          </label>
          <label className="text-gray-700">
            right delivery
            <select
              value={compareRightDeliveryId}
              onChange={(event) => setCompareRightDeliveryId(event.target.value)}
              className="mt-1 w-full px-2 py-1 rounded border border-gray-300 bg-white"
            >
              <option value="">Seleccionar...</option>
              {deliveries.map((delivery) => (
                <option key={`compare-right-${delivery.delivery_id}`} value={delivery.delivery_id}>
                  {delivery.delivery_id} ({delivery.is_test ? "test" : "notification"})
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            disabled={compareLoading}
            onClick={() => void compareSelectedDeliveries()}
            className="px-3 py-1 rounded border border-gray-300 bg-white text-[11px] text-gray-700 disabled:opacity-50"
          >
            {compareLoading ? "Comparando..." : "Comparar deliveries"}
          </button>
        </div>

        {deliveriesLoading ? (
          <div className="mt-2 text-[11px] text-gray-500">Cargando entregas...</div>
        ) : deliveries.length > 0 ? (
          <div className="mt-2 space-y-2 max-h-72 overflow-auto pr-1">
            {deliveries.map((delivery) => {
              const payloadMessage =
                typeof delivery.payload?.message === "string"
                  ? delivery.payload.message
                  : "";

              return (
                <div key={delivery.delivery_id} className="p-2 rounded border border-gray-200 bg-white">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] border" style={getDeliveryStatusStyle(delivery.delivery_status)}>
                      {delivery.delivery_status}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] border border-gray-300 bg-gray-100 text-gray-700">
                      {delivery.is_test ? "test" : "notification"}
                    </span>
                    <span className="text-[11px] text-gray-500">
                      webhook: {webhookNameById.get(delivery.webhook_id) ?? delivery.webhook_id}
                    </span>
                    <span className="ml-auto text-[11px] text-gray-500">{formatTimestamp(delivery.created_at)}</span>
                  </div>
                  <div className="mt-1 text-[11px] text-gray-600">
                    notif: {delivery.notification_id} | collection: {delivery.collection_id}
                  </div>
                  {payloadMessage ? (
                    <div className="mt-1 text-xs text-gray-700">{payloadMessage}</div>
                  ) : null}
                  <div className="mt-1 text-[11px] text-gray-500">
                    attempts: {delivery.attempt_count}/{delivery.max_attempts} | last_attempt_at: {formatTimestamp(delivery.last_attempt_at)}
                  </div>
                  <div className="mt-1 text-[11px] text-gray-500">
                    template_mode: {delivery.template_mode}
                  </div>
                  <div className="mt-1 text-[11px] text-gray-500">
                    routing_rule: {delivery.routing_rule_name ?? delivery.routing_rule_id ?? "-"}
                  </div>
                  <div className="mt-1 text-[11px] text-gray-500">
                    auth_mode: {delivery.auth_mode}
                    {delivery.signature_timestamp ? ` | signature_ts: ${delivery.signature_timestamp}` : ""}
                  </div>
                  <div className="mt-1 text-[11px] text-gray-500">
                    status_code: {delivery.response_status_code ?? "-"} | delivered_at: {formatTimestamp(delivery.delivered_at)}
                    | next_retry_at: {formatTimestamp(delivery.next_retry_at)}
                  </div>
                  <div className="mt-1 text-[11px] text-gray-500">
                    final_failure_at: {formatTimestamp(delivery.final_failure_at)}
                  </div>
                  {Object.keys(delivery.request_headers || {}).length > 0 ? (
                    <div className="mt-1 text-[11px] text-gray-500 break-all">
                      headers: {Object.entries(delivery.request_headers)
                        .map(([key, value]) => `${key}=${value}`)
                        .join(" | ")}
                    </div>
                  ) : null}
                  {delivery.error_message ? (
                    <div className="mt-1 text-[11px] text-red-700">ultimo error: {delivery.error_message}</div>
                  ) : null}
                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    <button
                      type="button"
                      onClick={() => setSelectedDeliveryId(delivery.delivery_id)}
                      className="px-2 py-0.5 rounded border border-gray-300 bg-white text-[11px] text-gray-700"
                    >
                      Ver detalle
                    </button>
                    <button
                      type="button"
                      onClick={() => setCompareLeftDeliveryId(delivery.delivery_id)}
                      className="px-2 py-0.5 rounded border border-gray-300 bg-white text-[11px] text-gray-700"
                    >
                      Set left
                    </button>
                    <button
                      type="button"
                      onClick={() => setCompareRightDeliveryId(delivery.delivery_id)}
                      className="px-2 py-0.5 rounded border border-gray-300 bg-white text-[11px] text-gray-700"
                    >
                      Set right
                    </button>
                  </div>
                  {delivery.delivery_status === "failed" ? (
                    <div className="mt-2">
                      <button
                        type="button"
                        disabled={
                          retryDeliveryId === delivery.delivery_id ||
                          delivery.attempt_count >= delivery.max_attempts
                        }
                        onClick={() => void retryDelivery(delivery)}
                        className="px-2 py-0.5 rounded border border-gray-300 bg-white text-[11px] text-gray-700 disabled:opacity-50"
                      >
                        {retryDeliveryId === delivery.delivery_id
                          ? "Reintentando..."
                          : delivery.attempt_count >= delivery.max_attempts
                            ? "Agotado"
                            : "Reintentar"}
                      </button>
                    </div>
                  ) : null}
                </div>
              );
            })}
          </div>
        ) : (
          <div className="mt-2 text-[11px] text-gray-500">Sin entregas registradas.</div>
        )}

        {selectedDelivery ? (
          <div className="mt-3 p-2 rounded border border-gray-200 bg-white space-y-2">
            <div className="flex flex-wrap items-center gap-2 justify-between">
              <div className="text-[11px] font-semibold text-gray-600">Detalle delivery</div>
              <button
                type="button"
                onClick={() => setSelectedDeliveryId(null)}
                className="px-2 py-0.5 rounded border border-gray-300 bg-white text-[11px] text-gray-700"
              >
                Cerrar detalle
              </button>
            </div>
            <div className="text-[11px] text-gray-600">
              id: {selectedDelivery.delivery_id} | webhook: {selectedDelivery.webhook_id} | status: {selectedDelivery.delivery_status}
            </div>
            <div className="text-[11px] text-gray-600">
              auth_mode: {selectedDelivery.auth_mode} | template_mode: {selectedDelivery.template_mode} | is_test: {selectedDelivery.is_test ? "true" : "false"}
            </div>
            <div className="text-[11px] text-gray-600">
              routing_rule: {selectedDelivery.routing_rule_name ?? selectedDelivery.routing_rule_id ?? "-"}
            </div>
            <label className="text-[11px] text-gray-700 block">
              payload final enviado
              <textarea
                value={JSON.stringify(selectedDelivery.payload ?? {}, null, 2)}
                readOnly
                rows={8}
                className="mt-1 w-full px-2 py-1 rounded border border-gray-200 bg-gray-100 font-mono text-[11px] text-gray-700"
              />
            </label>
            <label className="text-[11px] text-gray-700 block">
              headers enviados
              <textarea
                value={JSON.stringify(selectedDelivery.request_headers ?? {}, null, 2)}
                readOnly
                rows={6}
                className="mt-1 w-full px-2 py-1 rounded border border-gray-200 bg-gray-100 font-mono text-[11px] text-gray-700"
              />
            </label>
          </div>
        ) : null}

        {compareResponse ? (
          <div className="mt-3 p-2 rounded border border-gray-200 bg-white space-y-2">
            <div className="flex flex-wrap items-center gap-2 justify-between">
              <div className="text-[11px] font-semibold text-gray-600">Diff de deliveries</div>
              <button
                type="button"
                onClick={() => setCompareResponse(null)}
                className="px-2 py-0.5 rounded border border-gray-300 bg-white text-[11px] text-gray-700"
              >
                Cerrar diff
              </button>
            </div>
            <div className="text-[11px] text-gray-600 break-all">
              left: {compareResponse.left_delivery_id} | right: {compareResponse.right_delivery_id}
            </div>
            <div className="text-[11px] text-gray-600">
              auth: {compareResponse.auth_mode_left} to {compareResponse.auth_mode_right} | template: {compareResponse.payload_template_mode_left} to {compareResponse.payload_template_mode_right}
            </div>
            <label className="text-[11px] text-gray-700 block">
              payload_diff
              <textarea
                value={JSON.stringify(compareResponse.payload_diff, null, 2)}
                readOnly
                rows={8}
                className="mt-1 w-full px-2 py-1 rounded border border-gray-200 bg-gray-100 font-mono text-[11px] text-gray-700"
              />
            </label>
            <label className="text-[11px] text-gray-700 block">
              headers_diff
              <textarea
                value={JSON.stringify(compareResponse.headers_diff, null, 2)}
                readOnly
                rows={6}
                className="mt-1 w-full px-2 py-1 rounded border border-gray-200 bg-gray-100 font-mono text-[11px] text-gray-700"
              />
            </label>
          </div>
        ) : null}
      </div>

      <div className="mt-4 p-3 rounded border border-blue-200 bg-blue-50">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <div className="text-xs font-semibold text-blue-800">Canales adicionales (Slack / Telegram)</div>
            <div className="text-[11px] text-blue-700">Gestion de destinos de notificacion fuera de webhooks clasicos.</div>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              disabled={channelsLoading}
              onClick={() => void loadChannels(false)}
              className="px-3 py-1 text-xs font-semibold rounded border border-blue-300 bg-white text-blue-800 disabled:opacity-50"
            >
              {channelsLoading ? "Actualizando..." : "Recargar canales"}
            </button>
            <button
              type="button"
              disabled={channelDeliveriesLoading}
              onClick={() => void loadChannelDeliveries(false)}
              className="px-3 py-1 text-xs font-semibold rounded border border-blue-300 bg-white text-blue-800 disabled:opacity-50"
            >
              {channelDeliveriesLoading ? "Actualizando..." : "Recargar entregas canales"}
            </button>
          </div>
        </div>

        <div className="mt-3 grid grid-cols-1 xl:grid-cols-2 gap-3">
          <div className="p-3 rounded border border-blue-200 bg-white">
            <div className="text-[11px] font-semibold text-blue-700">Canales configurados</div>
            {channels.length > 0 ? (
              <div className="mt-2 space-y-2 max-h-72 overflow-auto pr-1">
                {channels.map((channel) => (
                  <div key={channel.channel_id} className="p-2 rounded border border-blue-200 bg-blue-50">
                    <div className="flex items-center gap-2">
                      <div className="font-semibold text-xs text-blue-900 truncate">{channel.name}</div>
                      <span className="px-2 py-0.5 rounded border border-blue-300 bg-white text-[10px] text-blue-800">
                        {channel.channel_type}
                      </span>
                      <span
                        className={`ml-auto px-2 py-0.5 rounded border text-[10px] ${channel.is_enabled ? "border-green-300 bg-green-50 text-green-700" : "border-gray-300 bg-gray-100 text-gray-600"}`}
                      >
                        {channel.is_enabled ? "enabled" : "disabled"}
                      </span>
                    </div>
                    <div className="mt-1 text-[11px] text-blue-700">
                      min={channel.min_severity} | types={channel.enabled_types.length > 0 ? channel.enabled_types.join(", ") : "todos"}
                    </div>
                    <div className="mt-2 flex flex-wrap items-center gap-2">
                      <button
                        type="button"
                        onClick={() => startEditChannel(channel)}
                        className="px-2 py-0.5 rounded border border-blue-300 bg-white text-[11px] text-blue-800"
                      >
                        Editar
                      </button>
                      <button
                        type="button"
                        disabled={channelActionId === channel.channel_id}
                        onClick={() => void toggleChannelEnabled(channel)}
                        className="px-2 py-0.5 rounded border border-blue-300 bg-white text-[11px] text-blue-800 disabled:opacity-50"
                      >
                        {channelActionId === channel.channel_id
                          ? "Guardando..."
                          : channel.is_enabled
                            ? "Deshabilitar"
                            : "Habilitar"}
                      </button>
                      <button
                        type="button"
                        disabled={channelTestId === channel.channel_id}
                        onClick={() => void sendChannelTestEvent(channel)}
                        className="px-2 py-0.5 rounded border border-blue-300 bg-white text-[11px] text-blue-800 disabled:opacity-50"
                      >
                        {channelTestId === channel.channel_id ? "Enviando..." : "Send test event"}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="mt-2 text-[11px] text-blue-700">No hay canales configurados.</div>
            )}
          </div>

          <div className="p-3 rounded border border-blue-200 bg-white space-y-2">
            <div className="text-[11px] font-semibold text-blue-700">
              {editingChannelId ? "Editar canal" : "Crear canal"}
            </div>
            {!editingChannelId ? (
              <label className="text-[11px] text-blue-800 block">
                channel_type
                <select
                  value={channelTypeInput}
                  onChange={(event) => setChannelTypeInput(event.target.value as SequenceNotificationChannelType)}
                  className="mt-1 w-full px-2 py-1 rounded border border-blue-300 bg-white"
                >
                  <option value="slack">slack</option>
                  <option value="telegram">telegram</option>
                </select>
              </label>
            ) : (
              <div className="text-[11px] text-blue-800">channel_type: {channelTypeInput}</div>
            )}
            <input
              type="text"
              value={channelNameInput}
              onChange={(event) => setChannelNameInput(event.target.value)}
              placeholder="name"
              className="w-full px-2 py-1 text-xs rounded border border-blue-300 bg-white"
            />
            <label className="inline-flex items-center gap-2 text-[11px] text-blue-800">
              <input
                type="checkbox"
                checked={channelEnabledInput}
                onChange={(event) => setChannelEnabledInput(event.target.checked)}
              />
              is_enabled
            </label>
            <label className="text-[11px] text-blue-800 block">
              min_severity
              <select
                value={channelMinSeverityInput}
                onChange={(event) => setChannelMinSeverityInput(event.target.value as SequenceNotificationSeverity)}
                className="mt-1 w-full px-2 py-1 rounded border border-blue-300 bg-white"
              >
                <option value="info">info</option>
                <option value="warning">warning</option>
                <option value="critical">critical</option>
              </select>
            </label>
            <label className="text-[11px] text-blue-800 block">
              enabled_types (coma o salto de linea)
              <textarea
                value={channelTypesInput}
                onChange={(event) => setChannelTypesInput(event.target.value)}
                rows={2}
                className="mt-1 w-full px-2 py-1 rounded border border-blue-300 bg-white"
              />
            </label>

            {channelTypeInput === "slack" ? (
              <input
                type="text"
                value={channelSlackWebhookInput}
                onChange={(event) => setChannelSlackWebhookInput(event.target.value)}
                placeholder="config.webhook_url"
                className="w-full px-2 py-1 text-xs rounded border border-blue-300 bg-white"
              />
            ) : null}
            {channelTypeInput === "telegram" ? (
              <>
                <input
                  type="password"
                  value={channelTelegramTokenInput}
                  onChange={(event) => setChannelTelegramTokenInput(event.target.value)}
                  placeholder={editingChannelId ? "config.bot_token (opcional actualizar)" : "config.bot_token"}
                  className="w-full px-2 py-1 text-xs rounded border border-blue-300 bg-white"
                />
                <input
                  type="text"
                  value={channelTelegramChatIdInput}
                  onChange={(event) => setChannelTelegramChatIdInput(event.target.value)}
                  placeholder="config.chat_id"
                  className="w-full px-2 py-1 text-xs rounded border border-blue-300 bg-white"
                />
              </>
            ) : null}

            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                disabled={channelSaving}
                onClick={() => void saveChannel()}
                className="px-3 py-1 text-xs font-semibold rounded border border-blue-300 bg-white text-blue-800 disabled:opacity-50"
              >
                {channelSaving ? "Guardando..." : editingChannelId ? "Guardar cambios" : "Crear canal"}
              </button>
              <button
                type="button"
                disabled={channelSaving}
                onClick={resetChannelForm}
                className="px-3 py-1 text-xs font-semibold rounded border border-blue-300 bg-white text-blue-800 disabled:opacity-50"
              >
                Limpiar formulario
              </button>
            </div>
          </div>
        </div>

        <div className="mt-3 p-3 rounded border border-blue-200 bg-white">
          <div className="flex flex-wrap items-center gap-2 justify-between">
            <div className="text-[11px] font-semibold text-blue-700">Entregas recientes de canales</div>
            <div className="flex items-center gap-2 text-[11px]">
              <button
                type="button"
                disabled={processingChannelRetries || channelDeliveriesLoading}
                onClick={() => void processChannelPendingRetries()}
                className="px-2 py-1 rounded border border-blue-300 bg-white text-[11px] text-blue-800 disabled:opacity-50"
              >
                {processingChannelRetries ? "Procesando..." : "Procesar retries"}
              </button>
              <label className="text-blue-700">Filtrar canal</label>
              <select
                value={channelDeliveriesFilter}
                onChange={(event) => setChannelDeliveriesFilter(event.target.value)}
                className="px-2 py-1 rounded border border-blue-300 bg-white text-[11px]"
              >
                <option value="">Todos</option>
                {channels.map((channel) => (
                  <option key={`channel-delivery-filter-${channel.channel_id}`} value={channel.channel_id}>
                    {channel.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {channelDeliveries.length > 0 ? (
            <div className="mt-2 space-y-2 max-h-72 overflow-auto pr-1">
              {channelDeliveries.map((delivery) => (
                <div key={delivery.delivery_id} className="p-2 rounded border border-blue-200 bg-blue-50">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] border" style={getDeliveryStatusStyle(delivery.delivery_status)}>
                      {delivery.delivery_status}
                    </span>
                    <span className="px-2 py-0.5 rounded border border-blue-300 bg-white text-[10px] text-blue-800">
                      {delivery.channel_type}
                    </span>
                    <span className="text-[11px] text-blue-700">channel: {delivery.channel_id}</span>
                    <span className="ml-auto text-[11px] text-blue-700">{formatTimestamp(delivery.created_at)}</span>
                  </div>
                  <div className="mt-1 text-[11px] text-blue-700 break-all">{delivery.message_text}</div>
                  <div className="mt-1 text-[11px] text-blue-700">
                    attempts: {delivery.attempt_count}/{delivery.max_attempts} | status_code: {delivery.response_status_code ?? "-"} | next_retry_at: {formatTimestamp(delivery.next_retry_at)}
                  </div>
                  <div className="mt-1 text-[11px] text-blue-700">
                    routing_rule: {delivery.routing_rule_name ?? delivery.routing_rule_id ?? "-"}
                  </div>
                  {delivery.error_message ? (
                    <div className="mt-1 text-[11px] text-red-700">ultimo error: {delivery.error_message}</div>
                  ) : null}
                  {delivery.delivery_status === "failed" ? (
                    <button
                      type="button"
                      disabled={channelRetryId === delivery.delivery_id || delivery.attempt_count >= delivery.max_attempts}
                      onClick={() => void retryChannelDelivery(delivery)}
                      className="mt-2 px-2 py-0.5 rounded border border-blue-300 bg-white text-[11px] text-blue-800 disabled:opacity-50"
                    >
                      {channelRetryId === delivery.delivery_id
                        ? "Reintentando..."
                        : delivery.attempt_count >= delivery.max_attempts
                          ? "Agotado"
                          : "Reintentar"}
                    </button>
                  ) : null}
                </div>
              ))}
            </div>
          ) : (
            <div className="mt-2 text-[11px] text-blue-700">Sin entregas de canales.</div>
          )}
        </div>

        <div className="mt-3 p-3 rounded border border-indigo-200 bg-indigo-50">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="text-[11px] font-semibold text-indigo-800">Reglas de ruteo de alertas</div>
            <button
              type="button"
              disabled={routingRulesLoading}
              onClick={() => void loadRoutingRules(false)}
              className="px-3 py-1 text-xs font-semibold rounded border border-indigo-300 bg-white text-indigo-800 disabled:opacity-50"
            >
              {routingRulesLoading ? "Actualizando..." : "Recargar reglas"}
            </button>
          </div>

          <div className="mt-2 grid grid-cols-1 xl:grid-cols-2 gap-3">
            <div className="p-3 rounded border border-indigo-200 bg-white">
              <div className="text-[11px] font-semibold text-indigo-700">Reglas actuales</div>
              {routingRules.length > 0 ? (
                <div className="mt-2 space-y-2 max-h-72 overflow-auto pr-1">
                  {routingRules.map((rule) => (
                    <div key={rule.rule_id} className="p-2 rounded border border-indigo-200 bg-indigo-50">
                      <div className="flex flex-wrap items-center gap-2">
                        <div className="font-semibold text-xs text-indigo-900 truncate">{rule.name}</div>
                        <span
                          className={`ml-auto px-2 py-0.5 rounded border text-[10px] ${rule.is_enabled ? "border-green-300 bg-green-50 text-green-700" : "border-gray-300 bg-gray-100 text-gray-600"}`}
                        >
                          {rule.is_enabled ? "enabled" : "disabled"}
                        </span>
                      </div>
                      <div className="mt-1 text-[11px] text-indigo-700">
                        target: {rule.target_name ?? rule.target_channel_id} ({rule.target_channel_kind})
                      </div>
                      <div className="mt-1 text-[11px] text-indigo-700">
                        min={rule.min_severity} | types={rule.match_types.length > 0 ? rule.match_types.join(", ") : "todos"}
                      </div>
                      <div className="mt-1 text-[11px] text-indigo-700">
                        collection={rule.match_collection_id ?? "*"} | health={rule.match_health_status ?? "*"}
                      </div>
                      <div className="mt-2 flex flex-wrap items-center gap-2">
                        <button
                          type="button"
                          onClick={() => startEditRoutingRule(rule)}
                          className="px-2 py-0.5 rounded border border-indigo-300 bg-white text-[11px] text-indigo-800"
                        >
                          Editar
                        </button>
                        <button
                          type="button"
                          disabled={ruleActionId === rule.rule_id}
                          onClick={() => void toggleRoutingRule(rule)}
                          className="px-2 py-0.5 rounded border border-indigo-300 bg-white text-[11px] text-indigo-800 disabled:opacity-50"
                        >
                          {ruleActionId === rule.rule_id
                            ? "Guardando..."
                            : rule.is_enabled
                              ? "Deshabilitar"
                              : "Habilitar"}
                        </button>
                        <button
                          type="button"
                          disabled={ruleActionId === rule.rule_id}
                          onClick={() => void removeRoutingRule(rule)}
                          className="px-2 py-0.5 rounded border border-red-300 bg-white text-[11px] text-red-700 disabled:opacity-50"
                        >
                          Eliminar
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="mt-2 text-[11px] text-indigo-700">No hay reglas definidas.</div>
              )}
            </div>

            <div className="p-3 rounded border border-indigo-200 bg-white space-y-2">
              <div className="text-[11px] font-semibold text-indigo-700">
                {editingRoutingRuleId ? "Editar regla" : "Crear regla"}
              </div>
              <input
                type="text"
                value={ruleNameInput}
                onChange={(event) => setRuleNameInput(event.target.value)}
                placeholder="name"
                className="w-full px-2 py-1 text-xs rounded border border-indigo-300 bg-white"
              />
              <label className="inline-flex items-center gap-2 text-[11px] text-indigo-800">
                <input
                  type="checkbox"
                  checked={ruleEnabledInput}
                  onChange={(event) => setRuleEnabledInput(event.target.checked)}
                />
                is_enabled
              </label>
              <label className="text-[11px] text-indigo-800 block">
                target_channel
                <select
                  value={ruleTargetRefInput}
                  onChange={(event) => setRuleTargetRefInput(event.target.value)}
                  className="mt-1 w-full px-2 py-1 rounded border border-indigo-300 bg-white"
                >
                  <option value="">Seleccionar destino...</option>
                  {routingTargetOptions.map((option) => (
                    <option key={`routing-target-${option.key}`} value={option.key}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-[11px] text-indigo-800 block">
                match_types (coma o salto de linea)
                <textarea
                  value={ruleTypesInput}
                  onChange={(event) => setRuleTypesInput(event.target.value)}
                  rows={2}
                  className="mt-1 w-full px-2 py-1 rounded border border-indigo-300 bg-white"
                />
              </label>
              <label className="text-[11px] text-indigo-800 block">
                min_severity
                <select
                  value={ruleMinSeverityInput}
                  onChange={(event) => setRuleMinSeverityInput(event.target.value as SequenceNotificationSeverity)}
                  className="mt-1 w-full px-2 py-1 rounded border border-indigo-300 bg-white"
                >
                  <option value="info">info</option>
                  <option value="warning">warning</option>
                  <option value="critical">critical</option>
                </select>
              </label>
              <input
                type="text"
                value={ruleMatchCollectionIdInput}
                onChange={(event) => setRuleMatchCollectionIdInput(event.target.value)}
                placeholder="match_collection_id (opcional)"
                className="w-full px-2 py-1 text-xs rounded border border-indigo-300 bg-white"
              />
              <label className="text-[11px] text-indigo-800 block">
                match_health_status
                <select
                  value={ruleMatchHealthStatusInput}
                  onChange={(event) => setRuleMatchHealthStatusInput(event.target.value as "all" | "green" | "yellow" | "red")}
                  className="mt-1 w-full px-2 py-1 rounded border border-indigo-300 bg-white"
                >
                  <option value="all">all</option>
                  <option value="green">green</option>
                  <option value="yellow">yellow</option>
                  <option value="red">red</option>
                </select>
              </label>

              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  disabled={ruleSaving}
                  onClick={() => void saveRoutingRule()}
                  className="px-3 py-1 text-xs font-semibold rounded border border-indigo-300 bg-white text-indigo-800 disabled:opacity-50"
                >
                  {ruleSaving ? "Guardando..." : editingRoutingRuleId ? "Guardar cambios" : "Crear regla"}
                </button>
                <button
                  type="button"
                  disabled={ruleSaving}
                  onClick={resetRoutingRuleForm}
                  className="px-3 py-1 text-xs font-semibold rounded border border-indigo-300 bg-white text-indigo-800 disabled:opacity-50"
                >
                  Limpiar formulario
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
