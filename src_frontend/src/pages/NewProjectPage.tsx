import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { projectsApi } from '@/api'
import { ArrowLeft, ArrowRight, FileText } from 'lucide-react'
import { t } from '@/i18n'

export default function NewProjectPage() {
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [scriptText, setScriptText] = useState('')
  const [error, setError] = useState('')
  const [recommendedUpgrade, setRecommendedUpgrade] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) {
      setError(t('internal.newProject.errors.nameRequired'))
      return
    }

    setError('')
    setRecommendedUpgrade(null)
    setIsLoading(true)

    try {
      const project = await projectsApi.create({ name: name.trim(), description: description.trim() })
      if (scriptText.trim()) {
        await projectsApi.updateScript(project.id, { script_text: scriptText.trim() })
      }
      navigate(`/projects/${project.id}`, { replace: true })
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
      const message = typeof detail === 'string'
        ? detail
        : typeof detail === 'object' && detail && 'message' in detail
          ? String((detail as { message?: unknown }).message || t('internal.newProject.errors.createError'))
          : t('internal.newProject.errors.createError')
      const suggested = typeof detail === 'object' && detail && 'recommended_plan' in detail
        ? String((detail as { recommended_plan?: unknown }).recommended_plan || '')
        : ''
      setError(message)
      setRecommendedUpgrade(suggested || null)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center gap-4 mb-8">
        <Link
          to="/projects"
          className="p-2 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold">{t('internal.newProject.title')}</h1>
          <p className="text-gray-400 text-sm mt-1">{t('internal.newProject.subtitle')}</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="card bg-dark-200/80 border border-white/5 p-6 space-y-5">
          <div>
            <label className="label">{t('internal.newProject.nameLabel')}</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Mi primer guion"
              className="input"
              required
            />
          </div>

          <div>
            <label className="label">{t('internal.newProject.descriptionLabel')}</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder={t('internal.newProject.descriptionPlaceholder')}
              className="input min-h-[80px] resize-none"
            />
          </div>
        </div>

        <div className="card bg-dark-200/80 border border-white/5 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center">
              <FileText className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <h3 className="font-semibold">{t('internal.newProject.scriptTitle')}</h3>
              <p className="text-gray-400 text-sm">{t('internal.newProject.scriptHelp')}</p>
            </div>
          </div>

          <textarea
            value={scriptText}
            onChange={(e) => setScriptText(e.target.value)}
            placeholder={t('internal.newProject.scriptPlaceholder')}
            className="input w-full min-h-[300px] resize-y font-mono text-sm"
          />
          <p className="text-gray-500 text-xs mt-2">
            {t('internal.newProject.scriptCharacterCount').replace('{count}', scriptText.length.toLocaleString())}
          </p>
        </div>

        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
            {error}
            {recommendedUpgrade && (
              <div className="mt-2">
                <Link to="/plans" className="text-amber-300 hover:text-amber-200 underline underline-offset-2">
                  Upgrade recomendado: {recommendedUpgrade}
                </Link>
              </div>
            )}
          </div>
        )}

        <div className="flex items-center justify-end gap-3">
          <Link
            to="/projects"
            className="px-6 py-3 border border-white/10 hover:border-white/20 rounded-xl transition-colors"
          >
            {t('internal.common.cancel')}
          </Link>
          <button
            type="submit"
            disabled={isLoading}
            className="btn-primary flex items-center gap-2"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Creando...
              </span>
            ) : (
              <>{t('internal.newProject.createProject')} <ArrowRight className="w-4 h-4" /></>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
