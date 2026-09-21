# 007 · Plan técnico · Autenticación y roles

## Decisiones

| Decisión | Elección | Motivo |
|---|---|---|
| Feature | `identity` en el backend con las mismas capas que `catalog` | Constitución I.1 |
| Contraseñas | Argon2id (`argon2-cffi`) detrás del puerto `PasswordHasher` | Estándar actual; dominio sin dependencias |
| Token | JWT HS256 (`PyJWT`) detrás del puerto `TokenService`; claims `sub`, `role`, `exp` | Sin estado en servidor |
| Transporte | Cookie `saury_session` HTTP-only, `SameSite=Lax`, `Secure` en producción, `Path=/` | No accesible desde JS |
| Caducidad | 8 h (`JWT_EXPIRES_MINUTES`) | Jornada de trabajo |
| Validación de sesión | En cada petición se carga el usuario; si no existe o está inactivo → 401 | RF-08 |
| Autorización | Dependencias FastAPI `require_role(Role.ADMIN)` / `require_role(Role.SUPER_ADMIN)` aplicadas por router | RF-04 |
| CORS | `allow_credentials=True` con orígenes explícitos | Cookies desde `localhost:4321` |
| Bootstrap | Script `create-super-admin` (`uv run create-super-admin --email … --name …`, contraseña por prompt o `SUPER_ADMIN_PASSWORD`) | RF-07 |
| Frontend | Middleware de Astro que llama a `GET /auth/me` reenviando la cookie y guarda el usuario en `Astro.locals`; tabla de permisos por prefijo de ruta | RF-06 |
| Cliente HTTP | El navegador llama a `/api/*`, un proxy de Astro hacia el backend (`API_URL`, solo servidor); en SSR el cliente llama directo al backend y reenvía la cookie de la petición mediante `AsyncLocalStorage` | La cookie es first-party aunque web y API vivan en dominios distintos |
| Cierre de sesión | `POST /admin/logout` (endpoint de Astro, sin JS) borra la cookie y redirige al login | Funciona sin hidratar islas |

## Modelo de datos

`users`: `id` (uuid), `email` (único, minúsculas), `name`, `password_hash`, `role` (`ADMIN`/`SUPER_ADMIN`), `is_active`, `created_at`, `updated_at`.

## Contrato de API

| Método | Ruta | Rol | Respuesta |
|---|---|---|---|
| POST | `/auth/login` | — | `UserResponse` + cookie; 401 si credenciales inválidas o usuario inactivo |
| POST | `/auth/logout` | — | 204 y borra la cookie |
| GET | `/auth/me` | sesión | `UserResponse`; 401 sin sesión |
| GET | `/users` | `SUPER_ADMIN` | `PageResponse[UserResponse]` |
| POST | `/users` | `SUPER_ADMIN` | Crea un `ADMIN`; 409 si el email existe |
| PATCH | `/users/{id}` | `SUPER_ADMIN` | Cambia `name`, `is_active` o `password` de un `ADMIN` |
| DELETE | `/users/{id}` | `SUPER_ADMIN` | 204; no puede borrarse a sí mismo ni a otro `SUPER_ADMIN` (409) |

## Tests

- Unit: entidad `User`, casos de uso con fakes de repositorio, hasher y token service.
- Integración: login/logout/me, gestión de usuarios y matriz 401/403 sobre todos los endpoints protegidos (CA-04).
