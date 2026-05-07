import { Plus, Film, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

const scenes = [
  {
    id: '01',
    title: 'Establishing shot',
    text: 'Amanecer en la ciudad. Cámara lenta sobre los tejados. Luz dorada y niebla matutina.',
    image: '/landing-media/cinematic-frame-01.webp',
  },
  {
    id: '02',
    title: 'Personaje principal',
    text: 'Primer plano del protagonista. Iluminación de claroscuro. Expresión de determinación.',
    image: '/landing-media/landing-comfyui-generation.webp',
  },
  {
    id: '03',
    title: 'Conflicto',
    text: 'Plano medio. Tensión entre personajes. Composición asimétrica con profundidad de campo.',
    image: '/landing-media/cinematic-frame-02.webp',
  },
  {
    id: '04',
    title: 'Resolución',
    text: 'Plano general. El personaje camina hacia el horizonte. Luz de atardecer. Cierre narrativo.',
    image: '/landing-media/cinematic-frame-03.webp',
  },
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

          <div className="landing-scene-carousel">
            <div className="flex gap-4 overflow-x-auto pb-4">
              {scenes.map((scene) => (
                <div key={scene.id} className="landing-scene-card shrink-0">
                  <div className="landing-scene-image">
                    <img
                      src={scene.image}
                      alt={scene.title}
                      className="h-full w-full object-cover"
                      loading="lazy"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-[#080808] via-transparent to-transparent" />
                  </div>
                  <div className="p-4">
                    <div className="flex items-center gap-2">
                      <span className="flex h-6 w-6 items-center justify-center rounded-full border border-amber-500/30 bg-amber-500/10 text-[10px] font-semibold text-amber-300">
                        {scene.id}
                      </span>
                      <span className="text-xs font-medium text-white">{scene.title}</span>
                    </div>
                    <p className="mt-2 text-xs leading-5 text-slate-400">{scene.text}</p>
                  </div>
                </div>
              ))}

              <div className="landing-scene-card-add shrink-0">
                <Plus className="h-8 w-8 text-slate-500" />
                <p className="mt-2 text-xs text-slate-500">Drop asset / reference</p>
              </div>
            </div>

            <div className="mt-4 flex items-center gap-2">
              <div className="h-px flex-1 bg-gradient-to-r from-amber-500/30 via-amber-400/20 to-transparent" />
              <span className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
                Línea temporal narrativa
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
