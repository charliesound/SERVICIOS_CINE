# AILink Sync Dialogue — Beta Form Spec v1

## 1. Título

**AILink Sync Dialogue — Beta Form Spec v1**

Especificación del formulario de captación beta, flujo operativo manual, criterios de selección, emails y textos listos para implementar para AILink Sync Dialogue.

## 2. Objetivo del formulario

El formulario beta debe:

- Captar interesados cualificados para la beta privada.
- Entender el perfil, rol y flujo audiovisual del solicitante.
- Identificar si trabajan con audio separado y timecode (factores críticos para el matching).
- Medir el interés en una beta de pago.
- Evitar pedir material sensible (vídeo, audio, enlaces a proyectos).
- Permitir contacto posterior con consentimiento explícito.
- Preparar una futura integración con CRM o base de datos de leads.

No es un formulario de venta directa. Es un filtro cualificado para una beta controlada.

## 3. Principios

- **No pedir subida de vídeo/audio.** El formulario recoge información, no material.
- **No pedir datos innecesarios.** Cada campo tiene un motivo claro.
- **Transparencia sobre beta/prototipo.** El texto deja claro que es una beta privada, no un producto final.
- **Privacidad desde el primer contacto.** El consentimiento de contacto es obligatorio.
- **Consentimiento claro para contacto.** No se asume permiso implícito.
- **Texto breve y profesional.** Sin exageraciones, sin falsas promesas.
- **No prometer acceso automático.** Completar el formulario no garantiza entrada en la beta.
- **Tratamiento de datos.** Los datos se tratan conforme a la política de privacidad que debe redactarse legalmente antes de publicar.

## 4. Ubicación en landing

El formulario aparece en los siguientes puntos de la landing:

- **CTA hero:** al hacer clic en "Solicitar acceso beta", scroll suave al bloque del formulario.
- **Bloque beta privada:** formulario embebido directamente en la sección de beta, sin redirigir.
- **Final CTA:** repetición del formulario o botón que lleva al mismo formulario más arriba.

**Recomendación final:** formulario embebido en la misma landing, visible tras el bloque beta. No usar página separada para maximizar conversión. Como alternativa futura, si el formulario crece, una página `/ailink-sync-dialogue-beta` independiente puede funcionar para campañas específicas.

## 5. Campos definitivos

### Campos obligatorios

| Campo | Tipo | Opciones | Motivo | Uso futuro |
|---|---|---|---|---|
| Nombre | texto libre | — | Identificar al solicitante | CRM |
| Email | email | — | Contacto principal | CRM, email automático |
| Empresa/escuela | texto libre | — | Segmentación por tipo de organización | CRM, etiquetado |
| Rol | selección única | Montaje, Ayudante de montaje, DIT/data wrangler, Productor/a, Coordinación de producción, Escuela/docente, Estudiante, Postproducción, Otro | Entender perfil | CRM, segmentación, métricas |
| País/ciudad | texto libre | — | Distribución geográfica | Métricas, husos horarios para contacto |
| Software de montaje | selección única | DaVinci Resolve, Avid Media Composer, Adobe Premiere Pro, Final Cut Pro, Otro, No lo sé todavía | Identificar ecosistema del usuario | Priorización, roadmap de integraciones |
| ¿Trabajáis con audio separado? | selección única | Sí, habitualmente; A veces; No; No lo sé | Factor crítico para utilidad del matching | Priorización |
| ¿Trabajáis con timecode? | selección única | Sí; A veces; No; No lo sé | Factor crítico para precisión del matching | Priorización |
| Principal problema actual al preparar material | texto libre (máx 300 caracteres) | — | Entender caso de uso real | Métricas, feedback cualitativo |
| Permiso de contacto | checkbox obligatorio | — | Consentimiento RGPD/LOPD legal | CRM, registro de consentimiento |
| Aceptación de privacidad | checkbox obligatorio | — | Consentimiento tratamiento de datos | CRM, registro de consentimiento |

### Campos opcionales

| Campo | Tipo | Opciones | Motivo | Uso futuro |
|---|---|---|---|---|
| Volumen aproximado de material por proyecto | selección única | Menos de 50 GB; 50-200 GB; 200 GB-1 TB; Más de 1 TB; Variable/no lo sé | Dimensionar escala de trabajo | Priorización |
| Interés en beta de pago | selección única | Sí, si resuelve mi problema; Quizá, quiero verlo antes; Solo beta gratuita; No lo sé | Medir disposición económica | Segmentación, pricing |
| ¿Aceptarías una demo de 10-15 minutos? | selección única | Sí; Quizá; No; No lo sé | Identificar candidatos listos para contacto activo | Priorización, calendarización |
| Comentarios adicionales | texto libre | — | Recoger contexto no cubierto | Feedback cualitativo |

## 6. Opciones recomendadas

### Rol

- Montaje
- Ayudante de montaje
- DIT/data wrangler
- Productor/a
- Coordinación de producción
- Escuela/docente
- Estudiante
- Postproducción
- Otro

### Software de montaje

- DaVinci Resolve
- Avid Media Composer
- Adobe Premiere Pro
- Final Cut Pro
- Otro
- No lo sé todavía

### Audio separado

- Sí, habitualmente
- A veces
- No
- No lo sé

### Timecode

- Sí
- A veces
- No
- No lo sé

### Volumen aproximado de material por proyecto

- Menos de 50 GB
- 50-200 GB
- 200 GB-1 TB
- Más de 1 TB
- Variable / no lo sé

### Interés en beta de pago

- Sí, si resuelve mi problema
- Quizá, quiero verlo antes
- Solo beta gratuita
- No lo sé

### ¿Aceptarías una demo de 10-15 minutos?

- Sí
- Quizá
- No
- No lo sé

## 7. Texto introductorio del formulario

**Versión final recomendada:**

> Completa el formulario para solicitar acceso a la beta privada de AILink Sync Dialogue.
>
> La beta tiene plazas limitadas y está pensada para probar la herramienta con casos controlados. Completar el formulario no garantiza acceso inmediato, pero nos ayuda a entender tu perfil y priorizar contactos.
>
> No pedimos material audiovisual. Solo información sobre tu flujo de trabajo.

## 8. Microcopy por campo

**Email:**
> Te escribiremos aquí si tu perfil encaja con la beta actual.

**Principal problema actual:**
> Descríbelo en pocas líneas. Nos ayuda a entender tu caso real.

**Audio separado:**
> ¿El audio se graba en un dispositivo distinto a la cámara?

**Timecode:**
> ¿Las cámaras y grabadoras registran timecode en el metraje?

**Volumen de material:**
> Aproximación. No hace falta ser exacto.

**Interés en beta de pago:**
> La beta tiene un precio reducido. Esta información nos ayuda a ajustar la oferta.

**Permiso de contacto:**
> Marca esta casilla para que podamos escribirte sobre la beta.

**Aceptación de privacidad:**
> Consulta nuestra política de privacidad (enlace futuro).

## 9. Mensaje de consentimiento

### Permiso de contacto

> Autorizo a AILinkCinema a contactarme sobre la beta privada de AILink Sync Dialogue.

Campo obligatorio. Checkbox individual.

### Aceptación de privacidad

> He leído y acepto la política de privacidad de AILinkCinema.

Campo obligatorio. Checkbox individual. **Nota:** antes de publicar el formulario, debe redactarse una política de privacidad legalmente válida y vincularla aquí. Este texto es provisional y debe validarse con asesoría legal antes de su uso en producción.

## 10. Mensaje de éxito tras enviar

### Variante A — Formal/profesional

> Gracias por solicitar acceso a la beta privada de AILink Sync Dialogue.
>
> Hemos recibido tu solicitud. Revisaremos los perfiles periódicamente y te contactaremos si tu caso encaja con la fase actual de la beta.
>
> Completar el formulario no garantiza acceso inmediato. La beta es limitada y controlada por ahora.
>
> No subas material audiovisual todavía. Si avanzamos, te indicaremos los pasos siguientes.
>
> Mientras tanto, puedes seguirnos para novedades sobre la herramienta.

### Variante B — Cercana

> Recibida tu solicitud para la beta de AILink Sync Dialogue. Gracias.
>
> Revisamos los perfiles semanalmente. Si tu caso encaja con la beta actual, te escribiremos para coordinar una demo corta o una prueba controlada.
>
> La beta es limitada, así que paciencia si no recibes respuesta inmediata. No significa que no te hayamos leído.

### Variante C — Breve

> Solicitud recibida. Gracias por tu interés en AILink Sync Dialogue.
>
> Revisaremos tu perfil y te contactaremos si encaja con la beta actual. No garantizamos acceso inmediato.
>
> No envíes material audiovisual ahora. Te indicaremos los próximos pasos si tu solicitud avanza.

**Recomendación:** usar variante A (formal) como principal. Reservar variante C para contextos móviles o enlaces rápidos.

## 11. Mensaje de error

### Email inválido

> El email introducido no parece válido. Revísalo e inténtalo de nuevo.

### Campo obligatorio vacío

> El campo [nombre del campo] es obligatorio. Complétalo para continuar.

### Consentimiento no marcado

> Es necesario marcar el permiso de contacto y aceptar la política de privacidad para enviar el formulario.

### Error temporal

> Ha ocurrido un error temporal al enviar el formulario. Inténtalo de nuevo en unos minutos. Si el problema persiste, escríbenos a [email de contacto futuro].

### Duplicado

> Ya recibimos una solicitud con este email. Si no te hemos contactado todavía, revisaremos tu perfil próximamente. No es necesario que la envíes de nuevo.

## 12. Email automático de confirmación

### Asunto

> AILink Sync Dialogue — Confirmación de solicitud beta

### Cuerpo

Hola [Nombre],

Gracias por solicitar acceso a la beta privada de **AILink Sync Dialogue**, la herramienta local de AILinkCinema para preparar material de vídeo y audio antes de montaje.

Hemos recibido tu solicitud correctamente. Estos son los datos que nos has facilitado:

- **Empresa/escuela:** [empresa]
- **Rol:** [rol]
- **Software de montaje:** [software]
- **Audio separado:** [respuesta]
- **Timecode:** [respuesta]

**¿Qué pasa ahora?**

Revisamos los perfiles periódicamente. Si tu caso encaja con la fase actual de la beta, te contactaremos para una demo corta o una prueba controlada.

Completar este formulario no garantiza acceso inmediato. La beta tiene plazas limitadas y está pensada para casos controlados donde la herramienta pueda validarse con utilidad real.

**Mientras tanto:**

- No subas material audiovisual a ningún sitio. No lo pedimos por formulario.
- Si tienes dudas, puedes responder a este email (si está habilitado) o escribirnos a [email de contacto futuro].

Gracias de nuevo por tu interés.

Un saludo,
Equipo AILinkCinema

### CTA suave

> Si quieres contarnos más sobre tu proyecto, responde a este email.

## 13. Email manual para candidato seleccionado

### Asunto

> AILink Sync Dialogue — Demo beta: [nombre del candidato]

### Cuerpo

Hola [Nombre],

Hemos revisado tu solicitud para la beta de **AILink Sync Dialogue** y creemos que tu perfil encaja bien con la fase actual de pruebas.

Trabajas con [software de montaje], [respuesta audio separado] y [respuesta timecode], y nos parece un caso interesante para validar la herramienta.

**¿Qué proponemos?**

Una demo de 10-15 minutos por videollamada donde te enseñamos el estado actual del prototipo y vemos si encaja con tu flujo real. Sin compromiso.

**¿Qué necesitamos de ti?**

- Cuéntanos brevemente qué tipo de proyectos tienes ahora.
- No hace falta que subas material. Podemos trabajar con una carpeta de prueba o con un ejemplo controlado que te facilitaremos.

Si te interesa, responde a este email con algunos horarios disponibles en los próximos días.

Un saludo,
[Tu nombre]
AILinkCinema

## 14. Email manual para candidato no prioritario ahora

### Asunto

> AILink Sync Dialogue — Gracias por tu interés

### Cuerpo

Hola [Nombre],

Gracias por solicitar acceso a la beta privada de **AILink Sync Dialogue**.

Hemos recibido muchas solicitudes y, por ahora, estamos priorizando perfiles que trabajan activamente con audio separado y timecode, y que pueden probar la herramienta con casos controlados a corto plazo.

Tu perfil no encaja con la fase actual de la beta, pero te mantendremos en nuestra lista para futuras rondas.

Si en los próximos meses tu situación cambia o empiezas a trabajar con material que encaje mejor con la herramienta, no dudes en volver a escribirnos.

Gracias por tu comprensión y por tu interés en AILinkCinema.

Un saludo,
Equipo AILinkCinema

## 15. Criterios de selección de beta testers

### Clasificación por prioridad

#### Alta prioridad

- Trabaja con audio separado habitualmente.
- Usa timecode en sus proyectos.
- Equipo de montaje o postproducción activo.
- Escuela o productora con casos reales para probar.
- Acepta una demo de 10-15 minutos.
- Interesado en beta de pago (si resuelve su problema).
- Ha descrito un problema concreto al preparar material.

#### Media prioridad

- Estudiante o docente con caso didáctico claro.
- Productora pequeña sin flujo definido pero con interés genuino.
- Interés exploratorio pero sin caso concreto ahora.
- Audio separado "a veces" o timecode "a veces".

#### Baja prioridad

- Busca edición automática completa (la herramienta no hace eso).
- Necesita integraciones con Avid/DaVinci/Premiere que aún no existen.
- No trabaja con vídeo ni audio separado.
- No acepta contacto ni demo.
- Solo interés en beta gratuita.
- No marca permiso de contacto ni aceptación de privacidad.

### Asignación de plazas

- La beta comienza con un número limitado de plazas (por definir según capacidad operativa).
- Priorizar alta prioridad primero.
- Reservar un cupo para escuelas/docentes aunque sean media prioridad.
- Si quedan plazas, abrir a media prioridad.

## 16. Flujo operativo manual inicial

Este flujo se ejecuta sin automatización (sin CRM, sin base de datos, sin backend):

1. **Usuario envía formulario.** Los datos llegan al medio que se defina en la implementación (email, Google Sheets provisional, formulario estático).
2. **Se guarda respuesta.** Almacenar en una hoja de cálculo o documento controlado (no implementar base de datos ahora).
3. **Revisión manual semanal.** El equipo revisa las solicitudes recibidas.
4. **Clasificación.** Asignar prioridad: alta, media o baja según criterios de la sección 15.
5. **Contacto por email.** Enviar email de selección o de no prioritario según clasificación.
6. **Demo corta.** Si el candidato acepta, coordinar demo de 10-15 minutos.
7. **Prueba controlada.** Si la demo valida el interés, invitar a la beta con un caso controlado.
8. **Recogida de feedback.** Durante la beta, recoger impresiones, problemas y sugerencias del tester.
9. **Seguimiento.** Actualizar estado del candidato periódicamente.

Esta fase no implementa CRM. Todo el flujo se gestiona manualmente hasta que el volumen justifique automatización.

## 17. Futuro CRM / base de datos

### Estructura futura de datos (no implementar ahora)

| Campo | Tipo | Ejemplo |
|---|---|---|
| `id` | UUID | `a1b2c3d4-...` |
| `nombre` | texto | "María García" |
| `email` | texto (único) | "maria@example.com" |
| `empresa` | texto | "Escuela de Cine" |
| `rol` | texto | "Ayudante de montaje" |
| `pais_ciudad` | texto | "México / CDMX" |
| `software` | texto | "DaVinci Resolve" |
| `audio_separado` | texto | "Sí, habitualmente" |
| `timecode` | texto | "Sí" |
| `volumen` | texto | "200 GB-1 TB" |
| `problema` | texto (máx 300) | "Llega material sin... " |
| `interes_pago` | texto | "Sí, si resuelve mi problema" |
| `acepta_demo` | texto | "Sí" |
| `comentarios` | texto | "Trabajamos con..." |
| `consentimiento_contacto` | boolean | true |
| `aceptacion_privacidad` | boolean | true |
| `estado` | texto | nuevo / contactado / demo_agendada / beta_activa / no_prioritario |
| `etiquetas` | array texto | ["escuela", "postproducción"] |
| `notas_internas` | texto | "Contactado el 12/06" |
| `fecha_contacto` | fecha | 2026-06-12 |
| `fecha_solicitud` | fecha | 2026-06-10 |
| `origen` | texto | landing / linkedin / facebook / email / whatsapp |

### Estados del lead

- `nuevo` — solicitud recibida, pendiente de revisión.
- `contactado` — se ha enviado email de selección.
- `demo_agendada` — demo coordinada.
- `beta_activa` — participando en beta.
- `no_prioritario` — no encaja ahora, en lista de espera.
- `rechazado` — no cumple requisitos.

### Etiquetas recomendadas

- escuela
- productora
- postproducción
- montaje
- DIT
- independiente
- beta_pago
- solo_gratuita

No implementar modelo ni migración. Esta estructura es orientativa para cuando se desarrolle el CRM.

## 18. Métricas de captación

No implementar analytics ni dashboard ahora. Métricas para seguimiento manual:

- Número de formularios recibidos.
- Tasa de conversión landing → formulario estimada (sobre visitas futuras).
- Porcentaje de solicitantes que trabajan con audio separado.
- Porcentaje de solicitantes que trabajan con timecode.
- Roles más frecuentes.
- Software de montaje más usado.
- Interés en beta de pago (sí / quizá / solo gratuita / no lo sé).
- Demos agendadas.
- Candidatos aceptados en beta.
- Tasa de respuesta a email de confirmación.
- Tasa de candidatos que aceptan demo tras ser contactados.
- Feedback cualitativo recogido durante pruebas.

## 19. Privacidad y legal pendiente

**Importante:** este documento no sustituye un aviso legal ni una política de privacidad formal.

Antes de publicar el formulario, es necesario preparar:

- **Aviso legal** de la landing y del servicio.
- **Política de privacidad** conforme a RGPD (UE) y LOPD (España) / legislación aplicable según país del usuario.
- **Condiciones de la beta privada** (derechos y obligaciones de ambas partes, confidencialidad, límite de responsabilidad, duración, etc.).

Recomendaciones mientras no exista documento legal definitivo:

- No pedir más datos de los necesarios (este spec ya limita al mínimo).
- No pedir material audiovisual por formulario.
- Conservar el consentimiento de contacto explícito e individual.
- Informar al usuario de que los datos se tratarán conforme a la política de privacidad (aunque sea provisional).
- No compartir los datos del formulario con terceros.
- Eliminar solicitudes si el usuario lo solicita (derecho de supresión).

Consultar con asesoría legal antes del lanzamiento de la landing.

## 20. Copy final listo para implementar

### Título del bloque formulario

> Solicitar acceso beta

### Subtítulo

> Completa el formulario para solicitar acceso a la beta privada de AILink Sync Dialogue. La beta tiene plazas limitadas y está pensada para probar la herramienta con casos controlados. Completar el formulario no garantiza acceso inmediato.

### Labels definitivos

- Nombre *
- Email *
- Empresa / escuela *
- Rol *
- País / ciudad *
- Software de montaje *
- ¿Trabajáis con audio separado? *
- ¿Trabajáis con timecode? *
- Volumen aproximado de material por proyecto
- Principal problema actual al preparar material *
- Interés en beta de pago
- ¿Aceptarías una demo de 10-15 minutos?
- Comentarios adicionales
- Permiso de contacto *
- Aceptación de privacidad *

(*) Campo obligatorio

### Placeholders recomendados

- **Nombre:** "Tu nombre"
- **Email:** "tu@email.com"
- **Empresa / escuela:** "Nombre de tu organización"
- **Rol:** (selector, sin placeholder)
- **País / ciudad:** "País y ciudad"
- **Software de montaje:** (selector, sin placeholder)
- **Audio separado:** (selector, sin placeholder)
- **Timecode:** (selector, sin placeholder)
- **Volumen:** (selector, sin placeholder)
- **Principal problema:** "Describe brevemente tu principal dificultad al preparar material de rodaje"
- **Interés en beta de pago:** (selector, sin placeholder)
- **Demo:** (selector, sin placeholder)
- **Comentarios:** "Cualquier cosa que quieras añadir"

### Textos de ayuda

- **Email:** "Te escribiremos aquí si tu perfil encaja con la beta actual."
- **Audio separado:** "¿El audio se graba en un dispositivo distinto a la cámara?"
- **Timecode:** "¿Las cámaras y grabadoras registran timecode en el metraje?"
- **Volumen:** "Aproximación. No hace falta ser exacto."
- **Problema:** "Máximo 300 caracteres."
- **Beta de pago:** "La beta tiene un precio reducido. Esta información nos ayuda a ajustar la oferta."

### Textos de consentimiento

**Permiso de contacto:**
> Autorizo a AILinkCinema a contactarme sobre la beta privada de AILink Sync Dialogue.

**Aceptación de privacidad:**
> He leído y acepto la política de privacidad de AILinkCinema. (Texto provisional — debe vincularse a la política legal definitiva antes de publicar.)

### Mensaje de éxito

> Gracias por solicitar acceso a la beta privada de AILink Sync Dialogue.
>
> Hemos recibido tu solicitud. Revisaremos los perfiles periódicamente y te contactaremos si tu caso encaja con la fase actual de la beta.
>
> Completar el formulario no garantiza acceso inmediato. La beta es limitada y controlada por ahora.
>
> No subas material audiovisual todavía. Si avanzamos, te indicaremos los pasos siguientes.
>
> Mientras tanto, puedes seguirnos para novedades sobre la herramienta.

### Email de confirmación

**Asunto:**
> AILink Sync Dialogue — Confirmación de solicitud beta

**Cuerpo:**

Hola [Nombre],

Gracias por solicitar acceso a la beta privada de **AILink Sync Dialogue**, la herramienta local de AILinkCinema para preparar material de vídeo y audio antes de montaje.

Hemos recibido tu solicitud correctamente.

**¿Qué pasa ahora?**

Revisamos los perfiles periódicamente. Si tu caso encaja con la fase actual de la beta, te contactaremos para una demo corta o una prueba controlada.

Completar este formulario no garantiza acceso inmediato. La beta tiene plazas limitadas y está pensada para casos controlados donde la herramienta pueda validarse con utilidad real.

**Mientras tanto:**

- No subas material audiovisual a ningún sitio.
- Si tienes dudas, puedes escribirnos a [email de contacto futuro].

Gracias de nuevo por tu interés.

Un saludo,
Equipo AILinkCinema

## 21. Criterios de aceptación

Este documento se considera aceptado si:

- Está en español correcto, con acentos y tildes cuidados.
- No implementa código.
- No modifica frontend ni backend existentes.
- No pide material sensible (vídeo, audio, enlaces a proyectos).
- No promete acceso automático a la beta.
- Distingue claramente entre prototipo, beta y futuro.
- Define campos, tipos, obligatoriedad, opciones y motivos.
- Define textos listos para implementar (labels, placeholders, ayuda, consentimiento, éxito, error).
- Incluye criterios de selección de beta testers.
- Incluye flujo operativo manual.
- Conecta correctamente AILink Sync Dialogue con AILinkCinema.
- No vende la herramienta como CID.
- Incluye advertencia clara sobre legal pendiente y necesidad de asesoría.
