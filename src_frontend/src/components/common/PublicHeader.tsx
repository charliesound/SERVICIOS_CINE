import { Link } from 'react-router-dom'
import { LayoutDashboard, LogOut } from 'lucide-react'
import LanguageToggle from '@/components/common/LanguageToggle'
import { useLanguage } from '@/i18n'
import { getPrimaryCIDTarget, useAuthStore } from '@/store'

type PublicHeaderProps = {
  eyebrowKey: string
  ctaTo?: string
  ctaKey?: string
}

const navItems = [
  { to: '/solutions', labelKey: 'public.nav.solutions' },
  { to: '/solutions/cid', labelKey: 'public.nav.cidStudio' },
  { to: '/pricing', labelKey: 'public.nav.pricing' },
  { to: '/legal/privacidad', labelKey: 'public.nav.legal' },
]

export default function PublicHeader({
  eyebrowKey,
  ctaTo = '/register/demo',
  ctaKey = 'common.cta.requestDemo',
}: PublicHeaderProps) {
  const { t } = useLanguage()
  const { isAuthenticated, user } = useAuthStore()
  const cidTarget = getPrimaryCIDTarget(user)

  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-white/10 bg-[#07111d]/55 backdrop-blur-2xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-4 md:px-6 lg:px-8">
        <Link to="/" className="flex items-center gap-3">
          <img
            src="/assets/ailinkcinema-logo.png"
            alt={t('common.brand.name')}
            className="h-11 w-11 rounded-2xl object-cover shadow-[0_0_32px_rgba(245,158,11,0.22)]"
          />
          <div>
            <p className="text-lg font-semibold tracking-tight text-white">{t('common.brand.name')}</p>
            <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-400">{t(eyebrowKey)}</p>
          </div>
        </Link>

        <nav className="hidden items-center gap-7 text-sm text-slate-300 xl:flex">
          {navItems.map((item) => (
            <Link key={item.to} to={item.to} className="transition-colors duration-300 hover:text-white">
              {t(item.labelKey)}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2 md:gap-3">
          <LanguageToggle />
          {isAuthenticated ? (
            <>
              <Link to={cidTarget} className="landing-cta-secondary hidden sm:inline-flex">
                <LayoutDashboard className="h-4 w-4" />
                {t('public.header.enterCid')}
              </Link>
              <button
                onClick={() => {
                  useAuthStore.getState().logout()
                  window.location.href = '/'
                }}
                className="inline-flex items-center gap-2 rounded-full px-3 py-2 text-sm text-slate-400 transition-colors hover:text-red-200"
              >
                <LogOut className="h-4 w-4" />
                {t('public.header.logout')}
              </button>
            </>
          ) : (
            <Link to={ctaTo} className="landing-cta-primary hidden sm:inline-flex">
              {t(ctaKey)}
            </Link>
          )}
        </div>
      </div>
    </header>
  )
}
