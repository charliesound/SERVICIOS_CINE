import { Link } from 'react-router-dom'
import {
  ArrowRight,
  ChevronRight,
  Clapperboard,
  Sparkles,
  FileText,
  Image,
  Palette,
  BookOpen,
  Camera,
  Film,
  Send,
  LayoutDashboard,
  LogOut,
  ShieldCheck,
  User,
  Mail,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import LandingAmbientScene from '@/components/landing/LandingAmbientScene'
import LandingReveal from '@/components/landing/LandingReveal'
import { useSeo } from '@/hooks/useSeo'
import { useAuthStore } from '@/store'
import { buildAbsoluteUrl } from '@/utils/seo'

const problemItems = [
  {
    title: 'Sin referencias visuales compartidas',
    text: 'El equipo interpreta el guion sin una base visual comun, generando desalineacion entre direccion, produccion y fotografia.',
  },
  {
    title: 'Dificultad para defender la vision',
    text: 'Comunicar la intencion estetica y dramatica a productores, DOP y disenadores sin storyboard ni tono visual definido.',
  },
  {
    title: 'Pitching debil sin material visual',
    text: 'Presentar un proyecto a financiacion o plataformas sin un dossier que transmita la experiencia cinematografica.',
  },
  {
    title: 'Preproduccion sin hoja de ruta',
    text: 'Arrancar el rodaje sin haber definido secuencias clave, tono dramatico ni referencias visuales por escena.',
  },
]

const solutionItems = [
  {
    icon: FileText,
    title: 'Analisis dramatico del guion',
    text: 'Lectura estructurada por actos, personajes, arcos narrativos y ritmo dramatico para entender la columna vertebral de la historia.',
  },
  {
    icon: Palette,
    title: 'Definicion de tono visual',
    text: 'Paleta cromatica, texturas, referencias de iluminacion y atmosfera por secuencia para alinear el lenguaje visual.',
  },
  {
    icon: Camera,
    title: 'Referencias cinematograficas',
    text: 'Seleccion de referentes visuales y cinematograficos que inspiran el tratamiento estetico de cada bloque narrativo.',
  },
  {
    icon: Image,
    title: 'Storyboard por secuencias clave',
    text: 'Representacion visual de las secuencias fundamentales para comunicar puesta en escena, angulacion y bloqueo.',
  },
  {
    icon: BookOpen,
    title: 'Dossier creativo del director',
    text: 'Documento ejecutivo que compila analisis, tono visual, storyboard y referencias para preproduccion o pitching.',
  },
]

const mvpSteps = [
  { number: '01', title: 'Subir guion', text: 'Sube tu guion en formato digital. Aceptamos PDF, Fountain, Final Draft o documentacion de proyecto.' },
  { number: '02', title: 'Analizar estructura', text: 'El sistema procesa el guion y extrae actos, personajes, escenarios, dialogo y estructura dramatica.' },
  { number: '03', title: 'Seleccionar secuencias', text: 'Identifica las secuencias clave con mayor peso narrativo y visual para el desarrollo del storyboard.' },
  { number: '04', title: 'Generar storyboard', text: 'Crea representaciones visuales de cada secuencia seleccionada con angulacion, composicion y tono.' },
  { number: '05', title: 'Exportar dossier', text: 'Compila el analisis completo, tono visual, storyboard y referencias en un dossier del director listo para compartir.' },
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
  { label: 'Tipo de proyecto', name: 'tipoProyecto', type: 'select', placeholder: 'Selecciona tipo', options: ['Largometraje', 'Cortometraje', 'Serie', 'Documental', 'Animacion', 'Otro'] },
  { label: 'Objetivo principal', name: 'objetivo', type: 'select', placeholder: 'Selecciona objetivo', options: ['Pitching / Financiacion', 'Preproduccion', 'Analisis narrativo', 'Storyboard', 'Dossier creativo', 'Otro'] },
]

export default function DirectorSolutionPage() {
  const { isAuthenticated, user } = useAuthStore()
  const cidTarget = user ? '/cid' : '/login'

  useSeo({
    title: 'Director AI Studio | AILinkCinema',
    description:
      'Convierte un guion en una vision cinematografica clara: analisis dramatico, tono visual, secuencias clave, storyboard y dossier creativo para preproduccion o pitching.',
    path: '/soluciones/director',
    keywords: [
      'director ai studio',
      'storyboard',
      'vision del director',
      'analisis de guion',
      'dossier creativo',
      'preproduccion cinematografica',
    ],
    structuredData: [
      {
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        name: 'Director AI Studio',
        applicationCategory: 'BusinessApplication',
        operatingSystem: 'Web',
        url: buildAbsoluteUrl('/soluciones/director'),
        description:
          'Convierte un guion en una vision cinematografica clara: analisis dramatico, tono visual, secuencias clave, storyboard y dossier creativo.',
      },
    ],
  })

  const scrollToForm = () => {
    const el = document.getElementById('director-form')
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
                Director AI Studio
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
                <Clapperboard className="h-3.5 w-3.5" />
                Director AI Studio
              </div>

              <h1 className="mt-8 font-display text-5xl font-semibold leading-[0.92] tracking-[-0.04em] text-white sm:text-6xl md:text-7xl lg:text-8xl">
                Del guion a la <span className="text-gradient-amber">vision del director</span>
              </h1>

              <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300 md:text-xl md:leading-9">
                Convierte un guion en una vision cinematografica clara: analisis dramatico, tono visual,
                secuencias clave, storyboard y dossier creativo para preproduccion o pitching.
              </p>

              <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
                <button
                  onClick={scrollToForm}
                  className="landing-cta-primary"
                >
                  Probar con mi guion
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
                  Visualizar, explicar y defender una pelicula <span className="text-gradient-amber">antes del rodaje</span>
                </h2>
                <p className="mt-4 text-lg leading-8 text-slate-400">
                  Todo director se enfrenta a los mismos desafios cuando necesita comunicar su vision antes de que exista un solo fotograma rodado.
                </p>
              </div>
            </LandingReveal>

            <div className="mt-14 grid gap-4 sm:grid-cols-2">
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
                  Todo lo que un director necesita para <span className="text-gradient-amber">preparar su pelicula</span>
                </h2>
                <p className="mt-4 text-lg leading-8 text-slate-400">
                  Un conjunto de herramientas conectadas que transforman el guion en material visual y estrategico para preproduccion o pitching.
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
                  Del guion al dossier del director <span className="text-gradient-amber">en 5 pasos</span>
                </h2>
                <p className="mt-4 text-lg leading-8 text-slate-400">
                  Un proceso simple y directo para convertir tu guion en una vision cinematografica clara.
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
                    Un dossier del director <span className="text-gradient-amber">listo para producir o presentar</span>
                  </h2>
                  <p className="mt-4 text-lg leading-8 text-slate-400">
                    Todo el analisis, material visual y documentacion estrategica compilados en un documento
                    ejecutivo que puedes usar para alinear a tu equipo, presentar a productores o preparar el rodaje.
                  </p>
                  <ul className="mt-8 space-y-4">
                    {[
                      'Analisis dramatico completo del guion',
                      'Storyboard de secuencias clave',
                      'Tono visual y paleta cromatica por secuencia',
                      'Referencias cinematograficas seleccionadas',
                      'Dossier ejecutivo listo para compartir',
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
                      <BookOpen className="h-5 w-5" />
                      <span className="solution-eyebrow">Dossier del director</span>
                    </div>
                    <p className="mt-4 font-display text-2xl font-semibold text-white">Nombre del proyecto</p>
                    <p className="mt-1 text-sm text-slate-400">Director / Productora</p>
                    <div className="mt-6 space-y-3">
                      {['Analisis dramatico', 'Tono visual', 'Storyboard', 'Referencias'].map((section) => (
                        <div key={section} className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3">
                          <Film className="h-4 w-4 text-amber-400" />
                          <span className="text-sm text-slate-200">{section}</span>
                        </div>
                      ))}
                    </div>
                    <div className="mt-6 flex flex-wrap gap-2">
                      {['Secuencia 1', 'Secuencia 2', 'Secuencia 3', '+8'].map((tag) => (
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
                  Acceso anticipado a Director AI Studio.
                </p>
                <p className="mt-3 text-base leading-7 text-slate-300">
                  Estamos seleccionando proyectos para la beta privada. Si eres director o realizador,
                  queremos conocerte y conocer tu proximo proyecto.
                </p>
                <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
                  <button
                    onClick={scrollToForm}
                    className="landing-cta-primary"
                  >
                    Probar con mi guion
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
        <section id="director-form" className="relative border-t border-white/5 bg-[#09111c]/40 py-24 md:py-32">
          <div className="mx-auto max-w-3xl px-5 md:px-8">
            <LandingReveal>
              <div className="text-center">
                <p className="editorial-kicker text-amber-300/90">Prueba Director AI Studio</p>
                <h2 className="mt-4 font-display text-4xl font-semibold leading-[1.1] text-white md:text-5xl">
                  Cuentanos sobre <span className="text-gradient-amber">tu proyecto</span>
                </h2>
                <p className="mt-4 text-lg leading-8 text-slate-400">
                  Rellena el formulario y te contactaremos para darte acceso a la beta privada.
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
                    <label className="label" htmlFor="descripcion">Descripcion breve del proyecto</label>
                    <textarea
                      id="descripcion"
                      name="descripcion"
                      rows={3}
                      className="input resize-none"
                      placeholder="Cuentanos de que trata tu proyecto, en que fase esta y que necesitas..."
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
                      Acepto que me contacten para gestionar esta solicitud y recibir informacion sobre Director AI Studio y AILinkCinema.
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
                  Prepara tu mejor pelicula desde el guion
                </h2>
                <p className="mt-6 max-w-2xl mx-auto text-lg leading-8 text-slate-300">
                  Director AI Studio te da las herramientas para visualizar, planificar y comunicar tu vision cinematografica.
                </p>
                <div className="mt-10 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
                  <button
                    onClick={scrollToForm}
                    className="landing-cta-primary text-base"
                  >
                    Probar con mi guion
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
