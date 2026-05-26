import { useEffect, useMemo, useState } from 'react'
import { CheckCircle2, ChevronLeft, ChevronRight, GitBranch, Image, Link2, Loader2, Plus, Save, Shield, Sparkles, UserRound } from 'lucide-react'
import { characterBibleApi } from '@/api/characterBible'
import { storyboardApi } from '@/api/storyboard'
import type {
  CharacterBibleApprovedAssetType,
  CharacterBibleEntry,
  CharacterBibleListResponse,
  CharacterBibleLookVariantPayload,
  CharacterBibleReferencePayload,
  CharacterBibleResolveResponse,
  CharacterBibleTraceResponse,
  CharacterBibleUpsertPayload,
} from '@/types/characterBible'
import type { ProjectImageAssetItem, ProjectImageAssetPaginationMeta } from '@/types/storyboard'

interface CharacterBiblePanelProps {
  projectId: string
  suggestedCharacters?: string[]
}

interface CharacterBibleDraft {
  characterId: string
  characterName: string
  visualDescription: string
  wardrobe: string
  hairMakeup: string
  associatedProps: string
  negativeConstraints: string
}

const APPROVED_ASSET_TYPES: CharacterBibleApprovedAssetType[] = [
  'face_sheet',
  'full_body',
  'costume',
  'hair_makeup',
  'prop',
  'mood',
  'other',
]

const EMPTY_DRAFT: CharacterBibleDraft = {
  characterId: '',
  characterName: '',
  visualDescription: '',
  wardrobe: '',
  hairMakeup: '',
  associatedProps: '',
  negativeConstraints: '',
}

const EMPTY_LOOK_VARIANT: CharacterBibleLookVariantPayload = {
  look_id: '',
  look_name: '',
  narrative_phase: '',
  wardrobe_notes: '',
  hair_makeup_notes: '',
  key_props: [],
  continuity_rules: [],
  negative_constraints: [],
  scene_ids: [],
}

const EMPTY_REFERENCE: CharacterBibleReferencePayload = {
  asset_id: '',
  asset_type: 'face_sheet',
  asset_api_url: null,
  asset_file_name: null,
  reference_id: null,
  description: '',
  is_primary: false,
  sort_order: 0,
  notes: '',
}

function parseApiError(error: unknown, fallback: string): string {
  if (typeof error === 'object' && error !== null) {
    const maybeResponse = error as { response?: { data?: { detail?: string } }; message?: string }
    return maybeResponse.response?.data?.detail || maybeResponse.message || fallback
  }
  return fallback
}

function slugifyCharacterId(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

function parseListField(value: string): string[] {
  return value
    .split(/\r?\n|,/)
    .map((item) => item.trim())
    .filter(Boolean)
}

function formatListField(values: string[]): string {
  return values.join(', ')
}

function isSafeAssetUrl(value?: string | null): value is string {
  if (!value) return false
  const lowered = value.toLowerCase()
  const blockedFragments = [
    ['/', 'opt'].join(''),
    ['/', 'mnt'].join(''),
    `c:${String.fromCharCode(92)}`,
    ['storage', 'path'].join('_'),
    ['canonical', 'path'].join('_'),
  ]
  if (blockedFragments.some((fragment) => lowered.includes(fragment))) {
    return false
  }
  return value.startsWith('/api/')
}

function toDraft(entry?: CharacterBibleEntry | null, characterName = ''): CharacterBibleDraft {
  if (!entry) {
    return {
      ...EMPTY_DRAFT,
      characterId: slugifyCharacterId(characterName),
      characterName,
    }
  }

  return {
    characterId: entry.character_id,
    characterName: entry.character_name,
    visualDescription: entry.notes || '',
    wardrobe: entry.wardrobe_notes || '',
    hairMakeup: entry.hair_makeup_notes || '',
    associatedProps: formatListField(entry.key_props),
    negativeConstraints: formatListField(entry.negative_constraints),
  }
}

export function CharacterBiblePanel({ projectId, suggestedCharacters = [] }: CharacterBiblePanelProps) {
  const [entries, setEntries] = useState<CharacterBibleEntry[]>([])
  const [selectedCharacterId, setSelectedCharacterId] = useState('')
  const [draft, setDraft] = useState<CharacterBibleDraft>(EMPTY_DRAFT)
  const [lookVariant, setLookVariant] = useState<CharacterBibleLookVariantPayload>(EMPTY_LOOK_VARIANT)
  const [referencePayload, setReferencePayload] = useState<CharacterBibleReferencePayload>(EMPTY_REFERENCE)
  const [resolveResult, setResolveResult] = useState<CharacterBibleResolveResponse | null>(null)
  const [traceResult, setTraceResult] = useState<CharacterBibleTraceResponse | null>(null)
  const [availableAssets, setAvailableAssets] = useState<ProjectImageAssetItem[]>([])
  const [selectedAsset, setSelectedAsset] = useState<ProjectImageAssetItem | null>(null)
  const [assetsMeta, setAssetsMeta] = useState<ProjectImageAssetPaginationMeta | null>(null)
  const [isAssetSelectorOpen, setIsAssetSelectorOpen] = useState(false)
  const [isAssetsLoading, setIsAssetsLoading] = useState(false)
  const [assetsError, setAssetsError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [traceOpen, setTraceOpen] = useState(false)

  const suggestedOnlyCharacters = useMemo(
    () => suggestedCharacters.filter((name) => !entries.some((entry) => entry.character_name.toLowerCase() === name.toLowerCase())),
    [entries, suggestedCharacters]
  )

  const selectedEntry = useMemo(
    () => entries.find((entry) => entry.character_id === selectedCharacterId) || null,
    [entries, selectedCharacterId]
  )

  const selectedReferencePreview = useMemo(() => {
    if (selectedAsset) return selectedAsset
    if (!referencePayload.asset_id) return null

    return availableAssets.find((asset) => asset.asset_id === referencePayload.asset_id) || null
  }, [availableAssets, referencePayload.asset_id, selectedAsset])

  const hasPersistedEntry = Boolean(selectedEntry)

  const fetchAssets = async (page = 1) => {
    setIsAssetsLoading(true)
    setAssetsError(null)

    try {
      const response = await storyboardApi.getImageAssets(projectId, page, 12)
      setAvailableAssets(response.items)
      setAssetsMeta(response.meta)
      setSelectedAsset((current) => response.items.find((asset) => asset.asset_id === current?.asset_id) || current)
    } catch (loadError) {
      setAssetsError(parseApiError(loadError, 'No se pudieron cargar los assets del proyecto'))
    } finally {
      setIsAssetsLoading(false)
    }
  }

  const loadCharacterBible = async (preferredCharacterId?: string) => {
    setIsLoading(true)
    setError(null)

    try {
      const response: CharacterBibleListResponse = await characterBibleApi.getCharacterBible(projectId)
      setEntries(response.entries)

      const nextCharacterId = preferredCharacterId
        || response.entries.find((entry) => entry.character_id === selectedCharacterId)?.character_id
        || response.entries[0]?.character_id
        || ''

      setSelectedCharacterId(nextCharacterId)
      setDraft(toDraft(response.entries.find((entry) => entry.character_id === nextCharacterId) || null))
      setResolveResult(null)
      setTraceResult(null)
    } catch (loadError) {
      setError(parseApiError(loadError, 'No se pudo cargar Character Bible'))
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    void loadCharacterBible()
  }, [projectId])

  const handleSelectEntry = async (characterId: string, fallbackName = '') => {
    setSelectedCharacterId(characterId)
    setResolveResult(null)
    setTraceResult(null)
    setTraceOpen(false)
    setSuccess(null)
    setError(null)

    if (!characterId) {
      setDraft(toDraft(null, fallbackName))
      return
    }

    const cachedEntry = entries.find((entry) => entry.character_id === characterId)
    if (cachedEntry) {
      setDraft(toDraft(cachedEntry))
      return
    }

    try {
      const entry = await characterBibleApi.getCharacterBibleEntry(projectId, characterId)
      setDraft(toDraft(entry))
    } catch (loadError) {
      setError(parseApiError(loadError, 'No se pudo cargar el personaje'))
      setDraft(toDraft(null, fallbackName))
    }
  }

  const handleSaveCharacter = async () => {
    const normalizedCharacterId = draft.characterId.trim() || slugifyCharacterId(draft.characterName)
    if (!normalizedCharacterId || !draft.characterName.trim()) {
      setError('Completa el ID y el nombre del personaje antes de guardar')
      return
    }

    const payload: CharacterBibleUpsertPayload = {
      character_id: normalizedCharacterId,
      character_name: draft.characterName.trim(),
      wardrobe_notes: draft.wardrobe.trim() || null,
      hair_makeup_notes: draft.hairMakeup.trim() || null,
      key_props: parseListField(draft.associatedProps),
      continuity_rules: [],
      negative_constraints: parseListField(draft.negativeConstraints),
      notes: draft.visualDescription.trim() || null,
      approved_reference_asset_id: selectedEntry?.approved_reference_asset_id || null,
    }

    setIsSaving(true)
    setError(null)
    setSuccess(null)

    try {
      const saved = await characterBibleApi.upsertCharacterBibleEntry(projectId, normalizedCharacterId, payload)
      await loadCharacterBible(saved.character_id)
      setDraft(toDraft(saved))
      setSuccess('Personaje guardado correctamente')
    } catch (saveError) {
      setError(parseApiError(saveError, 'No se pudo guardar el personaje'))
    } finally {
      setIsSaving(false)
    }
  }

  const handleAddLookVariant = async () => {
    if (!selectedCharacterId || !lookVariant.look_id.trim() || !lookVariant.look_name.trim()) {
      setError('Selecciona un personaje y completa look_id y look_name')
      return
    }

    setIsSaving(true)
    setError(null)
    setSuccess(null)

    try {
      await characterBibleApi.addCharacterBibleLookVariant(projectId, selectedCharacterId, {
        ...lookVariant,
        look_id: lookVariant.look_id.trim(),
        look_name: lookVariant.look_name.trim(),
        narrative_phase: lookVariant.narrative_phase?.trim() || null,
      })
      setLookVariant(EMPTY_LOOK_VARIANT)
      await loadCharacterBible(selectedCharacterId)
      setSuccess('Variante añadida correctamente')
    } catch (saveError) {
      setError(parseApiError(saveError, 'No se pudo añadir la variante'))
    } finally {
      setIsSaving(false)
    }
  }

  const handleAddReference = async () => {
    if (!selectedCharacterId || !referencePayload.asset_id.trim()) {
      setError('Selecciona un personaje e introduce un MediaAsset ID válido')
      return
    }

    setIsSaving(true)
    setError(null)
    setSuccess(null)

    try {
      await characterBibleApi.addCharacterBibleReference(projectId, selectedCharacterId, {
        ...referencePayload,
        asset_id: referencePayload.asset_id.trim(),
        asset_file_name: selectedReferencePreview?.file_name || referencePayload.asset_file_name || null,
        description: referencePayload.description?.trim() || null,
        notes: referencePayload.notes?.trim() || null,
      })
      setReferencePayload(EMPTY_REFERENCE)
      setSelectedAsset(null)
      await loadCharacterBible(selectedCharacterId)
      setSuccess('Referencia vinculada correctamente')
    } catch (saveError) {
      setError(parseApiError(saveError, 'No se pudo vincular la referencia'))
    } finally {
      setIsSaving(false)
    }
  }

  const handleResolveCharacter = async () => {
    if (!selectedCharacterId) {
      setError('Selecciona un personaje antes de resolver continuidad')
      return
    }

    setIsSaving(true)
    setError(null)
    setSuccess(null)

    try {
      const result = await characterBibleApi.resolveCharacterBible(projectId, selectedCharacterId, {
        project_id: projectId,
        character_id: selectedCharacterId,
        look_id: lookVariant.look_id.trim() || null,
        narrative_phase: lookVariant.narrative_phase?.trim() || null,
        scene_id: null,
      })
      setResolveResult(result)
      setSuccess('Continuidad resuelta correctamente')
    } catch (resolveError) {
      setError(parseApiError(resolveError, 'No se pudo resolver continuidad'))
    } finally {
      setIsSaving(false)
    }
  }

  const handleLoadTrace = async () => {
    if (!selectedCharacterId) {
      setError('Selecciona un personaje antes de consultar trazabilidad')
      return
    }

    setTraceOpen(true)
    setIsSaving(true)
    setError(null)
    setSuccess(null)

    try {
      const trace = await characterBibleApi.getCharacterBibleTrace(projectId, selectedCharacterId)
      setTraceResult(trace)
    } catch (traceError) {
      setError(parseApiError(traceError, 'No se pudo cargar la trazabilidad'))
    } finally {
      setIsSaving(false)
    }
  }

  const handleToggleAssetSelector = async () => {
    const nextOpen = !isAssetSelectorOpen
    setIsAssetSelectorOpen(nextOpen)

    if (nextOpen && availableAssets.length === 0 && !isAssetsLoading) {
      await fetchAssets(1)
    }
  }

  const handleSelectAsset = (asset: ProjectImageAssetItem) => {
    setSelectedAsset(asset)
    setReferencePayload((current: CharacterBibleReferencePayload) => ({
      ...current,
      asset_id: asset.asset_id,
      asset_file_name: asset.file_name,
    }))
    setSuccess('Asset seleccionado. Puedes vincularlo como referencia aprobada.')
  }

  return (
    <section className="rounded-2xl border border-white/10 bg-dark-200/80 p-5 space-y-5">
      <div className="flex flex-col gap-2 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white">Character Bible</h3>
          <p className="text-sm text-slate-400">Control de continuidad visual de personajes, referencias aprobadas y variantes de look.</p>
        </div>
        <div className="rounded-xl border border-cyan-500/20 bg-cyan-500/5 px-4 py-3 text-xs text-cyan-100 max-w-xl">
          <p className="flex items-center gap-2 text-cyan-300 font-medium"><Shield className="w-3.5 h-3.5" /> Seguridad UI</p>
          <p className="mt-1 text-slate-300">Introduce un MediaAsset ID ya existente para vincular una referencia aprobada. CID solo guarda el identificador y la URL API segura, nunca rutas internas del sistema.</p>
        </div>
      </div>

      {error && <div className="rounded-xl border border-red-500/20 bg-red-500/5 px-4 py-3 text-sm text-red-300">{error}</div>}
      {success && <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 px-4 py-3 text-sm text-emerald-300 inline-flex items-center gap-2"><CheckCircle2 className="w-4 h-4" />{success}</div>}

      {isLoading ? (
        <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-black/20 px-4 py-6 text-sm text-slate-300">
          <Loader2 className="w-4 h-4 animate-spin text-amber-400" /> Cargando Character Bible...
        </div>
      ) : (
        <div className="grid gap-5 xl:grid-cols-[280px_minmax(0,1fr)]">
          <aside className="space-y-4">
            <div className="rounded-xl border border-white/10 bg-black/20 p-3 space-y-3">
              <div className="flex items-center justify-between">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Personajes</p>
                <span className="text-[11px] text-slate-500">{entries.length}</span>
              </div>
              {entries.length === 0 && suggestedOnlyCharacters.length === 0 ? (
                <div className="rounded-lg border border-dashed border-white/10 px-3 py-4 text-xs text-slate-500">
                  No hay personajes cargados todavia.
                </div>
              ) : (
                <div className="space-y-2">
                  {entries.map((entry) => (
                    <button
                      key={entry.character_id}
                      type="button"
                      onClick={() => void handleSelectEntry(entry.character_id)}
                      className={`w-full rounded-xl border px-3 py-2 text-left transition-colors ${selectedCharacterId === entry.character_id ? 'border-amber-400/40 bg-amber-500/10' : 'border-white/10 bg-dark-300/40 hover:border-white/20'}`}
                    >
                      <p className="text-sm font-medium text-white">{entry.character_name}</p>
                      <p className="mt-1 text-[11px] text-slate-500">{entry.character_id}</p>
                    </button>
                  ))}
                  {suggestedOnlyCharacters.map((name) => (
                    <button
                      key={name}
                      type="button"
                      onClick={() => void handleSelectEntry(slugifyCharacterId(name), name)}
                      className="w-full rounded-xl border border-dashed border-cyan-500/30 bg-cyan-500/5 px-3 py-2 text-left transition-colors hover:bg-cyan-500/10"
                    >
                      <p className="text-sm font-medium text-cyan-200">{name}</p>
                      <p className="mt-1 text-[11px] text-cyan-400/70">Sugerido por secuencias</p>
                    </button>
                  ))}
                </div>
              )}
              <button
                type="button"
                onClick={() => void handleSelectEntry('')}
                className="inline-flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-xs text-slate-200 hover:bg-white/5"
              >
                <Plus className="w-3.5 h-3.5" /> Nuevo personaje
              </button>
            </div>
          </aside>

          <div className="space-y-5">
            <div className="grid gap-4 md:grid-cols-2">
              <label className="space-y-2">
                <span className="text-xs font-medium text-slate-300">Character ID</span>
                <input
                  value={draft.characterId}
                  onChange={(event) => setDraft((current) => ({ ...current, characterId: event.target.value }))}
                  placeholder="protagonist-01"
                  className="w-full rounded-xl border border-white/10 bg-dark-300/60 px-3 py-2 text-sm text-white outline-none"
                />
              </label>
              <label className="space-y-2">
                <span className="text-xs font-medium text-slate-300">Nombre del personaje</span>
                <input
                  value={draft.characterName}
                  onChange={(event) => setDraft((current) => ({ ...current, characterName: event.target.value }))}
                  placeholder="Lucia"
                  className="w-full rounded-xl border border-white/10 bg-dark-300/60 px-3 py-2 text-sm text-white outline-none"
                />
              </label>
              <label className="space-y-2 md:col-span-2">
                <span className="text-xs font-medium text-slate-300">Visual description</span>
                <textarea
                  value={draft.visualDescription}
                  onChange={(event) => setDraft((current) => ({ ...current, visualDescription: event.target.value }))}
                  rows={3}
                  className="w-full rounded-xl border border-white/10 bg-dark-300/60 px-3 py-2 text-sm text-white outline-none"
                />
              </label>
              <label className="space-y-2">
                <span className="text-xs font-medium text-slate-300">Wardrobe</span>
                <textarea
                  value={draft.wardrobe}
                  onChange={(event) => setDraft((current) => ({ ...current, wardrobe: event.target.value }))}
                  rows={3}
                  className="w-full rounded-xl border border-white/10 bg-dark-300/60 px-3 py-2 text-sm text-white outline-none"
                />
              </label>
              <label className="space-y-2">
                <span className="text-xs font-medium text-slate-300">Hair & makeup</span>
                <textarea
                  value={draft.hairMakeup}
                  onChange={(event) => setDraft((current) => ({ ...current, hairMakeup: event.target.value }))}
                  rows={3}
                  className="w-full rounded-xl border border-white/10 bg-dark-300/60 px-3 py-2 text-sm text-white outline-none"
                />
              </label>
              <label className="space-y-2">
                <span className="text-xs font-medium text-slate-300">Associated props</span>
                <textarea
                  value={draft.associatedProps}
                  onChange={(event) => setDraft((current) => ({ ...current, associatedProps: event.target.value }))}
                  rows={3}
                  placeholder="camera, ring, notebook"
                  className="w-full rounded-xl border border-white/10 bg-dark-300/60 px-3 py-2 text-sm text-white outline-none"
                />
              </label>
              <label className="space-y-2">
                <span className="text-xs font-medium text-slate-300">Negative constraints</span>
                <textarea
                  value={draft.negativeConstraints}
                  onChange={(event) => setDraft((current) => ({ ...current, negativeConstraints: event.target.value }))}
                  rows={3}
                  placeholder="no helmet, no backpack"
                  className="w-full rounded-xl border border-white/10 bg-dark-300/60 px-3 py-2 text-sm text-white outline-none"
                />
              </label>
            </div>

            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => void handleSaveCharacter()}
                disabled={isSaving}
                className="inline-flex items-center gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-2 text-sm font-medium text-amber-300 hover:bg-amber-500/20 disabled:opacity-40"
              >
                {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />} Guardar personaje
              </button>
              <button
                type="button"
                onClick={() => void handleResolveCharacter()}
                disabled={isSaving || !hasPersistedEntry}
                className="inline-flex items-center gap-2 rounded-xl border border-cyan-500/30 bg-cyan-500/10 px-4 py-2 text-sm font-medium text-cyan-300 hover:bg-cyan-500/20 disabled:opacity-40"
              >
                <Sparkles className="w-4 h-4" /> Resolver continuidad
              </button>
              <button
                type="button"
                onClick={() => void handleLoadTrace()}
                disabled={isSaving || !hasPersistedEntry}
                className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-white/10 disabled:opacity-40"
              >
                <GitBranch className="w-4 h-4" /> Ver trazabilidad
              </button>
            </div>

            <div className="grid gap-5 xl:grid-cols-2">
              <section className="rounded-xl border border-white/10 bg-black/20 p-4 space-y-3">
                <div className="flex items-center gap-2 text-white"><UserRound className="w-4 h-4 text-cyan-400" /> <h4 className="font-medium">Variantes de look</h4></div>
                <div className="grid gap-3 md:grid-cols-2">
                  <input value={lookVariant.look_id} onChange={(event) => setLookVariant((current: CharacterBibleLookVariantPayload) => ({ ...current, look_id: event.target.value }))} placeholder="look-night-exterior" className="rounded-xl border border-white/10 bg-dark-300/60 px-3 py-2 text-sm text-white outline-none" />
                  <input value={lookVariant.look_name} onChange={(event) => setLookVariant((current: CharacterBibleLookVariantPayload) => ({ ...current, look_name: event.target.value }))} placeholder="Night exterior" className="rounded-xl border border-white/10 bg-dark-300/60 px-3 py-2 text-sm text-white outline-none" />
                  <input value={lookVariant.narrative_phase || ''} onChange={(event) => setLookVariant((current: CharacterBibleLookVariantPayload) => ({ ...current, narrative_phase: event.target.value }))} placeholder="Acto 2" className="rounded-xl border border-white/10 bg-dark-300/60 px-3 py-2 text-sm text-white outline-none md:col-span-2" />
                </div>
                <button type="button" onClick={() => void handleAddLookVariant()} disabled={isSaving || !hasPersistedEntry} className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200 hover:bg-white/10 disabled:opacity-40">
                  <Plus className="w-4 h-4" /> Añadir variante
                </button>
                {selectedEntry?.look_variants.length ? (
                  <div className="space-y-2">
                    {selectedEntry.look_variants.map((variant) => (
                      <div key={variant.look_id} className="rounded-lg border border-white/10 bg-dark-300/40 px-3 py-2 text-sm text-slate-300">
                        <p className="font-medium text-white">{variant.look_name}</p>
                        <p className="text-xs text-slate-500">{variant.look_id}{variant.narrative_phase ? ` · ${variant.narrative_phase}` : ''}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-500">Todavia no hay variantes cargadas.</p>
                )}
              </section>

              <section className="rounded-xl border border-white/10 bg-black/20 p-4 space-y-3">
                <div className="flex items-center gap-2 text-white"><Link2 className="w-4 h-4 text-amber-400" /> <h4 className="font-medium">Referencias aprobadas</h4></div>
                <div className="grid gap-3 md:grid-cols-2">
                  <input value={referencePayload.asset_id} onChange={(event) => setReferencePayload((current: CharacterBibleReferencePayload) => ({ ...current, asset_id: event.target.value }))} placeholder="MediaAsset ID" className="rounded-xl border border-white/10 bg-dark-300/60 px-3 py-2 text-sm text-white outline-none" />
                  <select value={referencePayload.asset_type} onChange={(event) => setReferencePayload((current: CharacterBibleReferencePayload) => ({ ...current, asset_type: event.target.value as CharacterBibleApprovedAssetType }))} className="rounded-xl border border-white/10 bg-dark-300/60 px-3 py-2 text-sm text-white outline-none">
                    {APPROVED_ASSET_TYPES.map((assetType) => (
                      <option key={assetType} value={assetType}>{assetType}</option>
                    ))}
                  </select>
                  <input value={referencePayload.description || ''} onChange={(event) => setReferencePayload((current: CharacterBibleReferencePayload) => ({ ...current, description: event.target.value }))} placeholder="Descripcion opcional" className="rounded-xl border border-white/10 bg-dark-300/60 px-3 py-2 text-sm text-white outline-none md:col-span-2" />
                </div>
                <label className="inline-flex items-center gap-2 text-xs text-slate-300">
                  <input type="checkbox" checked={referencePayload.is_primary} onChange={(event) => setReferencePayload((current: CharacterBibleReferencePayload) => ({ ...current, is_primary: event.target.checked }))} /> Referencia principal
                </label>
                <div className="flex flex-wrap gap-3">
                  <button type="button" onClick={() => void handleAddReference()} disabled={isSaving || !hasPersistedEntry} className="inline-flex items-center gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-2 text-sm font-medium text-amber-300 hover:bg-amber-500/20 disabled:opacity-40">
                    <Link2 className="w-4 h-4" /> Vincular referencia
                  </button>
                  <button type="button" onClick={() => void handleToggleAssetSelector()} disabled={isSaving} className="inline-flex items-center gap-2 rounded-xl border border-cyan-500/30 bg-cyan-500/10 px-4 py-2 text-sm font-medium text-cyan-300 hover:bg-cyan-500/20 disabled:opacity-40">
                    <Image className="w-4 h-4" /> Seleccionar asset existente
                  </button>
                </div>

                {selectedReferencePreview && (
                  <div className="rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-3 text-sm text-slate-200">
                    <p className="font-medium text-white">Asset seleccionado</p>
                    <div className="mt-3 flex flex-wrap gap-3">
                      {isSafeAssetUrl(selectedReferencePreview.thumbnail_url) && (
                        <img
                          src={selectedReferencePreview.thumbnail_url}
                          alt={selectedReferencePreview.file_name}
                          className="h-20 w-20 rounded-lg border border-white/10 object-cover"
                          loading="lazy"
                        />
                      )}
                      <div className="space-y-1 text-xs text-slate-400">
                        <p>file_name: {selectedReferencePreview.file_name}</p>
                        <p>asset_id: {selectedReferencePreview.asset_id}</p>
                        {isSafeAssetUrl(selectedReferencePreview.preview_url) && (
                          <a href={selectedReferencePreview.preview_url} target="_blank" rel="noreferrer" className="inline-flex text-cyan-300 hover:text-cyan-200">
                            {selectedReferencePreview.preview_url}
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {isAssetSelectorOpen && (
                  <div className="rounded-xl border border-white/10 bg-dark-300/40 p-4 space-y-4">
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <p className="text-sm font-medium text-white">Assets existentes del proyecto</p>
                        <p className="text-xs text-slate-400">Selecciona un asset visual ya disponible en el proyecto o usa el campo manual de MediaAsset ID.</p>
                      </div>
                      <button type="button" onClick={() => void fetchAssets(assetsMeta?.page || 1)} className="inline-flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-xs text-slate-200 hover:bg-white/5">
                        {isAssetsLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Image className="w-3.5 h-3.5" />} Recargar assets
                      </button>
                    </div>

                    {assetsError && (
                      <div className="rounded-lg border border-red-500/20 bg-red-500/5 px-3 py-2 text-xs text-red-300">
                        {assetsError}
                      </div>
                    )}

                    {isAssetsLoading ? (
                      <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-black/20 px-3 py-6 text-sm text-slate-300">
                        <Loader2 className="w-4 h-4 animate-spin text-amber-400" /> Cargando assets...
                      </div>
                    ) : availableAssets.length === 0 ? (
                      <div className="rounded-lg border border-dashed border-white/10 px-3 py-6 text-sm text-slate-500">
                        Empty assets: no hay assets visuales disponibles en este proyecto. Puedes seguir vinculando referencias mediante MediaAsset ID manual.
                      </div>
                    ) : (
                      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                        {availableAssets.map((asset) => {
                          const safeThumbnailUrl = isSafeAssetUrl(asset.thumbnail_url) ? asset.thumbnail_url : null
                          const safePreviewUrl = isSafeAssetUrl(asset.preview_url) ? asset.preview_url : null
                          const isSelected = referencePayload.asset_id === asset.asset_id

                          return (
                            <button
                              key={asset.asset_id}
                              type="button"
                              onClick={() => handleSelectAsset(asset)}
                              className={`rounded-xl border p-3 text-left transition-colors ${isSelected ? 'border-amber-400/40 bg-amber-500/10' : 'border-white/10 bg-black/20 hover:border-white/20'}`}
                            >
                              <div className="flex gap-3">
                                <div className="h-20 w-20 shrink-0 overflow-hidden rounded-lg border border-white/10 bg-black/20">
                                  {safeThumbnailUrl ? (
                                    <img src={safeThumbnailUrl} alt={asset.file_name} className="h-full w-full object-cover" loading="lazy" />
                                  ) : (
                                    <div className="flex h-full w-full items-center justify-center text-slate-500">
                                      <Image className="w-5 h-5" />
                                    </div>
                                  )}
                                </div>
                                <div className="min-w-0 flex-1">
                                  <p className="truncate text-sm font-medium text-white">{asset.file_name}</p>
                                  <p className="mt-1 truncate text-[11px] text-slate-500">{asset.asset_id}</p>
                                  <p className="mt-2 text-[11px] text-slate-400">{safePreviewUrl ? 'Preview segura disponible' : 'Sin preview segura'}</p>
                                  <span className="mt-2 inline-flex rounded-lg border border-cyan-500/20 bg-cyan-500/10 px-2 py-1 text-[11px] text-cyan-300">
                                    Usar como referencia
                                  </span>
                                </div>
                              </div>
                            </button>
                          )
                        })}
                      </div>
                    )}

                    {assetsMeta && assetsMeta.total_pages > 1 && (
                      <div className="flex items-center justify-between rounded-lg border border-white/10 bg-black/20 px-3 py-2 text-xs text-slate-400">
                        <span>Pagina {assetsMeta.page} de {assetsMeta.total_pages} ({assetsMeta.total_items} assets)</span>
                        <div className="flex gap-2">
                          <button type="button" onClick={() => void fetchAssets(assetsMeta.page - 1)} disabled={!assetsMeta.has_prev || isAssetsLoading} className="rounded-lg border border-white/10 px-2 py-1 text-slate-200 hover:bg-white/5 disabled:opacity-40">
                            <ChevronLeft className="w-3.5 h-3.5" />
                          </button>
                          <button type="button" onClick={() => void fetchAssets(assetsMeta.page + 1)} disabled={!assetsMeta.has_next || isAssetsLoading} className="rounded-lg border border-white/10 px-2 py-1 text-slate-200 hover:bg-white/5 disabled:opacity-40">
                            <ChevronRight className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {selectedEntry?.approved_references.length ? (
                  <div className="space-y-2">
                    {selectedEntry.approved_references.map((reference) => (
                      <div key={`${reference.asset_id}-${reference.reference_id || reference.sort_order}`} className="rounded-lg border border-white/10 bg-dark-300/40 p-3 text-sm text-slate-300">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="font-medium text-white">{reference.asset_file_name || reference.asset_id}</span>
                          <span className="rounded bg-white/5 px-2 py-0.5 text-[10px] text-slate-400">{reference.asset_type}</span>
                          {reference.is_primary && <span className="rounded bg-amber-500/10 px-2 py-0.5 text-[10px] text-amber-300">Primary</span>}
                        </div>
                        <p className="mt-1 text-xs text-slate-500">asset_id: {reference.asset_id}</p>
                        {reference.description && <p className="mt-1 text-xs text-slate-400">{reference.description}</p>}
                        {reference.thumbnail_url && isSafeAssetUrl(reference.thumbnail_url) && (
                          <div className="mt-2 flex flex-wrap items-center gap-3">
                            <img src={reference.thumbnail_url} alt={reference.asset_file_name || reference.asset_id} className="h-16 w-16 rounded-lg border border-white/10 object-cover" loading="lazy" />
                            <a href={reference.thumbnail_url} target="_blank" rel="noreferrer" className="inline-flex text-xs text-cyan-300 hover:text-cyan-200">thumbnail_url</a>
                          </div>
                        )}
                        {!reference.thumbnail_url && isSafeAssetUrl(reference.asset_api_url) && (
                          <a href={reference.asset_api_url} target="_blank" rel="noreferrer" className="mt-2 inline-flex text-xs text-cyan-300 hover:text-cyan-200">{reference.asset_api_url}</a>
                        )}
                        {!reference.thumbnail_url && !isSafeAssetUrl(reference.asset_api_url) && <p className="mt-2 text-xs text-slate-500">asset_id fallback: {reference.asset_id}</p>}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-500">Todavia no hay referencias aprobadas.</p>
                )}
              </section>
            </div>

            {resolveResult && (
              <section className="rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-4 space-y-2 text-sm text-slate-200">
                <h4 className="font-medium text-cyan-300">Resolucion de continuidad</h4>
                <p><span className="text-slate-400">Personaje:</span> {resolveResult.character_name}</p>
                <p><span className="text-slate-400">Look resuelto:</span> {resolveResult.resolved_look?.look_name || 'No disponible'}</p>
                <p><span className="text-slate-400">Referencia primaria:</span> {resolveResult.primary_reference?.asset_id || 'No disponible'}</p>
                {resolveResult.prompt_lock_block && <p><span className="text-slate-400">Prompt lock:</span> {resolveResult.prompt_lock_block}</p>}
                {resolveResult.prompt_negative_block && <p><span className="text-slate-400">Negative block:</span> {resolveResult.prompt_negative_block}</p>}
                {resolveResult.continuity_block && <p><span className="text-slate-400">Continuity block:</span> {resolveResult.continuity_block}</p>}
              </section>
            )}

            {traceOpen && (
              <section className="rounded-xl border border-white/10 bg-black/20 p-4 space-y-2 text-sm text-slate-200">
                <h4 className="font-medium text-white">Trazabilidad</h4>
                {traceResult ? (
                  Object.entries(traceResult.trace_metadata).length > 0 ? (
                    <pre className="max-h-64 overflow-auto rounded-lg border border-white/10 bg-black/30 p-3 text-xs text-slate-400">{JSON.stringify(traceResult.trace_metadata, null, 2)}</pre>
                  ) : (
                    <p className="text-xs text-slate-500">No hay metadata de trazabilidad para este personaje.</p>
                  )
                ) : (
                  <p className="text-xs text-slate-500">Trazabilidad no disponible.</p>
                )}
              </section>
            )}
          </div>
        </div>
      )}
    </section>
  )
}
