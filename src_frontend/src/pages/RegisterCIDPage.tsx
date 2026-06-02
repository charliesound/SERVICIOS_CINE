import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Clapperboard, Mail, Lock, User, ArrowRight } from 'lucide-react'
import { useAuthStore } from '@/store'
import { PasswordToggle } from '@/components/PasswordToggle'
import { authApi } from '@/api'
import type { CIDProgram, RegisterCIDPayload } from '@/types'
import { getApiErrorMessage } from '@/utils/apiErrors'
import { useSeo } from '@/hooks/useSeo'
import LanguageToggle from '@/components/common/LanguageToggle'
import { useLanguage } from '@/i18n'

const programs: { id: CIDProgram; label: string; desc: string; badge: string }[] = [
  { id: 'demo', label: 'Demo', desc: 'auth.registerCid.plans.demo.desc', badge: 'auth.registerCid.plans.demo.badge' },
  { id: 'creator', label: 'Creator', desc: 'auth.registerCid.plans.creator.desc', badge: '9.99€/mes' },
  { id: 'producer', label: 'Producer', desc: 'auth.registerCid.plans.producer.desc', badge: '29.99€/mes' },
  { id: 'studio', label: 'Studio', desc: 'auth.registerCid.plans.studio.desc', badge: '79.99€/mes' },
  { id: 'enterprise', label: 'Enterprise', desc: 'auth.registerCid.plans.enterprise.desc', badge: 'auth.registerCid.plans.enterprise.badge' },
]

export default function RegisterCIDPage() {
  const { t } = useLanguage()
  const navigate = useNavigate()
  const { login } = useAuthStore()
  const [step, setStep] = useState<'select' | 'form'>('select')
  const [selectedProgram, setSelectedProgram] = useState<CIDProgram>('demo')
  const [form, setForm] = useState<RegisterCIDPayload>({
    username: '',
    email: '',
    password: '',
    full_name: '',
    company: '',
    country: '',
    accept_terms: false,
  })
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  useSeo({
    title: t('auth.registerCid.metaTitle'),
    description: t('auth.registerCid.metaDescription'),
    path: '/register/cid',
    robots: 'noindex, nofollow',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.accept_terms) {
      setError(t('auth.registerCid.acceptTermsError'))
      return
    }
    if (form.password.length < 6) {
      setError(t('auth.registerCid.passwordMinLength'))
      return
    }

    setError('')
    setIsLoading(true)

    try {
      await authApi.registerCID({
        ...form,
        program: selectedProgram,
      })
      await login(form.email, form.password)
      const target = `/cid/${selectedProgram}`
      navigate(target, { replace: true })
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, t('auth.registerCid.registerError')))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-dark-300 text-white flex flex-col">
      <nav className="border-b border-white/5">
        <div className="max-w-lg mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/register/select" className="text-sm text-gray-400 hover:text-white transition-colors">
            {t('auth.register.back')}
          </Link>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center">
              <Clapperboard className="w-4 h-4 text-black" />
            </div>
            <span className="text-sm font-medium">{t('auth.register.cidProgram')}</span>
          </div>
          <LanguageToggle />
        </div>
      </nav>

      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          {step === 'select' ? (
            <>
              <div className="text-center mb-8">
                <h1 className="text-2xl font-bold mb-2">{t('auth.register.cidTitle')}</h1>
                <p className="text-gray-400 text-sm">{t('auth.register.cidSubtitle')}</p>
              </div>

              <div className="space-y-3 mb-8">
                {programs.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => { setSelectedProgram(p.id); setStep('form') }}
                    className={`w-full p-4 rounded-xl border text-left transition-all ${
                      selectedProgram === p.id
                        ? 'bg-amber-500/10 border-amber-500/40'
                        : 'bg-white/5 border-white/10 hover:border-white/20'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold">{p.label}</h3>
                        <p className="text-sm text-gray-400">{p.desc}</p>
                      </div>
                      <span className={`text-sm font-medium px-3 py-1 rounded-full ${
                        selectedProgram === p.id ? 'bg-amber-500 text-black' : 'bg-white/10 text-gray-400'
                      }`}>
                        {p.badge}
                      </span>
                    </div>
                  </button>
                ))}
              </div>

              <button
                onClick={() => setStep('form')}
                className="w-full py-3 bg-amber-500 hover:bg-amber-400 text-black font-medium rounded-xl transition-colors flex items-center justify-center gap-2"
              >
                {t('auth.register.continue')} {programs.find((p) => p.id === selectedProgram)?.label} <ArrowRight className="w-4 h-4" />
              </button>
            </>
          ) : (
            <>
              <div className="flex items-center justify-between mb-6">
                <button
                  onClick={() => setStep('select')}
                  className="text-sm text-gray-400 hover:text-white transition-colors"
                >
                  {t('auth.register.changePlan')}
                </button>
                <span className="text-sm text-amber-400 font-medium px-3 py-1 bg-amber-500/10 rounded-full">
                  {programs.find((p) => p.id === selectedProgram)?.label} —{' '}
                  {programs.find((p) => p.id === selectedProgram)?.badge}
                </span>
              </div>

              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label className="label">{t('auth.registerCid.username')}</label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                    <input
                      type="text"
                      value={form.username}
                      onChange={(e) => setForm({ ...form, username: e.target.value })}
                      placeholder={t('auth.registerCid.usernamePlaceholder')}
                      className="input pl-10"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="label">{t('auth.registerCid.fullName')}</label>
                  <input
                    type="text"
                    value={form.full_name}
                    onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                    placeholder="Tu nombre"
                    className="input"
                  />
                </div>

                <div>
                  <label className="label">{t('auth.registerCid.email')}</label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                    <input
                      type="email"
                      value={form.email}
                      onChange={(e) => setForm({ ...form, email: e.target.value })}
                      placeholder="tu@email.com"
                      className="input pl-10"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="label">{t('auth.registerCid.company')}</label>
                  <input
                    type="text"
                    value={form.company}
                    onChange={(e) => setForm({ ...form, company: e.target.value })}
                    placeholder={t('auth.registerCid.companyPlaceholder')}
                    className="input"
                  />
                </div>

                <div>
                  <label className="label">{t('auth.registerCid.country')}</label>
                  <input
                    type="text"
                    value={form.country}
                    onChange={(e) => setForm({ ...form, country: e.target.value })}
                    placeholder={t('auth.registerCid.countryPlaceholder')}
                    className="input"
                  />
                </div>

                <div>
                  <label className="label">{t('auth.registerCid.password')}</label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={form.password}
                      onChange={(e) => setForm({ ...form, password: e.target.value })}
                      placeholder={t('auth.registerCid.passwordPlaceholder')}
                      className="input pl-10 pr-10"
                      required
                      minLength={6}
                    />
                    <PasswordToggle
                      visible={showPassword}
                      onToggle={() => setShowPassword(!showPassword)}
                    />
                  </div>
                </div>

                <label className="flex items-start gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.accept_terms}
                    onChange={(e) => setForm({ ...form, accept_terms: e.target.checked })}
                    className="mt-0.5 w-4 h-4 rounded border-gray-600 bg-dark-400 accent-amber-500"
                  />
                  <span className="text-sm text-gray-400">
                    Acepto los{' '}
                    <Link to="/legal/terminos" className="text-amber-400 hover:text-amber-300">
                      {t('auth.registerCid.terms')}
                    </Link>{' '}
                    y la{' '}
                    <Link to="/legal/privacidad" className="text-amber-400 hover:text-amber-300">
                      {t('auth.registerCid.privacy')}
                    </Link>
                  </span>
                </label>

                {error && (
                  <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={isLoading}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  {isLoading ? (
                    <span className="flex items-center gap-2">
                      <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      {t('auth.login.processing')}
                    </span>
                  ) : (
                    <>{t('auth.registerCid.createAccount')} <ArrowRight className="w-4 h-4" /></>
                  )}
                </button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
