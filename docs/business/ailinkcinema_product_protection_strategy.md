# AILinkCinema / CID — Product Protection Strategy

## 1. Principio general

No existe una forma 100% infalible de impedir que copien un software si se entrega completo a terceros.

El objetivo de AILinkCinema/CID debe ser que copiar el sistema sea difícil técnicamente, detectable mediante trazabilidad, arriesgado legalmente y poco útil comercialmente sin soporte, actualizaciones, datos, licencias y know-how.

AILinkCinema no debe venderse como una carpeta instalable con código fuente. Debe venderse como plataforma, servicio profesional o appliance licenciado.

---

## 2. Activos protegibles

AILinkCinema/CID debe proteger especialmente:

- código fuente
- arquitectura técnica
- prompts internos
- workflows n8n
- flows Flowise
- workflows ComfyUI
- base vectorial y memoria RAG
- modelos de datos
- lógica de ranking y selección
- exportadores XML/FCPXML/EDL
- conectores DaVinci Resolve, Avid Media Composer y Adobe Premiere Pro
- documentación interna
- textos comerciales
- datasets, plantillas y know-how

---

## 3. Qué no entregar nunca

No entregar al cliente:

- código fuente
- prompts internos
- workflows n8n
- flows Flowise
- workflows ComfyUI completos
- base vectorial interna
- lógica de ranking narrativo/editorial
- sistema de licencias
- conectores internos
- documentación técnica interna
- claves API o secretos
- configuración sensible

---

## 4. Qué puede recibir el cliente

El cliente puede recibir:

- acceso web
- ejecutable limitado si aplica
- panel de búsqueda
- panel de proyecto
- manual de usuario
- exports controlados
- licencia de uso
- resultados procesados
- documentación funcional no interna

---

## 5. Modelos comerciales seguros

### Servicio por proyecto

AILinkCinema procesa el material y entrega resultados. No se entrega software.

### SaaS

El cliente accede mediante usuario y contraseña. No recibe código fuente.

### Appliance local licenciado

Servidor local o mini-servidor instalado en productora. El material no sale de la empresa, pero el motor sigue protegido.

### Consultoría + herramienta

Se vende flujo de trabajo audiovisual con IA, formación, soporte y automatización.

---

## 6. Protección legal

Acciones recomendadas:

1. Registrar software en el Registro de Propiedad Intelectual.
2. Registrar marca en OEPM/EUIPO.
3. Guardar commits, tags, releases y changelog.
4. Generar hash SHA256 de releases importantes.
5. Preparar documentación técnica fechada.
6. Mantener repositorios privados.

---

## 7. Protección contractual

Documentos mínimos:

- NDA
- contrato de piloto
- contrato de licencia de uso
- condiciones de servicio
- cesión de derechos para colaboradores
- política de tratamiento de datos audiovisuales

Cláusulas clave:

- prohibición de copia
- prohibición de ingeniería inversa
- prohibición de sublicencia
- prohibición de extracción de prompts, workflows o bases de datos
- prohibición de crear producto competidor usando información de la demo
- revocación de acceso por incumplimiento
- auditoría de uso mediante logs

---

## 8. Protección técnica

Medidas recomendadas:

- no distribuir `.py`
- motor protegido por API
- licencias por usuario, proyecto o máquina
- logs de uso
- builds únicos por cliente
- watermark invisible en exports
- cifrado de configuración sensible
- secretos fuera del cliente
- repositorio privado
- permisos por rol
- CI/CD controlado

---

## 9. Arquitectura recomendada

Cliente / productora → interfaz web o cliente ligero → API controlada → motor protegido AILinkCinema/CID → base de datos protegida → Qdrant / pgvector / memoria RAG → exports controlados.

---

## 10. Editorial Intelligence & NLE Bridge

Este módulo debe ser vendible por separado y también estar incluido dentro de CID Suite.

Debe proteger especialmente:

- ingesta audiovisual
- transcripción con timecode
- diarización y personajes
- búsqueda semántica
- ranking narrativo
- generación de selects
- paper edit
- markers
- timelines
- exportadores XML/FCPXML/EDL
- conectores DaVinci Resolve
- conectores Avid Media Composer
- conectores Adobe Premiere Pro

No se debe entregar la lógica interna de búsqueda, ranking, exportación ni conectores.

---

## 11. Checklist para demos con productoras

Antes de demo:

- NDA firmado
- usuario individual
- acceso temporal
- material de prueba o autorizado
- sin código fuente
- sin exports completos si es demo temprana
- marca de agua en resultados
- logs activos
- permisos limitados

---

## 12. Checklist inmediata

1. Confirmar nombres comerciales.
2. Buscar marcas en OEPM.
3. Preparar dossier técnico.
4. Generar release/tag estable.
5. Preparar NDA.
6. Preparar contrato piloto.
7. Preparar licencia de uso.
8. Definir modelo SaaS/appliance.
9. Definir módulos vendibles por separado.
10. Definir qué incluye CID Suite.

---

## 13. Decisión recomendada para AILinkCinema

AILinkCinema no debe venderse como una carpeta instalable.

La estrategia recomendada es:

- vender servicio profesional al inicio
- evolucionar a plataforma SaaS
- ofrecer appliance local licenciado para productoras sensibles
- proteger CID Suite como paquete completo
- vender módulos independientes
- proteger especialmente Editorial Intelligence & NLE Bridge
