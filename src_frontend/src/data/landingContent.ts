import {
  BadgeCheck,
  Briefcase,
  CircleDollarSign,
  Clapperboard,
  FileSearch,
  Film,
  FolderKanban,
  GalleryVerticalEnd,
  PanelsTopLeft,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  Users,
  Waypoints,
} from 'lucide-react'

export const landingContent = {
  header: {
    nav: [
      { label: 'Producto', href: '#producto' },
      { label: 'Pipeline', href: '#pipeline' },
      { label: 'Modulos', href: '#modulos' },
      { label: 'Casos de uso', href: '#casos' },
      { label: 'FAQ', href: '#faq' },
    ],
    primaryCta: 'Solicitar demo',
    secondaryCta: 'Explorar CID',
  },
  hero: {
    eyebrow: 'AILinkCinema presenta CID',
    title: 'La capa operativa premium para desarrollar, producir y entregar proyectos audiovisuales.',
    subtitle:
      'CID no es un generador de video mas. Es un control center cinematografico para productores y equipos que necesitan guion, storyboard, presupuesto, operativa y entrega conectados en un mismo sistema.',
    description:
      'Pensado para proyectos reales: ordena decisiones creativas, materiales de pitch, pipeline de produccion y continuidad editorial sin fragmentar el contexto entre herramientas sueltas.',
    primaryCta: 'Solicitar demo',
    secondaryCta: 'Explorar CID',
    pills: [
      'Guion y versiones',
      'Storyboard asistido',
      'Presupuesto y ayudas',
      'Produccion y review',
      'Editorial y entrega',
    ],
    trustLine: [
      'Pensado para productores',
      'Flujo multirol',
      'Listo para demo y piloto',
    ],
  },
  controlCenter: {
    projectName: 'CID / Feature Launch',
    phase: 'Pilot mode',
    pulseLabel: 'Pipeline sincronizado',
    sideCards: [
      { label: 'Guion', value: '12 versiones', tone: 'amber' },
      { label: 'Analisis', value: '48 beats', tone: 'blue' },
      { label: 'Presupuesto', value: '4 escenarios', tone: 'emerald' },
    ],
    timeline: [
      'Script diagnosis',
      'Look dev',
      'Shot plan',
      'Budget review',
      'Editorial handoff',
    ],
    modules: [
      { title: 'Guion', text: 'Impacto narrativo y control de versiones', tone: 'amber' },
      { title: 'Storyboard', text: 'Frames, continuidad y referencias', tone: 'blue' },
      { title: 'Budget', text: 'Escenarios y alertas de produccion', tone: 'emerald' },
      { title: 'Review', text: 'Feedback operativo y aprobaciones', tone: 'rose' },
    ],
    floatingCards: [
      { title: 'Guion', detail: 'structure v12', tone: 'amber' },
      { title: 'Analisis', detail: 'scene map', tone: 'blue' },
      { title: 'Storyboard', detail: 'visual beats', tone: 'violet' },
      { title: 'Presupuesto', detail: '4 escenarios', tone: 'emerald' },
      { title: 'Produccion', detail: 'task sync', tone: 'cyan' },
      { title: 'Review', detail: 'notes + signoff', tone: 'rose' },
      { title: 'Entrega', detail: 'reports + export', tone: 'emerald' },
    ],
  },
  trust: {
    eyebrow: 'Confianza operativa',
    title: 'Una unica vista del proyecto para equipos que trabajan con deadlines, aprobaciones y entregables reales.',
    description:
      'CID esta planteado para direccion, produccion ejecutiva, coordinacion, pitch, montaje y delivery. La promesa no es generar ruido visual, sino reducir friccion entre decisiones y ejecucion.',
    metrics: [
      { value: '1', label: 'base de proyecto', detail: 'guion, visual, presupuesto y entrega alineados' },
      { value: '6', label: 'capas conectadas', detail: 'desarrollo, storyboard, funding, produccion, review y editorial' },
      { value: '0', label: 'handoffs ciegos', detail: 'cada modulo hereda contexto del anterior' },
    ],
    strips: [
      'Workflow para productores',
      'Continuidad narrativa a editorial',
      'Pitch, presupuesto y seguimiento comercial',
      'Preparado para pilotos guiados',
    ],
  },
  about: {
    eyebrow: 'Que es CID',
    title: 'Un sistema integral para cine y audiovisual, no una herramienta aislada para generar imagen o video.',
    description:
      'CID agrupa capas que normalmente viven separadas: analisis de guion, visualizacion, estructura operativa, materiales para financiacion y continuidad editorial. La experiencia se diseña como producto premium para equipos que necesitan control, claridad y velocidad sin perder criterio.',
    pillars: [
      {
        icon: Sparkles,
        title: 'Contexto cinematografico',
        text: 'Cada decision visual o operativa se ancla al proyecto, no a prompts sueltos.',
      },
      {
        icon: ShieldCheck,
        title: 'Trazabilidad y control',
        text: 'Estados, revisiones, dependencias y materiales listos para circular por equipo.',
      },
      {
        icon: Users,
        title: 'Vista util por rol',
        text: 'Direccion, produccion, pitch y montaje trabajan sobre la misma fuente de verdad.',
      },
    ],
  },
  pipeline: {
    eyebrow: 'Pipeline visual',
    title: 'Del tratamiento al handoff editorial en un recorrido continuo.',
    description:
      'La landing presenta CID como pipeline, no como lista de features. Cada etapa alimenta la siguiente y conserva la lectura del proyecto.',
    steps: [
      {
        icon: FileSearch,
        title: 'Diagnostico de guion',
        text: 'Lectura estructural, versiones, escenas clave y puntos de tension narrativa.',
        meta: 'Narrative layer',
      },
      {
        icon: GalleryVerticalEnd,
        title: 'Storyboard y look development',
        text: 'Frames de referencia, tono visual, continuidad y material listo para pitch.',
        meta: 'Visual layer',
      },
      {
        icon: CircleDollarSign,
        title: 'Budget y funding',
        text: 'Escenarios de presupuesto, ayudas y listas de requisitos accionables.',
        meta: 'Business layer',
      },
      {
        icon: Briefcase,
        title: 'Produccion y seguimiento',
        text: 'Shotlist, pendientes, validaciones y coordinacion entre equipos.',
        meta: 'Ops layer',
      },
      {
        icon: PanelsTopLeft,
        title: 'Review y aprobaciones',
        text: 'Notas, decisiones y checkpoints antes de pasar a entrega.',
        meta: 'Review layer',
      },
      {
        icon: Film,
        title: 'Editorial y delivery',
        text: 'Reports, continuidad, export y materiales listos para handoff.',
        meta: 'Delivery layer',
      },
    ],
  },
  modules: {
    eyebrow: 'Modulos clave',
    title: 'Bloques de producto pensados para conversion comercial y uso real.',
    description:
      'Cada modulo resuelve una capa concreta del proyecto, pero todos comparten identidad, datos y continuidad de decisiones.',
    items: [
      {
        icon: FileSearch,
        title: 'Guion y versiones',
        description: 'Comparativa de versiones, impacto creativo y lectura rapida del estado del proyecto.',
        bullets: ['Versionado', 'Impacto por cambios', 'Notas por escena'],
      },
      {
        icon: Clapperboard,
        title: 'Storyboard asistido',
        description: 'Visuales de referencia con continuidad y presentacion premium para desarrollo o pitch.',
        bullets: ['Secuencias', 'Frames clave', 'Look coherente'],
      },
      {
        icon: CircleDollarSign,
        title: 'Budget estimado',
        description: 'Escenarios rapidos para que produccion y financiacion hablen sobre la misma base.',
        bullets: ['Partidas base', 'Revision de coste', 'Escenarios'],
      },
      {
        icon: FolderKanban,
        title: 'Produccion y control',
        description: 'Seguimiento de tareas, estados y dependencias del flujo operativo.',
        bullets: ['Shot planning', 'Checklist', 'Coordinacion'],
      },
      {
        icon: ScanSearch,
        title: 'Funding y dossiers',
        description: 'Ayudas, oportunidades y materiales de presentacion en el mismo entorno.',
        bullets: ['Calls verificadas', 'Requisitos', 'Pitch pack'],
      },
      {
        icon: Waypoints,
        title: 'Review y entrega',
        description: 'Feedback consolidado para que editorial y delivery no arranquen sin contexto.',
        bullets: ['Notas', 'Aprobaciones', 'Handoff'],
      },
    ],
  },
  comparison: {
    eyebrow: 'Posicionamiento',
    title: 'CID vs generadores de video simples',
    description:
      'El diferencial no es solo la salida visual. Es la capacidad de convertir informacion del proyecto en una plataforma util para negocio, produccion y entrega.',
    rows: [
      {
        label: 'Trabaja con contexto del proyecto',
        cid: 'Base comun de guion, visual, presupuesto y flujo editorial.',
        simple: 'Respuesta puntual a prompts sin memoria operativa.',
      },
      {
        label: 'Sirve a varios roles',
        cid: 'Productor, direccion, produccion, pitch y montaje en una sola capa.',
        simple: 'Uso individual y aislado.',
      },
      {
        label: 'Acompana el pipeline',
        cid: 'Desde desarrollo hasta review y delivery.',
        simple: 'Se queda en la generacion de piezas.',
      },
      {
        label: 'Convierte contenido en decision',
        cid: 'Ayuda a presentar, presupuestar, priorizar y validar.',
        simple: 'Produce resultados visuales sin gestion posterior.',
      },
    ],
  },
  useCases: {
    eyebrow: 'Casos de uso',
    title: 'Donde CID aporta mas valor en equipos audiovisuales.',
    description:
      'La propuesta comercial esta enfocada a productores y profesionales que necesitan velocidad, narrativa clara y continuidad entre departamentos.',
    items: [
      {
        icon: Briefcase,
        title: 'Productoras desarrollando varios proyectos',
        text: 'Centraliza materiales, presupuesto, ayudas y decisiones visuales sin dispersar el contexto.',
        deliverables: ['Pitch packs', 'Funding maps', 'Dashboards por proyecto'],
      },
      {
        icon: Clapperboard,
        title: 'Direccion y desarrollo creativo',
        text: 'Acelera iteraciones de escenas, look, storyboard y tono visual antes de mover recursos de rodaje.',
        deliverables: ['Look dev', 'Storyboard premium', 'Notas por secuencia'],
      },
      {
        icon: PanelsTopLeft,
        title: 'Produccion y coordinacion',
        text: 'Reduce handoffs manuales y convierte la informacion dispersa en seguimiento operativo.',
        deliverables: ['Shot planning', 'Checklists', 'Estados por area'],
      },
      {
        icon: Film,
        title: 'Editorial y entrega',
        text: 'Llega a montaje y delivery con reports, contexto previo y una lectura mas limpia del proyecto.',
        deliverables: ['Review logs', 'Continuidad editorial', 'Material de entrega'],
      },
    ],
  },
  showcase: {
    eyebrow: 'Showcase',
    title: 'Mockups pensados para vender plataforma, no solo tecnologia.',
    description:
      'Cada pantalla refuerza una historia comercial: control, claridad y continuidad entre creatividad y produccion.',
    items: [
      {
        tab: 'Control center',
        eyebrow: 'Vista principal',
        title: 'Dashboard cinematografico del proyecto',
        description: 'Una lectura de alto nivel para entender version, estado visual, riesgo de produccion y siguiente accion.',
        highlights: ['Resumen ejecutivo', 'Prioridades por equipo', 'Estado vivo del pipeline'],
        visual: 'control',
      },
      {
        tab: 'Storyboard',
        eyebrow: 'Visual pipeline',
        title: 'Storyboard listo para alinear tono y vender vision',
        description: 'Frames, continuidad y referencias dentro de una interfaz orientada a pitch y validacion.',
        highlights: ['Secuencias claras', 'Beats por escena', 'Visual premium para presentacion'],
        visual: 'storyboard',
      },
      {
        tab: 'Business',
        eyebrow: 'Ops + funding',
        title: 'Capas de presupuesto, ayudas y entrega sin salir del producto',
        description: 'CID mantiene juntas las conversaciones creativas y las operativas para que no compitan entre si.',
        highlights: ['Budget scenarios', 'Funding checklist', 'Review to delivery'],
        visual: 'business',
      },
    ],
  },
  finalCta: {
    eyebrow: 'Activar CID',
    title: 'Si el proyecto necesita una plataforma integral y no otra herramienta suelta, este es el siguiente paso.',
    description:
      'Solicita una demo guiada si quieres ver el enfoque comercial con tu caso. Si prefieres explorar el producto, entra al acceso demo CID y recorre la plataforma.',
    primaryCta: 'Solicitar demo',
    secondaryCta: 'Explorar CID',
    bullets: ['Demo guiada para productoras', 'Acceso demo para explorar flujo', 'Base pensada para crecimiento de producto'],
  },
  faq: {
    eyebrow: 'FAQ',
    title: 'Preguntas frecuentes',
    description: 'Mensajes breves para reducir friccion y reforzar el posicionamiento premium del producto.',
    items: [
      {
        question: 'CID es un generador de video?',
        answer:
          'No. CID incorpora capas visuales, pero se posiciona como plataforma integral para desarrollo, produccion, review y entrega.',
      },
      {
        question: 'Puedo usarlo solo para storyboard o pitch?',
        answer:
          'Si. Puedes entrar por una necesidad concreta y despues ampliar al resto del pipeline cuando el proyecto lo requiera.',
      },
      {
        question: 'Sirve para productores y no solo para perfiles creativos?',
        answer:
          'Si. De hecho, gran parte del valor esta en conectar lo creativo con presupuesto, ayudas, control y continuidad operativa.',
      },
      {
        question: 'La demo guiada da acceso inmediato a CID?',
        answer:
          'No necesariamente. La demo guiada es una sesion comercial. Si quieres entrar ya, utiliza el acceso demo CID.',
      },
    ],
  },
  footer: {
    brandLine: 'AILinkCinema / CID',
    description: 'Plataforma premium para desarrollo, produccion y entrega audiovisual asistida por IA.',
    links: [
      { label: 'Explorar CID', href: '/register/cid' },
      { label: 'Solicitar demo', href: '/register/demo' },
      { label: 'Acceso partner', href: '/register/partner' },
    ],
    legalLinks: [
      { label: 'Privacidad', href: '/legal/privacidad' },
      { label: 'Aviso legal', href: '/legal/aviso-legal' },
      { label: 'Términos', href: '/legal/terminos' },
      { label: 'IA y contenidos', href: '/legal/ia-y-contenidos' },
    ],
    legal: 'CID conecta creatividad, produccion y negocio en una sola experiencia de producto.',
  },
  proofIcons: [BadgeCheck, ShieldCheck, Sparkles],
} as const

export type LandingContent = typeof landingContent
