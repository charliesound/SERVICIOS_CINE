import { BrainCircuit, FileText, Image as ImageIcon, Sparkles } from 'lucide-react'
import { getLandingVisual } from '@/utils/landingVisuals'

const proofVisual = getLandingVisual('script_to_prompt_proof_result')

const interpretation = [
  'Escena interior de revision en sala de reuniones.',
  'Tono narrativo: tension creativa, decision inminente, ambiente premium.',
  'Personajes: directora en foco, equipo en espera, pantallas como soporte narrativo.',
  'Necesidad visual: storyboard abierto, materiales en revision, entorno de produccion real.',
  'Continuidad: luz ambar, interfaz oscura, lenguaje visual coherente con CID.',
]

const shortPrompt =
  'interior night review room, director evaluating storyboard frames on premium displays, waiting team, dark charcoal palette, warm amber highlights, cinematic SaaS workflow, grounded production realism'

export default function LandingScriptToPromptProof() {
  return (
    <section className="relative border-t border-white/5 py-24 md:py-32">
      <div className="landing-section-glow-right" />
      <div className="mx-auto max-w-7xl px-5 md:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-amber-400">
            Texto -&gt; Prompt -&gt; Imagen
          </p>
          <h2 className="mt-4 font-display text-4xl font-semibold leading-[1.05] text-white md:text-5xl">
            No vendemos una imagen aislada. <br />
            <span className="text-gradient-amber">Vendemos interpretacion narrativa con continuidad visual.</span>
          </h2>
          <p className="mt-4 text-lg leading-8 text-slate-400">
            CID parte de un briefing o fragmento de guion, lo interpreta en lenguaje de produccion y construye prompts coherentes antes de generar imagen.
          </p>
        </div>

        <div className="mt-16 grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
          <div className="space-y-5">
            <div className="rounded-[2rem] border border-white/10 bg-white/[0.03] p-6 backdrop-blur-sm">
              <div className="flex items-center gap-3 text-amber-300">
                <FileText className="h-5 w-5" />
                <span className="font-mono text-[11px] uppercase tracking-[0.24em]">Fragmento de guion / briefing</span>
              </div>
              <p className="mt-4 text-lg leading-8 text-slate-100">
                "INT. SALA DE REUNIONES - NOCHE. Una directora revisa el storyboard de una escena mientras el equipo espera una decision."
              </p>
            </div>

            <div className="rounded-[2rem] border border-white/10 bg-white/[0.03] p-6 backdrop-blur-sm">
              <div className="flex items-center gap-3 text-amber-300">
                <BrainCircuit className="h-5 w-5" />
                <span className="font-mono text-[11px] uppercase tracking-[0.24em]">Interpretacion CID</span>
              </div>
              <ul className="mt-4 grid gap-3 text-sm leading-7 text-slate-300 md:grid-cols-2">
                {interpretation.map((item) => (
                  <li key={item} className="rounded-2xl border border-white/8 bg-black/20 px-4 py-3">
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            <div className="rounded-[2rem] border border-white/10 bg-white/[0.03] p-6 backdrop-blur-sm">
              <div className="flex items-center gap-3 text-amber-300">
                <Sparkles className="h-5 w-5" />
                <span className="font-mono text-[11px] uppercase tracking-[0.24em]">Prompt generado</span>
              </div>
              <pre className="mt-4 whitespace-pre-wrap break-words font-mono text-xs leading-7 text-slate-300">
                {shortPrompt}
              </pre>
            </div>
          </div>

          <div className="rounded-[2rem] border border-white/10 bg-gradient-to-b from-white/[0.06] to-white/[0.02] p-5 backdrop-blur-sm">
            <div className="flex items-center gap-3 text-amber-300">
              <ImageIcon className="h-5 w-5" />
              <span className="font-mono text-[11px] uppercase tracking-[0.24em]">Resultado visual</span>
            </div>

            <div className="relative mt-5 overflow-hidden rounded-[1.6rem] border border-white/10 bg-black/30">
              <img
                src={proofVisual.imagePath}
                alt={proofVisual.visualConcept}
                className="h-[420px] w-full object-cover md:h-[520px]"
                loading="lazy"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#080808] via-transparent to-transparent" />
              <div className="absolute inset-x-0 bottom-0 p-5">
                <div className="rounded-[1.4rem] border border-white/10 bg-[#080808]/70 p-4 backdrop-blur-xl">
                  <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-amber-300">
                    Lo que demuestra esta escena
                  </p>
                  <p className="mt-2 text-sm leading-7 text-slate-200">
                    La imagen ya no es un decorado generico: responde a interior, tono, jerarquia de personajes, revision de storyboard y atmosfera premium de produccion.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
