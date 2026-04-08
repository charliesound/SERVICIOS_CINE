import crypto from "node:crypto";
import {
  createShot as createShotInRepo,
  deleteShot as deleteShotInRepo,
  getAllShots,
  getShotById,
  updateShot as updateShotInRepo,
} from "../repositories/shots.repository.js";

function normalizeString(value) {
  return typeof value === "string" ? value.trim() : value;
}

function normalizeArray(value) {
  return Array.isArray(value) ? value : [];
}

function normalizeShotPayload(payload = {}, existingShot = null) {
  const base = existingShot ? { ...existingShot } : {};

  const next = {
    ...base,
    ...payload,
  };

  if (!next.id) {
    next.id = crypto.randomUUID();
  }

  if ("title" in next) next.title = normalizeString(next.title);
  if ("prompt" in next) next.prompt = normalizeString(next.prompt);
  if ("raw_prompt" in next) next.raw_prompt = normalizeString(next.raw_prompt);
  if ("negative_prompt" in next) next.negative_prompt = normalizeString(next.negative_prompt);
  if ("camera_preset" in next) next.camera_preset = normalizeString(next.camera_preset);
  if ("nominal_ratio" in next) next.nominal_ratio = normalizeString(next.nominal_ratio);
  if ("scene_id" in next) next.scene_id = normalizeString(next.scene_id);
  if ("sequence_id" in next) next.sequence_id = normalizeString(next.sequence_id);
  if ("status" in next) next.status = normalizeString(next.status);

  if ("tags" in next) next.tags = normalizeArray(next.tags);
  if ("references" in next) next.references = normalizeArray(next.references);
  if ("layers" in next) next.layers = normalizeArray(next.layers);
  if ("render_inputs" in next) next.render_inputs = next.render_inputs ?? {};
  if ("structured_prompt" in next) next.structured_prompt = next.structured_prompt ?? {};
  if ("metadata" in next) next.metadata = next.metadata ?? {};

  next.updated_at = new Date().toISOString();
  if (!existingShot) {
    next.created_at = next.created_at ?? next.updated_at;
  }

  return next;
}

export async function listShots() {
  return getAllShots();
}

export async function findShotById(id) {
  return getShotById(id);
}

export async function createShot(payload) {
  const shot = normalizeShotPayload(payload);
  return createShotInRepo(shot);
}

export async function updateShot(id, payload) {
  return updateShotInRepo(id, async (existingShot) => {
    if (!existingShot) {
      return null;
    }
    return normalizeShotPayload(payload, existingShot);
  });
}

export async function patchShot(id, patch) {
  return updateShotInRepo(id, async (existingShot) => {
    if (!existingShot) {
      return null;
    }
    return normalizeShotPayload({ ...existingShot, ...patch }, existingShot);
  });
}

export async function removeShot(id) {
  return deleteShotInRepo(id);
}