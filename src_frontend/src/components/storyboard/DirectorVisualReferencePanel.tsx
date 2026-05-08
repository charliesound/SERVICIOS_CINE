import { useState } from 'react'
import { Sparkles, Upload, Eye, Image, Palette, Lightbulb, Camera, LayoutGrid, AlignStartHorizontal, AlertTriangle, CheckCircle2, FileText } from 'lucide-react'

type ReferencePurpose =
  | 'global_project_style'
  | 'scene_mood'
  | 'character_visual_reference'
  | 'location_reference'
  | 'lighting_reference'
  | 'color_palette_reference'
  | 'composition_reference'
  | 'storyboard_reference'

type ReferenceIntensity = 'low' | 'medium' | 'high'

type ReferenceMode = 'mood_only' | 'palette_lighting' | 'composition_guidance' | 'full_art_direction'

interface StyleReferenceProfile {
  reference_id: string
  visual_summary: string
  palette_description: string
  lighting_description: string
  atmosphere_description: string
  composition_description: string
  transferable_traits: string[]
  non_transferable_traits: string[]
  prompt_modifiers: string[]
  qa_requirements: string[]
}

interface DirectorVisualReferencePanelProps {
  onApplyReference: (profileId: string, mode: string) => void
  projectId?: string
}

const PURPOSE_OPTIONS: { value: ReferencePurpose; label: string }[] = [
  { value: 'global_project_style', label: 'Estilo global del proyecto' },
  { value: 'scene_mood', label: 'Atmósfera de escena' },
  { value: 'character_visual_reference', label: 'Referencia visual de personaje' },
  { value: 'location_reference', label: 'Referencia de localización' },
  { value: 'lighting_reference', label: 'Referencia de iluminación' },
  { value: 'color_palette_reference', label: 'Referencia de paleta de color' },
  { value: 'composition_reference', label: 'Referencia de composición' },
  { value: 'storyboard_reference', label: 'Referencia de storyboard' },
]

const MODE_OPTIONS: { value: ReferenceMode; label: string; description: string }[] = [
  { value: 'mood_only', label: 'Solo atmósfera', description: 'Transfiere solo el ambiente y la sensación visual' },
  { value: 'palette_lighting', label: 'Paleta y luz', description: 'Transfiere color e iluminación' },
  { value: 'composition_guidance', label: 'Guía de composición', description: 'Transfiere encuadre y composición' },
  { value: 'full_art_direction', label: 'Dirección artística completa', description: 'Transfiere todos los aspectos visuales' },
]

export default function DirectorVisualReferencePanel({
  onApplyReference,
  projectId,
}: DirectorVisualReferencePanelProps) {
  const [referenceUrl, setReferenceUrl] = useState('')
  const [purpose, setPurpose] = useState<ReferencePurpose>('scene_mood')
  const [intensity, setIntensity] = useState<ReferenceIntensity>('medium')
  const [mode, setMode] = useState<ReferenceMode>('palette_lighting')
  const [directorNotes, setDirectorNotes] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [profile, setProfile] = useState<StyleReferenceProfile | null>(null)
  const [error, setError] = useState('')
  const [scriptExcerpt, setScriptExcerpt] = useState('')
  const [isAligning, setIsAligning] = useState(false)
  const [alignmentResult, setAlignmentResult] = useState<{
    alignment_score: number
    matching_elements: string[]
    tension_points: string[]
    recommended_prompt_guidance: string
    safe_constraints: string[]
    warnings: string[]
  } | null>(null)
  const [enrichedIntent, setEnrichedIntent] = useState<string>('')

  const handleAnalyze = async () => {
    setIsAnalyzing(true)
    setError('')
    setProfile(null)

    try {
      const response = await fetch('/api/cid/visual-reference/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId || null,
          reference_image_url: referenceUrl || null,
          reference_purpose: purpose,
          intensity: intensity,
          reference_mode: mode,
          notes_from_director: directorNotes || null,
          allow_composition_transfer: mode === 'composition_guidance' || mode === 'full_art_direction',
          allow_palette_transfer: mode === 'palette_lighting' || mode === 'full_art_direction',
          allow_lighting_transfer: mode === 'palette_lighting' || mode === 'full_art_direction',
          allow_texture_transfer: mode === 'full_art_direction',
          forbid_identity_copy: true,
        }),
      })
      if (!response.ok) throw new Error('Analysis failed')
      const result = await response.json()
      setProfile(result.profile)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleApply = () => {
    if (profile) {
      onApplyReference(profile.reference_id, mode)
    }
  }

  const handleAlignWithScript = async () => {
    if (!profile || !scriptExcerpt.trim()) return
    setIsAligning(true)
    setAlignmentResult(null)
    setEnrichedIntent('')
    try {
      const response = await fetch('/api/cid/visual-reference/align-with-script', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          script_excerpt: scriptExcerpt,
          reference_profile: profile,
        }),
      })
      if (!response.ok) throw new Error('Alignment failed')
      const result = await response.json()
      setAlignmentResult(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Alignment error')
    }
    try {
      const enrichedResp = await fetch('/api/cid/visual-reference/enriched-intent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          script_excerpt: scriptExcerpt,
          reference_profile: profile,
        }),
      })
      if (enrichedResp.ok) {
        const enriched = await enrichedResp.json()
        setEnrichedIntent(enriched.merged_intent_summary || '')
      }
    } catch {
    }
    setIsAligning(false)
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-[#0e1419] p-6 space-y-6">
      <div className="flex items-center gap-3">
        <div className="rounded-xl bg-amber-400/10 p-2.5">
          <Eye className="h-5 w-5 text-amber-400" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">Referencia visual del director</h3>
          <p className="text-sm text-slate-400">
            Sube una imagen de referencia para guiar el estilo visual de las generaciones
          </p>
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1.5">
            <Upload className="inline h-3.5 w-3.5 mr-1.5" />
            Imagen de referencia (URL o asset ID)
          </label>
          <input
            type="text"
            value={referenceUrl}
            onChange={(e) => setReferenceUrl(e.target.value)}
            placeholder="https://ejemplo.com/referencia.webp o asset_id"
            className="w-full rounded-xl border border-white/10 bg-[#0a1016] px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:border-amber-500/50 focus:outline-none"
          />
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">
              <Image className="inline h-3.5 w-3.5 mr-1.5" />
              Propósito de la referencia
            </label>
            <select
              value={purpose}
              onChange={(e) => setPurpose(e.target.value as ReferencePurpose)}
              className="w-full rounded-xl border border-white/10 bg-[#0a1016] px-4 py-2.5 text-sm text-white focus:border-amber-500/50 focus:outline-none"
            >
              {PURPOSE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">
              <Lightbulb className="inline h-3.5 w-3.5 mr-1.5" />
              Intensidad
            </label>
            <div className="flex gap-2">
              {(['low', 'medium', 'high'] as ReferenceIntensity[]).map((level) => (
                <button
                  key={level}
                  onClick={() => setIntensity(level)}
                  className={`flex-1 rounded-xl border px-3 py-2 text-xs font-medium transition-all ${
                    intensity === level
                      ? 'border-amber-500/50 bg-amber-400/10 text-amber-300'
                      : 'border-white/10 bg-[#0a1016] text-slate-400 hover:border-white/20'
                  }`}
                >
                  {level === 'low' ? 'Suave' : level === 'medium' ? 'Media' : 'Fuerte'}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1.5">
            <LayoutGrid className="inline h-3.5 w-3.5 mr-1.5" />
            Modo de referencia
          </label>
          <div className="grid grid-cols-2 gap-2">
            {MODE_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setMode(opt.value)}
                className={`rounded-xl border p-3 text-left transition-all ${
                  mode === opt.value
                    ? 'border-amber-500/50 bg-amber-400/10'
                    : 'border-white/10 bg-[#0a1016] hover:border-white/20'
                }`}
              >
                <div className="flex items-center gap-2">
                  {opt.value === 'mood_only' && <Eye className="h-3.5 w-3.5 text-amber-400" />}
                  {opt.value === 'palette_lighting' && <Palette className="h-3.5 w-3.5 text-amber-400" />}
                  {opt.value === 'composition_guidance' && <Camera className="h-3.5 w-3.5 text-amber-400" />}
                  {opt.value === 'full_art_direction' && <Sparkles className="h-3.5 w-3.5 text-amber-400" />}
                  <span className="text-sm font-medium text-white">{opt.label}</span>
                </div>
                <p className="mt-1 text-xs text-slate-400">{opt.description}</p>
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1.5">Notas del director</label>
          <textarea
            value={directorNotes}
            onChange={(e) => setDirectorNotes(e.target.value)}
            placeholder='Ej: "Quiero que esta escena tenga una luz suave como la del参考, pero con colores más cálidos"'
            rows={2}
            className="w-full rounded-xl border border-white/10 bg-[#0a1016] px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:border-amber-500/50 focus:outline-none resize-none"
          />
        </div>

        <button
          onClick={handleAnalyze}
          disabled={isAnalyzing || !referenceUrl}
          className="w-full rounded-xl bg-amber-500/20 border border-amber-500/30 px-4 py-3 text-sm font-medium text-amber-300 hover:bg-amber-500/30 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {isAnalyzing ? 'Analizando referencia visual...' : 'Analizar referencia visual'}
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {profile && (
        <div className="space-y-3 rounded-xl border border-white/10 bg-[#0a1016] p-4">
          <h4 className="text-sm font-semibold text-amber-300">Perfil de estilo extraído</h4>
          <div className="space-y-2 text-sm text-slate-300">
            <p><span className="text-slate-400">Resumen:</span> {profile.visual_summary}</p>
            <p><span className="text-slate-400">Paleta:</span> {profile.palette_description}</p>
            <p><span className="text-slate-400">Iluminación:</span> {profile.lighting_description}</p>
            <p><span className="text-slate-400">Atmósfera:</span> {profile.atmosphere_description}</p>
          </div>
          {profile.transferable_traits.length > 0 && (
            <div>
              <p className="text-xs font-medium text-slate-400 mb-1">Rasgos transferibles:</p>
              <ul className="list-inside list-disc text-xs text-slate-500">
                {profile.transferable_traits.map((trait, i) => (
                  <li key={i}>{trait}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="border-t border-white/10 pt-4 mt-4">
            <h4 className="text-sm font-semibold text-amber-300 mb-3 flex items-center gap-2">
              <AlignStartHorizontal className="h-4 w-4" />
              Cotejo con el guion
            </h4>
            <textarea
              value={scriptExcerpt}
              onChange={(e) => setScriptExcerpt(e.target.value)}
              placeholder="Pega aquí el texto de la escena del guion para cotejarlo con la referencia visual..."
              rows={3}
              className="w-full rounded-xl border border-white/10 bg-[#0a1016] px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:border-amber-500/50 focus:outline-none resize-none mb-3"
            />
            <button
              onClick={handleAlignWithScript}
              disabled={isAligning || !scriptExcerpt.trim()}
              className="w-full rounded-xl border border-cyan-500/30 bg-cyan-500/10 px-4 py-2.5 text-sm font-medium text-cyan-300 hover:bg-cyan-500/20 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <FileText className="h-4 w-4" />
              {isAligning ? 'Cotejando con el guion...' : 'Cotejar con el guion'}
            </button>
            {alignmentResult && (
              <div className="mt-3 space-y-3 rounded-xl border border-white/10 bg-[#0a1016] p-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-400">Score de alineación</span>
                  <span className={`text-sm font-bold ${
                    alignmentResult.alignment_score >= 0.7 ? 'text-green-400' :
                    alignmentResult.alignment_score >= 0.4 ? 'text-amber-400' : 'text-red-400'
                  }`}>
                    {(alignmentResult.alignment_score * 100).toFixed(0)}%
                  </span>
                </div>
                {alignmentResult.matching_elements.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-green-400/80 mb-1 flex items-center gap-1">
                      <CheckCircle2 className="h-3 w-3" /> Coincidencias
                    </p>
                    <ul className="list-inside list-disc text-xs text-slate-400 space-y-0.5">
                      {alignmentResult.matching_elements.map((m, i) => (
                        <li key={i}>{m}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {alignmentResult.tension_points.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-amber-400/80 mb-1 flex items-center gap-1">
                      <AlertTriangle className="h-3 w-3" /> Tensiones detectadas
                    </p>
                    <ul className="list-inside list-disc text-xs text-slate-400 space-y-0.5">
                      {alignmentResult.tension_points.map((t, i) => (
                        <li key={i}>{t}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {alignmentResult.warnings.length > 0 && (
                  <div className="text-xs text-amber-400/70">
                    {alignmentResult.warnings.map((w, i) => (
                      <p key={i}>{w}</p>
                    ))}
                  </div>
                )}
                {enrichedIntent && (
                  <div className="border-t border-white/10 pt-2">
                    <p className="text-xs font-medium text-cyan-400/80 mb-1">Intención enriquecida</p>
                    <p className="text-xs text-slate-400">{enrichedIntent}</p>
                  </div>
                )}
              </div>
            )}
          </div>

          <button
            onClick={handleApply}
            className="w-full rounded-xl bg-amber-500/20 border border-amber-500/30 px-4 py-2.5 text-sm font-medium text-amber-300 hover:bg-amber-500/30 transition-all"
          >
            Usar esta referencia en storyboard
          </button>
        </div>
      )}
    </div>
  )
}
