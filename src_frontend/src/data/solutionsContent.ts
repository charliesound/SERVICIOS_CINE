import {
  AudioWaveform,
  Clapperboard,
  FileSearch,
  Film,
  LayoutTemplate,
  Mic2,
  MonitorPlay,
  PenSquare,
  Sparkles,
  type LucideIcon,
} from 'lucide-react'

export type SolutionSlug =
  | 'cid'
  | 'script-breakdown'
  | 'storyboard'
  | 'production-planner'
  | 'dubbing'
  | 'sound-post'
  | 'promo-video'
  | 'vfx'

export interface SolutionEntry {
  slug: SolutionSlug
  path: string
  title: string
  shortTitle: string
  type: 'Producto completo' | 'Modulo independiente'
  icon: LucideIcon
  priceLabel: string
  description: string
  heroDescription: string
  bullets: readonly string[]
  includedInCid: boolean
  ctaLabel: string
}

export const cidProduct = {
  slug: 'cid' as const,
  path: '/solutions/cid',
  title: 'CID - Cine Inteligente Digital',
  shortTitle: 'CID',
  type: 'Producto completo' as const,
  icon: Film,
  priceLabel: 'Setup inicial desde 1.500 EUR + desde 299 EUR/mes',
  description:
    'Solucion integral para desarrollar una produccion audiovisual con todos los departamentos conectados en un mismo flujo de trabajo.',
  heroDescription:
    'CID es el producto principal de AILinkCinema: una plataforma premium que organiza guion, analisis, storyboard, presupuesto, produccion, postproduccion, distribucion y entrega en una sola experiencia.',
  pricing: {
    headline: 'Modelo de precio',
    setup: 'Setup inicial desde 1.500 EUR',
    monthly: 'Cuota mensual desde 299 EUR/mes',
    requirements: 'Requiere demo y diagnostico previo para adaptar el flujo a la produccion real.',
    bullets: [
      'Incluye todos los modulos de AILinkCinema dentro de la configuracion base.',
      'Se adapta al pipeline, roles, aprobaciones y necesidades de cada proyecto o estudio.',
      'Puede convivir con integraciones, herramientas externas y desarrollo a medida bajo presupuesto.',
    ],
  },
  includedModules: [
    'Script & Breakdown AI',
    'Storyboard AI Studio',
    'Production Planner AI',
    'DubbingTake Studio AI',
    'Sound Post AI',
    'Promo Video AI',
    'VFX & Enhancement AI',
  ],
  pipeline: [
    'Guion y desarrollo',
    'Analisis y desglose',
    'Storyboard y previz',
    'Planificacion y produccion',
    'Doblaje, sonido y post',
    'Distribucion y entrega',
  ],
}

export const standaloneSolutions: SolutionEntry[] = [
  {
    slug: 'script-breakdown',
    path: '/solutions/script-breakdown',
    title: 'Script & Breakdown AI',
    shortTitle: 'Script & Breakdown AI',
    type: 'Modulo independiente',
    icon: PenSquare,
    priceLabel: 'Desde 49 EUR/mes',
    description:
      'Ayuda a redaccion, analisis y desglose de guion por secuencias, personajes, localizaciones, elementos de produccion y necesidades tecnicas.',
    heroDescription:
      'Una capa de trabajo para convertir guion y materiales narrativos en una base operativa mas clara antes de storyboard, presupuesto o planificacion.',
    bullets: ['Analisis por secuencias', 'Desglose inicial por recursos', 'Lectura de personajes y localizaciones'],
    includedInCid: true,
    ctaLabel: 'Ver Script & Breakdown AI',
  },
  {
    slug: 'storyboard',
    path: '/solutions/storyboard',
    title: 'Storyboard AI Studio',
    shortTitle: 'Storyboard AI Studio',
    type: 'Modulo independiente',
    icon: Clapperboard,
    priceLabel: 'Desde 59 EUR/mes',
    description:
      'Creacion de storyboards por secuencia, referencias visuales, moodboards y previz para desarrollo, pitch y produccion.',
    heroDescription:
      'Pensado para construir tono, ritmo visual y material de presentacion sin perder lectura cinematografica del proyecto.',
    bullets: ['Frames por secuencia', 'Look dev y moodboards', 'Previz para pitch y desarrollo'],
    includedInCid: true,
    ctaLabel: 'Ver Storyboard AI Studio',
  },
  {
    slug: 'production-planner',
    path: '/solutions/production-planner',
    title: 'Production Planner AI',
    shortTitle: 'Production Planner AI',
    type: 'Modulo independiente',
    icon: LayoutTemplate,
    priceLabel: 'Desde 69 EUR/mes',
    description:
      'Plan de rodaje, organizacion de jornadas, departamentos, recursos, secuencias, localizaciones y necesidades de produccion.',
    heroDescription:
      'Una capa de organizacion para transformar informacion del proyecto en plan de trabajo mas ordenado y legible para produccion.',
    bullets: ['Planificacion de jornadas', 'Coordinacion de recursos y departamentos', 'Base operativa por secuencia y localizacion'],
    includedInCid: true,
    ctaLabel: 'Ver Production Planner AI',
  },
  {
    slug: 'dubbing',
    path: '/solutions/dubbing',
    title: 'DubbingTake Studio AI',
    shortTitle: 'DubbingTake Studio AI',
    type: 'Modulo independiente',
    icon: Mic2,
    priceLabel: 'Desde 79 EUR/mes',
    description:
      'App para doblaje, control de takes, QC, sincronia, revision, voces y organizacion de sesiones.',
    heroDescription:
      'Construida para equipos que necesitan orden, trazabilidad y control de calidad en procesos de doblaje y revision de voces.',
    bullets: ['Control de takes y sesiones', 'QC y sincronias', 'Organizacion por voces y revision'],
    includedInCid: true,
    ctaLabel: 'Ver DubbingTake Studio AI',
  },
  {
    slug: 'sound-post',
    path: '/solutions/sound-post',
    title: 'Sound Post AI',
    shortTitle: 'Sound Post AI',
    type: 'Modulo independiente',
    icon: AudioWaveform,
    priceLabel: 'Desde 79 EUR/mes',
    description:
      'Herramientas para sonido, limpieza, stems, spotting, organizacion, mezcla preliminar y entregables.',
    heroDescription:
      'Una solucion pensada para mantener control en fases de audio, limpieza y preparacion de materiales para post y entrega.',
    bullets: ['Limpieza y preparacion de audio', 'Spotting y stems', 'Materiales organizados para post y delivery'],
    includedInCid: true,
    ctaLabel: 'Ver Sound Post AI',
  },
  {
    slug: 'promo-video',
    path: '/solutions/promo-video',
    title: 'Promo Video AI',
    shortTitle: 'Promo Video AI',
    type: 'Modulo independiente',
    icon: MonitorPlay,
    priceLabel: 'Desde 89 EUR/mes',
    description:
      'Creacion de videos promocionales, teasers, trailers conceptuales y piezas audiovisuales para pitch, venta y marketing.',
    heroDescription:
      'Pensada para productoras y equipos comerciales que necesitan presentar proyectos con piezas audiovisuales mas rapidas y atractivas.',
    bullets: ['Teasers y trailers conceptuales', 'Piezas para pitch y ventas', 'Promocion audiovisual orientada a presentacion'],
    includedInCid: true,
    ctaLabel: 'Ver Promo Video AI',
  },
  {
    slug: 'vfx',
    path: '/solutions/vfx',
    title: 'VFX & Enhancement AI',
    shortTitle: 'VFX & Enhancement AI',
    type: 'Modulo independiente',
    icon: Sparkles,
    priceLabel: 'Desde 99 EUR/mes',
    description:
      'Apoyo en VFX, generacion de assets visuales, mejora de planos, referencias y elementos para postproduccion.',
    heroDescription:
      'Una capa de apoyo visual para postproduccion, referencias y mejora de materiales donde se necesita mas capacidad de iteracion.',
    bullets: ['Assets visuales y referencias', 'Mejora de planos', 'Apoyo a fases de VFX y enhancement'],
    includedInCid: true,
    ctaLabel: 'Ver VFX & Enhancement AI',
  },
]

export const allSolutions: SolutionEntry[] = [
  {
    slug: cidProduct.slug,
    path: cidProduct.path,
    title: cidProduct.title,
    shortTitle: cidProduct.shortTitle,
    type: cidProduct.type,
    icon: cidProduct.icon,
    priceLabel: 'Desde 1.500 EUR setup + 299 EUR/mes',
    description: cidProduct.description,
    heroDescription: cidProduct.heroDescription,
    bullets: ['Incluye todos los modulos', 'Setup adaptado al flujo real', 'Demo y diagnostico previos'],
    includedInCid: true,
    ctaLabel: 'Ver CID',
  },
  ...standaloneSolutions,
]

export const pricingOverview = {
  cidSummary: {
    title: 'CID - Producto completo',
    setup: cidProduct.pricing.setup,
    monthly: cidProduct.pricing.monthly,
    note: 'Todos los modulos pueden quedar incluidos dentro de CID.',
  },
  customDevelopment: {
    title: 'Desarrollo a medida',
    description:
      'AILinkCinema tambien ofrece desarrollo de soluciones IA personalizadas, integraciones y adaptaciones de flujo bajo presupuesto y diagnostico previo.',
  },
}

export function getSolutionBySlug(slug: string) {
  return standaloneSolutions.find((solution) => solution.slug === slug)
}

export const publicBrandLinks = [
  { label: 'Inicio', to: '/' },
  { label: 'Soluciones', to: '/solutions' },
  { label: 'Precios', to: '/pricing' },
  { label: 'CID', to: '/solutions/cid' },
] as const

export const publicFooterLinks = [
  { label: 'Soluciones', to: '/solutions' },
  { label: 'Precios', to: '/pricing' },
  { label: 'Explorar CID', to: '/solutions/cid' },
  { label: 'Solicitar demo', to: '/register/demo' },
] as const

export const publicLegalLinks = [
  { label: 'Privacidad', to: '/legal/privacidad' },
  { label: 'Aviso legal', to: '/legal/aviso-legal' },
  { label: 'Terminos', to: '/legal/terminos' },
  { label: 'IA y contenidos', to: '/legal/ia-y-contenidos' },
] as const

export const solutionsMarketingNotes = [
  'Cada modulo puede contratarse por separado.',
  'Todos los modulos pueden incluirse dentro de CID.',
  'CID incorpora setup inicial porque se adapta al flujo real de cada produccion.',
  'AILinkCinema tambien ofrece desarrollo a medida bajo presupuesto.',
]

export const solutionsHeroContent = {
  title: 'Soluciones IA para cine con estructura comercial clara y enfoque de industria.',
  description:
    'AILinkCinema organiza su oferta en un producto principal - CID - y una suite de aplicaciones especializadas que pueden contratarse por separado o formar parte del flujo completo.',
}

export const pricingHeroContent = {
  title: 'Precios pensados para producto, modulos y configuracion real de pipeline.',
  description:
    'El modelo comercial diferencia entre el producto integral CID, los modulos independientes y el desarrollo a medida para partners, estudios o productoras.',
}

export const cidPageHighlights = [
  'Producto principal de AILinkCinema',
  'Conecta departamentos y fases del proyecto',
  'Incluye todos los modulos en un mismo entorno',
] as const

export const solutionsPageHighlights = [
  'Producto flagship + modulos contratables por separado',
  'Mismo lenguaje visual y comercial premium',
  'Preparado para productoras, estudios y partners',
] as const

export const pricingPageHighlights = [
  'CID con setup y cuota mensual',
  'Apps con precio individual desde 49 EUR/mes',
  'Desarrollo a medida bajo presupuesto',
] as const

export const marketingPillars = [
  { icon: Sparkles, title: 'Software serio para cine' },
  { icon: FileSearch, title: 'Pipeline y departamentos conectados' },
  { icon: Clapperboard, title: 'Herramientas visuales y operativas' },
] as const
