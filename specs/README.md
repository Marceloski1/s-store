# Specs · sauri-store

Este directorio aplica **Spec-Driven Development (SDD)**: ningún trabajo se implementa sin una especificación aprobada.

## Flujo

1. **`spec.md`** — qué y por qué: historias de usuario, requisitos, criterios de aceptación, fuera de alcance y preguntas abiertas. Sin detalles de implementación.
2. **`plan.md`** — cómo: decisiones técnicas, capas afectadas, modelo de datos, contratos de API y estrategia de tests. Solo en specs de tamaño medio o grande.
3. **`tasks.md`** — checklist ordenado y verificable. Cada tarea termina con tests en verde.
4. **Implementación** — tarea a tarea, respetando [`constitution.md`](./constitution.md).

Estados: `Borrador` → `Aprobada` → `En progreso` → `Hecha` · `Diferida`.

## Índice

| ID | Spec | Estado | Prioridad | Depende de |
|---|---|---|---|---|
| 001 | [Catálogo de sneakers](./001-sneaker-catalog/spec.md) | En progreso | P1 | 002 (imágenes) |
| 002 | [Almacenamiento de imágenes con Cloudinary](./002-image-storage-cloudinary/spec.md) | En progreso | P1 | — |
| 003 | [Catálogo público interactivo](./003-public-interactive-catalog/spec.md) | Borrador | P2 | 001 |
| 004 | [Preparación para producción](./004-production-readiness/spec.md) | Borrador | P2 | 007 |
| 005 | [Calidad y tooling](./005-quality-tooling/spec.md) | Borrador | P2 | — |
| 006 | [Adopción completa de TypeScript 7](./006-typescript-7-full-adoption/spec.md) | Diferida | P3 | Upstream (TS 7.1, Astro, typescript-eslint, openapi-typescript) |
| 007 | [Autenticación y roles del panel](./007-admin-auth/spec.md) | Diferida | P2 | — |

## Ya implementado (referencia)

- Monorepo pnpm (`apps/web`, `packages/node/ui`) + workspace uv (`apps/saury-backend`, `packages/python/shared`).
- Backend Clean Architecture con CRUD de `Brand` y `Category`, paginación, errores de dominio → HTTP, Alembic y settings por entorno.
- Postgres local con Docker Compose y CORS configurable.
- UI de pruebas en Astro + React conectada a la API con cliente tipado desde OpenAPI.
- Node 26, Python 3.14 y TypeScript 7 (con alias TS 6 para tooling).
