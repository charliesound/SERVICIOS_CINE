import {
  AudioWaveform,
  BadgeCheck,
  Briefcase,
  Clapperboard,
  Film,
  FileSearch,
  FolderKanban,
  LayoutTemplate,
  MonitorPlay,
  Mic2,
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
    title: 'IA diseñada para crear y producir cine',
    subtitle:
      'AILinkCinema combina creatividad visual, lienzo colaborativo e inteligencia artificial con un sistema real de produccion audiovisual.',
    differentialLine:
      'Desde la idea inicial hasta la entrega final, CID conecta guion, storyboard, planificacion, doblaje, sonido, VFX, montaje y distribucion en un mismo flujo de trabajo.',
    description:
      'AILinkCinema transforma la creatividad audiovisual en un sistema de produccion completo con IA aplicada.',
    chips: ['Creatividad + Canvas', 'IA aplicada', 'Produccion real'],
    proof: [
      { label: 'Creatividad + Canvas', text: 'Lienzo colaborativo para storyboard, previz y desarrollo visual conectado al pipeline.' },
      { label: 'IA + Produccion', text: 'No solo genera contenido: estructura, planifica y ejecuta produccion real.' },
      { label: 'Implementacion real', text: 'Acompanamos la transicion de la idea creativa al rodaje y entrega final.' },
    ],
    visualProducts: [
      { name: 'Storyboard AI Studio', label: 'canvas / previz / visual', tone: 'amber' },
      { name: 'Script & Breakdown AI', label: 'creative analysis / planning', tone: 'emerald' },
      { name: 'Promo Video AI', label: 'creative pieces / pitch', tone: 'violet' },
      { name: 'DubbingTake', label: 'voice / creative QC', tone: 'cyan' },
      { name: 'Sound Post AI', label: 'audio / post / delivery', tone: 'rose' },
    ],
    heroCore: {
      eyebrow: 'El lienzo que conecta con la produccion',
      title: 'CID',
      subtitle: 'El producto que une creatividad, canvas e IA con produccion cinematografica real',
      description:
        'CID conecta el lienzo creativo con guion, desglose, storyboard, planificacion, produccion, doblaje, sonido, VFX, montaje, promocion y entrega en un flujo real.',
      phases: ['Idea', 'Canvas', 'Guion', 'Storyboard', 'Produccion', 'Post', 'Entrega'],
    },
  },
  about: {
    eyebrow: 'AILinkCinema',
    title: 'Desarrollamos software y sistemas de trabajo para produccion audiovisual basados en IA.',
    description:
      'AILinkCinema es un partner tecnologico que une la vision creativa con la ejecucion de produccion, acompanando a equipos desde la idea hasta la entrega final.',
    supportStrip: [
      'Desde la idea inicial hasta la entrega final.',
      'Software, automatizacion y criterio de industria.',
      'Implementacion acompanada en proyectos reales.',
    ],
    pillars: [
      {
        icon: Sparkles,
        title: 'Desarrollo de software especializado',
        text: 'Herramientas que conectan el lienzo creativo con guion, produccion, postproduccion y entrega.',
      },
      {
        icon: Briefcase,
        title: 'Sistemas de produccion conectados',
        text: 'Convertimos vision creativa y tareas tecnicas en flujos operativos entre departamentos.',
      },
      {
        icon: Users,
        title: 'Acompanamiento tecnico en proyectos reales',
        text: 'Acompanamos implementacion, ajuste operativo y evolucion del sistema junto al equipo de produccion.',
      },
    ],
  },
  cid: {
    eyebrow: 'CID / Sistema de produccion',
    badge: 'CID - Creatividad conectada con produccion real',
    title: 'El sistema que conecta la parte creativa con todos los departamentos de una produccion audiovisual.',
    description:
      'CID une el lienzo creativo, la inteligencia artificial y la ejecucion tecnica en un flujo conectado que respeta el pipeline cinematografico.',
    priceLine: 'Setup inicial desde 1.500 EUR y cuota mensual desde 299 EUR/mes.',
    supportLine: 'Incluye todos los modulos adaptados al flujo real del proyecto antes de entrar en operacion.',
    departmentLine: 'Todos los departamentos conectados en un mismo sistema de produccion.',
    phases: [
      'Idea',
      'Canvas',
      'Guion',
      'Storyboard',
      'Produccion',
      'Doblaje',
      'Sonido',
      'VFX',
      'Entrega',
    ],
    highlights: [
      {
        icon: FileSearch,
        title: 'Creatividad y departamentos',
        text: 'El lienzo creativo conectado con produccion, post y entrega en un mismo sistema de trabajo.',
      },
      {
        icon: Waypoints,
        title: 'Continuidad del flujo',
        text: 'Desde la idea visual y el storyboard hasta el rodaje, post y entrega sin romper la estructura operativa.',
      },
      {
        icon: FolderKanban,
        title: 'Sistema orientado a pipeline',
        text: 'CID conecta decisiones, seguimiento de produccion y entregables reduciendo la friccion entre fases.',
      },
    ],
  },
  solutions: {
    eyebrow: 'Soluciones / Por departamento',
    title: 'Herramientas por departamento diseñadas para integrarse en un flujo de produccion real.',
    description:
      'Cada aplicacion responde a un oficio concreto de la produccion audiovisual y puede operar por separado o dentro del sistema CID.',
    items: [
      {
        icon: Mic2,
        title: 'DubbingTake',
        description: 'Gestion de doblaje, control de takes, sincronia y calidad para entornos profesionales.',
        tag: 'Dubbing / Voice / QC',
        price: 'Desde 79 EUR/mes',
        href: '/solutions/dubbing',
        includedLabel: 'Incluido en CID',
      },
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
        icon: AudioWaveform,
        title: 'Sound Post AI',
        description: 'Preparacion de sonido, spotting, limpieza y entregables para postproduccion y delivery.',
        tag: 'Sound / Post / Delivery',
        price: 'Desde 79 EUR/mes',
        href: '/solutions/sound-post',
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
    title: 'Desarrollamos software y sistemas de trabajo para produccion audiovisual basados en IA.',
    description:
      'AILinkCinema no solo desarrolla software: implementa sistemas de trabajo que conectan la vision creativa con la ejecucion tecnica de cada departamento.',
    bullets: [
      'Software y sistemas de produccion',
      'Implementacion adaptada al pipeline',
      'Acompanamiento tecnico especializado',
      'Soporte que entiende industria cinematografica',
    ],
  },
  pricing: {
    eyebrow: 'Precios y despliegue',
    title: 'Un modelo claro para desplegar CID o empezar por una necesidad concreta.',
    description:
      'CID se implementa con setup inicial porque se adapta al flujo real de cada produccion. Las apps pueden contratarse por separado y siguen quedando incluidas dentro del sistema completo.',
    cidSetup: 'Setup inicial para adaptar departamentos, permisos, validaciones y recorrido del pipeline a cada proyecto.',
    cidMonthly: 'Cuota mensual para operar CID con todos los modulos conectados dentro del mismo entorno.',
    modulePricing: 'Las apps empiezan desde 49 EUR/mes y permiten resolver una necesidad concreta antes de desplegar todo CID.',
    custom: 'AILinkCinema desarrolla integraciones y software especializado cuando el pipeline del cliente lo requiere.',
    bullets: [
      'Setup inicial para configurar el sistema.',
      'Cuota mensual para operar el entorno.',
      'Todos los modulos quedan incluidos dentro de CID.',
    ],
  },
  audience: {
    eyebrow: 'Para quien esta pensado',
    title: 'Una propuesta disenada para equipos que producen, desarrollan y entregan cine y audiovisual.',
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
        title: 'Post, delivery y partners',
        text: 'Para areas que necesitan trazabilidad, QC y continuidad desde origen hasta entrega.',
      },
    ],
  },
  howItWorks: {
    eyebrow: 'Como funciona',
    title: 'Un modelo simple: detectar necesidad, construir flujo, operar con claridad y entregar con control.',
    description:
      'La experiencia comercial debe sentirse cercana a software serio para cine: menos promesa abstracta, mas estructura, especializacion y recorrido de producto.',
    steps: [
      {
        step: '01',
        title: 'Mapeamos el momento del pipeline',
        text: 'Identificamos donde esta la friccion: desarrollo, previz, produccion, promo, dubbing o entrega.',
      },
      {
        step: '02',
        title: 'Asignamos producto o solucion',
        text: 'CID cubre el flujo integral y las apps especializadas entran donde hace falta profundidad funcional.',
      },
      {
        step: '03',
        title: 'Orquestamos trabajo real',
        text: 'El equipo trabaja con una interfaz clara, decisiones trazables y materiales pensados para la industria.',
      },
      {
        step: '04',
        title: 'Validamos, revisamos y entregamos',
        text: 'Seguridad, legalidad, control de cambios y handoff limpio para cada siguiente fase.',
      },
    ],
  },
  useCases: {
    eyebrow: 'Casos de uso',
    title: 'Ejemplos concretos donde la propuesta de valor se vuelve evidente.',
    description:
      'La landing debe dejar claro que AILinkCinema sirve para producir mejor, presentar mejor y entregar mejor.',
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
        title: 'Doblaje, sonido y entrega',
        text: 'Entrar en fases avanzadas con mas control sobre voz, QC, stems, trazabilidad y compliance.',
        outputs: ['Dub QC', 'Sound cleanup', 'Delivery handoff'],
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
        text: 'Especialmente relevante en voz, dubbing, materiales fuente y reutilizacion de activos.',
      },
      {
        icon: BadgeCheck,
        title: 'QC y supervision humana',
        text: 'La IA acelera, pero las decisiones de calidad, revision y entrega permanecen controladas.',
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
    title: 'Una nueva generacion de herramientas para la produccion audiovisual.',
    quote:
      'Estamos construyendo una nueva generacion de herramientas para la produccion audiovisual, donde la inteligencia artificial no sustituye el proceso creativo, sino que lo organiza, lo acelera y lo conecta.',
  },
  finalCta: {
    eyebrow: 'Demo, precios y siguiente paso',
    title: 'Si tu proyecto necesita produccion conectada por departamentos, hablemos.',
    description:
      'Explora CID si buscas el sistema completo. Revisa precios si estas evaluando modulos o despliegue integral. Solicita demo si necesitas una conversacion sobre implementacion real.',
    primaryCta: 'Solicitar demo',
    secondaryCta: 'Explorar CID',
    bullets: ['CID como sistema central', 'Apps por departamento', 'Acompanamiento tecnico real'],
  },
  footer: {
    brandLine: 'AILinkCinema',
    description: 'Inteligencia artificial para cine, television y publicidad con software especializado, CID como sistema central y acompanamiento tecnico real.',
    links: [
      { label: 'Explorar CID', href: '/solutions/cid' },
      { label: 'Solicitar demo', href: '/pricing' },
      { label: 'Ver soluciones', href: '/solutions' },
      { label: 'Precios', href: '/pricing' },
    ],
    legalLinks: [
      { label: 'Privacidad', href: '/legal/privacidad' },
      { label: 'Aviso legal', href: '/legal/aviso-legal' },
      { label: 'Terminos', href: '/legal/terminos' },
      { label: 'IA y contenidos', href: '/legal/ia-y-contenidos' },
    ],
    legal: 'AILinkCinema posiciona a CID como sistema completo de produccion audiovisual y articula soluciones especializadas para cada departamento.',
  },
} as const

export type LandingContent = typeof landingContent
