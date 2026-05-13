# Demo CID — Workflow n8n para captura de leads

## 1. Objetivo

Este workflow captura los leads enviados desde el formulario de la página `/demo-cid` de AILinkCinema/CID.

El frontend envía un **POST JSON** a un webhook de n8n. El workflow:

1. Recibe el payload
2. Valida los campos obligatorios
3. Si es inválido → responde `400` con los errores
4. Si es válido → guarda en Google Sheets, envía email de confirmación al lead, notifica al equipo interno y responde `200`

---

## 2. Payload esperado desde el frontend

```json
{
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "empresa": "Productora Demo",
  "rol": "productor",
  "tipoProyecto": "largometraje",
  "faseProyecto": "guion",
  "objetivoPrincipal": "pitching",
  "enlaceGuion": "https://example.com/guion.pdf",
  "mensaje": "Quiero validar un largometraje en fase de desarrollo.",
  "aceptaContacto": true,
  "_timestamp": "2026-05-13T10:00:00.000Z",
  "_source": "demo-cid-page"
}
```

Ver archivo: `docs/n8n/demo_cid_leads_payload_example.json`

Campos obligatorios desde el frontend:
- `nombre` — string no vacío
- `email` — string con formato email
- `rol` — string no vacío
- `tipoProyecto` — string no vacío
- `aceptaContacto` — debe ser `true`

---

## 3. Pasos para crear el Webhook node en n8n

### 3.1. Desde la interfaz de n8n

1. Abre tu instancia de n8n
2. Crea un nuevo workflow
3. Añade un nodo **Webhook**
4. Configura:
   - **HTTP Method**: `POST`
   - **Path**: `cid-demo`
   - **Options → Response Mode**: `Respond to Webhook node` (envía respuesta cuando termine el workflow completo, no inmediatamente)
5. Haz clic en **Listen for test event** para que n8n genere la URL de test
6. Copia la URL que aparece (ej: `https://tu-n8n.cloud/webhook/cid-demo`)

### 3.2. Importar el workflow exportado

También puedes importar directamente el archivo `docs/n8n/demo_cid_leads_workflow_export.json`:

1. En n8n, ve a **Workflows → Import from File**
2. Selecciona el archivo JSON exportado
3. Revisa los nodos y ajusta las conexiones si es necesario
4. Los nodos **Google Sheets**, **Email** y **Internal Notification** quedan placeholder; debes configurar sus credenciales

---

## 4. Cómo copiar la URL de producción del webhook

Una vez activado el workflow en n8n:

1. Abre el workflow
2. En el nodo **Webhook**, haz clic en **Production URL**
3. Se genera una URL del estilo:
   ```
   https://tu-instancia.n8n.cloud/webhook/cid-demo
   ```
4. Copia esta URL

---

## 5. Cómo ponerla en `src_frontend/.env.local`

```bash
# .env.local
VITE_DEMO_CID_WEBHOOK_URL=https://tu-instancia.n8n.cloud/webhook/cid-demo
```

El frontend usa `import.meta.env.VITE_DEMO_CID_WEBHOOK_URL` para enviar el POST.

Si la variable está vacía, el formulario muestra un mensaje informativo:
> "El servicio de envio no esta configurado. Contacta con el equipo de AILinkCinema."

---

## 6. Cómo probar con curl

```bash
export WEBHOOK_URL="https://tu-instancia.n8n.cloud/webhook/cid-demo"

bash docs/n8n/demo_cid_leads_curl_test.sh
```

O manualmente:

```bash
curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test",
    "email": "test@example.com",
    "empresa": "Test Prod",
    "rol": "director",
    "tipoProyecto": "cortometraje",
    "faseProyecto": "guion",
    "objetivoPrincipal": "analisis",
    "enlaceGuion": "https://example.com",
    "mensaje": "Test",
    "aceptaContacto": true,
    "_source": "demo-cid-page"
  }'
```

Esperado:
```json
{ "ok": true, "message": "Solicitud recibida correctamente" }
```

---

## 7. Cómo validar que el frontend recibe respuesta OK

1. Arranca el frontend: `npm run dev` dentro de `src_frontend/`
2. Abre `http://localhost:3000/demo-cid` en el navegador
3. Abre las DevTools → pestaña **Network**
4. Rellena el formulario y pulsa **Enviar solicitud**
5. Busca la petición POST a tu webhook URL
6. Verifica:
   - **Status**: `200`
   - **Response body**: `{ "ok": true, "message": "Solicitud recibida correctamente" }`
   - En la UI: desaparece el formulario y aparece el mensaje de éxito
7. Si falla:
   - En la UI aparece un banner rojo con el error
   - En la consola del navegador: `[Track] submit_demo_cid_form_error`
   - En n8n: revisa **Execution Log**

---

## 8. Cómo conectar Google Sheets

El nodo **Save Lead to Google Sheets** está preparado en el workflow exportado.

Para activarlo:

1. En n8n, abre el workflow importado
2. Haz doble clic en el nodo **Save Lead to Google Sheets**
3. En **Credential → Google Sheets OAuth2**, haz clic en **Create New**
4. Sigue el flujo de OAuth2 de Google:
   - Te redirigirá a Google para autorizar
   - Necesitas una cuenta de Google con acceso al spreadsheet
5. Configura:
   - **Google Sheet**: selecciona el spreadsheet o pega su ID
   - **Sheet Name**: `Leads`
   - **Mode**: `Append`
   - **Data Mapping Mode**: `Map each field below`
   - Mapea cada campo del lead a la columna correspondiente:

     | Columna | Valor n8n |
     |---------|-----------|
     | fecha | `{{ $json.lead.fecha }}` |
     | nombre | `{{ $json.lead.nombre }}` |
     | email | `{{ $json.lead.email }}` |
     | empresa | `{{ $json.lead.empresa }}` |
     | rol | `{{ $json.lead.rol }}` |
     | tipoProyecto | `{{ $json.lead.tipoProyecto }}` |
     | faseProyecto | `{{ $json.lead.faseProyecto }}` |
     | objetivoPrincipal | `{{ $json.lead.objetivoPrincipal }}` |
     | enlaceGuion | `{{ $json.lead.enlaceGuion }}` |
     | mensaje | `{{ $json.lead.mensaje }}` |
     | source | `{{ $json.lead.source }}` |

6. Crea el spreadsheet con las columnas en la primera fila. Puedes usar el archivo `docs/n8n/demo_cid_google_sheets_columns.csv` como referencia.

---

## 9. Cómo enviar email de confirmación

El nodo **Send Confirmation Email** está preparado en el workflow exportado.

Para activarlo:

1. Haz doble clic en el nodo
2. Configura el **Credential** de email (SMTP o servicio compatible):
   - **Email (SMTP)**: servidor SMTP, puerto, usuario, contraseña
   - O **Gmail OAuth2** si usas una cuenta de Google
3. Parámetros:
   - **From**: `noreply@ailinkcinema.com`
   - **To**: `{{ $json.lead.email }}`
   - **Subject**: `Hemos recibido tu solicitud para probar CID`
   - **Text**: (cuerpo del email)

### Plantilla del email de confirmación

```
Hemos recibido tu solicitud para probar CID

Gracias por contactar con AILinkCinema.

Hemos recibido tu solicitud para probar CID con tu proyecto
"{{ $json.lead.nombre }}" ({{ $json.lead.empresa }}).

Nuestro equipo revisará la información y te responderemos
lo antes posible para coordinar los siguientes pasos.

Mientras tanto, si tienes alguna duda puedes escribirnos a
contacto@ailinkcinema.com.

Equipo AILinkCinema
https://ailinkcinema.com
```

---

## 10. Cómo enviar aviso interno

El nodo **Notify AILinkCinema** está preparado para notificar al equipo comercial.

Para activarlo (SMTP):

1. Reutiliza el mismo credencial de email del nodo de confirmación
2. Parámetros:
   - **From**: `noreply@ailinkcinema.com`
   - **To**: `cid.jcc@gmail.com`
   - **Subject**: `Nuevo lead /demo-cid — {{ $json.lead.nombre }}`
   - **Text**:

```
Nuevo lead recibido desde /demo-cid

Nombre: {{ $json.lead.nombre }}
Email: {{ $json.lead.email }}
Empresa: {{ $json.lead.empresa }}
Rol: {{ $json.lead.rol }}
Tipo de proyecto: {{ $json.lead.tipoProyecto }}
Fase: {{ $json.lead.faseProyecto }}
Objetivo: {{ $json.lead.objetivoPrincipal }}
Enlace: {{ $json.lead.enlaceGuion }}
Mensaje: {{ $json.lead.mensaje }}

Fecha: {{ $json.lead.fecha }}
```

También puedes reemplazar el email por una notificación vía Slack, Telegram, o webhook a un CRM.

---

## 11. Recomendaciones de seguridad

| Recomendación | Detalle |
|---------------|---------|
| **HTTPS obligatorio** | n8n debe estar detrás de HTTPS. La mayoría de servicios cloud lo incluyen. |
| **Rate limiting** | Añade un nodo **Rate Limit** en n8n para evitar abuso (ej: 10 peticiones/minuto por IP). |
| **Validar en frontend también** | El frontend ya valida `required` en HTML5 y checkbox obligatorio. El Code node de validación en n8n es la segunda capa. |
| **No exponer credenciales** | Las credenciales OAuth2 y SMTP se guardan cifradas en n8n. No las incluyas en el JSON exportado. |
| **Logs de ejecución** | n8n guarda histórico de ejecuciones por defecto. Útil para debug. |
| **Honeypot field** | Para producción, añade un campo oculto en el formulario HTML (invisible para humanos) que los bots rellenan. Si llega con valor, descarta el lead en el Code node. |
| **CORS** | n8n no necesita CORS porque el frontend llama directamente al webhook desde fetch(). Sin embargo, el webhook acepta peticiones de cualquier origen por defecto. Si quieres restringir, usa los headers CORS en n8n o un proxy inverso. |
| **Webhook secret** | Opcional: configura un query param secreto en la URL del webhook (ej: `/cid-demo?secret=xxx`) para filtrar peticiones no autorizadas. |

---

## 12. Variables de entorno del frontend

| Variable | Obligatorio | Descripción |
|----------|-------------|-------------|
| `VITE_DEMO_CID_WEBHOOK_URL` | Sí (para producción) | URL completa del webhook n8n |

Ejemplo en `.env.local`:

```env
VITE_DEMO_CID_WEBHOOK_URL=https://tu-instancia.n8n.cloud/webhook/cid-demo
```

Ver archivo: `src_frontend/.env.example`
