import { api } from "./api";

import type { Character } from "../types/character";
import type { Job } from "../types/job";
import type { Project } from "../types/project";
import type { Scene } from "../types/scene";
import type { Shot } from "../types/shot";


type StorageProject = {
  id?: string;
  title?: string | null;
  name?: string | null;
  description?: string | null;
};

type StorageCharacter = {
  id?: string;
  project_id?: string | null;
  name?: string | null;
  seed_master?: number | string | null;
  reference_images?: unknown;
};

type StorageScene = {
  id?: string;
  title?: string | null;
  name?: string | null;
  dramatic_purpose?: string | null;
};

type StorageShot = {
  id?: string;
  title?: string | null;
  prompt?: string | null;
  negative_prompt?: string | null;
  scene_id?: string | null;
  sequence_id?: string | null;
  seed?: number | string | null;
  cfg?: number | string | null;
  steps?: number | string | null;
  workflow_key?: string | null;
  refs?: unknown;
  references?: unknown;
};

export type DashboardData = {
  projects: Project[];
  characters: Character[];
  scenes: Scene[];
  shots: Shot[];
  jobs: Job[];
};

export type StorageExportData = {
  project: Record<string, unknown> | null;
  characters: Array<Record<string, unknown>>;
  sequences: Array<Record<string, unknown>>;
  scenes: Array<Record<string, unknown>>;
  shots: Array<Record<string, unknown>>;
};

export type StorageImportMode = "replace" | "append";

export type StorageImportPayload = {
  project: Record<string, unknown> | null;
  characters: unknown[];
  sequences: unknown[];
  scenes: unknown[];
  shots: unknown[];
};


function isObjectRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}


function normalizeImportList(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}


export function normalizeStorageImportPayload(rawValue: unknown): StorageImportPayload {
  if (!isObjectRecord(rawValue)) {
    throw new Error("IMPORT_INCOMPATIBLE_FORMAT");
  }

  const payloadCandidate = isObjectRecord(rawValue.data) ? rawValue.data : rawValue;
  const hasSupportedKeys =
    Object.prototype.hasOwnProperty.call(payloadCandidate, "project") ||
    Object.prototype.hasOwnProperty.call(payloadCandidate, "characters") ||
    Object.prototype.hasOwnProperty.call(payloadCandidate, "sequences") ||
    Object.prototype.hasOwnProperty.call(payloadCandidate, "scenes") ||
    Object.prototype.hasOwnProperty.call(payloadCandidate, "shots");

  if (!hasSupportedKeys) {
    throw new Error("IMPORT_INCOMPATIBLE_FORMAT");
  }

  return {
    project: isObjectRecord(payloadCandidate.project) ? payloadCandidate.project : null,
    characters: normalizeImportList(payloadCandidate.characters),
    sequences: normalizeImportList(payloadCandidate.sequences),
    scenes: normalizeImportList(payloadCandidate.scenes),
    shots: normalizeImportList(payloadCandidate.shots),
  };
}


function mapStorageProject(project: StorageProject | null | undefined): Project | null {
  if (!project || typeof project.id !== "string" || project.id.trim() === "") {
    return null;
  }

  const title =
    typeof project.title === "string" && project.title.trim() !== ""
      ? project.title.trim()
      : typeof project.name === "string" && project.name.trim() !== ""
        ? project.name.trim()
        : project.id.trim();

  const description =
    typeof project.description === "string" && project.description.trim() !== ""
      ? project.description.trim()
      : null;

  return {
    id: project.id.trim(),
    title,
    description,
  };
}


function mapStorageCharacter(character: StorageCharacter): Character | null {
  if (typeof character.id !== "string" || character.id.trim() === "") {
    return null;
  }

  const projectId = typeof character.project_id === "string" ? character.project_id.trim() : "";
  const name =
    typeof character.name === "string" && character.name.trim() !== ""
      ? character.name.trim()
      : character.id.trim();

  const referenceImages = mapStringArray(character.reference_images);
  const seedMaster = parseInteger(character.seed_master) ?? 0;

  return {
    id: character.id.trim(),
    project_id: projectId,
    name,
    seed_master: seedMaster,
    reference_images: referenceImages,
  };
}


function normalizeCharacterSeedMaster(value: unknown): number {
  if (value === undefined || value === null) {
    return 0;
  }

  if (typeof value === "string" && value.trim() === "") {
    return 0;
  }

  const parsed = parseInteger(value);
  if (parsed === null) {
    throw new Error("Character seed_master must be an integer");
  }

  return parsed;
}


function mapStorageScene(scene: StorageScene, projectId: string): Scene | null {
  if (typeof scene.id !== "string" || scene.id.trim() === "") {
    return null;
  }

  const title =
    typeof scene.title === "string" && scene.title.trim() !== ""
      ? scene.title.trim()
      : typeof scene.name === "string" && scene.name.trim() !== ""
        ? scene.name.trim()
        : scene.id.trim();

  const dramaticPurpose =
    typeof scene.dramatic_purpose === "string" && scene.dramatic_purpose.trim() !== ""
      ? scene.dramatic_purpose.trim()
      : null;

  return {
    id: scene.id.trim(),
    project_id: projectId,
    title,
    dramatic_purpose: dramaticPurpose,
  };
}


function parseNumber(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  if (typeof value === "string") {
    const trimmed = value.trim();
    if (!trimmed) {
      return null;
    }

    const parsed = Number(trimmed);
    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }

  return null;
}


function parseInteger(value: unknown): number | null {
  const parsed = parseNumber(value);
  return parsed === null ? null : Math.trunc(parsed);
}


function mapStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return Array.from(
    new Set(
      value
        .filter((item): item is string => typeof item === "string")
        .map((item) => item.trim())
        .filter((item) => item.length > 0)
    )
  );
}


function mapStorageShot(shot: StorageShot): Shot | null {
  if (typeof shot.id !== "string" || shot.id.trim() === "") {
    return null;
  }

  if (typeof shot.scene_id !== "string" || shot.scene_id.trim() === "") {
    return null;
  }

  const title = typeof shot.title === "string" && shot.title.trim() !== "" ? shot.title.trim() : shot.id.trim();
  const sequenceId = typeof shot.sequence_id === "string" ? shot.sequence_id.trim() : "";
  const prompt = typeof shot.prompt === "string" && shot.prompt.trim() !== "" ? shot.prompt.trim() : title;
  const negativePrompt =
    typeof shot.negative_prompt === "string"
      ? shot.negative_prompt.trim() || null
      : shot.negative_prompt === null
        ? null
        : null;
  const seed = parseInteger(shot.seed) ?? 0;
  const cfg = parseNumber(shot.cfg) ?? 0;
  const steps = parseInteger(shot.steps) ?? 0;
  const workflowKeyFromShot = typeof shot.workflow_key === "string" ? shot.workflow_key.trim() : "";
  const refs = mapStringArray(Array.isArray(shot.refs) ? shot.refs : shot.references);

  return {
    id: shot.id.trim(),
    scene_id: shot.scene_id.trim(),
    type: title,
    prompt,
    negative_prompt: negativePrompt,
    seed,
    cfg,
    steps,
    workflow_key: workflowKeyFromShot || (sequenceId ? `sequence:${sequenceId}` : "storage"),
    refs,
  };
}


function mapStorageShotFromMutationResponse(storageShot: StorageShot): Shot {
  const mappedShot = mapStorageShot(storageShot);
  if (!mappedShot) {
    throw new Error("Storage shot response is not compatible with editor");
  }

  const prompt = typeof storageShot.prompt === "string" ? storageShot.prompt : mappedShot.prompt;
  const negativePrompt =
    typeof storageShot.negative_prompt === "string" || storageShot.negative_prompt === null
      ? storageShot.negative_prompt
      : mappedShot.negative_prompt;
  const seed = parseInteger(storageShot.seed) ?? mappedShot.seed;
  const cfg = parseNumber(storageShot.cfg) ?? mappedShot.cfg;
  const steps = parseInteger(storageShot.steps) ?? mappedShot.steps;
  const workflowKey =
    typeof storageShot.workflow_key === "string" && storageShot.workflow_key.trim() !== ""
      ? storageShot.workflow_key.trim()
      : mappedShot.workflow_key;
  const refs = mapStringArray(Array.isArray(storageShot.refs) ? storageShot.refs : storageShot.references);

  return {
    ...mappedShot,
    prompt,
    negative_prompt: negativePrompt,
    seed,
    cfg,
    steps,
    workflow_key: workflowKey,
    refs,
  };
}


async function loadProjectAndScenesFromStorage(): Promise<{ projects: Project[]; scenes: Scene[] }> {
  const projectResponse = await api.get<{ ok?: boolean; project?: StorageProject | null }>("/api/storage/project");
  const project = mapStorageProject(projectResponse.data?.project);

  if (!project) {
    return {
      projects: [],
      scenes: [],
    };
  }

  const scenesResponse = await api.get<{ ok?: boolean; project_id?: string; scenes?: StorageScene[]; count?: number }>(
    `/api/storage/project/${encodeURIComponent(project.id)}/scenes`
  );
  const rawScenes: StorageScene[] = Array.isArray(scenesResponse.data?.scenes) ? scenesResponse.data.scenes : [];
  const scenes: Scene[] = [];

  for (const rawScene of rawScenes) {
    const scene = mapStorageScene(rawScene, project.id);
    if (scene) {
      scenes.push(scene);
    }
  }

  return {
    projects: [project],
    scenes,
  };
}


export async function loadDashboardData(): Promise<DashboardData> {
  const [charactersResponse, shotsResponse] = await Promise.all([
    api.get("/api/storage/characters"),
    api.get("/api/storage/shots"),
  ]);

  const rawStorageCharacters: StorageCharacter[] = Array.isArray(charactersResponse.data?.characters)
    ? charactersResponse.data.characters
    : [];
  const characters = rawStorageCharacters
    .map(mapStorageCharacter)
    .filter((character): character is Character => character !== null);

  const rawStorageShots: StorageShot[] = Array.isArray(shotsResponse.data?.shots)
    ? shotsResponse.data.shots
    : [];
  const shots = rawStorageShots
    .map(mapStorageShot)
    .filter((shot): shot is Shot => shot !== null);

  const storageData = await loadProjectAndScenesFromStorage();
  const projects = storageData.projects;
  const scenes = storageData.scenes;

  // LEGACY-TRANSIENT: `/jobs` is mock-only and intentionally excluded
  // from dashboard critical loading until a persistent replacement exists.
  const jobs: Job[] = [];

  return {
    projects,
    characters,
    scenes,
    shots,
    jobs,
  };
}


export async function updateStorageShot(updatedShot: Shot): Promise<Shot> {
  const response = await api.patch(`/api/storage/shot/${encodeURIComponent(updatedShot.id)}`, {
    title: updatedShot.type,
    prompt: updatedShot.prompt,
    negative_prompt: updatedShot.negative_prompt || null,
    seed: updatedShot.seed,
    cfg: updatedShot.cfg,
    steps: updatedShot.steps,
    workflow_key: updatedShot.workflow_key,
    refs: updatedShot.refs,
  });

  const storageShot = response.data?.shot;

  if (!storageShot || typeof storageShot !== "object") {
    throw new Error("Invalid storage shot response");
  }

  return mapStorageShotFromMutationResponse(storageShot as StorageShot);
}


export async function createStorageShot(sceneId: string): Promise<Shot> {
  const normalizedSceneId = sceneId.trim();
  if (!normalizedSceneId) {
    throw new Error("Invalid scene id");
  }

  const response = await api.post("/api/storage/shot", {
    title: "Nuevo Plano",
    prompt: "Describe este plano",
    negative_prompt: null,
    status: "draft",
    scene_id: normalizedSceneId,
    seed: 0,
    cfg: 0,
    steps: 0,
    workflow_key: "storage",
    refs: [],
  });

  const storageShot = response.data?.shot;
  if (!storageShot || typeof storageShot !== "object") {
    throw new Error("Invalid storage shot response");
  }

  return mapStorageShotFromMutationResponse(storageShot as StorageShot);
}


export async function deleteStorageShot(shotId: string): Promise<void> {
  await api.delete(`/api/storage/shot/${encodeURIComponent(shotId)}`);
}


export async function createStorageCharacter(projectId: string, name: string): Promise<void> {
  const normalizedProjectId = projectId.trim();
  const normalizedName = name.trim();

  if (!normalizedProjectId) {
    throw new Error("Invalid project id");
  }

  if (!normalizedName) {
    throw new Error("Character name is required");
  }

  await api.post("/api/storage/character", {
    project_id: normalizedProjectId,
    name: normalizedName,
  });
}


export async function deleteStorageCharacter(characterId: string): Promise<void> {
  await api.delete(`/api/storage/character/${encodeURIComponent(characterId)}`);
}


export async function updateStorageCharacter(
  characterId: string,
  payload: { name?: string; seed_master?: number | string | null; reference_images?: unknown }
): Promise<void> {
  const normalizedCharacterId = characterId.trim();
  if (!normalizedCharacterId) {
    throw new Error("Invalid character id");
  }

  const patchPayload: { name?: string; seed_master?: number; reference_images?: string[] } = {};

  if (payload.name !== undefined) {
    const normalizedName = payload.name.trim();
    if (!normalizedName) {
      throw new Error("Character name is required");
    }
    patchPayload.name = normalizedName;
  }

  if (payload.seed_master !== undefined) {
    patchPayload.seed_master = normalizeCharacterSeedMaster(payload.seed_master);
  }

  if (payload.reference_images !== undefined) {
    patchPayload.reference_images = mapStringArray(payload.reference_images);
  }

  if (
    patchPayload.name === undefined &&
    patchPayload.seed_master === undefined &&
    patchPayload.reference_images === undefined
  ) {
    throw new Error("No character fields to update");
  }

  await api.patch(`/api/storage/character/${encodeURIComponent(normalizedCharacterId)}`, patchPayload);
}


export async function createStorageScene(projectId: string): Promise<void> {
  const normalizedProjectId = projectId.trim();
  if (!normalizedProjectId) {
    throw new Error("Invalid project id");
  }

  const sequencesResponse = await api.get<{ sequences?: Array<{ id?: string }> }>(
    `/api/storage/project/${encodeURIComponent(normalizedProjectId)}/sequences`
  );

  const sequences = Array.isArray(sequencesResponse.data?.sequences)
    ? sequencesResponse.data.sequences
    : [];
  const firstSequenceWithId = sequences.find(
    (sequence) => typeof sequence.id === "string" && sequence.id.trim() !== ""
  );

  if (!firstSequenceWithId || !firstSequenceWithId.id) {
    throw new Error("Project has no available sequence for scene creation");
  }

  await api.post("/api/storage/scene", {
    title: "Nueva Escena",
    dramatic_purpose: null,
    sequence_id: firstSequenceWithId.id.trim(),
  });
}


export async function deleteStorageScene(sceneId: string): Promise<void> {
  await api.delete(`/api/storage/scene/${encodeURIComponent(sceneId)}`);
}


export async function renameStorageProject(projectId: string, nextTitle: string): Promise<void> {
  const normalizedProjectId = projectId.trim();
  const normalizedTitle = nextTitle.trim();

  if (!normalizedProjectId) {
    throw new Error("Invalid project id");
  }

  if (!normalizedTitle) {
    throw new Error("Project title is required");
  }

  const currentProjectResponse = await api.get<{ project?: Record<string, unknown> | null }>("/api/storage/project");
  const currentProject = currentProjectResponse.data?.project;

  if (!currentProject || typeof currentProject !== "object") {
    throw new Error("No active project available");
  }

  const currentId =
    typeof currentProject.id === "string" && currentProject.id.trim() !== "" ? currentProject.id.trim() : null;

  if (!currentId || currentId !== normalizedProjectId) {
    throw new Error("Active project mismatch");
  }

  await api.patch("/api/storage/project", {
    ...currentProject,
    id: currentId,
    title: normalizedTitle,
    name: normalizedTitle,
  });
}


export async function resetStorageData(): Promise<void> {
  await api.post("/api/storage/reset");
}


export async function seedStorageData(): Promise<void> {
  await api.post("/api/storage/seed-demo?replace=false");
}


export async function exportStorageData(): Promise<StorageExportData> {
  const response = await api.get<{ data?: StorageExportData }>("/api/storage/export-json");
  const exportData = response.data?.data;

  if (!exportData || typeof exportData !== "object") {
    throw new Error("Invalid storage export response");
  }

  const characters = Array.isArray(exportData.characters) ? exportData.characters : [];
  const sequences = Array.isArray(exportData.sequences) ? exportData.sequences : [];
  const scenes = Array.isArray(exportData.scenes) ? exportData.scenes : [];
  const shots = Array.isArray(exportData.shots) ? exportData.shots : [];

  return {
    project:
      exportData.project && typeof exportData.project === "object" && !Array.isArray(exportData.project)
        ? exportData.project
        : null,
    characters,
    sequences,
    scenes,
    shots,
  };
}


export async function importStorageData(
  payload: StorageImportPayload,
  mode: StorageImportMode = "replace"
): Promise<void> {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    throw new Error("Invalid storage import payload");
  }

  await api.post("/api/storage/import-json", payload, {
    params: { mode },
  });
}


export async function exportActiveStorageProject(): Promise<StorageExportData> {
  return exportStorageData();
}
