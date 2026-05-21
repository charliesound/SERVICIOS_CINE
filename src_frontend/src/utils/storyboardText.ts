type StoryboardMetadata = Record<string, unknown> | null | undefined

const TECHNICAL_PATTERNS = [
  'cinematic storyboard frame',
  'model family',
  'positive prompt',
  'negative prompt',
  'prompt:',
  'comfyui',
  'workflow',
  'stable identity',
  'no watermark',
  'no text',
]

function cleanVisibleText(value: unknown): string | null {
  if (typeof value !== 'string') return null
  const normalized = value.replace(/\s+/g, ' ').trim()
  if (!normalized) return null
  const lower = normalized.toLowerCase()
  if (TECHNICAL_PATTERNS.some((pattern) => lower.includes(pattern))) {
    return null
  }
  return normalized
}

function fromMetadata(metadata: StoryboardMetadata, key: string): string | null {
  if (!metadata || typeof metadata !== 'object') return null
  return cleanVisibleText(metadata[key])
}

export function getStoryboardUiLocale(): string {
  if (typeof document !== 'undefined' && document.documentElement.lang) {
    return document.documentElement.lang
  }
  if (typeof navigator !== 'undefined' && navigator.language) {
    return navigator.language
  }
  return 'es'
}

export function getStoryboardShotDisplayText(
  shot: { metadata_json?: StoryboardMetadata; narrative_text?: string | null },
  locale: string = 'es'
): string {
  const metadata = shot.metadata_json
  const localeKey = locale.toLowerCase().startsWith('en') ? 'en' : 'es'

  const localizedPriority = localeKey === 'es'
    ? [
        fromMetadata(metadata, 'display_description_es'),
        fromMetadata(metadata, 'directorial_intent_es'),
        fromMetadata(metadata, 'shot_objective_es'),
        fromMetadata(metadata, 'display_description_en'),
        fromMetadata(metadata, 'directorial_intent_en'),
        fromMetadata(metadata, 'shot_objective_en'),
      ]
    : [
        fromMetadata(metadata, 'display_description_en'),
        fromMetadata(metadata, 'directorial_intent_en'),
        fromMetadata(metadata, 'shot_objective_en'),
        fromMetadata(metadata, 'display_description_es'),
        fromMetadata(metadata, 'directorial_intent_es'),
        fromMetadata(metadata, 'shot_objective_es'),
      ]

  const genericPriority = [
    fromMetadata(metadata, 'shot_objective'),
    fromMetadata(metadata, 'shot_plan_reason'),
    cleanVisibleText(shot.narrative_text),
  ]

  const resolved = [...localizedPriority, ...genericPriority].find((item): item is string => Boolean(item))
  if (resolved) return resolved
  return localeKey === 'en' ? 'Shot description pending.' : 'Descripción del plano pendiente.'
}
