import { useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowRight,
  ChevronRight,
  Sparkles,
  Clapperboard,
  PenSquare,
  Scissors,
  Globe,
  FileText,
  Search,
  TrendingUp,
  Camera,
  Image,
  Palette,
  Users,
  BookOpen,
  MessageCircle,
  Upload,
  Send,
  CheckCircle,
  AlertCircle,
  Loader,
  Shield,
  Briefcase,
  Star,
  LayoutDashboard,
  LogOut,
  Mail,
  User,
  Building2,
  ChevronDown,
} from 'lucide-react'
import LandingAmbientScene from '@/components/landing/LandingAmbientScene'
import LandingReveal from '@/components/landing/LandingReveal'
import { useSeo } from '@/hooks/useSeo'
import { useAuthStore } from '@/store'
import { buildAbsoluteUrl } from '@/utils/seo'

function trackEvent(eventName: string, payload?: Record<string, unknown>) {
  if (typeof window !== 'undefined' && import.meta.env.DEV) {
    console.info(`[Track] ${eventName}`, payload ?? {})
  }
}

const audienceItems = [
  {
    icon: Briefcase,
    title: 'Productores',
    text: 'Valida el potencial de produccion de un proyecto antes de comprometer presupuesto, equipo o rodaje.',
    accent: 'amber',
  },
  {
    icon: Clapperboard,
    title: 'Directores',
    text: 'Obtén una lectura visual y estrategica de tu guion para alinear a tu equipo creativo y tecnico.',
    accent: 'violet',
  },
  {
    icon: PenSquare,
    title: 'Guionistas',
    text: 'Descubre cómo se traduce tu escritura a terminos de produccion, riesgo narrativo y oportunidades de desarrollo.',
    accent: 'cyan',
  },
  {
    icon: Scissors,
    title: 'Montadores',
    text: 'Recibe un mapa de escenas clave, ritmo narrativo y material preparado para empezar la edición con criterio.',
    accent: 'emerald',
  },
  {
    icon: Globe,
    title: 'Distribuidores',
    text: 'Evalúa la viabilidad comercial de un proyecto a partir del analisis de guion y el material de presentacion.',
    accent: 'rose',
  },
]

const accentClasses: Record<string, string> = {
  amber: 'border-l-amber-500/50',
  violet: 'border-l-violet-500/50',
  cyan: 'border-l-cyan-500/50',
  emerald: 'border-l-emerald-500/50',
  rose: 'border-l-rose-500/50',
}

const accentDots: Record<string, string> = {
  amber: 'bg-amber-500',
  violet: 'bg-violet-500',
  cyan: 'bg-cyan-500',
  emerald: 'bg-emerald-500',
  rose: 'bg-rose-500',
}

const deliverables = [
  { icon: FileText, title: 'Analisis narrativo del guion', text: 'Lectura estructurada por actos, personajes, tramas y ritmo dramatico.' },
  { icon: Search, title: 'Detección de fortalezas y riesgos', text: 'Puntos fuertes, carencias narrativas y riesgos de produccion detectados.' },
  { icon: TrendingUp, title: 'Desglose inicial de producción', text: 'Estimacion de recursos, localizaciones, personajes y necesidades tecnicas.' },
  { icon: Camera, title: 'Selección de secuencias clave', text: 'Identificacion de las escenas con mayor peso narrativo y visual.' },
  { icon: Image, title: 'Storyboard o concept frames', text: 'Frames conceptuales de las secuencias clave para comunicar la vision.' },
  { icon: Palette, title: 'Propuesta de tono visual', text: 'Paleta cromática, referencias de iluminacion y atmosfera por secuencia.' },
  { icon: Users, title: 'Público objetivo', text: 'Perfil de audiencia potencial, demografia y canales de distribución optimos.' },
  { icon: BookOpen, title: 'Mini dossier de pitching', text: 'Documento ejecutivo con los hallazgos clave para presentar el proyecto.' },
  { icon: MessageCircle, title: 'Reunión de devolución', text: 'Sesión online para recorrer el analisis y resolver dudas con el equipo.' },
]

const steps = [
  { number: '01', title: 'Envias tu guion o tratamiento', text: 'Sube tu material en formato digital. Aceptamos guiones, tratamientos, escaletas o documentacion de proyecto.' },
  { number: '02', title: 'CID analiza la estructura narrativa y productiva', text: 'Nuestro sistema procesa el material y extrae personajes, escenas, localizaciones, dialogos y necesidades de produccion.' },
  { number: '03', title: 'Seleccionamos las secuencias clave', text: 'Identificamos los momentos narrativos y visuales mas relevantes para el analisis y la presentacion.' },
  { number: '04', title: 'Generamos concept frames o storyboard', text: 'Creamos representaciones visuales de las secuencias clave para comunicar la propuesta estetica.' },
  { number: '05', title: 'Preparamos un mini dossier', text: 'Compilamos los hallazgos en un documento ejecutivo listo para pitching, financiacion o produccion.' },
  { number: '06', title: 'Te damos una devolución profesional', text: 'Reunion online para presentar los resultados, resolver dudas y planificar los siguientes pasos.' },
]

const plans = [
  {
    name: 'Diagnóstico inicial',
    price: 'Gratuito',
    period: 'para proyectos seleccionados',
    description: 'Validacion ligera del potencial de tu proyecto.',
    features: [
      'Analisis narrativo basico',
      'Detección de fortalezas y riesgos',
      'Perfil de público objetivo',
      'Resumen ejecutivo',
    ],
    cta: 'Solicitar selección',
    featured: false,
  },
  {
    name: 'Sprint básico',
    price: '299 €',
    period: 'por proyecto',
    description: 'Analisis completo con material visual para pitching.',
    features: [
      'Todo lo del diagnóstico',
      'Desglose inicial de producción',
      'Selección de secuencias clave',
      'Storyboard o concept frames',
      'Mini dossier de pitching',
    ],
    cta: 'Contratar sprint',
    featured: true,
  },
  {
    name: 'Sprint profesional',
    price: 'Bajo presupuesto',
    period: 'consultar',
    description: 'Analisis profundo con reunion de devolución incluida.',
    features: [
      'Todo lo del sprint básico',
      'Propuesta de tono visual completa',
      'Analisis de público objetivo detallado',
      'Dossier de pitching profesional',
      'Reunión de devolución online',
    ],
    cta: 'Consultar precio',
    featured: false,
  },
]

const faqs = [
  {
    q: '¿Tengo que tener un guion terminado?',
    a: 'No. Aceptamos tratamientos, escaletas, documentacion de proyecto o incluso ideas desarrolladas. Cuanto mas material tengas, mas completo será el analisis.',
  },
  {
    q: '¿Se usa IA sin supervisión?',
    a: 'No. La IA acelera el procesamiento, pero todo el analisis es revisado y validado por nuestro equipo profesional antes de entregartelo.',
  },
  {
    q: '¿El material sigue siendo mío?',
    a: 'Sí. Todo el material que nos envias sigue siendo 100% tuyo. No lo utilizamos para entrenar modelos ni lo compartimos con terceros sin tu autorización explicita.',
  },
  {
    q: '¿Sirve para pitching?',
    a: 'Sí. El mini dossier de pitching esta diseñado especificamente para presentar tu proyecto a productoras, fondos de financiacion o plataformas.',
  },
  {
    q: '¿Puedo usarlo con una productora?',
    a: 'Sí. De hecho esta pensado para que productoras y directores validen proyectos antes de invertir tiempo y recursos en desarrollo.',
  },
  {
    q: '¿Se puede generar storyboard de toda la película?',
    a: 'El piloto se centra en secuencias clave. Si necesitas un storyboard completo, podemos diseñar un plan a medida con nuestro equipo.',
  },
]

const initialFormState = {
  nombre: '',
  email: '',
  empresa: '',
  rol: '',
  tipoProyecto: '',
  faseProyecto: '',
  objetivoPrincipal: '',
  enlaceGuion: '',
  mensaje: '',
  aceptaContacto: false,
}

type FormData = typeof initialFormState

const DEMO_CID_WEBHOOK = import.meta.env.VITE_DEMO_CID_WEBHOOK_URL

export default function DemoCIDPage() {
  const { isAuthenticated } = useAuthStore()
  const [form, setForm] = useState<FormData>(initialFormState)
  const [formSubmitted, setFormSubmitted] = useState(false)
  const [formSubmitting, setFormSubmitting] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)
  const [openFaq, setOpenFaq] = useState<number | null>(null)

  useSeo({
    title: 'Prueba CID con tu guion | AILinkCinema',
    description:
      'Convierte un guion o tratamiento en un análisis visual y estratégico para desarrollo, pitching, financiación o producción.',
    path: '/demo-cid',
    keywords: [
      'analisis de guion',
      'prueba cid',
      'storyboard',
      'pitching cinematografico',
      'desglose de produccion',
    ],
    structuredData: [
      {
        '@context': 'https://schema.org',
        '@type': 'WebPage',
        name: 'Prueba CID con tu guion',
        description:
          'Convierte un guion o tratamiento en un análisis visual y estratégico para desarrollo, pitching, financiación o producción.',
        url: buildAbsoluteUrl('/demo-cid'),
        inLanguage: 'es',
      },
    ],
  })

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      const { name, value, type } = e.target
      setForm((prev) => ({
        ...prev,
        [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
      }))
    },
    []
  )

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault()
      setFormError(null)
      setFormSubmitting(true)
      trackEvent('submit_demo_cid_form', { ...form })

      if (!DEMO_CID_WEBHOOK) {
        setFormError('El servicio de envio no esta configurado. Contacta con el equipo de AILinkCinema.')
        setFormSubmitting(false)
        return
      }

      try {
        const payload = { ...form, _timestamp: new Date().toISOString(), _source: 'demo-cid-page' }
        const res = await fetch(DEMO_CID_WEBHOOK, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        setFormSubmitted(true)
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Error de conexion'
        setFormError(`No se pudo enviar la solicitud (${msg}). Intentalo de nuevo o escribenos a contacto@ailinkcinema.com.`)
        trackEvent('submit_demo_cid_form_error', { error: msg })
      } finally {
        setFormSubmitting(false)
      }
    },
    [form]
  )

  const scrollToForm = useCallback(() => {
    trackEvent('click_demo_cid_secondary')
    const el = document.getElementById('demo-form')
    el?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [])

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
                CID &mdash; Cine Inteligente Digital
              </p>
            </div>
          </Link>

          <nav className="hidden items-center gap-7 text-sm text-slate-300 xl:flex">
            <a href="#para-quien" className="transition-colors hover:text-white">Para quién es</a>
            <a href="#que-incluye" className="transition-colors hover:text-white">Qué incluye</a>
            <a href="#como-funciona" className="transition-colors hover:text-white">Cómo funciona</a>
            <a href="#planes" className="transition-colors hover:text-white">Planes</a>
            <a href="#faq" className="transition-colors hover:text-white">FAQ</a>
          </nav>

          <div className="flex items-center gap-2 md:gap-3">
            {isAuthenticated ? (
              <>
                <Link to="/cid" className="landing-cta-secondary hidden sm:inline-flex">
                  <LayoutDashboard className="h-4 w-4" />
                  Ir a CID
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
              <>
                <Link to="/login" className="hidden rounded-full border border-white/10 px-4 py-2 text-sm text-slate-200 transition-colors hover:border-white/20 hover:bg-white/5 sm:inline-flex">
                  Iniciar sesion
                </Link>
                <Link
                  to="/register/demo"
                  className="landing-cta-primary hidden sm:inline-flex"
                  onClick={() => trackEvent('click_demo_cid_hero')}
                >
                  Solicitar demo
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </>
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
                <Sparkles className="h-3.5 w-3.5" />
                CID &mdash; Prueba piloto
              </div>

              <h1 className="mt-8 font-display text-5xl font-semibold leading-[0.92] tracking-[-0.04em] text-white sm:text-6xl md:text-7xl lg:text-8xl">
                Prueba CID con <span className="text-gradient-amber">tu guion</span>
              </h1>

              <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300 md:text-xl md:leading-9">
                Convierte un guion o tratamiento en un análisis visual y estratégico para desarrollo, pitching, financiación o producción.
              </p>

              <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
                <Link
                  to="/register/demo"
                  className="landing-cta-primary"
                  onClick={() => trackEvent('click_demo_cid_hero', { cta: 'Solicitar prueba piloto' })}
                >
                  Solicitar prueba piloto
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <button
                  onClick={scrollToForm}
                  className="landing-cta-secondary"
                >
                  Ver qué incluye
                  <ChevronDown className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* PARA QUIÉN ES */}
        <section id="para-quien" className="relative border-t border-white/5 py-24 md:py-32">
          <div className="mx-auto max-w-7xl px-5 md:px-8">
            <LandingReveal>
              <div className="mx-auto max-w-3xl text-center">
                <p className="editorial-kicker text-amber-300/90">Para quién es</p>
                <h2 className="mt-4 font-display text-4xl font-semibold leading-[1.1] text-white md:text-5xl">
                  Diseñado para <span className="text-gradient-amber">equipos audiovisuales</span>
                </h2>
                <p className="mt-4 text-lg leading-8 text-slate-400">
                  Si trabajas con guiones, proyectos o financiacion audiovisual, CID te da una ventaja real.
                </p>
              </div>
            </LandingReveal>

            <div className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
              {audienceItems.map((item) => (
                <LandingReveal key={item.title}>
                  <div className={`landing-audience-card ${accentClasses[item.accent]}`}>
                    <item.icon className={`mb-3 h-5 w-5 ${accentDots[item.accent].replace('bg-', 'text-')}`} />
                    <h3 className="text-base font-semibold text-white">{item.title}</h3>
                    <p className="mt-2 text-sm leading-7 text-slate-400">{item.text}</p>
                  </div>
                </LandingReveal>
              ))}
            </div>
          </div>
        </section>

        {/* QUÉ RECIBE EL USUARIO */}
        <section id="que-incluye" className="relative border-t border-white/5 bg-[#09111c]/40 py-24 md:py-32">
          <div className="mx-auto max-w-7xl px-5 md:px-8">
            <LandingReveal>
              <div className="mx-auto max-w-3xl text-center">
                <p className="editorial-kicker text-amber-300/90">Qué recibe el usuario</p>
                <h2 className="mt-4 font-display text-4xl font-semibold leading-[1.1] text-white md:text-5xl">
                  Todo lo que necesitas para <span className="text-gradient-amber">avanzar</span>
                </h2>
                <p className="mt-4 text-lg leading-8 text-slate-400">
                  Un paquete completo de análisis y materiales listos para presentar, producir o financiar.
                </p>
              </div>
            </LandingReveal>

            <div className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {deliverables.map((item) => (
                <LandingReveal key={item.title}>
                  <div className="landing-creative-card h-full">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10">
                        <item.icon className="h-5 w-5 text-amber-400" />
                      </div>
                      <h3 className="text-sm font-semibold text-white">{item.title}</h3>
                    </div>
                    <p className="mt-3 text-sm leading-7 text-slate-400">{item.text}</p>
                  </div>
                </LandingReveal>
              ))}
            </div>
          </div>
        </section>

        {/* CÓMO FUNCIONA */}
        <section id="como-funciona" className="relative border-t border-white/5 py-24 md:py-32">
          <div className="mx-auto max-w-7xl px-5 md:px-8">
            <LandingReveal>
              <div className="mx-auto max-w-3xl text-center">
                <p className="editorial-kicker text-amber-300/90">Cómo funciona</p>
                <h2 className="mt-4 font-display text-4xl font-semibold leading-[1.1] text-white md:text-5xl">
                  De tu guion al <span className="text-gradient-amber">análisis</span> en 6 pasos
                </h2>
                <p className="mt-4 text-lg leading-8 text-slate-400">
                  Un proceso claro, rapido y sin complicaciones.
                </p>
              </div>
            </LandingReveal>

            <div className="mt-14 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
              {steps.map((step) => (
                <LandingReveal key={step.number}>
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
        </section>

        {/* VALIDACIÓN COMERCIAL */}
        <section className="relative border-y border-white/10 py-20">
          <div className="landing-section-glow-left" />
          <div className="landing-section-glow-right" />
          <div className="mx-auto max-w-4xl px-5 text-center md:px-8">
            <LandingReveal>
              <div className="landing-brand-final-cta rounded-[2.4rem] p-8 sm:p-10 lg:p-12">
                <Sparkles className="mx-auto h-8 w-8 text-amber-400" />
                <p className="mt-4 font-display text-2xl font-semibold leading-snug text-white md:text-3xl">
                  Estamos seleccionando proyectos reales para probar CID en fase piloto con productoras, directores y equipos audiovisuales.
                </p>
                <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
                  <Link
                    to="/register/demo"
                    className="landing-cta-primary"
                    onClick={() => trackEvent('click_demo_cid_hero', { cta: 'Solicitar prueba piloto' })}
                  >
                    Solicitar prueba piloto
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                  <button
                    onClick={scrollToForm}
                    className="landing-cta-secondary"
                  >
                    Ver qué incluye
                    <ChevronDown className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </LandingReveal>
          </div>
        </section>

        {/* PLANES */}
        <section id="planes" className="relative border-t border-white/5 py-24 md:py-32">
          <div className="mx-auto max-w-7xl px-5 md:px-8">
            <LandingReveal>
              <div className="mx-auto max-w-3xl text-center">
                <p className="editorial-kicker text-amber-300/90">Planes piloto</p>
                <h2 className="mt-4 font-display text-4xl font-semibold leading-[1.1] text-white md:text-5xl">
                  Elige el plan que mejor se <span className="text-gradient-amber">adapte</span>
                </h2>
                <p className="mt-4 text-lg leading-8 text-slate-400">
                  Desde una validación gratuita hasta un análisis profesional completo.
                </p>
              </div>
            </LandingReveal>

            <div className="mt-14 grid gap-6 md:grid-cols-3">
              {plans.map((plan) => (
                <LandingReveal key={plan.name}>
                  <div
                    className={`relative flex h-full flex-col rounded-[2rem] border p-6 sm:p-8 ${
                      plan.featured
                        ? 'border-amber-500/20 bg-gradient-to-b from-amber-500/5 to-transparent shadow-[0_24px_80px_rgba(245,158,11,0.08)]'
                        : 'border-white/10 bg-white/[0.03]'
                    }`}
                  >
                    {plan.featured && (
                      <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                        <span className="inline-flex items-center gap-1 rounded-full bg-amber-500 px-3 py-1 text-[10px] font-semibold uppercase tracking-wider text-black">
                          <Star className="h-3 w-3" />
                          Recomendado
                        </span>
                      </div>
                    )}

                    <div>
                      <h3 className="text-lg font-semibold text-white">{plan.name}</h3>
                      <div className="mt-3">
                        <span className="font-display text-4xl text-white">{plan.price}</span>
                        <span className="ml-2 text-sm text-slate-400">{plan.period}</span>
                      </div>
                      <p className="mt-3 text-sm leading-7 text-slate-400">{plan.description}</p>
                    </div>

                    <ul className="mt-6 flex-1 space-y-3">
                      {plan.features.map((feature) => (
                        <li key={feature} className="flex items-start gap-2 text-sm text-slate-300">
                          <CheckCircle className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
                          {feature}
                        </li>
                      ))}
                    </ul>

                    <div className="mt-8">
                      <Link
                        to="/register/demo"
                        className={
                          plan.featured ? 'landing-cta-primary w-full justify-center' : 'landing-cta-secondary w-full justify-center'
                        }
                        onClick={() => trackEvent('click_demo_cid_pricing', { plan: plan.name })}
                      >
                        {plan.cta}
                        <ArrowRight className="h-4 w-4" />
                      </Link>
                    </div>
                  </div>
                </LandingReveal>
              ))}
            </div>
          </div>
        </section>

        {/* FORMULARIO */}
        <section id="demo-form" className="relative border-t border-white/5 bg-[#09111c]/40 py-24 md:py-32">
          <div className="mx-auto max-w-3xl px-5 md:px-8">
            <LandingReveal>
              <div className="text-center">
                <p className="editorial-kicker text-amber-300/90">Solicita tu prueba</p>
                <h2 className="mt-4 font-display text-4xl font-semibold leading-[1.1] text-white md:text-5xl">
                  Cuéntanos sobre <span className="text-gradient-amber">tu proyecto</span>
                </h2>
                <p className="mt-4 text-lg leading-8 text-slate-400">
                  Rellena el formulario y nuestro equipo te contactará para iniciar la prueba piloto.
                </p>
              </div>
            </LandingReveal>

            <LandingReveal>
              <div className="mt-12">
                {formSubmitted ? (
                  <div className="landing-brand-final-cta rounded-[2rem] p-10 text-center">
                    <CheckCircle className="mx-auto h-12 w-12 text-emerald-400" />
                    <h3 className="mt-4 font-display text-2xl text-white">Solicitud enviada</h3>
                    <p className="mt-3 text-base leading-7 text-slate-300">
                      Gracias por tu interes. Nuestro equipo revisará tu solicitud y te contactaremos pronto.
                    </p>
                  </div>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="grid gap-5 sm:grid-cols-2">
                      <div>
                        <label className="label" htmlFor="nombre">Nombre completo</label>
                        <div className="relative">
                          <User className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                          <input
                            id="nombre"
                            name="nombre"
                            type="text"
                            required
                            value={form.nombre}
                            onChange={handleChange}
                            className="input pl-10"
                            placeholder="Tu nombre"
                          />
                        </div>
                      </div>
                      <div>
                        <label className="label" htmlFor="email">Email</label>
                        <div className="relative">
                          <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                          <input
                            id="email"
                            name="email"
                            type="email"
                            required
                            value={form.email}
                            onChange={handleChange}
                            className="input pl-10"
                            placeholder="tu@email.com"
                          />
                        </div>
                      </div>
                    </div>

                    <div className="grid gap-5 sm:grid-cols-2">
                      <div>
                        <label className="label" htmlFor="empresa">Empresa o productora</label>
                        <div className="relative">
                          <Building2 className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                          <input
                            id="empresa"
                            name="empresa"
                            type="text"
                            value={form.empresa}
                            onChange={handleChange}
                            className="input pl-10"
                            placeholder="Nombre de tu empresa"
                          />
                        </div>
                      </div>
                      <div>
                        <label className="label" htmlFor="rol">Rol</label>
                        <div className="relative">
                          <Users className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                          <select
                            id="rol"
                            name="rol"
                            required
                            value={form.rol}
                            onChange={handleChange}
                            className="input pl-10 appearance-none"
                          >
                            <option value="" disabled>Selecciona tu rol</option>
                            <option value="productor">Productor</option>
                            <option value="director">Director</option>
                            <option value="guionista">Guionista</option>
                            <option value="montador">Montador</option>
                            <option value="distribuidor">Distribuidor</option>
                            <option value="otro">Otro</option>
                          </select>
                        </div>
                      </div>
                    </div>

                    <div className="grid gap-5 sm:grid-cols-2">
                      <div>
                        <label className="label" htmlFor="tipoProyecto">Tipo de proyecto</label>
                        <select
                          id="tipoProyecto"
                          name="tipoProyecto"
                          required
                          value={form.tipoProyecto}
                          onChange={handleChange}
                          className="input"
                        >
                          <option value="" disabled>Selecciona tipo</option>
                          <option value="largometraje">Largometraje</option>
                          <option value="cortometraje">Cortometraje</option>
                          <option value="serie">Serie</option>
                          <option value="documental">Documental</option>
                          <option value="animacion">Animación</option>
                          <option value="otro">Otro</option>
                        </select>
                      </div>
                      <div>
                        <label className="label" htmlFor="faseProyecto">Fase del proyecto</label>
                        <select
                          id="faseProyecto"
                          name="faseProyecto"
                          required
                          value={form.faseProyecto}
                          onChange={handleChange}
                          className="input"
                        >
                          <option value="" disabled>Selecciona fase</option>
                          <option value="idea">Idea / Concepto</option>
                          <option value="tratamiento">Tratamiento</option>
                          <option value="guion">Guion en desarrollo</option>
                          <option value="guion_terminado">Guion terminado</option>
                          <option value="preproduccion">Preproducción</option>
                          <option value="produccion">Producción</option>
                        </select>
                      </div>
                    </div>

                    <div>
                      <label className="label" htmlFor="objetivoPrincipal">Objetivo principal</label>
                      <select
                        id="objetivoPrincipal"
                        name="objetivoPrincipal"
                        required
                        value={form.objetivoPrincipal}
                        onChange={handleChange}
                        className="input"
                      >
                        <option value="" disabled>Selecciona tu objetivo</option>
                        <option value="pitching">Pitching / financiación</option>
                        <option value="produccion">Preparación de producción</option>
                        <option value="analisis">Análisis narrativo</option>
                        <option value="distribucion">Distribución</option>
                        <option value="presentacion">Material de presentación</option>
                        <option value="otro">Otro</option>
                      </select>
                    </div>

                    <div>
                      <label className="label" htmlFor="enlaceGuion">Enlace al guion o material</label>
                      <div className="relative">
                        <Upload className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-slate-500" />
                        <input
                          id="enlaceGuion"
                          name="enlaceGuion"
                          type="url"
                          value={form.enlaceGuion}
                          onChange={handleChange}
                          className="input pl-10"
                          placeholder="Drive, Dropbox, o enlace directo"
                        />
                      </div>
                      <p className="mt-1 text-xs text-slate-500">Comparte un enlace a tu guion, tratamiento o documentación.</p>
                    </div>

                    <div>
                      <label className="label" htmlFor="mensaje">Mensaje adicional</label>
                      <textarea
                        id="mensaje"
                        name="mensaje"
                        rows={3}
                        value={form.mensaje}
                        onChange={handleChange}
                        className="input resize-none"
                        placeholder="Cuéntanos más sobre tu proyecto..."
                      />
                    </div>

                    <label className="flex items-start gap-3 cursor-pointer">
                      <input
                        type="checkbox"
                        name="aceptaContacto"
                        checked={form.aceptaContacto}
                        onChange={handleChange}
                        required
                        className="mt-1 h-4 w-4 rounded border-white/20 bg-white/5 text-amber-500 focus:ring-amber-500/30"
                      />
                      <span className="text-sm text-slate-400">
                        Acepto que me contacten para gestionar esta solicitud y recibir información sobre CID y AILinkCinema.
                      </span>
                    </label>

                    {formError && (
                      <div className="flex items-start gap-3 rounded-xl border border-red-500/20 bg-red-500/10 p-4">
                        <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-400" />
                        <p className="text-sm leading-6 text-red-200">{formError}</p>
                      </div>
                    )}

                    <button
                      type="submit"
                      disabled={formSubmitting}
                      className="landing-cta-primary w-full justify-center py-4 text-base disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {formSubmitting ? (
                        <Loader className="h-4 w-4 animate-spin" />
                      ) : (
                        <Send className="h-4 w-4" />
                      )}
                      {formSubmitting ? 'Enviando...' : 'Enviar solicitud'}
                    </button>
                  </form>
                )}
              </div>
            </LandingReveal>
          </div>
        </section>

        {/* FAQ */}
        <section id="faq" className="relative border-t border-white/5 py-24 md:py-32">
          <div className="mx-auto max-w-3xl px-5 md:px-8">
            <LandingReveal>
              <div className="text-center">
                <p className="editorial-kicker text-amber-300/90">FAQ</p>
                <h2 className="mt-4 font-display text-4xl font-semibold leading-[1.1] text-white md:text-5xl">
                  Preguntas <span className="text-gradient-amber">frecuentes</span>
                </h2>
              </div>
            </LandingReveal>

            <div className="mt-12 space-y-3">
              {faqs.map((faq, i) => (
                <LandingReveal key={i}>
                  <div className="rounded-2xl border border-white/10 bg-white/[0.03] overflow-hidden">
                    <button
                      onClick={() => {
                        setOpenFaq(openFaq === i ? null : i)
                      }}
                      className="flex w-full items-center justify-between gap-4 px-6 py-5 text-left transition-colors hover:bg-white/[0.02]"
                    >
                      <span className="text-sm font-semibold text-white">{faq.q}</span>
                      <ChevronDown
                        className={`h-4 w-4 shrink-0 text-slate-400 transition-transform duration-300 ${
                          openFaq === i ? 'rotate-180' : ''
                        }`}
                      />
                    </button>
                    <div
                      className={`overflow-hidden transition-all duration-300 ${
                        openFaq === i ? 'max-h-80 opacity-100' : 'max-h-0 opacity-0'
                      }`}
                    >
                      <p className="px-6 pb-5 text-sm leading-7 text-slate-400">{faq.a}</p>
                    </div>
                  </div>
                </LandingReveal>
              ))}
            </div>
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
                  Valida tu proyecto antes de invertir más tiempo y dinero
                </h2>
                <p className="mt-6 max-w-2xl mx-auto text-lg leading-8 text-slate-300">
                  Descubre el potencial real de tu guion con un análisis profesional. Sin compromiso.
                </p>
                <div className="mt-10 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
                  <Link
                    to="/register/demo"
                    className="landing-cta-primary text-base"
                    onClick={() => trackEvent('click_demo_cid_hero', { cta: 'Solicitar prueba piloto' })}
                  >
                    Solicitar prueba piloto
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                  <Link
                    to="/solutions/cid"
                    className="landing-cta-secondary"
                    onClick={() => trackEvent('click_demo_cid_secondary', { cta: 'Explorar CID' })}
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

      {/* FOOTER */}
      <footer className="border-t border-white/5 py-10">
        <div className="mx-auto grid max-w-7xl gap-8 px-5 md:px-6 lg:grid-cols-[1fr_auto] lg:items-center lg:px-8">
          <div>
            <p className="font-display text-3xl text-white">AILinkCinema</p>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-400">
              Inteligencia artificial para cine, television y publicidad con software especializado, CID como sistema central y acompañamiento tecnico real.
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
                Términos
              </Link>
              <Link to="/legal/ia-y-contenidos" className="text-xs text-slate-500 transition-colors hover:text-slate-200">
                IA y contenidos
              </Link>
            </div>
          </div>
        </div>

        <div className="mx-auto mt-8 flex max-w-7xl items-center gap-3 px-5 text-sm text-slate-500 md:px-6 lg:px-8">
          <Shield className="h-4 w-4 text-amber-300" />
          <p>AILinkCinema posiciona a CID como sistema completo de producción audiovisual y articula soluciones especializadas para cada departamento.</p>
        </div>
      </footer>
    </div>
  )
}
