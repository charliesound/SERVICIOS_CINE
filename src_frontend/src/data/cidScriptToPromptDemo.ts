export const sampleScriptText = `1 INT. SALA DE REUNIONES. NOCHE.
Una directora revisa un storyboard sobre una mesa llena de notas. El productor espera una decision.
DIRECTORA
Necesito ver si esta escena respira.
PRODUCTOR
Entonces generemos otra version.`

export const expectedScene = {
  heading: 'INT. SALA DE REUNIONES. NOCHE.',
  location: 'SALA DE REUNIONES',
  timeOfDay: 'NOCHE',
  characters: ['DIRECTORA', 'PRODUCTOR'],
  actionSummary: 'Una directora revisa un storyboard sobre una mesa llena de notas. El productor espera una decision.',
}

export const expectedIntent = {
  outputType: 'storyboard_frame',
  subject: 'storyboard panels for the scene',
  dramaticIntent: 'support a moment of evaluation and narrative decision',
  lighting: 'low-key lighting with warm practicals, controlled contrast, readable shadows and premium amber accents',
}

export const expectedPromptShort =
  'subject: storyboard panels for the scene, action: mapping the scene into readable shot panels with camera logic, environment: int sala de reuniones at noche'

export const directorLensExamples = [
  {
    lensId: 'adaptive_auteur_fusion',
    label: 'Seleccion automatica',
    why: 'elige lenguaje cinematografico segun conflicto, espacio y tono',
  },
  {
    lensId: 'suspense_geometric_control',
    label: 'Suspense geometrico',
    why: 'dosifica informacion y usa el encuadre como presion dramatica',
  },
  {
    lensId: 'formal_symmetry_control',
    label: 'Control formal',
    why: 'ordena el espacio para revelar perturbacion bajo apariencia de calma',
  },
]

export const directorialIntentExample = {
  selectedLensId: 'adaptive_auteur_fusion',
  selectedLensName: 'Adaptive Auteur Fusion',
  miseEnScene:
    'Una directora agotada ocupa la mesa central mientras el productor queda de pie ligeramente desplazado; storyboard, notas y huecos de espacio hacen visible la decision pendiente.',
  blocking:
    'La distancia entre ambos personajes y la mesa funciona como tension creativa materializada.',
  cameraStrategy:
    'Plano medio lateral con profundidad suficiente para leer personajes, materiales y aire negativo entre ellos.',
  suspenseOrEmotionStrategy:
    'La escena retiene la decision y deja que el peso dramatico aparezca antes en las pausas y miradas que en el dialogo.',
  rhythmStrategy:
    'Ritmo contenido, preciso y sobrio, con progresion de presion mas que de movimiento.',
}

export const promptBefore =
  'cinematic image of a meeting room, dramatic lighting'

export const promptAfter =
  'Una directora revisa un storyboard sobre una mesa llena de notas en una sala de reuniones nocturna; el productor espera de pie, ligeramente fuera de foco; la camara se mantiene en un plano medio lateral que deja ver el espacio entre ambos como tension dramatica; luz practica calida sobre los papeles y fondo frio corporativo; composicion precisa, sobria, con continuidad de mesa, notas, storyboard y decision pendiente.'

export const montageIntelligenceExample = {
  sceneText:
    'Una directora revisa un storyboard sobre una mesa llena de notas. El productor espera una decision.',
  directorThinking:
    'La escena no debe resolver la decision; debe contenerla. La distancia entre ambos personajes y la mesa materializa la presion creativa.',
  montageThinking:
    'Este plano existe para preparar el corte hacia un detalle del storyboard o hacia la reaccion del productor. Debe reservar parte de la informacion visual y mantener continuidad de mirada y eje.',
  genericPrompt:
    'Cinematic image of a director looking at a storyboard.',
  cidPromptWithMontage:
    'Primer plano sostenido de una directora mirando un storyboard, pero el encuadre deja fuera la pagina completa para reservar la revelacion al siguiente plano; la luz practica ilumina sus ojos y el borde del papel; el fondo mantiene al productor desenfocado como presion narrativa; el plano esta disenado para cortar despues a un detalle del storyboard, manteniendo continuidad de mirada y tension de decision.',
  beforeAfterLabels: ['Prompt generico', 'Direccion + montaje CID'],
}

export const proofLabels = [
  'Guion detectado',
  'Escena estructurada',
  'Intencion cinematografica',
  'Lente directorial',
  'Inteligencia de montaje',
  'Mise en scene',
  'Prompt controlado',
  'Validacion semantica',
]
