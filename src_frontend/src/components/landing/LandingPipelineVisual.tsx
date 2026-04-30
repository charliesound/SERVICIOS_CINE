interface PipelineStep {
  title: string
  text: string
  meta: string
}

interface LandingPipelineVisualProps {
  steps: readonly PipelineStep[]
}

export default function LandingPipelineVisual({ steps }: LandingPipelineVisualProps) {
  return (
    <div className="landing-pipeline-visual rounded-[2rem] border border-white/10 bg-[#08111b]/80 p-5 shadow-[0_28px_80px_rgba(0,0,0,0.35)] backdrop-blur-2xl">
      <div className="rounded-[1.7rem] border border-white/10 bg-white/[0.03] p-5">
        <div className="flex items-center justify-between gap-4 border-b border-white/10 pb-4">
          <div>
            <p className="text-[10px] uppercase tracking-[0.28em] text-slate-500">CID orchestration view</p>
            <h3 className="mt-2 font-display text-3xl text-white sm:text-4xl">Pipeline de proyecto</h3>
          </div>
          <div className="rounded-full border border-cyan-300/15 bg-cyan-300/10 px-3 py-1 text-[11px] uppercase tracking-[0.22em] text-cyan-100">
            live orchestration
          </div>
        </div>

        <div className="mt-6 grid gap-5 lg:grid-cols-[0.68fr_0.32fr]">
          <div className="rounded-[1.4rem] border border-white/10 bg-black/20 p-4">
            <div className="landing-pipeline-track">
              {steps.map((step, index) => (
                <div key={step.title} className="landing-pipeline-node">
                  <div className="landing-pipeline-marker">
                    <span>{index + 1}</span>
                  </div>
                  <div className="landing-pipeline-node-card">
                    <p className="text-[10px] uppercase tracking-[0.24em] text-slate-500">{step.meta}</p>
                    <h4 className="mt-2 text-lg font-semibold text-white">{step.title}</h4>
                    <p className="mt-2 text-sm leading-7 text-slate-300">{step.text}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="grid gap-4">
            <div className="rounded-[1.3rem] border border-white/10 bg-gradient-to-br from-white/[0.06] to-white/[0.02] p-4">
              <p className="text-[10px] uppercase tracking-[0.24em] text-slate-500">Sync map</p>
              <div className="mt-4 space-y-3">
                {['Narrativa', 'Visual', 'Budget', 'Review'].map((item, index) => (
                  <div key={item} className="rounded-2xl border border-white/10 bg-black/20 p-3">
                    <div className="flex items-center justify-between text-sm text-white">
                      <span>{item}</span>
                      <span className="text-slate-400">0{index + 1}</span>
                    </div>
                    <div className="mt-3 h-2 rounded-full bg-white/5">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-amber-300 via-cyan-300 to-emerald-300"
                        style={{ width: `${68 + index * 8}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-[1.3rem] border border-white/10 bg-black/20 p-4">
              <p className="text-[10px] uppercase tracking-[0.24em] text-slate-500">Outcome</p>
              <p className="mt-3 text-sm leading-7 text-slate-300">
                Cada etapa deja trazas utiles para la siguiente: menos handoff manual, mas continuidad entre desarrollo, produccion y entrega.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
