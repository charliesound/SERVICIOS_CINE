export interface DemoStep {
  step: number
  title: string
  description: string
  targetRoute: string
  roleRecommended: string[]
  talkingPoints: string[]
  expectedOutcome: string
}

export const DEMO_GUIDE: DemoStep[] = [
  {
    step: 1,
    title: "Dashboard Principal",
    description: "Ver el estado general del proyecto y módulos disponibles",
    targetRoute: "/projects/:projectId/dashboard",
    roleRecommended: ["producer", "production_manager", "director"],
    talkingPoints: [
      "Esta es la vista unificada del proyecto",
      "Cada módulo representa una fase o herramienta",
      "El progreso se calcula automáticamente según los datos cargados",
    ],
    expectedOutcome: "Usuario entiende la estructura general de CID",
  },
  {
    step: 2,
    title: "Guion y Versiones",
    description: "Ver el guion loaded y las versiones",
    targetRoute: "/projects/:projectId",
    roleRecommended: ["director", "producer"],
    talkingPoints: [
      "Se pueden cargar guiones en formatotxt, PDF o Word",
      "Cada cambio genera una versión con tracking",
      "El sistema analiza automáticamente locations, personajes, etc.",
    ],
    expectedOutcome: "Usuario ve cómo se gestiona el guion",
  },
  {
    step: 3,
    title: "Storyboard",
    description: "Ver el storyboard generado",
    targetRoute: "/projects/:projectId/storyboard-builder",
    roleRecommended: ["director", "visual"],
    talkingPoints: [
      "Generamos frames automáticamente desde el guion",
      "Se pueden regenerar en diferentes estilos",
      "Cada frame incluye descripción y cámara",
    ],
    expectedOutcome: "Usuario ve el potencial visual",
  },
  {
    step: 4,
    title: "Presupuesto",
    description: "Ver el presupuesto estimado",
    targetRoute: "/projects/:projectId/budget",
    roleRecommended: ["producer", "production_manager"],
    talkingPoints: [
      "El presupuesto se genera automáticamente desde el guion",
      "Usa reglas de mercado españolas",
      "Se puede ajustar por nivel: low, medium, high",
    ],
    expectedOutcome: "Usuario ve estimación orientativa de presupuesto",
  },
  {
    step: 5,
    title: "Ayudas y Financiación",
    description: "Ver las ayudas disponibles",
    targetRoute: "/projects/:projectId/funding",
    roleRecommended: ["producer"],
    talkingPoints: [
      "Catálogo de ayudas cinematográficas",
      "Se pueden buscar portipo, territorio, formato",
      "Cada ayuda tiene requisitos y документы",
    ],
    expectedOutcome: "Usuario conoce el catálogo de ayudas",
  },
  {
    step: 6,
    title: "Producer Pitch Pack",
    description: "Ver el dossier para productores",
    targetRoute: "/projects/:projectId/producer-pitch",
    roleRecommended: ["producer"],
    talkingPoints: [
      "Genera un dossier comercial automático",
      "Incluye logline, sinopsis, presupuesto resumido",
      "Se puede exportar en JSON o Markdown",
    ],
    expectedOutcome: "Usuario tiene un dossier listo para presentar",
  },
  {
    step: 7,
    title: "Distribution Pack",
    description: "Ver el pack de distribución",
    targetRoute: "/projects/:projectId/distribution",
    roleRecommended: ["producer"],
    talkingPoints: [
      "Genera packs específicos por canal: distribuidora, plataforma, festival",
      "Incluye estrategia territorial y ventanas",
      "No garantiza aceptación, es herramienta de preparación",
    ],
    expectedOutcome: "Usuario tiene materiales comerciales",
  },
  {
    step: 8,
    title: "CRM Comercial",
    description: "Ver seguimiento comercial",
    targetRoute: "/projects/:projectId/crm",
    roleRecommended: ["producer"],
    talkingPoints: [
      "Seguimiento manual de oportunidades",
      "Estados: nueva, contactada, interesada, negociación",
      "No envía emails automáticamente",
    ],
    expectedOutcome: "Usuario entiende el seguimiento manual",
  },
  {
    step: 9,
    title: "Cambios y Aprobaciones",
    description: "Ver Change Requests",
    targetRoute: "/projects/:projectId/change-requests",
    roleRecommended: ["producer", "production_manager"],
    talkingPoints: [
      "Registro de cambios creativos y de presupuesto",
      "Requiere aprobación según el tipo de cambio",
      "Tracking completo de quién approve qué",
    ],
    expectedOutcome: "Usuario ve el flujo de gobernanza",
  },
  {
    step: 10,
    title: "Editorial / DaVinci",
    description: "Ver premontaje y export",
    targetRoute: "/projects/:projectId/editorial",
    roleRecommended: ["editor", "producer"],
    talkingPoints: [
      "Generamos un XML para DaVinci Resolve",
      "Incluye referencias a media indexada",
      "Export multiplataforma: Windows, Mac, Linux",
    ],
    expectedOutcome: "Usuario puede importar en DaVinci",
  },
]

export const DEMO_QUICK_GUIDE = DEMO_GUIDE.slice(0, 5)

export const DEMO_FULL_GUIDE = DEMO_GUIDE