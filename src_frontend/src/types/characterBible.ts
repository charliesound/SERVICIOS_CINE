export type CharacterBibleApprovedAssetType =
  | 'face_sheet'
  | 'full_body'
  | 'costume'
  | 'hair_makeup'
  | 'prop'
  | 'mood'
  | 'other'

export interface CharacterBibleReference {
  asset_id: string
  asset_type: CharacterBibleApprovedAssetType
  asset_api_url?: string | null
  thumbnail_url?: string | null
  asset_file_name?: string | null
  reference_id?: string | null
  description?: string | null
  is_primary: boolean
  sort_order: number
  approved_by_user_id?: string | null
  approved_at?: string | null
  notes?: string | null
}

export interface CharacterBibleLookVariant {
  look_id: string
  look_name: string
  narrative_phase?: string | null
  approved_references: CharacterBibleReference[]
  wardrobe_notes?: string | null
  hair_makeup_notes?: string | null
  key_props: string[]
  continuity_rules: string[]
  negative_constraints: string[]
  scene_ids: string[]
}

export interface CharacterBibleEntry {
  character_id: string
  project_id: string
  character_name: string
  approved_reference_asset_id?: string | null
  secondary_reference_asset_ids: string[]
  approved_references: CharacterBibleReference[]
  look_variants: CharacterBibleLookVariant[]
  default_look_id?: string | null
  wardrobe_notes?: string | null
  hair_makeup_notes?: string | null
  key_props: string[]
  continuity_rules: string[]
  negative_constraints: string[]
  notes?: string | null
  version: number
  created_at?: string | null
  updated_at?: string | null
}

export interface CharacterBibleListResponse {
  entries: CharacterBibleEntry[]
  total: number
}

export interface CharacterBibleUpsertPayload {
  character_id: string
  character_name: string
  approved_reference_asset_id?: string | null
  wardrobe_notes?: string | null
  hair_makeup_notes?: string | null
  key_props: string[]
  continuity_rules: string[]
  negative_constraints: string[]
  notes?: string | null
}

export interface CharacterBibleLookVariantPayload {
  look_id: string
  look_name: string
  narrative_phase?: string | null
  wardrobe_notes?: string | null
  hair_makeup_notes?: string | null
  key_props: string[]
  continuity_rules: string[]
  negative_constraints: string[]
  scene_ids: string[]
}

export interface CharacterBibleReferencePayload {
  asset_id: string
  asset_type: CharacterBibleApprovedAssetType
  asset_api_url?: string | null
  asset_file_name?: string | null
  reference_id?: string | null
  description?: string | null
  is_primary: boolean
  sort_order: number
  notes?: string | null
}

export interface CharacterBibleResolvePayload {
  project_id: string
  character_id: string
  look_id?: string | null
  narrative_phase?: string | null
  scene_id?: string | null
}

export interface CharacterBibleResolveResponse {
  project_id: string
  character_id: string
  character_name: string
  resolved_look: CharacterBibleLookVariant | null
  primary_reference: CharacterBibleReference | null
  secondary_references: CharacterBibleReference[]
  prompt_lock_block?: string | null
  prompt_negative_block?: string | null
  continuity_block?: string | null
  applied_reference_ids: string[]
  unresolved_props: string[]
  trace_metadata: Record<string, unknown>
}

export interface CharacterBibleTraceResponse {
  character_id: string
  character_name: string
  trace_metadata: Record<string, unknown>
}
