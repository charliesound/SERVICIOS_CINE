# Directiva Técnica: Autenticación y Roles Mínimos Viables (RBAC)

## 1. Objetivo
Implementar un sistema de autenticación centralizada y un modelo de Autorización Basado en Roles (RBAC) que permita transformar la aplicación actual en una plataforma SaaS segura y operable. Esto garantizará que las operaciones de producción críticas sean accedidas exclusivamente por perfiles autorizados con sus respectivos privilegios.

## 2. Problema que Resuelve
Hasta la fecha, características sensibles como ejecuciones (jobs costosos o flujos de IA), gestión de colecciones, revisiones, manejo de integraciones externas (webhooks) y exportación no delimitan la autoridad sobre quién puede leer o modificar el estado de estas entidades. Esto representa un riesgo severo en un entorno de producción donde un usuario raso podría alterar el webhook de n8n, detener exportaciones o borrar el trabajo de revisión consolidado por otro equipo. La implementación sella las rutas, unifica quién y dónde entra al sistema bajo control total.

## 3. Modelo Mínimo de Usuario Recomendado
Se delega la gestión primaria a Supabase Auth (`auth.users`), extendiéndola con una tabla pública (`public.profiles` o `public.users`) referenciada y sincronizada por trigger.

**Tabla: `public.profiles`**
- `id` (UUID, PK, FK a `auth.users.id` con `ON DELETE CASCADE`)
- `email` (String)
- `full_name` (String)
- `avatar_url` (String)
- `role` (Enum/String - default `'viewer'`)
- `created_at` / `updated_at` (Timestamps)

*(Las credenciales completas de autorización OAuth deben permanecer invisibles al cliente gracias al manejo de Supabase)*.

## 4. Estrategia Recomendada de Autenticación
Basado en el SaaS Tech Stack, se descartan métodos complejos a favor de:
- **Proveedor:** Supabase Auth usando **OAuth 2.0 con Google** (`signInWithOAuth`).
- **Manejo de Sesión:** Cookies seguras administradas vía un SSR Client (Server-Side Rendering Auth Helpers de Supabase para Next.js / App Router). Esto evita fugas comunes de tokens en LocalStorage.
- **Flujo de Seguridad:** Redirección automática desde el root (`/`) si no hay sesión hacia la pantalla de `/login`.
- **Secretos:** Llaves API de Supabase public/anon keys en el enviroment (`.env.local`), con Service Role keys puramente aisladas y nunca expuestas en el frontend.

## 5. Roles Mínimos y Permisos Orientativos (RBAC)
Para dar balance entre flexibilidad y estructura de operación interna SaaS:

1. **Admin / SysAdmin (`admin`):**
   - Acceso irrestricto.
   - Gestiona Reglas de Alertas, configuración de Webhooks n8n, ajustes Core del pipeline y puede asignar roles a otros perfiles.
2. **Editor / Productor (`editor`):**
   - Perfil de gestión de operaciones base.
   - Crea/Edita ejecuciones, colecciones, flujos de revisión.
   - Detiene o relanza jobs de rendering, lanza procesos de exportación de la plataforma de Cine AI.
3. **Revisor / Visualizador (`viewer` / `reviewer`):**
   - Accesos puramente de lectura (Read-Only). 
   - Pueden visualizar resultados generados, realizar comentarios sobre estados de revisión ("Aprobar/Rechazar" según diseño de estados en el pipeline, mas no alterar configuración bruta).

## 6. Rutas que Deben Protegerse Primero (Prioridad Máxima)
A nivel de middleware de Next.js (protegiendo en borde), las rutas son:
- `/settings/*` o `/config/*`: Protegido íntegramente de cara al rol `admin` (configuraciones de sistema, webhooks, base de datos).
- `/jobs/*` o `/executions/*`: Bloquear mutaciones (POST/PUT/DELETE) a editores/administradores (para ahorrar consumo y costes imprevistos).
- `/api/auth/*`: Endpoints internos.
- `/api/webhooks/*`: Asegurarse que reciban y validen _API Keys_ o firmas del N8N de forma agnóstica a la sesión de usuario final.

## 7. Integración Recomendada en UI
Siguiendo **Shadcn UI** y **Tailwind CSS**:
- **Vista de Login Centralizada:** Una página limpia, minimalista (`/login`) mostrando únicamente los logos SaaS y el botón "Continuar con Google".
- **Gestión de Sesión:** Menú de usuario (`DropdownMenu` de Shadcn UI) en la AppBar o Navbar flotante de la plataforma con: Perfil, Rol Activo y "Cerrar Sesión".
- **Feedback UI condicional:** Botones y características peligrosas (ej: "Eliminar colección", "Modificar Webhook") son renderizados u ocultados en React directamente leyendo si el `user.role === 'admin'`.

## 8. Criterios de Aceptación
1. Ingreso de un usuario bloqueado exitosamente si carece de cuenta Google corporativa/permitida.
2. Creación e instanciación automática del perfil de usuario en `public.profiles` del lado de la base de datos tras loguearse la primera vez.
3. Rutas administrativas expulsan y redireccionan roles base de `editor` a un 404 o `/dashboard` mediante el Contexto o Middleware.
4. RLS (Row Level Security) activado en Supabase al menos en tablas críticas para asegurar que incluso llamadas manipuladas prevengan robo o mal uso de datos sin permisos.

## 9. Riesgos
- **Desincronización de Sesiones Next.js SSG / CSR:** Error común en el stack de Next/Supabase, provocando caídas visuales si no usamos cookies robustamente en el `middleware.ts`.
  *(Mitigación: Apegarse estrictamente al paquete oficial `@supabase/ssr` en todas las capas del renderizado).*
- **Errores de Sync entre `auth.users` y `public.profiles`:** Que el trigger falle y un usuario válido por Google quede sin rol en el modelo relacional.
  *(Mitigación: Agregar manejo estricto de excepciones SQL en los Hooks de Supabase. Default role always assigned).*

## 10. Siguiente Evolución Recomendada
- **Soporte Multi-Tenancy (Organizaciones/Workspaces):** En vez de un rol local único, los usuarios pertenecerán a un Workspace y tendrán roles puntuales de acuerdo al proyecto de la película/serie.
- **Permisos Granulares (ABAC):** Cambiar de roles monolíticos estáticos a permisos en matriz: `['can_edit_collections', 'can_trigger_n8n']` brindando más control granular de equipos grandes.
