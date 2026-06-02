import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Clapperboard, Mail, ArrowRight, Check } from 'lucide-react'
import { authApi } from '@/api'
import { useAuthStore, getPrimaryCIDTarget } from '@/store'
import type { RegisterPartnerPayload } from '@/types'
import { getApiErrorMessage } from '@/utils/apiErrors'
import { useSeo } from '@/hooks/useSeo'
import { t } from '@/i18n'

export default function RegisterPartnerPage() {
  const navigate = useNavigate()
  const { login, user } = useAuthStore()
  const [form, setForm] = useState<RegisterPartnerPayload>({
    full_name: '',
    email: '',
    company: '',
    collaboration_type: '',
    message: '',
  })
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [step, setStep] = useState<'form' | 'success'>('form')

  useSeo({
    title: step === 'success' ? t('auth.registerPartner.seo.successTitle') : t('auth.registerPartner.seo.title'),
    description: t('auth.registerPartner.seo.description'),
    path: '/register/partner',
    robots: 'noindex, nofollow',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    const tempPassword = `partner_${Math.random().toString(36).slice(2, 18)}`

    try {
      await authApi.registerPartnerWithPassword({
        ...form,
        password: tempPassword,
      })
      await login(form.email, tempPassword)
      setStep('success')
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, t('auth.registerPartner.requestError')))
    } finally {
      setIsLoading(false)
    }
  }

  if (step === 'success') {
    return (
      <div className="min-h-screen bg-dark-300 flex items-center justify-center px-6">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 rounded-full bg-purple-500/20 flex items-center justify-center mx-auto mb-6">
            <Check className="w-8 h-8 text-purple-400" />
          </div>
          <h1 className="text-2xl font-bold mb-4">{t('auth.registerPartner.success.title')}</h1>
          <p className="text-gray-400 mb-8">
            {t('auth.registerPartner.success.message')}
          </p>
          <button
            onClick={() => navigate(getPrimaryCIDTarget(user))}
            className="px-8 py-3 bg-purple-500 hover:bg-purple-400 text-black font-medium rounded-xl transition-colors flex items-center gap-2 mx-auto"
          >
            {t('auth.registerPartner.success.dashboard')} <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-dark-300 text-white flex flex-col">
      <nav className="border-b border-white/5">
        <div className="max-w-lg mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/register/select" className="text-sm text-gray-400 hover:text-white transition-colors">
            {t('auth.registerPartner.back')}
          </Link>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center">
              <Clapperboard className="w-4 h-4 text-black" />
            </div>
            <span className="text-sm font-medium">{t('auth.registerPartner.badge')}</span>
          </div>
          <div className="w-16" />
        </div>
      </nav>

      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold mb-2">{t('auth.registerPartner.title')}</h1>
            <p className="text-gray-400 text-sm">{t('auth.registerPartner.subtitle')}</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="label">{t('auth.registerPartner.fields.fullName')}</label>
              <input
                type="text"
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                placeholder={t('auth.registerPartner.placeholders.fullName')}
                className="input"
                required
              />
            </div>

            <div>
              <label className="label">{t('auth.registerPartner.fields.email')}</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  placeholder="tu@empresa.com"
                  className="input pl-10"
                  required
                />
              </div>
            </div>

            <div>
              <label className="label">{t('auth.registerPartner.fields.company')}</label>
              <input
                type="text"
                value={form.company}
                onChange={(e) => setForm({ ...form, company: e.target.value })}
                placeholder={t('auth.registerPartner.placeholders.company')}
                className="input"
                required
              />
            </div>

            <div>
              <label className="label">{t('auth.registerPartner.fields.collaborationType')}</label>
              <select
                value={form.collaboration_type}
                onChange={(e) => setForm({ ...form, collaboration_type: e.target.value })}
                className="input"
                required
              >
                <option value="">{t('auth.registerPartner.options.select')}</option>
                <option value="integrador">{t('auth.registerPartner.options.integrator')}</option>
                <option value="distribuidor">{t('auth.registerPartner.options.distributor')}</option>
                <option value="whitelabel">{t('auth.registerPartner.options.whiteLabel')}</option>
                <option value="agencia">{t('auth.registerPartner.options.productionAgency')}</option>
                <option value="otro">{t('auth.registerPartner.options.other')}</option>
              </select>
            </div>

            <div>
              <label className="label">{t('auth.registerPartner.fields.message')}</label>
              <textarea
                value={form.message}
                onChange={(e) => setForm({ ...form, message: e.target.value })}
                placeholder={t('auth.registerPartner.placeholders.message')}
                className="input min-h-[80px] resize-none"
              />
            </div>

            <p className="text-xs leading-5 text-slate-500">
              {t('auth.registerPartner.legal.prefix')}{' '}
              <Link to="/legal/privacidad" className="text-purple-400 hover:text-purple-300">
                {t('auth.registerPartner.legal.privacy')}
              </Link>
              , el{' '}
              <Link to="/legal/aviso-legal" className="text-purple-400 hover:text-purple-300">
                {t('auth.registerPartner.legal.legalNotice')}
              </Link>{' '}
              {t('auth.registerPartner.legal.andConditions')}{' '}
              <Link to="/legal/ia-y-contenidos" className="text-purple-400 hover:text-purple-300">
                {t('auth.registerPartner.legal.aiContent')}
              </Link>
              .
            </p>

            {error && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-purple-500 hover:bg-purple-400 text-black font-medium rounded-xl transition-colors flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  {t('auth.registerPartner.sending')}
                </span>
              ) : (
                <>{t('auth.registerPartner.submit')} <ArrowRight className="w-4 h-4" /></>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
