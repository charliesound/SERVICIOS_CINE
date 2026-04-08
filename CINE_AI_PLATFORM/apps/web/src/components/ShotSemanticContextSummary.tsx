import { useEffect, useMemo, useState } from "react";

import { searchSemanticContext } from "../services/semanticContextApi";
import type { Scene } from "../types/scene";
import type { Shot } from "../types/shot";
import type { SemanticContextSearchResult } from "../types/semanticContext";


type ShotSemanticContextSummaryProps = {
  selectedShot: Shot | null;
  selectedScene: Scene | null;
};


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


function buildShotSearchText(selectedShot: Shot, selectedScene: Scene | null): string {
  const sceneTitle = selectedScene?.title?.trim() ?? "";
  const prompt = selectedShot.prompt.trim();
  return [sceneTitle, prompt].filter((value) => value !== "").join(" · ");
}


function summarizeContent(content: string | null): string {
  const normalized = String(content ?? "").trim();
  if (normalized.length <= 180) {
    return normalized || "Sin contenido";
  }

  return `${normalized.slice(0, 177)}...`;
}


export default function ShotSemanticContextSummary({
  selectedShot,
  selectedScene,
}: ShotSemanticContextSummaryProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState<SemanticContextSearchResult[]>([]);

  const projectId = selectedScene?.project_id?.trim() ?? "";
  const queryText = useMemo(() => {
    if (!selectedShot) {
      return "";
    }

    return buildShotSearchText(selectedShot, selectedScene);
  }, [selectedScene, selectedShot]);

  useEffect(() => {
    if (!selectedShot || !projectId || !queryText.trim()) {
      setResults([]);
      setError("");
      return;
    }

    const shot = selectedShot;
    let cancelled = false;

    async function loadSemanticSummary() {
      setLoading(true);
      setError("");

      try {
        const response = await searchSemanticContext({
          text: queryText,
          project_id: projectId,
          scene_id: shot.scene_id,
          shot_id: shot.id,
          entity_type: "shot_note",
          limit: 3,
        });

        if (!cancelled) {
          setResults(response.results.slice(0, 3));
        }
      } catch (searchError) {
        if (!cancelled) {
          setResults([]);
          setError(getBackendErrorMessage(searchError, "No se pudo cargar el contexto relevante del shot."));
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadSemanticSummary();

    return () => {
      cancelled = true;
    };
  }, [projectId, queryText, selectedShot]);

  if (!selectedShot) {
    return (
      <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
        <h3 className="m-0 text-base font-semibold text-gray-900">Contexto relevante</h3>
        <p className="mt-2 text-sm text-gray-500">Selecciona un shot para ver contexto semántico relacionado.</p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between gap-3">
        <div>
          <h3 className="m-0 text-base font-semibold text-gray-900">Contexto relevante</h3>
          <p className="mt-1 text-xs text-gray-500">Top 3 resultados para el shot seleccionado.</p>
        </div>
        <div className="rounded-full border border-violet-200 bg-violet-50 px-2 py-1 text-[11px] font-semibold text-violet-700">
          {selectedShot.id}
        </div>
      </div>

      {loading ? <p className="text-sm text-gray-500">Buscando contexto...</p> : null}
      {error ? <div className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div> : null}

      {!loading && !error && results.length === 0 ? (
        <p className="text-sm text-gray-500">No hay contexto relevante para este shot.</p>
      ) : null}

      <div className="space-y-3">
        {results.map((result, index) => (
          <article key={`${result.point_id ?? selectedShot.id}:${index}`} className="rounded-xl border border-gray-200 bg-gray-50 px-3 py-3 text-left">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-sm font-semibold text-gray-900">{result.title || "Sin título"}</div>
                <div className="mt-1 text-xs text-gray-500">
                  {result.entity_type || "entity"}
                </div>
              </div>
              <div className="rounded-full border border-violet-200 bg-white px-2 py-1 text-[11px] font-semibold text-violet-700">
                {typeof result.score === "number" ? result.score.toFixed(3) : "n/a"}
              </div>
            </div>

            <p className="mt-2 text-sm text-gray-700">{summarizeContent(result.content)}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
