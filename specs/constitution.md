# Constitución del proyecto

Principios no negociables. Toda spec, plan y tarea debe cumplirlos; cualquier excepción se documenta en el `plan.md` correspondiente con su justificación.

## I. Arquitectura

1. **Clean Architecture + Screaming Architecture.** El código se organiza primero por feature (`catalog/`, …) y dentro por capas: `domain` → `application` → `infrastructure` / `presentation`.
2. **Regla de dependencias.** Las dependencias apuntan siempre hacia dentro. `domain` no importa SQLAlchemy, Pydantic, FastAPI ni SDKs externos.
3. **Dominio puro.** Entidades y value objects como `dataclass`; invariantes validadas en el dominio.
4. **Puertos y adaptadores.** Repositorios y servicios externos (p. ej. almacenamiento de imágenes) se definen como `Protocol` en capas internas y se implementan en `infrastructure`.
5. **Transacciones explícitas.** Los casos de uso confirman cambios mediante el puerto `UnitOfWork`; nunca en dependencias de FastAPI.
6. **Pydantic solo en los bordes**: `presentation` (schemas HTTP) y `config` (pydantic-settings).
7. **Lo genérico vive en `packages/`**: `packages/python/shared` y `packages/node/ui`. Nada específico de una feature entra ahí.
8. **Configuración compartida de tooling** en `packages/node/{eslint-config,prettier-config,typescript-config}`. Todo proyecto Node del repo extiende de ahí; no se duplican reglas ni opciones de compilador localmente (salvo `paths` y ajustes propios del framework).

## II. Monorepo y stack

| Área | Decisión |
|---|---|
| Gestor Node | **pnpm** siempre (`pnpm add`, `pnpm dlx`, `pnpm view`); nunca `npm`/`npx` |
| Runtime Node | Node 26 (`.nvmrc`, `engines`) |
| TypeScript | 7 (`tsc`) + alias `typescript` → `@typescript/typescript6` para tooling que necesita la API |
| Frontend | Astro 7 + islas React 19, Tailwind 4, shadcn (`base-lyra`) en `@workspace/ui` |
| Python | 3.14 gestionado con **uv** (workspace en la raíz) |
| Backend | FastAPI, SQLAlchemy 2 async + asyncpg, Alembic, pydantic-settings |
| Base de datos | PostgreSQL: Docker Compose en local (puerto 5434), Neon en producción |
| Imágenes | Cloudinary |

## III. Testing

1. **pytest** para todo el backend: unitarios de casos de uso con fakes en memoria e integración de API con `TestClient`.
2. Cada feature se entrega con tests en todas sus capas; ninguna tarea se da por hecha con tests en rojo.
3. Frontend: `pnpm typecheck`, `pnpm lint` y `pnpm --filter web build` en verde.
4. Los cambios de UI se validan en el navegador contra el backend real antes de cerrarlos.

## IV. Frontend

1. Patrón **contenedor / presentacional**: hooks y contenedores gestionan datos; componentes presentacionales solo reciben props.
2. Estructura por feature en `apps/web/src/features/<feature>/{api,hooks,components}`.
3. El cliente HTTP es tipado a partir del OpenAPI del backend (`pnpm --filter web api:types`); no se escriben tipos de la API a mano.
4. Variables de entorno declaradas con `astro:env`.

## V. Código

1. **Sin comentarios** en el código, salvo marcadores `TODO(...)` para trabajo pendiente.
2. Código, identificadores y mensajes de commit en inglés; documentación y textos de UI en español.

## VI. Entornos y secretos

1. Backend: `APP_ENV` (`development` por defecto) selecciona `.env.{APP_ENV}`.
2. Frontend: `.env.development` / `.env.production` según el modo de Astro.
3. Solo se versionan los `.env.example`; los `.env.*` reales nunca se commitean.

## VII. Git

1. Conventional Commits en inglés y minúsculas.
2. **Solo línea de asunto**: sin descripción y sin `Co-Authored-By`.
3. Commits pequeños y agrupados por responsabilidad.
