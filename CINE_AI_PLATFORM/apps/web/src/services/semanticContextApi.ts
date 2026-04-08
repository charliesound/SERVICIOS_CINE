import { api } from "./api";

import type {
  SemanticContextIngestRequest,
  SemanticContextIngestResponse,
  SemanticContextSearchRequest,
  SemanticContextSearchResponse,
} from "../types/semanticContext";


export async function searchSemanticContext(payload: SemanticContextSearchRequest): Promise<SemanticContextSearchResponse> {
  const response = await api.post<SemanticContextSearchResponse>("/context/semantic/search", payload);
  return response.data;
}


export async function ingestSemanticContext(payload: SemanticContextIngestRequest): Promise<SemanticContextIngestResponse> {
  const response = await api.post<SemanticContextIngestResponse>("/context/semantic/ingest", payload);
  return response.data;
}
