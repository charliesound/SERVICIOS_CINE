import clsx from 'clsx'
import { useLanguage } from '@/i18n'

export default function LanguageToggle() {
  const { language, setLanguage, t } = useLanguage()

  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-2 py-2">
      <span className="px-2 text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-400">
        {t('common.language.toggleLabel')}
      </span>
      <button
        type="button"
        onClick={() => setLanguage('es')}
        className={clsx(
          'rounded-full px-3 py-1.5 text-xs font-semibold transition-colors',
          language === 'es'
            ? 'bg-amber-400 text-black'
            : 'text-slate-300 hover:bg-white/10 hover:text-white'
        )}
        aria-pressed={language === 'es'}
      >
        ES
      </button>
      <button
        type="button"
        onClick={() => setLanguage('en')}
        className={clsx(
          'rounded-full px-3 py-1.5 text-xs font-semibold transition-colors',
          language === 'en'
            ? 'bg-amber-400 text-black'
            : 'text-slate-300 hover:bg-white/10 hover:text-white'
        )}
        aria-pressed={language === 'en'}
      >
        EN
      </button>
    </div>
  )
}
