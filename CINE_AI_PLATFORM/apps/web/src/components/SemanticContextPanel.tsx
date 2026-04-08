import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";

import { ingestSemanticContext, searchSemanticContext } from "../services/semanticContextApi";
import type { Scene } from "../types/scene";
import type { Shot } from "../types/shot";
import type {
  SemanticContextIngestResponse,
  SemanticContextSearchResponse,
  SemanticContextSearchResult,
} from "../types/semanticContext";


type SemanticContextPanelProps = {
  defaultProjectId?: string;
  scenes: Scene[];
  selectedShot: Shot | null;
  isReadOnly: boolean;
};

type SearchFormState = {
  text: string;
  project_id: string;
  sequence_id: string;
  scene_id: string;
  shot_id: string;
  entity_type: string;
  source: string;
  limit: string;
  tags: string;
};

type IngestFormState = {
  text: string;
  project_id: string;
  sequence_id: string;
  scene_id: string;
  shot_id: string;
  entity_type: string;
  title: string;
  content: string;
  tags: string;
  source: string;
  created_at: string;
  point_id: string;
};

type SemanticContextPanelPreferences = {
  autoSearchEnabled: boolean;
  searchLimit: string;
  searchEntityType: string;
  searchSource: string;
};

const SEMANTIC_CONTEXT_PREFERENCES_KEY = "cine_ai_platform_semantic_context_preferences";


function readSemanticContextPanelPreferences(): SemanticContextPanelPreferences {
  const fallback: SemanticContextPanelPreferences = {
    autoSearchEnabled: true,
    searchLimit: "5",
    searchEntityType: "",
    searchSource: "",
  };

  try {
    if (typeof window === "undefined" || !window.localStorage) {
      return fallback;
    }

    const rawValue = window.localStorage.getItem(SEMANTIC_CONTEXT_PREFERENCES_KEY);
    if (!rawValue) {
      return fallback;
    }

    const parsed = JSON.parse(rawValue) as Partial<SemanticContextPanelPreferences>;
    const parsedLimit = String(parsed.searchLimit ?? fallback.searchLimit).trim();
    const normalizedLimitNumber = Number(parsedLimit);

    return {
      autoSearchEnabled: typeof parsed.autoSearchEnabled === "boolean" ? parsed.autoSearchEnabled : fallback.autoSearchEnabled,
      searchLimit: Number.isFinite(normalizedLimitNumber) && normalizedLimitNumber >= 1 && normalizedLimitNumber <= 20
        ? String(Math.trunc(normalizedLimitNumber))
        : fallback.searchLimit,
      searchEntityType: typeof parsed.searchEntityType === "string" ? parsed.searchEntityType : fallback.searchEntityType,
      searchSource: typeof parsed.searchSource === "string" ? parsed.searchSource : fallback.searchSource,
    };
  } catch {
    return fallback;
  }
}


function writeSemanticContextPanelPreferences(preferences: SemanticContextPanelPreferences): void {
  try {
    if (typeof window === "undefined" || !window.localStorage) {
      return;
    }

    window.localStorage.setItem(SEMANTIC_CONTEXT_PREFERENCES_KEY, JSON.stringify(preferences));
  } catch {
    // Ignore localStorage failures to keep the panel usable.
  }
}


function parseTags(value: string): string[] {
  return Array.from(
    new Set(
      value
        .split(",")
        .map((item) => item.trim())
        .filter((item) => item.length > 0)
    )
  );
}


function normalizeOptional(value: string): string | undefined {
  const normalized = value.trim();
  return normalized === "" ? undefined : normalized;
}


function getBackendErrorMessage(error: unknown, fallback: string): string {
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
    if (typeof detail === "string" && detail.trim() !== "") {
      return detail.trim();
    }

    if (typeof maybeResponse.message === "string" && maybeResponse.message.trim() !== "") {
      return maybeResponse.message.trim();
    }
  }

  return fallback;
}


export default function SemanticContextPanel({
  defaultProjectId,
  scenes,
  selectedShot,
  isReadOnly,
}: SemanticContextPanelProps) {
  const storedPreferences = readSemanticContextPanelPreferences();
  const selectedScene = useMemo(
    () => scenes.find((scene) => scene.id === selectedShot?.scene_id) ?? null,
    [scenes, selectedShot]
  );

  const [searchForm, setSearchForm] = useState<SearchFormState>({
    text: "",
    project_id: defaultProjectId ?? "",
    sequence_id: "",
    scene_id: selectedShot?.scene_id ?? "",
    shot_id: selectedShot?.id ?? "",
    entity_type: storedPreferences.searchEntityType,
    source: storedPreferences.searchSource,
    limit: storedPreferences.searchLimit,
    tags: "",
  });
  const [ingestForm, setIngestForm] = useState<IngestFormState>({
    text: selectedShot?.prompt ?? "",
    project_id: defaultProjectId ?? "",
    sequence_id: "",
    scene_id: selectedShot?.scene_id ?? "",
    shot_id: selectedShot?.id ?? "",
    entity_type: "shot_note",
    title: selectedShot ? `Contexto ${selectedShot.id}` : "",
    content: selectedShot?.prompt ?? "",
    tags: "",
    source: "editorial_note",
    created_at: "",
    point_id: "",
  });
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState("");
  const [searchResponse, setSearchResponse] = useState<SemanticContextSearchResponse | null>(null);
  const [ingestLoading, setIngestLoading] = useState(false);
  const [ingestError, setIngestError] = useState("");
  const [ingestResponse, setIngestResponse] = useState<SemanticContextIngestResponse | null>(null);
  const [autoSearchEnabled, setAutoSearchEnabled] = useState(storedPreferences.autoSearchEnabled);
  const lastAutoSearchKeyRef = useRef<string>("");
  const lastIngestAutofillRef = useRef<Partial<IngestFormState> | null>(null);

  useEffect(() => {
    writeSemanticContextPanelPreferences({
      autoSearchEnabled,
      searchLimit: searchForm.limit,
      searchEntityType: searchForm.entity_type,
      searchSource: searchForm.source,
    });
  }, [autoSearchEnabled, searchForm.entity_type, searchForm.limit, searchForm.source]);

  useEffect(() => {
    if (defaultProjectId) {
      setSearchForm((current) => (current.project_id.trim() ? current : { ...current, project_id: defaultProjectId }));
      setIngestForm((current) => (current.project_id.trim() ? current : { ...current, project_id: defaultProjectId }));
    }
  }, [defaultProjectId]);

  useEffect(() => {
    if (!selectedShot) {
      return;
    }

    const nextIngestAutofill: Partial<IngestFormState> = {
      project_id: selectedScene?.project_id || defaultProjectId || "",
      scene_id: selectedShot.scene_id,
      shot_id: selectedShot.id,
      entity_type: "shot_note",
      title: selectedScene?.title?.trim() ? `${selectedScene.title.trim()} · ${selectedShot.id}` : `Contexto ${selectedShot.id}`,
      content: selectedShot.prompt,
      text: selectedShot.prompt,
    };

    setSearchForm((current) => ({
      ...current,
      project_id: current.project_id.trim() || selectedScene?.project_id || defaultProjectId || "",
      scene_id: selectedShot.scene_id,
      shot_id: selectedShot.id,
    }));

    setIngestForm((current) => {
      const previousAutofill = lastIngestAutofillRef.current;

      const resolveAutofillValue = (field: keyof IngestFormState): string => {
        const currentValue = current[field].trim();
        const nextValue = (nextIngestAutofill[field] ?? "").trim();
        const previousValue = (previousAutofill?.[field] ?? "").trim();

        if (currentValue === "" || currentValue === previousValue) {
          return nextValue;
        }

        return current[field];
      };

      const nextFormState: IngestFormState = {
        ...current,
        project_id: resolveAutofillValue("project_id"),
        scene_id: resolveAutofillValue("scene_id"),
        shot_id: resolveAutofillValue("shot_id"),
        entity_type: resolveAutofillValue("entity_type"),
        title: resolveAutofillValue("title"),
        content: resolveAutofillValue("content"),
        text: resolveAutofillValue("text"),
      };

      lastIngestAutofillRef.current = nextIngestAutofill;
      return nextFormState;
    });
  }, [defaultProjectId, selectedScene?.project_id, selectedScene?.title, selectedShot]);

  const canSearch = searchForm.text.trim() !== "" && searchForm.project_id.trim() !== "";
  const canIngest =
    ingestForm.project_id.trim() !== "" &&
    ingestForm.entity_type.trim() !== "" &&
    ingestForm.title.trim() !== "" &&
    ingestForm.content.trim() !== "" &&
    ingestForm.source.trim() !== "";

  function buildShotSearchFormState(): SearchFormState | null {
    if (!selectedShot) {
      return null;
    }

    const baseText = selectedShot.prompt.trim();
    const sceneContext = selectedScene?.title?.trim() ?? "";
    const queryText = [sceneContext, baseText].filter((value) => value !== "").join(" · ");

    return {
      ...searchForm,
      text: queryText || baseText,
      project_id: searchForm.project_id.trim() || selectedScene?.project_id || defaultProjectId || "",
      scene_id: selectedShot.scene_id,
      shot_id: selectedShot.id,
      entity_type: searchForm.entity_type.trim() || "shot_note",
    };
  }

  async function submitSearch(formState: SearchFormState) {
    setSearchLoading(true);
    setSearchError("");
    setSearchResponse(null);

    try {
      const response = await searchSemanticContext({
        text: formState.text.trim(),
        project_id: formState.project_id.trim(),
        sequence_id: normalizeOptional(formState.sequence_id),
        scene_id: normalizeOptional(formState.scene_id),
        shot_id: normalizeOptional(formState.shot_id),
        entity_type: normalizeOptional(formState.entity_type),
        source: normalizeOptional(formState.source),
        tags: parseTags(formState.tags),
        limit: Number(formState.limit) || 5,
      });
      setSearchResponse(response);
    } catch (error) {
      setSearchError(getBackendErrorMessage(error, "No se pudo ejecutar la búsqueda semántica."));
      setSearchResponse(null);
    } finally {
      setSearchLoading(false);
    }
  }

  async function handleSearchSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSearch) {
      setSearchError("Texto y project_id son obligatorios para buscar.");
      return;
    }

    await submitSearch(searchForm);
  }

  async function handleQuickShotSearch() {
    const nextForm = buildShotSearchFormState();
    if (!nextForm || !nextForm.text.trim() || !nextForm.project_id.trim()) {
      setSearchError("Selecciona un shot con prompt válido para lanzar una búsqueda rápida.");
      return;
    }

    setSearchForm(nextForm);
    await submitSearch(nextForm);
  }

  useEffect(() => {
    if (!autoSearchEnabled) {
      lastAutoSearchKeyRef.current = "";
      return;
    }

    const nextForm = buildShotSearchFormState();
    if (!nextForm || !nextForm.text.trim() || !nextForm.project_id.trim()) {
      return;
    }

    const nextKey = [
      selectedShot?.id ?? "",
      nextForm.project_id.trim(),
      nextForm.scene_id.trim(),
      nextForm.shot_id.trim(),
      nextForm.text.trim(),
    ].join("|");

    if (lastAutoSearchKeyRef.current === nextKey) {
      return;
    }

    lastAutoSearchKeyRef.current = nextKey;
    setSearchForm(nextForm);
    void submitSearch(nextForm);
  }, [autoSearchEnabled, defaultProjectId, selectedScene?.project_id, selectedScene?.title, selectedShot]);

  async function handleIngestSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canIngest) {
      setIngestError("project_id, entity_type, title, content y source son obligatorios.");
      return;
    }

    setIngestLoading(true);
    setIngestError("");
    setIngestResponse(null);

    try {
      const response = await ingestSemanticContext({
        project_id: ingestForm.project_id.trim(),
        sequence_id: normalizeOptional(ingestForm.sequence_id),
        scene_id: normalizeOptional(ingestForm.scene_id),
        shot_id: normalizeOptional(ingestForm.shot_id),
        entity_type: ingestForm.entity_type.trim(),
        title: ingestForm.title.trim(),
        content: ingestForm.content.trim(),
        tags: parseTags(ingestForm.tags),
        source: ingestForm.source.trim(),
        created_at: normalizeOptional(ingestForm.created_at),
        point_id: normalizeOptional(ingestForm.point_id),
        text: normalizeOptional(ingestForm.text),
      });
      setIngestResponse(response);
    } catch (error) {
      setIngestError(getBackendErrorMessage(error, "No se pudo ingerir el contexto semántico."));
      setIngestResponse(null);
    } finally {
      setIngestLoading(false);
    }
  }

  function renderSearchResult(result: SemanticContextSearchResult, index: number) {
    return (
      <article
        key={`${result.point_id ?? "result"}:${index}`}
        className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm"
      >
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h4 className="m-0 text-base font-semibold text-gray-900">{result.title || "Sin título"}</h4>
            <div className="mt-1 text-xs text-gray-500">
              {result.entity_type || "entity"}
              {result.source ? <span> · {result.source}</span> : null}
              {result.point_id ? <span> · {result.point_id}</span> : null}
            </div>
          </div>
          <div className="rounded-full border border-violet-200 bg-violet-50 px-3 py-1 text-xs font-semibold text-violet-700">
            score {typeof result.score === "number" ? result.score.toFixed(3) : "n/a"}
          </div>
        </div>

        <p className="mt-3 whitespace-pre-wrap text-sm text-gray-700">{result.content || "Sin contenido"}</p>

        <div className="mt-3 flex flex-wrap gap-2 text-xs text-gray-500">
          <span className="rounded-full bg-gray-100 px-2 py-1">project {result.project_id || "-"}</span>
          {result.sequence_id ? <span className="rounded-full bg-gray-100 px-2 py-1">sequence {result.sequence_id}</span> : null}
          {result.scene_id ? <span className="rounded-full bg-gray-100 px-2 py-1">scene {result.scene_id}</span> : null}
          {result.shot_id ? <span className="rounded-full bg-gray-100 px-2 py-1">shot {result.shot_id}</span> : null}
          {result.created_at ? <span className="rounded-full bg-gray-100 px-2 py-1">{result.created_at}</span> : null}
        </div>

        {result.tags.length > 0 ? (
          <div className="mt-3 flex flex-wrap gap-2">
            {result.tags.map((tag) => (
              <span key={`${result.point_id}:${tag}`} className="rounded-full border border-blue-200 bg-blue-50 px-2 py-1 text-xs text-blue-700">
                {tag}
              </span>
            ))}
          </div>
        ) : null}
      </article>
    );
  }

  return (
    <section className="mt-8 rounded-[28px] border border-gray-200 bg-gradient-to-br from-white via-white to-violet-50/60 p-6 shadow-sm md:p-8">
      <div className="mb-6 flex flex-col gap-2 text-left">
        <div className="text-xs font-semibold uppercase tracking-[0.2em] text-violet-500">Semantic Context</div>
        <h2 className="m-0">Búsqueda y contexto semántico</h2>
        <p className="text-sm text-gray-600">
          Consulta el contexto guardado en Qdrant y, si encaja, ingiere nuevo contexto textual desde el panel.
        </p>
      </div>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.15fr)_minmax(320px,0.85fr)]">
        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="mb-4 text-left">
            <h3 className="m-0 text-lg font-semibold text-gray-900">Buscar contexto</h3>
            <p className="mt-1 text-sm text-gray-600">Texto libre más filtros de metadatos básicos.</p>
            <label className="mt-3 inline-flex items-center gap-2 text-sm text-gray-600">
              <input
                type="checkbox"
                checked={autoSearchEnabled}
                onChange={(event) => setAutoSearchEnabled(event.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-violet-600 focus:ring-violet-500"
              />
              Auto-buscar al cambiar de shot
            </label>
          </div>

          <form className="space-y-4" onSubmit={(event) => void handleSearchSubmit(event)}>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="semantic-search-text">Consulta</label>
              <textarea
                id="semantic-search-text"
                rows={3}
                value={searchForm.text}
                onChange={(event) => setSearchForm((current) => ({ ...current, text: event.target.value }))}
                className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-violet-500 focus:ring-2 focus:ring-violet-200"
                placeholder="lluvia nocturna reflejos tension"
              />
            </div>

            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              <input value={searchForm.project_id} onChange={(event) => setSearchForm((current) => ({ ...current, project_id: event.target.value }))} className="rounded-xl border border-gray-300 px-3 py-2 text-sm" placeholder="project_id" />
              <input value={searchForm.sequence_id} onChange={(event) => setSearchForm((current) => ({ ...current, sequence_id: event.target.value }))} className="rounded-xl border border-gray-300 px-3 py-2 text-sm" placeholder="sequence_id" />
              <input value={searchForm.scene_id} onChange={(event) => setSearchForm((current) => ({ ...current, scene_id: event.target.value }))} className="rounded-xl border border-gray-300 px-3 py-2 text-sm" placeholder="scene_id" />
              <input value={searchForm.shot_id} onChange={(event) => setSearchForm((current) => ({ ...current, shot_id: event.target.value }))} className="rounded-xl border border-gray-300 px-3 py-2 text-sm" placeholder="shot_id" />
              <input value={searchForm.entity_type} onChange={(event) => setSearchForm((current) => ({ ...current, entity_type: event.target.value }))} className="rounded-xl border border-gray-300 px-3 py-2 text-sm" placeholder="entity_type" />
              <input value={searchForm.source} onChange={(event) => setSearchForm((current) => ({ ...current, source: event.target.value }))} className="rounded-xl border border-gray-300 px-3 py-2 text-sm" placeholder="source" />
              <input value={searchForm.tags} onChange={(event) => setSearchForm((current) => ({ ...current, tags: event.target.value }))} className="rounded-xl border border-gray-300 px-3 py-2 text-sm md:col-span-2 xl:col-span-2" placeholder="tags separadas por coma" />
              <input value={searchForm.limit} onChange={(event) => setSearchForm((current) => ({ ...current, limit: event.target.value }))} className="rounded-xl border border-gray-300 px-3 py-2 text-sm" placeholder="limit" type="number" min={1} max={20} />
            </div>

            {searchError ? <div className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{searchError}</div> : null}

            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="text-xs text-gray-500">
                {searchResponse ? `${searchResponse.count} resultado(s) · modelo ${searchResponse.embedding_model}` : "Sin búsqueda ejecutada"}
              </div>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => void handleQuickShotSearch()}
                  disabled={searchLoading || !selectedShot}
                  className="rounded-xl border border-violet-300 bg-white px-4 py-2 text-sm font-semibold text-violet-700 transition hover:bg-violet-50 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Buscar contexto del shot
                </button>
                <button
                  type="submit"
                  disabled={searchLoading || !canSearch}
                  className="rounded-xl bg-violet-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {searchLoading ? "Buscando..." : "Buscar contexto"}
                </button>
              </div>
            </div>
          </form>

          <div className="mt-5 space-y-3">
            {searchResponse?.results.length ? searchResponse.results.map(renderSearchResult) : null}
            {searchResponse && searchResponse.results.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-gray-300 bg-gray-50 px-4 py-6 text-sm text-gray-500">
                No hubo coincidencias para la consulta actual.
              </div>
            ) : null}
          </div>
        </div>

        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="mb-4 text-left">
            <h3 className="m-0 text-lg font-semibold text-gray-900">Ingest simple</h3>
            <p className="mt-1 text-sm text-gray-600">
              Upsert manual de contexto semántico. Útil para notas editoriales rápidas.
            </p>
          </div>

          <form className="space-y-3" onSubmit={(event) => void handleIngestSubmit(event)}>
            <input value={ingestForm.project_id} onChange={(event) => setIngestForm((current) => ({ ...current, project_id: event.target.value }))} className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm" placeholder="project_id" disabled={isReadOnly} />
            <div className="grid gap-3 md:grid-cols-2">
              <input value={ingestForm.sequence_id} onChange={(event) => setIngestForm((current) => ({ ...current, sequence_id: event.target.value }))} className="rounded-xl border border-gray-300 px-3 py-2 text-sm" placeholder="sequence_id" disabled={isReadOnly} />
              <input value={ingestForm.scene_id} onChange={(event) => setIngestForm((current) => ({ ...current, scene_id: event.target.value }))} className="rounded-xl border border-gray-300 px-3 py-2 text-sm" placeholder="scene_id" disabled={isReadOnly} />
              <input value={ingestForm.shot_id} onChange={(event) => setIngestForm((current) => ({ ...current, shot_id: event.target.value }))} className="rounded-xl border border-gray-300 px-3 py-2 text-sm" placeholder="shot_id" disabled={isReadOnly} />
              <input value={ingestForm.entity_type} onChange={(event) => setIngestForm((current) => ({ ...current, entity_type: event.target.value }))} className="rounded-xl border border-gray-300 px-3 py-2 text-sm" placeholder="entity_type" disabled={isReadOnly} />
            </div>
            <input value={ingestForm.title} onChange={(event) => setIngestForm((current) => ({ ...current, title: event.target.value }))} className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm" placeholder="title" disabled={isReadOnly} />
            <textarea value={ingestForm.content} onChange={(event) => setIngestForm((current) => ({ ...current, content: event.target.value }))} rows={4} className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm" placeholder="content" disabled={isReadOnly} />
            <textarea value={ingestForm.text} onChange={(event) => setIngestForm((current) => ({ ...current, text: event.target.value }))} rows={3} className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm" placeholder="text opcional para embedding. Si se deja vacío, se usa title + content." disabled={isReadOnly} />
            <div className="grid gap-3 md:grid-cols-2">
              <input value={ingestForm.source} onChange={(event) => setIngestForm((current) => ({ ...current, source: event.target.value }))} className="rounded-xl border border-gray-300 px-3 py-2 text-sm" placeholder="source" disabled={isReadOnly} />
              <input value={ingestForm.tags} onChange={(event) => setIngestForm((current) => ({ ...current, tags: event.target.value }))} className="rounded-xl border border-gray-300 px-3 py-2 text-sm" placeholder="tags separadas por coma" disabled={isReadOnly} />
              <input value={ingestForm.created_at} onChange={(event) => setIngestForm((current) => ({ ...current, created_at: event.target.value }))} className="rounded-xl border border-gray-300 px-3 py-2 text-sm" placeholder="created_at ISO opcional" disabled={isReadOnly} />
              <input value={ingestForm.point_id} onChange={(event) => setIngestForm((current) => ({ ...current, point_id: event.target.value }))} className="rounded-xl border border-gray-300 px-3 py-2 text-sm" placeholder="point_id opcional" disabled={isReadOnly} />
            </div>

            {ingestError ? <div className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{ingestError}</div> : null}
            {ingestResponse ? (
              <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-3 text-sm text-emerald-800">
                Upsert correcto en <code>{ingestResponse.collection}</code> con punto <code>{ingestResponse.point_id}</code>.
              </div>
            ) : null}

            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="text-xs text-gray-500">
                {isReadOnly ? "Modo lectura: la búsqueda sigue disponible, el ingest queda desactivado." : "Ingest manual disponible para admin/editor."}
              </div>
              <button
                type="submit"
                disabled={isReadOnly || ingestLoading || !canIngest}
                className="rounded-xl border border-violet-300 bg-white px-4 py-2 text-sm font-semibold text-violet-700 transition hover:bg-violet-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {ingestLoading ? "Ingeriendo..." : "Ingerir contexto"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </section>
  );
}
