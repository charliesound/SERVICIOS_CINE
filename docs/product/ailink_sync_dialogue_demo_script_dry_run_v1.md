# AILink Sync Dialogue — Demo Script Dry Run v1

## 1. Objetivo

Este documento define el ensayo controlado del guion de demo de AILink Sync Dialogue.

La finalidad es ensayar la demo sin grabar vídeo público, sin enseñar a terceros externos, sin prometer sincronización automática final y sin convertir todavía el estado LIMITED PASS en PASS público.

Esta fase responde directamente a:

- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.PHASE7.
- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.AUDIT.PHASE7.1.
- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.EVIDENCE.PHASE7.2.
- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.EVIDENCE.RUN.PHASE7.3.
- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.SCRIPT.REFINEMENT.PHASE7.4.

Esta fase es documental y de ensayo. No implementa código, no modifica scanner, no modifica matching, no modifica exports, no modifica reportes, no crea UI real, no crea backend, no crea frontend, no crea instalador, no crea n8n, no crea CRM, no toca PostgreSQL real, no toca Docker, no toca runtime, no toca configuración, no graba vídeo público y no modifica CID SaaS.

## 2. Estado inicial

Estado de entrada:

- LIMITED PASS.
- Guion hablado de 5 a 7 minutos preparado.
- Evidence run real registrada.
- Demo pública no recomendada todavía.
- Contacto con escuelas o productoras no recomendado todavía como demo final.
- Persona de confianza permitida solo si el ensayo interno no detecta riesgos.

Objetivo de salida:

- Mantener LIMITED PASS si el ensayo no está claro.
- Subir a PASS interno solo si el mensaje es seguro, el tiempo es controlado, las frases peligrosas no aparecen y el feedback pedido queda claro.
- No subir a PASS público en esta fase.

## 3. Público del dry run

Permitido:

- Ensayo individual.
- Ensayo interno sin público.
- Ensayo con una persona de confianza si el primer ensayo individual pasa.
- Revisión por colaborador técnico cercano.

No permitido:

- Escuelas de cine.
- Productoras externas.
- Leads fríos.
- LinkedIn.
- Facebook.
- YouTube.
- Vídeo promocional público.
- Demo comercial con precio cerrado.

## 4. Material permitido durante el ensayo

Permitido:

- Guion de Phase7.4.
- Metadata demo controlada.
- Report HTML controlado.
- CSV de media files.
- CSV de match suggestions.
- Evidence run summary.
- Checklist de límites.
- Plantilla de feedback.

No permitido:

- Material audiovisual de cliente.
- Datos personales reales.
- Credenciales.
- .env.
- Paneles de administración.
- n8n.
- CRM.
- CID SaaS.
- Docker.
- Configuración del sistema.
- Bases de datos reales.
- Carpetas privadas no relacionadas.

## 5. Preparación previa

Antes de ensayar:

1. Confirmar que el repo está limpio.
2. Tener visible el guion de Phase7.4.
3. Tener visible el reporte HTML controlado o una captura controlada.
4. Tener visible una tabla de match suggestions.
5. Tener visible la frase de estado LIMITED PASS.
6. Tener visible la explicación de 0 match suggestions en e2e dummy.
7. Tener visible la lista de frases prohibidas.
8. Tener visible la lista de frases permitidas.
9. Tener visible la plantilla de feedback.
10. Cerrar cualquier ventana con secretos, rutas sensibles o material real.

## 6. Estructura del ensayo cronometrado

El ensayo debe durar entre 5 y 7 minutos.

Bloques esperados:

- 0:00-0:40 Apertura.
- 0:40-1:20 Problema.
- 1:20-2:10 Qué hace hoy.
- 2:10-3:10 Evidence run real.
- 3:10-4:20 Lectura del reporte.
- 4:20-5:10 Explicación del e2e dummy.
- 5:10-6:00 Límites honestos.
- 6:00-6:45 Qué feedback pedir.
- 6:45-7:00 Cierre.

Regla de tiempo:

- Menos de 5 minutos: falta explicación o contexto.
- Entre 5 y 7 minutos: rango correcto.
- Más de 7 minutos: hay exceso de detalle técnico o comercial.

## 7. Checklist durante el ensayo

Durante el ensayo confirmar:

- Se dice LIMITED PASS.
- Se dice beta controlada.
- Se dice local-first.
- Se dice outputs revisables.
- Se explica que no es sincronización final.
- Se explica que el e2e dummy puede dar 0 match suggestions.
- Se explica que 0 match suggestions en dummy no es fallo.
- Se pide feedback concreto.
- Se evita vender.
- Se evita precio cerrado.
- Se evita prometer integración con editores.
- Se evita prometer waveform sync.
- Se evita prometer transcripción.
- Se evita prometer claqueta visual.
- Se evita abrir CID SaaS.
- Se evita abrir n8n.
- Se evita abrir CRM.

## 8. Frases peligrosas que obligan a repetir el ensayo

Si aparece cualquiera de estas frases, el ensayo no pasa:

- Esto sincroniza automáticamente todo.
- Ya está listo para productoras.
- Ya lo podemos vender públicamente.
- Sustituye al montador.
- Funciona con cualquier cámara.
- Funciona con cualquier grabador.
- Ya detecta claqueta visual.
- Ya transcribe diálogos.
- Ya se integra con DaVinci.
- Ya se integra con Avid.
- Ya se integra con Premiere.
- Puedes usar material sensible sin problema.
- Esto ya es CID terminado.
- Esto ya está para LinkedIn como demo final.

## 9. Frases obligatorias

El ensayo debe incluir estas frases o equivalentes:

- AILink Sync Dialogue está en LIMITED PASS.
- Esta demo es beta controlada.
- No es sincronización automática final.
- La demo usa material controlado.
- La metadata demo enseña matching sugerido.
- La e2e dummy enseña flujo local con outputs.
- El resultado 0 match suggestions en dummy no es fallo.
- El reporte ayuda a revisar antes de montaje.
- La decisión final sigue siendo humana.
- El objetivo de hoy es feedback, no venta.

## 10. Matriz de evaluación del ensayo

### PASS interno

Requisitos:

- Duración entre 5 y 7 minutos.
- Ninguna frase peligrosa.
- Estado LIMITED PASS explicado.
- 0 match suggestions del dummy explicado.
- Límites honestos explicados.
- Feedback pedido con claridad.
- No se abre material sensible.
- No se promete sincronización final.
- No se promete integración con editores.
- No se vende precio cerrado.

Resultado:

- Puede enseñarse a una persona de confianza.
- No puede enseñarse todavía como demo pública.

### LIMITED PASS mantenido

Causas:

- La demo se entiende, pero dura demasiado.
- La demo se entiende, pero falta claridad en límites.
- La explicación de 0 matches no es suficientemente clara.
- Se pide feedback, pero de forma débil.
- Aparecen dudas sobre qué enseñar primero.

Resultado:

- Repetir ensayo.
- Ajustar guion.
- No enseñar todavía a persona de confianza.

### FAIL

Causas:

- Se promete sincronización automática final.
- Se confunde beta con producto terminado.
- Se abre material sensible.
- Se abren configuraciones o secretos.
- Se intenta vender precio cerrado.
- Se presenta como demo pública.
- Se omite el estado LIMITED PASS.
- Se omite el problema de 0 match suggestions en dummy.

Resultado:

- No enseñar.
- Volver a Phase7.4 o ajustar guion.

## 11. Hoja de registro del dry run

Plantilla:

- Fecha:
- Persona que ensaya:
- Duración total:
- ¿Se dijo LIMITED PASS?: sí/no.
- ¿Se dijo beta controlada?: sí/no.
- ¿Se explicó local-first?: sí/no.
- ¿Se explicó 0 match suggestions en dummy?: sí/no.
- ¿Se evitaron frases peligrosas?: sí/no.
- ¿Se pidieron preguntas concretas?: sí/no.
- ¿Se abrió material sensible?: sí/no.
- ¿Se prometió sincronización final?: sí/no.
- Resultado: PASS interno / LIMITED PASS mantenido / FAIL.
- Ajustes necesarios:
- Siguiente acción:

## 12. Orden de pantalla recomendado

Orden recomendado:

1. Guion o notas.
2. Report HTML controlado.
3. Tabla match suggestions.
4. Tabla media files.
5. Resumen evidence run.
6. Plantilla de feedback.

Orden no recomendado:

1. JSON como primera pantalla.
2. Terminal como primera pantalla.
3. Código fuente como primera pantalla.
4. CID SaaS.
5. n8n.
6. CRM.
7. Configuración.
8. Material real de cliente.

## 13. Preguntas de autocontrol después del ensayo

Preguntas:

1. ¿La demo se entiende sin explicar código?
2. ¿El valor para montaje queda claro?
3. ¿La demo evita vender sincronización final?
4. ¿La explicación de 0 matches queda natural?
5. ¿El interlocutor entiende qué feedback se busca?
6. ¿El reporte se puede leer en menos de dos minutos?
7. ¿Se nota demasiado técnica?
8. ¿Falta una pantalla visual más clara?
9. ¿Hay alguna frase que suene a promesa comercial?
10. ¿Está lista para una persona de confianza?

## 14. Criterio para pasar a persona de confianza

Puede pasar a persona de confianza si:

- El ensayo individual obtiene PASS interno.
- La duración queda entre 5 y 7 minutos.
- No se detectan frases peligrosas.
- No se usan datos reales.
- No se abre nada sensible.
- El cierre pide feedback, no venta.
- Se acepta explícitamente que no es demo pública.

No puede pasar si:

- Sigue en LIMITED PASS mantenido.
- Hay frases peligrosas.
- El mensaje se alarga por encima de 7 minutos.
- El dummy e2e genera confusión.
- Se intenta vender precio o acceso.
- Se mezcla con CID SaaS.

## 15. Siguiente fase recomendada

Si el dry run pasa:

- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.TRUSTED.PERSON.FEEDBACK.PHASE7.6

Objetivo:

- Enseñar la demo a una persona de confianza.
- Registrar feedback real.
- Decidir si se mantiene LIMITED PASS o pasa a PASS interno validado.

Si el dry run no pasa:

- Repetir Phase7.5 tras ajustar guion.
- No añadir funcionalidad nueva todavía.

## 16. Resumen ejecutivo

Phase7.5 no busca vender, grabar ni publicar.

Busca ensayar la demo con control de tiempo, lenguaje y riesgos.

El resultado máximo de esta fase es PASS interno.

El resultado no puede ser PASS público.

La prioridad es proteger credibilidad, privacidad y claridad comercial antes de enseñar AILink Sync Dialogue fuera del círculo de confianza.
