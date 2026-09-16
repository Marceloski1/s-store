# 007 · Autenticación y roles del panel

- **Estado:** Diferida (la UI actual es solo para pruebas, sin autenticación por decisión explícita)
- **Prioridad:** P2 — bloqueante para [004](../004-production-readiness/spec.md)

## Contexto

Todos los endpoints de escritura (`POST`, `PUT`, `DELETE`) y la UI de gestión son públicos. Es aceptable en local, pero no en producción.

## Historias de usuario

1. **Como administrador** quiero iniciar sesión para gestionar el catálogo.
2. **Como administrador** quiero invitar a editores que puedan gestionar productos pero no usuarios.
3. **Como cliente** quiero seguir viendo el catálogo público sin iniciar sesión.

## Requisitos funcionales

- **RF-01** Autenticación para la UI de gestión y los endpoints de escritura.
- **RF-02** Roles mínimos: `admin` (todo) y `editor` (gestión del catálogo).
- **RF-03** Endpoints públicos de lectura del catálogo accesibles sin autenticación.
- **RF-04** La autorización se comprueba en el backend, nunca solo en el frontend.
- **RF-05** Rutas `/admin/*` del frontend redirigen a login si no hay sesión.

## Criterios de aceptación

- **CA-01** Una petición de escritura sin credenciales responde 401; con rol insuficiente, 403.
- **CA-02** Un `editor` puede crear sneakers pero no gestionar usuarios.
- **CA-03** El catálogo público funciona sin sesión.
- **CA-04** Tests de integración cubren 401/403 en todos los endpoints de escritura.

## Preguntas abiertas

- **PA-01** ¿Proveedor gestionado (Clerk, Auth0, Supabase Auth, Better Auth…) o autenticación propia con JWT?
- **PA-02** ¿Sesión por cookie HTTP-only o token Bearer?
- **PA-03** ¿Hace falta registro de clientes en el futuro (afecta al modelo de usuarios)?
