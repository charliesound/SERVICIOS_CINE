import { ArrowRight, Sparkles, ChevronRight } from 'lucide-react'
import LandingActionButton from '@/components/landing/LandingActionButton'

interface HeroContent {
  eyebrow: string
  title: string
  subtitle: string
}

interface LandingHeroCinematicProps {
  content: HeroContent
  exploreCidTarget: string
  solutionsTarget: string
  requestDemoTarget: string
}

export default function LandingHeroCinematic({
  content,
  exploreCidTarget,
  solutionsTarget,
  requestDemoTarget,
}: LandingHeroCinematicProps) {
  return (
    <section className="relative min-h-screen overflow-hidden">
      <div className="landing-cinematic-hero-bg" />

      <div className="landing-cinematic-glow-top" />
      <div className="landing-cinematic-glow-side" />

      <div className="relative z-10 mx-auto flex min-h-screen max-w-7xl flex-col items-start justify-center px-5 pt-28 md:px-8 lg:flex-row lg:items-center lg:gap-16 lg:pt-0">
        <div className="max-w-2xl shrink-0 pt-8 lg:pt-0">
          <div className="inline-flex items-center gap-2 rounded-full border border-amber-400/20 bg-amber-400/10 px-4 py-2 font-mono text-[11px] uppercase tracking-[0.28em] text-amber-300">
            <Sparkles className="h-3.5 w-3.5" />
            {content.eyebrow}
          </div>

          <h1 className="mt-6 font-display text-5xl font-semibold leading-[0.9] tracking-[-0.04em] text-white sm:text-6xl md:text-7xl lg:text-[5.6rem] xl:text-[6.4rem]">
            {content.title.split(' ').map((word, i) =>
              word === 'Inteligente' || word === 'Digital' ? (
                <span key={i} className="text-gradient-amber">
                  {' '}{word}{' '}
                </span>
              ) : (
                <span key={i}> {word}</span>
              )
            )}
          </h1>

          <p className="mt-6 max-w-xl text-lg leading-8 text-slate-300 md:text-xl md:leading-9">
            {content.subtitle}
          </p>

          <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
            <LandingActionButton destination={exploreCidTarget} variant="primary">
              Crear proyecto
              <ArrowRight className="h-4 w-4" />
            </LandingActionButton>
            <LandingActionButton destination={solutionsTarget} variant="secondary">
              Ver flujo completo
              <ChevronRight className="h-4 w-4" />
            </LandingActionButton>
            <LandingActionButton destination={requestDemoTarget} variant="ghost">
              Solicitar demo
            </LandingActionButton>
          </div>

        </div>

        <div className="relative mt-10 w-full shrink-0 lg:mt-0 lg:w-[42rem]">
          <div className="landing-cinematic-hero-image">
            <img
              src="/landing-media/hero-cinematic.webp"
              alt="Cineframe cinematográfico generado por IA"
              className="h-full w-full object-cover"
              loading="eager"
            />
            <div className="absolute inset-0 bg-gradient-to-r from-[#080808] via-transparent to-transparent" />
          </div>

          <div className="landing-cinematic-floating-card">
            <div className="flex items-center gap-2 text-[10px] uppercase tracking-[0.24em] text-amber-400">
              <Sparkles className="h-3 w-3" />
              Prompt de ejemplo
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-200">
              "Analiza este guion y genera las secuencias visuales para un storyboard cinematográfico."
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
