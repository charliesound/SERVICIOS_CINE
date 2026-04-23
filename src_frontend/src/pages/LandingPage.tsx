import { Link } from 'react-router-dom'
import { useAuthStore, getPrimaryCIDTarget } from '@/store'
import { ArrowRight, FileText, Layers, Eye, Clapperboard, Shield, Users, LogOut, LayoutDashboard } from 'lucide-react'

const workflowSteps = [
  {
    icon: FileText,
    title: 'Guion o idea',
    description: 'Partes de un guion en texto plano, un tratamiento o simplemente una idea estructurada.',
  },
  {
    icon: Layers,
    title: 'Análisis automático',
    description: 'CID lee el texto, detecta escenas, personajes, localizaciones y necesidades de producción.',
  },
  {
    icon: Clapperboard,
    title: 'Desglose y planificación',
    description: 'Obtienes un breakdown cinematográfico con beats narrativos y estructura visual de cada plano.',
  },
  {
    icon: Eye,
    title: 'Storyboard y visualización',
    description: 'Generas un storyboard con grounding visual, continuidad formal y renders listos para presentar.',
  },
]

const audienceItems = [
  {
    title: 'Productoras',
    description: 'Acelera el desglose de guiones, planifica rodajes con datos y presenta proyectos con material visual profesional.',
  },
  {
    title: 'Directores y guionistas',
    description: 'Visualiza tu guion escena a escena antes de rodar. Comprueba ritmo, continuidad y enfoque visual.',
  },
  {
    title: 'Equipos de preproducción',
    description: 'Desglose automático de props, localizaciones y personajes. Menos trabajo manual, más criterio creativo.',
  },
  {
    title: 'Estudios y distribuidoras',
    description: 'Acceso a API, renders dedicados y SLA. Infraestructura que escala con el tamaño de tu catálogo.',
  },
]

export default function LandingPage() {
  const { isAuthenticated, user } = useAuthStore()
  const cidTarget = getPrimaryCIDTarget(user)

  return (
    <div className="min-h-screen bg-dark-300 text-white">
      <nav className="fixed top-0 left-0 right-0 z-50 bg-dark-300/80 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center shadow-lg">
              <Clapperboard className="w-5 h-5 text-black" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight">AILink</h1>
              <p className="text-xs text-amber-400/80 font-medium">CINEMA</p>
            </div>
          </Link>
          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <>
                <Link
                  to={cidTarget}
                  className="px-5 py-2 text-sm font-medium bg-amber-500 hover:bg-amber-400 text-black rounded-xl transition-colors flex items-center gap-2"
                >
                  <LayoutDashboard className="w-4 h-4" />
                  Mi área CID
                </Link>
                <Link
                  to="/dashboard"
                  className="text-sm text-gray-400 hover:text-white transition-colors"
                >
                  Panel
                </Link>
                <button
                  onClick={() => {
                    useAuthStore.getState().logout()
                    window.location.href = '/'
                  }}
                  className="text-sm text-gray-400 hover:text-red-400 transition-colors flex items-center gap-1"
                >
                  <LogOut className="w-4 h-4" />
                  Cerrar sesión
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-sm text-gray-400 hover:text-white transition-colors"
                >
                  Entrar
                </Link>
                <Link
                  to="/register/select"
                  className="px-5 py-2 text-sm font-medium bg-amber-500 hover:bg-amber-400 text-black rounded-xl transition-colors"
                >
                  Solicitar acceso
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      <section className="relative overflow-hidden pt-32 pb-20 md:pt-48 md:pb-32">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-amber-500/10 blur-[100px] rounded-full opacity-50 pointer-events-none" />
        <div className="max-w-7xl mx-auto px-6 relative z-10">
          <div className="grid items-center gap-12 lg:grid-cols-[1.1fr_0.9fr]">
            <div className="text-center lg:text-left">
              <div className="inline-flex items-center gap-2 rounded-full border border-amber-500/20 bg-amber-500/10 px-3 py-1 text-amber-400 mb-8">
                <span className="text-sm font-medium">Plataforma de servicios inteligentes para cine</span>
              </div>
              <h1 className="mb-6 text-4xl md:text-6xl font-bold tracking-tight">
                Del guion al storyboard.
                <br />
                <span className="text-amber-400">Con criterio cinematográfico.</span>
              </h1>
              <p className="mb-10 max-w-2xl text-xl text-gray-400 md:text-2xl lg:mx-0 mx-auto">
                CID analiza guiones, genera desgloses de producción y crea storyboards con IA.
                Todo en una plataforma pensada para cine y audiovisual.
              </p>
              <div className="flex flex-col items-center justify-center gap-4 sm:flex-row lg:justify-start">
                {isAuthenticated ? (
                  <Link
                    to={cidTarget}
                    className="px-8 py-3 text-lg font-medium bg-amber-500 hover:bg-amber-400 text-black rounded-xl shadow-lg shadow-amber-500/20 transition-colors flex items-center gap-2"
                  >
                    Entrar a mi área CID <ArrowRight className="w-5 h-5" />
                  </Link>
                ) : (
                  <>
                    <Link
                      to="/register/select"
                      className="px-8 py-3 text-lg font-medium bg-amber-500 hover:bg-amber-400 text-black rounded-xl shadow-lg shadow-amber-500/20 transition-colors flex items-center gap-2"
                    >
                      Solicitar acceso <ArrowRight className="w-5 h-5" />
                    </Link>
                    <Link
                      to="/login"
                      className="px-8 py-3 text-lg font-medium border border-white/10 hover:border-white/20 text-white rounded-xl transition-colors"
                    >
                      Entrar
                    </Link>
                  </>
                )}
              </div>
            </div>
            <div className="relative flex justify-center">
              <div className="absolute inset-0 rounded-[2rem] bg-[radial-gradient(circle_at_30%_25%,rgba(0,190,255,0.18),transparent_32%),radial-gradient(circle_at_70%_75%,rgba(255,140,0,0.14),transparent_34%)] blur-3xl" />
              <div className="relative rounded-[2rem] border border-white/10 bg-white/5 px-6 py-8 shadow-2xl backdrop-blur-sm">
                <div className="w-48 h-48 mx-auto bg-gradient-to-br from-amber-400/20 to-amber-600/10 rounded-2xl flex items-center justify-center border border-amber-500/20">
                  <Clapperboard className="w-20 h-20 text-amber-400/50" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold mb-4">Qué es CID</h2>
              <p className="text-gray-400 text-lg leading-relaxed mb-4">
                CID es una plataforma de servicios inteligentes para cine y audiovisual.
                No es un generador de imágenes suelto ni una herramienta genérica de IA.
              </p>
              <p className="text-gray-400 text-lg leading-relaxed mb-4">
                Conecta módulos de análisis de guion, desglose cinematográfico,
                planificación visual y storyboard con IA en un flujo de trabajo continuo.
              </p>
              <p className="text-gray-400 text-lg leading-relaxed">
                CID no sustituye el criterio creativo. Lo acelera y lo ordena.
              </p>
            </div>
            <div className="flex justify-center">
              <div className="w-full max-w-sm aspect-[4/5] bg-gradient-to-br from-amber-500/10 to-transparent rounded-2xl border border-white/10 flex items-center justify-center">
                <span className="text-gray-500 text-sm">Vista previa de plataforma</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Cómo funciona</h2>
            <p className="text-gray-400 text-lg max-w-xl mx-auto">
              Un flujo continuo desde el texto hasta la imagen. Cada módulo se conecta con el siguiente.
            </p>
          </div>
          <div className="grid md:grid-cols-4 gap-6">
            {workflowSteps.map((step, i) => {
              const Icon = step.icon
              return (
                <div key={step.title} className="relative">
                  {i < workflowSteps.length - 1 && (
                    <div className="hidden md:block absolute top-8 -right-3 w-6 h-px bg-white/10" />
                  )}
                  <div className="p-6 bg-white/5 rounded-xl border border-white/10 h-full">
                    <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center mb-4 text-amber-400">
                      <Icon className="w-5 h-5" />
                    </div>
                    <h3 className="text-lg font-semibold mb-2">{step.title}</h3>
                    <p className="text-gray-400 text-sm leading-relaxed">{step.description}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      <section className="py-20 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Módulos conectados</h2>
            <p className="text-gray-400 text-lg max-w-xl mx-auto">
              Servicios que trabajan juntos. No herramientas sueltas.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              'Análisis de guion',
              'Desglose cinematográfico',
              'Planificación visual',
              'Storyboard con IA',
              'Subvenciones inteligentes',
              'Agentes de producción',
            ].map((service) => (
              <div key={service} className="p-6 bg-white/5 rounded-xl border border-white/10 hover:border-amber-500/30 transition-colors">
                <h3 className="text-lg font-semibold mb-2">{service}</h3>
                <p className="text-gray-400 text-sm">Módulo conectado en el flujo CID.</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Para quién es CID</h2>
            <p className="text-gray-400 text-lg max-w-xl mx-auto">
              Diseñado para profesionales del cine y el audiovisual.
            </p>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            {audienceItems.map((item) => (
              <div key={item.title} className="p-6 bg-white/5 rounded-xl border border-white/10">
                <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-12 bg-white/5 p-12 rounded-3xl border border-white/10">
            <div className="flex-1">
              <h2 className="text-3xl font-bold mb-4">Cine, no contenido genérico</h2>
              <p className="text-gray-400 text-lg mb-6">
                CID no es un generador de imágenes al uso. Entiende escenas, planos,
                continuidad de eje, grounding visual y la estructura narrativa de un guion.
              </p>
              <ul className="space-y-3">
                <li className="flex items-center gap-2"><Shield className="w-5 h-5 text-amber-400" /> Tus guiones nunca entrenan modelos públicos</li>
                <li className="flex items-center gap-2"><Users className="w-5 h-5 text-amber-400" /> Infraestructura europea con cumplimiento GDPR</li>
                <li className="flex items-center gap-2"><Eye className="w-5 h-5 text-amber-400" /> Continuidad formal y criterio visual por plano</li>
              </ul>
            </div>
            <div className="flex-1 flex justify-center">
              <div className="w-full max-w-md aspect-[4/3] bg-gradient-to-br from-amber-500/10 to-transparent rounded-2xl border border-white/10 flex items-center justify-center">
                <span className="text-gray-500 text-sm">Storyboard de ejemplo</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-32 text-center">
        <div className="max-w-7xl mx-auto px-6">
          <h2 className="text-4xl font-bold mb-4">Empieza a visualizar tu proyecto</h2>
          <p className="text-gray-400 text-lg max-w-lg mx-auto mb-8">
            {isAuthenticated
              ? 'Continúa en tu área CID para acceder a todos los módulos.'
              : 'Solicita acceso al programa CID o contacta con el equipo.'}
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            {isAuthenticated ? (
              <Link
                to={cidTarget}
                className="px-12 py-4 text-lg font-medium bg-amber-500 hover:bg-amber-400 text-black rounded-xl transition-colors flex items-center gap-2"
              >
                Ir a mi área CID <ArrowRight className="w-5 h-5" />
              </Link>
            ) : (
              <>
                <Link
                  to="/register/select"
                  className="px-12 py-4 text-lg font-medium bg-amber-500 hover:bg-amber-400 text-black rounded-xl transition-colors"
                >
                  Solicitar acceso
                </Link>
                <Link
                  to="/login"
                  className="px-12 py-4 text-lg font-medium border border-white/10 hover:border-white/20 text-white rounded-xl transition-colors"
                >
                  Entrar
                </Link>
              </>
            )}
          </div>
        </div>
      </section>
    </div>
  )
}
