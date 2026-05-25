import {
  BadgeCheck,
  Briefcase,
  Clapperboard,
  Film,
  FileSearch,
  FolderKanban,
  LayoutTemplate,
  MonitorPlay,
  PanelsTopLeft,
  PenSquare,
  ShieldCheck,
  Sparkles,
  Users,
  Waypoints,
  Scale,
} from 'lucide-react'

export const landingContent = {
  header: {
    nav: [
      { label: 'AILinkCinema', href: '#que-es' },
      { label: 'CID', href: '#cid' },
      { label: 'Soluciones', href: '#soluciones' },
      { label: 'Precios', href: '#pricing' },
      { label: 'Implementacion', href: '#mas-alla' },
      { label: 'Legal', href: '#legal' },
    ],
    primaryCta: 'Solicitar demo',
    secondaryCta: 'Explorar CID',
  },
  hero: {
    eyebrow: 'AILinkCinema / Inteligencia Artificial para Cine',
    title: 'IA diseñada para preparar cine',
    subtitle:
      'AILinkCinema combina creatividad visual, analisis de guion e inteligencia artificial con un sistema real de preproduccion cinematografica.',
    differentialLine:
      'Desde la idea inicial hasta el pitch, CID conecta guion, analisis, storyboard, visual bible, presupuesto y planificacion en un mismo flujo de trabajo.',
    description:
      'AILinkCinema transforma la creatividad cinematografica en un sistema de preproduccion claro con IA aplicada.',
    chips: ['Guion + Analisis', 'IA aplicada', 'Preproduccion real'],
    proof: [
      { label: 'Creatividad + Canvas', text: 'Lienzo colaborativo para storyboard, previz y desarrollo visual conectado al pipeline.' },
      { label: 'IA + Preproduccion', text: 'No solo genera contenido: estructura guion, referencias, presupuesto y pitch.' },
      { label: 'Implementacion real', text: 'Acompanamos la transicion de la idea creativa a una preproduccion defendible.' },
    ],
    visualProducts: [
      { name: 'Storyboard AI Studio', label: 'canvas / previz / visual', tone: 'amber' },
      { name: 'Script & Breakdown AI', label: 'creative analysis / planning', tone: 'emerald' },
      { name: 'Promo Video AI', label: 'creative pieces / pitch', tone: 'violet' },
      { name: 'Budget & Funding', label: 'budget / viability', tone: 'cyan' },
      { name: 'Pitch & Visual Bible', label: 'pitch / dossier', tone: 'rose' },
    ],
    heroCore: {
      eyebrow: 'El lienzo que conecta la preproduccion',
      title: 'CID',
      subtitle: 'El producto que une creatividad, analisis e IA con preproduccion cinematografica real',
      description:
        'CID conecta el lienzo creativo con guion, analisis, desglose, storyboard, visual bible, presupuesto, planificacion y pitch en un flujo real.',
      phases: ['Idea', 'Guion', 'Analisis', 'Storyboard', 'Visual bible', 'Presupuesto', 'Pitch'],
    },
  },
  about: {
    eyebrow: 'AILinkCinema',
    title: 'Desarrollamos software y sistemas de trabajo para preproduccion cinematografica basados en IA.',
    description:
      'AILinkCinema es un partner tecnologico que une la vision creativa con analisis, planificacion y materiales de presentacion, acompanando a equipos desde la idea hasta el pitch.',
    supportStrip: [
      'Desde la idea inicial hasta un pitch defendible.',
      'Software, automatizacion y criterio de industria.',
      'Implementacion acompanada en proyectos reales.',
    ],
    pillars: [
      {
        icon: Sparkles,
        title: 'Desarrollo de software especializado',
        text: 'Herramientas que conectan el lienzo creativo con guion, analisis, storyboard, presupuesto y pitch.',
      },
      {
        icon: Briefcase,
        title: 'Sistemas de preproduccion conectados',
        text: 'Convertimos vision creativa y tareas tecnicas en flujos operativos para desarrollo, presupuesto y presentacion.',
      },
      {
        icon: Users,
        title: 'Acompanamiento tecnico en proyectos reales',
        text: 'Acompanamos implementacion, ajuste operativo y evolucion del sistema junto al equipo creativo y productor.',
      },
    ],
  },
  cid: {
    eyebrow: 'CID / Sistema de preproduccion',
    badge: 'CID - Creatividad conectada con preproduccion real',
    title: 'El sistema que conecta la parte creativa con las decisiones clave de preproduccion cinematografica.',
    description:
      'CID une el lienzo creativo, la inteligencia artificial y la ejecucion tecnica en un flujo conectado que respeta el pipeline cinematografico.',
    priceLine: 'Setup inicial desde 1.500 EUR y cuota mensual desde 299 EUR/mes.',
    supportLine: 'Incluye los modulos CID Core adaptados al flujo real del proyecto antes de entrar en produccion.',
    departmentLine: 'Guion, visual bible, presupuesto, pitch y planificacion conectados en un mismo sistema.',
    phases: [
      'Idea',
      'Canvas',
      'Guion',
      'Storyboard',
      'Visual bible',
      'Presupuesto',
      'Pitch',
    ],
    highlights: [
      {
        icon: FileSearch,
        title: 'Creatividad y departamentos',
        text: 'El lienzo creativo conectado con analisis, storyboard, presupuesto y pitch en un mismo sistema de trabajo.',
      },
      {
        icon: Waypoints,
        title: 'Continuidad del flujo',
        text: 'Desde la idea visual y el storyboard hasta la planificacion y el dossier sin romper la estructura operativa.',
      },
      {
        icon: FolderKanban,
        title: 'Sistema orientado a pipeline',
        text: 'CID conecta decisiones, planificacion y materiales de presentacion reduciendo la friccion entre fases.',
      },
    ],
  },
  solutions: {
    eyebrow: 'Soluciones / CID Core',
    title: 'Herramientas de preproduccion diseñadas para integrarse en un flujo cinematografico real.',
    description:
      'Cada aplicacion responde a una necesidad concreta de desarrollo, analisis, storyboard, planificacion, pitch o viabilidad.',
    items: [
      {
        icon: Clapperboard,
        title: 'Storyboard AI Studio',
        description: 'Storyboard y previz para alinear secuencias, puesta en escena y referencias visuales de produccion.',
        tag: 'Storyboard / Previz',
        price: 'Desde 59 EUR/mes',
        href: '/solutions/storyboard',
        includedLabel: 'Incluido en CID',
      },
      {
        icon: MonitorPlay,
        title: 'Promo Video AI',
        description: 'Piezas promocionales, teasers y materiales de venta para presentaciones y circulacion comercial.',
        tag: 'Promo / Teaser / Pitch',
        price: 'Desde 89 EUR/mes',
        href: '/solutions/promo-video',
        includedLabel: 'Incluido en CID',
      },
      {
        icon: PenSquare,
        title: 'Script & Breakdown AI',
        description: 'Desglose tecnico de guion para produccion, con analisis por secuencias, personajes, localizaciones y necesidades reales de rodaje.',
        tag: 'Script / Breakdown',
        price: 'Desde 49 EUR/mes',
        href: '/solutions/script-breakdown',
        includedLabel: 'Incluido en CID',
      },
      {
        icon: LayoutTemplate,
        title: 'Production Planner AI',
        description: 'Planificacion de rodaje con jornadas, recursos, localizaciones, dependencias y seguimiento operativo.',
        tag: 'Planning / Production',
        price: 'Desde 69 EUR/mes',
        href: '/solutions/production-planner',
        includedLabel: 'Incluido en CID',
      },
      {
        icon: Sparkles,
        title: 'VFX & Enhancement AI',
        description: 'Coordinacion de necesidades VFX, referencias de plano y apoyo de post para pipelines profesionales.',
        tag: 'VFX / Enhancement',
        price: 'Desde 99 EUR/mes',
        href: '/solutions/vfx',
        includedLabel: 'Incluido en CID',
      },
    ],
  },
  serviceLayer: {
    eyebrow: 'Mas alla de la herramienta',
    title: 'Desarrollamos software y sistemas de trabajo para preproduccion cinematografica basados en IA.',
    description:
      'AILinkCinema no solo desarrolla software: implementa sistemas de trabajo que conectan la vision creativa con analisis, planificacion y presentacion.',
    bullets: [
      'Software y sistemas de preproduccion',
      'Implementacion adaptada al pipeline',
      'Acompanamiento tecnico especializado',
      'Soporte que entiende industria cinematografica',
    ],
  },
  pricing: {
    eyebrow: 'Precios y despliegue',
    title: 'Un modelo claro para desplegar CID o empezar por una necesidad concreta.',
    description:
      'CID se implementa con setup inicial porque se adapta al flujo real de cada proyecto. Las apps de CID Core pueden contratarse por separado y quedar integradas dentro del sistema.',
    cidSetup: 'Setup inicial para adaptar departamentos, permisos, validaciones y recorrido del pipeline a cada proyecto.',
    cidMonthly: 'Cuota mensual para operar CID con los modulos Core conectados dentro del mismo entorno.',
    modulePricing: 'Las apps empiezan desde 49 EUR/mes y permiten resolver una necesidad concreta antes de desplegar todo CID.',
    custom: 'AILinkCinema desarrolla integraciones y software especializado cuando el pipeline del cliente lo requiere.',
    bullets: [
      'Setup inicial para configurar el sistema.',
      'Cuota mensual para operar el entorno.',
      'Los modulos CID Core quedan incluidos dentro de CID.',
    ],
  },
  audience: {
    eyebrow: 'Para quien esta pensado',
    title: 'Una propuesta disenada para equipos que desarrollan, preparan y presentan cine y audiovisual.',
    description:
      'AILinkCinema no esta planteado para un perfil unico. Su valor aparece cuando varios roles necesitan una base comun sin perder especializacion por departamento.',
    items: [
      {
        icon: Briefcase,
        title: 'Productoras y estudios',
        text: 'Para equipos que quieren ordenar desarrollo, operativa, materiales y control de proyecto.',
      },
      {
        icon: Film,
        title: 'Direccion y desarrollo creativo',
        text: 'Para quienes necesitan acelerar decisiones narrativas, visuales y de presentacion.',
      },
      {
        icon: PanelsTopLeft,
        title: 'Produccion y coordinacion',
        text: 'Para quienes trabajan con fases, aprobaciones, dependencias y entregables reales.',
      },
      {
        icon: LayoutTemplate,
        title: 'Pitch, financiacion y partners',
        text: 'Para areas que necesitan materiales claros, viabilidad y continuidad desde guion hasta presentacion.',
      },
    ],
  },
  howItWorks: {
    eyebrow: 'Como funciona',
    title: 'Un modelo simple: detectar necesidad, construir flujo, preparar con claridad y presentar con control.',
    description:
      'La experiencia comercial debe sentirse cercana a software serio para cine: menos promesa abstracta, mas estructura, especializacion y recorrido de producto.',
    steps: [
      {
        step: '01',
        title: 'Mapeamos el momento del pipeline',
        text: 'Identificamos donde esta la friccion: desarrollo, analisis, previz, presupuesto, promo o pitch.',
      },
      {
        step: '02',
        title: 'Asignamos producto o solucion',
        text: 'CID cubre el flujo de preproduccion y las apps especializadas entran donde hace falta profundidad funcional.',
      },
      {
        step: '03',
        title: 'Orquestamos trabajo real',
        text: 'El equipo trabaja con una interfaz clara, decisiones trazables y materiales pensados para la industria.',
      },
      {
        step: '04',
        title: 'Validamos, revisamos y presentamos',
        text: 'Seguridad, legalidad, control de cambios y materiales claros para cada siguiente fase.',
      },
    ],
  },
  useCases: {
    eyebrow: 'Casos de uso',
    title: 'Ejemplos concretos donde la propuesta de valor se vuelve evidente.',
    description:
      'La landing debe dejar claro que AILinkCinema sirve para desarrollar mejor, presentar mejor y decidir mejor.',
    items: [
      {
        title: 'Desarrollo y pitch de proyecto',
        text: 'Convertir guion, concepto y propuesta visual en material claro para presentar y alinear.',
        outputs: ['Look references', 'Storyboard premium', 'Pitch support'],
      },
      {
        title: 'Analisis y desglose temprano',
        text: 'Preparar una lectura operativa del guion antes de comprometer rodaje, presupuesto o equipo.',
        outputs: ['Scene map', 'Breakdown basis', 'Planning signals'],
      },
      {
        title: 'Promo y piezas de venta',
        text: 'Generar teasers y materiales cortos para captar interes comercial o reforzar presentaciones.',
        outputs: ['Teasers', 'Promo cuts', 'Investor visuals'],
      },
      {
        title: 'Pitch, presupuesto y visual bible',
        text: 'Entrar en decisiones de viabilidad y presentacion con mas control sobre materiales, tono, coste y narrativa.',
        outputs: ['Pitch dossier', 'Budget signals', 'Visual bible'],
      },
    ],
  },
  trustLegal: {
    eyebrow: 'Seguridad, derechos y legalidad',
    title: 'Tecnologia aplicable al cine solo tiene valor si tambien es responsable.',
    description:
      'AILinkCinema se posiciona como empresa seria: workflows trazables, controles de uso, sensibilidad legal y espacio para validacion humana en procesos criticos.',
    items: [
      {
        icon: ShieldCheck,
        title: 'Controles de uso y trazabilidad',
        text: 'Registro de fases, validaciones y estados para que el pipeline mantenga contexto operativo.',
      },
      {
        icon: Scale,
        title: 'Derechos y consentimiento',
        text: 'Especialmente relevante en materiales fuente, derechos de referencia y reutilizacion de activos.',
      },
      {
        icon: BadgeCheck,
        title: 'QC y supervision humana',
        text: 'La IA acelera, pero las decisiones de calidad, revision y presentacion permanecen controladas.',
      },
    ],
    notes: [
      'Pensado para contextos profesionales, no para uso improvisado sin criterio de industria.',
      'Capas legales y de compliance visibles en flujos sensibles.',
      'Base preparada para trabajo con equipos, clientes y partners.',
    ],
  },
  vision: {
    eyebrow: 'Vision',
    title: 'Una nueva generacion de herramientas para la preproduccion cinematografica.',
    quote:
      'Estamos construyendo una nueva generacion de herramientas para la preproduccion cinematografica, donde la inteligencia artificial no sustituye el proceso creativo, sino que lo organiza, lo acelera y lo conecta.',
  },
  finalCta: {
    eyebrow: 'Demo, precios y siguiente paso',
    title: 'Si tu proyecto necesita preproduccion conectada y defendible, hablemos.',
    description:
      'Explora CID si buscas un sistema de preproduccion. Revisa precios si estas evaluando modulos o despliegue integral. Solicita demo si necesitas una conversacion sobre implementacion real.',
    primaryCta: 'Solicitar demo',
    secondaryCta: 'Explorar CID',
    bullets: ['CID como sistema central', 'Apps CID Core', 'Acompanamiento tecnico real'],
  },
  footer: {
    brandLine: 'AILinkCinema',
    description: 'Inteligencia artificial para preproduccion cinematografica con software especializado, CID como sistema central y acompanamiento tecnico real.',
    links: [
      { label: 'Explorar CID', href: '/solutions/cid' },
      { label: 'Solicitar demo', href: '/register/demo' },
      { label: 'Ver soluciones', href: '/solutions' },
      { label: 'Precios', href: '/pricing' },
    ],
    legalLinks: [
      { label: 'Privacidad', href: '/legal/privacidad' },
      { label: 'Aviso legal', href: '/legal/aviso-legal' },
      { label: 'Terminos', href: '/legal/terminos' },
      { label: 'IA y contenidos', href: '/legal/ia-y-contenidos' },
    ],
    legal: 'AILinkCinema posiciona a CID como sistema de preproduccion cinematografica y articula soluciones especializadas para desarrollo, analisis, storyboard, presupuesto y pitch.',
  },
} as const

export type LandingContent = typeof landingContent
