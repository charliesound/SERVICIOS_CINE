import api from './client'
import type {
  CharacterBibleEntry,
  CharacterBibleListResponse,
  CharacterBibleLookVariant,
  CharacterBibleLookVariantPayload,
  CharacterBibleReference,
  CharacterBibleReferencePayload,
  CharacterBibleResolvePayload,
  CharacterBibleResolveResponse,
  CharacterBibleTraceResponse,
  CharacterBibleUpsertPayload,
} from '@/types/characterBible'

export async function getCharacterBible(projectId: string): Promise<CharacterBibleListResponse> {
  const { data } = await api.get<CharacterBibleListResponse>(`/projects/${projectId}/character-bible`)
  return data
}

export async function getCharacterBibleEntry(projectId: string, characterId: string): Promise<CharacterBibleEntry> {
  const { data } = await api.get<CharacterBibleEntry>(`/projects/${projectId}/character-bible/${characterId}`)
  return data
}

export async function upsertCharacterBibleEntry(
  projectId: string,
  characterId: string,
  payload: CharacterBibleUpsertPayload
): Promise<CharacterBibleEntry> {
  if (payload.character_id !== characterId) {
    throw new Error('character_id in path and body must match')
  }

  const { data } = await api.put<CharacterBibleEntry>(`/projects/${projectId}/character-bible/${characterId}`, payload)
  return data
}

export async function addCharacterBibleLookVariant(
  projectId: string,
  characterId: string,
  payload: CharacterBibleLookVariantPayload
): Promise<CharacterBibleLookVariant> {
  const { data } = await api.post<CharacterBibleLookVariant>(
    `/projects/${projectId}/character-bible/${characterId}/look-variants`,
    payload
  )
  return data
}

export async function addCharacterBibleReference(
  projectId: string,
  characterId: string,
  payload: CharacterBibleReferencePayload
): Promise<CharacterBibleReference> {
  const { data } = await api.post<CharacterBibleReference>(
    `/projects/${projectId}/character-bible/${characterId}/references`,
    payload
  )
  return data
}

export async function resolveCharacterBible(
  projectId: string,
  characterId: string,
  payload: CharacterBibleResolvePayload
): Promise<CharacterBibleResolveResponse> {
  if (payload.project_id !== projectId) {
    throw new Error('project_id in path and body must match')
  }
  if (payload.character_id !== characterId) {
    throw new Error('character_id in path and body must match')
  }

  const { data } = await api.post<CharacterBibleResolveResponse>(
    `/projects/${projectId}/character-bible/${characterId}/resolve`,
    payload
  )
  return data
}

export async function getCharacterBibleTrace(
  projectId: string,
  characterId: string
): Promise<CharacterBibleTraceResponse> {
  const { data } = await api.get<CharacterBibleTraceResponse>(`/projects/${projectId}/character-bible/${characterId}/trace`)
  return data
}

export const characterBibleApi = {
  getCharacterBible,
  getCharacterBibleEntry,
  upsertCharacterBibleEntry,
  addCharacterBibleLookVariant,
  addCharacterBibleReference,
  resolveCharacterBible,
  getCharacterBibleTrace,
}
