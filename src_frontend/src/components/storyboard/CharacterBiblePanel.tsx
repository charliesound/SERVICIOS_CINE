import { useEffect, useMemo, useState } from 'react'
import { CheckCircle2, GitBranch, Link2, Loader2, Plus, Save, Shield, Sparkles, UserRound } from 'lucide-react'
import { characterBibleApi } from '@/api/characterBible'
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
  'wardrobe_sheet',
  'full_body',
  'hair_makeup',
  'prop_reference',
  'expression_sheet',
  'pose_sheet',
  'action_still',
  'mood_board',
  'concept_art',
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
  if (lowered.includes('/opt') || lowered.includes('/mnt') || lowered.includes('c:\\') || lowered.includes('storage_path') || lowered.includes('canonical_path')) {
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

  const hasPersistedEntry = Boolean(selectedEntry)

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
        description: referencePayload.description?.trim() || null,
        notes: referencePayload.notes?.trim() || null,
      })
      setReferencePayload(EMPTY_REFERENCE)
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
                  <input value={lookVariant.look_id} onChange={(event) => setLookVariant((current) => ({ ...current, look_id: event.target.value }))} placeholder="look-night-exterior" className="rounded-xl border border-white/10 bg-dark-300/60 px-3 py-2 text-sm text-white outline-none" />
                  <input value={lookVariant.look_name} onChange={(event) => setLookVariant((current) => ({ ...current, look_name: event.target.value }))} placeholder="Night exterior" className="rounded-xl border border-white/10 bg-dark-300/60 px-3 py-2 text-sm text-white outline-none" />
                  <input value={lookVariant.narrative_phase || ''} onChange={(event) => setLookVariant((current) => ({ ...current, narrative_phase: event.target.value }))} placeholder="Acto 2" className="rounded-xl border border-white/10 bg-dark-300/60 px-3 py-2 text-sm text-white outline-none md:col-span-2" />
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
                  <input value={referencePayload.asset_id} onChange={(event) => setReferencePayload((current) => ({ ...current, asset_id: event.target.value }))} placeholder="MediaAsset ID" className="rounded-xl border border-white/10 bg-dark-300/60 px-3 py-2 text-sm text-white outline-none" />
                  <select value={referencePayload.asset_type} onChange={(event) => setReferencePayload((current) => ({ ...current, asset_type: event.target.value as CharacterBibleApprovedAssetType }))} className="rounded-xl border border-white/10 bg-dark-300/60 px-3 py-2 text-sm text-white outline-none">
                    {APPROVED_ASSET_TYPES.map((assetType) => (
                      <option key={assetType} value={assetType}>{assetType}</option>
                    ))}
                  </select>
                  <input value={referencePayload.description || ''} onChange={(event) => setReferencePayload((current) => ({ ...current, description: event.target.value }))} placeholder="Descripcion opcional" className="rounded-xl border border-white/10 bg-dark-300/60 px-3 py-2 text-sm text-white outline-none md:col-span-2" />
                </div>
                <label className="inline-flex items-center gap-2 text-xs text-slate-300">
                  <input type="checkbox" checked={referencePayload.is_primary} onChange={(event) => setReferencePayload((current) => ({ ...current, is_primary: event.target.checked }))} /> Referencia principal
                </label>
                <button type="button" onClick={() => void handleAddReference()} disabled={isSaving || !hasPersistedEntry} className="inline-flex items-center gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-2 text-sm font-medium text-amber-300 hover:bg-amber-500/20 disabled:opacity-40">
                  <Link2 className="w-4 h-4" /> Vincular referencia
                </button>
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
                          <a href={reference.thumbnail_url} target="_blank" rel="noreferrer" className="mt-2 inline-flex text-xs text-cyan-300 hover:text-cyan-200">thumbnail_url</a>
                        )}
                        {isSafeAssetUrl(reference.asset_api_url) && (
                          <a href={reference.asset_api_url} target="_blank" rel="noreferrer" className="mt-2 inline-flex text-xs text-cyan-300 hover:text-cyan-200">{reference.asset_api_url}</a>
                        )}
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
