export type LandingVisualRole =
  | 'hero'
  | 'problem'
  | 'script_analysis'
  | 'moodboard'
  | 'storyboard'
  | 'pipeline_builder'
  | 'continuity'
  | 'collaboration'
  | 'production'
  | 'delivery'
  | 'b2b'
  | 'traceability'
  | 'proof'

export interface LandingVisualSpec {
  id: string
  section: string
  role: LandingVisualRole
  narrativePurpose: string
  sourceText: string
  visualConcept: string
  continuityRules: string[]
  positivePrompt: string
  negativePrompt: string
  imagePath: string
  status: 'ready' | 'needs_regeneration' | 'placeholder'
}

const commonNegativePrompt =
  'low quality, blurry, random interface, unreadable text, distorted UI, messy layout, watermark, logo artifacts, extra fingers, bad anatomy, cheap sci-fi, oversaturated, childish, cartoon'

export const landingVisualBible: LandingVisualSpec[] = [
  {
    id: 'hero_control_center',
    section: 'Hero principal',
    role: 'hero',
    narrativePurpose:
      'Mostrar que AILinkCinema convierte un guion o briefing narrativo en un centro de control cinematografico conectado con pipeline real.',
    sourceText:
      'AILinkCinema combina creatividad visual, lienzo colaborativo e inteligencia artificial con un sistema real de produccion audiovisual. Desde la idea inicial hasta la entrega final, CID conecta guion, storyboard, planificacion, doblaje, sonido, VFX, montaje y distribucion en un mismo flujo de trabajo.',
    visualConcept:
      'Centro operativo oscuro con guion analizado, escenas conectadas, revisiones visuales y supervision de pipeline dentro de un producto real.',
    continuityRules: [
      'Mantener paneles de guion, storyboard y delivery en el mismo encuadre.',
      'Evitar paisajes bonitos sin contexto de producto.',
      'La interfaz debe sentirse como software real, no como decoracion futurista.',
    ],
    positivePrompt:
      'premium cinematic SaaS interface, dark charcoal background, warm amber highlights, film production control center, realistic cinematic lighting, glass UI panels, high-end audiovisual workflow, professional studio environment, hero product screen showing screenplay analysis, connected scene cards, prompt orchestration, storyboard frames and delivery checkpoints, the image must clearly communicate a real platform that turns script text into a controlled visual production pipeline',
    negativePrompt: commonNegativePrompt,
    imagePath: '/landing-media/landing-hero-main-v3.webp',
    status: 'needs_regeneration',
  },
  {
    id: 'fragmented_departments',
    section: 'Problema / produccion fragmentada',
    role: 'problem',
    narrativePurpose:
      'Explicar que guion, storyboard, produccion y post siguen viviendo en sistemas separados y que ahi se pierde contexto.',
    sourceText:
      'Guion, storyboard, produccion y post suelen operar en entornos separados. Cada fase pierde contexto de la anterior. Las herramientas de IA aparecen cada semana, pero ninguna esta disenada para integrarse en un flujo de produccion real.',
    visualConcept:
      'Mesa de produccion con materiales desconectados, monitores aislados, documentos y referencias que no convergen en un sistema comun.',
    continuityRules: [
      'La fragmentacion debe verse organizada, no caotica ni sucia.',
      'Deben convivir materiales de guion, imagen y post.',
      'No debe parecer un dashboard centralizado.',
    ],
    positivePrompt:
      'premium cinematic SaaS interface, dark charcoal background, warm amber highlights, film production control center, realistic cinematic lighting, glass UI panels, high-end audiovisual workflow, professional studio environment, disconnected production desk with separate monitors, open script pages, storyboard references, post-production screens and isolated review stations, the image must clearly communicate fragmented departments and loss of continuity between tools',
    negativePrompt: commonNegativePrompt,
    imagePath: '/landing-media/landing-problem-fragmented-v3.webp',
    status: 'ready',
  },
  {
    id: 'script_analysis_breakdown',
    section: 'Analisis de guion',
    role: 'script_analysis',
    narrativePurpose:
      'Demostrar que el sistema entiende narrativa, escenas, personajes, localizaciones y necesidades de produccion antes de generar imagen.',
    sourceText:
      'Desglose automatico de guion con identificacion de personajes, localizaciones, planos y necesidades de produccion. Analiza el guion, identifica personajes, localizaciones y desglose tecnico. Recomienda planos y encuadres.',
    visualConcept:
      'Interfaz de lectura de guion con escenas extraidas, tarjetas conectadas, desglose tecnico y sugerencias visuales por bloque.',
    continuityRules: [
      'El guion debe sentirse como origen del sistema.',
      'Las relaciones entre escenas y personajes deben ser visibles.',
      'La interfaz no puede parecer un node editor de generacion.',
    ],
    positivePrompt:
      'premium cinematic SaaS interface, dark charcoal background, warm amber highlights, film production control center, realistic cinematic lighting, glass UI panels, high-end audiovisual workflow, professional studio environment, screenplay analysis workspace with extracted scenes, character relationship cards, location tags, tone markers and production breakdown modules, the image must clearly communicate that the product understands narrative structure before generating visuals',
    negativePrompt: commonNegativePrompt,
    imagePath: '/landing-media/landing-ai-reasoning-v3.webp',
    status: 'ready',
  },
  {
    id: 'moodboard_bible',
    section: 'Moodboard / biblia visual',
    role: 'moodboard',
    narrativePurpose:
      'Hacer visible que CID transforma el texto en una atmósfera coherente de color, iluminación, vestuario y localización.',
    sourceText:
      'Construye referencias visuales por escena, personaje y atmosfera. Consolida la direccion artistica antes del rodaje.',
    visualConcept:
      'Tablero editorial con key stills, paleta cromatica, vestuario y referencias de localizacion del mismo universo visual.',
    continuityRules: [
      'Debe leerse como moodboard y no como una sola imagen hero.',
      'La paleta debe ser coherente con el resto de la landing.',
      'No incluir personajes aleatorios sin relacion entre si.',
    ],
    positivePrompt:
      'premium cinematic SaaS interface, dark charcoal background, warm amber highlights, film production control center, realistic cinematic lighting, glass UI panels, high-end audiovisual workflow, professional studio environment, curated visual bible board built from script interpretation, color swatches, lighting references, wardrobe cues, location frames and premium film still references, the image must clearly communicate moodboard construction from narrative text',
    negativePrompt: commonNegativePrompt,
    imagePath: '/landing-media/landing-concept-keyvisual-v3.webp',
    status: 'needs_regeneration',
  },
  {
    id: 'storyboard_sequence',
    section: 'Storyboard / previsualizacion',
    role: 'storyboard',
    narrativePurpose:
      'Mostrar que a partir del texto se construyen viñetas coherentes por escena con continuidad entre planos.',
    sourceText:
      'Construye tu storyboard escena por escena. Cada plano mantiene coherencia narrativa, direccion de arte y continuidad visual. Genera storyboards por plano con encuadre, angulo e iluminacion.',
    visualConcept:
      'Storyboard horizontal con varias viñetas del mismo universo visual, mismo personaje y misma direccion de luz.',
    continuityRules: [
      'Las viñetas deben compartir personaje, tono y atmosfera.',
      'Debe sentirse secuencia, no frame aislado.',
      'La composicion debe ser legible como board de produccion.',
    ],
    positivePrompt:
      'premium cinematic SaaS interface, dark charcoal background, warm amber highlights, film production control center, realistic cinematic lighting, glass UI panels, high-end audiovisual workflow, professional studio environment, horizontal storyboard board with multiple connected frames from the same scene, same protagonist across wide shot, medium shot and close-up, visible shot planning markers and continuity notes, the image must clearly communicate sequence planning from a script',
    negativePrompt: commonNegativePrompt,
    imagePath: '/landing-media/landing-storyboard-preview-v3.webp',
    status: 'needs_regeneration',
  },
  {
    id: 'comfyui_generation_engine',
    section: 'Generacion visual controlada',
    role: 'pipeline_builder',
    narrativePurpose:
      'Mostrar que ComfyUI recibe prompts estructurados por CID y genera imagen dentro de un flujo controlado, no como experimento aislado.',
    sourceText:
      'Workflows de Flux/SDXL para storyboard, concept art y previz. Control de estilo, iluminacion y atmosfera. El sistema valida antes de regenerar.',
    visualConcept:
      'Motor visual node-based con prompt, frame resultante y checkpoints de revision conectados.',
    continuityRules: [
      'La interfaz debe sentirse node-based y profesional.',
      'El frame generado debe verse como salida del pipeline.',
      'Evitar abstraccion vacia sin nodos ni resultado.',
    ],
    positivePrompt:
      'premium cinematic SaaS interface, dark charcoal background, warm amber highlights, film production control center, realistic cinematic lighting, glass UI panels, high-end audiovisual workflow, professional studio environment, node-based visual generation engine with prompt modules feeding a premium cinematic frame, review checkpoints and regeneration controls, the image must clearly communicate controlled ComfyUI image generation inside a production pipeline',
    negativePrompt: commonNegativePrompt,
    imagePath: '/landing-media/landing-comfyui-generation-v3.webp',
    status: 'needs_regeneration',
  },
  {
    id: 'pipeline_orchestration',
    section: 'Pipeline Builder',
    role: 'pipeline_builder',
    narrativePurpose:
      'Hacer visible que Ollama interpreta, CID estructura, ComfyUI genera y el sistema valida todo el flujo.',
    sourceText:
      'Orquesta el flujo completo: guion -> analisis -> prompt visual -> ComfyUI -> storyboard -> revision -> entrega. Trazabilidad total.',
    visualConcept:
      'Diagrama premium con nodos claros y modulos conectados desde guion hasta revision final.',
    continuityRules: [
      'El flujo debe ser legible de izquierda a derecha.',
      'ComfyUI debe aparecer como motor visual y no como pieza aislada.',
      'La imagen debe sentirse producto, no escenografia vacia.',
    ],
    positivePrompt:
      'premium cinematic SaaS interface, dark charcoal background, warm amber highlights, film production control center, realistic cinematic lighting, glass UI panels, high-end audiovisual workflow, professional studio environment, elegant pipeline diagram showing script to analysis to prompt to ComfyUI to image to review, modular production routing with traceability, the image must clearly communicate product orchestration across the audiovisual workflow',
    negativePrompt: commonNegativePrompt,
    imagePath: '/landing-media/landing-cid-orchestration-v3.webp',
    status: 'needs_regeneration',
  },
  {
    id: 'continuity_guardrail',
    section: 'Continuidad visual',
    role: 'continuity',
    narrativePurpose:
      'Explicar que el sistema mantiene consistencia de personaje, tono, luz y estilo entre prompts, planos y versiones.',
    sourceText:
      'Los planos mantienen coherencia narrativa y visual entre escenas. Deteccion de saltos de raccord. Mantiene continuidad visual entre escenas.',
    visualConcept:
      'Panel de continuidad con el mismo personaje o la misma escena en varios planos y checkpoints de consistencia.',
    continuityRules: [
      'Mismo personaje entre plano general, medio y primer plano.',
      'Misma iluminacion, vestuario y tono.',
      'Evitar mosaicos abstractos o paneles vacios.',
    ],
    positivePrompt:
      'premium cinematic SaaS interface, dark charcoal background, warm amber highlights, film production control center, realistic cinematic lighting, glass UI panels, high-end audiovisual workflow, professional studio environment, continuity review board with the same character in multiple shot sizes and consistent wardrobe, lighting and mood, visual checkpoints for continuity validation, the image must clearly communicate coherence across prompts and scenes',
    negativePrompt: commonNegativePrompt,
    imagePath: '/landing-media/landing-storyboard-preview-v3.webp',
    status: 'needs_regeneration',
  },
  {
    id: 'collaboration_review',
    section: 'Colaboracion y aprobacion',
    role: 'collaboration',
    narrativePurpose:
      'Enseñar que director, produccion y equipo revisan, comentan y aprueban versiones sobre materiales concretos.',
    sourceText:
      'Comparte storyboards, moodboards y versiones con tu equipo. Comentarios contextuales por plano. Director, productor y equipo pueden revisar, comentar y aprobar versiones.',
    visualConcept:
      'Mesa de revision premium con dos perfiles profesionales, pantallas con materiales visuales y sensacion clara de decision editorial.',
    continuityRules: [
      'Debe parecer una revision real de produccion.',
      'Las pantallas deben mostrar materiales visuales del mismo proyecto.',
      'Evitar foto de stock o coworking generico.',
    ],
    positivePrompt:
      'premium cinematic SaaS interface, dark charcoal background, warm amber highlights, film production control center, realistic cinematic lighting, glass UI panels, high-end audiovisual workflow, professional studio environment, director and producer reviewing storyboard and visual versions on premium monitors, collaborative approval table with annotations and version checkpoints, the image must clearly communicate review and decision-making around generated film visuals',
    negativePrompt: commonNegativePrompt,
    imagePath: '/landing-media/landing-producers-studios-v3.webp',
    status: 'ready',
  },
  {
    id: 'production_b2b_dashboard',
    section: 'Produccion B2B',
    role: 'b2b',
    narrativePurpose:
      'Posicionar la plataforma como sistema para productoras, direccion, produccion y post, no como juguete de prompts.',
    sourceText:
      'Disenado para productoras, directores y equipos tecnicos que necesitan un sistema, no solo herramientas sueltas. Para equipos que trabajan con fases, aprobaciones, dependencias y entregables reales.',
    visualConcept:
      'Entorno ejecutivo de produccion con modulos visibles de guion, storyboard, seguimiento y entrega.',
    continuityRules: [
      'La imagen debe sugerir gestion de produccion real.',
      'Tiene que sentirse B2B y no una escena de rodaje.',
      'Debe convivir con la paleta oscura premium del resto de la landing.',
    ],
    positivePrompt:
      'premium cinematic SaaS interface, dark charcoal background, warm amber highlights, film production control center, realistic cinematic lighting, glass UI panels, high-end audiovisual workflow, professional studio environment, executive production dashboard with script module, storyboard review, planning checkpoints, version approvals and delivery status, the image must clearly communicate a B2B production system for film teams',
    negativePrompt: commonNegativePrompt,
    imagePath: '/landing-media/landing-producers-studios-v3.webp',
    status: 'needs_regeneration',
  },
  {
    id: 'professional_traceability',
    section: 'Diferencial profesional',
    role: 'traceability',
    narrativePurpose:
      'Hacer visible la trazabilidad, el versionado y la supervision humana sobre cada decision creativa.',
    sourceText:
      'Cada decision creativa, cada version y cada aprobacion quedan registradas. La IA acelera, pero las decisiones de calidad y entrega permanecen controladas por el director, el productor y el equipo tecnico.',
    visualConcept:
      'Capa de supervision premium con estados, validaciones y trazas que atraviesan el pipeline creativo.',
    continuityRules: [
      'La metafora debe ser tecnologica pero especifica.',
      'No usar abstraccion vacia ni pasillos sin significado.',
      'Se deben insinuar capas de control y aprobacion.',
    ],
    positivePrompt:
      'premium cinematic SaaS interface, dark charcoal background, warm amber highlights, film production control center, realistic cinematic lighting, glass UI panels, high-end audiovisual workflow, professional studio environment, traceability dashboard with approval layers, version history rails, human supervision markers and quality gates, the image must clearly communicate professional control over the creative pipeline',
    negativePrompt: commonNegativePrompt,
    imagePath: '/landing-media/landing-professional-differential-v3.webp',
    status: 'needs_regeneration',
  },
  {
    id: 'delivery_qc_suite',
    section: 'Delivery / QC final',
    role: 'delivery',
    narrativePurpose:
      'Cerrar el discurso demostrando que el flujo llega a aprobacion final, QC y entrega del paquete audiovisual.',
    sourceText:
      'Entrar en fases avanzadas con mas control sobre voz, QC, stems, trazabilidad y compliance. Validamos, revisamos y entregamos. Seguridad, legalidad, control de cambios y handoff limpio para cada siguiente fase.',
    visualConcept:
      'Sala de finishing oscura con control de calidad, aprobacion final y handoff de deliverables.',
    continuityRules: [
      'Debe sentirse fase final del pipeline.',
      'Monitores o checkpoints de validacion tienen que ser visibles.',
      'Evitar habitaciones vacias sin contexto.',
    ],
    positivePrompt:
      'premium cinematic SaaS interface, dark charcoal background, warm amber highlights, film production control center, realistic cinematic lighting, glass UI panels, high-end audiovisual workflow, professional studio environment, finishing and delivery suite with quality control monitors, approval status, package validation and final handoff, the image must clearly communicate the end of the audiovisual pipeline',
    negativePrompt: commonNegativePrompt,
    imagePath: '/landing-media/landing-delivery-final-v3.webp',
    status: 'needs_regeneration',
  },
  {
    id: 'script_to_prompt_proof_result',
    section: 'Texto -> prompt -> imagen',
    role: 'proof',
    narrativePurpose:
      'Demostrar de forma concreta que CID interpreta un fragmento narrativo, lo convierte en prompt y produce una visual coherente.',
    sourceText:
      'INT. SALA DE REUNIONES - NOCHE. Una directora revisa el storyboard de una escena mientras el equipo espera una decision.',
    visualConcept:
      'Resultado visual de una escena interior de revision de storyboard en entorno premium de produccion.',
    continuityRules: [
      'El encuadre debe mostrar decision editorial y revision de materiales.',
      'La atmosfera debe ser nocturna, contenida y profesional.',
      'Evitar personas random o fondos sin pantallas de trabajo.',
    ],
    positivePrompt:
      'premium cinematic SaaS interface, dark charcoal background, warm amber highlights, film production control center, realistic cinematic lighting, glass UI panels, high-end audiovisual workflow, professional studio environment, interior night meeting room where a director reviews storyboard frames on premium displays while the team waits for a decision, tense creative atmosphere, premium review workflow, the image must clearly communicate text-to-prompt interpretation for film production',
    negativePrompt: commonNegativePrompt,
    imagePath: '/landing-media/landing-producers-studios-v3.webp',
    status: 'ready',
  },
]
