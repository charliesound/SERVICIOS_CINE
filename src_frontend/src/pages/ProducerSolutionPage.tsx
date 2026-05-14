import { Link } from 'react-router-dom'
import {
  ArrowRight,
  ChevronRight,
  Clapperboard,
  Sparkles,
  BarChart3,
  Coins,
  Calendar,
  FileSearch,
  LineChart,
  LogOut,
  ShieldCheck,
  User,
  Mail,
  Send,
  LayoutDashboard,
  Wallet,
  FileStack,
  PieChart,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import LandingAmbientScene from '@/components/landing/LandingAmbientScene'
import LandingReveal from '@/components/landing/LandingReveal'
import { useSeo } from '@/hooks/useSeo'
import { useAuthStore } from '@/store'
import { buildAbsoluteUrl } from '@/utils/seo'

const problemItems = [
  {
    title: 'Incertidumbre presupuestaria',
    text: 'Dificultad para estimar costes reales en fases tempranas, lo que compromete la viabilidad y la busqueda de socios.',
  },
  {
    title: 'Documentacion fragmentada',
    text: 'Gestionar dossieres, planes de financiacion y desgloses en herramientas inconexas genera errores y perdida de tiempo.',
  },
  {
    title: 'Complejidad en subvenciones',
    text: 'Preparar la documentacion tecnica y financiera necesaria para ayudas publicas y desgravaciones sin una estructura solida.',
  },
  {
    title: 'Falta de control en tiempo real',
    text: 'Desconexion entre lo que se planifica y lo que ocurre en rodaje, dificultando la toma de decisiones financieras urgentes.',
  },
  {
    title: 'Coordinacion multidepartamental',
    text: 'Alinear la vision creativa con las restricciones presupuestarias y las necesidades de distribucion y ventas.',
  },
]

const solutionItems = [
  {
    icon: FileSearch,
    title: 'Analisis de viabilidad',
    text: 'Analisis tecnico y financiero del proyecto desde el guion para detectar necesidades operativas y puntos criticos.',
  },
  {
    icon: BarChart3,
    title: 'Presupuesto inteligente',
    text: 'Estimacion de costes asistida por IA basada en el desglose real del proyecto, localizaciones y equipo necesario.',
  },
  {
    icon: Coins,
    title: 'Financiacion y subvenciones',
    text: 'Herramientas para estructurar el plan de financiacion y generar la documentacion para ayudas y tax rebates.',
  },
  {
    icon: Calendar,
    title: 'Planificacion operativa',
    text: 'Calendario de produccion conectado a recursos, jornadas y dependencias reales entre departamentos.',
  },
  {
    icon: FileStack,
    title: 'Gestion documental',
    text: 'Centralizacion de contratos, permisos y documentacion legal con trazabilidad completa para auditorias.',
  },
  {
    icon: PieChart,
    title: 'Control de produccion',
    text: 'Seguimiento del estado de produccion, costes incurridos y desviaciones respecto al plan inicial.',
  },
  {
    icon: LineChart,
    title: 'Distribucion y ventas',
    text: 'Preparacion de materiales para preventa, mercados y seguimiento de la circulacion comercial del proyecto.',
  },
]

const mvpSteps = [
  { number: '01', title: 'Subir proyecto', text: 'Sube tu guion o documentacion base. El sistema mapea la estructura y necesidades del proyecto.' },
  { number: '02', title: 'Analizar viabilidad', text: 'Analisis de recursos, localizaciones y personal para establecer una base operativa solida.' },
  { number: '03', title: 'Generar presupuesto', text: 'Crea una primera version del presupuesto conectada directamente al analisis tecnico del proyecto.' },
  { number: '04', title: 'Paquete ejecutivo', text: 'Genera el Executive Production Pack con toda la documentacion necesaria para financiacion y pitching.' },
  { number: '05', title: 'Planificar y operar', text: 'Establece el plan de rodaje y haz seguimiento de la produccion real integrada en el sistema CID.' },
]

interface FormField {
  label: string
  name: string
  type: string
  placeholder: string
  icon?: LucideIcon
  options?: string[]
}

const formFields: FormField[] = [
  { label: 'Nombre completo', name: 'nombre', type: 'text', placeholder: 'Tu nombre', icon: User },
  { label: 'Email', name: 'email', type: 'email', placeholder: 'tu@email.com', icon: Mail },
  { label: 'Tipo de produccion', name: 'tipoProduccion', type: 'select', placeholder: 'Selecciona tipo', options: ['Largometraje', 'Serie', 'Publicidad', 'Documental', 'Animacion'] },
  { label: 'Necesidad principal', name: 'necesidad', type: 'select', placeholder: 'Selecciona necesidad', options: ['Financiacion', 'Presupuesto / Desglose', 'Planificacion', 'Control de produccion', 'Distribucion', 'Otro'] },
]

export default function ProducerSolutionPage() {
  const { isAuthenticated, user } = useAuthStore()
  const cidTarget = user ? '/cid' : '/login'

  useSeo({
    title: 'Producer AI Studio | AILinkCinema',
    description:
      'Control total de tu produccion cinematografica: analisis de viabilidad, presupuesto inteligente, financiacion, planificacion y seguimiento real con IA.',
    path: '/soluciones/productor',
    keywords: [
      'productor ai studio',
      'produccion cinematografica',
      'presupuesto cine',
      'financiacion audiovisual',
      'executive production pack',
      'planificacion de rodaje',
    ],
    structuredData: [
      {
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        name: 'Producer AI Studio',
        applicationCategory: 'BusinessApplication',
        operatingSystem: 'Web',
        url: buildAbsoluteUrl('/soluciones/productor'),
        description:
          'Control total de tu produccion cinematografica: analisis de viabilidad, presupuesto, financiacion y planificacion.',
      },
    ],
  })

  const scrollToForm = () => {
    const el = document.getElementById('producer-form')
    el?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <div className="landing-shell landing-cinematic-shell min-h-screen text-white">
      <LandingAmbientScene />
      <div className="landing-noise" />
      <div className="landing-backdrop" />

      <header className="fixed inset-x-0 top-0 z-50 border-b border-white/5 bg-[#080808]/70 backdrop-blur-2xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-3 md:px-6 lg:px-8 lg:py-4">
          <Link to="/" className="flex items-center gap-3 md:gap-4">
            <img
              src="/assets/ailinkcinema-logo.png"
              alt="AILinkCinema"
              className="h-11 w-11 rounded-2xl object-cover shadow-[0_0_36px_rgba(245,158,11,0.28)] md:h-14 md:w-14"
            />
            <div>
              <p className="text-xl font-bold tracking-tight text-white md:text-2xl landing-brand-name">AILinkCinema</p>
              <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-amber-400/60 md:text-[11px]">
                Producer AI Studio
              </p>
            </div>
          </Link>

          <nav className="hidden items-center gap-7 text-sm text-slate-300 xl:flex">
            <a href="#problema" className="transition-colors hover:text-white">Problema</a>
            <a href="#solucion" className="transition-colors hover:text-white">Solucion</a>
            <a href="#flujo" className="transition-colors hover:text-white">Flujo</a>
            <a href="#resultado" className="transition-colors hover:text-white">Resultado</a>
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
              <Link to="/pricing" className="landing-cta-primary hidden sm:inline-flex">
                Ver precios
                <ArrowRight className="h-4 w-4" />
              </Link>
            )}
          </div>
        </div>
      </header>

      <main>
        {/* HERO */}
        <section className="relative min-h-[90vh] overflow-hidden flex items-center">
          <div className="landing-cinematic-hero-bg" />
          <div className="landing-cinematic-glow-top" />
          <div className="landing-cinematic-glow-side" />

          <div className="relative z-10 mx-auto max-w-7xl px-5 pt-32 pb-20 md:px-8 md:pt-40 md:pb-28">
            <div className="max-w-3xl">
              <div className="inline-flex items-center gap-2 rounded-full border border-amber-400/20 bg-amber-400/10 px-4 py-2 font-mono text-[11px] uppercase tracking-[0.28em] text-amber-300">
                <Wallet className="h-3.5 w-3.5" />
                Producer AI Studio
              </div>

              <h1 className="mt-8 font-display text-5xl font-semibold leading-[0.92] tracking-[-0.04em] text-white sm:text-6xl md:text-7xl lg:text-8xl">
                Producción cinematográfica <span className="text-gradient-amber">asistida por IA</span>
              </h1>

              <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300 md:text-xl md:leading-9">
                Toma el control total de tu proyecto: desde el analisis de viabilidad y presupuesto hasta
                la financiacion, planificacion operativa y seguimiento de produccion en tiempo real.
              </p>

              <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
                <button
                  onClick={scrollToForm}
                  className="landing-cta-primary"
                >
                  Preparar mi proyecto
                  <ArrowRight className="h-4 w-4" />
                </button>
                <a href="#flujo" className="landing-cta-secondary">
                  Como funciona
                  <ChevronRight className="h-4 w-4" />
                </a>
              </div>
            </div>
          </div>
        </section>

        {/* PROBLEMA */}
        <section id="problema" className="relative border-t border-white/5 py-24 md:py-32">
          <div className="mx-auto max-w-7xl px-5 md:px-8">
            <LandingReveal>
              <div className="mx-auto max-w-3xl text-center">
                <p className="editorial-kicker text-amber-300/90">El problema</p>
                <h2 className="mt-4 font-display text-4xl font-semibold leading-[1.1] text-white md:text-5xl">
                  Gestionar la complejidad de una <span className="text-gradient-amber">produccion moderna</span>
                </h2>
                <p className="mt-4 text-lg leading-8 text-slate-400">
                  La produccion audiovisual actual requiere un control exhaustivo de datos, costes y documentacion que las herramientas tradicionales no pueden ofrecer de forma integrada.
                </p>
              </div>
            </LandingReveal>

            <div className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {problemItems.map((item) => (
                <LandingReveal key={item.title}>
                  <div className="landing-creative-card h-full">
                    <h3 className="text-base font-semibold text-white">{item.title}</h3>
                    <p className="mt-2 text-sm leading-7 text-slate-400">{item.text}</p>
                  </div>
                </LandingReveal>
              ))}
            </div>
          </div>
        </section>

        {/* SOLUCION */}
        <section id="solucion" className="relative border-t border-white/5 bg-[#09111c]/40 py-24 md:py-32">
          <div className="mx-auto max-w-7xl px-5 md:px-8">
            <LandingReveal>
              <div className="mx-auto max-w-3xl text-center">
                <p className="editorial-kicker text-amber-300/90">La solucion</p>
                <h2 className="mt-4 font-display text-4xl font-semibold leading-[1.1] text-white md:text-5xl">
                  CID como centro de <span className="text-gradient-amber">control de produccion</span>
                </h2>
                <p className="mt-4 text-lg leading-8 text-slate-400">
                  Un sistema integral que conecta las decisiones de produccion con la realidad operativa de todos los departamentos.
                </p>
              </div>
            </LandingReveal>

            <div className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {solutionItems.map((item) => {
                const Icon = item.icon
                return (
                  <LandingReveal key={item.title}>
                    <div className="landing-creative-card h-full">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10">
                          <Icon className="h-5 w-5 text-amber-400" />
                        </div>
                        <h3 className="text-sm font-semibold text-white">{item.title}</h3>
                      </div>
                      <p className="mt-3 text-sm leading-7 text-slate-400">{item.text}</p>
                    </div>
                  </LandingReveal>
                )
              })}
            </div>
          </div>
        </section>

        {/* FLUJO MVP */}
        <section id="flujo" className="relative border-t border-white/5 py-24 md:py-32">
          <div className="mx-auto max-w-7xl px-5 md:px-8">
            <LandingReveal>
              <div className="mx-auto max-w-3xl text-center">
                <p className="editorial-kicker text-amber-300/90">Flujo de trabajo</p>
                <h2 className="mt-4 font-display text-4xl font-semibold leading-[1.1] text-white md:text-5xl">
                  Gestiona tu produccion <span className="text-gradient-amber">paso a paso</span>
                </h2>
                <p className="mt-4 text-lg leading-8 text-slate-400">
                  Desde la idea inicial hasta el cierre de produccion, un camino guiado y trazable.
                </p>
              </div>
            </LandingReveal>

            <div className="mt-14">
              <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
                {mvpSteps.map((step, index) => (
                  <LandingReveal key={step.number} delay={index * 85}>
                    <div className="landing-pipeline-step h-full">
                      <div className="landing-pipeline-step-header">
                        <span className="landing-pipeline-step-number rounded-full border border-amber-400/20 bg-amber-400/10 text-amber-300">
                          {step.number}
                        </span>
                      </div>
                      <h3 className="mt-4 text-base font-semibold text-white">{step.title}</h3>
                      <p className="mt-3 text-sm leading-7 text-slate-400">{step.text}</p>
                    </div>
                  </LandingReveal>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* RESULTADO ESPERADO */}
        <section id="resultado" className="relative border-t border-white/5 bg-[#09111c]/40 py-24 md:py-32">
          <div className="mx-auto max-w-7xl px-5 md:px-8">
            <div className="grid gap-8 xl:grid-cols-[0.55fr_0.45fr] xl:items-center">
              <LandingReveal>
                <div>
                  <p className="editorial-kicker text-amber-300/90">Resultado esperado</p>
                  <h2 className="mt-4 font-display text-4xl font-semibold leading-[1.1] text-white md:text-5xl">
                    Executive Production Pack <span className="text-gradient-amber">listo para inversores y partners</span>
                  </h2>
                  <p className="mt-4 text-lg leading-8 text-slate-400">
                    Toda la documentacion estrategica, financiera y operativa compilada en un paquete
                    ejecutivo profesional que garantiza la solidez de tu proyecto.
                  </p>
                  <ul className="mt-8 space-y-4">
                    {[
                      'Presupuesto detallado por departamentos',
                      'Plan de financiacion y calendario de ayudas',
                      'Analisis de viabilidad y desglose tecnico',
                      'Cronograma operativo de produccion',
                      'Documentacion legal y de compliance base',
                    ].map((item) => (
                      <li key={item} className="flex items-start gap-3 text-sm text-slate-300">
                        <span className="mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-amber-400/20 bg-amber-400/10">
                          <span className="h-1.5 w-1.5 rounded-full bg-amber-400" />
                        </span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              </LandingReveal>

              <LandingReveal delay={120}>
                <div className="solution-hero-panel">
                  <div className="solution-grid-overlay" />
                  <div className="relative z-10">
                    <div className="flex items-center gap-2 text-amber-300">
                      <FileStack className="h-5 w-5" />
                      <span className="solution-eyebrow">Executive Production Pack</span>
                    </div>
                    <p className="mt-4 font-display text-2xl font-semibold text-white">Proyecto de Producción</p>
                    <p className="mt-1 text-sm text-slate-400">Productora Ejecutiva / CID Studio</p>
                    <div className="mt-6 space-y-3">
                      {['Plan Financiero', 'Presupuesto', 'Cronograma', 'Analisis Legal'].map((section) => (
                        <div key={section} className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3">
                          <Clapperboard className="h-4 w-4 text-amber-400" />
                          <span className="text-sm text-slate-200">{section}</span>
                        </div>
                      ))}
                    </div>
                    <div className="mt-6 flex flex-wrap gap-2">
                      {['Financiado 65%', 'Preprod', 'Ventas Int', '+4'].map((tag) => (
                        <span key={tag} className="landing-pill text-xs">{tag}</span>
                      ))}
                    </div>
                  </div>
                </div>
              </LandingReveal>
            </div>
          </div>
        </section>

        {/* BETA PRIVADA CTA */}
        <section className="relative border-y border-white/10 py-20">
          <div className="landing-section-glow-left" />
          <div className="landing-section-glow-right" />
          <div className="mx-auto max-w-4xl px-5 text-center md:px-8">
            <LandingReveal>
              <div className="landing-brand-final-cta rounded-[2.4rem] p-8 sm:p-10 lg:p-12">
                <Sparkles className="mx-auto h-8 w-8 text-amber-400" />
                <p className="mt-4 font-display text-2xl font-semibold leading-snug text-white md:text-3xl">
                  Acceso anticipado a Producer AI Studio.
                </p>
                <p className="mt-3 text-base leading-7 text-slate-300">
                  Estamos seleccionando productoras para el programa de implementacion CID.
                  Optimiza tus procesos y toma el control de tu proxima produccion.
                </p>
                <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
                  <button
                    onClick={scrollToForm}
                    className="landing-cta-primary"
                  >
                    Solicitar acceso
                    <ArrowRight className="h-4 w-4" />
                  </button>
                  <Link to="/solutions" className="landing-cta-secondary">
                    Ver todas las soluciones
                    <ChevronRight className="h-4 w-4" />
                  </Link>
                </div>
              </div>
            </LandingReveal>
          </div>
        </section>

        {/* FORMULARIO VISUAL */}
        <section id="producer-form" className="relative border-t border-white/5 bg-[#09111c]/40 py-24 md:py-32">
          <div className="mx-auto max-w-3xl px-5 md:px-8">
            <LandingReveal>
              <div className="text-center">
                <p className="editorial-kicker text-amber-300/90">Prueba Producer AI Studio</p>
                <h2 className="mt-4 font-display text-4xl font-semibold leading-[1.1] text-white md:text-5xl">
                  Impulsa tu <span className="text-gradient-amber">proxima produccion</span>
                </h2>
                <p className="mt-4 text-lg leading-8 text-slate-400">
                  Rellena el formulario y evaluaremos tu proyecto para el acceso a la beta de gestion.
                </p>
              </div>
            </LandingReveal>

            <LandingReveal>
              <div className="mt-12">
                <form onSubmit={(e) => e.preventDefault()} className="space-y-6">
                  <div className="grid gap-5 sm:grid-cols-2">
                    {formFields.slice(0, 2).map((field) => {
                      const IconComponent = field.icon as LucideIcon
                      return (
                        <div key={field.name}>
                          <label className="label" htmlFor={field.name}>{field.label}</label>
                          <div className="relative">
                            <IconComponent className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                            <input
                              id={field.name}
                              name={field.name}
                              type={field.type}
                              className="input pl-10"
                              placeholder={field.placeholder}
                              readOnly
                            />
                          </div>
                        </div>
                      )
                    })}
                  </div>

                  <div className="grid gap-5 sm:grid-cols-2">
                    {formFields.slice(2).map((field) => {
                      const options = field.options as string[]
                      return (
                        <div key={field.name}>
                          <label className="label" htmlFor={field.name}>{field.label}</label>
                          <select
                            id={field.name}
                            name={field.name}
                            className="input"
                            defaultValue=""
                          >
                            <option value="" disabled>{field.placeholder}</option>
                            {options.map((opt) => (
                              <option key={opt} value={opt}>{opt}</option>
                            ))}
                          </select>
                        </div>
                      )
                    })}
                  </div>

                  <div>
                    <label className="label" htmlFor="descripcion">Estado actual del proyecto</label>
                    <textarea
                      id="descripcion"
                      name="descripcion"
                      rows={3}
                      className="input resize-none"
                      placeholder="Cuentanos en que fase esta el proyecto (desarrollo, preprod...) y tus necesidades de gestion..."
                      readOnly
                    />
                  </div>

                  <div className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      id="acepta"
                      className="mt-1 h-4 w-4 rounded border-white/20 bg-white/5 text-amber-500 focus:ring-amber-500/30"
                      checked
                      readOnly
                    />
                    <label htmlFor="acepta" className="text-sm text-slate-400">
                      Acepto que me contacten para gestionar esta solicitud de acceso a Producer AI Studio.
                    </label>
                  </div>

                  <button
                    type="submit"
                    className="landing-cta-primary w-full justify-center py-4 text-base opacity-60 cursor-not-allowed"
                    disabled
                  >
                    <Send className="h-4 w-4" />
                    Enviar solicitud
                  </button>
                </form>
              </div>
            </LandingReveal>
          </div>
        </section>

        {/* CTA FINAL */}
        <section className="relative border-t border-white/5 py-24 md:py-32">
          <div className="landing-section-glow-left" />
          <div className="landing-section-glow-right" />
          <div className="mx-auto max-w-5xl px-5 text-center md:px-8">
            <LandingReveal>
              <div className="landing-brand-final-cta rounded-[2.4rem] p-8 sm:p-10 lg:p-12">
                <h2 className="font-display text-4xl font-semibold leading-[0.92] text-white md:text-6xl">
                  El control que tu produccion merece
                </h2>
                <p className="mt-6 max-w-2xl mx-auto text-lg leading-8 text-slate-300">
                  Producer AI Studio te da las herramientas financieras y operativas para llevar tu proyecto al siguiente nivel.
                </p>
                <div className="mt-10 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
                  <button
                    onClick={scrollToForm}
                    className="landing-cta-primary text-base"
                  >
                    Empezar ahora
                    <ArrowRight className="h-4 w-4" />
                  </button>
                  <Link
                    to="/solutions/cid"
                    className="landing-cta-secondary"
                  >
                    Explorar CID
                    <ChevronRight className="h-4 w-4" />
                  </Link>
                </div>
              </div>
            </LandingReveal>
          </div>
        </section>
      </main>

      <footer className="border-t border-white/5 py-10">
        <div className="mx-auto grid max-w-7xl gap-8 px-5 md:px-6 lg:grid-cols-[1fr_auto] lg:items-center lg:px-8">
          <div>
            <p className="font-display text-3xl text-white">AILinkCinema</p>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-400">
              Inteligencia artificial para cine, television y publicidad con software especializado, CID como sistema central y acompanamiento tecnico real.
            </p>
          </div>

          <div className="flex flex-col gap-4 sm:items-end">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center lg:justify-end">
              <Link to="/solutions/cid" className="text-sm text-slate-300 transition-colors hover:text-white">
                Explorar CID
              </Link>
              <Link to="/register/demo" className="text-sm text-slate-300 transition-colors hover:text-white">
                Solicitar demo
              </Link>
              <Link to="/solutions" className="text-sm text-slate-300 transition-colors hover:text-white">
                Ver soluciones
              </Link>
              <Link to="/pricing" className="text-sm text-slate-300 transition-colors hover:text-white">
                Precios
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
          <p>AILinkCinema posiciona a CID como sistema completo de produccion audiovisual y articula soluciones especializadas para cada departamento.</p>
        </div>
      </footer>
    </div>
  )
}
