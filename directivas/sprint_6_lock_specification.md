# Sprint 6 Locking Specification: Producer Area & Funding Matching

## 1. Objetivo del Sprint
Proporcionar al Productor Ejecutivo una visión de alto nivel sobre la salud financiera y operativa del proyecto, y facilitar el acceso a oportunidades de financiación y contacto comercial para el escalado Studio.

## 2. Alcance Exacto
### Entra:
- **Producer Control Center:** Dashboard ejecutivo con métricas de salud (Escenas aprobadas vs. Pendientes, Créditos consumidos, Ahorro estimado en Renders).
- **Funding Explorer:** Directorio filtrable de oportunidades de financiación (Incentivos fiscales, Grants, Inversores) basadas en los metadatos del proyecto.
- **Opportunity Detail:** Ficha técnica de cada ayuda con requisitos y enlace de interés.
- **Commercial Contact Flow:** Formulario de "Solicitar Demo / Contacto Studio" integrado para la conversión de clientes piloto a planes Enterprise.
- **Acceso por Rol:** Restricción de estas vistas solo a usuarios con rol `Producer` u `Owner`.

### No Entra:
- **Financial CRM:** No hay gestión de facturas, pagos o nóminas vinculadas.
- **Automated Funding Application:** El sistema no rellena formularios de subvención automáticamente.
- **Crowdfunding Platform:** No hay pasarela de pago para micro-inversores en esta versión.

## 3. Vistas Finales
1.  **Producer Dashboard:** Panel de mando con KPIs de producción y atajos a las escenas críticas.
2.  **Funding Opportunities List:** Listado de "Matching" entre el proyecto y posibles fuentes de capital.
3.  **Funding Opportunity Detail:** Información extendida sobre una ayuda específica.
4.  **Demo/Contact Hub:** Interfaz simplificada para escalar la relación comercial con AILinkCinema.

## 4. Acciones del Usuario por Vista
- **Producer Dashboard:** Ver el porcentaje de compleción del "Assembly Cut", consultar el saldo de créditos de la organización.
- **Funding List:** Filtrar por tipo de ayuda (Fiscal, Estatal, Privado), marcar oportunidades como "Interesantes".
- **Funding Detail:** Leer requisitos, descargar sumario ejecutivo del proyecto para la aplicación (S5).
- **Contact Hub:** Enviar solicitud de reunión para el plan corporativo.

## 5. Nivel de Control (MVP)
- **Analytics:** Basadas en los estados de aprobación del Sprint 5.
- **Funding:** Lista curada de al menos 10 oportunidades reales/demo de alta relevancia.
- **Contacto:** Notificación interna al equipo de AILinkCinema (No es un CRM multicanal).

## 6. Datos Demo Obligatorios
- **Incentivos Demo:** Al menos 5 incentivos fiscales cinematográficos (ej: "Tax Rebate Spain", "MGE Grant").
- **Metrics Demo:** Datos de consumo histórico para el proyecto *The Robot's Journey*.

## 7. Estados Vacíos / Placeholders
- **Empty Dashboard:** "No approved scenes yet. Complete Sprint 4 and 5 to unlock producer analytics."
- **Funding Placeholder:** Mensaje de "More opportunities unlocking as your project metadata grows."

## 8. Percepción del Producto
- **Cierre del MVP:** El usuario siente que el software no solo "hace imágenes", sino que "ayuda a financiar y gestionar el negocio".
- **Aspiracional:** El portal de financiación posiciona a AILinkCinema como un socio estratégico del productor.
- **Escalabilidad:** El flujo de contacto comercial prepara la conversión a clientes de largo plazo.

## 9. Criterios de Terminado (DoD)
- [ ] El `Producer Dashboard` muestra métricas coherentes extraídas del estado de las escenas.
- [ ] El directorio de `Funding` es navegable y permite ver detalles de oportunidad.
- [ ] El flujo de "Solicitar Demo" envía una señal de lead correcta.
- [ ] El acceso a estas áreas está protegido por roles de seguridad.
- [ ] Demo Final: "Ver el progreso del proyecto, encontrar una ayuda fiscal adecuada y solicitar una llamada para escalar la producción".

## 10. Decisiones Congeladas
1.  **Metric Aggregation:** Los datos del dashboard se actualizan en base a los cambios en el Review & Approval (S5).
2.  **Static Lead Management:** Para el MVP, la gestión de leads de financiación es informativa (links externos).
3.  **Professional Gatekeeping:** El modo 'Producer' es la puerta de entrada oficial a los servicios Enterprise.
