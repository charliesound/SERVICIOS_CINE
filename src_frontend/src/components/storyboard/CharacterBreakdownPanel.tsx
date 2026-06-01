import { useMemo } from 'react'
import { Users, Film, Filter } from 'lucide-react'
import type { StoryboardSequence } from '@/types/storyboard'
import { deriveCharacterBreakdown } from '@/utils/characterBreakdown'
import { useLanguage } from '@/i18n'

interface CharacterBreakdownPanelProps {
  sequences: StoryboardSequence[]
  onFilterByCharacter?: (character: string) => void
  onSelectSequencesByCharacter?: (sequenceIds: string[]) => void
}

export function CharacterBreakdownPanel({
  sequences,
  onFilterByCharacter,
  onSelectSequencesByCharacter,
}: CharacterBreakdownPanelProps) {
  const { t } = useLanguage()
  const breakdown = useMemo(() => deriveCharacterBreakdown(sequences), [sequences])

  if (breakdown.length === 0) {
    return (
      <div className="rounded-xl border border-white/10 bg-dark-200/80 p-6 text-center">
        <Users className="w-10 h-10 text-slate-600 mx-auto mb-2" />
        <p className="text-sm text-slate-400">{t('components.storyboard.characterBreakdown.empty')}</p>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-white/10 bg-dark-200/80 p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2">
          <Users className="w-4 h-4 text-cyan-400" />
          {t('components.storyboard.characterBreakdown.title')} ({breakdown.length})
        </h3>
      </div>

      <div className="grid gap-2">
        {breakdown.map((entry) => (
          <div
            key={entry.character}
            className="rounded-lg border border-white/10 bg-black/20 p-3 hover:border-cyan-500/30 transition-all"
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-semibold text-white">{entry.character}</span>
              <span className="text-xs text-slate-400">
                {entry.appearances} {entry.appearances !== 1 ? t('components.storyboard.characterBreakdown.sequencePlural') : t('components.storyboard.characterBreakdown.sequenceSingular')}
              </span>
            </div>
            <div className="flex flex-wrap gap-1 mb-2">
              {entry.sequence_numbers.map((num) => (
                <span
                  key={num}
                  className="px-1.5 py-0.5 text-[10px] bg-amber-400/10 text-amber-300 rounded"
                >
                  #{num}
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              {onFilterByCharacter && (
                <button
                  type="button"
                  onClick={() => onFilterByCharacter(entry.character)}
                  className="inline-flex items-center gap-1 px-2 py-1 text-[10px] font-medium bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 rounded-lg hover:bg-cyan-500/20 transition-all"
                >
                  <Film className="w-3 h-3" />
                  {t('components.storyboard.characterBreakdown.filterStoryboard')}
                </button>
              )}
              {onSelectSequencesByCharacter && (
                <button
                  type="button"
                  onClick={() => onSelectSequencesByCharacter(entry.sequence_ids)}
                  className="inline-flex items-center gap-1 px-2 py-1 text-[10px] font-medium bg-amber-500/10 border border-amber-500/30 text-amber-300 rounded-lg hover:bg-amber-500/20 transition-all"
                >
                  <Filter className="w-3 h-3" />
                  {t('components.storyboard.characterBreakdown.selectSequences')}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
