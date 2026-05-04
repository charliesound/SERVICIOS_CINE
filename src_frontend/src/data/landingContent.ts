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
      { label: 'Soluciones', href: '/solutions' },
      { label: 'Precios', href: '/pricing' },
      { label: 'Casos de uso', href: '#casos' },
      { label: 'Legal', href: '#legal' },
    ],
    primaryCta: 'Solicitar demo',
    secondaryCta: 'Explorar CID',
  },
  hero: {
    eyebrow: 'AILinkCinema / AI tools for cinema',
    title: 'IA disenada para hacer cine',
    subtitle:
      'Creamos herramientas inteligentes para desarrollar, producir, analizar, organizar y entregar proyectos audiovisuales con flujos de trabajo pensados para la industria real.',
    description:
      'AILinkCinema crea herramientas de inteligencia artificial disenadas para el sector cinematografico, desde soluciones a medida hasta producto flagship y apps especializadas.',
    chips: ['Partner tecnologico', 'Producto flagship: CID', 'Apps especializadas'],
    proof: [
      { label: 'Industria real', text: 'Flujos pensados para desarrollo, produccion, postproduccion y entrega audiovisual.' },
      { label: 'Acompanamiento', text: 'Diagnostico, configuracion y evolucion de producto segun el momento de cada produccion.' },
      { label: 'IA aplicada', text: 'Herramientas concretas para guion, storyboard, dubbing, promo, planificacion y sonido.' },
    ],
    visualProducts: [
      { name: 'DubbingTake Studio AI', label: 'dubbing / QC / takes', tone: 'cyan' },
      { name: 'Storyboard AI Studio', label: 'previz / visual beats', tone: 'amber' },
      { name: 'Promo Video AI', label: 'teasers / pitch pieces', tone: 'violet' },
      { name: 'Script & Breakdown AI', label: 'analysis / planning', tone: 'emerald' },
      { name: 'Sound Post AI', label: 'cleanup / stems / spotting', tone: 'rose' },
    ],
    heroCore: {
      eyebrow: 'Producto principal',
      title: 'CID',
      subtitle: 'Cine Inteligente Digital',
      description:
        'Un pipeline integral para conectar guion, analisis, desglose, storyboard, presupuesto, produccion, postproduccion, distribucion y entrega.',
      phases: ['Guion', 'Analisis', 'Storyboard', 'Budget', 'Produccion', 'Post', 'Distribucion', 'Entrega'],
    },
  },
  about: {
    eyebrow: 'Que es AILinkCinema',
    title: 'Una empresa que combina producto, soluciones a medida y acompanamiento para cine y audiovisual.',
    description:
      'AILinkCinema funciona como partner tecnologico para productoras, estudios y equipos que necesitan software especializado, criterio de industria y despliegues adaptados a su flujo real.',
    supportStrip: [
      'Empresa enfocada en IA aplicada al sector cinematografico.',
      'Soluciones a medida para equipos, estudios y partners.',
      'Acompanamiento desde diagnostico hasta operacion del flujo.',
    ],
    pillars: [
      {
        icon: Sparkles,
        title: 'Herramientas con criterio de industria',
        text: 'No disenamos demos genericas: construimos software con lenguaje, necesidades y entregables del sector audiovisual.',
      },
      {
        icon: Briefcase,
        title: 'Producto + despliegue a medida',
        text: 'Combinamos software propio con adaptaciones, integraciones y configuracion segun el modelo operativo del cliente.',
      },
      {
        icon: Users,
        title: 'Acompanamiento por pipeline y equipos',
        text: 'Direccion, desarrollo, produccion, post y negocio pueden operar con una misma lectura del proyecto sin perder especializacion.',
      },
    ],
  },
  cid: {
    eyebrow: 'CID como producto principal',
    badge: 'CID - Cine Inteligente Digital',
    title: 'El producto central de AILinkCinema para desarrollar y operar una produccion audiovisual de extremo a extremo.',
    description:
      'CID organiza el proyecto como una cadena continua de decisiones, materiales y validaciones. No es una app aislada: es el nucleo del flujo audiovisual cuando creatividad, operativa y entrega necesitan hablar el mismo idioma.',
    priceLine: 'Setup inicial desde 1.500 EUR + cuota mensual desde 299 EUR/mes.',
    supportLine: 'Incluye todos los modulos y requiere demo o diagnostico previo para adaptar el flujo al proyecto real.',
    phases: [
      'Guion y desarrollo',
      'Analisis narrativo',
      'Desglose y planificacion',
      'Storyboard y previz',
      'Presupuesto y ayudas',
      'Produccion y seguimiento',
      'Postproduccion y QC',
      'Distribucion y entrega',
    ],
    highlights: [
      {
        icon: FileSearch,
        title: 'Lectura util del proyecto',
        text: 'CID convierte informacion dispersa en contexto accionable para el equipo.',
      },
      {
        icon: Waypoints,
        title: 'Continuidad entre fases',
        text: 'Cada etapa alimenta a la siguiente para evitar handoffs ciegos y reprocesos.',
      },
      {
        icon: FolderKanban,
        title: 'Producto orientado a pipeline',
        text: 'Desde desarrollo hasta delivery, el proyecto mantiene trazabilidad y estructura.',
      },
    ],
  },
  solutions: {
    eyebrow: 'Soluciones especializadas',
    title: 'Apps independientes con precio propio, tambien incluidas dentro de CID.',
    description:
      'Ademas de CID, AILinkCinema articula aplicaciones especializadas para departamentos concretos. Cada una puede contratarse por separado o entrar dentro del despliegue completo de CID.',
    items: [
      {
        icon: Mic2,
        title: 'DubbingTake Studio AI',
        description: 'App para doblaje, control de takes, QC de voz, sincronias y procesos supervisados.',
        tag: 'Dubbing / Voice / QC',
        price: 'Desde 79 EUR/mes',
        href: '/solutions/dubbing',
        includedLabel: 'Incluido en CID',
      },
      {
        icon: Clapperboard,
        title: 'Storyboard AI Studio',
        description: 'Creacion de storyboard, previz, referencias visuales y lectura cinematografica por secuencias.',
        tag: 'Storyboard / Previz',
        price: 'Desde 59 EUR/mes',
        href: '/solutions/storyboard',
        includedLabel: 'Incluido en CID',
      },
      {
        icon: MonitorPlay,
        title: 'Promo Video AI',
        description: 'Generacion de videos promocionales, teasers, piezas cortas y material para pitch comercial.',
        tag: 'Promo / Teaser / Pitch',
        price: 'Desde 89 EUR/mes',
        href: '/solutions/promo-video',
        includedLabel: 'Incluido en CID',
      },
      {
        icon: PenSquare,
        title: 'Script & Breakdown AI',
        description: 'Asistencia para guion, analisis, desglose, deteccion de necesidades y plan de rodaje.',
        tag: 'Script / Breakdown',
        price: 'Desde 49 EUR/mes',
        href: '/solutions/script-breakdown',
        includedLabel: 'Incluido en CID',
      },
      {
        icon: LayoutTemplate,
        title: 'Production Planner AI',
        description: 'Plan de rodaje, jornadas, recursos, secuencias, localizaciones y necesidades de produccion.',
        tag: 'Planning / Production',
        price: 'Desde 69 EUR/mes',
        href: '/solutions/production-planner',
        includedLabel: 'Incluido en CID',
      },
      {
        icon: AudioWaveform,
        title: 'Sound Post AI',
        description: 'Herramientas para limpieza, spotting, stems, preparacion de audio y entregables de post.',
        tag: 'Sound / Post / Delivery',
        price: 'Desde 79 EUR/mes',
        href: '/solutions/sound-post',
        includedLabel: 'Incluido en CID',
      },
      {
        icon: Sparkles,
        title: 'VFX & Enhancement AI',
        description: 'Apoyo en VFX, mejora de planos, referencias visuales y assets para postproduccion.',
        tag: 'VFX / Enhancement',
        price: 'Desde 99 EUR/mes',
        href: '/solutions/vfx',
        includedLabel: 'Incluido en CID',
      },
    ],
  },
  pricing: {
    eyebrow: 'Precios y despliegue',
    title: 'Modelo comercial claro para producto completo, apps independientes y soluciones a medida.',
    description:
      'CID se implementa con setup inicial porque se adapta al flujo real de cada produccion. Las apps pueden contratarse por separado y AILinkCinema tambien ofrece desarrollo a medida bajo presupuesto.',
    cidSetup: 'Configuracion inicial del producto flagship para adaptar estructura, departamentos, validaciones y recorrido del pipeline.',
    cidMonthly: 'Operacion mensual del entorno con todos los modulos incluidos dentro de la capa principal de producto.',
    modulePricing: 'Los servicios/apps empiezan desde 49 EUR/mes y permiten entrar por una necesidad concreta sin desplegar todo CID.',
    custom: 'Para estudios, productoras o partners que necesitan una solucion especifica, AILinkCinema ofrece desarrollo y adaptacion bajo presupuesto.',
    bullets: [
      'Cada modulo puede contratarse por separado.',
      'Todos los modulos pueden quedar incluidos dentro de CID.',
      'CID requiere demo o diagnostico previo para ajustar el flujo real.',
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
  finalCta: {
    eyebrow: 'Demo, precios y siguiente paso',
    title: 'Si tu proyecto necesita software, criterio de industria y una arquitectura de IA pensada para cine, este es el momento de hablar.',
    description:
      'Explora CID si quieres conocer el producto flagship. Revisa precios si estas evaluando modulos o despliegue integral. Solicita demo si buscas una conversacion sobre pipeline real, acompanamiento y soluciones a medida.',
    primaryCta: 'Solicitar demo',
    secondaryCta: 'Explorar CID',
    bullets: ['Producto principal: CID', 'Apps independientes con precio propio', 'Desarrollo a medida para cine y audiovisual'],
  },
  footer: {
    brandLine: 'AILinkCinema',
    description: 'Herramientas de inteligencia artificial disenadas para el sector cinematografico, desde producto flagship hasta soluciones a medida.',
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
    legal: 'AILinkCinema posiciona a CID como producto flagship y articula apps especializadas para storyboard, produccion, dubbing, sonido, promo y postproduccion.',
  },
} as const

export type LandingContent = typeof landingContent
