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
    eyebrow: 'AILinkCinema / IA para cine y audiovisual',
    title: 'IA disenada para hacer cine',
    subtitle:
      'Desarrollamos herramientas de inteligencia artificial para crear, producir y entregar proyectos audiovisuales, conectando todos los departamentos en un flujo de trabajo real.',
    differentialLine:
      'A diferencia de las herramientas creativas aisladas, AILinkCinema esta disenado para produccion audiovisual completa.',
    description:
      'Partner tecnologico para cine, television y publicidad con software, sistema y acompanamiento real para equipos profesionales.',
    chips: ['Partner tecnologico', 'CID como sistema', 'Acompanamiento real'],
    proof: [
      { label: 'Produccion completa', text: 'Desde guion y desglose hasta postproduccion, promocion y entrega final.' },
      { label: 'Por departamentos', text: 'Cada equipo trabaja con informacion util dentro de un mismo sistema de produccion.' },
      { label: 'Implementacion real', text: 'No solo software: tambien adaptacion, integracion y soporte tecnico especializado.' },
    ],
    visualProducts: [
      { name: 'DubbingTake', label: 'dubbing / QC / takes', tone: 'cyan' },
      { name: 'Storyboard AI Studio', label: 'previz / visual beats', tone: 'amber' },
      { name: 'Promo Video AI', label: 'teasers / pitch pieces', tone: 'violet' },
      { name: 'Script & Breakdown AI', label: 'analysis / planning', tone: 'emerald' },
      { name: 'Sound Post AI', label: 'cleanup / stems / spotting', tone: 'rose' },
    ],
    heroCore: {
      eyebrow: 'Sistema principal',
      title: 'CID',
      subtitle: 'Sistema completo de produccion audiovisual',
      description:
        'CID conecta guion, desglose, storyboard, planificacion, produccion, doblaje, sonido, VFX, montaje, promocion y entrega.',
      phases: ['Guion', 'Desglose', 'Storyboard', 'Planificacion', 'Produccion', 'Doblaje', 'Sonido', 'Entrega'],
    },
  },
  about: {
    eyebrow: 'AILinkCinema',
    title: 'Un partner tecnologico para cine, television y publicidad.',
    description:
      'AilinkCinema es un partner tecnologico que desarrolla soluciones de IA para cine, television y publicidad, acompanando a equipos desde la idea inicial hasta la entrega final.',
    supportStrip: [
      'Desde la idea inicial hasta la entrega final.',
      'Software, automatizacion y criterio de industria.',
      'Implementacion acompanada en proyectos reales.',
    ],
    pillars: [
      {
        icon: Sparkles,
        title: 'Desarrollo de software especializado',
        text: 'Herramientas pensadas para guion, produccion, postproduccion y entrega dentro del sector audiovisual.',
      },
      {
        icon: Briefcase,
        title: 'Automatizacion de procesos de produccion',
        text: 'Convertimos tareas repetitivas y traspasos manuales en flujos conectados entre departamentos.',
      },
      {
        icon: Users,
        title: 'Acompanamiento tecnico en proyectos reales',
        text: 'Acompanamos implementacion, ajuste operativo y evolucion del sistema junto al equipo de produccion.',
      },
    ],
  },
  cid: {
    eyebrow: 'CID',
    badge: 'CID - Cine Inteligente Digital',
    title: 'CID no es una herramienta de creacion. Es un sistema completo de produccion audiovisual.',
    description:
      'Organiza el proyecto como un flujo conectado entre desarrollo, produccion, postproduccion y entrega, con continuidad real entre departamentos.',
    priceLine: 'Setup inicial desde 1.500 EUR y cuota mensual desde 299 EUR/mes.',
    supportLine: 'Incluye todos los modulos y se adapta al flujo real del proyecto antes de entrar en operacion.',
    departmentLine: 'Todos los departamentos conectados en un mismo flujo de trabajo.',
    phases: [
      'Guion',
      'Desglose',
      'Storyboard',
      'Planificacion',
      'Produccion',
      'Doblaje',
      'Sonido',
      'VFX',
      'Montaje',
      'Promocion',
      'Entrega',
    ],
    highlights: [
      {
        icon: FileSearch,
        title: 'Trabajo por departamentos',
        text: 'Cada area recibe contexto, materiales y tareas utiles sin perder continuidad con el resto del proyecto.',
      },
      {
        icon: Waypoints,
        title: 'Continuidad entre fases',
        text: 'Guion, planificacion, produccion, post y entrega comparten una misma estructura operativa.',
      },
      {
        icon: FolderKanban,
        title: 'Sistema orientado a pipeline',
        text: 'CID conecta decisiones, seguimiento y entregables para reducir friccion en la produccion real.',
      },
    ],
  },
  solutions: {
    eyebrow: 'Soluciones',
    title: 'Herramientas profesionales por departamento, tambien incluidas dentro de CID.',
    description:
      'Cada aplicacion responde a una necesidad concreta de produccion audiovisual y puede operar por separado o dentro del sistema completo de CID.',
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
    title: 'AILinkCinema no solo desarrolla software.',
    description:
      'Tambien acompana a productoras y equipos creativos en la implementacion real de soluciones de inteligencia artificial en sus proyectos.',
    bullets: [
      'Adaptacion a flujos de produccion reales',
      'Integracion de herramientas',
      'Optimizacion de pipelines',
      'Soporte tecnico especializado',
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
