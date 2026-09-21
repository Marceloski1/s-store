# 007 · Autenticación y roles del panel

- **Estado:** En progreso
- **Prioridad:** P2 — bloqueante para [004](../004-production-readiness/spec.md)

## Contexto

Todos los endpoints de escritura y la UI de gestión son públicos. Es aceptable en local, pero no en producción. El catálogo público sigue sin requerir sesión.

## Roles

| Rol | Puede |
|---|---|
| Sin sesión | Ver el catálogo público (`/`, `/sneakers/*`) |
| `ADMIN` | Gestionar el catálogo: sneakers, colores, tallas, fotos, marcas y categorías |
| `SUPER_ADMIN` | Gestionar usuarios `ADMIN` (alta, baja, activación). No gestiona el catálogo |

## Historias de usuario

1. **Como `SUPER_ADMIN`** quiero dar de alta usuarios `ADMIN` para que gestionen el catálogo.
2. **Como `SUPER_ADMIN`** quiero desactivar o borrar un `ADMIN` para retirarle el acceso.
3. **Como `ADMIN`** quiero iniciar sesión y gestionar el catálogo.
4. **Como cliente** quiero seguir viendo el catálogo público sin iniciar sesión.

## Requisitos funcionales

- **RF-01** Inicio y cierre de sesión con email y contraseña.
- **RF-02** Roles `ADMIN` y `SUPER_ADMIN` con los permisos de la tabla; no son acumulativos.
- **RF-03** Los endpoints `/catalog/*` y las lecturas de marcas y categorías (`GET /brands`, `GET /brands/{id}`, `GET /categories`, `GET /categories/{id}`) son públicos.
- **RF-04** El resto de endpoints del catálogo exige `ADMIN`; los de usuarios exigen `SUPER_ADMIN`.
- **RF-05** La autorización se comprueba en el backend, nunca solo en el frontend.
- **RF-06** Permisos por ruta en el frontend: `/admin/login` es pública; las rutas del catálogo del panel exigen `ADMIN`; `/admin/usuarios` exige `SUPER_ADMIN`. Sin sesión se redirige al login; con rol insuficiente, a la ruta de inicio de su rol.
- **RF-07** El primer `SUPER_ADMIN` se crea con un comando de consola.
- **RF-08** Un usuario desactivado no puede iniciar sesión y su sesión deja de ser válida.

## Criterios de aceptación

- **CA-01** Una petición protegida sin sesión responde 401; con rol insuficiente, 403.
- **CA-02** Un `ADMIN` puede crear sneakers pero no gestionar usuarios; un `SUPER_ADMIN` puede gestionar usuarios pero no sneakers.
- **CA-03** El catálogo público funciona sin sesión.
- **CA-04** Tests de integración cubren 401/403 en todos los endpoints protegidos.
- **CA-05** Visitar `/admin` sin sesión redirige a `/admin/login`; tras iniciar sesión se vuelve a la ruta pedida.

## Fuera de alcance

- Registro de clientes y recuperación de contraseña por email.
- Proveedores externos (OAuth).

## Preguntas resueltas

- **PA-01** Autenticación propia en el backend (feature `identity`).
- **PA-02** JWT firmado en cookie HTTP-only.
- **PA-03** No hay registro de clientes; el modelo solo contempla usuarios del panel.
