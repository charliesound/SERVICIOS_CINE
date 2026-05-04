import { useEffect } from 'react'
import { ArrowRight, Clapperboard, Film, Mic2, ShieldCheck, Sparkles, Wand2 } from 'lucide-react'
import LandingAmbientScene from '@/components/landing/LandingAmbientScene'
import LandingReveal from '@/components/landing/LandingReveal'
import LandingSectionHeading from '@/components/landing/LandingSectionHeading'

const smokeProof = [
  'Hero premium con jerarquia cinematografica clara',
  'Tailwind responsive para desktop y mobile',
  'Microcopy comercial con tono audiovisual',
]

const capabilityCards = [
  {
    icon: Film,
    title: 'CID como nucleo narrativo',
    text: 'Un sistema que conecta desarrollo, produccion y entrega sin convertir la experiencia en un dashboard generico.',
  },
  {
    icon: Mic2,
    title: 'Apps de oficio',
    text: 'Dubbing, storyboard, promo y sonido aparecen como herramientas serias para departamentos reales.',
  },
  {
    icon: Wand2,
    title: 'Presentacion premium',
    text: 'La interfaz favorece claridad, espacio visual y lectura de producto antes que ruido tecnico.',
  },
]

export default function SkillSmokeTestPage() {
  useEffect(() => {
    document.title = 'AILinkCinema Skill Smoke Test - Premium Cinema UI'

    const description = 'Smoke test visual para validar hero premium, responsive Tailwind, microcopy cinematografico y estructura coherente con AILinkCinema/CID.'
    let meta = document.querySelector('meta[name="description"]')

    if (!meta) {
      meta = document.createElement('meta')
      meta.setAttribute('name', 'description')
      document.head.appendChild(meta)
    }

    meta.setAttribute('content', description)
  }, [])

  return (
    <div className="landing-shell landing-brand-shell min-h-screen text-white">
      <LandingAmbientScene />
      <div className="landing-noise" />
      <div className="landing-backdrop" />

      <main>
        <section className="relative overflow-hidden pt-24 md:pt-32 lg:pt-36">
          <div className="landing-hero-radial" />
          <div className="mx-auto max-w-7xl px-5 pb-20 md:px-6 lg:px-8">
            <div className="solution-hero-panel">
              <div className="solution-grid-overlay" />
              <div className="relative z-10 grid gap-10 xl:grid-cols-[0.95fr_1.05fr] xl:items-center">
                <LandingReveal>
                  <div>
                    <div className="inline-flex items-center gap-2 rounded-full border border-amber-300/20 bg-amber-300/10 px-4 py-2 font-mono text-[11px] uppercase tracking-[0.28em] text-amber-200">
                      <Sparkles className="h-3.5 w-3.5" />
                      Skill smoke test
                    </div>

                    <h1 className="mt-7 max-w-4xl font-display text-5xl font-semibold leading-[0.88] tracking-[-0.04em] text-white sm:text-6xl md:text-7xl xl:text-[6rem]">
                      IA disenada para hacer cine, presentada como producto serio.
                    </h1>

                    <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-200 md:text-2xl md:leading-10">
                      Esta pagina de prueba demuestra un hero premium, responsive y con tono cinematografico alineado con AILinkCinema y CID.
                    </p>

                    <p className="mt-5 max-w-2xl text-base leading-8 text-slate-400 md:text-lg">
                      El enfoque prioriza claridad comercial, atmosfera audiovisual y una lectura elegante de producto, sin parecer dashboard tecnico ni landing SaaS intercambiable.
                    </p>

                    <div className="mt-8 flex flex-wrap gap-2.5">
                      {smokeProof.map((item) => (
                        <span key={item} className="landing-pill">
                          {item}
                        </span>
                      ))}
                    </div>

                    <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
                      <a href="#capabilities" className="landing-cta-primary inline-flex">
                        Ver estructura
                        <ArrowRight className="h-4 w-4" />
                      </a>
                      <a href="#seo-block" className="landing-cta-secondary inline-flex">
                        Revisar SEO basico
                      </a>
                    </div>
                  </div>
                </LandingReveal>

                <LandingReveal delay={120}>
                  <div className="landing-brand-hero-panel">
                    <div className="landing-brand-grid-lines" />
                    <div className="relative z-10 grid gap-4 md:grid-cols-2">
                      <div className="landing-brand-cid-core">
                        <p className="text-[10px] uppercase tracking-[0.28em] text-amber-200">Marca principal</p>
                        <h2 className="mt-4 font-display text-4xl text-white md:text-5xl">AILinkCinema</h2>
                        <p className="mt-4 text-sm leading-7 text-slate-300">
                          Partner tecnologico que desarrolla soluciones IA a medida y productos propios para cine y audiovisual.
                        </p>
                      </div>

                      <div className="landing-brand-cid-core">
                        <p className="text-[10px] uppercase tracking-[0.28em] text-cyan-200">Producto principal</p>
                        <h2 className="mt-4 font-display text-4xl text-white md:text-5xl">CID</h2>
                        <p className="mt-2 text-lg font-medium text-slate-100">Cine Inteligente Digital</p>
                        <p className="mt-4 text-sm leading-7 text-slate-300">
                          Un flujo premium para desarrollar, producir, coordinar y entregar proyectos audiovisuales con continuidad real entre departamentos.
                        </p>
                      </div>

                      <div className="landing-brand-product-tile landing-brand-product-tile-amber md:col-span-2">
                        <div className="flex items-center gap-3">
                          <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-amber-300">
                            <Clapperboard className="h-5 w-5" />
                          </div>
                          <div>
                            <p className="text-[10px] uppercase tracking-[0.24em] text-white/60">Microcopy cinematografico</p>
                            <p className="mt-1 text-base font-semibold text-white">Menos promesa abstracta, mas oficio, pipeline y lenguaje de industria.</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </LandingReveal>
              </div>
            </div>
          </div>
        </section>

        <section id="capabilities" className="relative py-24">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <LandingReveal>
              <LandingSectionHeading
                eyebrow="Responsive structure"
                title="Tailwind responsive con ritmo visual limpio y lectura de producto."
                description="La composicion se adapta a mobile, tablet y desktop sin colapsar la jerarquia, manteniendo espacio visual y bloques cortos de texto."
              />
            </LandingReveal>

            <div className="mt-14 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
              {capabilityCards.map((card, index) => {
                const Icon = card.icon
                return (
                  <LandingReveal key={card.title} delay={index * 90}>
                    <div className="solution-card h-full">
                      <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-amber-300">
                        <Icon className="h-5 w-5" />
                      </div>
                      <h3 className="mt-5 text-2xl font-semibold text-white">{card.title}</h3>
                      <p className="mt-3 text-sm leading-7 text-slate-300">{card.text}</p>
                    </div>
                  </LandingReveal>
                )
              })}
            </div>
          </div>
        </section>

        <section id="seo-block" className="relative border-y border-white/10 bg-[#09111c]/80 py-24">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <LandingReveal>
              <div className="solution-pricing-block solution-pricing-block-featured">
                <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                  <div>
                    <p className="solution-eyebrow text-amber-300">SEO basico</p>
                    <h2 className="mt-3 text-3xl font-semibold text-white">Si el stack no usa SSR, al menos debe cuidar title, description y semantica.</h2>
                    <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-300">
                      Este smoke test actualiza `document.title`, asegura un `meta description` y usa encabezados semanticos para reforzar la lectura de marca y producto.
                    </p>
                  </div>

                  <div className="rounded-[1.4rem] border border-white/10 bg-white/[0.04] p-4">
                    <p className="text-base font-medium text-amber-200">Title + meta description</p>
                    <p className="mt-2 text-sm text-slate-300">Semantica visible</p>
                  </div>
                </div>

                <div className="mt-6 grid gap-3 md:grid-cols-3">
                  <div className="rounded-[1.25rem] border border-white/10 bg-white/[0.03] p-4 text-sm leading-7 text-slate-200">
                    Hero con `h1` unico y copy orientado a busqueda de producto cinematografico.
                  </div>
                  <div className="rounded-[1.25rem] border border-white/10 bg-white/[0.03] p-4 text-sm leading-7 text-slate-200">
                    Secciones con jerarquia clara para AILinkCinema como marca y CID como producto.
                  </div>
                  <div className="rounded-[1.25rem] border border-white/10 bg-white/[0.03] p-4 text-sm leading-7 text-slate-200">
                    Microcopy breve, especifico y alineado con cine, produccion y software premium.
                  </div>
                </div>
              </div>
            </LandingReveal>
          </div>
        </section>

        <section className="relative py-24">
          <div className="mx-auto max-w-6xl px-5 md:px-6 lg:px-8">
            <LandingReveal>
              <div className="landing-brand-final-cta rounded-[2.4rem] p-8 sm:p-10 lg:p-12">
                <div className="grid gap-8 lg:grid-cols-[1fr_auto] lg:items-end">
                  <div>
                    <p className="editorial-kicker text-amber-300">Diagnostico visual</p>
                    <h2 className="mt-4 max-w-4xl font-display text-4xl font-semibold leading-[0.92] text-white md:text-6xl">
                      Si los skills existieran y estuvieran conectados, este es el tipo de salida que deberian empujar.
                    </h2>
                    <p className="mt-5 max-w-3xl text-base leading-8 text-slate-200 md:text-lg">
                      Premium oscuro, tipografia amplia, copy corto, atmosfera cinematografica y una arquitectura de producto que no se pierde en patrones genericos.
                    </p>
                  </div>

                  <div className="rounded-[1.5rem] border border-white/10 bg-white/[0.04] px-5 py-5 text-sm leading-7 text-slate-200">
                    <div className="flex items-center gap-2 text-amber-200">
                      <ShieldCheck className="h-4 w-4" />
                      Smoke test visual coherente con AILinkCinema/CID
                    </div>
                  </div>
                </div>
              </div>
            </LandingReveal>
          </div>
        </section>
      </main>
    </div>
  )
}
