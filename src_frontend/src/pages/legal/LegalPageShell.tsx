import { Link } from 'react-router-dom'
import { ArrowLeft, ShieldCheck } from 'lucide-react'

interface LegalPageShellProps {
  eyebrow: string
  title: string
  description: string
  children: React.ReactNode
}

const legalLinks = [
  { label: 'Privacidad', href: '/legal/privacidad' },
  { label: 'Aviso legal', href: '/legal/aviso-legal' },
  { label: 'Terminos', href: '/legal/terminos' },
  { label: 'IA y contenidos', href: '/legal/ia-y-contenidos' },
]

export default function LegalPageShell({ eyebrow, title, description, children }: LegalPageShellProps) {
  return (
    <div className="landing-shell min-h-screen text-white">
      <div className="landing-noise" />
      <div className="landing-backdrop" />

      <main className="relative z-10 px-5 py-10 md:px-6 lg:px-8">
        <div className="mx-auto max-w-5xl">
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-6">
            <Link
              to="/"
              className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-slate-200 transition-colors hover:border-white/20 hover:bg-white/[0.08]"
            >
              <ArrowLeft className="h-4 w-4" />
              Volver a la landing
            </Link>

            <div className="flex flex-wrap items-center gap-2 text-sm text-slate-300">
              {legalLinks.map((item) => (
                <Link
                  key={item.href}
                  to={item.href}
                  className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1.5 transition-colors hover:border-white/20 hover:text-white"
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>

          <section className="pt-10 md:pt-14">
            <p className="editorial-kicker text-amber-300/90">{eyebrow}</p>
            <h1 className="mt-4 max-w-4xl font-display text-4xl font-semibold leading-[0.92] text-white md:text-6xl">
              {title}
            </h1>
            <p className="mt-5 max-w-3xl text-base leading-8 text-slate-300 md:text-lg">{description}</p>

            <div className="landing-panel mt-8 rounded-[1.8rem] border-amber-300/20 bg-amber-300/10 p-5 text-sm leading-7 text-amber-50">
              <div className="flex items-start gap-3">
                <ShieldCheck className="mt-1 h-5 w-5 shrink-0 text-amber-300" />
                <p>Texto provisional pendiente de revision legal especializada en Espana/UE.</p>
              </div>
            </div>

            <div className="mt-8 space-y-6">{children}</div>
          </section>
        </div>
      </main>
    </div>
  )
}
