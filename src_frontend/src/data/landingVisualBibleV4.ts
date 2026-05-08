export type LandingVisualRoleV4 =
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

export interface LandingVisualSpecV4 {
  id: string
  section: string
  role: LandingVisualRoleV4
  narrativePurpose: string
  sourceText: string
  visualConcept: string
  imagePath: string
  status: 'ready' | 'needs_regeneration' | 'placeholder'

  semanticIntent: string
  requiredVisualElements: string[]
  forbiddenVisualElements: string[]
  cinematicLanguage: string
  continuityRequirements: string[]
  promptBrief: string
  negativePromptBrief: string
  qaChecklist: string[]
}

const commonForbidden = [
  'persona de espaldas mirando pantalla',
  'persona sola en oscuridad',
  'foto de stock genérica',
  'interfaz inventada sin función real',
  'texto legible, logos o marcas',
  'ciencia ficción barata',
  'calidad baja, borroso, sobreexpuesto',
  'caricatura, anime, estilo infantil',
  'deformaciones, manos rotas',
]

const commonNegativePrompt =
  'low quality, blurry, random interface, unreadable text, distorted UI, messy layout, watermark, logo artifacts, extra fingers, bad anatomy, cheap sci-fi, oversaturated, childish, cartoon, person standing alone in dark room facing away from camera, generic stock photo, empty dark room without context'

export const landingVisualBibleV4: LandingVisualSpecV4[] = [
  {
    id: 'hero_control_center',
    section: 'Hero principal',
    role: 'hero',
    narrativePurpose:
      'Mostrar que AILinkCinema convierte un guion en un centro de control cinematográfico conectado con pipeline real.',
    sourceText:
      'AILinkCinema combina creatividad visual, lienzo colaborativo e inteligencia artificial con un sistema real de producción audiovisual. Desde la idea inicial hasta la entrega final, CID conecta guion, storyboard, planificación, doblaje, sonido, VFX, montaje y distribución en un mismo flujo de trabajo.',
    visualConcept:
      'Dashboard panorámico 1536×864 con el flujo guion→storyboard→generación→entrega visible como paneles interconectados en un mismo sistema.',
    imagePath: '/landing-media/landing-hero-main-v4.webp',
    status: 'needs_regeneration',
    semanticIntent:
      'Centro de control operativo premium que muestra el pipeline completo: guion entrando por la izquierda, análisis en curso, storyboard generándose, salida visual a la derecha. Todo conectado visualmente.',
    requiredVisualElements: [
      'panel de guion con texto analizado',
      'panel de storyboard con viñetas',
      'panel de generación visual con resultado',
      'panel de delivery con estado',
      'conexiones visuales entre todos los paneles',
      'atmósfera oscura premium con acentos ámber',
    ],
    forbiddenVisualElements: commonForbidden,
    cinematicLanguage:
      'Plano general amplio del dashboard completo. Iluminación suave desde arriba. Destellos ámber sutiles. Sensación de centro de control real no decorativo.',
    continuityRequirements: [
      'Coherencia cromática con el resto de la landing (carbón, ámber, teal)',
      'Los paneles deben sentirse parte del mismo sistema',
      'Sin elementos UI genéricos ni decorativos sin función',
    ],
    promptBrief:
      'premium cinematic SaaS dashboard, dark charcoal background, warm amber highlights, complete production pipeline visible from left to right: screenplay panel with analyzed text feeding into storyboard panels connected to generation output panel with delivery status, elegant glass UI, interconnected modules, realistic film production control center, 16:9 widescreen, volumetric lighting, subtle amber glow',
    negativePromptBrief: commonNegativePrompt,
    qaChecklist: [
      '¿Se ve el pipeline guion→generación→entrega?',
      '¿Los paneles están visualmente conectados?',
      '¿La atmósfera es premium y no genérica?',
      '¿Se distingue del V3?',
    ],
  },
  {
    id: 'fragmented_departments',
    section: 'Problema / producción fragmentada',
    role: 'problem',
    narrativePurpose:
      'Explicar que guion, storyboard, producción y post viven en sistemas separados sin conexión.',
    sourceText:
      'Guion, storyboard, producción y post suelen operar en entornos separados. Cada fase pierde contexto de la anterior. Las herramientas de IA aparecen cada semana, pero ninguna está diseñada para integrarse en un flujo de producción real.',
    visualConcept:
      'Mesa de producción con materiales claramente separados: guion impreso, storyboard en papel, monitor de edición, panel de IA. Fragmentación ordenada pero evidente.',
    imagePath: '/landing-media/landing-problem-fragmented-v4.webp',
    status: 'needs_regeneration',
    semanticIntent:
      'Comunicar desconexión entre herramientas de producción mediante objetos físicos y digitales separados sin integración.',
    requiredVisualElements: [
      'guion impreso con anotaciones',
      'paneles de storyboard en papel',
      'monitor con línea de tiempo de edición',
      'interfaz de IA en tablet o monitor pequeño',
      'ningún elemento conectado a otro',
      'atmósfera profesional, no caótica',
    ],
    forbiddenVisualElements: commonForbidden,
    cinematicLanguage:
      'Plano cenital o contrapicado suave sobre la mesa. Separación visual entre cada elemento. Luz puntual sobre cada zona. Paleta carbón con acentos teal fríos.',
    continuityRequirements: [
      'Misma paleta que el hero pero más fría (teal en lugar de ámber)',
      'Los objetos deben ser reconocibles como herramientas de producción real',
      'No debe parecer un escritorio de oficina genérico',
    ],
    promptBrief:
      'premium production desk top-down or slight low angle, separated creative tools: printed screenplay with handwritten notes, storyboard panels on paper, editing timeline on monitor, AI interface on tablet, each element isolated without connection, organized fragmentation, cold teal accents instead of warm amber, professional film production atmosphere, dark charcoal environment, soft directional lighting',
    negativePromptBrief: commonNegativePrompt,
    qaChecklist: [
      '¿Se ve la fragmentación sin ser caótica?',
      '¿Los elementos son reconocibles como herramientas de producción?',
      '¿Hay una clara separación visual entre ellos?',
    ],
  },
  {
    id: 'script_analysis_breakdown',
    section: 'Análisis de guion',
    role: 'script_analysis',
    narrativePurpose:
      'Demostrar que CID entiende narrativa: personajes, localizaciones y planos antes de generar imagen.',
    sourceText:
      'Desglose automático de guion con identificación de personajes, localizaciones, planos y necesidades de producción. Analiza el guion, identifica personajes, localizaciones y desglose técnico. Recomienda planos y encuadres.',
    visualConcept:
      'Pantalla dividida: izquierda = guion real con líneas resaltadas en ámber; derecha = fichas semánticas de personajes, localizaciones y planos extraídos.',
    imagePath: '/landing-media/landing-ai-reasoning-v4.webp',
    status: 'needs_regeneration',
    semanticIntent:
      'Mostrar un GUIÓN REAL siendo procesado. El texto del guion debe ser visible, con overlays semánticos que revelan personajes, localizaciones, planos recomendados.',
    requiredVisualElements: [
      'texto de guion real legible (sin palabras completas, pero con estructura de guion)',
      'resaltado semántico sobre el texto (personajes en ámber, localizaciones en teal)',
      'panel lateral con fichas de personajes',
      'panel inferior con desglose de localizaciones',
      'conexiones entre texto y fichas',
    ],
    forbiddenVisualElements: commonForbidden,
    cinematicLanguage:
      'Plano medio de la interfaz de análisis. El guion ocupa el centro visual. Las extracciones semánticas fluyen hacia los paneles laterales. Iluminación tipo sala de edición.',
    continuityRequirements: [
      'El guion visible debe tener estructura de escena real (INT./EXT., personajes, diálogos)',
      'Las fichas extraídas deben coincidir con el contenido del guion visible',
      'Misma familia visual que el hero (carbón, ámber)',
    ],
    promptBrief:
      'premium cinematic SaaS split-screen interface, left side shows actual screenplay text with amber highlights on character names and teal on locations, right side shows semantic extraction cards with character portraits, location tags, recommended shot types, elegant glass UI panels, dark charcoal background, warm amber accents, sophisticated AI analysis visualization, realistic film production software, professional analytical atmosphere, no generic dashboard',
    negativePromptBrief: commonNegativePrompt,
    qaChecklist: [
      '¿Se ve texto de guion real (aunque simulado)?',
      '¿Hay extracción semántica visible (personajes, localizaciones)?',
      '¿Las fichas laterales se conectan visualmente con el texto?',
    ],
  },
  {
    id: 'moodboard_bible',
    section: 'Moodboard / biblia visual',
    role: 'moodboard',
    narrativePurpose:
      'Hacer visible que CID transforma el texto en atmósfera coherente: color, iluminación, vestuario, localización.',
    sourceText:
      'Construye referencias visuales por escena, personaje y atmósfera. Consolida la dirección artística antes del rodaje.',
    visualConcept:
      'Tablero dividido en zonas por escena. Cada escena tiene su paleta cromática, referencia de localización, vestuario y atmósfera.',
    imagePath: '/landing-media/landing-concept-keyvisual-v4.webp',
    status: 'needs_regeneration',
    semanticIntent:
      'Mostrar un MOODBOARD ORGANIZADO POR ESCENAS, no una colección aleatoria de imágenes bonitas. Cada grupo de referencias corresponde a una escena del guion.',
    requiredVisualElements: [
      '3-4 grupos visuales distintos, cada uno etiquetado con nombre de escena',
      'cada grupo incluye: paleta de color, referencia de localización, referencia de vestuario',
      'conexión sutil entre grupos (misma producción, diferentes escenas)',
      'atmósfera premium de departamento de arte',
    ],
    forbiddenVisualElements: commonForbidden,
    cinematicLanguage:
      'Plano general del tablero. Cada zona con su propia atmósfera pero armonía global. Iluminación de sala de arte. Paletas de color visibles como swatches.',
    continuityRequirements: [
      'Las paletas de cada escena deben ser distintas pero armonizar entre sí',
      'Si la Escena 1 es nocturna, su paleta debe ser fría; si la Escena 2 es diurna, cálida',
      'Misma jerarquía visual que los bloques anteriores',
    ],
    promptBrief:
      'premium cinematic art department moodboard, large board divided into 3-4 scene zones, each zone showing: color palette swatches, location reference photography, wardrobe fabric samples, lighting reference stills, scene labels visible, elegant organized layout, dark charcoal background with warm amber accents, sophisticated creative development atmosphere, professional film pre-production environment, realistic art department tools',
    negativePromptBrief: commonNegativePrompt,
    qaChecklist: [
      '¿El moodboard está organizado por escenas?',
      '¿Cada escena tiene paleta + localización + vestuario?',
      '¿Se distingue de un tablero Pinterest genérico?',
    ],
  },
  {
    id: 'storyboard_sequence',
    section: 'Storyboard / previsualización',
    role: 'storyboard',
    narrativePurpose:
      'Mostrar que CID construye storyboards con continuidad: planos del mismo personaje, misma localización, misma luz.',
    sourceText:
      'Construye tu storyboard escena por escena. Cada plano mantiene coherencia narrativa, dirección de arte y continuidad visual. Genera storyboards por plano con encuadre, ángulo e iluminación.',
    visualConcept:
      'Tira horizontal de 5-6 viñetas del mismo personaje en la misma localización: plano general, plano medio, over shoulder, contraplano, primer plano, two-shot.',
    imagePath: '/landing-media/landing-storyboard-preview-v4.webp',
    status: 'needs_regeneration',
    semanticIntent:
      'Secuencia REAL de storyboard cinematográfico. Mismos personajes, misma ropa, misma luz, diferentes encuadres. Progresión narrativa evidente.',
    requiredVisualElements: [
      '5-6 viñetas consecutivas en formato horizontal',
      'mismo personaje principal en todas las viñetas',
      'misma localización de fondo',
      'progresión de planos: general → medio → over shoulder → contraplano → primer plano',
      'etiquetas de tipo de plano visibles',
      'consistencia de vestuario e iluminación entre viñetas',
    ],
    forbiddenVisualElements: commonForbidden,
    cinematicLanguage:
      'Composición horizontal, las viñetas fluyen de izquierda a derecha. Cada plano respeta el eje de cámara. Iluminación consistente. Estilo de storyboard profesional, no ilustración.',
    continuityRequirements: [
      'El personaje debe usar la misma ropa en todas las viñetas',
      'La localización debe ser la misma (misma mesa, misma ventana, etc.)',
      'La luz debe venir de la misma dirección en todos los planos',
    ],
    promptBrief:
      'premium cinematic storyboard strip with 5-6 consecutive panels showing the same scene and same character, wide shot establishing location, medium shot showing character, over-the-shoulder shot, reverse shot close-up on face, close-up detail, two-shot, all panels maintain consistent wardrobe, same indoor location, same lighting direction, amber and charcoal film aesthetic, professional storyboard layout with shot type labels, realistic film pre-visualization, dark premium atmosphere',
    negativePromptBrief: commonNegativePrompt,
    qaChecklist: [
      '¿Hay al menos 5 viñetas consecutivas?',
      '¿El personaje usa la misma ropa en todas?',
      '¿El fondo/localización es consistente?',
      '¿Hay progresión de planos (general → primer plano)?',
    ],
  },
  {
    id: 'comfyui_generation_engine',
    section: 'Generación visual controlada',
    role: 'pipeline_builder',
    narrativePurpose:
      'Mostrar que ComfyUI recibe prompts estructurados y genera dentro de un flujo controlado con validación.',
    sourceText:
      'Workflows de Flux/SDXL para storyboard, concept art y previz. Control de estilo, iluminación y atmósfera. El sistema valida antes de regenerar.',
    visualConcept:
      'Interfaz node-based: caja de prompt → nodos Flux → imagen generada → badge de validación (✓ VALIDADO o ⚠ REVISAR).',
    imagePath: '/landing-media/landing-comfyui-generation-v4.webp',
    status: 'needs_regeneration',
    semanticIntent:
      'Mostrar el PROCESO: prompt estructurado por CID → nodos de ComfyUI → resultado visual con estado de validación.',
    requiredVisualElements: [
      'panel de prompt/input con texto visible',
      'nodos de workflow conectados',
      'imagen generada visible en panel de salida',
      'badge o indicador de validación',
      'estética node-based profesional',
    ],
    forbiddenVisualElements: commonForbidden,
    cinematicLanguage:
      'Plano centrado en el workflow. Los nodos tienen un glow sutil. La imagen generada es el punto focal visual. Iluminación tipo laboratorio digital premium.',
    continuityRequirements: [
      'El estilo de la imagen generada debe ser coherente con los storyboards',
      'La interfaz node-based debe sentirse real, no decorativa',
      'Misma paleta carbón + ámber',
    ],
    promptBrief:
      'premium cinematic node-based AI generation interface, connected workflow nodes with subtle amber glow, prompt module on left feeding into Flux model nodes, cinematic frame emerging on right output panel, validation badge showing green checkmark, dark charcoal background, elegant glass UI, professional creative AI tooling, realistic ComfyUI-style interface, sophisticated film technology atmosphere, the generated image should look like a premium cinematic still',
    negativePromptBrief: commonNegativePrompt,
    qaChecklist: [
      '¿Se ve el workflow de nodos claramente?',
      '¿Hay una imagen generada visible como resultado?',
      '¿Hay indicador de validación?',
    ],
  },
  {
    id: 'pipeline_orchestration',
    section: 'Pipeline Builder',
    role: 'pipeline_builder',
    narrativePurpose:
      'Hacer visible el flujo completo: guion → análisis → prompt → ComfyUI → storyboard → revisión → entrega.',
    sourceText:
      'Orquesta el flujo completo: guion → análisis → prompt visual → ComfyUI → storyboard → revisión → entrega. Trazabilidad total.',
    visualConcept:
      'Pipeline horizontal premium con 7 módulos conectados: 📄 Guion → 🔍 Análisis → ✏️ Prompt → 🎨 ComfyUI → 🎞️ Storyboard → ✅ Revisión → 📦 Entrega.',
    imagePath: '/landing-media/landing-cid-orchestration-v4.webp',
    status: 'needs_regeneration',
    semanticIntent:
      'Diagrama de flujo PREMIUM con módulos reales. Cada módulo debe tener una miniatura o icono representativo. No abstracto.',
    requiredVisualElements: [
      '7 módulos en secuencia horizontal',
      'cada módulo con icono y etiqueta',
      'flechas de conexión entre módulos',
      'los módulos deben tener miniaturas/imágenes pequeñas representativas',
      'estilo premium, no diagrama corporativo',
    ],
    forbiddenVisualElements: commonForbidden,
    cinematicLanguage:
      'Composición horizontal panorámica. Los módulos flotan sobre un fondo oscuro con líneas de conexión luminosas. Transiciones sutiles entre fases.',
    continuityRequirements: [
      'Coherencia visual con los paneles de hero y generación',
      'Las miniaturas en cada módulo deben reflejar el contenido real',
      'Misma paleta carbón + ámber + teal',
    ],
    promptBrief:
      'premium cinematic pipeline diagram, 7 horizontal modules connected by glowing amber flow lines: Guion (script icon with text snippet), Analisis (magnifying glass over structured data), Prompt (edit icon), ComfyUI (node icon), Storyboard (film strip), Revision (checkmark), Entrega (package), each module has a small thumbnail preview, dark charcoal background, elegant glass modules, subtle teal accents, professional film production orchestration, sophisticated system architecture visualization',
    negativePromptBrief: commonNegativePrompt,
    qaChecklist: [
      '¿Hay 7 módulos claramente identificables?',
      '¿Cada módulo tiene icono + etiqueta + miniatura?',
      '¿Las conexiones entre módulos son visibles?',
    ],
  },
  {
    id: 'collaboration_review',
    section: 'Colaboración y aprobación',
    role: 'collaboration',
    narrativePurpose:
      'Enseñar que director, producción y equipo revisan, comentan y aprueban sobre materiales concretos.',
    sourceText:
      'Comparte storyboards, moodboards y versiones con tu equipo. Director, productor y equipo pueden revisar, comentar y aprobar versiones.',
    visualConcept:
      'Sala oscura premium con dos profesionales (director + productor) señalando un storyboard en pantalla grande. Anotaciones visibles.',
    imagePath: '/landing-media/landing-producers-studios-v4.webp',
    status: 'needs_regeneration',
    semanticIntent:
      'REVISIÓN REAL DE PRODUCCIÓN. No personas genéricas frente a pantallas. Debe verse la toma de decisiones sobre material concreto.',
    requiredVisualElements: [
      'dos personas (director y productor) en una sala',
      'una pantalla grande mostrando storyboard o moodboard',
      'al menos una persona señalando la pantalla',
      'anotaciones o notas adhesivas virtuales visibles',
      'atmósfera de sala de proyección/post',
    ],
    forbiddenVisualElements: commonForbidden,
    cinematicLanguage:
      'Plano medio desde atrás del sofá/silla, mostrando la pantalla y los profesionales de costado o tres cuartos. Iluminación de pantalla como fuente principal de luz.',
    continuityRequirements: [
      'El material en pantalla debe ser coherente con los storyboards V4',
      'La sala debe sentirse de producción, no de coworking',
      'Misma paleta oscura premium',
    ],
    promptBrief:
      'premium cinematic production review room, dark intimate atmosphere, director and producer reviewing storyboard frames on a large premium display, one person pointing at the screen, subtle annotations visible on screen, warm screen glow illuminating faces, professional decision-making mood, high-end post-production facility, elegant dark interior, amber accent lighting, realistic film production environment, no generic office or coworking space',
    negativePromptBrief: commonNegativePrompt,
    qaChecklist: [
      '¿Se ve la pantalla con material de storyboard?',
      '¿Hay al menos una persona interactuando con el material?',
      '¿La atmósfera es de producción, no de oficina genérica?',
    ],
  },
  {
    id: 'professional_traceability',
    section: 'Diferencial profesional',
    role: 'traceability',
    narrativePurpose:
      'Hacer visible la trazabilidad, versionado y supervisión humana sobre cada decisión creativa.',
    sourceText:
      'Cada decisión creativa, cada versión y cada aprobación quedan registradas. La IA acelera, pero las decisiones de calidad y entrega permanecen controladas.',
    visualConcept:
      'Timeline de producción con versiones (V1, V2, V3...), checkpoints de aprobación (✅ director, ✅ productor), y trazabilidad de cambios.',
    imagePath: '/landing-media/landing-professional-differential-v4.webp',
    status: 'needs_regeneration',
    semanticIntent:
      'Panel de CONTROL DE VERSIONES Y APROBACIONES. Debe sentirse como un sistema de seguimiento de producción real.',
    requiredVisualElements: [
      'línea de tiempo horizontal con versiones',
      'checkpoints de aprobación con avatares o iniciales',
      'estados visibles: pendiente, aprobado, rechazado',
      'cambios registrados entre versiones',
      'estética de herramienta de producción real',
    ],
    forbiddenVisualElements: commonForbidden,
    cinematicLanguage:
      'Plano centrado en la línea de tiempo. Versiones como nodos conectados. Los checkpoints de aprobación brillan en ámber. Fondo oscuro con paneles de vidrio.',
    continuityRequirements: [
      'Las versiones deben corresponder a los mismos activos visuales (storyboard frames)',
      'La trazabilidad debe ser legible de un vistazo',
      'Misma paleta carbón + ámber',
    ],
    promptBrief:
      'premium cinematic production traceability dashboard, horizontal timeline showing versions V1 through V4 with connected nodes, approval checkpoints with avatar initials in amber (D for director, P for producer), status badges: pending, approved, rejected, version diff notes between nodes, elegant glass UI panels, dark charcoal background, warm amber highlights, sophisticated production tracking system, professional film project management atmosphere, realistic industry tool aesthetic',
    negativePromptBrief: commonNegativePrompt,
    qaChecklist: [
      '¿Hay una línea de tiempo con versiones visible?',
      '¿Los checkpoints de aprobación son claros?',
      '¿Se entiende el concepto de trazabilidad sin leer el texto?',
    ],
  },
  {
    id: 'visual_bible_overview',
    section: 'Biblia visual / Referencias CID',
    role: 'proof',
    narrativePurpose:
      'Demostrar que CID construye una biblia visual completa del proyecto cotejando guion, personajes, localizaciones, paleta de color, continuidad, planos y atmosfera antes de generar prompts.',
    sourceText:
      'CID construye una biblia visual cinematográfica: coteja el guion con referencias de personajes, localizaciones, paleta de color, continuidad, planos y atmósfera antes de generar prompts para ComfyUI.',
    visualConcept:
      'Panel luminoso y profesional que muestra la biblia visual del proyecto con secciones interconectadas: guion analizado, fichas de personajes, mapa de localizaciones, paleta cromática, lineas de continuidad y referencias de atmósfera.',
    imagePath: '/landing-media/landing-visual-bible-v4.webp',
    status: 'needs_regeneration',
    semanticIntent:
      'BIBLIA VISUAL COMPLETA. Panel que muestra cómo CID organiza y cruza toda la información visual del proyecto: guion, personajes, localizaciones, paleta, continuidad, planos y atmósfera. Conexiones visibles entre cada elemento.',
    requiredVisualElements: [
      'sección de guion analizado con líneas extraídas',
      'fichas de personajes con retratos conceptuales',
      'mapa de localizaciones con referencias fotográficas',
      'paleta cromática del proyecto visible como swatches',
      'líneas de continuidad entre escenas y elementos',
      'referencias de atmósfera e iluminación',
      'conexiones visuales entre todos los elementos',
    ],
    forbiddenVisualElements: commonForbidden,
    cinematicLanguage:
      'Plano general del panel de biblia visual. Composicion en cuadrícula tipo visual development wall premium. Conexiones visuales entre secciones. Sensación de documentación cinematográfica completa.',
    continuityRequirements: [
      'Los personajes y localizaciones deben ser coherentes entre sí (misma producción)',
      'Las conexiones deben reflejar relaciones reales del guion',
      'La paleta cromática del proyecto debe ser visible como referencia global',
    ],
    promptBrief:
      'premium cinematic visual bible reference dashboard, well-lit professional layout showing complete film project documentation, screenplay analysis with annotations, character concept sheets, location reference map, color palette swatches, continuity timeline, atmospheric references, elegant glass panels on professional background, warm amber connections, clear legible composition, sophisticated film development reference system',
    negativePromptBrief: commonNegativePrompt,
    qaChecklist: [
      '¿La biblia visual muestra guion + personajes + localizaciones + paleta + continuidad?',
      '¿La composición es clara y legible, no oscura ni abstracta?',
      '¿Hay conexiones visuales entre elementos?',
      '¿Sugiere que CID coteja toda la información antes de generar?',
    ],
  },
  {
    id: 'delivery_qc_suite',
    section: 'Delivery / QC final',
    role: 'delivery',
    narrativePurpose:
      'Cerrar demostrando que el flujo llega a aprobación final, QC y entrega del paquete audiovisual.',
    sourceText:
      'Entrar en fases avanzadas con más control sobre voz, QC, stems, trazabilidad y compliance. Validamos, revisamos y entregamos. Handoff limpio.',
    visualConcept:
      'Dashboard de delivery: lista de entregables (master video, stems, subtítulos, metadata), checkmarks de QC, estado "LISTO PARA ENTREGA".',
    imagePath: '/landing-media/landing-delivery-final-v4.webp',
    status: 'needs_regeneration',
    semanticIntent:
      'PANEL DE CIERRE DE PRODUCCIÓN. Muestra entregables, su estado de QC y la opción de aprobar entrega. Sensación de finalización profesional.',
    requiredVisualElements: [
      'lista de entregables con checkmarks',
      'estado QC visible (pasado/pendiente)',
      'badge "LISTO PARA ENTREGA" o similar',
      'panel de validación final',
      'atmósfera de sala de finishing/post',
    ],
    forbiddenVisualElements: commonForbidden,
    cinematicLanguage:
      'Plano del dashboard de delivery. Los entregables listos brillan en verde/ámber. Fondo oscuro de sala de postproducción. Luz de monitor como fuente principal.',
    continuityRequirements: [
      'Los entregables deben ser reales de producción (master video, stems, subtítulos)',
      'El estado debe reflejar un flujo completo que empezó en hero',
      'Misma paleta carbón + ámber + verde QC',
    ],
    promptBrief:
      'premium cinematic delivery and QC suite dashboard, list of deliverables with checkboxes: Master Video 4K, Audio Stems, Subtitles SRT, Metadata XML, Color Grade LUTs, each with QC status passed/pending, prominent green or amber badge "READY FOR DELIVERY", elegant glass UI panels, dark charcoal background, warm amber and subtle green highlights, professional post-production atmosphere, realistic film finishing software, sophisticated quality control interface, calm completion mood',
    negativePromptBrief: commonNegativePrompt,
    qaChecklist: [
      '¿Hay una lista de entregables con estado?',
      '¿El estado QC es visible para cada entregable?',
      '¿Hay un indicador claro de "listo para entrega"?',
    ],
  },
]

export function getLandingVisualV4(id: string): LandingVisualSpecV4 {
  const visual = landingVisualBibleV4.find((item) => item.id === id)
  if (!visual) {
    throw new Error(`Landing visual V4 not found: ${id}`)
  }
  return visual
}

export function getDefaultVisualV4(): LandingVisualSpecV4 {
  return landingVisualBibleV4[0]
}
