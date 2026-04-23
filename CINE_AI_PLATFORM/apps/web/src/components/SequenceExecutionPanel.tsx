import { useCallback, useEffect, useMemo, useState, type CSSProperties, type FormEvent } from "react";
import { jsPDF } from "jspdf";

import {
  addSequenceExecutionCollectionItems,
  createSequenceExecutionCollection,
  getSequenceExecutionCollectionAudit,
  getSequenceExecutionCollectionsDashboard,
  getSequenceExecutionCollectionReview,
  getSequenceNotificationPreferences,
  listSequenceExecutionCollections,
  listSequenceNotifications,
  markSequenceNotificationRead,
  removeSequenceExecutionCollectionItem,
  setSequenceExecutionCollectionBest,
  setSequenceExecutionCollectionItemHighlight,
  updateSequenceExecutionCollection,
  updateSequenceNotificationPreferences,
  createSequencePlanAndRender,
  getSequencePlanAndRender,
  getSequencePlanAndRenderReviewHistory,
  listRecentSequenceExecutions,
  retrySequenceShot,
  updateSequencePlanAndRenderMeta,
  updateSequencePlanAndRenderReview,
} from "../services/sequenceApi";
import type {
  RenderJobData,
  SequenceExecutionCollectionAuditResponse,
  SequenceExecutionCollectionsDashboardResponse,
  SequenceExecutionNotification,
  SequenceExecutionNotificationPreferences,
  SequenceExecutionNotificationPreferencesUpdateRequest,
  SequenceNotificationSeverity,
  RetryShotRequest,
  SequenceExecutionCollection,
  SequenceExecutionCollectionReviewResponse,
  SequenceCollectionHealthStatus,
  SequenceExecutionRecentFilters,
  SequenceExecutionRecentItem,
  SequenceExecutionRecentRanking,
  SequenceExecutionReviewHistoryEntry,
  SequenceExecutionReviewStatus,
  SequencePlanAndRenderExecution,
  SequenceShotJobLink,
  SequenceShotPlan,
} from "../types/sequenceExecution";
import SequenceWebhooksPanel from "./SequenceWebhooksPanel";


type SequenceExecutionPanelProps = {
  defaultProjectId?: string;
};

type StatusFilter = "all" | "queued" | "running" | "succeeded" | "failed" | "timeout";

const STATUS_FILTER_OPTIONS: StatusFilter[] = ["all", "queued", "running", "succeeded", "failed", "timeout"];

type RecentRankingFilter = "updated_at_desc" | "most_stable" | "most_problematic" | "most_retries" | "highest_success_ratio";

const RECENT_RANKING_OPTIONS: RecentRankingFilter[] = [
  "updated_at_desc",
  "most_stable",
  "most_problematic",
  "most_retries",
  "highest_success_ratio",
];

const REVIEW_STATUS_OPTIONS: SequenceExecutionReviewStatus[] = ["pending_review", "approved", "rejected"];

type ShotExecutionRow = {
  shot: SequenceShotPlan;
  links: SequenceShotJobLink[];
  latestLink: SequenceShotJobLink | null;
  latestJob: RenderJobData | null;
  retries: Array<{
    link: SequenceShotJobLink;
    job: RenderJobData | null;
  }>;
};

type JobDetailSelection = {
  shotId: string;
  job: RenderJobData;
  link: SequenceShotJobLink | null;
  source: "latest" | "retry";
};

type ExecutionMetrics = {
  requestId: string;
  shotsCount: number;
  jobCount: number;
  totalRetries: number;
  successCount: number;
  failedCount: number;
  timeoutCount: number;
  queuedCount: number;
  runningCount: number;
  successRatio: number;
  shotWithMostRetries: {
    shotId: string;
    retries: number;
  } | null;
  statusDistribution: Array<{
    status: string;
    count: number;
    percent: number;
  }>;
};


function buildShotExecutionRows(execution: SequencePlanAndRenderExecution): ShotExecutionRow[] {
  const jobsById = new Map<string, RenderJobData>();
  for (const job of execution.created_jobs) {
    jobsById.set(job.job_id, job);
  }

  return execution.plan.shots.map((shot) => {
    const links = execution.shot_job_links
      .filter((link) => link.shot_id === shot.shot_id)
      .sort((left, right) => {
        const leftRetry = getLinkRetryIndex(left);
        const rightRetry = getLinkRetryIndex(right);
        if (leftRetry !== rightRetry) {
          return leftRetry - rightRetry;
        }
        return left.job_id.localeCompare(right.job_id);
      });

    const latestLink = links.length > 0 ? links[links.length - 1] : null;
    const latestJob = latestLink ? jobsById.get(latestLink.job_id) ?? null : null;
    const retries = links
      .filter((link) => getLinkRetryIndex(link) > 0)
      .map((link) => ({
        link,
        job: jobsById.get(link.job_id) ?? null,
      }));

    return {
      shot,
      links,
      latestLink,
      latestJob,
      retries,
    };
  });
}


function buildExecutionMetrics(
  execution: SequencePlanAndRenderExecution,
  shotRows: ShotExecutionRow[]
): ExecutionMetrics {
  const counts = {
    queued: 0,
    running: 0,
    succeeded: 0,
    failed: 0,
    timeout: 0,
  };

  const extraStatusCounts = new Map<string, number>();
  for (const job of execution.created_jobs) {
    const status = formatStatus(job.status ? String(job.status) : "unknown");

    if (status in counts) {
      const key = status as keyof typeof counts;
      counts[key] += 1;
      continue;
    }

    extraStatusCounts.set(status, (extraStatusCounts.get(status) ?? 0) + 1);
  }

  const jobCount = execution.created_jobs.length;
  const successRatio = jobCount > 0 ? (counts.succeeded / jobCount) * 100 : 0;

  const totalRetries = execution.shot_job_links.filter((link) => getLinkRetryIndex(link) > 0).length;

  let shotWithMostRetries: ExecutionMetrics["shotWithMostRetries"] = null;
  for (const row of shotRows) {
    const retries = row.retries.length;
    if (retries <= 0) {
      continue;
    }

    if (!shotWithMostRetries || retries > shotWithMostRetries.retries) {
      shotWithMostRetries = {
        shotId: row.shot.shot_id,
        retries,
      };
    }
  }

  const distributionBase = [
    { status: "queued", count: counts.queued },
    { status: "running", count: counts.running },
    { status: "succeeded", count: counts.succeeded },
    { status: "failed", count: counts.failed },
    { status: "timeout", count: counts.timeout },
  ];

  const distribution = [
    ...distributionBase,
    ...Array.from(extraStatusCounts.entries()).map(([status, count]) => ({ status, count })),
  ]
    .filter((item) => item.count > 0 || item.status === "queued" || item.status === "running" || item.status === "succeeded" || item.status === "failed" || item.status === "timeout")
    .map((item) => ({
      ...item,
      percent: jobCount > 0 ? (item.count / jobCount) * 100 : 0,
    }));

  return {
    requestId: execution.request_id,
    shotsCount: execution.plan.shots.length,
    jobCount,
    totalRetries,
    successCount: counts.succeeded,
    failedCount: counts.failed,
    timeoutCount: counts.timeout,
    queuedCount: counts.queued,
    runningCount: counts.running,
    successRatio,
    shotWithMostRetries,
    statusDistribution: distribution,
  };
}


type CompareShotMode = "initial" | "latest" | "history";

const COMPARE_SHOT_MODE_OPTIONS: CompareShotMode[] = ["initial", "latest", "history"];

type ComparisonDiffKind = "same" | "changed" | "missing";

type ShotAttemptSnapshot = {
  retryIndex: number;
  jobId: string | null;
  status: string | null;
  prompt: string | null;
  negativePrompt: string | null;
  renderContext: Record<string, unknown> | null;
  updatedAt: string | null;
};

type ComparableShotData = {
  shotId: string;
  shotType: string | null;
  planPrompt: string | null;
  planNegativePrompt: string | null;
  attempts: ShotAttemptSnapshot[];
  retriesCount: number;
  initialAttempt: ShotAttemptSnapshot | null;
  latestAttempt: ShotAttemptSnapshot | null;
};

type ShotHistorySummary = {
  attemptsCount: number;
  retriesCount: number;
  promptChanges: number;
  negativePromptChanges: number;
  renderContextChanges: number;
};

type ShotComparisonItem = {
  shotId: string;
  leftExists: boolean;
  rightExists: boolean;
  shotTypeLeft: string | null;
  shotTypeRight: string | null;
  promptLeft: string | null;
  promptRight: string | null;
  negativePromptLeft: string | null;
  negativePromptRight: string | null;
  renderContextLeft: Record<string, unknown> | null;
  renderContextRight: Record<string, unknown> | null;
  statusLeft: string | null;
  statusRight: string | null;
  retriesLeft: number;
  retriesRight: number;
  diffShotType: ComparisonDiffKind;
  diffPrompt: ComparisonDiffKind;
  diffNegativePrompt: ComparisonDiffKind;
  diffRenderContext: ComparisonDiffKind;
  diffStatus: ComparisonDiffKind;
  diffRetries: ComparisonDiffKind;
  leftHistory: ShotHistorySummary | null;
  rightHistory: ShotHistorySummary | null;
  leftAttempts: ShotAttemptSnapshot[];
  rightAttempts: ShotAttemptSnapshot[];
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

  return "Error en la operación";
}


function getStatusStyle(status: string): CSSProperties {
  const normalized = status.trim().toLowerCase();

  if (normalized === "queued") {
    return { background: "#eff6ff", color: "#1d4ed8", border: "1px solid #bfdbfe" };
  }
  if (normalized === "running") {
    return { background: "#fef3c7", color: "#92400e", border: "1px solid #fde68a" };
  }
  if (normalized === "succeeded") {
    return { background: "#ecfdf3", color: "#166534", border: "1px solid #86efac" };
  }
  if (normalized === "failed") {
    return { background: "#fee2e2", color: "#991b1b", border: "1px solid #fca5a5" };
  }
  if (normalized === "timeout") {
    return { background: "#f3e8ff", color: "#6b21a8", border: "1px solid #d8b4fe" };
  }

  return { background: "#f3f4f6", color: "#374151", border: "1px solid #d1d5db" };
}


function getReviewStatusStyle(status: SequenceExecutionReviewStatus): CSSProperties {
  if (status === "approved") {
    return { background: "#ecfdf3", color: "#166534", border: "1px solid #86efac" };
  }
  if (status === "rejected") {
    return { background: "#fef2f2", color: "#991b1b", border: "1px solid #fecaca" };
  }
  // pending_review
  return { background: "#f9fafb", color: "#4b5563", border: "1px solid #e5e7eb" };
}


function formatReviewStatusLabel(status: SequenceExecutionReviewStatus): string {
  if (status === "approved") {
    return "Aprobado";
  }
  if (status === "rejected") {
    return "Rechazado";
  }
  return "Pendiente";
}


function getCollectionHealthStyle(status: SequenceCollectionHealthStatus): CSSProperties {
  if (status === "red") {
    return { background: "#fef2f2", color: "#991b1b", border: "1px solid #fecaca" };
  }
  if (status === "yellow") {
    return { background: "#fffbeb", color: "#92400e", border: "1px solid #fde68a" };
  }
  return { background: "#ecfdf3", color: "#166534", border: "1px solid #86efac" };
}


function formatCollectionHealthLabel(status: SequenceCollectionHealthStatus): string {
  if (status === "red") {
    return "Riesgo alto";
  }
  if (status === "yellow") {
    return "Atención";
  }
  return "Saludable";
}


function getNotificationSeverityStyle(severity: "info" | "warning" | "critical"): CSSProperties {
  if (severity === "critical") {
    return { background: "#fef2f2", color: "#991b1b", border: "1px solid #fecaca" };
  }
  if (severity === "warning") {
    return { background: "#fffbeb", color: "#92400e", border: "1px solid #fde68a" };
  }
  return { background: "#eff6ff", color: "#1d4ed8", border: "1px solid #bfdbfe" };
}


function getNotificationSeverityRank(severity: SequenceNotificationSeverity): number {
  if (severity === "critical") {
    return 3;
  }
  if (severity === "warning") {
    return 2;
  }
  return 1;
}


function parseNotificationTypesInput(rawValue: string): string[] {
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


function formatStatus(status: string): string {
  const normalized = status.trim().toLowerCase();
  if (!normalized) {
    return "unknown";
  }
  return normalized;
}


function isActiveStatus(status: string): boolean {
  const normalized = formatStatus(status);
  return normalized === "queued" || normalized === "running";
}


function formatTimestamp(value: string | undefined): string {
  if (!value) {
    return "-";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}


function summarizeSemanticContextText(value: string | null | undefined, maxChars = 220): string {
  const normalized = typeof value === "string" ? value.trim() : "";
  if (!normalized) {
    return "-";
  }

  if (normalized.length <= maxChars) {
    return normalized;
  }

  return `${normalized.slice(0, maxChars - 3).trimEnd()}...`;
}


function extractPromptAddition(promptBase: string | null | undefined, promptEnriched: string | null | undefined): string | null {
  const base = typeof promptBase === "string" ? promptBase.trim() : "";
  const enriched = typeof promptEnriched === "string" ? promptEnriched.trim() : "";

  if (!base || !enriched || base === enriched) {
    return null;
  }

  if (enriched.startsWith(base)) {
    const suffix = enriched.slice(base.length).trim();
    return suffix || null;
  }

  return enriched;
}


function getLinkRetryIndex(link: SequenceShotJobLink): number {
  return typeof link.retry_index === "number" ? link.retry_index : 0;
}


function matchesStatusFilter(status: string, filter: StatusFilter): boolean {
  if (filter === "all") {
    return true;
  }

  return formatStatus(status) === filter;
}


function isObjectRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}


function normalizeStringValue(value: unknown): string | null {
  if (typeof value !== "string") {
    return null;
  }

  const trimmed = value.trim();
  return trimmed === "" ? null : trimmed;
}


function isPreviewUrl(value: string): boolean {
  const normalized = value.toLowerCase();

  if (
    normalized.startsWith("http://") ||
    normalized.startsWith("https://") ||
    normalized.startsWith("data:image/") ||
    normalized.startsWith("blob:") ||
    normalized.startsWith("/")
  ) {
    return true;
  }

  return false;
}


function isVisualReference(value: string): boolean {
  const normalized = value.toLowerCase();
  return (
    normalized.includes(".png") ||
    normalized.includes(".jpg") ||
    normalized.includes(".jpeg") ||
    normalized.includes(".webp") ||
    normalized.includes(".gif") ||
    normalized.includes(".bmp") ||
    normalized.includes(".avif") ||
    normalized.includes("/view?") ||
    normalized.includes("filename=")
  );
}


function collectVisualCandidates(value: unknown, depth = 0, keyHint = ""): string[] {
  if (depth > 6) {
    return [];
  }

  const direct = normalizeStringValue(value);
  if (direct) {
    const keyNormalized = keyHint.toLowerCase();
    const keyLooksVisual =
      keyNormalized.includes("preview") ||
      keyNormalized.includes("image") ||
      keyNormalized.includes("thumbnail") ||
      keyNormalized.includes("output") ||
      keyNormalized.includes("url") ||
      keyNormalized.includes("file") ||
      keyNormalized.includes("path") ||
      keyNormalized.includes("src");

    if (keyLooksVisual || isPreviewUrl(direct) || isVisualReference(direct)) {
      return [direct];
    }

    return [];
  }

  if (Array.isArray(value)) {
    const values: string[] = [];
    for (let index = 0; index < Math.min(value.length, 30); index += 1) {
      values.push(...collectVisualCandidates(value[index], depth + 1, keyHint));
    }
    return values;
  }

  if (isObjectRecord(value)) {
    const values: string[] = [];
    for (const [key, nestedValue] of Object.entries(value)) {
      values.push(...collectVisualCandidates(nestedValue, depth + 1, key));
    }
    return values;
  }

  return [];
}


function extractJobPreview(job: RenderJobData | null): { previewUrl: string | null; visualReference: string | null } {
  if (!job) {
    return { previewUrl: null, visualReference: null };
  }

  const candidates = [
    ...collectVisualCandidates(job.result),
    ...collectVisualCandidates(job.request_payload),
    ...collectVisualCandidates(job.error),
  ];

  const uniqueCandidates = Array.from(new Set(candidates));
  const previewUrl = uniqueCandidates.find((item) => isPreviewUrl(item) && isVisualReference(item)) ?? null;
  if (previewUrl) {
    return { previewUrl, visualReference: previewUrl };
  }

  const fallbackUrl = uniqueCandidates.find((item) => isPreviewUrl(item)) ?? null;
  if (fallbackUrl) {
    return { previewUrl: fallbackUrl, visualReference: fallbackUrl };
  }

  const visualReference = uniqueCandidates.find((item) => isVisualReference(item)) ?? null;
  return { previewUrl: null, visualReference };
}


type JobPreviewProps = {
  job: RenderJobData | null;
  label: string;
  onOpenPreview: (previewUrl: string, label: string) => void;
};


function JobPreview({ job, label, onOpenPreview }: JobPreviewProps) {
  const [imageFailed, setImageFailed] = useState(false);
  const preview = useMemo(() => extractJobPreview(job), [job]);

  useEffect(() => {
    setImageFailed(false);
  }, [preview.previewUrl]);

  if (preview.previewUrl && !imageFailed) {
    return (
      <div className="mt-2 p-2 rounded-md border border-gray-200 bg-gray-50">
        <div className="text-[11px] font-semibold text-gray-600 mb-1">Preview</div>
        <button
          type="button"
          onClick={() => onOpenPreview(preview.previewUrl as string, label)}
          className="block border border-gray-300 rounded-md overflow-hidden bg-white"
        >
          <img
            src={preview.previewUrl}
            alt={`preview-${label}`}
            className="w-28 h-28 object-cover"
            onError={() => setImageFailed(true)}
          />
        </button>
        <button
          type="button"
          onClick={() => onOpenPreview(preview.previewUrl as string, label)}
          className="mt-2 px-2 py-1 text-[11px] font-semibold rounded border border-gray-300 bg-white text-gray-700"
        >
          Abrir preview
        </button>
      </div>
    );
  }

  return (
    <div className="mt-2 p-2 rounded-md border border-gray-200 bg-gray-50 text-xs text-gray-600">
      <div className="font-semibold text-[11px] text-gray-600 mb-1">Preview</div>
      {preview.visualReference ? (
        <div>
          <div className="text-gray-500">Referencia visual detectada:</div>
          <div className="font-mono break-all">{preview.visualReference}</div>
          <div className="mt-1 text-gray-500">sin preview</div>
        </div>
      ) : (
        <span>sin preview</span>
      )}
    </div>
  );
}


function extractRenderContext(job: RenderJobData): Record<string, unknown> | null {
  const metadata = isObjectRecord(job.request_payload.metadata) ? job.request_payload.metadata : null;
  if (!metadata) {
    return null;
  }

  const renderContext = isObjectRecord(metadata.render_context) ? metadata.render_context : null;
  return renderContext;
}


function collectClipPromptTexts(promptGraph: Record<string, unknown>): string[] {
  const entries: Array<{ order: number; text: string }> = [];

  for (const [nodeId, node] of Object.entries(promptGraph)) {
    if (!isObjectRecord(node)) {
      continue;
    }
    if (node.class_type !== "CLIPTextEncode") {
      continue;
    }

    const inputs = isObjectRecord(node.inputs) ? node.inputs : null;
    if (!inputs) {
      continue;
    }

    const text = normalizeStringValue(inputs.text);
    if (!text) {
      continue;
    }

    const order = Number.parseInt(nodeId, 10);
    entries.push({ order: Number.isFinite(order) ? order : 9999, text });
  }

  entries.sort((left, right) => left.order - right.order);
  return entries.map((item) => item.text);
}


function extractPromptSummary(job: RenderJobData): {
  positive: string | null;
  negative: string | null;
} {
  const promptGraph = isObjectRecord(job.request_payload.prompt) ? job.request_payload.prompt : null;
  if (!promptGraph) {
    return { positive: null, negative: null };
  }

  const node6 = isObjectRecord(promptGraph["6"]) ? promptGraph["6"] : null;
  const node7 = isObjectRecord(promptGraph["7"]) ? promptGraph["7"] : null;

  const node6Inputs = node6 && isObjectRecord(node6.inputs) ? node6.inputs : null;
  const node7Inputs = node7 && isObjectRecord(node7.inputs) ? node7.inputs : null;

  let positive = normalizeStringValue(node6Inputs?.text);
  let negative = normalizeStringValue(node7Inputs?.text);

  const collected = collectClipPromptTexts(promptGraph);
  if (!positive && collected.length > 0) {
    positive = collected[0];
  }
  if (!negative && collected.length > 1) {
    negative = collected[1];
  }

  return { positive, negative };
}


function summarizeText(text: string | null, maxLength = 220): string {
  if (!text) {
    return "-";
  }

  if (text.length <= maxLength) {
    return text;
  }

  return `${text.slice(0, maxLength)}...`;
}


function parseTagEditorInput(rawValue: string): string[] {
  const seen = new Set<string>();
  const tags: string[] = [];

  const segments = rawValue
    .split("\n")
    .flatMap((line) => line.split(","))
    .map((item) => item.trim())
    .filter((item) => item !== "");

  for (const item of segments) {
    const lowered = item.toLowerCase();
    if (seen.has(lowered)) {
      continue;
    }
    seen.add(lowered);
    tags.push(item);
  }

  return tags;
}


function isProblematicRecentExecution(item: SequenceExecutionRecentItem): boolean {
  const failed = item.status_summary.by_status.failed ?? 0;
  const timeout = item.status_summary.by_status.timeout ?? 0;
  return failed > 0 || timeout > 0 || item.total_retries > 0;
}


function isStableRecentExecution(item: SequenceExecutionRecentItem): boolean {
  const failed = item.status_summary.by_status.failed ?? 0;
  const timeout = item.status_summary.by_status.timeout ?? 0;
  return item.success_ratio >= 0.8 && failed === 0 && timeout === 0;
}


function extractVisualReferences(job: RenderJobData): string[] {
  const rawCandidates = [
    ...collectVisualCandidates(job.result),
    ...collectVisualCandidates(job.request_payload),
    ...collectVisualCandidates(job.error),
  ];

  return Array.from(new Set(rawCandidates.filter((item) => isVisualReference(item)))).slice(0, 8);
}


function summarizeResult(result: Record<string, unknown> | null | undefined): Array<{ label: string; value: string }> {
  if (!result || !isObjectRecord(result)) {
    return [];
  }

  const summary: Array<{ label: string; value: string }> = [];

  const provider = normalizeStringValue(result.provider);
  if (provider) {
    summary.push({ label: "provider", value: provider });
  }

  const promptId = normalizeStringValue(result.prompt_id);
  if (promptId) {
    summary.push({ label: "prompt_id", value: promptId });
  }

  const completionSource = normalizeStringValue(result.completion_source);
  if (completionSource) {
    summary.push({ label: "completion_source", value: completionSource });
  }

  if (typeof result.submit_status_code === "number") {
    summary.push({ label: "submit_status_code", value: String(result.submit_status_code) });
  }

  if (typeof result.poll_elapsed_ms === "number") {
    summary.push({ label: "poll_elapsed_ms", value: String(result.poll_elapsed_ms) });
  }

  const historySummary = isObjectRecord(result.history_summary) ? result.history_summary : null;
  if (historySummary) {
    if (typeof historySummary.has_outputs === "boolean") {
      summary.push({ label: "has_outputs", value: historySummary.has_outputs ? "true" : "false" });
    }
    if (typeof historySummary.output_node_count === "number") {
      summary.push({ label: "output_node_count", value: String(historySummary.output_node_count) });
    }
    const statusStr = normalizeStringValue(historySummary.status_str);
    if (statusStr) {
      summary.push({ label: "history_status", value: statusStr });
    }
  }

  return summary;
}


function prettyJson(value: unknown): string {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}


function hasComparableValue(value: unknown): boolean {
  if (value === null || value === undefined) {
    return false;
  }

  if (typeof value === "string") {
    return value.trim() !== "";
  }

  return true;
}


function normalizeForComparison(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map((item) => normalizeForComparison(item));
  }

  if (isObjectRecord(value)) {
    const sortedEntries = Object.entries(value).sort(([leftKey], [rightKey]) => leftKey.localeCompare(rightKey));
    const normalizedObject: Record<string, unknown> = {};
    for (const [key, nestedValue] of sortedEntries) {
      normalizedObject[key] = normalizeForComparison(nestedValue);
    }
    return normalizedObject;
  }

  if (typeof value === "string") {
    return value.trim();
  }

  return value;
}


function serializeForComparison(value: unknown): string {
  if (!hasComparableValue(value)) {
    return "";
  }

  if (typeof value === "string") {
    return value.trim();
  }

  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }

  try {
    return JSON.stringify(normalizeForComparison(value));
  } catch {
    return String(value);
  }
}


function detectDiffKind(left: unknown, right: unknown): ComparisonDiffKind {
  const leftPresent = hasComparableValue(left);
  const rightPresent = hasComparableValue(right);

  if (!leftPresent || !rightPresent) {
    return leftPresent === rightPresent ? "same" : "missing";
  }

  return serializeForComparison(left) === serializeForComparison(right) ? "same" : "changed";
}


function getDiffBadgeStyle(diffKind: ComparisonDiffKind): CSSProperties {
  if (diffKind === "same") {
    return { background: "#ecfdf3", color: "#166534", border: "1px solid #86efac" };
  }
  if (diffKind === "changed") {
    return { background: "#fff7ed", color: "#9a3412", border: "1px solid #fdba74" };
  }
  return { background: "#fee2e2", color: "#991b1b", border: "1px solid #fca5a5" };
}


function getDiffBadgeLabel(diffKind: ComparisonDiffKind): string {
  if (diffKind === "same") {
    return "igual";
  }
  if (diffKind === "changed") {
    return "cambiado";
  }
  return "ausente";
}


function buildComparableShotMap(execution: SequencePlanAndRenderExecution): Map<string, ComparableShotData> {
  const map = new Map<string, ComparableShotData>();

  const jobsById = new Map<string, RenderJobData>();
  for (const job of execution.created_jobs) {
    jobsById.set(job.job_id, job);
  }

  const planShotsById = new Map<string, SequenceShotPlan>();
  for (const shot of execution.plan.shots) {
    planShotsById.set(shot.shot_id, shot);
  }

  const linksByShotId = new Map<string, SequenceShotJobLink[]>();
  for (const link of execution.shot_job_links) {
    if (!linksByShotId.has(link.shot_id)) {
      linksByShotId.set(link.shot_id, []);
    }
    const links = linksByShotId.get(link.shot_id);
    if (links) {
      links.push(link);
    }
  }

  const allShotIds = new Set<string>([
    ...Array.from(planShotsById.keys()),
    ...Array.from(linksByShotId.keys()),
  ]);

  for (const shotId of Array.from(allShotIds).sort((left, right) => left.localeCompare(right))) {
    const planShot = planShotsById.get(shotId) ?? null;
    const sortedLinks = (linksByShotId.get(shotId) ?? []).slice().sort((left, right) => {
      const leftRetry = getLinkRetryIndex(left);
      const rightRetry = getLinkRetryIndex(right);
      if (leftRetry !== rightRetry) {
        return leftRetry - rightRetry;
      }
      return left.job_id.localeCompare(right.job_id);
    });

    const attempts: ShotAttemptSnapshot[] = sortedLinks.map((link) => {
      const normalizedJobId = normalizeStringValue(link.job_id);
      const job = normalizedJobId ? jobsById.get(normalizedJobId) ?? null : null;
      const promptSummary = job ? extractPromptSummary(job) : { positive: null, negative: null };

      return {
        retryIndex: getLinkRetryIndex(link),
        jobId: normalizedJobId,
        status: job ? formatStatus(job.status ? String(job.status) : "unknown") : null,
        prompt: promptSummary.positive ?? normalizeStringValue(planShot?.prompt) ?? null,
        negativePrompt: promptSummary.negative ?? normalizeStringValue(planShot?.negative_prompt) ?? null,
        renderContext: job ? extractRenderContext(job) : null,
        updatedAt: job ? normalizeStringValue(job.updated_at) : null,
      };
    });

    const initialAttempt = attempts.find((attempt) => attempt.retryIndex === 0) ?? (attempts[0] ?? null);
    const latestAttempt = attempts.length > 0 ? attempts[attempts.length - 1] : null;

    map.set(shotId, {
      shotId,
      shotType: planShot ? normalizeStringValue(planShot.shot_type) : null,
      planPrompt: planShot ? normalizeStringValue(planShot.prompt) : null,
      planNegativePrompt: planShot ? normalizeStringValue(planShot.negative_prompt) : null,
      attempts,
      retriesCount: attempts.filter((attempt) => attempt.retryIndex > 0).length,
      initialAttempt,
      latestAttempt,
    });
  }

  return map;
}


function selectAttemptForMode(
  shotData: ComparableShotData | null,
  compareMode: CompareShotMode
): ShotAttemptSnapshot | null {
  if (!shotData) {
    return null;
  }

  if (compareMode === "initial") {
    return shotData.initialAttempt;
  }

  return shotData.latestAttempt;
}


function buildShotHistorySummary(shotData: ComparableShotData | null): ShotHistorySummary | null {
  if (!shotData) {
    return null;
  }

  let promptChanges = 0;
  let negativePromptChanges = 0;
  let renderContextChanges = 0;

  for (let index = 1; index < shotData.attempts.length; index += 1) {
    const previous = shotData.attempts[index - 1];
    const current = shotData.attempts[index];

    if (detectDiffKind(previous.prompt, current.prompt) === "changed") {
      promptChanges += 1;
    }
    if (detectDiffKind(previous.negativePrompt, current.negativePrompt) === "changed") {
      negativePromptChanges += 1;
    }
    if (detectDiffKind(previous.renderContext, current.renderContext) === "changed") {
      renderContextChanges += 1;
    }
  }

  return {
    attemptsCount: shotData.attempts.length,
    retriesCount: shotData.retriesCount,
    promptChanges,
    negativePromptChanges,
    renderContextChanges,
  };
}


export default function SequenceExecutionPanel({ defaultProjectId }: SequenceExecutionPanelProps) {
  const [scriptText, setScriptText] = useState("");
  const [projectId, setProjectId] = useState("");
  const [sequenceId, setSequenceId] = useState("");
  const [styleProfile, setStyleProfile] = useState("cinematic still");
  const [continuityMode, setContinuityMode] = useState("strict");
  const [semanticPromptEnrichmentEnabled, setSemanticPromptEnrichmentEnabled] = useState(true);
  const [semanticPromptEnrichmentMaxChars, setSemanticPromptEnrichmentMaxChars] = useState("400");

  const [requestIdInput, setRequestIdInput] = useState("");
  const [execution, setExecution] = useState<SequencePlanAndRenderExecution | null>(null);

  const [submitting, setSubmitting] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [retrySubmitting, setRetrySubmitting] = useState(false);
  const [exportingJson, setExportingJson] = useState(false);
  const [exportingPdf, setExportingPdf] = useState(false);
  const [exportingPromptCompareJson, setExportingPromptCompareJson] = useState(false);
  const [exportingPromptCompareCsv, setExportingPromptCompareCsv] = useState(false);
  const [promptComparisonShotFilter, setPromptComparisonShotFilter] = useState("");
  const [promptComparisonSourceFilter, setPromptComparisonSourceFilter] = useState("all");
  const [promptComparisonEnrichmentFilter, setPromptComparisonEnrichmentFilter] = useState<"all" | "enriched" | "not_enriched">("all");
  const [pollingEnabled, setPollingEnabled] = useState(true);
  const [pollingIntervalMs, setPollingIntervalMs] = useState(4000);
  const [pollingInFlight, setPollingInFlight] = useState(false);

  const [activeRetryShotId, setActiveRetryShotId] = useState<string | null>(null);
  const [retryPrompt, setRetryPrompt] = useState("");
  const [retryNegativePrompt, setRetryNegativePrompt] = useState("");
  const [retryReason, setRetryReason] = useState("");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [previewModal, setPreviewModal] = useState<{ url: string; label: string } | null>(null);
  const [jobDetailModal, setJobDetailModal] = useState<JobDetailSelection | null>(null);
  const [recentExecutions, setRecentExecutions] = useState<SequenceExecutionRecentItem[]>([]);
  const [recentLoading, setRecentLoading] = useState(false);
  const [recentError, setRecentError] = useState("");
  const [recentQuery, setRecentQuery] = useState("");
  const [recentProjectIdFilter, setRecentProjectIdFilter] = useState("");
  const [recentSequenceIdFilter, setRecentSequenceIdFilter] = useState("");
  const [recentStatusFilter, setRecentStatusFilter] = useState<StatusFilter>("all");
  const [recentTagFilter, setRecentTagFilter] = useState("");
  const [recentFavoriteOnly, setRecentFavoriteOnly] = useState(false);
  const [recentRanking, setRecentRanking] = useState<RecentRankingFilter>("updated_at_desc");
  const [recentLimit, setRecentLimit] = useState(20);
  const [collections, setCollections] = useState<SequenceExecutionCollection[]>([]);
  const [selectedCollectionId, setSelectedCollectionId] = useState("");
  const [collectionsLoading, setCollectionsLoading] = useState(false);
  const [collectionsError, setCollectionsError] = useState("");
  const [notifications, setNotifications] = useState<SequenceExecutionNotification[]>([]);
  const [notificationsLoading, setNotificationsLoading] = useState(false);
  const [notificationsError, setNotificationsError] = useState("");
  const [notificationsUnreadOnly, setNotificationsUnreadOnly] = useState(false);
  const [notificationPreferences, setNotificationPreferences] = useState<SequenceExecutionNotificationPreferences | null>(null);
  const [notificationPreferencesLoading, setNotificationPreferencesLoading] = useState(false);
  const [notificationPreferencesSaving, setNotificationPreferencesSaving] = useState(false);
  const [notificationPreferencesError, setNotificationPreferencesError] = useState("");
  const [notificationPreferencesInitialized, setNotificationPreferencesInitialized] = useState(false);
  const [notificationEnabledInput, setNotificationEnabledInput] = useState(true);
  const [notificationMinSeverityInput, setNotificationMinSeverityInput] = useState<SequenceNotificationSeverity>("info");
  const [notificationEnabledTypesInput, setNotificationEnabledTypesInput] = useState("");
  const [notificationUnreadDefaultInput, setNotificationUnreadDefaultInput] = useState(false);
  const [notificationActionId, setNotificationActionId] = useState<string | null>(null);
  const [collectionsDashboard, setCollectionsDashboard] = useState<SequenceExecutionCollectionsDashboardResponse | null>(null);
  const [collectionsDashboardLoading, setCollectionsDashboardLoading] = useState(false);
  const [collectionsDashboardError, setCollectionsDashboardError] = useState("");
  const [createCollectionName, setCreateCollectionName] = useState("");
  const [createCollectionDescription, setCreateCollectionDescription] = useState("");
  const [collectionReview, setCollectionReview] = useState<SequenceExecutionCollectionReviewResponse | null>(null);
  const [collectionReviewLoading, setCollectionReviewLoading] = useState(false);
  const [collectionReviewError, setCollectionReviewError] = useState("");
  const [collectionAudit, setCollectionAudit] = useState<SequenceExecutionCollectionAuditResponse | null>(null);
  const [collectionAuditLoading, setCollectionAuditLoading] = useState(false);
  const [collectionAuditError, setCollectionAuditError] = useState("");
  const [collectionReviewRanking, setCollectionReviewRanking] = useState<RecentRankingFilter>("updated_at_desc");
  const [collectionEditorialNoteDraft, setCollectionEditorialNoteDraft] = useState("");
  const [collectionSaving, setCollectionSaving] = useState(false);

  const promptComparisons = useMemo(() => {
    if (!execution) {
      return [];
    }

    return Array.isArray(execution.prompt_comparisons) && execution.prompt_comparisons.length > 0
      ? execution.prompt_comparisons
      : execution.plan.render_inputs.jobs;
  }, [execution]);

  const promptComparisonSourceOptions = useMemo(() => {
    return Array.from(
      new Set(
        promptComparisons.map((job) =>
          typeof job.source === "string" && job.source.trim() ? job.source.trim() : "live"
        )
      )
    ).sort((left, right) => left.localeCompare(right));
  }, [promptComparisons]);

  const filteredPromptComparisons = useMemo(() => {
    const normalizedShotFilter = promptComparisonShotFilter.trim().toLowerCase();

    return promptComparisons.filter((job) => {
      const shotId = String(job.shot_id ?? "").trim();
      const source = typeof job.source === "string" && job.source.trim() ? job.source.trim() : "live";
      const enrichmentApplied = Boolean(job.semantic_enrichment_applied);

      if (normalizedShotFilter && !shotId.toLowerCase().includes(normalizedShotFilter)) {
        return false;
      }

      if (promptComparisonSourceFilter !== "all" && source !== promptComparisonSourceFilter) {
        return false;
      }

      if (promptComparisonEnrichmentFilter === "enriched" && !enrichmentApplied) {
        return false;
      }

      if (promptComparisonEnrichmentFilter === "not_enriched" && enrichmentApplied) {
        return false;
      }

      return true;
    });
  }, [promptComparisons, promptComparisonEnrichmentFilter, promptComparisonShotFilter, promptComparisonSourceFilter]);

  const promptComparisonMetrics = useMemo(() => {
    const persisted = execution?.prompt_comparison_metrics;
    if (persisted) {
      const total = Number(persisted.total);
      const enriched = Number(persisted.enriched);
      const notEnriched = Number(persisted.not_enriched);
      const retries = Number(persisted.retries);
      const enrichmentRatio = Number(persisted.enrichment_ratio);
      const uniqueShots = Number(persisted.unique_shots);
      const shotsWithRetries = Number(persisted.shots_with_retries);
      const shotsWithEnrichment = Number(persisted.shots_with_enrichment);
      const rawSources = persisted.sources;

      if (
        Number.isFinite(total) &&
        Number.isFinite(enriched) &&
        Number.isFinite(notEnriched) &&
        Number.isFinite(retries)
      ) {
        return {
          total,
          enriched,
          notEnriched,
          retries,
          enrichmentRatio: Number.isFinite(enrichmentRatio) ? enrichmentRatio : 0,
          uniqueShots: Number.isFinite(uniqueShots) ? uniqueShots : 0,
          shotsWithRetries: Number.isFinite(shotsWithRetries) ? shotsWithRetries : 0,
          shotsWithEnrichment: Number.isFinite(shotsWithEnrichment) ? shotsWithEnrichment : 0,
          sources:
            rawSources && typeof rawSources === "object"
              ? Object.fromEntries(
                  Object.entries(rawSources).filter(
                    ([key, value]) => key.trim() !== "" && Number.isFinite(Number(value))
                  ).map(([key, value]) => [key, Number(value)])
                )
              : {},
        };
      }
    }

    let enriched = 0;
    let retries = 0;
    const sources: Record<string, number> = {};

    for (const job of promptComparisons) {
      if (job.semantic_enrichment_applied) {
        enriched += 1;
      }
      if (typeof job.retry_index === "number" && job.retry_index > 0) {
        retries += 1;
      }

      const source = typeof job.source === "string" && job.source.trim() ? job.source.trim() : "live";
      sources[source] = (sources[source] ?? 0) + 1;
    }

    return {
      total: promptComparisons.length,
      enriched,
      notEnriched: Math.max(promptComparisons.length - enriched, 0),
      retries,
      enrichmentRatio: 0,
      uniqueShots: 0,
      shotsWithRetries: 0,
      shotsWithEnrichment: 0,
      sources,
    };
  }, [execution, promptComparisons]);
  const [collectionExecutiveExportingJson, setCollectionExecutiveExportingJson] = useState(false);
  const [collectionExecutiveExportingPdf, setCollectionExecutiveExportingPdf] = useState(false);
  const [collectionItemActionRequestId, setCollectionItemActionRequestId] = useState<string | null>(null);
  const [compareLeftRequestId, setCompareLeftRequestId] = useState("");
  const [compareRightRequestId, setCompareRightRequestId] = useState("");
  const [compareShotMode, setCompareShotMode] = useState<CompareShotMode>("latest");
  const [compareLoading, setCompareLoading] = useState(false);
  const [compareError, setCompareError] = useState("");
  const [compareLeftExecution, setCompareLeftExecution] = useState<SequencePlanAndRenderExecution | null>(null);
  const [compareRightExecution, setCompareRightExecution] = useState<SequencePlanAndRenderExecution | null>(null);
  const [metaTagsInput, setMetaTagsInput] = useState("");
  const [metaNoteInput, setMetaNoteInput] = useState("");
  const [metaSaving, setMetaSaving] = useState(false);
  const [reviewStatusInput, setReviewStatusInput] = useState<SequenceExecutionReviewStatus>("pending_review");
  const [reviewNoteInput, setReviewNoteInput] = useState("");
  const [reviewSaving, setReviewSaving] = useState(false);
  const [reviewHistory, setReviewHistory] = useState<SequenceExecutionReviewHistoryEntry[]>([]);
  const [reviewHistoryLoading, setReviewHistoryLoading] = useState(false);
  const [reviewHistoryError, setReviewHistoryError] = useState("");
  const [recentMetaSavingRequestId, setRecentMetaSavingRequestId] = useState<string | null>(null);

  const [panelError, setPanelError] = useState("");
  const [panelInfo, setPanelInfo] = useState("");

  const recentFilters = useMemo<SequenceExecutionRecentFilters>(() => {
    const normalizedStatus = recentStatusFilter === "all" ? undefined : recentStatusFilter;
    const normalizedRanking = recentRanking === "updated_at_desc" ? undefined : recentRanking;
    return {
      q: recentQuery,
      project_id: recentProjectIdFilter,
      sequence_id: recentSequenceIdFilter,
      status: normalizedStatus,
      is_favorite: recentFavoriteOnly ? true : undefined,
      tag: recentTagFilter,
      ranking: normalizedRanking,
      limit: recentLimit,
    };
  }, [
    recentQuery,
    recentProjectIdFilter,
    recentSequenceIdFilter,
    recentStatusFilter,
    recentFavoriteOnly,
    recentTagFilter,
    recentRanking,
    recentLimit,
  ]);

  const loadRecentExecutions = useCallback(async (silent = false) => {
    if (!silent) {
      setRecentLoading(true);
    }
    setRecentError("");

    try {
      const recent = await listRecentSequenceExecutions(recentFilters);
      setRecentExecutions(recent.executions);
    } catch (error) {
      setRecentError(getBackendErrorMessage(error));
    } finally {
      if (!silent) {
        setRecentLoading(false);
      }
    }
  }, [recentFilters]);

  const loadNotificationPreferences = useCallback(async (silent = false) => {
    if (!silent) {
      setNotificationPreferencesLoading(true);
    }
    setNotificationPreferencesError("");

    try {
      const response = await getSequenceNotificationPreferences();
      const preferences = response.preferences;
      setNotificationPreferences(preferences);
      setNotificationEnabledInput(preferences.notifications_enabled);
      setNotificationMinSeverityInput(preferences.min_severity);
      setNotificationEnabledTypesInput(preferences.enabled_types.join(", "));
      setNotificationUnreadDefaultInput(preferences.show_only_unread_by_default);

      if (!notificationPreferencesInitialized) {
        setNotificationsUnreadOnly(preferences.show_only_unread_by_default);
        setNotificationPreferencesInitialized(true);
      }
    } catch (error) {
      setNotificationPreferencesError(getBackendErrorMessage(error));
      setNotificationPreferences(null);
    } finally {
      if (!silent) {
        setNotificationPreferencesLoading(false);
      }
    }
  }, [notificationPreferencesInitialized]);

  const loadNotifications = useCallback(async (silent = false) => {
    if (!silent) {
      setNotificationsLoading(true);
    }
    setNotificationsError("");

    try {
      const response = await listSequenceNotifications({
        limit: 100,
        is_read: notificationsUnreadOnly ? false : undefined,
      });

      const severityFloor = notificationPreferences
        ? getNotificationSeverityRank(notificationPreferences.min_severity)
        : 1;
      const enabledTypes = new Set(
        notificationPreferences?.enabled_types && notificationPreferences.enabled_types.length > 0
          ? notificationPreferences.enabled_types
          : []
      );

      const filtered = response.notifications.filter((item) => {
        const severityOk = getNotificationSeverityRank(item.severity) >= severityFloor;
        const typeOk = enabledTypes.size > 0 ? enabledTypes.has(item.type) : true;
        return severityOk && typeOk;
      });

      setNotifications(filtered);
    } catch (error) {
      setNotificationsError(getBackendErrorMessage(error));
      setNotifications([]);
    } finally {
      if (!silent) {
        setNotificationsLoading(false);
      }
    }
  }, [notificationsUnreadOnly, notificationPreferences]);

  const loadCollectionsDashboard = useCallback(async (silent = false) => {
    if (!silent) {
      setCollectionsDashboardLoading(true);
    }
    setCollectionsDashboardError("");

    try {
      const dashboard = await getSequenceExecutionCollectionsDashboard({
        limit: 200,
        include_archived: false,
        top_limit: 5,
      });
      setCollectionsDashboard(dashboard);
      void loadNotifications(true);
      void loadNotificationPreferences(true);
    } catch (error) {
      setCollectionsDashboardError(getBackendErrorMessage(error));
      setCollectionsDashboard(null);
    } finally {
      if (!silent) {
        setCollectionsDashboardLoading(false);
      }
    }
  }, [loadNotifications, loadNotificationPreferences]);

  const loadCollections = useCallback(async (silent = false) => {
    if (!silent) {
      setCollectionsLoading(true);
    }
    setCollectionsError("");

    try {
      const response = await listSequenceExecutionCollections(200, false);
      const nextCollections = response.collections;
      setCollections(nextCollections);

      if (nextCollections.length === 0) {
        setSelectedCollectionId("");
        void loadCollectionsDashboard(true);
        return;
      }

      const hasCurrentSelection = nextCollections.some((item) => item.collection_id === selectedCollectionId);
      if (!hasCurrentSelection) {
        setSelectedCollectionId(nextCollections[0].collection_id);
      }

      void loadCollectionsDashboard(true);
    } catch (error) {
      setCollectionsError(getBackendErrorMessage(error));
    } finally {
      if (!silent) {
        setCollectionsLoading(false);
      }
    }
  }, [selectedCollectionId, loadCollectionsDashboard]);

  const loadReviewHistory = useCallback(async (requestId: string, silent = false) => {
    const normalizedRequestId = requestId.trim();
    if (!normalizedRequestId) {
      setReviewHistory([]);
      setReviewHistoryError("");
      return;
    }

    if (!silent) {
      setReviewHistoryLoading(true);
    }
    setReviewHistoryError("");

    try {
      const response = await getSequencePlanAndRenderReviewHistory(normalizedRequestId, 200);
      setReviewHistory(response.history);
    } catch (error) {
      setReviewHistory([]);
      setReviewHistoryError(getBackendErrorMessage(error));
    } finally {
      if (!silent) {
        setReviewHistoryLoading(false);
      }
    }
  }, []);

  const loadCollectionAudit = useCallback(async (collectionId: string, silent = false) => {
    const normalizedCollectionId = collectionId.trim();
    if (!normalizedCollectionId) {
      setCollectionAudit(null);
      setCollectionAuditError("");
      return;
    }

    if (!silent) {
      setCollectionAuditLoading(true);
    }
    setCollectionAuditError("");

    try {
      const audit = await getSequenceExecutionCollectionAudit(normalizedCollectionId);
      setCollectionAudit(audit);
      void loadNotifications(true);
    } catch (error) {
      setCollectionAuditError(getBackendErrorMessage(error));
      setCollectionAudit(null);
    } finally {
      if (!silent) {
        setCollectionAuditLoading(false);
      }
    }
  }, [loadNotifications]);

  const loadCollectionReview = useCallback(async (collectionId: string, silent = false) => {
    const normalizedCollectionId = collectionId.trim();
    if (!normalizedCollectionId) {
      setCollectionReview(null);
      setCollectionReviewError("");
      return;
    }

    if (!silent) {
      setCollectionReviewLoading(true);
    }
    setCollectionReviewError("");

    const rankingParam: SequenceExecutionRecentRanking | undefined =
      collectionReviewRanking === "updated_at_desc" ? undefined : collectionReviewRanking;

    try {
      const review = await getSequenceExecutionCollectionReview(normalizedCollectionId, {
        ranking: rankingParam,
        limit: 200,
      });
      setCollectionReview(review);
      setCollectionEditorialNoteDraft(review.collection.editorial_note || "");
    } catch (error) {
      setCollectionReviewError(getBackendErrorMessage(error));
      setCollectionReview(null);
    } finally {
      if (!silent) {
        setCollectionReviewLoading(false);
      }
    }
  }, [collectionReviewRanking]);

  const hasActiveJobs = useMemo(() => {
    if (!execution) {
      return false;
    }

    return execution.created_jobs.some((job) =>
      isActiveStatus(job.status ? String(job.status) : "")
    );
  }, [execution]);

  const selectedCollection = useMemo(() => {
    if (collectionReview && collectionReview.collection.collection_id === selectedCollectionId) {
      return collectionReview.collection;
    }
    return collections.find((item) => item.collection_id === selectedCollectionId) ?? null;
  }, [collectionReview, collections, selectedCollectionId]);

  useEffect(() => {
    if (!defaultProjectId) {
      return;
    }

    if (projectId.trim() !== "") {
      return;
    }

    setProjectId(defaultProjectId);
  }, [defaultProjectId, projectId]);

  useEffect(() => {
    void loadRecentExecutions(true);
  }, [loadRecentExecutions]);

  useEffect(() => {
    void loadCollections(true);
  }, [loadCollections]);

  useEffect(() => {
    void loadNotificationPreferences(true);
  }, [loadNotificationPreferences]);

  useEffect(() => {
    void loadNotifications(true);
  }, [loadNotifications]);

  useEffect(() => {
    if (!selectedCollectionId) {
      setCollectionReview(null);
      setCollectionAudit(null);
      setCollectionAuditError("");
      return;
    }

    void loadCollectionReview(selectedCollectionId, true);
    void loadCollectionAudit(selectedCollectionId, true);
  }, [selectedCollectionId, loadCollectionReview, loadCollectionAudit]);

  useEffect(() => {
    if (!execution) {
      setMetaTagsInput("");
      setMetaNoteInput("");
      setReviewStatusInput("pending_review");
      setReviewNoteInput("");
      setReviewHistory([]);
      setReviewHistoryError("");
      setReviewHistoryLoading(false);
      return;
    }

    setMetaTagsInput((execution.tags ?? []).join(", "));
    setMetaNoteInput(execution.note ?? "");
    setReviewStatusInput(execution.review_status ?? "pending_review");
    setReviewNoteInput(execution.review_note ?? "");
    void loadReviewHistory(execution.request_id, true);
  }, [execution?.request_id, loadReviewHistory]);

  function clearRecentFilters() {
    const filtersAlreadyDefault =
      recentQuery.trim() === "" &&
      recentProjectIdFilter.trim() === "" &&
      recentSequenceIdFilter.trim() === "" &&
      recentStatusFilter === "all" &&
      recentTagFilter.trim() === "" &&
      !recentFavoriteOnly &&
      recentRanking === "updated_at_desc" &&
      recentLimit === 20;

    setRecentQuery("");
    setRecentProjectIdFilter("");
    setRecentSequenceIdFilter("");
    setRecentStatusFilter("all");
    setRecentTagFilter("");
    setRecentFavoriteOnly(false);
    setRecentRanking("updated_at_desc");
    setRecentLimit(20);

    if (filtersAlreadyDefault) {
      void loadRecentExecutions(false);
    }
  }

  function assignComparisonSide(side: "left" | "right", requestId: string) {
    if (side === "left") {
      setCompareLeftRequestId(requestId);
      return;
    }

    setCompareRightRequestId(requestId);
  }

  function swapComparisonSides() {
    setCompareLeftRequestId(compareRightRequestId);
    setCompareRightRequestId(compareLeftRequestId);

    setCompareLeftExecution(compareRightExecution);
    setCompareRightExecution(compareLeftExecution);
    setCompareError("");
  }

  async function loadComparisonExecutions() {
    const leftRequestId = compareLeftRequestId.trim();
    const rightRequestId = compareRightRequestId.trim();

    if (!leftRequestId || !rightRequestId) {
      setCompareError("Debes completar request_id izquierda y derecha para comparar.");
      return;
    }

    setCompareLoading(true);
    setCompareError("");

    try {
      const [leftExecution, rightExecution] = await Promise.all([
        getSequencePlanAndRender(leftRequestId),
        getSequencePlanAndRender(rightRequestId),
      ]);

      setCompareLeftExecution(leftExecution);
      setCompareRightExecution(rightExecution);
    } catch (error) {
      setCompareError(getBackendErrorMessage(error));
      setCompareLeftExecution(null);
      setCompareRightExecution(null);
    } finally {
      setCompareLoading(false);
    }
  }

  async function applyMetaUpdate(
    requestId: string,
    payload: {
      is_favorite?: boolean;
      tags?: string[];
      note?: string;
    },
    successMessage: string
  ): Promise<SequencePlanAndRenderExecution | null> {
    try {
      const updated = await updateSequencePlanAndRenderMeta(requestId, payload);

      if (execution && execution.request_id === updated.request_id) {
        setExecution(updated);
        setRequestIdInput(updated.request_id);
      }

      setPanelInfo(successMessage);
      setPanelError("");
      void loadRecentExecutions(true);
      if (selectedCollectionId.trim() !== "") {
        void loadCollectionReview(selectedCollectionId, true);
        void loadCollectionAudit(selectedCollectionId, true);
      }
      return updated;
    } catch (error) {
      setPanelError(getBackendErrorMessage(error));
      return null;
    }
  }

  async function toggleCurrentFavorite() {
    if (!execution) {
      return;
    }

    setMetaSaving(true);
    await applyMetaUpdate(
      execution.request_id,
      { is_favorite: !execution.is_favorite },
      `Favorito actualizado: ${execution.request_id}`
    );
    setMetaSaving(false);
  }

  async function saveCurrentExecutionMeta() {
    if (!execution) {
      return;
    }

    setMetaSaving(true);
    await applyMetaUpdate(
      execution.request_id,
      {
        tags: parseTagEditorInput(metaTagsInput),
        note: metaNoteInput,
      },
      `Metadatos guardados: ${execution.request_id}`
    );
    setMetaSaving(false);
  }

  async function applyReviewUpdate(
    requestId: string,
    status: SequenceExecutionReviewStatus,
    note?: string
  ): Promise<SequencePlanAndRenderExecution | null> {
    setReviewSaving(true);
    try {
      const updated = await updateSequencePlanAndRenderReview(requestId, {
        review_status: status,
        review_note: note,
      });

      if (execution && execution.request_id === updated.request_id) {
        setExecution(updated);
        setRequestIdInput(updated.request_id);
        setReviewStatusInput(updated.review_status);
        setReviewNoteInput(updated.review_note);
      }

      setPanelInfo(`Revisión actualizada: ${updated.request_id}`);
      setPanelError("");
      void loadReviewHistory(updated.request_id, true);
      void loadRecentExecutions(true);
      if (selectedCollectionId.trim() !== "") {
        void loadCollectionReview(selectedCollectionId, true);
        void loadCollectionAudit(selectedCollectionId, true);
      }
      void loadCollectionsDashboard(true);
      return updated;
    } catch (error) {
      setPanelError(getBackendErrorMessage(error));
      return null;
    } finally {
      setReviewSaving(false);
    }
  }

  async function saveCurrentExecutionReview() {
    if (!execution) {
      return;
    }

    await applyReviewUpdate(execution.request_id, reviewStatusInput, reviewNoteInput);
  }

  async function toggleRecentFavorite(item: SequenceExecutionRecentItem) {
    setRecentMetaSavingRequestId(item.request_id);
    setRecentError("");

    try {
      const updated = await updateSequencePlanAndRenderMeta(item.request_id, {
        is_favorite: !item.is_favorite,
      });

      if (execution && execution.request_id === updated.request_id) {
        setExecution(updated);
      }

      setPanelInfo(`Favorito actualizado: ${item.request_id}`);
      void loadRecentExecutions(true);
      if (selectedCollectionId.trim() !== "") {
        void loadCollectionReview(selectedCollectionId, true);
        void loadCollectionAudit(selectedCollectionId, true);
      }
    } catch (error) {
      setRecentError(getBackendErrorMessage(error));
    } finally {
      setRecentMetaSavingRequestId(null);
    }
  }

  async function createCollectionFromForm() {
    const name = createCollectionName.trim();
    if (!name) {
      setCollectionsError("Debes indicar nombre de colección.");
      return;
    }

    setCollectionSaving(true);
    setCollectionsError("");

    try {
      const created = await createSequenceExecutionCollection({
        name,
        description: createCollectionDescription,
      });
      setCreateCollectionName("");
      setCreateCollectionDescription("");
      setPanelInfo(`Colección creada: ${created.collection.name}`);
      await loadCollections(true);
      setSelectedCollectionId(created.collection.collection_id);
      await loadCollectionReview(created.collection.collection_id, true);
      await loadCollectionAudit(created.collection.collection_id, true);
    } catch (error) {
      setCollectionsError(getBackendErrorMessage(error));
    } finally {
      setCollectionSaving(false);
    }
  }

  async function addExecutionToSelectedCollection(requestId: string) {
    const collectionId = selectedCollectionId.trim();
    if (!collectionId) {
      setCollectionsError("Selecciona una colección para añadir ejecuciones.");
      return;
    }

    setCollectionItemActionRequestId(requestId);
    setCollectionReviewError("");

    try {
      await addSequenceExecutionCollectionItems(collectionId, [requestId]);
      setPanelInfo(`Ejecución ${requestId} añadida a la colección.`);
      await loadCollections(true);
      await loadCollectionReview(collectionId, true);
      await loadCollectionAudit(collectionId, true);
    } catch (error) {
      setCollectionReviewError(getBackendErrorMessage(error));
    } finally {
      setCollectionItemActionRequestId(null);
    }
  }

  async function removeExecutionFromSelectedCollection(requestId: string) {
    const collectionId = selectedCollectionId.trim();
    if (!collectionId) {
      return;
    }

    setCollectionItemActionRequestId(requestId);
    setCollectionReviewError("");

    try {
      await removeSequenceExecutionCollectionItem(collectionId, requestId);
      setPanelInfo(`Ejecución ${requestId} removida de la colección.`);
      await loadCollections(true);
      await loadCollectionReview(collectionId, true);
      await loadCollectionAudit(collectionId, true);
    } catch (error) {
      setCollectionReviewError(getBackendErrorMessage(error));
    } finally {
      setCollectionItemActionRequestId(null);
    }
  }

  async function toggleCollectionCandidate(item: SequenceExecutionRecentItem) {
    const collectionId = selectedCollectionId.trim();
    if (!collectionId) {
      return;
    }

    setCollectionItemActionRequestId(item.request_id);
    setCollectionReviewError("");

    try {
      await setSequenceExecutionCollectionItemHighlight(
        collectionId,
        item.request_id,
        !Boolean(item.collection_candidate)
      );
      setPanelInfo(`Candidata actualizada: ${item.request_id}`);
      await loadCollections(true);
      await loadCollectionReview(collectionId, true);
      await loadCollectionAudit(collectionId, true);
    } catch (error) {
      setCollectionReviewError(getBackendErrorMessage(error));
    } finally {
      setCollectionItemActionRequestId(null);
    }
  }

  async function setCollectionBestCandidate(requestId: string | null) {
    const collectionId = selectedCollectionId.trim();
    if (!collectionId) {
      return;
    }

    const normalizedRequestId = requestId ? requestId.trim() : "";
    setCollectionItemActionRequestId(normalizedRequestId || "__clear_best__");
    setCollectionReviewError("");

    try {
      await setSequenceExecutionCollectionBest(collectionId, normalizedRequestId || null);
      if (normalizedRequestId) {
        setPanelInfo(`Best candidate actualizado: ${normalizedRequestId}`);
      } else {
        setPanelInfo("Best candidate limpiado en la colección.");
      }
      await loadCollections(true);
      await loadCollectionReview(collectionId, true);
      await loadCollectionAudit(collectionId, true);
    } catch (error) {
      setCollectionReviewError(getBackendErrorMessage(error));
    } finally {
      setCollectionItemActionRequestId(null);
    }
  }

  async function saveCollectionEditorialNote() {
    const collectionId = selectedCollectionId.trim();
    if (!collectionId) {
      return;
    }

    setCollectionSaving(true);
    setCollectionReviewError("");

    try {
      await updateSequenceExecutionCollection(collectionId, {
        editorial_note: collectionEditorialNoteDraft,
      });
      setPanelInfo("Nota editorial de colección guardada.");
      await loadCollections(true);
      await loadCollectionReview(collectionId, true);
      await loadCollectionAudit(collectionId, true);
    } catch (error) {
      setCollectionReviewError(getBackendErrorMessage(error));
    } finally {
      setCollectionSaving(false);
    }
  }

  async function saveNotificationPreferences() {
    setNotificationPreferencesSaving(true);
    setNotificationPreferencesError("");

    const payload: SequenceExecutionNotificationPreferencesUpdateRequest = {
      notifications_enabled: notificationEnabledInput,
      min_severity: notificationMinSeverityInput,
      enabled_types: parseNotificationTypesInput(notificationEnabledTypesInput),
      show_only_unread_by_default: notificationUnreadDefaultInput,
    };

    try {
      const response = await updateSequenceNotificationPreferences(payload);
      const preferences = response.preferences;
      setNotificationPreferences(preferences);
      setNotificationEnabledInput(preferences.notifications_enabled);
      setNotificationMinSeverityInput(preferences.min_severity);
      setNotificationEnabledTypesInput(preferences.enabled_types.join(", "));
      setNotificationUnreadDefaultInput(preferences.show_only_unread_by_default);
      setNotificationsUnreadOnly(preferences.show_only_unread_by_default);
      setNotificationPreferencesInitialized(true);
      setPanelInfo("Preferencias de notificación actualizadas.");
      void loadNotifications(true);
    } catch (error) {
      setNotificationPreferencesError(getBackendErrorMessage(error));
    } finally {
      setNotificationPreferencesSaving(false);
    }
  }

  async function markNotificationAsRead(notificationId: string) {
    const normalizedNotificationId = notificationId.trim();
    if (!normalizedNotificationId) {
      return;
    }

    setNotificationActionId(normalizedNotificationId);
    setNotificationsError("");

    try {
      const response = await markSequenceNotificationRead(normalizedNotificationId, true);
      setNotifications((previous) =>
        previous.map((item) =>
          item.notification_id === response.notification.notification_id
            ? response.notification
            : item
        )
      );
      setPanelInfo("Notificación marcada como leída.");
      void loadNotifications(true);
      void loadCollectionsDashboard(true);
    } catch (error) {
      setNotificationsError(getBackendErrorMessage(error));
    } finally {
      setNotificationActionId(null);
    }
  }

  function handleExportCollectionJson() {
    if (!collectionReview) {
      return;
    }

    const payload = {
      collection: collectionReview.collection,
      summary: collectionReview.summary,
      executions: collectionReview.executions,
      audit: collectionAudit,
      exported_at: new Date().toISOString(),
    };

    downloadFile(
      JSON.stringify(payload, null, 2),
      `sequence_collection_${collectionReview.collection.collection_id}.json`,
      "application/json;charset=utf-8"
    );

    setPanelInfo(`Colección exportada: ${collectionReview.collection.name}`);
  }

  async function resolveExecutiveCollectionData(): Promise<{
    collection: SequenceExecutionCollection;
    review: SequenceExecutionCollectionReviewResponse;
    audit: SequenceExecutionCollectionAuditResponse;
  } | null> {
    const collectionId = selectedCollectionId.trim();
    if (!collectionId) {
      setPanelError("Selecciona una colección para exportar informe ejecutivo.");
      return null;
    }

    try {
      const rankingParam: SequenceExecutionRecentRanking | undefined =
        collectionReviewRanking === "updated_at_desc" ? undefined : collectionReviewRanking;

      let review =
        collectionReview && collectionReview.collection.collection_id === collectionId
          ? collectionReview
          : null;

      if (!review) {
        review = await getSequenceExecutionCollectionReview(collectionId, {
          ranking: rankingParam,
          limit: 200,
        });
        setCollectionReview(review);
      }

      let audit =
        collectionAudit && collectionAudit.collection_id === collectionId
          ? collectionAudit
          : null;

      if (!audit) {
        audit = await getSequenceExecutionCollectionAudit(collectionId);
        setCollectionAudit(audit);
      }

      const collectionPayload: SequenceExecutionCollection = {
        ...review.collection,
        health_status: audit.health_status,
        alerts: audit.alerts,
      };

      return {
        collection: collectionPayload,
        review,
        audit,
      };
    } catch (error) {
      setPanelError(getBackendErrorMessage(error));
      return null;
    }
  }

  async function handleExportCollectionExecutiveJson() {
    setCollectionExecutiveExportingJson(true);
    setPanelError("");

    try {
      const data = await resolveExecutiveCollectionData();
      if (!data) {
        return;
      }

      const payload = {
        report_type: "collection_executive_report",
        exported_at: new Date().toISOString(),
        collection_id: data.collection.collection_id,
        name: data.collection.name,
        description: data.collection.description,
        created_at: data.collection.created_at,
        updated_at: data.collection.updated_at,
        health_status: data.audit.health_status,
        alerts: data.audit.alerts,
        audit_summary: {
          total_executions: data.audit.total_executions,
          total_jobs: data.audit.total_jobs,
          total_retries: data.audit.total_retries,
          failed_count: data.audit.failed_count,
          timeout_count: data.audit.timeout_count,
          success_ratio_summary: data.audit.success_ratio_summary,
          best_request_id: data.audit.best_request_id ?? null,
          executions_without_review: data.audit.executions_without_review,
        },
        editorial_summary: data.audit.editorial_summary,
        operational_summary: data.audit.operational_summary,
        executions: data.review.executions.map((item) => ({
          request_id: item.request_id,
          sequence_summary: item.sequence_summary,
          review_status: item.review_status,
          is_favorite: item.is_favorite,
          tags: item.tags,
          note: item.note,
          status_summary: item.status_summary,
          success_ratio: item.success_ratio,
          job_count: item.job_count,
          total_retries: item.total_retries,
          collection_candidate: item.collection_candidate,
          collection_best: item.collection_best,
        })),
      };

      downloadFile(
        JSON.stringify(payload, null, 2),
        `sequence_collection_executive_${data.collection.collection_id}.json`,
        "application/json;charset=utf-8"
      );

      setPanelInfo(`Informe ejecutivo JSON exportado: ${data.collection.name}`);
    } finally {
      setCollectionExecutiveExportingJson(false);
    }
  }

  async function handleExportCollectionExecutivePdf() {
    setCollectionExecutiveExportingPdf(true);
    setPanelError("");

    try {
      const data = await resolveExecutiveCollectionData();
      if (!data) {
        return;
      }

      const documentPdf = new jsPDF({ unit: "pt", format: "a4" });
      const pageWidth = documentPdf.internal.pageSize.getWidth();
      const pageHeight = documentPdf.internal.pageSize.getHeight();
      const margin = 36;
      const lineHeight = 14;
      const maxTextWidth = pageWidth - margin * 2;

      let cursorY = margin;

      const ensureSpace = (extra = lineHeight) => {
        if (cursorY + extra <= pageHeight - margin) {
          return;
        }
        documentPdf.addPage();
        cursorY = margin;
      };

      const writeLine = (
        text: string,
        options?: { size?: number; bold?: boolean; color?: [number, number, number] }
      ) => {
        ensureSpace(lineHeight * 2);
        documentPdf.setFont("helvetica", options?.bold ? "bold" : "normal");
        documentPdf.setFontSize(options?.size ?? 10);
        if (options?.color) {
          documentPdf.setTextColor(options.color[0], options.color[1], options.color[2]);
        } else {
          documentPdf.setTextColor(33, 37, 41);
        }

        const lines = documentPdf.splitTextToSize(text, maxTextWidth);
        for (const line of lines) {
          ensureSpace(lineHeight);
          documentPdf.text(line, margin, cursorY);
          cursorY += lineHeight;
        }
      };

      const writeSection = (title: string) => {
        cursorY += 8;
        writeLine(title, { size: 12, bold: true, color: [17, 24, 39] });
        cursorY += 2;
      };

      writeLine("CINE AI PLATFORM - Informe Ejecutivo de Colección", { size: 16, bold: true });
      writeLine(data.collection.name, { size: 14, bold: true });
      writeLine(`collection_id: ${data.collection.collection_id}`);
      writeLine(`description: ${data.collection.description || "-"}`);
      writeLine(`created_at: ${formatTimestamp(data.collection.created_at)}`);
      writeLine(`updated_at: ${formatTimestamp(data.collection.updated_at)}`);
      writeLine(`exported_at: ${new Date().toISOString()}`);

      writeSection("Estado Global");
      writeLine(`health_status: ${data.audit.health_status}`);
      writeLine(`alerts_count: ${data.audit.alerts.length}`);
      writeLine(`best_request_id: ${data.audit.best_request_id || "-"}`);

      writeSection("Alertas Activas");
      if (data.audit.alerts.length === 0) {
        writeLine("- sin alertas activas");
      } else {
        data.audit.alerts.forEach((alert) => {
          writeLine(`- ${alert}`);
        });
      }

      writeSection("Resumen Editorial");
      writeLine(`total_executions: ${data.audit.editorial_summary.total_executions}`);
      writeLine(`approved_count: ${data.audit.editorial_summary.approved_count}`);
      writeLine(`rejected_count: ${data.audit.editorial_summary.rejected_count}`);
      writeLine(`pending_review_count: ${data.audit.editorial_summary.pending_review_count}`);
      writeLine(`favorite_count: ${data.audit.editorial_summary.favorite_count}`);
      writeLine(`executions_without_review: ${data.audit.editorial_summary.executions_without_review}`);

      writeSection("Resumen Operativo");
      writeLine(`total_jobs: ${data.audit.operational_summary.total_jobs}`);
      writeLine(`total_retries: ${data.audit.operational_summary.total_retries}`);
      writeLine(`failed_count: ${data.audit.operational_summary.failed_count}`);
      writeLine(`timeout_count: ${data.audit.operational_summary.timeout_count}`);
      writeLine(
        `success_ratio: ${(data.audit.operational_summary.success_ratio_summary.ratio * 100).toFixed(1)}%`
      );

      writeSection("Best Execution");
      if (!data.audit.best_request_id) {
        writeLine("- no definida");
      } else {
        const best = data.review.executions.find((item) => item.request_id === data.audit.best_request_id) || null;
        writeLine(`request_id: ${data.audit.best_request_id}`);
        if (best) {
          writeLine(`summary: ${summarizeText(best.sequence_summary, 180)}`);
          writeLine(`review_status: ${best.review_status}`);
          writeLine(`success_ratio: ${(best.success_ratio * 100).toFixed(1)}%`);
        }
      }

      writeSection("Ejecuciones");
      if (data.review.executions.length === 0) {
        writeLine("- sin ejecuciones en la colección");
      } else {
        data.review.executions.forEach((item, index) => {
          writeLine(`${index + 1}. ${item.request_id}`, { bold: true });
          writeLine(`summary: ${summarizeText(item.sequence_summary, 170)}`);
          writeLine(
            `review_status: ${item.review_status} | favorite: ${item.is_favorite ? "yes" : "no"} | success_ratio: ${(item.success_ratio * 100).toFixed(1)}%`
          );
          writeLine(`tags: ${item.tags.length > 0 ? item.tags.join(", ") : "-"}`);
          writeLine(`note: ${item.note || "-"}`);
          writeLine(`status_summary: ${JSON.stringify(item.status_summary.by_status || {})}`);
          cursorY += 2;
        });
      }

      documentPdf.save(`sequence_collection_executive_${data.collection.collection_id}.pdf`);
      setPanelInfo(`Informe ejecutivo PDF exportado: ${data.collection.name}`);
    } finally {
      setCollectionExecutiveExportingPdf(false);
    }
  }

  const comparisonGlobalFields = useMemo(() => {
    if (!compareLeftExecution || !compareRightExecution) {
      return [] as Array<{
        key: string;
        label: string;
        leftValue: unknown;
        rightValue: unknown;
        diffKind: ComparisonDiffKind;
      }>;
    }

    const leftProjectId = normalizeStringValue(compareLeftExecution.request_payload.project_id);
    const rightProjectId = normalizeStringValue(compareRightExecution.request_payload.project_id);
    const leftSequenceId = normalizeStringValue(compareLeftExecution.request_payload.sequence_id);
    const rightSequenceId = normalizeStringValue(compareRightExecution.request_payload.sequence_id);

    const fields = [
      {
        key: "request_id",
        label: "request_id",
        leftValue: compareLeftExecution.request_id,
        rightValue: compareRightExecution.request_id,
      },
      {
        key: "project_id",
        label: "project_id",
        leftValue: leftProjectId,
        rightValue: rightProjectId,
      },
      {
        key: "sequence_id",
        label: "sequence_id",
        leftValue: leftSequenceId,
        rightValue: rightSequenceId,
      },
      {
        key: "sequence_summary",
        label: "sequence_summary",
        leftValue: normalizeStringValue(compareLeftExecution.plan.sequence_summary),
        rightValue: normalizeStringValue(compareRightExecution.plan.sequence_summary),
      },
      {
        key: "job_count",
        label: "job_count",
        leftValue: compareLeftExecution.job_count,
        rightValue: compareRightExecution.job_count,
      },
      {
        key: "shots_count",
        label: "shots_count",
        leftValue: compareLeftExecution.plan.shots.length,
        rightValue: compareRightExecution.plan.shots.length,
      },
      {
        key: "status_summary",
        label: "status_summary",
        leftValue: compareLeftExecution.status_summary,
        rightValue: compareRightExecution.status_summary,
      },
      {
        key: "is_favorite",
        label: "is_favorite",
        leftValue: compareLeftExecution.is_favorite,
        rightValue: compareRightExecution.is_favorite,
      },
      {
        key: "tags",
        label: "tags",
        leftValue: compareLeftExecution.tags,
        rightValue: compareRightExecution.tags,
      },
      {
        key: "note",
        label: "note",
        leftValue: compareLeftExecution.note,
        rightValue: compareRightExecution.note,
      },
      {
        key: "review_status",
        label: "review_status",
        leftValue: compareLeftExecution.review_status,
        rightValue: compareRightExecution.review_status,
      },
      {
        key: "review_note",
        label: "review_note",
        leftValue: compareLeftExecution.review_note,
        rightValue: compareRightExecution.review_note,
      },
      {
        key: "reviewed_at",
        label: "reviewed_at",
        leftValue: compareLeftExecution.reviewed_at,
        rightValue: compareRightExecution.reviewed_at,
      },
    ];

    return fields.map((field) => ({
      ...field,
      diffKind: detectDiffKind(field.leftValue, field.rightValue),
    }));
  }, [compareLeftExecution, compareRightExecution]);

  const shotComparisons = useMemo(() => {
    if (!compareLeftExecution || !compareRightExecution) {
      return [] as ShotComparisonItem[];
    }

    const leftShotMap = buildComparableShotMap(compareLeftExecution);
    const rightShotMap = buildComparableShotMap(compareRightExecution);

    const shotIds = Array.from(new Set<string>([
      ...Array.from(leftShotMap.keys()),
      ...Array.from(rightShotMap.keys()),
    ])).sort((left, right) => left.localeCompare(right));

    return shotIds.map((shotId) => {
      const leftShotData = leftShotMap.get(shotId) ?? null;
      const rightShotData = rightShotMap.get(shotId) ?? null;

      const leftSelectedAttempt = selectAttemptForMode(leftShotData, compareShotMode);
      const rightSelectedAttempt = selectAttemptForMode(rightShotData, compareShotMode);

      const leftPrompt = leftSelectedAttempt?.prompt ?? leftShotData?.planPrompt ?? null;
      const rightPrompt = rightSelectedAttempt?.prompt ?? rightShotData?.planPrompt ?? null;

      const leftNegativePrompt = leftSelectedAttempt?.negativePrompt ?? leftShotData?.planNegativePrompt ?? null;
      const rightNegativePrompt = rightSelectedAttempt?.negativePrompt ?? rightShotData?.planNegativePrompt ?? null;

      const leftRenderContext = leftSelectedAttempt?.renderContext ?? null;
      const rightRenderContext = rightSelectedAttempt?.renderContext ?? null;

      const leftStatus = leftSelectedAttempt?.status ?? null;
      const rightStatus = rightSelectedAttempt?.status ?? null;

      const retriesLeft = leftShotData?.retriesCount ?? 0;
      const retriesRight = rightShotData?.retriesCount ?? 0;

      return {
        shotId,
        leftExists: leftShotData !== null,
        rightExists: rightShotData !== null,
        shotTypeLeft: leftShotData?.shotType ?? null,
        shotTypeRight: rightShotData?.shotType ?? null,
        promptLeft: leftPrompt,
        promptRight: rightPrompt,
        negativePromptLeft: leftNegativePrompt,
        negativePromptRight: rightNegativePrompt,
        renderContextLeft: leftRenderContext,
        renderContextRight: rightRenderContext,
        statusLeft: leftStatus,
        statusRight: rightStatus,
        retriesLeft,
        retriesRight,
        diffShotType: detectDiffKind(leftShotData?.shotType, rightShotData?.shotType),
        diffPrompt: detectDiffKind(leftPrompt, rightPrompt),
        diffNegativePrompt: detectDiffKind(leftNegativePrompt, rightNegativePrompt),
        diffRenderContext: detectDiffKind(leftRenderContext, rightRenderContext),
        diffStatus: detectDiffKind(leftStatus, rightStatus),
        diffRetries: detectDiffKind(retriesLeft, retriesRight),
        leftHistory: buildShotHistorySummary(leftShotData),
        rightHistory: buildShotHistorySummary(rightShotData),
        leftAttempts: leftShotData?.attempts ?? [],
        rightAttempts: rightShotData?.attempts ?? [],
      };
    });
  }, [compareLeftExecution, compareRightExecution, compareShotMode]);

  const shotRows = useMemo<ShotExecutionRow[]>(() => {
    if (!execution) {
      return [];
    }

    return buildShotExecutionRows(execution);
  }, [execution]);

  const filteredShotRows = useMemo(() => {
    if (statusFilter === "all") {
      return shotRows;
    }

    return shotRows.filter((row) => {
      const latestStatus = formatStatus(row.latestJob?.status ? String(row.latestJob.status) : "unknown");
      if (latestStatus === statusFilter) {
        return true;
      }

      return row.retries.some(({ job }) => {
        const retryStatus = formatStatus(job?.status ? String(job.status) : "unknown");
        return retryStatus === statusFilter;
      });
    });
  }, [shotRows, statusFilter]);

  const executionMetrics = useMemo<ExecutionMetrics | null>(() => {
    if (!execution) {
      return null;
    }

    return buildExecutionMetrics(execution, shotRows);
  }, [execution, shotRows]);

  const jobDetailData = useMemo(() => {
    if (!jobDetailModal) {
      return null;
    }

    const { job, link } = jobDetailModal;
    const status = formatStatus(job.status ? String(job.status) : "unknown");
    const promptSummary = extractPromptSummary(job);
    const renderContext = extractRenderContext(job);
    const visualReferences = extractVisualReferences(job);
    const resultSummary = summarizeResult(job.result);

    return {
      status,
      retryIndex: link ? getLinkRetryIndex(link) : null,
      promptSummary,
      renderContext,
      visualReferences,
      resultSummary,
    };
  }, [jobDetailModal]);

  async function runPlanAndRender(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (scriptText.trim() === "") {
      setPanelError("script_text es obligatorio");
      setPanelInfo("");
      return;
    }

    setSubmitting(true);
    setPanelError("");
    setPanelInfo("");

    try {
      const created = await createSequencePlanAndRender({
        script_text: scriptText,
        project_id: projectId,
        sequence_id: sequenceId,
        style_profile: styleProfile,
        continuity_mode: continuityMode,
        semantic_prompt_enrichment_enabled: semanticPromptEnrichmentEnabled,
        semantic_prompt_enrichment_max_chars:
          semanticPromptEnrichmentMaxChars.trim() === ""
            ? undefined
            : Number(semanticPromptEnrichmentMaxChars),
      });

      setExecution(created);
      setRequestIdInput(created.request_id);
      setPanelInfo(`Ejecucion creada: ${created.request_id}`);
      void loadRecentExecutions(true);
    } catch (error) {
      setPanelError(getBackendErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  }

  const loadExecution = useCallback(
    async (
      requestIdValue: string,
      options?: {
        silent?: boolean;
        fromPolling?: boolean;
      }
    ) => {
      const normalizedRequestId = requestIdValue.trim();
      if (!normalizedRequestId) {
        setPanelError("request_id es obligatorio para consultar");
        setPanelInfo("");
        return;
      }

      const silent = options?.silent ?? false;
      const fromPolling = options?.fromPolling ?? false;

      if (!silent) {
        setRefreshing(true);
      }
      if (fromPolling) {
        setPollingInFlight(true);
      }
      if (!fromPolling) {
        setPanelError("");
      }

      try {
        const loaded = await getSequencePlanAndRender(normalizedRequestId);
        setExecution(loaded);
        void loadReviewHistory(loaded.request_id, true);
        setRequestIdInput(loaded.request_id);
        if (!silent) {
        setPanelInfo(`Ejecucion cargada: ${loaded.request_id}`);
      }

      if (!fromPolling) {
        void loadRecentExecutions(true);
      }
    } catch (error) {
      const message = getBackendErrorMessage(error);
        if (fromPolling) {
          setPanelError(`Auto refresh: ${message}`);
        } else {
          setPanelError(message);
        }

        if (!silent) {
          setPanelInfo("");
        }
      } finally {
        if (!silent) {
          setRefreshing(false);
        }
        if (fromPolling) {
          setPollingInFlight(false);
        }
      }
    },
    [loadRecentExecutions, loadReviewHistory]
  );

  useEffect(() => {
    if (!execution) {
      return;
    }
    if (submitting || refreshing || retrySubmitting || pollingInFlight) {
      return;
    }
    if (!pollingEnabled) {
      return;
    }
    if (!hasActiveJobs) {
      return;
    }

    const intervalMs = Math.max(1000, pollingIntervalMs);
    const timer = window.setTimeout(() => {
      void loadExecution(execution.request_id, {
        silent: true,
        fromPolling: true,
      });
    }, intervalMs);

    return () => {
      window.clearTimeout(timer);
    };
  }, [
    execution,
    hasActiveJobs,
    pollingEnabled,
    pollingIntervalMs,
    loadExecution,
    submitting,
    refreshing,
    retrySubmitting,
    pollingInFlight,
  ]);

  function openRetryEditor(shot: SequenceShotPlan) {
    setActiveRetryShotId(shot.shot_id);
    setRetryPrompt(shot.prompt);
    setRetryNegativePrompt(shot.negative_prompt || "");
    setRetryReason("");
    setPanelError("");
    setPanelInfo("");
  }

  function closeRetryEditor() {
    setActiveRetryShotId(null);
    setRetryPrompt("");
    setRetryNegativePrompt("");
    setRetryReason("");
  }

  function openJobDetail(
    shotId: string,
    link: SequenceShotJobLink | null,
    job: RenderJobData | null,
    source: "latest" | "retry"
  ) {
    if (!job) {
      return;
    }

    setJobDetailModal({
      shotId,
      link,
      job,
      source,
    });
  }

  async function copyJobId(jobId: string) {
    if (!jobId.trim()) {
      return;
    }

    try {
      if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
        await navigator.clipboard.writeText(jobId);
        setPanelInfo(`job_id copiado: ${jobId}`);
        return;
      }
    } catch {
      // fallback handled below
    }

    window.prompt("Copia manualmente el job_id:", jobId);
  }

  async function submitRetry(shotId: string) {
    if (!execution) {
      setPanelError("No hay ejecucion cargada para retry");
      return;
    }

    setRetrySubmitting(true);
    setPanelError("");
    setPanelInfo("");

    try {
      const retryPayload: RetryShotRequest = {
        shot_id: shotId,
      };

      if (retryPrompt.trim() !== "") {
        retryPayload.override_prompt = retryPrompt;
      }
      if (retryNegativePrompt.trim() !== "") {
        retryPayload.override_negative_prompt = retryNegativePrompt;
      }
      if (retryReason.trim() !== "") {
        retryPayload.reason = retryReason;
      }

      const retryResult = await retrySequenceShot(execution.request_id, retryPayload);
      setPanelInfo(
        `Retry creado para ${retryResult.shot_id}: ${retryResult.new_job_id} (retry_index=${retryResult.retry_index})`
      );

      closeRetryEditor();
      await loadExecution(execution.request_id, { silent: true });
      void loadRecentExecutions(true);
    } catch (error) {
      setPanelError(getBackendErrorMessage(error));
    } finally {
      setRetrySubmitting(false);
    }
  }

  async function fetchLatestExecutionForExport(): Promise<SequencePlanAndRenderExecution | null> {
    const requestId = (execution?.request_id || requestIdInput).trim();
    if (!requestId) {
      setPanelError("request_id es obligatorio para exportar");
      return null;
    }

    try {
      const latest = await getSequencePlanAndRender(requestId);
      setExecution(latest);
      void loadReviewHistory(latest.request_id, true);
      setRequestIdInput(latest.request_id);
      return latest;
    } catch (error) {
      setPanelError(getBackendErrorMessage(error));
      return null;
    }
  }

  function downloadFile(content: BlobPart, fileName: string, mimeType: string) {
    const blob = new Blob([content], { type: mimeType });
    const objectUrl = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = objectUrl;
    anchor.download = fileName;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(objectUrl);
  }

  function buildPromptComparisonExportRows(latest: SequencePlanAndRenderExecution) {
    const enrichmentEnabled = latest.plan.semantic_prompt_enrichment?.enabled ?? false;
    const enrichmentMaxChars = latest.plan.semantic_prompt_enrichment?.max_chars ?? 0;

    const comparisonSource = Array.isArray(latest.prompt_comparisons) && latest.prompt_comparisons.length > 0
      ? latest.prompt_comparisons
      : latest.plan.render_inputs.jobs;

    return comparisonSource.map((job) => ({
      shot_id: job.shot_id,
      prompt_base: job.prompt_base,
      prompt_enriched: job.prompt_enriched,
      semantic_summary_used: job.semantic_summary_used ?? null,
      semantic_enrichment_applied: job.semantic_enrichment_applied,
      job_id: typeof job.job_id === "string" ? job.job_id : null,
      retry_index: typeof job.retry_index === "number" ? job.retry_index : 0,
      source: typeof job.source === "string" ? job.source : "live",
      semantic_prompt_enrichment_enabled: enrichmentEnabled,
      semantic_prompt_enrichment_max_chars: enrichmentMaxChars,
    }));
  }

  function escapeCsvCell(value: unknown): string {
    const normalized = value == null ? "" : String(value);
    const escaped = normalized.replaceAll('"', '""');
    return `"${escaped}"`;
  }

  async function handleExportJson() {
    setExportingJson(true);
    setPanelError("");

    try {
      const latest = await fetchLatestExecutionForExport();
      if (!latest) {
        return;
      }

      const exportPayload = {
        request_id: latest.request_id,
        request_payload: latest.request_payload,
        plan: latest.plan,
        created_jobs: latest.created_jobs,
        job_ids: latest.job_ids,
        shot_job_links: latest.shot_job_links,
        job_count: latest.job_count,
        status_summary: latest.status_summary,
        is_favorite: latest.is_favorite,
        tags: latest.tags,
        note: latest.note,
        review_status: latest.review_status,
        review_note: latest.review_note,
        reviewed_at: latest.reviewed_at,
        review_history_summary: latest.review_history_summary,
        review_history: reviewHistory,
      };

      downloadFile(
        JSON.stringify(exportPayload, null, 2),
        `sequence_execution_${latest.request_id}.json`,
        "application/json;charset=utf-8"
      );

      setPanelInfo(`Exportación JSON generada: ${latest.request_id}`);
    } finally {
      setExportingJson(false);
    }
  }

  async function handleExportPdf() {
    setExportingPdf(true);
    setPanelError("");

    try {
      const latest = await fetchLatestExecutionForExport();
      if (!latest) {
        return;
      }

      const rows = buildShotExecutionRows(latest);
      const documentPdf = new jsPDF({ unit: "pt", format: "a4" });
      const pageWidth = documentPdf.internal.pageSize.getWidth();
      const pageHeight = documentPdf.internal.pageSize.getHeight();
      const margin = 36;
      const lineHeight = 14;
      const maxTextWidth = pageWidth - margin * 2;

      let cursorY = margin;

      const ensureSpace = (extra = lineHeight) => {
        if (cursorY + extra <= pageHeight - margin) {
          return;
        }
        documentPdf.addPage();
        cursorY = margin;
      };

      const writeLine = (text: string, options?: { size?: number; bold?: boolean; color?: [number, number, number] }) => {
        ensureSpace(lineHeight * 2);
        documentPdf.setFont("helvetica", options?.bold ? "bold" : "normal");
        documentPdf.setFontSize(options?.size ?? 10);
        if (options?.color) {
          documentPdf.setTextColor(options.color[0], options.color[1], options.color[2]);
        } else {
          documentPdf.setTextColor(33, 37, 41);
        }

        const lines = documentPdf.splitTextToSize(text, maxTextWidth);
        for (const line of lines) {
          ensureSpace(lineHeight);
          documentPdf.text(line, margin, cursorY);
          cursorY += lineHeight;
        }
      };

      const writeSection = (title: string) => {
        cursorY += 6;
        writeLine(title, { size: 12, bold: true, color: [17, 24, 39] });
        cursorY += 2;
      };

      writeLine("CINE AI PLATFORM - Sequence Execution Export", { size: 14, bold: true });
      writeLine(`request_id: ${latest.request_id}`, { size: 10 });
      writeLine(`exported_at: ${new Date().toISOString()}`, { size: 10 });

      writeSection("Sequence Summary");
      writeLine(latest.plan.sequence_summary || "-");
      writeLine(`job_count: ${latest.job_count}`);
      writeLine(`status_summary: ${JSON.stringify(latest.status_summary)}`);
      writeLine(`is_favorite: ${latest.is_favorite ? "true" : "false"}`);
      writeLine(`tags: ${latest.tags.length > 0 ? latest.tags.join(", ") : "-"}`);
      writeLine(`note: ${latest.note || "-"}`);
      writeLine(`review_status: ${latest.review_status}`);
      writeLine(`review_note: ${latest.review_note || "-"}`);
      writeLine(`reviewed_at: ${latest.reviewed_at || "-"}`);
      writeLine(`review_history_count: ${latest.review_history_summary?.history_count ?? 0}`);
      writeLine(`review_history_latest: ${latest.review_history_summary?.latest_created_at || "-"}`);

      writeSection("Beats");
      if (latest.plan.beats.length === 0) {
        writeLine("- sin beats");
      } else {
        latest.plan.beats.forEach((beat, index) => {
          const beatId = normalizeStringValue(beat.beat_id) ?? `beat_${index + 1}`;
          const summary = normalizeStringValue(beat.summary) ?? normalizeStringValue(beat.text) ?? "-";
          writeLine(`- ${beatId}: ${summary}`);
        });
      }

      writeSection("Shots and Jobs");
      if (rows.length === 0) {
        writeLine("- sin shots");
      } else {
        rows.forEach((row) => {
          const latestStatus = formatStatus(row.latestJob?.status ? String(row.latestJob.status) : "unknown");
          writeLine(`${row.shot.shot_id} | ${row.shot.shot_type} | latest_status=${latestStatus}`, { bold: true });
          writeLine(`prompt: ${summarizeText(row.shot.prompt, 160)}`);

          if (row.latestJob) {
            const latestPreview = extractJobPreview(row.latestJob);
            const latestErrorCode = row.latestJob.error?.code ?? "-";
            const latestErrorMessage = row.latestJob.error?.message ?? "-";
            writeLine(`latest_job_id: ${row.latestJob.job_id}`);
            writeLine(`latest_updated_at: ${formatTimestamp(row.latestJob.updated_at)}`);
            writeLine(`latest_error.code: ${latestErrorCode}`);
            writeLine(`latest_error.message: ${latestErrorMessage}`);
            writeLine(
              `latest_preview: ${latestPreview.previewUrl ?? latestPreview.visualReference ?? "sin preview"}`
            );
          } else {
            writeLine("latest_job: -");
            writeLine("latest_preview: sin preview");
          }

          if (row.retries.length === 0) {
            writeLine("retries: 0");
          } else {
            writeLine(`retries: ${row.retries.length}`);
            row.retries.forEach(({ link, job }) => {
              const retryStatus = formatStatus(job?.status ? String(job.status) : "unknown");
              const retryJobId = normalizeStringValue(link.job_id) ?? "-";
              const retryPreview = extractJobPreview(job);
              const retryErrorCode = job?.error?.code ?? "-";
              const retryErrorMessage = job?.error?.message ?? "-";
              writeLine(
                `  - retry_index=${getLinkRetryIndex(link)} job_id=${retryJobId} status=${retryStatus}`
              );
              writeLine(`    error.code=${retryErrorCode} error.message=${retryErrorMessage}`);
              writeLine(
                `    preview=${retryPreview.previewUrl ?? retryPreview.visualReference ?? "sin preview"}`
              );
            });
          }

          cursorY += 2;
        });
      }

      documentPdf.save(`sequence_execution_${latest.request_id}.pdf`);
      setPanelInfo(`Exportación PDF generada: ${latest.request_id}`);
    } finally {
      setExportingPdf(false);
    }
  }

  async function handleExportPromptComparisonJson() {
    setExportingPromptCompareJson(true);
    setPanelError("");

    try {
      const latest = await fetchLatestExecutionForExport();
      if (!latest) {
        return;
      }

      const exportPayload = {
        request_id: latest.request_id,
        semantic_prompt_enrichment: latest.plan.semantic_prompt_enrichment ?? {
          enabled: false,
          max_chars: 0,
        },
        jobs: buildPromptComparisonExportRows(latest),
      };

      downloadFile(
        JSON.stringify(exportPayload, null, 2),
        `sequence_prompt_comparison_${latest.request_id}.json`,
        "application/json;charset=utf-8"
      );

      setPanelInfo(`Comparativa de prompts JSON generada: ${latest.request_id}`);
    } finally {
      setExportingPromptCompareJson(false);
    }
  }

  async function handleExportPromptComparisonCsv() {
    setExportingPromptCompareCsv(true);
    setPanelError("");

    try {
      const latest = await fetchLatestExecutionForExport();
      if (!latest) {
        return;
      }

      const rows = buildPromptComparisonExportRows(latest);
      const headers = [
        "shot_id",
        "job_id",
        "retry_index",
        "prompt_base",
        "prompt_enriched",
        "semantic_summary_used",
        "semantic_enrichment_applied",
        "source",
        "semantic_prompt_enrichment_enabled",
        "semantic_prompt_enrichment_max_chars",
      ];
      const csvLines = [headers.join(",")];

      for (const row of rows) {
        csvLines.push([
          escapeCsvCell(row.shot_id),
          escapeCsvCell(row.job_id),
          escapeCsvCell(row.retry_index),
          escapeCsvCell(row.prompt_base),
          escapeCsvCell(row.prompt_enriched),
          escapeCsvCell(row.semantic_summary_used),
          escapeCsvCell(row.semantic_enrichment_applied),
          escapeCsvCell(row.source),
          escapeCsvCell(row.semantic_prompt_enrichment_enabled),
          escapeCsvCell(row.semantic_prompt_enrichment_max_chars),
        ].join(","));
      }

      downloadFile(
        csvLines.join("\n"),
        `sequence_prompt_comparison_${latest.request_id}.csv`,
        "text/csv;charset=utf-8"
      );

      setPanelInfo(`Comparativa de prompts CSV generada: ${latest.request_id}`);
    } finally {
      setExportingPromptCompareCsv(false);
    }
  }

  return (
    <section className="text-left">
      <div className="overflow-hidden rounded-[30px] border border-black/8 bg-[linear-gradient(145deg,_#171411_0%,_#2a221d_48%,_#8b5732_100%)] p-6 text-white shadow-[0_24px_70px_rgba(25,22,18,0.10)]">
        <div className="grid gap-6 xl:grid-cols-[minmax(0,1.15fr)_360px] xl:items-stretch">
          <div>
            <div className="mito-eyebrow border-white/15 bg-white/8 text-white/80">Sequence Plan and Render</div>
            <h3 className="mt-4 text-3xl font-semibold tracking-[-0.05em] text-white md:text-4xl">Orquesta plan, render y revision desde un solo canvas</h3>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-white/72 md:text-base">
              Ejecuta plan-and-render por request_id, monitoriza estados y reintenta shots individuales sin perder continuidad editorial.
            </p>

            <div className="mt-6 grid gap-3 sm:grid-cols-3">
              <div className="rounded-2xl border border-white/10 bg-white/8 p-4 backdrop-blur-sm">
                <div className="text-[11px] uppercase tracking-[0.18em] text-white/55">Polling</div>
                <div className="mt-2 text-lg font-semibold text-white">{pollingEnabled ? "Activo" : "Pausado"}</div>
                <div className="mt-1 text-xs text-white/60">{pollingEnabled ? `${Math.round(pollingIntervalMs / 1000)}s` : "manual"}</div>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/8 p-4 backdrop-blur-sm">
                <div className="text-[11px] uppercase tracking-[0.18em] text-white/55">Colecciones</div>
                <div className="mt-2 text-lg font-semibold text-white">{collectionsDashboard?.total_collections ?? collections.length}</div>
                <div className="mt-1 text-xs text-white/60">vision global</div>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/8 p-4 backdrop-blur-sm">
                <div className="text-[11px] uppercase tracking-[0.18em] text-white/55">Notificaciones</div>
                <div className="mt-2 text-lg font-semibold text-white">{notifications.length}</div>
                <div className="mt-1 text-xs text-white/60">bandeja activa</div>
              </div>
            </div>
          </div>

          <div className="relative overflow-hidden rounded-[28px] border border-white/10 bg-[linear-gradient(180deg,_rgba(255,255,255,0.14),_rgba(255,255,255,0.05))] p-5 backdrop-blur-sm">
            <div className="absolute -right-8 -top-8 h-28 w-28 rounded-full bg-white/10 blur-2xl" />
            <div className="relative flex h-full flex-col justify-between gap-4">
              <div>
                <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-white/55">Creative Prompt Surface</div>
                <div className="mt-3 rounded-2xl border border-white/10 bg-black/10 p-4">
                  <div className="text-xs text-white/55">Style Profile</div>
                  <div className="mt-1 text-sm font-semibold text-white">{styleProfile || "cinematic still"}</div>
                  <div className="mt-4 h-28 rounded-2xl bg-[linear-gradient(135deg,_rgba(255,225,188,0.55),_rgba(255,255,255,0.08)),radial-gradient(circle_at_top_right,_rgba(255,255,255,0.18),_transparent_34%)]" />
                </div>
              </div>

              <div className="rounded-2xl border border-white/10 bg-black/15 p-4">
                <div className="text-[11px] uppercase tracking-[0.18em] text-white/55">Quick Actions</div>
                <div className="mt-3 flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => execution && loadExecution(execution.request_id)}
                    disabled={!execution || refreshing}
                    className="rounded-full border border-white/15 bg-white/10 px-4 py-2 text-xs font-semibold text-white transition hover:bg-white/16 disabled:opacity-45"
                  >
                    Refrescar estado
                  </button>
                  <button
                    type="button"
                    onClick={() => void loadCollectionsDashboard(false)}
                    disabled={collectionsDashboardLoading}
                    className="rounded-full border border-white/15 bg-white px-4 py-2 text-xs font-semibold text-[#38261b] transition hover:bg-[#f7ede2] disabled:opacity-45"
                  >
                    Actualizar dashboard
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 grid gap-4 xl:grid-cols-[minmax(0,1.35fr)_minmax(320px,0.85fr)]">
        <form className="rounded-[28px] border border-black/8 bg-[linear-gradient(180deg,_rgba(255,252,247,0.98),_rgba(249,244,236,0.95))] p-5 shadow-[0_18px_50px_rgba(25,22,18,0.05)] md:grid md:grid-cols-2 md:gap-4 md:p-6" onSubmit={runPlanAndRender}>
          <div className="md:col-span-2 mb-2">
            <div className="mito-kicker">Launch</div>
            <h4 className="mt-3 text-2xl font-semibold tracking-[-0.04em] text-gray-950">Lanzar plan-and-render</h4>
            <p className="mt-2 text-sm leading-6 text-[#6a645b]">Prepara la secuencia, ajusta continuidad y dispara el flujo desde una caja de mando más visual.</p>
          </div>

          <div className="md:col-span-2">
            <label className="text-xs font-semibold uppercase tracking-[0.14em] text-[#736b60]">script_text *</label>
            <textarea
              value={scriptText}
              onChange={(event) => setScriptText(event.target.value)}
              rows={6}
              placeholder="Escribe un fragmento de guion o texto narrativo…"
              className="mt-2 w-full rounded-2xl border border-black/10 bg-white px-4 py-4 text-sm text-gray-900 outline-none transition focus-visible:border-[#c86f31] focus-visible:ring-4 focus-visible:ring-[#f3dbc8]"
            />
          </div>

          <div>
            <label className="text-xs font-semibold uppercase tracking-[0.14em] text-[#736b60]">project_id</label>
            <input
              type="text"
              value={projectId}
              onChange={(event) => setProjectId(event.target.value)}
              placeholder="project_001…"
              className="mt-2 w-full rounded-2xl border border-black/10 bg-white px-4 py-3 text-sm text-gray-900 outline-none transition focus-visible:border-[#c86f31] focus-visible:ring-4 focus-visible:ring-[#f3dbc8]"
            />
          </div>

          <div>
            <label className="text-xs font-semibold uppercase tracking-[0.14em] text-[#736b60]">sequence_id</label>
            <input
              type="text"
              value={sequenceId}
              onChange={(event) => setSequenceId(event.target.value)}
              placeholder="seq_001…"
              className="mt-2 w-full rounded-2xl border border-black/10 bg-white px-4 py-3 text-sm text-gray-900 outline-none transition focus-visible:border-[#c86f31] focus-visible:ring-4 focus-visible:ring-[#f3dbc8]"
            />
          </div>

          <div>
            <label className="text-xs font-semibold uppercase tracking-[0.14em] text-[#736b60]">style_profile</label>
            <input
              type="text"
              value={styleProfile}
              onChange={(event) => setStyleProfile(event.target.value)}
              placeholder="cinematic still…"
              className="mt-2 w-full rounded-2xl border border-black/10 bg-white px-4 py-3 text-sm text-gray-900 outline-none transition focus-visible:border-[#c86f31] focus-visible:ring-4 focus-visible:ring-[#f3dbc8]"
            />
          </div>

          <div>
            <label className="text-xs font-semibold uppercase tracking-[0.14em] text-[#736b60]">continuity_mode</label>
            <input
              type="text"
              value={continuityMode}
              onChange={(event) => setContinuityMode(event.target.value)}
              placeholder="strict…"
              className="mt-2 w-full rounded-2xl border border-black/10 bg-white px-4 py-3 text-sm text-gray-900 outline-none transition focus-visible:border-[#c86f31] focus-visible:ring-4 focus-visible:ring-[#f3dbc8]"
            />
          </div>

          <div className="rounded-2xl border border-black/8 bg-[#f8f2e9] px-4 py-4">
            <label className="text-xs font-semibold uppercase tracking-[0.14em] text-[#736b60]">semantic prompt enrichment</label>
            <label className="mt-3 flex items-center gap-3 text-sm text-gray-800">
              <input
                type="checkbox"
                checked={semanticPromptEnrichmentEnabled}
                onChange={(event) => setSemanticPromptEnrichmentEnabled(event.target.checked)}
                className="h-4 w-4 rounded border-gray-300"
              />
              activar refuerzo semántico
            </label>
          </div>

          <div>
            <label className="text-xs font-semibold uppercase tracking-[0.14em] text-[#736b60]">semantic max_chars</label>
            <input
              type="number"
              min={0}
              max={2000}
              value={semanticPromptEnrichmentMaxChars}
              onChange={(event) => setSemanticPromptEnrichmentMaxChars(event.target.value)}
              placeholder="400…"
              className="mt-2 w-full rounded-2xl border border-black/10 bg-white px-4 py-3 text-sm text-gray-900 outline-none transition focus-visible:border-[#c86f31] focus-visible:ring-4 focus-visible:ring-[#f3dbc8]"
            />
          </div>

          <div className="md:col-span-2 mt-1 flex flex-wrap gap-3">
            <button
              type="submit"
              disabled={submitting}
              className="rounded-full bg-[#1f1b17] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#312923] disabled:opacity-50"
            >
              {submitting ? "Ejecutando…" : "Lanzar plan-and-render"}
            </button>
          </div>
        </form>

        <div className="rounded-[28px] border border-black/8 bg-[linear-gradient(180deg,_rgba(255,252,247,0.98),_rgba(249,244,236,0.95))] p-5 shadow-[0_18px_50px_rgba(25,22,18,0.05)] md:p-6">
          <div className="mito-kicker">Lookup</div>
          <h4 className="mt-3 text-2xl font-semibold tracking-[-0.04em] text-gray-950">Consultar por request_id</h4>
          <p className="mt-2 text-sm leading-6 text-[#6a645b]">Carga una ejecución concreta y deja el auto-refresh listo para seguir el progreso.</p>

          <div className="mt-5 space-y-3">
            <input
              type="text"
              value={requestIdInput}
              onChange={(event) => setRequestIdInput(event.target.value)}
              placeholder="request_id…"
              className="w-full rounded-2xl border border-black/10 bg-white px-4 py-3 text-sm text-gray-900 outline-none transition focus-visible:border-[#c86f31] focus-visible:ring-4 focus-visible:ring-[#f3dbc8]"
            />

            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={refreshing}
                onClick={() => loadExecution(requestIdInput)}
                className="rounded-full bg-[#1f1b17] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#312923] disabled:opacity-50"
              >
                {refreshing ? "Consultando…" : "Cargar ejecución"}
              </button>
              <button
                type="button"
                disabled={refreshing || !execution}
                onClick={() => execution && loadExecution(execution.request_id)}
                className="rounded-full border border-black/10 bg-white px-4 py-3 text-sm font-semibold text-gray-800 transition hover:bg-[#f6f0e7] disabled:opacity-50"
              >
                Refrescar
              </button>
            </div>

            <div className="rounded-2xl border border-black/8 bg-[#f8f2e9] p-4 text-sm text-gray-700">
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={pollingEnabled}
                  onChange={(event) => setPollingEnabled(event.target.checked)}
                />
                Auto refresh
              </label>

              <label className="mt-3 flex items-center gap-3 text-sm text-gray-700">
                <span>intervalo (ms)</span>
                <input
                  type="number"
                  min={1000}
                  step={500}
                  value={pollingIntervalMs}
                  disabled={!pollingEnabled}
                  onChange={(event) => {
                    const parsed = Number(event.target.value);
                    if (!Number.isFinite(parsed)) {
                      return;
                    }
                    setPollingIntervalMs(Math.max(1000, Math.trunc(parsed)));
                  }}
                  className="w-28 rounded-xl border border-black/10 bg-white px-3 py-2 text-sm disabled:bg-gray-100"
                />
              </label>

              <span
                className="mt-4 inline-flex items-center gap-2 rounded-full border px-3 py-2 text-xs font-semibold"
                style={
                  pollingEnabled && hasActiveJobs
                    ? pollingInFlight
                      ? getStatusStyle("running")
                      : getStatusStyle("queued")
                    : getStatusStyle("succeeded")
                }
              >
                <span
                  className="inline-block h-2 w-2 rounded-full"
                  style={{
                    backgroundColor:
                      pollingEnabled && hasActiveJobs
                        ? pollingInFlight
                          ? "#92400e"
                          : "#1d4ed8"
                        : "#166534",
                  }}
                />
                {pollingEnabled && hasActiveJobs
                  ? pollingInFlight
                    ? "Auto refresh consultando…"
                    : `Auto refresh activo cada ${Math.round(pollingIntervalMs / 1000)}s`
                  : pollingEnabled
                    ? "Auto refresh en espera (sin jobs activos)"
                    : "Auto refresh desactivado"}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 rounded-[28px] border border-black/8 bg-[linear-gradient(180deg,_rgba(255,252,247,0.98),_rgba(249,244,236,0.95))] p-5 shadow-[0_18px_50px_rgba(25,22,18,0.05)] md:p-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="mito-kicker">Dashboard</div>
            <h4 className="mt-3 text-2xl font-semibold tracking-[-0.04em] text-gray-950">Dashboard global de colecciones</h4>
            <p className="mt-2 text-sm leading-6 text-[#6a645b]">Vista agregada del estado editorial y operativo de todas las colecciones.</p>
          </div>
          <button
            type="button"
            disabled={collectionsDashboardLoading}
            onClick={() => void loadCollectionsDashboard(false)}
            className="rounded-full border border-black/10 bg-white px-4 py-3 text-sm font-semibold text-gray-800 transition hover:bg-[#f6f0e7] disabled:opacity-50"
          >
            {collectionsDashboardLoading ? "Actualizando dashboard…" : "Actualizar dashboard"}
          </button>
        </div>

        <div className="mt-5 rounded-2xl border border-gray-200 bg-white p-4">

        {collectionsDashboardError ? (
          <div className="mt-3 px-2 py-2 rounded border border-red-200 bg-red-50 text-[11px] text-red-700">{collectionsDashboardError}</div>
        ) : null}

        {collectionsDashboardLoading ? (
          <div className="mt-3 text-[11px] text-gray-500">Cargando dashboard global...</div>
        ) : collectionsDashboard ? (
          <div className="mt-3 space-y-3">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-[11px]">
              <div className="px-2 py-2 rounded border border-gray-200 bg-gray-50">
                <div className="text-gray-500">total_collections</div>
                <div className="font-semibold text-gray-800">{collectionsDashboard.total_collections}</div>
              </div>
              <div className="px-2 py-2 rounded border border-green-200 bg-green-50">
                <div className="text-green-700">collections_green</div>
                <div className="font-semibold text-green-800">{collectionsDashboard.collections_green}</div>
              </div>
              <div className="px-2 py-2 rounded border border-amber-200 bg-amber-50">
                <div className="text-amber-700">collections_yellow</div>
                <div className="font-semibold text-amber-800">{collectionsDashboard.collections_yellow}</div>
              </div>
              <div className="px-2 py-2 rounded border border-red-200 bg-red-50">
                <div className="text-red-700">collections_red</div>
                <div className="font-semibold text-red-800">{collectionsDashboard.collections_red}</div>
              </div>
            </div>

            <div>
              <div className="text-[11px] font-semibold text-gray-600 mb-1">Distribución por semáforo</div>
              <div className="h-2 w-full rounded bg-gray-200 overflow-hidden flex">
                <div
                  style={{
                    width: `${collectionsDashboard.total_collections > 0 ? (collectionsDashboard.collections_green / collectionsDashboard.total_collections) * 100 : 0}%`,
                    background: "#16a34a",
                  }}
                />
                <div
                  style={{
                    width: `${collectionsDashboard.total_collections > 0 ? (collectionsDashboard.collections_yellow / collectionsDashboard.total_collections) * 100 : 0}%`,
                    background: "#ca8a04",
                  }}
                />
                <div
                  style={{
                    width: `${collectionsDashboard.total_collections > 0 ? (collectionsDashboard.collections_red / collectionsDashboard.total_collections) * 100 : 0}%`,
                    background: "#dc2626",
                  }}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-2 text-[11px]">
              <div className="p-2 rounded border border-gray-200 bg-gray-50">
                <div className="font-semibold text-gray-700 mb-1">Top por ejecuciones</div>
                {collectionsDashboard.top_collections_by_executions.length > 0 ? (
                  <div className="space-y-1">
                    {collectionsDashboard.top_collections_by_executions.map((item) => (
                      <button
                        key={`dashboard-top-exec-${item.collection_id}`}
                        type="button"
                        onClick={() => setSelectedCollectionId(item.collection_id)}
                        className="w-full text-left px-2 py-1 rounded border border-gray-200 bg-white"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <span className="font-semibold text-gray-700 truncate">{item.name}</span>
                          <span className="px-2 py-0.5 rounded border text-[10px]" style={getCollectionHealthStyle(item.health_status)}>{formatCollectionHealthLabel(item.health_status)}</span>
                        </div>
                        <div className="text-gray-500">exec={item.total_executions} | retries={item.total_retries}</div>
                      </button>
                    ))}
                  </div>
                ) : <div className="text-gray-500">Sin datos.</div>}
              </div>

              <div className="p-2 rounded border border-gray-200 bg-gray-50">
                <div className="font-semibold text-gray-700 mb-1">Top por retries</div>
                {collectionsDashboard.top_collections_by_retries.length > 0 ? (
                  <div className="space-y-1">
                    {collectionsDashboard.top_collections_by_retries.map((item) => (
                      <button
                        key={`dashboard-top-retries-${item.collection_id}`}
                        type="button"
                        onClick={() => setSelectedCollectionId(item.collection_id)}
                        className="w-full text-left px-2 py-1 rounded border border-gray-200 bg-white"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <span className="font-semibold text-gray-700 truncate">{item.name}</span>
                          <span className="px-2 py-0.5 rounded border text-[10px]" style={getCollectionHealthStyle(item.health_status)}>{formatCollectionHealthLabel(item.health_status)}</span>
                        </div>
                        <div className="text-gray-500">retries={item.total_retries} | success={(item.success_ratio * 100).toFixed(1)}%</div>
                      </button>
                    ))}
                  </div>
                ) : <div className="text-gray-500">Sin datos.</div>}
              </div>

              <div className="p-2 rounded border border-gray-200 bg-gray-50">
                <div className="font-semibold text-gray-700 mb-1">Sin best execution</div>
                {collectionsDashboard.collections_without_best_execution.length > 0 ? (
                  <div className="space-y-1">
                    {collectionsDashboard.collections_without_best_execution.map((item) => (
                      <button
                        key={`dashboard-without-best-${item.collection_id}`}
                        type="button"
                        onClick={() => setSelectedCollectionId(item.collection_id)}
                        className="w-full text-left px-2 py-1 rounded border border-gray-200 bg-white"
                      >
                        <div className="font-semibold text-gray-700 truncate">{item.name}</div>
                        <div className="text-gray-500">exec={item.total_executions} | pending={item.pending_review_count}</div>
                      </button>
                    ))}
                  </div>
                ) : <div className="text-gray-500">Sin pendientes de best.</div>}
              </div>

              <div className="p-2 rounded border border-gray-200 bg-gray-50">
                <div className="font-semibold text-gray-700 mb-1">Con pending review</div>
                {collectionsDashboard.collections_with_pending_review.length > 0 ? (
                  <div className="space-y-1">
                    {collectionsDashboard.collections_with_pending_review.map((item) => (
                      <button
                        key={`dashboard-pending-${item.collection_id}`}
                        type="button"
                        onClick={() => setSelectedCollectionId(item.collection_id)}
                        className="w-full text-left px-2 py-1 rounded border border-gray-200 bg-white"
                      >
                        <div className="font-semibold text-gray-700 truncate">{item.name}</div>
                        <div className="text-gray-500">pending={item.pending_review_count} | exec={item.total_executions}</div>
                      </button>
                    ))}
                  </div>
                ) : <div className="text-gray-500">Sin colecciones con pending review.</div>}
              </div>
            </div>

            {collectionsDashboard.highlighted_collections.length > 0 ? (
              <div className="p-2 rounded border border-gray-200 bg-gray-50">
                <div className="font-semibold text-gray-700 mb-1 text-[11px]">Colecciones destacadas</div>
                <div className="flex flex-wrap gap-1">
                  {collectionsDashboard.highlighted_collections.map((item) => (
                    <button
                      key={`dashboard-highlighted-${item.collection_id}`}
                      type="button"
                      onClick={() => setSelectedCollectionId(item.collection_id)}
                      className="px-2 py-1 text-[11px] rounded border bg-white"
                      style={getCollectionHealthStyle(item.health_status)}
                    >
                      {item.name}
                    </button>
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        ) : null}
        </div>
      </div>

      <div className="mt-4 p-4 rounded-xl border border-gray-200 bg-white">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <div>
            <div className="text-xs font-semibold text-gray-600">Notificaciones de alertas por colección</div>
            <div className="text-xs text-gray-500">
              Alertas automáticas cuando una colección entra en riesgo o supera umbrales relevantes.
            </div>
          </div>
          <div className="flex items-center gap-2">
            <label className="inline-flex items-center gap-1 text-[11px] text-gray-600">
              <input
                type="checkbox"
                checked={notificationsUnreadOnly}
                onChange={(event) => setNotificationsUnreadOnly(event.target.checked)}
              />
              solo no leídas
            </label>
            <button
              type="button"
              disabled={notificationsLoading}
              onClick={() => void loadNotifications(false)}
              className="px-3 py-1 text-xs font-semibold rounded border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
            >
              {notificationsLoading ? "Actualizando..." : "Actualizar notificaciones"}
            </button>
          </div>
        </div>

        {notificationPreferencesLoading ? (
          <div className="mt-3 text-[11px] text-gray-500">Cargando preferencias de notificación...</div>
        ) : notificationPreferences ? (
          <div className="mt-3 p-3 rounded border border-gray-200 bg-gray-50 space-y-2">
            <div className="text-[11px] font-semibold text-gray-600">Preferencias de notificación</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px]">
              <label className="inline-flex items-center gap-2 text-gray-700">
                <input
                  type="checkbox"
                  checked={notificationEnabledInput}
                  onChange={(event) => setNotificationEnabledInput(event.target.checked)}
                />
                notifications_enabled
              </label>

              <label className="inline-flex items-center gap-2 text-gray-700">
                <input
                  type="checkbox"
                  checked={notificationUnreadDefaultInput}
                  onChange={(event) => setNotificationUnreadDefaultInput(event.target.checked)}
                />
                show_only_unread_by_default
              </label>

              <label className="text-gray-700">
                min_severity
                <select
                  value={notificationMinSeverityInput}
                  onChange={(event) => setNotificationMinSeverityInput(event.target.value as SequenceNotificationSeverity)}
                  className="mt-1 w-full px-2 py-1 rounded border border-gray-300 bg-white"
                >
                  <option value="info">info</option>
                  <option value="warning">warning</option>
                  <option value="critical">critical</option>
                </select>
              </label>

              <label className="text-gray-700">
                enabled_types (coma o salto de línea)
                <textarea
                  value={notificationEnabledTypesInput}
                  onChange={(event) => setNotificationEnabledTypesInput(event.target.value)}
                  rows={3}
                  className="mt-1 w-full px-2 py-1 rounded border border-gray-300 bg-white"
                />
              </label>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                disabled={notificationPreferencesSaving}
                onClick={() => void saveNotificationPreferences()}
                className="px-3 py-1 text-xs font-semibold rounded border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
              >
                {notificationPreferencesSaving ? "Guardando preferencias..." : "Guardar preferencias"}
              </button>
              <button
                type="button"
                disabled={notificationPreferencesLoading}
                onClick={() => void loadNotificationPreferences(false)}
                className="px-3 py-1 text-xs font-semibold rounded border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
              >
                Recargar preferencias
              </button>
            </div>
          </div>
        ) : null}

        {notificationPreferencesError ? (
          <div className="mt-3 px-2 py-2 rounded border border-red-200 bg-red-50 text-[11px] text-red-700">{notificationPreferencesError}</div>
        ) : null}

        {notificationsError ? (
          <div className="mt-3 px-2 py-2 rounded border border-red-200 bg-red-50 text-[11px] text-red-700">{notificationsError}</div>
        ) : null}

        {notificationPreferences && !notificationPreferences.notifications_enabled ? (
          <div className="mt-3 text-[11px] text-gray-500">
            Notificaciones deshabilitadas por preferencia del usuario. Ajusta preferencias para volver a ver la bandeja.
          </div>
        ) : null}

        {notificationsLoading ? (
          <div className="mt-3 text-[11px] text-gray-500">Cargando notificaciones...</div>
        ) : notificationPreferences && !notificationPreferences.notifications_enabled ? null : notifications.length > 0 ? (
          <div className="mt-3 space-y-2 max-h-64 overflow-auto pr-1">
            {notifications.map((notification) => (
              <div
                key={`notification-${notification.notification_id}`}
                className="p-2 rounded border border-gray-200 bg-gray-50"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span
                    className="px-2 py-0.5 rounded text-[10px] font-semibold border"
                    style={getNotificationSeverityStyle(notification.severity)}
                  >
                    {notification.severity}
                  </span>
                  <span className="text-[11px] text-gray-500">{notification.type}</span>
                  <span className="ml-auto text-[11px] text-gray-500">{formatTimestamp(notification.created_at)}</span>
                </div>
                <div className="mt-1 text-xs text-gray-700">{notification.message}</div>
                <div className="mt-2 flex flex-wrap items-center gap-2 text-[11px]">
                  <span className="px-2 py-0.5 rounded border border-gray-300 bg-white text-gray-600">
                    collection: {notification.collection_id}
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded border ${notification.is_read ? "border-green-300 bg-green-50 text-green-700" : "border-amber-300 bg-amber-50 text-amber-700"}`}
                  >
                    {notification.is_read ? "leída" : "no leída"}
                  </span>
                  <button
                    type="button"
                    onClick={() => setSelectedCollectionId(notification.collection_id)}
                    className="px-2 py-0.5 rounded border border-gray-300 bg-white text-gray-700"
                  >
                    Abrir colección
                  </button>
                  <button
                    type="button"
                    disabled={notification.is_read || notificationActionId === notification.notification_id}
                    onClick={() => void markNotificationAsRead(notification.notification_id)}
                    className="px-2 py-0.5 rounded border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
                  >
                    {notificationActionId === notification.notification_id ? "Marcando..." : "Marcar leída"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="mt-3 text-[11px] text-gray-500">Sin notificaciones.</div>
        )}
      </div>

      <SequenceWebhooksPanel className="mt-4" />

      <div className="mt-4 p-4 rounded-xl border border-gray-200 bg-white">
        <div className="flex flex-col gap-1">
          <div className="text-xs font-semibold text-gray-600">Panel de revisión por colección</div>
          <div className="text-xs text-gray-500">
            Espacio editorial/operativo para revisar ejecuciones agrupadas, marcar candidatas y comparar dentro de la colección.
          </div>
        </div>

        <div className="mt-3 grid grid-cols-1 xl:grid-cols-3 gap-3">
          <div className="xl:col-span-1 p-3 rounded-lg border border-gray-200 bg-gray-50 space-y-3">
            <div>
              <div className="text-[11px] font-semibold text-gray-600">Crear colección</div>
              <input
                type="text"
                value={createCollectionName}
                onChange={(event) => setCreateCollectionName(event.target.value)}
                placeholder="Nombre colección"
                className="w-full mt-1 px-3 py-2 text-xs rounded-lg border border-gray-200"
              />
              <textarea
                value={createCollectionDescription}
                onChange={(event) => setCreateCollectionDescription(event.target.value)}
                rows={2}
                placeholder="Descripción"
                className="w-full mt-1 px-3 py-2 text-xs rounded-lg border border-gray-200"
              />
              <button
                type="button"
                disabled={collectionSaving}
                onClick={() => void createCollectionFromForm()}
                className="mt-1 px-3 py-1 text-xs font-semibold rounded-md border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
              >
                {collectionSaving ? "Creando..." : "Crear colección"}
              </button>
            </div>

            <div>
              <div className="text-[11px] font-semibold text-gray-600">Colecciones</div>
              <div className="mt-1 space-y-1 max-h-64 overflow-auto pr-1">
                {collections.map((collection) => {
                  const isSelected = collection.collection_id === selectedCollectionId;
                  return (
                    <button
                      key={collection.collection_id}
                      type="button"
                      onClick={() => setSelectedCollectionId(collection.collection_id)}
                      className="w-full text-left px-2 py-2 rounded border text-xs"
                      style={isSelected ? { borderColor: "#3b82f6", background: "#eff6ff" } : undefined}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <div className="font-semibold text-gray-700">{collection.name}</div>
                        <span
                          className="px-2 py-0.5 rounded text-[10px] font-semibold border"
                          style={getCollectionHealthStyle(collection.health_status)}
                        >
                          {formatCollectionHealthLabel(collection.health_status)}
                        </span>
                      </div>
                      <div className="text-[11px] text-gray-500">
                        items: {collection.item_count} | candidatas: {collection.highlighted_count}
                      </div>
                      {collection.alerts.length > 0 ? (
                        <div className="text-[11px] text-amber-700 mt-1 truncate">
                          alertas: {collection.alerts[0]}
                        </div>
                      ) : (
                        <div className="text-[11px] text-green-700 mt-1">sin alertas activas</div>
                      )}
                    </button>
                  );
                })}
                {collections.length === 0 ? (
                  <div className="text-[11px] text-gray-500 px-2 py-2 border border-dashed rounded">Sin colecciones</div>
                ) : null}
              </div>
            </div>

            {collectionsError ? (
              <div className="px-2 py-2 rounded border border-red-200 bg-red-50 text-[11px] text-red-700">{collectionsError}</div>
            ) : null}
            {collectionsLoading ? (
              <div className="text-[11px] text-gray-500">Cargando colecciones...</div>
            ) : null}
          </div>

          <div className="xl:col-span-2 p-3 rounded-lg border border-gray-200 bg-gray-50">
            {!selectedCollection ? (
              <div className="text-xs text-gray-500">Selecciona una colección para revisar ejecuciones.</div>
            ) : (
              <div className="space-y-3">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <div className="text-sm font-semibold text-gray-800">{selectedCollection.name}</div>
                      <span
                        className="px-2 py-0.5 rounded text-[10px] font-semibold border"
                        style={getCollectionHealthStyle(selectedCollection.health_status)}
                      >
                        {formatCollectionHealthLabel(selectedCollection.health_status)}
                      </span>
                    </div>
                    <div className="text-xs text-gray-500">{selectedCollection.description || "Sin descripción"}</div>
                    <div className="text-[11px] text-gray-500 mt-1">
                      items: {selectedCollection.item_count} | candidatas: {selectedCollection.highlighted_count}
                    </div>
                    <div className="text-[11px] text-gray-500 mt-1">
                      best execution: {selectedCollection.best_request_id || "-"}
                    </div>
                    <div className="text-[11px] text-gray-500 mt-1">
                      alertas activas: {selectedCollection.alerts.length}
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <select
                      value={collectionReviewRanking}
                      onChange={(event) => setCollectionReviewRanking(event.target.value as RecentRankingFilter)}
                      className="px-3 py-1 text-xs rounded border border-gray-300 bg-white"
                    >
                      {RECENT_RANKING_OPTIONS.map((option) => (
                        <option key={`collection-ranking-${option}`} value={option}>{option}</option>
                      ))}
                    </select>
                    <button
                      type="button"
                      disabled={collectionReviewLoading || collectionAuditLoading}
                      onClick={() => {
                        void loadCollectionReview(selectedCollection.collection_id, false);
                        void loadCollectionAudit(selectedCollection.collection_id, false);
                      }}
                      className="px-3 py-1 text-xs font-semibold rounded border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
                    >
                      {collectionReviewLoading || collectionAuditLoading ? "Actualizando..." : "Actualizar"}
                    </button>
                    <button
                      type="button"
                      disabled={!collectionReview}
                      onClick={handleExportCollectionJson}
                      className="px-3 py-1 text-xs font-semibold rounded border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
                    >
                      Exportar colección JSON
                    </button>
                    <button
                      type="button"
                      disabled={collectionExecutiveExportingJson || !selectedCollection}
                      onClick={() => void handleExportCollectionExecutiveJson()}
                      className="px-3 py-1 text-xs font-semibold rounded border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
                    >
                      {collectionExecutiveExportingJson ? "Exportando informe JSON..." : "Exportar informe ejecutivo JSON"}
                    </button>
                    <button
                      type="button"
                      disabled={collectionExecutiveExportingPdf || !selectedCollection}
                      onClick={() => void handleExportCollectionExecutivePdf()}
                      className="px-3 py-1 text-xs font-semibold rounded border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
                    >
                      {collectionExecutiveExportingPdf ? "Exportando informe PDF..." : "Exportar informe ejecutivo PDF"}
                    </button>
                    <button
                      type="button"
                      disabled={collectionItemActionRequestId === "__clear_best__" || !selectedCollection.best_request_id}
                      onClick={() => void setCollectionBestCandidate(null)}
                      className="px-3 py-1 text-xs font-semibold rounded border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
                    >
                      Limpiar best
                    </button>
                  </div>
                </div>

                {collectionAuditError ? (
                  <div className="px-2 py-2 rounded border border-red-200 bg-red-50 text-[11px] text-red-700">{collectionAuditError}</div>
                ) : null}

                {collectionAuditLoading ? (
                  <div className="text-[11px] text-gray-500">Cargando auditoría de colección...</div>
                ) : collectionAudit ? (
                  <div className="p-3 rounded-lg border border-gray-200 bg-white space-y-3">
                    <div className="flex items-center justify-between gap-2">
                      <div className="text-xs font-semibold text-gray-700">Auditoría de colección</div>
                      <span
                        className="px-2 py-1 rounded text-[11px] font-semibold border"
                        style={getCollectionHealthStyle(collectionAudit.health_status)}
                      >
                        {formatCollectionHealthLabel(collectionAudit.health_status)}
                      </span>
                    </div>

                    <div>
                      <div className="text-[11px] font-semibold text-gray-600 mb-1">Alertas activas</div>
                      {collectionAudit.alerts.length > 0 ? (
                        <div className="space-y-1">
                          {collectionAudit.alerts.map((alert, index) => (
                            <div
                              key={`collection-audit-alert-${collectionAudit.collection_id}-${index}`}
                              className="px-2 py-1 rounded border border-amber-200 bg-amber-50 text-[11px] text-amber-800"
                            >
                              {alert}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-[11px] text-green-700">Sin alertas activas.</div>
                      )}
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-6 gap-2 text-[11px]">
                      <div className="px-2 py-2 rounded border border-gray-200 bg-gray-50"><div className="text-gray-500">total</div><div className="font-semibold text-gray-800">{collectionAudit.total_executions}</div></div>
                      <div className="px-2 py-2 rounded border border-gray-200 bg-gray-50"><div className="text-gray-500">approved</div><div className="font-semibold text-green-700">{collectionAudit.approved_count}</div></div>
                      <div className="px-2 py-2 rounded border border-gray-200 bg-gray-50"><div className="text-gray-500">rejected</div><div className="font-semibold text-red-700">{collectionAudit.rejected_count}</div></div>
                      <div className="px-2 py-2 rounded border border-gray-200 bg-gray-50"><div className="text-gray-500">pending</div><div className="font-semibold text-gray-700">{collectionAudit.pending_review_count}</div></div>
                      <div className="px-2 py-2 rounded border border-gray-200 bg-gray-50"><div className="text-gray-500">favoritas</div><div className="font-semibold text-amber-700">{collectionAudit.favorite_count}</div></div>
                      <div className="px-2 py-2 rounded border border-gray-200 bg-gray-50"><div className="text-gray-500">sin review</div><div className="font-semibold text-orange-700">{collectionAudit.executions_without_review}</div></div>
                      <div className="px-2 py-2 rounded border border-gray-200 bg-gray-50"><div className="text-gray-500">total jobs</div><div className="font-semibold text-gray-800">{collectionAudit.total_jobs}</div></div>
                      <div className="px-2 py-2 rounded border border-gray-200 bg-gray-50"><div className="text-gray-500">total retries</div><div className="font-semibold text-gray-800">{collectionAudit.total_retries}</div></div>
                      <div className="px-2 py-2 rounded border border-gray-200 bg-gray-50"><div className="text-gray-500">failed</div><div className="font-semibold text-red-700">{collectionAudit.failed_count}</div></div>
                      <div className="px-2 py-2 rounded border border-gray-200 bg-gray-50"><div className="text-gray-500">timeout</div><div className="font-semibold text-purple-700">{collectionAudit.timeout_count}</div></div>
                      <div className="px-2 py-2 rounded border border-gray-200 bg-gray-50 xl:col-span-2"><div className="text-gray-500">success ratio</div><div className="font-semibold text-gray-800">{(collectionAudit.success_ratio_summary.ratio * 100).toFixed(1)}%</div></div>
                    </div>

                    <div>
                      <div className="text-[11px] font-semibold text-gray-600 mb-1">Distribución editorial</div>
                      <div className="h-2 w-full rounded bg-gray-200 overflow-hidden flex">
                        <div style={{ width: `${collectionAudit.total_executions > 0 ? (collectionAudit.approved_count / collectionAudit.total_executions) * 100 : 0}%`, background: "#16a34a" }} />
                        <div style={{ width: `${collectionAudit.total_executions > 0 ? (collectionAudit.rejected_count / collectionAudit.total_executions) * 100 : 0}%`, background: "#dc2626" }} />
                        <div style={{ width: `${collectionAudit.total_executions > 0 ? (collectionAudit.pending_review_count / collectionAudit.total_executions) * 100 : 0}%`, background: "#6b7280" }} />
                      </div>
                      <div className="mt-1 text-[11px] text-gray-600">
                        {formatReviewStatusLabel("approved")}: {collectionAudit.approved_count} | {formatReviewStatusLabel("rejected")}: {collectionAudit.rejected_count} | {formatReviewStatusLabel("pending_review")}: {collectionAudit.pending_review_count}
                      </div>
                    </div>

                    <div>
                      <div className="text-[11px] font-semibold text-gray-600 mb-1">Señales</div>
                      {collectionAudit.signals.length > 0 ? (
                        <div className="space-y-1">
                          {collectionAudit.signals.map((signal) => (
                            <div
                              key={`collection-audit-signal-${signal.code}`}
                              className="px-2 py-1 rounded border text-[11px]"
                              style={
                                signal.severity === "critical"
                                  ? { borderColor: "#fecaca", background: "#fef2f2", color: "#991b1b" }
                                  : signal.severity === "warning"
                                    ? { borderColor: "#fde68a", background: "#fffbeb", color: "#92400e" }
                                    : { borderColor: "#bfdbfe", background: "#eff6ff", color: "#1d4ed8" }
                              }
                            >
                              {signal.code}: {signal.message}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-[11px] text-gray-500">Sin alertas relevantes.</div>
                      )}
                    </div>
                  </div>
                ) : null}

                <div>
                  <label className="text-[11px] font-semibold text-gray-600">Nota editorial de colección</label>
                  <textarea
                    value={collectionEditorialNoteDraft}
                    onChange={(event) => setCollectionEditorialNoteDraft(event.target.value)}
                    rows={3}
                    placeholder="Criterios editoriales de revisión"
                    className="w-full mt-1 px-3 py-2 text-xs rounded-lg border border-gray-200"
                  />
                  <button
                    type="button"
                    disabled={collectionSaving}
                    onClick={() => void saveCollectionEditorialNote()}
                    className="mt-1 px-3 py-1 text-xs font-semibold rounded border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
                  >
                    {collectionSaving ? "Guardando..." : "Guardar nota editorial"}
                  </button>
                </div>

                {collectionReviewError ? (
                  <div className="px-2 py-2 rounded border border-red-200 bg-red-50 text-[11px] text-red-700">{collectionReviewError}</div>
                ) : null}

                {collectionReview ? (
                  <div className="space-y-2 max-h-[420px] overflow-auto pr-1">
                    {collectionReview.executions.map((item) => (
                      <div
                        key={`collection-review-${item.request_id}`}
                        className="p-3 rounded-md border bg-white"
                        style={
                          item.collection_best
                            ? { borderColor: "#0891b2", background: "#ecfeff" }
                            : item.collection_candidate
                              ? { borderColor: "#f59e0b", background: "#fffbeb" }
                              : undefined
                        }
                      >
                        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-2">
                          <div className="min-w-0">
                            <button
                              type="button"
                              onClick={() => loadExecution(item.request_id)}
                              className="text-xs font-mono text-blue-700 hover:text-blue-900 underline break-all"
                            >
                              {item.request_id}
                            </button>
                            <div className="mt-1 text-xs text-gray-700">{item.sequence_summary || "-"}</div>
                            <div className="mt-1 flex flex-wrap gap-1">
                              {item.is_favorite ? (
                                <span className="px-2 py-1 text-[11px] rounded border border-amber-300 bg-amber-50 text-amber-700">favorita</span>
                              ) : null}
                              {isProblematicRecentExecution(item) ? (
                                <span className="px-2 py-1 text-[11px] rounded border border-red-300 bg-red-50 text-red-700">problemática</span>
                              ) : null}
                              {isStableRecentExecution(item) ? (
                                <span className="px-2 py-1 text-[11px] rounded border border-green-300 bg-green-50 text-green-700">estable</span>
                              ) : null}
                              {item.collection_candidate ? (
                                <span className="px-2 py-1 text-[11px] rounded border border-amber-300 bg-amber-50 text-amber-700">candidata destacada</span>
                              ) : null}
                              {item.collection_best ? (
                                <span className="px-2 py-1 text-[11px] rounded border border-cyan-300 bg-cyan-50 text-cyan-700">best execution</span>
                              ) : null}
                            </div>
                            <div className="mt-1 flex flex-wrap gap-1">
                              {item.tags.length > 0 ? item.tags.map((tag) => (
                                <span key={`collection-item-${item.request_id}-${tag}`} className="px-2 py-1 text-[11px] rounded border border-gray-300 bg-white text-gray-700">
                                  {tag}
                                </span>
                              )) : <span className="text-[11px] text-gray-500">sin etiquetas</span>}
                            </div>
                            <div className="mt-2 flex items-center gap-2">
                              <span 
                                className="px-2 py-0.5 rounded text-[10px] font-bold uppercase border shadow-sm"
                                style={getReviewStatusStyle(item.review_status)}
                              >
                                {item.review_status === "pending_review" ? "Pendiente" : item.review_status === "approved" ? "Aprobado" : "Rechazado"}
                              </span>
                              {item.reviewed_at ? (
                                <span className="text-[10px] text-gray-400 italic">
                                  {formatTimestamp(item.reviewed_at)}
                                </span>
                              ) : null}
                            </div>
                            
                            <div className="mt-2 flex flex-wrap gap-1">
                              {REVIEW_STATUS_OPTIONS.map((status) => {
                                const isSelected = item.review_status === status;
                                return (
                                  <button
                                    key={`quick-review-${item.request_id}-${status}`}
                                    type="button"
                                    disabled={reviewSaving}
                                    onClick={() => void applyReviewUpdate(item.request_id, status, item.review_note)}
                                    className={`px-2 py-1 text-[10px] font-bold rounded border transition-all ${
                                      isSelected ? "shadow-sm scale-[1.05]" : "opacity-40 hover:opacity-100 bg-white hover:scale-[1.02]"
                                    }`}
                                    style={isSelected ? getReviewStatusStyle(status) : undefined}
                                    title={`Marcar como ${status}`}
                                  >
                                    {status === "pending_review" ? "⏸️" : status === "approved" ? "✅" : "❌"}
                                  </button>
                                );
                              })}
                            </div>

                            <div className="mt-2 text-[11px] text-gray-600 bg-white/50 p-2 rounded border border-gray-100 italic">
                              {item.review_note ? `“${item.review_note}”` : "sin feedback editorial"}
                            </div>
                          </div>

                          <div className="flex flex-col items-start md:items-end gap-1 text-[11px] text-gray-600">
                            <span className="px-2 py-1 rounded border border-gray-300 bg-white">jobs: {item.job_count}</span>
                            <span className="px-2 py-1 rounded border border-gray-300 bg-white">
                              success_ratio: {(item.success_ratio * 100).toFixed(1)}%
                            </span>
                            <span className="px-2 py-1 rounded border border-gray-300 bg-white">retries: {item.total_retries}</span>
                            <div className="flex flex-wrap gap-1 md:justify-end">
                              {Object.entries(item.status_summary.by_status).map(([status, count]) => (
                                <span key={`collection-status-${item.request_id}-${status}`} className="px-2 py-1 rounded border" style={getStatusStyle(status)}>
                                  {status}: {count}
                                </span>
                              ))}
                            </div>
                            <div className="flex flex-wrap gap-1 md:justify-end">
                              <button
                                type="button"
                                onClick={() => assignComparisonSide("left", item.request_id)}
                                className="px-2 py-1 text-[11px] rounded border border-gray-300 bg-white text-gray-700"
                              >
                                Comparar A
                              </button>
                              <button
                                type="button"
                                onClick={() => assignComparisonSide("right", item.request_id)}
                                className="px-2 py-1 text-[11px] rounded border border-gray-300 bg-white text-gray-700"
                              >
                                Comparar B
                              </button>
                              <button
                                type="button"
                                disabled={collectionItemActionRequestId === item.request_id}
                                onClick={() => void toggleCollectionCandidate(item)}
                                className="px-2 py-1 text-[11px] rounded border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
                              >
                                {item.collection_candidate ? "Quitar candidata" : "Marcar candidata"}
                              </button>
                              <button
                                type="button"
                                disabled={collectionItemActionRequestId === item.request_id}
                                onClick={() => void setCollectionBestCandidate(item.request_id)}
                                className="px-2 py-1 text-[11px] rounded border border-cyan-300 bg-white text-cyan-700 disabled:opacity-50"
                              >
                                {item.collection_best ? "Es best" : "Marcar best"}
                              </button>
                              <button
                                type="button"
                                disabled={collectionItemActionRequestId === item.request_id}
                                onClick={() => void removeExecutionFromSelectedCollection(item.request_id)}
                                className="px-2 py-1 text-[11px] rounded border border-red-200 bg-white text-red-700 disabled:opacity-50"
                              >
                                Remover
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                    {collectionReview.executions.length === 0 ? (
                      <div className="text-[11px] text-gray-500 px-2 py-2 border border-dashed rounded bg-white">
                        La colección no tiene ejecuciones.
                      </div>
                    ) : null}
                  </div>
                ) : null}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="mt-4 p-4 rounded-xl border border-gray-200 bg-white">
        <div className="flex items-center justify-between gap-3">
          <div>
            <div className="text-xs font-semibold text-gray-600">Ejecuciones recientes</div>
            <div className="text-xs text-gray-500">Ordenado por updated_at desc</div>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={clearRecentFilters}
              className="px-3 py-1 text-xs font-semibold rounded-md bg-white text-gray-700 border border-gray-300"
            >
              Limpiar filtros
            </button>
            <button
              type="button"
              disabled={recentLoading}
              onClick={() => loadRecentExecutions(false)}
              className="px-3 py-1 text-xs font-semibold rounded-md bg-white text-gray-700 border border-gray-300 disabled:opacity-50"
            >
              {recentLoading ? "Actualizando..." : "Actualizar lista"}
            </button>
          </div>
        </div>

        <div className="mt-3 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-8 gap-2">
          <div className="xl:col-span-2">
            <label className="text-[11px] font-semibold text-gray-600">Buscar (q)</label>
            <input
              type="text"
              value={recentQuery}
              onChange={(event) => setRecentQuery(event.target.value)}
              placeholder="request_id, summary, project_id, sequence_id"
              className="w-full mt-1 px-3 py-2 text-xs rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-gray-600">status</label>
            <select
              value={recentStatusFilter}
              onChange={(event) => setRecentStatusFilter(event.target.value as StatusFilter)}
              className="w-full mt-1 px-3 py-2 text-xs rounded-lg border border-gray-200 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            >
              {STATUS_FILTER_OPTIONS.map((option) => (
                <option key={`recent-${option}`} value={option}>{option}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-[11px] font-semibold text-gray-600">ranking</label>
            <select
              value={recentRanking}
              onChange={(event) => setRecentRanking(event.target.value as RecentRankingFilter)}
              className="w-full mt-1 px-3 py-2 text-xs rounded-lg border border-gray-200 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            >
              {RECENT_RANKING_OPTIONS.map((option) => (
                <option key={`recent-ranking-${option}`} value={option}>{option}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-[11px] font-semibold text-gray-600">project_id</label>
            <input
              type="text"
              value={recentProjectIdFilter}
              onChange={(event) => setRecentProjectIdFilter(event.target.value)}
              placeholder="project_001"
              className="w-full mt-1 px-3 py-2 text-xs rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-gray-600">sequence_id</label>
            <input
              type="text"
              value={recentSequenceIdFilter}
              onChange={(event) => setRecentSequenceIdFilter(event.target.value)}
              placeholder="seq_001"
              className="w-full mt-1 px-3 py-2 text-xs rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-gray-600">tag</label>
            <input
              type="text"
              value={recentTagFilter}
              onChange={(event) => setRecentTagFilter(event.target.value)}
              placeholder="revision"
              className="w-full mt-1 px-3 py-2 text-xs rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
          </div>

          <div className="flex items-end">
            <label className="inline-flex items-center gap-2 text-[11px] font-semibold text-gray-600">
              <input
                type="checkbox"
                checked={recentFavoriteOnly}
                onChange={(event) => setRecentFavoriteOnly(event.target.checked)}
              />
              solo favoritas
            </label>
          </div>

          <div>
            <label className="text-[11px] font-semibold text-gray-600">limit</label>
            <input
              type="number"
              min={1}
              max={200}
              value={recentLimit}
              onChange={(event) => {
                const parsed = Number(event.target.value);
                if (!Number.isFinite(parsed)) {
                  return;
                }
                setRecentLimit(Math.max(1, Math.min(200, Math.trunc(parsed))));
              }}
              className="w-full mt-1 px-3 py-2 text-xs rounded-lg border border-gray-200 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
          </div>
        </div>

        {recentError ? (
          <div className="mt-3 px-3 py-2 rounded-md border border-red-200 bg-red-50 text-xs text-red-700">{recentError}</div>
        ) : null}

        <div className="mt-3 space-y-2 max-h-72 overflow-auto pr-1">
          {recentExecutions.length === 0 ? (
            <div className="px-3 py-2 rounded-md border border-dashed border-gray-300 bg-gray-50 text-xs text-gray-600">
              Sin ejecuciones recientes.
            </div>
          ) : (
            recentExecutions.map((item) => (
              <div key={item.request_id} className="p-3 rounded-lg border border-gray-200 bg-gray-50">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-2">
                  <div className="min-w-0">
                    <button
                      type="button"
                      onClick={() => loadExecution(item.request_id)}
                      className="text-xs font-mono text-blue-700 hover:text-blue-900 underline break-all"
                    >
                      {item.request_id}
                    </button>
                    <div className="mt-1 flex flex-wrap gap-1">
                      <button
                        type="button"
                        disabled={recentMetaSavingRequestId === item.request_id}
                        onClick={() => void toggleRecentFavorite(item)}
                        className="px-2 py-1 text-[11px] font-semibold rounded border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
                      >
                        {item.is_favorite ? "Quitar favorito" : "Marcar favorito"}
                      </button>
                      <button
                        type="button"
                        disabled={collectionItemActionRequestId === item.request_id || !selectedCollectionId}
                        onClick={() => void addExecutionToSelectedCollection(item.request_id)}
                        className="px-2 py-1 text-[11px] font-semibold rounded border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
                      >
                        Añadir a colección
                      </button>
                      <button
                        type="button"
                        onClick={() => assignComparisonSide("left", item.request_id)}
                        className="px-2 py-1 text-[11px] font-semibold rounded border border-gray-300 bg-white text-gray-700"
                      >
                        Usar en A
                      </button>
                      <button
                        type="button"
                        onClick={() => assignComparisonSide("right", item.request_id)}
                        className="px-2 py-1 text-[11px] font-semibold rounded border border-gray-300 bg-white text-gray-700"
                      >
                        Usar en B
                      </button>
                    </div>
                    <div className="mt-1 text-xs text-gray-700">{item.sequence_summary || "-"}</div>
                    <div className="mt-1 text-[11px] text-gray-500">
                      created_at: {formatTimestamp(item.created_at)} | updated_at: {formatTimestamp(item.updated_at)}
                    </div>
                    <div className="mt-1 text-[11px] text-gray-500">
                      project_id: {item.project_id || "-"} | sequence_id: {item.sequence_id || "-"}
                    </div>
                    <div className="mt-1 text-[11px] text-gray-600">
                      favorito: {item.is_favorite ? "si" : "no"}
                    </div>
                    <div className="mt-2 flex items-center gap-2">
                      <span 
                        className="px-2 py-0.5 rounded text-[10px] font-bold uppercase border shadow-sm"
                        style={getReviewStatusStyle(item.review_status)}
                      >
                        {item.review_status === "pending_review" ? "Pendiente" : item.review_status === "approved" ? "Aprobado" : "Rechazado"}
                      </span>
                      {item.reviewed_at ? (
                        <span className="text-[10px] text-gray-400 italic">
                          {formatTimestamp(item.reviewed_at)}
                        </span>
                      ) : null}
                    </div>
                    {item.collection_best ? (
                      <div className="mt-1 text-[11px] text-cyan-700">best execution en colección</div>
                    ) : null}
                    <div className="mt-1 flex flex-wrap gap-1">
                      {item.tags.length > 0 ? (
                        item.tags.map((tag) => (
                          <span key={`${item.request_id}-tag-${tag}`} className="px-2 py-1 text-[11px] rounded border border-gray-300 bg-white text-gray-700">
                            {tag}
                          </span>
                        ))
                      ) : (
                        <span className="text-[11px] text-gray-500">sin etiquetas</span>
                      )}
                    </div>
                    <div className="mt-1 text-[11px] text-gray-600 whitespace-pre-wrap">
                      note: {item.note ? summarizeText(item.note, 140) : "-"}
                    </div>
                    <div className="mt-2 text-[11px] text-gray-600 italic line-clamp-2">
                      {item.review_note ? `feedback: “${summarizeText(item.review_note, 140)}”` : "sin feedback editorial"}
                    </div>
                  </div>

                  <div className="flex flex-col items-start md:items-end gap-1 text-[11px] text-gray-600">
                    <span className="px-2 py-1 rounded-md border border-gray-300 bg-white">jobs: {item.job_count}</span>
                    <span className="px-2 py-1 rounded-md border border-gray-300 bg-white">
                      success_ratio: {(item.success_ratio * 100).toFixed(1)}%
                    </span>
                    <span className="px-2 py-1 rounded-md border border-gray-300 bg-white">retries: {item.total_retries}</span>
                    <span className="px-2 py-1 rounded-md border border-gray-300 bg-white">
                      terminal: {item.status_summary.terminal_jobs}/{item.status_summary.total_jobs}
                    </span>
                    {typeof item.ranking_score === "number" ? (
                      <span className="px-2 py-1 rounded-md border border-gray-300 bg-white">
                        ranking_score: {item.ranking_score.toFixed(3)}
                      </span>
                    ) : null}
                    {item.ranking_reason ? (
                      <span className="max-w-[320px] text-[11px] text-gray-500 text-right whitespace-pre-wrap">
                        {item.ranking_reason}
                      </span>
                    ) : null}
                    <div className="flex flex-wrap gap-1 md:justify-end">
                      {Object.entries(item.status_summary.by_status).map(([status, count]) => (
                        <span key={`${item.request_id}-${status}`} className="px-2 py-1 rounded-md border" style={getStatusStyle(status)}>
                          {status}: {count}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="mt-4 p-4 rounded-xl border border-gray-200 bg-white">
        <div className="flex flex-col gap-1">
          <div className="text-xs font-semibold text-gray-600">Comparación de ejecuciones</div>
          <div className="text-xs text-gray-500">
            Compara prompt, negative_prompt, render_context, status y retries por shot entre dos request_id.
          </div>
        </div>

        <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-2">
          <div>
            <label className="text-[11px] font-semibold text-gray-600">request_id A</label>
            <input
              type="text"
              value={compareLeftRequestId}
              onChange={(event) => setCompareLeftRequestId(event.target.value)}
              placeholder="request_id izquierda"
              className="w-full mt-1 px-3 py-2 text-xs rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-gray-600">request_id B</label>
            <input
              type="text"
              value={compareRightRequestId}
              onChange={(event) => setCompareRightRequestId(event.target.value)}
              placeholder="request_id derecha"
              className="w-full mt-1 px-3 py-2 text-xs rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
          </div>
        </div>

        <div className="mt-2 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-2">
          <div>
            <label className="text-[11px] font-semibold text-gray-600">Modo de comparación por shot</label>
            <select
              value={compareShotMode}
              onChange={(event) => setCompareShotMode(event.target.value as CompareShotMode)}
              className="w-full mt-1 px-3 py-2 text-xs rounded-lg border border-gray-200 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            >
              {COMPARE_SHOT_MODE_OPTIONS.map((mode) => (
                <option key={`compare-mode-${mode}`} value={mode}>{mode}</option>
              ))}
            </select>
          </div>

          <div className="xl:col-span-3 flex flex-wrap items-end gap-2">
            <button
              type="button"
              disabled={compareLoading}
              onClick={() => void loadComparisonExecutions()}
              className="px-3 py-2 text-xs font-semibold rounded-md bg-blue-600 text-white border border-blue-600 disabled:opacity-50"
            >
              {compareLoading ? "Comparando..." : "Comparar ejecuciones"}
            </button>
            <button
              type="button"
              onClick={swapComparisonSides}
              className="px-3 py-2 text-xs font-semibold rounded-md bg-white text-gray-700 border border-gray-300"
            >
              Intercambiar A/B
            </button>
            <button
              type="button"
              disabled={!execution}
              onClick={() => execution && setCompareLeftRequestId(execution.request_id)}
              className="px-3 py-2 text-xs font-semibold rounded-md bg-white text-gray-700 border border-gray-300 disabled:opacity-50"
            >
              Usar actual en A
            </button>
            <button
              type="button"
              disabled={!execution}
              onClick={() => execution && setCompareRightRequestId(execution.request_id)}
              className="px-3 py-2 text-xs font-semibold rounded-md bg-white text-gray-700 border border-gray-300 disabled:opacity-50"
            >
              Usar actual en B
            </button>
          </div>
        </div>

        {compareError ? (
          <div className="mt-3 px-3 py-2 rounded-md border border-red-200 bg-red-50 text-xs text-red-700">{compareError}</div>
        ) : null}

        {compareLeftExecution && compareRightExecution ? (
          <div className="mt-4 space-y-3">
            <div className="p-3 rounded-lg border border-gray-200 bg-gray-50">
              <div className="text-xs font-semibold text-gray-600 mb-2">Diferencias globales</div>
              <div className="space-y-2">
                {comparisonGlobalFields.map((field) => (
                  <div key={field.key} className="p-2 rounded-md border border-gray-200 bg-white">
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <span className="text-[11px] font-semibold text-gray-600">{field.label}</span>
                      <span className="px-2 py-1 rounded-md border text-[11px]" style={getDiffBadgeStyle(field.diffKind)}>
                        {getDiffBadgeLabel(field.diffKind)}
                      </span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                      <div className="p-2 rounded border border-gray-200 bg-gray-50">
                        <div className="text-[11px] font-semibold text-gray-500 mb-1">A</div>
                        <div className="text-gray-700 whitespace-pre-wrap break-all">
                          {typeof field.leftValue === "string" || typeof field.leftValue === "number"
                            ? String(field.leftValue)
                            : field.leftValue
                              ? prettyJson(field.leftValue)
                              : "-"}
                        </div>
                      </div>
                      <div className="p-2 rounded border border-gray-200 bg-gray-50">
                        <div className="text-[11px] font-semibold text-gray-500 mb-1">B</div>
                        <div className="text-gray-700 whitespace-pre-wrap break-all">
                          {typeof field.rightValue === "string" || typeof field.rightValue === "number"
                            ? String(field.rightValue)
                            : field.rightValue
                              ? prettyJson(field.rightValue)
                              : "-"}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-3 rounded-lg border border-gray-200 bg-gray-50">
              <div className="flex items-center justify-between gap-2 mb-2">
                <div className="text-xs font-semibold text-gray-600">Diferencias por shot</div>
                <div className="text-[11px] text-gray-500">shots comparados: {shotComparisons.length}</div>
              </div>

              <div className="space-y-3 max-h-[560px] overflow-auto pr-1">
                {shotComparisons.map((item) => (
                  <article key={`compare-shot-${item.shotId}`} className="p-3 rounded-md border border-gray-200 bg-white space-y-2">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div>
                        <div className="text-[11px] text-gray-500">shot_id</div>
                        <div className="text-sm font-mono text-gray-800">{item.shotId}</div>
                      </div>
                      <div className="text-[11px] text-gray-600">
                        presencia: A={item.leftExists ? "si" : "no"} | B={item.rightExists ? "si" : "no"}
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                      <div className="p-2 rounded border border-gray-200 bg-gray-50">
                        <div className="text-[11px] font-semibold text-gray-500 mb-1">A</div>
                        <div><strong>shot_type:</strong> {item.shotTypeLeft || "-"}</div>
                        <div className="mt-1"><strong>prompt:</strong> <span className="whitespace-pre-wrap">{item.promptLeft || "-"}</span></div>
                        <div className="mt-1"><strong>negative_prompt:</strong> <span className="whitespace-pre-wrap">{item.negativePromptLeft || "-"}</span></div>
                        <div className="mt-1 flex items-center gap-2">
                          <strong>status:</strong>
                          <span className="px-2 py-1 rounded-md border" style={getStatusStyle(item.statusLeft || "unknown")}>
                            {item.statusLeft || "-"}
                          </span>
                        </div>
                        <div className="mt-1"><strong>retries:</strong> {item.retriesLeft}</div>
                      </div>

                      <div className="p-2 rounded border border-gray-200 bg-gray-50">
                        <div className="text-[11px] font-semibold text-gray-500 mb-1">B</div>
                        <div><strong>shot_type:</strong> {item.shotTypeRight || "-"}</div>
                        <div className="mt-1"><strong>prompt:</strong> <span className="whitespace-pre-wrap">{item.promptRight || "-"}</span></div>
                        <div className="mt-1"><strong>negative_prompt:</strong> <span className="whitespace-pre-wrap">{item.negativePromptRight || "-"}</span></div>
                        <div className="mt-1 flex items-center gap-2">
                          <strong>status:</strong>
                          <span className="px-2 py-1 rounded-md border" style={getStatusStyle(item.statusRight || "unknown")}>
                            {item.statusRight || "-"}
                          </span>
                        </div>
                        <div className="mt-1"><strong>retries:</strong> {item.retriesRight}</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-[11px]">
                      <span className="px-2 py-1 rounded border w-fit" style={getDiffBadgeStyle(item.diffShotType)}>
                        shot_type: {getDiffBadgeLabel(item.diffShotType)}
                      </span>
                      <span className="px-2 py-1 rounded border w-fit" style={getDiffBadgeStyle(item.diffPrompt)}>
                        prompt: {getDiffBadgeLabel(item.diffPrompt)}
                      </span>
                      <span className="px-2 py-1 rounded border w-fit" style={getDiffBadgeStyle(item.diffNegativePrompt)}>
                        negative_prompt: {getDiffBadgeLabel(item.diffNegativePrompt)}
                      </span>
                      <span className="px-2 py-1 rounded border w-fit" style={getDiffBadgeStyle(item.diffRenderContext)}>
                        render_context: {getDiffBadgeLabel(item.diffRenderContext)}
                      </span>
                      <span className="px-2 py-1 rounded border w-fit" style={getDiffBadgeStyle(item.diffStatus)}>
                        status: {getDiffBadgeLabel(item.diffStatus)}
                      </span>
                      <span className="px-2 py-1 rounded border w-fit" style={getDiffBadgeStyle(item.diffRetries)}>
                        retries: {getDiffBadgeLabel(item.diffRetries)}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                      <div className="p-2 rounded border border-gray-200 bg-gray-50">
                        <div className="text-[11px] font-semibold text-gray-500 mb-1">render_context A</div>
                        {item.renderContextLeft ? (
                          <pre className="text-[11px] whitespace-pre-wrap break-all">{prettyJson(item.renderContextLeft)}</pre>
                        ) : (
                          <span className="text-gray-500">-</span>
                        )}
                      </div>
                      <div className="p-2 rounded border border-gray-200 bg-gray-50">
                        <div className="text-[11px] font-semibold text-gray-500 mb-1">render_context B</div>
                        {item.renderContextRight ? (
                          <pre className="text-[11px] whitespace-pre-wrap break-all">{prettyJson(item.renderContextRight)}</pre>
                        ) : (
                          <span className="text-gray-500">-</span>
                        )}
                      </div>
                    </div>

                    {compareShotMode === "history" ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                        <div className="p-2 rounded border border-gray-200 bg-gray-50">
                          <div className="text-[11px] font-semibold text-gray-500 mb-1">Historial A</div>
                          <div className="text-[11px] text-gray-600">
                            {item.leftHistory
                              ? `intentos=${item.leftHistory.attemptsCount}, retries=${item.leftHistory.retriesCount}, cambios_prompt=${item.leftHistory.promptChanges}, cambios_negative=${item.leftHistory.negativePromptChanges}, cambios_context=${item.leftHistory.renderContextChanges}`
                              : "sin historial"}
                          </div>
                          <div className="mt-1 space-y-1">
                            {item.leftAttempts.map((attempt) => (
                              <div key={`left-${item.shotId}-${attempt.retryIndex}-${attempt.jobId || "none"}`} className="text-[11px] text-gray-700">
                                retry={attempt.retryIndex} | status={attempt.status || "-"} | job_id={attempt.jobId || "-"} | updated_at={formatTimestamp(attempt.updatedAt || undefined)}
                              </div>
                            ))}
                          </div>
                        </div>
                        <div className="p-2 rounded border border-gray-200 bg-gray-50">
                          <div className="text-[11px] font-semibold text-gray-500 mb-1">Historial B</div>
                          <div className="text-[11px] text-gray-600">
                            {item.rightHistory
                              ? `intentos=${item.rightHistory.attemptsCount}, retries=${item.rightHistory.retriesCount}, cambios_prompt=${item.rightHistory.promptChanges}, cambios_negative=${item.rightHistory.negativePromptChanges}, cambios_context=${item.rightHistory.renderContextChanges}`
                              : "sin historial"}
                          </div>
                          <div className="mt-1 space-y-1">
                            {item.rightAttempts.map((attempt) => (
                              <div key={`right-${item.shotId}-${attempt.retryIndex}-${attempt.jobId || "none"}`} className="text-[11px] text-gray-700">
                                retry={attempt.retryIndex} | status={attempt.status || "-"} | job_id={attempt.jobId || "-"} | updated_at={formatTimestamp(attempt.updatedAt || undefined)}
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    ) : null}
                  </article>
                ))}
              </div>
            </div>
          </div>
        ) : null}
      </div>

      {panelError ? (
        <div className="mt-4 px-4 py-3 rounded-lg border border-red-200 bg-red-50 text-red-700 text-sm">{panelError}</div>
      ) : null}
      {panelInfo ? (
        <div className="mt-4 px-4 py-3 rounded-lg border border-green-200 bg-green-50 text-green-700 text-sm">{panelInfo}</div>
      ) : null}

      {execution ? (
        <div className="mt-6 space-y-4">
          <div className="p-4 rounded-xl border border-gray-200 bg-white">
            <div className="text-xs text-gray-500">request_id</div>
            <div className="font-mono text-sm text-gray-900 break-all">{execution.request_id}</div>
            <div className="mt-2 text-sm text-gray-700">{execution.plan.sequence_summary}</div>

            <div className="mt-3 p-3 rounded-lg border border-gray-200 bg-gray-50">
              <div className="flex items-center justify-between gap-3 mb-2">
                <div className="text-xs font-semibold text-gray-700 uppercase tracking-tight">Contexto semántico</div>
                <div className="flex flex-wrap gap-2 text-[11px]">
                  <span className="px-2 py-1 rounded border border-gray-300 bg-white text-gray-700">
                    enabled: {execution.plan.semantic_context?.enabled ? "si" : "no"}
                  </span>
                  <span className="px-2 py-1 rounded border border-gray-300 bg-white text-gray-700">
                    count: {execution.plan.semantic_context?.count ?? 0}
                  </span>
                </div>
              </div>

              <div className="mb-2 flex flex-wrap gap-2 text-[11px]">
                <span className="px-2 py-1 rounded border border-gray-300 bg-white text-gray-700">
                  enrichment_enabled: {execution.plan.semantic_prompt_enrichment?.enabled ? "si" : "no"}
                </span>
                <span className="px-2 py-1 rounded border border-gray-300 bg-white text-gray-700">
                  enrichment_max_chars: {execution.plan.semantic_prompt_enrichment?.max_chars ?? 0}
                </span>
              </div>

              {execution.plan.semantic_context?.error ? (
                <div className="mb-2 rounded border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
                  <div className="font-semibold">{execution.plan.semantic_context.error.code}</div>
                  <div className="mt-1">{execution.plan.semantic_context.error.message}</div>
                </div>
              ) : null}

              {execution.plan.semantic_context?.entity_types?.length ? (
                <div className="mb-2 flex flex-wrap gap-2">
                  {execution.plan.semantic_context.entity_types.map((item) => (
                    <span key={`${execution.request_id}-semantic-type-${item}`} className="px-2 py-1 rounded border border-violet-200 bg-violet-50 text-[11px] text-violet-700">
                      {item}
                    </span>
                  ))}
                </div>
              ) : null}

              {execution.plan.semantic_context?.summary_text ? (
                <div className="mb-2 text-xs text-gray-700">
                  <span className="font-semibold text-gray-600">summary_text:</span>{" "}
                  {execution.plan.semantic_context.summary_text}
                </div>
              ) : null}

              {execution.plan.semantic_context?.continuity_hints?.length ? (
                <div className="mb-2">
                  <div className="text-[11px] font-semibold text-gray-600 mb-1">continuity_hints</div>
                  <ul className="space-y-1 pl-4 text-xs text-gray-700 list-disc">
                    {execution.plan.semantic_context.continuity_hints.map((item, index) => (
                      <li key={`${execution.request_id}-semantic-hint-${index}`}>{item}</li>
                    ))}
                  </ul>
                </div>
              ) : null}

              {execution.plan.semantic_context?.items?.length ? (
                <div className="space-y-2">
                  <div className="text-[11px] font-semibold text-gray-600">items relevantes</div>
                  {execution.plan.semantic_context.items.slice(0, 3).map((item, index) => (
                    <div
                      key={`${execution.request_id}-semantic-item-${item.point_id || index}`}
                      className="rounded border border-gray-200 bg-white px-3 py-2 text-xs text-gray-700"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="font-semibold text-gray-800">{item.title || "Untitled context"}</div>
                        <div className="flex flex-wrap gap-2">
                          <span className="px-2 py-1 rounded border border-gray-300 bg-gray-50 text-[11px] text-gray-700">
                            {item.entity_type || "context"}
                          </span>
                          <span className="px-2 py-1 rounded border border-gray-300 bg-gray-50 text-[11px] text-gray-700">
                            score: {typeof item.score === "number" ? item.score.toFixed(3) : "n/a"}
                          </span>
                        </div>
                      </div>
                      <div className="mt-1 text-gray-600">
                        {summarizeSemanticContextText(item.content_excerpt || item.content)}
                      </div>
                    </div>
                  ))}
                </div>
              ) : null}

              {!execution.plan.semantic_context?.error && !((execution.plan.semantic_context?.count ?? 0) > 0) ? (
                <div className="text-xs text-gray-500">Sin contexto semántico relevante para esta ejecución.</div>
              ) : null}
            </div>

            <div className="mt-3 p-3 rounded-lg border border-gray-200 bg-gray-50">
              <div className="flex items-center justify-between gap-3 mb-2">
                <div className="text-xs font-semibold text-gray-700 uppercase tracking-tight">Comparativa de prompts</div>
                <div className="text-[11px] text-gray-500">mostrando: {filteredPromptComparisons.length} / {promptComparisonMetrics.total}</div>
              </div>

              <div className="mb-3 grid grid-cols-2 xl:grid-cols-4 gap-2 text-[11px]">
                <div className="rounded border border-gray-200 bg-white px-2 py-2 text-gray-700">total: {promptComparisonMetrics.total}</div>
                <div className="rounded border border-violet-200 bg-violet-50 px-2 py-2 text-violet-800">enriquecidos: {promptComparisonMetrics.enriched}</div>
                <div className="rounded border border-gray-200 bg-white px-2 py-2 text-gray-700">sin enriquecimiento: {promptComparisonMetrics.notEnriched}</div>
                <div className="rounded border border-amber-200 bg-amber-50 px-2 py-2 text-amber-800">retries: {promptComparisonMetrics.retries}</div>
                <div className="rounded border border-blue-200 bg-blue-50 px-2 py-2 text-blue-800">ratio: {(promptComparisonMetrics.enrichmentRatio * 100).toFixed(1)}%</div>
                <div className="rounded border border-gray-200 bg-white px-2 py-2 text-gray-700">shots únicos: {promptComparisonMetrics.uniqueShots}</div>
                <div className="rounded border border-amber-200 bg-amber-50 px-2 py-2 text-amber-800">shots con retry: {promptComparisonMetrics.shotsWithRetries}</div>
                <div className="rounded border border-violet-200 bg-violet-50 px-2 py-2 text-violet-800">shots con enriquecimiento: {promptComparisonMetrics.shotsWithEnrichment}</div>
              </div>

              {Object.keys(promptComparisonMetrics.sources).length > 0 ? (
                <div className="mb-3 flex flex-wrap gap-2 text-[11px]">
                  {Object.entries(promptComparisonMetrics.sources).map(([source, count]) => (
                    <span key={`prompt-metric-source-${source}`} className="rounded border border-gray-300 bg-white px-2 py-1 text-gray-700">
                      {source}: {count}
                    </span>
                  ))}
                </div>
              ) : null}

              <div className="mb-3 grid grid-cols-1 md:grid-cols-3 gap-2">
                <input
                  type="text"
                  value={promptComparisonShotFilter}
                  onChange={(event) => setPromptComparisonShotFilter(event.target.value)}
                  placeholder="Filtrar por shot_id"
                  className="w-full px-3 py-2 text-xs rounded-lg border border-gray-200 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                />
                <select
                  value={promptComparisonSourceFilter}
                  onChange={(event) => setPromptComparisonSourceFilter(event.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-gray-200 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                >
                  <option value="all">Todos los sources</option>
                  {promptComparisonSourceOptions.map((source) => (
                    <option key={`prompt-comparison-source-${source}`} value={source}>
                      {source}
                    </option>
                  ))}
                </select>
                <select
                  value={promptComparisonEnrichmentFilter}
                  onChange={(event) => setPromptComparisonEnrichmentFilter(event.target.value as "all" | "enriched" | "not_enriched")}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-gray-200 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                >
                  <option value="all">Todos</option>
                  <option value="enriched">Enriquecidos</option>
                  <option value="not_enriched">No enriquecidos</option>
                </select>
              </div>

              {filteredPromptComparisons.length > 0 ? (
                <div className="space-y-3">
                  {filteredPromptComparisons.map((job, index) => {
                    const promptAddition = extractPromptAddition(job.prompt_base, job.prompt_enriched);

                    return (
                      <div
                        key={`${execution.request_id}-prompt-compare-${job.shot_id}-${index}`}
                        className={`rounded-lg border px-3 py-3 ${
                          job.semantic_enrichment_applied
                            ? "border-violet-200 bg-violet-50/40"
                            : "border-gray-200 bg-white"
                        }`}
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <div className="font-semibold text-sm text-gray-800">{job.shot_id}</div>
                          <div className="flex flex-wrap gap-2 text-[11px]">
                            <span className="px-2 py-1 rounded border border-gray-300 bg-gray-50 text-gray-700">
                              job_id: {typeof job.job_id === "string" && job.job_id.trim() ? job.job_id : "-"}
                            </span>
                            <span className="px-2 py-1 rounded border border-gray-300 bg-gray-50 text-gray-700">
                              retry: {typeof job.retry_index === "number" ? job.retry_index : 0}
                            </span>
                            <span className="px-2 py-1 rounded border border-gray-300 bg-gray-50 text-gray-700">
                              source: {typeof job.source === "string" && job.source.trim() ? job.source : "live"}
                            </span>
                            <span
                              className={`px-2 py-1 rounded border ${
                                job.semantic_enrichment_applied
                                  ? "border-violet-300 bg-violet-100 text-violet-800"
                                  : "border-gray-300 bg-gray-50 text-gray-700"
                              }`}
                            >
                              enrichment: {job.semantic_enrichment_applied ? "aplicado" : "no aplicado"}
                            </span>
                          </div>
                        </div>

                        <div className="mt-3 grid grid-cols-1 xl:grid-cols-2 gap-3 text-xs text-gray-700">
                          <div className="rounded border border-gray-200 bg-white px-3 py-2">
                            <div className="font-semibold text-gray-600 mb-1">prompt_base</div>
                            <div className="whitespace-pre-wrap">{summarizeText(job.prompt_base, 260)}</div>
                          </div>

                          <div className="rounded border border-gray-200 bg-white px-3 py-2">
                            <div className="font-semibold text-gray-600 mb-1">prompt_enriched</div>
                            <div className="whitespace-pre-wrap">{summarizeText(job.prompt_enriched, 260)}</div>
                          </div>
                        </div>

                        <div className="mt-3 grid grid-cols-1 xl:grid-cols-2 gap-3 text-xs text-gray-700">
                          <div className="rounded border border-gray-200 bg-white px-3 py-2">
                            <div className="font-semibold text-gray-600 mb-1">semantic_summary_used</div>
                            <div className="whitespace-pre-wrap">{summarizeSemanticContextText(job.semantic_summary_used, 220)}</div>
                          </div>

                          <div className="rounded border border-gray-200 bg-white px-3 py-2">
                            <div className="font-semibold text-gray-600 mb-1">texto añadido</div>
                            <div className="whitespace-pre-wrap text-violet-800">
                              {promptAddition ? summarizeSemanticContextText(promptAddition, 220) : "-"}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-xs text-gray-500">Sin entradas que coincidan con los filtros actuales.</div>
              )}
            </div>

            <div className="mt-3 p-3 rounded-lg border border-gray-200 bg-gray-50">
              <div className="text-xs font-semibold text-gray-600 mb-2">Metadatos de revisión</div>

              <div className="flex flex-wrap items-center gap-2 mb-2">
                <span className="text-xs text-gray-600">favorito:</span>
                <span className="px-2 py-1 rounded-md border border-gray-300 bg-white text-xs text-gray-700">
                  {execution.is_favorite ? "si" : "no"}
                </span>
                <button
                  type="button"
                  disabled={metaSaving}
                  onClick={() => void toggleCurrentFavorite()}
                  className="px-3 py-1 text-xs font-semibold rounded-md border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
                >
                  {execution.is_favorite ? "Quitar favorito" : "Marcar favorito"}
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                <div>
                  <label className="text-[11px] font-semibold text-gray-600">Etiquetas (coma o nueva línea)</label>
                  <textarea
                    value={metaTagsInput}
                    onChange={(event) => setMetaTagsInput(event.target.value)}
                    rows={2}
                    placeholder="hero, retry, revision"
                    className="w-full mt-1 px-3 py-2 text-xs rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                  />
                  <div className="mt-1 flex flex-wrap gap-1">
                    {execution.tags.length > 0 ? (
                      execution.tags.map((tag) => (
                        <span key={`${execution.request_id}-exec-tag-${tag}`} className="px-2 py-1 text-[11px] rounded border border-gray-300 bg-white text-gray-700">
                          {tag}
                        </span>
                      ))
                    ) : (
                      <span className="text-[11px] text-gray-500">sin etiquetas</span>
                    )}
                  </div>
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-gray-600">Nota</label>
                  <textarea
                    value={metaNoteInput}
                    onChange={(event) => setMetaNoteInput(event.target.value)}
                    rows={3}
                    placeholder="Notas de revisión de esta ejecución"
                    className="w-full mt-1 px-3 py-2 text-xs rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="mt-2 flex flex-wrap gap-2">
                <button
                  type="button"
                  disabled={metaSaving}
                  onClick={() => void saveCurrentExecutionMeta()}
                  className="px-3 py-1 text-xs font-semibold rounded-md border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
                >
                  {metaSaving ? "Guardando metadatos..." : "Guardar metadatos"}
                </button>
              </div>
            </div>

            <div className="mt-3 p-3 rounded-lg border border-gray-200 bg-gray-50">
              <div className="flex items-center justify-between mb-3">
                <div className="text-xs font-bold text-gray-700 uppercase tracking-tight">Criterio Editorial</div>
                <div 
                  className="px-2 py-1 rounded text-[10px] font-bold uppercase border"
                  style={getReviewStatusStyle(execution.review_status)}
                >
                  {formatReviewStatusLabel(execution.review_status)}
                </div>
              </div>

              <div className="grid grid-cols-1 gap-3">
                <div className="flex flex-wrap gap-2">
                  {REVIEW_STATUS_OPTIONS.map((status) => {
                    const isSelected = reviewStatusInput === status;
                    const style = getReviewStatusStyle(status);
                    return (
                      <button
                        key={`review-choice-${status}`}
                        type="button"
                        onClick={() => setReviewStatusInput(status)}
                        className={`px-3 py-2 rounded-lg text-xs font-bold border transition-all ${
                          isSelected ? "shadow-sm scale-[1.02]" : "opacity-60 grayscale-[0.5] hover:opacity-100 hover:grayscale-0"
                        }`}
                        style={isSelected ? style : { background: "white", color: "#6b7280", borderColor: "#e5e7eb" }}
                      >
                        {status === "pending_review" ? "⏸️ Marcar Pendiente" : status === "approved" ? "✅ Aprobar Plan" : "❌ Rechazar Plan"}
                      </button>
                    );
                  })}
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-gray-600 ml-1">Nota de revisión / Feedback creativo</label>
                  <textarea
                    value={reviewNoteInput}
                    onChange={(event) => setReviewNoteInput(event.target.value)}
                    rows={2}
                    placeholder="Escribe una nota editorial o motivo de rechazo..."
                    className="w-full mt-1 px-3 py-2 text-xs rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 bg-white"
                  />
                </div>
                
                <button
                  type="button"
                  disabled={reviewSaving}
                  onClick={() => void saveCurrentExecutionReview()}
                  className="w-full py-2.5 text-xs font-bold rounded-lg bg-gray-900 text-white hover:bg-black disabled:opacity-50 transition-colors shadow-sm"
                >
                  {reviewSaving ? "Guardando revisión..." : "Registrar Decisión Creativa"}
                </button>
                
                {execution.reviewed_at && (
                  <div className="text-[10px] text-gray-400 text-right italic">
                     Audit: {formatTimestamp(execution.reviewed_at)}
                  </div>
                )}
              </div>
            </div>

            <div className="mt-3 p-3 rounded-lg border border-gray-200 bg-gray-50">
              <div className="flex items-center justify-between mb-2">
                <div className="text-xs font-semibold text-gray-700">Historial editorial</div>
                <span className="px-2 py-1 rounded border border-gray-300 bg-white text-[11px] text-gray-700">
                  total: {execution.review_history_summary?.history_count ?? 0}
                </span>
              </div>

              <div className="text-[11px] text-gray-500 mb-2">
                ultimo cambio: {formatTimestamp(execution.review_history_summary?.latest_created_at ?? undefined)}
              </div>

              {reviewHistoryError ? (
                <div className="mb-2 px-2 py-2 rounded border border-red-200 bg-red-50 text-[11px] text-red-700">
                  {reviewHistoryError}
                </div>
              ) : null}

              {reviewHistoryLoading ? (
                <div className="text-xs text-gray-500">Cargando historial editorial...</div>
              ) : reviewHistory.length > 0 ? (
                <div className="space-y-2">
                  {reviewHistory.map((item) => (
                    <div
                      key={`${execution.request_id}-review-history-${item.history_id}`}
                      className="p-2 rounded border border-gray-200 bg-white"
                    >
                      <div className="flex flex-wrap items-center gap-2 text-[11px]">
                        <span className="px-2 py-1 rounded border" style={getReviewStatusStyle(item.previous_review_status)}>
                          {formatReviewStatusLabel(item.previous_review_status)}
                        </span>
                        <span className="text-gray-500">-&gt;</span>
                        <span className="px-2 py-1 rounded border" style={getReviewStatusStyle(item.new_review_status)}>
                          {formatReviewStatusLabel(item.new_review_status)}
                        </span>
                        <span className="ml-auto text-gray-500">{formatTimestamp(item.created_at)}</span>
                      </div>
                      <div className="mt-1 text-xs text-gray-700">
                        nota: {item.review_note ? item.review_note : "-"}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-xs text-gray-500">Sin decisiones editoriales registradas.</div>
              )}
            </div>

            <div className="mt-3 p-3 rounded-lg border border-gray-200 bg-gray-50">
              <div className="text-xs font-semibold text-gray-600 mb-2">Colecciones asociadas</div>
              {execution.collections.length > 0 ? (
                <div className="space-y-2">
                  {execution.collections.map((item) => (
                    <div key={`${execution.request_id}-membership-${item.collection_id}`} className="p-2 rounded border border-gray-200 bg-white text-xs text-gray-700">
                      <div className="font-semibold text-gray-800">{item.name}</div>
                      <div className="mt-1 flex flex-wrap gap-2 text-[11px]">
                        <span className="px-2 py-1 rounded border border-gray-300 bg-gray-50 text-gray-700">id: {item.collection_id}</span>
                        <span className="px-2 py-1 rounded border border-gray-300 bg-gray-50 text-gray-700">candidata: {item.is_highlighted ? "si" : "no"}</span>
                        <span className="px-2 py-1 rounded border border-gray-300 bg-gray-50 text-gray-700">best: {item.is_best ? "si" : "no"}</span>
                        <span className="px-2 py-1 rounded border border-gray-300 bg-gray-50 text-gray-700">agregada: {formatTimestamp(item.added_at)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-xs text-gray-500">Esta ejecucion no pertenece a ninguna coleccion.</div>
              )}
            </div>

            <div className="mt-3 flex flex-wrap gap-2">
              <button
                type="button"
                disabled={!selectedCollectionId || collectionItemActionRequestId === execution.request_id}
                onClick={() => void addExecutionToSelectedCollection(execution.request_id)}
                className="px-3 py-1 text-xs font-semibold rounded-md border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
              >
                Añadir a colección seleccionada
              </button>
              <button
                type="button"
                disabled={exportingJson}
                onClick={handleExportJson}
                className="px-3 py-1 text-xs font-semibold rounded-md border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
              >
                {exportingJson ? "Exportando JSON..." : "Exportar ejecución JSON"}
              </button>
              <button
                type="button"
                disabled={exportingPdf}
                onClick={handleExportPdf}
                className="px-3 py-1 text-xs font-semibold rounded-md border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
              >
                {exportingPdf ? "Exportando PDF..." : "Exportar ejecución PDF"}
              </button>
              <button
                type="button"
                disabled={exportingPromptCompareJson}
                onClick={() => void handleExportPromptComparisonJson()}
                className="px-3 py-1 text-xs font-semibold rounded-md border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
              >
                {exportingPromptCompareJson ? "Exportando comparativa JSON..." : "Exportar comparativa JSON"}
              </button>
              <button
                type="button"
                disabled={exportingPromptCompareCsv}
                onClick={() => void handleExportPromptComparisonCsv()}
                className="px-3 py-1 text-xs font-semibold rounded-md border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
              >
                {exportingPromptCompareCsv ? "Exportando comparativa CSV..." : "Exportar comparativa CSV"}
              </button>
            </div>

            {executionMetrics ? (
              <div className="mt-4 p-3 rounded-lg border border-gray-200 bg-gray-50">
                <div className="text-xs font-semibold text-gray-600 mb-3">Métricas operativas</div>

                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-2 text-xs">
                  <div className="px-2 py-2 rounded border border-gray-200 bg-white">
                    <div className="text-gray-500">request_id</div>
                    <div className="font-mono text-gray-800 break-all">{executionMetrics.requestId}</div>
                  </div>
                  <div className="px-2 py-2 rounded border border-gray-200 bg-white">
                    <div className="text-gray-500">shots_count</div>
                    <div className="font-semibold text-gray-800">{executionMetrics.shotsCount}</div>
                  </div>
                  <div className="px-2 py-2 rounded border border-gray-200 bg-white">
                    <div className="text-gray-500">job_count</div>
                    <div className="font-semibold text-gray-800">{executionMetrics.jobCount}</div>
                  </div>
                  <div className="px-2 py-2 rounded border border-gray-200 bg-white">
                    <div className="text-gray-500">total_retries</div>
                    <div className="font-semibold text-gray-800">{executionMetrics.totalRetries}</div>
                  </div>
                  <div className="px-2 py-2 rounded border border-gray-200 bg-white">
                    <div className="text-gray-500">success_count</div>
                    <div className="font-semibold text-green-700">{executionMetrics.successCount}</div>
                  </div>
                  <div className="px-2 py-2 rounded border border-gray-200 bg-white">
                    <div className="text-gray-500">failed_count</div>
                    <div className="font-semibold text-red-700">{executionMetrics.failedCount}</div>
                  </div>
                  <div className="px-2 py-2 rounded border border-gray-200 bg-white">
                    <div className="text-gray-500">timeout_count</div>
                    <div className="font-semibold text-purple-700">{executionMetrics.timeoutCount}</div>
                  </div>
                  <div className="px-2 py-2 rounded border border-gray-200 bg-white">
                    <div className="text-gray-500">queued_count</div>
                    <div className="font-semibold text-blue-700">{executionMetrics.queuedCount}</div>
                  </div>
                  <div className="px-2 py-2 rounded border border-gray-200 bg-white">
                    <div className="text-gray-500">running_count</div>
                    <div className="font-semibold text-amber-700">{executionMetrics.runningCount}</div>
                  </div>
                  <div className="px-2 py-2 rounded border border-gray-200 bg-white">
                    <div className="text-gray-500">success_ratio</div>
                    <div className="font-semibold text-gray-800">{executionMetrics.successRatio.toFixed(1)}%</div>
                  </div>
                  <div className="px-2 py-2 rounded border border-gray-200 bg-white md:col-span-2 xl:col-span-2">
                    <div className="text-gray-500">shot con más retries</div>
                    <div className="font-semibold text-gray-800">
                      {executionMetrics.shotWithMostRetries
                        ? `${executionMetrics.shotWithMostRetries.shotId} (${executionMetrics.shotWithMostRetries.retries})`
                        : "-"}
                    </div>
                  </div>
                </div>

                <div className="mt-4">
                  <div className="text-xs font-semibold text-gray-600 mb-2">Distribución por estado</div>
                  <div className="space-y-2">
                    {executionMetrics.statusDistribution.map((item) => (
                      <div key={item.status}>
                        <div className="flex justify-between text-[11px] text-gray-600 mb-1">
                          <span>{item.status}</span>
                          <span>{item.count} ({item.percent.toFixed(1)}%)</span>
                        </div>
                        <div className="h-2 rounded bg-gray-200 overflow-hidden">
                          <div
                            className="h-full"
                            style={{
                              width: `${Math.max(0, Math.min(100, item.percent))}%`,
                              ...getStatusStyle(item.status),
                            }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : null}

            <div className="mt-3 flex flex-wrap gap-2 text-xs">
              <span className="px-2 py-1 rounded-md bg-gray-100 text-gray-700 border border-gray-200">
                jobs: {execution.status_summary.total_jobs}
              </span>
              <span className="px-2 py-1 rounded-md bg-gray-100 text-gray-700 border border-gray-200">
                terminal: {execution.status_summary.terminal_jobs}
              </span>
              <span className="px-2 py-1 rounded-md bg-gray-100 text-gray-700 border border-gray-200">
                shots visibles: {filteredShotRows.length}/{shotRows.length}
              </span>
              {Object.entries(execution.status_summary.by_status).map(([status, count]) => (
                <span
                  key={status}
                  className="px-2 py-1 rounded-md border"
                  style={getStatusStyle(status)}
                >
                  {status}: {count}
                </span>
              ))}
            </div>

            <div className="mt-4">
              <div className="text-xs font-semibold text-gray-600 mb-2">Filtro por estado</div>
              <div className="flex flex-wrap gap-2">
                {STATUS_FILTER_OPTIONS.map((option) => {
                  const isActive = statusFilter === option;
                  const count = option === "all"
                    ? shotRows.length
                    : shotRows.filter((row) => {
                        const latestStatus = formatStatus(row.latestJob?.status ? String(row.latestJob.status) : "unknown");
                        if (latestStatus === option) {
                          return true;
                        }

                        return row.retries.some(({ job }) => {
                          const retryStatus = formatStatus(job?.status ? String(job.status) : "unknown");
                          return retryStatus === option;
                        });
                      }).length;

                  return (
                    <button
                      key={option}
                      type="button"
                      onClick={() => setStatusFilter(option)}
                      className="px-3 py-1 text-xs font-semibold rounded-md border"
                      style={isActive ? getStatusStyle(option === "all" ? "succeeded" : option) : undefined}
                    >
                      {option} ({count})
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {filteredShotRows.map((row) => {
            const latestJobId = row.latestLink?.job_id ?? "-";
            const latestStatus = formatStatus(row.latestJob?.status ? String(row.latestJob.status) : "unknown");
            const retryCount = row.retries.length;
            const isRetryOpen = activeRetryShotId === row.shot.shot_id;
            const retriesForView = statusFilter === "all"
              ? row.retries
              : row.retries.filter(({ job }) => {
                  const retryStatus = formatStatus(job?.status ? String(job.status) : "unknown");
                  return matchesStatusFilter(retryStatus, statusFilter);
                });

            return (
              <article key={row.shot.shot_id} className="p-4 rounded-xl border border-gray-200 bg-white">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3">
                  <div>
                    <div className="text-xs text-gray-500">{row.shot.shot_id}</div>
                    <div className="text-sm font-semibold text-gray-900">{row.shot.shot_type}</div>
                    <div className="mt-2 text-sm text-gray-700 whitespace-pre-wrap">{row.shot.prompt}</div>
                  </div>

                  <div className="text-xs text-gray-600 min-w-[240px]">
                    <div className="mb-1">
                      <strong>Último job_id:</strong> <span className="font-mono">{latestJobId}</span>
                    </div>
                    <div className="mb-2 flex items-center gap-2">
                      <strong>Status:</strong>
                      <span className="px-2 py-1 rounded-md border" style={getStatusStyle(latestStatus)}>
                        {latestStatus}
                      </span>
                    </div>
                    <div className="mb-2">
                      <strong>updated_at:</strong> {formatTimestamp(row.latestJob?.updated_at)}
                    </div>
                    {row.latestJob?.error ? (
                      <div className="mb-2 p-2 rounded-md border border-red-200 bg-red-50 text-red-700">
                        <div>
                          <strong>error.code:</strong> {row.latestJob.error.code}
                        </div>
                        <div>
                          <strong>error.message:</strong> {row.latestJob.error.message}
                        </div>
                      </div>
                    ) : null}
                    <JobPreview
                      job={row.latestJob}
                      label={`${row.shot.shot_id}-latest`}
                      onOpenPreview={(url, label) => setPreviewModal({ url, label })}
                    />
                    <button
                      type="button"
                      disabled={!row.latestJob}
                      onClick={() => openJobDetail(row.shot.shot_id, row.latestLink, row.latestJob, "latest")}
                      className="mt-2 px-2 py-1 text-[11px] font-semibold rounded border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
                    >
                      Ver detalle
                    </button>
                    <div>
                      <strong>Retries asociados:</strong> {retryCount}
                    </div>
                  </div>
                </div>

                {retriesForView.length > 0 ? (
                  <div className="mt-3 p-3 rounded-lg border border-gray-200 bg-gray-50">
                    <div className="text-xs font-semibold text-gray-600 mb-2">Historial de retries</div>
                    <div className="space-y-2">
                      {retriesForView.map(({ link, job }) => {
                        const retryStatus = formatStatus(job?.status ? String(job.status) : "unknown");
                        return (
                          <div key={link.job_id} className="text-xs text-gray-700 border border-gray-200 rounded-md p-2 bg-white">
                            <div className="flex flex-wrap items-center gap-2">
                              <span className="font-mono">{link.job_id}</span>
                              <span className="px-2 py-1 rounded-md border" style={getStatusStyle(retryStatus)}>
                                {retryStatus}
                              </span>
                              <span>retry_index={getLinkRetryIndex(link)}</span>
                              {link.reason ? <span>reason={link.reason}</span> : null}
                            </div>
                            <div className="mt-1">
                              <strong>updated_at:</strong> {formatTimestamp(job?.updated_at)}
                            </div>
                            {job?.error ? (
                              <div className="mt-1 p-2 rounded-md border border-red-200 bg-red-50 text-red-700">
                                <div>
                                  <strong>error.code:</strong> {job.error.code}
                                </div>
                                <div>
                                  <strong>error.message:</strong> {job.error.message}
                                </div>
                              </div>
                            ) : null}
                            <JobPreview
                              job={job}
                              label={`${row.shot.shot_id}-retry-${link.job_id}`}
                              onOpenPreview={(url, label) => setPreviewModal({ url, label })}
                            />
                            <button
                              type="button"
                              disabled={!job}
                              onClick={() => openJobDetail(row.shot.shot_id, link, job, "retry")}
                              className="mt-2 px-2 py-1 text-[11px] font-semibold rounded border border-gray-300 bg-white text-gray-700 disabled:opacity-50"
                            >
                              Ver detalle
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ) : null}

                <div className="mt-4 flex gap-2">
                  <button
                    type="button"
                    disabled={retrySubmitting}
                    onClick={() => openRetryEditor(row.shot)}
                    className="px-3 py-2 text-sm font-semibold rounded-lg bg-white text-gray-700 border border-gray-300 disabled:opacity-50"
                  >
                    Retry shot
                  </button>
                </div>

                {isRetryOpen ? (
                  <div className="mt-4 p-4 rounded-lg border border-blue-200 bg-blue-50/40">
                    <div className="text-sm font-semibold text-gray-800 mb-3">Retry shot: {row.shot.shot_id}</div>
                    <div className="space-y-3">
                      <div>
                        <label className="text-xs font-semibold text-gray-600">override_prompt</label>
                        <textarea
                          value={retryPrompt}
                          onChange={(event) => setRetryPrompt(event.target.value)}
                          rows={3}
                          placeholder="Opcional"
                          className="w-full mt-1 px-3 py-2 text-sm rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="text-xs font-semibold text-gray-600">override_negative_prompt</label>
                        <textarea
                          value={retryNegativePrompt}
                          onChange={(event) => setRetryNegativePrompt(event.target.value)}
                          rows={2}
                          placeholder="Opcional"
                          className="w-full mt-1 px-3 py-2 text-sm rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="text-xs font-semibold text-gray-600">reason</label>
                        <input
                          type="text"
                          value={retryReason}
                          onChange={(event) => setRetryReason(event.target.value)}
                          placeholder="Opcional"
                          className="w-full mt-1 px-3 py-2 text-sm rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                        />
                      </div>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          disabled={retrySubmitting}
                          onClick={() => submitRetry(row.shot.shot_id)}
                          className="px-3 py-2 text-sm font-semibold rounded-lg bg-blue-600 text-white border border-blue-600 disabled:opacity-50"
                        >
                          {retrySubmitting ? "Creando retry..." : "Crear retry"}
                        </button>
                        <button
                          type="button"
                          disabled={retrySubmitting}
                          onClick={closeRetryEditor}
                          className="px-3 py-2 text-sm font-semibold rounded-lg bg-white text-gray-700 border border-gray-300 disabled:opacity-50"
                        >
                          Cancelar
                        </button>
                      </div>
                    </div>
                  </div>
                ) : null}
              </article>
            );
          })}

          {filteredShotRows.length === 0 ? (
            <div className="p-4 rounded-xl border border-dashed border-gray-300 bg-gray-50 text-sm text-gray-600">
              No hay shots que coincidan con el filtro <strong>{statusFilter}</strong>.
            </div>
          ) : null}
        </div>
      ) : null}

      {jobDetailModal && jobDetailData ? (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-5xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
              <div>
                <div className="text-sm font-semibold text-gray-800">Detalle de job</div>
                <div className="text-xs text-gray-500">shot_id: {jobDetailModal.shotId}</div>
              </div>
              <button
                type="button"
                onClick={() => setJobDetailModal(null)}
                className="px-3 py-1 text-sm font-semibold rounded-lg bg-white text-gray-700 border border-gray-300"
              >
                Cerrar
              </button>
            </div>

            <div className="p-4 bg-gray-50 overflow-auto max-h-[calc(90vh-64px)] space-y-4">
              <section className="p-3 rounded-lg border border-gray-200 bg-white">
                <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Identidad</div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-700">
                  <div>
                    <strong>job_id:</strong> <span className="font-mono break-all">{jobDetailModal.job.job_id}</span>
                  </div>
                  <div>
                    <strong>source:</strong> {jobDetailModal.source === "retry" ? "retry" : "principal"}
                  </div>
                  <div>
                    <strong>request_id:</strong> <span className="font-mono break-all">{execution?.request_id ?? "-"}</span>
                  </div>
                  <div>
                    <strong>shot_id:</strong> {jobDetailModal.shotId}
                  </div>
                  {(jobDetailModal.job.parent_job_id || jobDetailModal.link?.parent_job_id) ? (
                    <div className="md:col-span-2">
                      <strong>parent_job_id:</strong>{" "}
                      <span className="font-mono break-all">
                        {jobDetailModal.job.parent_job_id || jobDetailModal.link?.parent_job_id}
                      </span>
                    </div>
                  ) : null}
                  {jobDetailData.retryIndex !== null ? (
                    <div>
                      <strong>retry_index:</strong> {jobDetailData.retryIndex}
                    </div>
                  ) : null}
                </div>
                <button
                  type="button"
                  onClick={() => copyJobId(jobDetailModal.job.job_id)}
                  className="mt-3 px-3 py-1 text-xs font-semibold rounded border border-gray-300 bg-white text-gray-700"
                >
                  Copiar job_id
                </button>
              </section>

              <section className="p-3 rounded-lg border border-gray-200 bg-white">
                <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Estado</div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-700">
                  <div className="flex items-center gap-2">
                    <strong>status:</strong>
                    <span className="px-2 py-1 rounded-md border text-xs" style={getStatusStyle(jobDetailData.status)}>
                      {jobDetailData.status}
                    </span>
                  </div>
                  <div>
                    <strong>duration_ms:</strong> {typeof jobDetailModal.job.duration_ms === "number" ? jobDetailModal.job.duration_ms : "-"}
                  </div>
                  <div>
                    <strong>created_at:</strong> {formatTimestamp(jobDetailModal.job.created_at)}
                  </div>
                  <div>
                    <strong>updated_at:</strong> {formatTimestamp(jobDetailModal.job.updated_at)}
                  </div>
                </div>
              </section>

              <section className="p-3 rounded-lg border border-gray-200 bg-white">
                <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Prompt y contexto</div>
                <div className="space-y-2 text-sm text-gray-700">
                  <div>
                    <strong>prompt (resumen):</strong>
                    <div className="mt-1 whitespace-pre-wrap">{summarizeText(jobDetailData.promptSummary.positive)}</div>
                  </div>
                  <div>
                    <strong>negative_prompt (resumen):</strong>
                    <div className="mt-1 whitespace-pre-wrap">{summarizeText(jobDetailData.promptSummary.negative)}</div>
                  </div>
                  <div>
                    <strong>request_payload.metadata.render_context:</strong>
                    {jobDetailData.renderContext ? (
                      <pre className="mt-1 p-2 text-xs rounded bg-gray-50 border border-gray-200 overflow-auto">{prettyJson(jobDetailData.renderContext)}</pre>
                    ) : (
                      <div className="mt-1 text-gray-500">-</div>
                    )}
                  </div>
                  <div>
                    <strong>referencias visuales detectadas:</strong>
                    {jobDetailData.visualReferences.length > 0 ? (
                      <ul className="mt-1 list-disc pl-5 space-y-1 text-xs">
                        {jobDetailData.visualReferences.map((reference) => (
                          <li key={reference} className="font-mono break-all">{reference}</li>
                        ))}
                      </ul>
                    ) : (
                      <div className="mt-1 text-gray-500">sin referencias visuales</div>
                    )}
                  </div>
                </div>
              </section>

              <section className="p-3 rounded-lg border border-gray-200 bg-white">
                <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Error</div>
                {jobDetailModal.job.error ? (
                  <div className="text-sm text-red-700 space-y-1">
                    <div><strong>error.code:</strong> {jobDetailModal.job.error.code}</div>
                    <div><strong>error.message:</strong> {jobDetailModal.job.error.message}</div>
                    {jobDetailModal.job.error.details ? (
                      <pre className="mt-1 p-2 text-xs rounded bg-red-50 border border-red-200 overflow-auto text-red-700">
                        {prettyJson(jobDetailModal.job.error.details)}
                      </pre>
                    ) : null}
                  </div>
                ) : (
                  <div className="text-sm text-gray-500">sin error</div>
                )}
              </section>

              <section className="p-3 rounded-lg border border-gray-200 bg-white">
                <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Resultado</div>
                {jobDetailData.resultSummary.length > 0 ? (
                  <div className="space-y-1 text-sm text-gray-700">
                    {jobDetailData.resultSummary.map((item) => (
                      <div key={item.label}>
                        <strong>{item.label}:</strong> {item.value}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-sm text-gray-500">sin resultado</div>
                )}
                {jobDetailModal.job.result ? (
                  <pre className="mt-2 p-2 text-xs rounded bg-gray-50 border border-gray-200 overflow-auto">
                    {prettyJson(jobDetailModal.job.result)}
                  </pre>
                ) : null}
              </section>
            </div>
          </div>
        </div>
      ) : null}

      {previewModal ? (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-4xl w-full overflow-hidden">
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
              <div className="text-sm font-semibold text-gray-800">Preview: {previewModal.label}</div>
              <button
                type="button"
                onClick={() => setPreviewModal(null)}
                className="px-3 py-1 text-sm font-semibold rounded-lg bg-white text-gray-700 border border-gray-300"
              >
                Cerrar
              </button>
            </div>
            <div className="p-4 bg-gray-50 flex items-center justify-center min-h-[320px]">
              <img
                src={previewModal.url}
                alt={`preview-${previewModal.label}`}
                className="max-h-[70vh] w-auto object-contain rounded-md border border-gray-200 bg-white"
              />
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}
