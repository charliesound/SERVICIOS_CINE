import { Plus, Film, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { getLandingVisual } from '@/utils/landingVisuals'

const storyboardVisual = getLandingVisual('storyboard_sequence')
const continuityVisual = getLandingVisual('continuity_guardrail')

const continuityChecks = [
  'Mismo personaje y misma direccion de arte entre planos.',
  'Raccord de luz y atmosfera estable entre escenas cercanas.',
  'Prompt y biblia visual reutilizados sin romper el universo.',
]

export default function LandingStoryboardCanvas() {
  return (
    <section className="relative border-t border-white/5 py-28 md:py-36">
      <div className="landing-section-glow-right" />
      <div className="mx-auto max-w-7xl px-5 md:px-8">
        <div className="grid items-center gap-12 lg:grid-cols-[1fr_1.2fr]">
          <div>
            <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-amber-400">
              Narrativa y Storyboard
            </p>
            <h2 className="mt-4 font-display text-4xl font-semibold leading-[1.1] text-white md:text-5xl">
              Trabaja por escenas. <br />
              <span className="text-gradient-amber">Mantén la continuidad visual.</span>
            </h2>
            <p className="mt-4 max-w-lg text-lg leading-8 text-slate-400">
              Construye tu storyboard escena por escena. Cada plano mantiene coherencia narrativa, 
              dirección de arte y continuidad visual. Regenera, ajusta y compara versiones.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to="/solutions/cid"
                className="inline-flex items-center gap-2 rounded-full border border-amber-500/30 bg-amber-500/10 px-6 py-3 text-sm font-medium text-amber-300 transition-all hover:bg-amber-500/20"
              >
                <Film className="h-4 w-4" />
                Probar storyboard
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                to="/solutions"
                className="inline-flex items-center gap-2 rounded-full border border-white/10 px-6 py-3 text-sm text-slate-300 transition-all hover:border-white/20"
              >
                <Plus className="h-4 w-4" />
                Subir referencia
              </Link>
            </div>
          </div>

          <div className="space-y-5">
            <div className="overflow-hidden rounded-[2rem] border border-white/10 bg-white/[0.03]">
              <div className="relative h-[340px] md:h-[420px]">
                <img
                  src={storyboardVisual.imagePath}
                  alt={storyboardVisual.visualConcept}
                  className="h-full w-full object-cover"
                  loading="lazy"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#080808] via-transparent to-transparent" />
                <div className="absolute inset-x-0 bottom-0 p-5">
                  <div className="rounded-[1.4rem] border border-white/10 bg-[#080808]/75 p-4 backdrop-blur-xl">
                    <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-amber-300">
                      Qué debe demostrar este bloque
                    </p>
                    <p className="mt-2 text-sm leading-7 text-slate-200">
                      {storyboardVisual.narrativePurpose}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-[0.9fr_1.1fr]">
              <div className="overflow-hidden rounded-[1.6rem] border border-white/10 bg-white/[0.03]">
                <div className="relative h-full min-h-[240px]">
                  <img
                    src={continuityVisual.imagePath}
                    alt={continuityVisual.visualConcept}
                    className="h-full w-full object-cover"
                    loading="lazy"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-[#080808] via-transparent to-transparent" />
                  <div className="absolute inset-x-0 bottom-0 p-4 text-xs text-slate-200">
                    Mismo universo visual, mismas reglas de continuidad.
                  </div>
                </div>
              </div>

              <div className="rounded-[1.6rem] border border-white/10 bg-white/[0.03] p-5">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[10px] uppercase tracking-[0.24em] text-amber-300">
                    Chequeos de continuidad
                  </span>
                </div>

                <div className="mt-4 grid gap-3">
                  {continuityChecks.map((item, index) => (
                    <div key={item} className="rounded-2xl border border-white/8 bg-black/20 px-4 py-4 text-sm leading-7 text-slate-300">
                      <span className="mr-2 font-mono text-[10px] uppercase tracking-[0.18em] text-amber-300">
                        0{index + 1}
                      </span>
                      {item}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
