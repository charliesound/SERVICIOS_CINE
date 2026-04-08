export type SemanticContextSearchRequest = {
  text: string;
  project_id: string;
  sequence_id?: string;
  scene_id?: string;
  shot_id?: string;
  entity_type?: string;
  source?: string;
  tags?: string[];
  limit?: number;
};

export type SemanticContextSearchQuery = {
  text: string;
  project_id: string;
  sequence_id?: string | null;
  scene_id?: string | null;
  shot_id?: string | null;
  entity_type?: string | null;
  source?: string | null;
  tags: string[];
  limit: number;
};

export type SemanticContextSearchResult = {
  point_id: string | null;
  score: number | null;
  project_id: string | null;
  sequence_id: string | null;
  scene_id: string | null;
  shot_id: string | null;
  entity_type: string | null;
  title: string | null;
  content: string | null;
  tags: string[];
  source: string | null;
  created_at: string | null;
};

export type SemanticContextSearchResponse = {
  ok: boolean;
  collection: string;
  embedding_model: string;
  dimensions: number;
  query: SemanticContextSearchQuery;
  count: number;
  results: SemanticContextSearchResult[];
};

export type SemanticContextIngestRequest = {
  project_id: string;
  sequence_id?: string;
  scene_id?: string;
  shot_id?: string;
  entity_type: string;
  title: string;
  content: string;
  tags?: string[];
  source: string;
  created_at?: string;
  point_id?: string;
  text?: string;
};

export type SemanticContextPayload = {
  project_id: string;
  sequence_id?: string | null;
  scene_id?: string | null;
  shot_id?: string | null;
  entity_type: string;
  title: string;
  content: string;
  tags: string[];
  source: string;
  created_at: string;
};

export type SemanticContextIngestResponse = {
  ok: boolean;
  collection: string;
  point_id: string;
  embedding_model: string;
  dimensions: number;
  payload: SemanticContextPayload;
  qdrant: Record<string, unknown>;
};
