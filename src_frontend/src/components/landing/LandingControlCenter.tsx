import clsx from 'clsx'

type Tone = 'amber' | 'blue' | 'emerald' | 'rose' | 'violet' | 'cyan'

interface MetricCard {
  label: string
  value: string
  tone: Tone
}

interface ModuleCard {
  title: string
  text: string
  tone: Tone
}

interface FloatingCard {
  title: string
  detail: string
  tone: Tone
}

interface LandingControlCenterProps {
  projectName: string
  phase: string
  pulseLabel: string
  sideCards: readonly MetricCard[]
  timeline: readonly string[]
  modules: readonly ModuleCard[]
  floatingCards: readonly FloatingCard[]
}

const toneClassNames: Record<Tone, string> = {
  amber: 'from-amber-300/25 to-amber-500/10 border-amber-300/20 text-amber-100',
  blue: 'from-sky-300/20 to-blue-500/10 border-sky-300/20 text-sky-100',
  emerald: 'from-emerald-300/20 to-emerald-500/10 border-emerald-300/20 text-emerald-100',
  rose: 'from-rose-300/20 to-rose-500/10 border-rose-300/20 text-rose-100',
  violet: 'from-violet-300/20 to-violet-500/10 border-violet-300/20 text-violet-100',
  cyan: 'from-cyan-300/20 to-cyan-500/10 border-cyan-300/20 text-cyan-100',
}

const floatingCardPositions = [
  'left-[-5.75rem] top-[8%]',
  'right-[-5.5rem] top-[9%]',
  'left-[-6.5rem] top-[30%]',
  'right-[-6rem] top-[32%]',
  'left-[-5.4rem] top-[54%]',
  'right-[-5.8rem] top-[58%]',
  'left-[14%] -bottom-10',
]

export default function LandingControlCenter({
  projectName,
  phase,
  pulseLabel,
  sideCards,
  timeline,
  modules,
  floatingCards,
}: LandingControlCenterProps) {
  return (
    <div className="landing-control-shell relative mx-auto w-full max-w-[720px]">
      <div className="landing-orb landing-orb-left" />
      <div className="landing-orb landing-orb-right" />

      {floatingCards.map((card, index) => (
        <div
          key={card.title}
          className={clsx(
            'landing-floating-card hidden xl:block',
            floatingCardPositions[index] || 'right-[-5.5rem] top-[12%]'
          )}
          style={{ animationDelay: `${index * 320}ms` }}
        >
          <div className={clsx('landing-tone-card bg-gradient-to-br', toneClassNames[card.tone])}>
            <p className="text-[10px] uppercase tracking-[0.26em] text-white/70">{card.title}</p>
            <p className="mt-2 text-sm font-medium text-white">{card.detail}</p>
          </div>
        </div>
      ))}

      <div className="landing-panel relative overflow-hidden rounded-[2rem] p-4 sm:p-5">
        <div className="landing-control-grid relative overflow-hidden rounded-[1.7rem] border border-white/10 bg-[#0c111b]/90 p-4 sm:p-5">
          <div className="landing-grid-overlay" />

          <div className="relative z-10 flex items-center justify-between border-b border-white/10 pb-4">
            <div>
              <p className="text-[10px] uppercase tracking-[0.3em] text-slate-500">CID control center</p>
              <h3 className="mt-2 font-display text-3xl text-white sm:text-4xl">{projectName}</h3>
            </div>
            <div className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-[11px] uppercase tracking-[0.24em] text-emerald-200">
              {phase}
            </div>
          </div>

          <div className="relative z-10 mt-5 grid gap-4 lg:grid-cols-[0.34fr_0.66fr]">
            <div className="space-y-4 rounded-[1.4rem] border border-white/10 bg-white/[0.03] p-4 backdrop-blur-xl">
              <div className="rounded-[1.1rem] border border-white/10 bg-white/[0.045] p-4">
                <p className="text-[10px] uppercase tracking-[0.24em] text-slate-500">Status pulse</p>
                <p className="mt-2 text-sm font-medium text-white">{pulseLabel}</p>
              </div>

              {sideCards.map((card) => (
                <div key={card.label} className={clsx('rounded-[1.1rem] border bg-gradient-to-br p-4', toneClassNames[card.tone])}>
                  <p className="text-[10px] uppercase tracking-[0.24em] text-white/65">{card.label}</p>
                  <p className="mt-2 text-lg font-semibold text-white">{card.value}</p>
                </div>
              ))}
            </div>

            <div className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                {modules.map((module) => (
                  <div key={module.title} className={clsx('rounded-[1.2rem] border bg-gradient-to-br p-4', toneClassNames[module.tone])}>
                    <p className="text-[10px] uppercase tracking-[0.24em] text-white/65">{module.title}</p>
                    <p className="mt-2 text-base font-semibold text-white">{module.text}</p>
                  </div>
                ))}
              </div>

              <div className="rounded-[1.4rem] border border-white/10 bg-white/[0.035] p-4">
                <div className="flex items-center justify-between">
                  <p className="text-[10px] uppercase tracking-[0.24em] text-slate-500">Pipeline live</p>
                  <p className="text-xs text-slate-400">handoff aware</p>
                </div>
                <div className="mt-4 grid gap-3 sm:grid-cols-5">
                  {timeline.map((item, index) => (
                    <div key={item} className="rounded-[1rem] border border-white/10 bg-black/20 p-3">
                      <p className="text-[10px] uppercase tracking-[0.22em] text-slate-500">0{index + 1}</p>
                      <p className="mt-2 text-sm font-medium text-white">{item}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-[1.4rem] border border-white/10 bg-black/20 p-4">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-[10px] uppercase tracking-[0.24em] text-slate-500">Executive summary</p>
                    <p className="mt-2 max-w-xl text-sm leading-7 text-slate-300">
                      Una interfaz unica para coordinar guion, plan visual, presupuesto, feedback y entrega sin perder continuidad.
                    </p>
                  </div>
                  <div className="hidden rounded-full border border-amber-300/20 bg-amber-300/10 px-3 py-1 text-[11px] uppercase tracking-[0.22em] text-amber-200 sm:block">
                    premium workflow
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
