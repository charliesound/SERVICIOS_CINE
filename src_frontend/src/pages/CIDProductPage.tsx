import { useState } from 'react'
import { Link } from 'react-router-dom'
import { LayoutDashboard, LogOut, ShieldCheck, ArrowRight, ChevronRight, Film, FileSearch, Clapperboard, LayoutTemplate, Mic2, AudioWaveform, MonitorPlay, Sparkles, Waypoints } from 'lucide-react'
import LandingAmbientScene from '@/components/landing/LandingAmbientScene'
import { useSeo } from '@/hooks/useSeo'
import { getPrimaryCIDTarget, useAuthStore } from '@/store'
import { buildAbsoluteUrl, buildBreadcrumbStructuredData } from '@/utils/seo'

const pipelinePhases = [
  { name: 'Guion', icon: FileSearch, description: 'Desarrollo y analisis' },
  { name: 'Desglose', icon: FileSearch, description: 'Tecnico y produccion' },
  { name: 'Storyboard', icon: Clapperboard, description: 'Previz y visual' },
  { name: 'Planificacion', icon: LayoutTemplate, description: 'Rodaje y recursos' },
  { name: 'Produccion', icon: Film, description: 'Rodaje y ejecucion' },
  { name: 'Post', icon: AudioWaveform, description: 'Sonido y VFX' },
  { name: 'Entrega', icon: MonitorPlay, description: 'Distribucion y delivery' },
]

const departments = [
  { name: 'Desarrollo', icon: FileSearch, items: ['Guion', 'Analisis', 'Desglose'] },
  { name: 'Direccion y previsión', icon: Clapperboard, items: ['Storyboard', 'Referencias visuales', 'Planificacion creativa'] },
  { name: 'Produccion', icon: Film, items: ['Plan de rodaje', 'Recursos', 'Coordinacion', 'Logistica'] },
  { name: 'Sonido y doblaje', icon: Mic2, items: ['Takes', 'Limpieza', 'Sincronia', 'QC', 'Entregables'] },
  { name: 'Postproduccion', icon: Sparkles, items: ['Montaje', 'VFX', 'Finishing', 'Revision'] },
  { name: 'Marketing y distribucion', icon: MonitorPlay, items: ['Teasers', 'Piezas promocionales', 'Materiales de entrega'] },
]

const modules = [
  { name: 'Script & Breakdown AI', icon: FileSearch, description: 'Analisis y desglose tecnico' },
  { name: 'Storyboard AI Studio', icon: Clapperboard, description: 'Previz y referencias visuales' },
  { name: 'Production Planner AI', icon: LayoutTemplate, description: 'Planificacion de rodaje' },
  { name: 'DubbingTake Studio AI', icon: Mic2, description: 'Gestion de doblaje y QC' },
  { name: 'Sound Post AI', icon: AudioWaveform, description: 'Sonido y entregables' },
  { name: 'Promo Video AI', icon: MonitorPlay, description: 'Piezas promocionales' },
  { name: 'VFX & Enhancement AI', icon: Sparkles, description: 'VFX y apoyo de post' },
]

const useCases = [
  { name: 'Largometrajes', description: 'Desarrollo y produccion completa' },
  { name: 'Series y plataformas', description: 'Contenido para streaming' },
  { name: 'Publicidad', description: 'Produccion comercial' },
  { name: 'Videoclips', description: 'Musica y contenido creativo' },
  { name: 'Promocional', description: 'Pitch y presentaciones' },
  { name: 'Documentales', description: 'Proyectos independientes' },
]

export default function CIDProductPage() {
  const { isAuthenticated, user } = useAuthStore()
  const cidTarget = getPrimaryCIDTarget(user)
  const [activePricing, setActivePricing] = useState<'setup' | 'modules'>('setup')

  useSeo({
    title: 'CID - El sistema para desarrollar y producir cine con IA',
    description: 'CID conecta creatividad, planificacion y produccion en un flujo de trabajo real. Desde la idea inicial hasta la entrega final, todos los departamentos trabajan coordinados dentro de un mismo sistema.',
    path: '/solutions/cid',
    robots: 'index, follow',
    keywords: ['CID cine inteligente digital', 'sistema produccion audiovisual', 'software IA cine', 'pipeline audiovisual completo'],
    structuredData: [
      buildBreadcrumbStructuredData([
        { name: 'Inicio', path: '/' },
        { name: 'Soluciones', path: '/solutions' },
        { name: 'CID', path: '/solutions/cid' },
      ]),
      {
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        name: 'CID - Cine Inteligente Digital',
        applicationCategory: 'BusinessApplication',
        operatingSystem: 'Web',
        url: buildAbsoluteUrl('/solutions/cid'),
        description: 'Sistema completo de produccion audiovisual que une creatividad, canvas colaborativo, IA y departamentos reales en un flujo conectado.',
        offers: {
          '@type': 'Offer',
          priceCurrency: 'EUR',
          description: 'Setup inicial desde 1.500 EUR + cuota mensual desde 299 EUR/mes',
        },
      },
    ],
  })

  return (
    <div className="landing-shell landing-brand-shell min-h-screen text-white">
      <LandingAmbientScene />
      <div className="landing-noise" />
      <div className="landing-backdrop" />

      {/* Header */}
      <header className="fixed inset-x-0 top-0 z-50 border-b border-white/10 bg-[#07111d]/55 backdrop-blur-2xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-4 md:px-6 lg:px-8">
          <Link to="/" className="flex items-center gap-3">
            <img src="/assets/ailinkcinema-logo.png" alt="AILinkCinema" className="h-11 w-11 rounded-2xl object-cover shadow-[0_0_32px_rgba(245,158,11,0.22)]" />
            <div>
              <p className="text-lg font-semibold tracking-tight text-white">AILinkCinema</p>
              <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-400">CID Product</p>
            </div>
          </Link>

          <nav className="hidden items-center gap-7 text-sm text-slate-300 xl:flex">
            <Link to="/solutions" className="transition-colors duration-300 hover:text-white">Soluciones</Link>
            <Link to="/pricing" className="transition-colors duration-300 hover:text-white">Precios</Link>
            <Link to="/legal/privacidad" className="transition-colors duration-300 hover:text-white">Legal</Link>
          </nav>

          <div className="flex items-center gap-2 md:gap-3">
            {isAuthenticated ? (
              <>
                <Link to={cidTarget} className="landing-cta-secondary hidden sm:inline-flex">
                  <LayoutDashboard className="h-4 w-4" />
                  Entrar a CID
                </Link>
                <button
                  onClick={() => {
                    useAuthStore.getState().logout()
                    window.location.href = '/'
                  }}
                  className="inline-flex items-center gap-2 rounded-full px-3 py-2 text-sm text-slate-400 transition-colors hover:text-red-200"
                >
                  <LogOut className="h-4 w-4" />
                  Salir
                </button>
              </>
            ) : (
              <Link to="/register/demo" className="landing-cta-primary hidden sm:inline-flex">
                Solicitar demo
              </Link>
            )}
          </div>
        </div>
      </header>

      <main>
        {/* 1. HERO */}
        <section className="relative overflow-hidden pt-28 md:pt-36 lg:pt-40">
          <div className="landing-hero-radial" />
          <div className="mx-auto max-w-7xl px-5 pb-20 md:px-6 lg:px-8">
            <div className="relative z-10 max-w-4xl">
              <div className="inline-flex items-center gap-2 rounded-full border border-amber-300/20 bg-amber-300/10 px-4 py-2 font-mono text-[11px] uppercase tracking-[0.28em] text-amber-200">
                <Sparkles className="h-3.5 w-3.5" />
                CID — Sistema de produccion
              </div>

              <h1 className="mt-7 max-w-5xl font-display text-5xl font-semibold leading-[0.88] tracking-[-0.04em] text-white sm:text-6xl md:text-7xl xl:text-[6.1rem]">
                CID — El sistema para desarrollar y producir cine con inteligencia artificial
              </h1>

              <p className="mt-6 max-w-3xl text-lg font-medium leading-8 text-slate-100 md:text-2xl md:leading-10">
                CID conecta creatividad, planificacion y produccion en un flujo de trabajo real. Desde la idea inicial hasta la entrega final, todos los departamentos trabajan coordinados dentro de un mismo sistema.
              </p>

              <div className="mt-5 inline-flex max-w-3xl rounded-[1.4rem] border border-cyan-300/15 bg-cyan-300/10 px-4 py-3 text-sm leading-7 text-cyan-50 backdrop-blur-xl md:text-base">
                No es una herramienta creativa. Es un sistema de produccion audiovisual.
              </div>

              <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
                <Link to="/register/demo" className="landing-cta-primary inline-flex items-center gap-2">
                  Solicitar demo
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <Link to="/pricing" className="landing-cta-secondary inline-flex items-center gap-2">
                  Ver precios
                  <ChevronRight className="h-4 w-4" />
                </Link>
                <Link to="/solutions" className="landing-cta-ghost inline-flex items-center gap-2">
                  Hablar con un especialista
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* 2. PROBLEM */}
        <section className="relative border-y border-white/10 bg-[#09111c]/80 py-28">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <div className="max-w-3xl">
              <p className="editorial-kicker text-amber-300">El problema</p>
              <h2 className="mt-6 font-display text-5xl text-white md:text-6xl">La produccion audiovisual esta fragmentada</h2>
              <p className="mt-8 text-lg leading-9 text-slate-300 md:text-xl md:leading-10">
                Guion, desglose, storyboard, planificacion, rodaje, sonido, postproduccion y entrega funcionan como piezas separadas. Esto genera perdidas de tiempo, errores de coordinacion y sobrecostes.
              </p>
              <p className="mt-6 text-base leading-8 text-slate-400">
                Las herramientas actuales no siempre resuelven el problema: algunas son creativas pero no productivas; otras son tecnicas pero desconectadas del proceso creativo.
              </p>
            </div>
          </div>
        </section>

        {/* 3. SOLUTION */}
        <section className="relative py-28">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <div className="max-w-3xl">
              <p className="editorial-kicker text-amber-300">La solucion</p>
              <h2 className="mt-6 font-display text-5xl text-white md:text-6xl">CID unifica el proceso completo</h2>
              <p className="mt-8 text-lg leading-9 text-slate-300 md:text-xl md:leading-10">
                CID conecta creatividad, planificacion y produccion en un flujo de trabajo real. Desde la idea inicial hasta la entrega final, todos los departamentos trabajan coordinados dentro de un mismo sistema.
              </p>
            </div>
          </div>
        </section>

        {/* 4. PIPELINE */}
        <section className="relative border-y border-white/10 bg-[#09111c]/80 py-28">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <div className="mb-16 max-w-3xl">
              <p className="editorial-kicker text-amber-300">Pipeline</p>
              <h2 className="mt-6 font-display text-5xl text-white md:text-6xl">Flujo visual del proceso</h2>
              <p className="mt-6 text-base leading-8 text-slate-400">
                Cada fase no es un bloque aislado. Esta conectada con la siguiente, manteniendo informacion, intencion creativa y trazabilidad durante todo el proceso.
              </p>
            </div>

            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7">
              {pipelinePhases.map((phase, index) => (
                <div key={phase.name} className="landing-panel rounded-[1.7rem] p-8">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-amber-300">
                    <phase.icon className="h-5 w-5" />
                  </div>
                  <p className="mt-4 text-[11px] uppercase tracking-[0.24em] text-slate-500">0{index + 1}</p>
                  <h3 className="mt-4 text-xl font-semibold text-white">{phase.name}</h3>
                  <p className="mt-4 text-sm leading-6 text-slate-400">{phase.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* 5. DEPARTMENTS */}
        <section className="relative py-28">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <div className="mb-16 max-w-3xl">
              <p className="editorial-kicker text-amber-300">Departamentos</p>
              <h2 className="mt-6 font-display text-5xl text-white md:text-6xl">Diseñado para los departamentos reales de una produccion</h2>
            </div>

            <div className="grid gap-8 md:grid-cols-2 xl:grid-cols-3">
              {departments.map((dept) => (
                <div key={dept.name} className="landing-panel rounded-[1.7rem] p-8">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-amber-300">
                    <dept.icon className="h-5 w-5" />
                  </div>
                  <h3 className="mt-5 text-2xl font-semibold text-white">{dept.name}</h3>
                  <div className="mt-5 flex flex-wrap gap-3">
                    {dept.items.map((item) => (
                      <span key={item} className="landing-pill text-slate-200">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* 6. MODULES */}
        <section className="relative border-y border-white/10 bg-[#09111c]/80 py-24">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <div className="mb-12 max-w-3xl">
              <p className="editorial-kicker text-amber-300">Modulos incluidos</p>
              <h2 className="mt-4 font-display text-4xl text-white md:text-6xl">Herramientas especializadas dentro de CID</h2>
              <p className="mt-4 text-base leading-7 text-slate-400">
                CID incluye modulos que pueden funcionar por separado o conectados dentro del sistema completo.
              </p>
            </div>

            <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
              {modules.map((mod) => (
                <div key={mod.name} className="landing-panel rounded-[1.7rem] p-6">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-amber-300">
                    <mod.icon className="h-5 w-5" />
                  </div>
                  <h3 className="mt-4 text-xl font-semibold text-white">{mod.name}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-300">{mod.description}</p>
                </div>
              ))}
            </div>

            <div className="mt-8 rounded-[1.4rem] border border-cyan-300/15 bg-cyan-300/10 px-5 py-4 text-sm leading-7 text-cyan-50">
              Cada herramienta esta diseñada para un departamento real y funciona de forma coordinada con el resto del sistema.
            </div>
          </div>
        </section>

        {/* 7. DIFFERENTIAL */}
        <section className="relative py-24">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <div className="max-w-3xl">
              <p className="editorial-kicker text-amber-300">Diferencial</p>
              <h2 className="mt-4 font-display text-4xl text-white md:text-6xl">Mas alla de un canvas creativo</h2>
              <p className="mt-6 text-lg leading-8 text-slate-300 md:text-xl md:leading-9">
                CID no se limita a generar contenido. Une creatividad visual, lienzo colaborativo, inteligencia artificial y produccion cinematografica real.
              </p>

              <div className="mt-8 grid gap-4 sm:grid-cols-2">
                {[
                  'No es solo generacion de imagenes o video',
                  'No es un lienzo creativo aislado',
                  'No es un software tecnico desconectado del proceso',
                  'Es un sistema completo de produccion audiovisual',
                ].map((item) => (
                  <div key={item} className="landing-panel rounded-[1.4rem] p-4">
                    <p className="text-sm leading-6 text-slate-300">{item}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* 8. IMPLEMENTATION */}
        <section className="relative border-y border-white/10 bg-[#09111c]/80 py-24">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <div className="max-w-3xl">
              <p className="editorial-kicker text-amber-300">Implementacion</p>
              <h2 className="mt-4 font-display text-4xl text-white md:text-6xl">Software con acompañamiento real</h2>
              <p className="mt-6 text-lg leading-8 text-slate-300 md:text-xl md:leading-9">
                CID no se entrega como una herramienta generica. Se adapta al flujo de trabajo de cada productora, equipo o proyecto.
              </p>

              <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {[
                  'Diagnostico inicial',
                  'Configuracion del sistema',
                  'Adaptacion al flujo de trabajo',
                  'Integracion con herramientas existentes',
                  'Acompañamiento tecnico durante la produccion',
                ].map((item) => (
                  <div key={item} className="landing-panel rounded-[1.4rem] p-4">
                    <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-amber-300/10 text-amber-300">
                      <Waypoints className="h-4 w-4" />
                    </div>
                    <p className="mt-3 text-sm font-medium text-white">{item}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* 9. PRICING */}
        <section className="relative py-24">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <div className="mb-12 max-w-3xl">
              <p className="editorial-kicker text-amber-300">Modelo de acceso</p>
              <h2 className="mt-4 font-display text-4xl text-white md:text-6xl">Precios pensados para produccion real</h2>
            </div>

            <div className="flex gap-3 mb-8">
              <button
                onClick={() => setActivePricing('setup')}
                className={`rounded-full px-5 py-2 text-sm font-medium transition-all ${
                  activePricing === 'setup'
                    ? 'bg-amber-500 text-black'
                    : 'border border-white/10 bg-white/5 text-slate-300 hover:border-white/20'
                }`}
              >
                Setup + Cuota
              </button>
              <button
                onClick={() => setActivePricing('modules')}
                className={`rounded-full px-5 py-2 text-sm font-medium transition-all ${
                  activePricing === 'modules'
                    ? 'bg-amber-500 text-black'
                    : 'border border-white/10 bg-white/5 text-slate-300 hover:border-white/20'
                }`}
              >
                Modulos
              </button>
            </div>

            {activePricing === 'setup' ? (
              <div className="grid gap-6 xl:grid-cols-[0.52fr_0.48fr]">
                <div className="solution-card solution-card-featured">
                  <p className="solution-eyebrow text-amber-300">Setup + Cuota mensual</p>
                  <h3 className="mt-3 text-3xl font-semibold text-white">CID completo</h3>
                  <div className="mt-6 space-y-3">
                    <p className="text-sm leading-7 text-slate-300">Setup inicial desde 1.500 EUR</p>
                    <p className="text-sm leading-7 text-slate-300">Cuota mensual desde 299 EUR/mes</p>
                    <p className="text-sm leading-7 text-slate-300">Incluye todos los modulos</p>
                  </div>
                  <p className="mt-6 text-sm leading-7 text-slate-400">
                    Requiere demo y diagnostico previo para adaptar el flujo a la produccion real.
                  </p>
                </div>

                <div className="solution-card">
                  <p className="solution-eyebrow text-cyan-200">Incluye</p>
                  <div className="mt-4 flex flex-wrap gap-2.5">
                    {['Script & Breakdown AI', 'Storyboard AI Studio', 'Production Planner AI', 'DubbingTake Studio AI', 'Sound Post AI', 'Promo Video AI', 'VFX & Enhancement AI'].map((mod) => (
                      <span key={mod} className="landing-pill text-slate-200">
                        {mod}
                      </span>
                    ))}
                  </div>
                  <p className="mt-6 text-sm leading-7 text-slate-300">
                    El setup inicial existe porque CID se adapta al flujo real de la produccion, al modelo de aprobaciones y a la forma de trabajar de cada equipo.
                  </p>
                </div>
              </div>
            ) : (
              <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
                {[
                  { name: 'Script & Breakdown AI', price: 'Desde 49 EUR/mes' },
                  { name: 'Storyboard AI Studio', price: 'Desde 59 EUR/mes' },
                  { name: 'Production Planner AI', price: 'Desde 69 EUR/mes' },
                  { name: 'DubbingTake Studio AI', price: 'Desde 79 EUR/mes' },
                  { name: 'Sound Post AI', price: 'Desde 79 EUR/mes' },
                  { name: 'Promo Video AI', price: 'Desde 89 EUR/mes' },
                  { name: 'VFX & Enhancement AI', price: 'Desde 99 EUR/mes' },
                ].map((mod) => (
                  <div key={mod.name} className="solution-card rounded-[1.7rem] p-6">
                    <h3 className="text-lg font-semibold text-white">{mod.name}</h3>
                    <p className="mt-2 text-sm text-amber-200">{mod.price}</p>
                  </div>
                ))}
              </div>
            )}

            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link to="/pricing" className="landing-cta-primary inline-flex items-center gap-2">
                Ver precios completos
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link to="/register/demo" className="landing-cta-secondary inline-flex items-center gap-2">
                Solicitar propuesta
                <ChevronRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </section>

        {/* 10. USE CASES */}
        <section className="relative border-y border-white/10 bg-[#09111c]/80 py-24">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <div className="mb-12 max-w-3xl">
              <p className="editorial-kicker text-amber-300">Casos de uso</p>
              <h2 className="mt-4 font-display text-4xl text-white md:text-6xl">Pensado para proyectos audiovisuales reales</h2>
            </div>

            <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {useCases.map((useCase) => (
                <div key={useCase.name} className="landing-panel rounded-[1.7rem] p-6">
                  <h3 className="text-xl font-semibold text-white">{useCase.name}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-300">{useCase.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* 11. CLOSING */}
        <section className="relative py-24">
          <div className="mx-auto max-w-6xl px-5 text-center md:px-6 lg:px-8">
            <div className="landing-brand-final-cta rounded-[2.4rem] p-8 sm:p-10 lg:p-12">
              <p className="editorial-kicker text-amber-300">Cierrre</p>
              <h2 className="mt-4 max-w-4xl mx-auto font-display text-4xl font-semibold leading-[0.92] text-white md:text-6xl">
                La inteligencia artificial no sustituye la creatividad. La organiza, la acelera y la conecta.
              </h2>
              <blockquote className="mt-6 max-w-4xl mx-auto text-lg leading-9 text-slate-100 md:text-2xl md:leading-[1.6]">
                CID convierte la creacion audiovisual en un sistema de produccion real.
              </blockquote>

              <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
                <Link to="/register/demo" className="landing-cta-primary inline-flex items-center justify-center gap-2">
                  Solicitar demo
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <Link to="/solutions" className="landing-cta-secondary inline-flex items-center justify-center gap-2">
                  Hablar con nosotros
                  <ChevronRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 py-10">
        <div className="mx-auto grid max-w-7xl gap-8 px-5 md:px-6 lg:grid-cols-[1fr_auto] lg:items-center lg:px-8">
          <div>
            <p className="font-display text-3xl text-white">AILinkCinema / CID</p>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-400">
              Sistema completo para desarrollo, produccion, post y entrega con todos los modulos conectados.
            </p>
          </div>

          <div className="flex flex-col gap-4 sm:items-end">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center lg:justify-end">
              <Link to="/solutions" className="text-sm text-slate-300 transition-colors hover:text-white">
                Soluciones
              </Link>
              <Link to="/pricing" className="text-sm text-slate-300 transition-colors hover:text-white">
                Precios
              </Link>
              <Link to="/solutions/cid" className="text-sm text-slate-300 transition-colors hover:text-white">
                Explorar CID
              </Link>
              <Link to="/register/demo" className="text-sm text-slate-300 transition-colors hover:text-white">
                Solicitar demo
              </Link>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center lg:justify-end">
              <Link to="/legal/privacidad" className="text-xs text-slate-500 transition-colors hover:text-slate-200">
                Privacidad
              </Link>
              <Link to="/legal/aviso-legal" className="text-xs text-slate-500 transition-colors hover:text-slate-200">
                Aviso legal
              </Link>
              <Link to="/legal/terminos" className="text-xs text-slate-500 transition-colors hover:text-slate-200">
                Terminos
              </Link>
              <Link to="/legal/ia-y-contenidos" className="text-xs text-slate-500 transition-colors hover:text-slate-200">
                IA y contenidos
              </Link>
            </div>
          </div>
        </div>

        <div className="mx-auto mt-8 flex max-w-7xl items-center gap-3 px-5 text-sm text-slate-500 md:px-6 lg:px-8">
          <ShieldCheck className="h-4 w-4 text-amber-300" />
          <p>CID tiene setup inicial porque se adapta al flujo real de cada produccion.</p>
        </div>
      </footer>
    </div>
  )
}
