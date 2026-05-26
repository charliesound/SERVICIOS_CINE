import api from './client'
import type {
  CharacterBibleEntry,
  CharacterBibleListResponse,
  CharacterBibleEntryCreate,
  CharacterBibleEntryUpdate,
  LookVariantCreate,
  ReferenceAssetCreate,
  CharacterBibleResolveRequest,
  CharacterBibleResolveResult,
  TraceResponse,
  ApprovedReferenceAsset,
  CharacterLookVariant,
} from '@/types/characterBible'

export const characterBibleApi = {
  list: async (projectId: string): Promise<CharacterBibleListResponse> => {
    const { data } = await api.get<CharacterBibleListResponse>(
      `/api/projects/${projectId}/character-bible`
    )
    return data
  },

  get: async (projectId: string, characterId: string): Promise<CharacterBibleEntry> => {
    const { data } = await api.get<CharacterBibleEntry>(
      `/api/projects/${projectId}/character-bible/${characterId}`
    )
    return data
  },

  upsert: async (
    projectId: string,
    characterId: string,
    payload: CharacterBibleEntryCreate
  ): Promise<CharacterBibleEntry> => {
    if (payload.character_id !== characterId) {
      throw new Error('character_id in path and body must match')
    }
    const { data } = await api.put<CharacterBibleEntry>(
      `/api/projects/${projectId}/character-bible/${characterId}`,
      payload
    )
    return data
  },

  addLookVariant: async (
    projectId: string,
    characterId: string,
    payload: LookVariantCreate
  ): Promise<CharacterLookVariant> => {
    const { data } = await api.post<CharacterLookVariant>(
      `/api/projects/${projectId}/character-bible/${characterId}/look-variants`,
      payload
    )
    return data
  },

  addReference: async (
    projectId: string,
    characterId: string,
    payload: ReferenceAssetCreate
  ): Promise<ApprovedReferenceAsset> => {
    const { data } = await api.post<ApprovedReferenceAsset>(
      `/api/projects/${projectId}/character-bible/${characterId}/references`,
      payload
    )
    return data
  },

  resolve: async (
    projectId: string,
    characterId: string,
    payload: CharacterBibleResolveRequest
  ): Promise<CharacterBibleResolveResult> => {
    if (payload.project_id !== projectId) {
      throw new Error('project_id in path and body must match')
    }
    if (payload.character_id !== characterId) {
      throw new Error('character_id in path and body must match')
    }
    const { data } = await api.post<CharacterBibleResolveResult>(
      `/api/projects/${projectId}/character-bible/${characterId}/resolve`,
      payload
    )
    return data
  },

  getTrace: async (
    projectId: string,
    characterId: string
  ): Promise<TraceResponse> => {
    const { data } = await api.get<TraceResponse>(
      `/api/projects/${projectId}/character-bible/${characterId}/trace`
    )
    return data
  },
}