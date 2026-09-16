# 005 · Calidad y tooling

- **Estado:** Borrador
- **Prioridad:** P2

## Contexto

Deuda técnica y huecos de tooling detectados durante la sesión inicial.

## Requisitos

- **RF-01 · Lint de `@workspace/ui` en rojo.** `packages/node/ui/src/components/button.tsx` exporta `buttonVariants` y rompe `react-refresh/only-export-components`. `pnpm lint` falla desde el commit inicial.
- **RF-02 · Tests de backend contra Postgres real.** Los tests de integración usan SQLite (aiosqlite); no cubren tipos y comportamientos específicos de Postgres (`UUID` nativo, `ILIKE`, `NUMERIC`, `CHECK`, FKs `RESTRICT`). Necesario para los filtros de 001.
- **RF-03 · Python dentro de Turborepo.** `pnpm dev`, `pnpm build` y `pnpm typecheck` no ejecutan nada del backend.
- **RF-04 · Linter y type checker para Python.** No hay `ruff` ni `mypy`/`pyright` configurados.
- **RF-05 · Errores tipados en OpenAPI.** Las respuestas 404/409 no están declaradas, por lo que `openapi-fetch` no las tipa en el frontend.
- **RF-06 · Tests de frontend.** No existe tooling de tests de componentes (Vitest + Testing Library).
- **RF-07 · README desactualizado.** No documenta el backend, uv, Docker Compose, Alembic, entornos ni SDD.
- **RF-08 · Hints de `astro check`.** Hay 2 hints sin revisar.
- **RF-09 · Aviso de deprecación en tests.** `starlette.testclient` emite `anyio.abc.BlockingPortal` deprecado (upstream); revisar al actualizar Starlette.

## Criterios de aceptación

- **CA-01** `pnpm lint` en verde en todo el monorepo.
- **CA-02** Los tests de integración del backend pueden ejecutarse contra Postgres (Docker/testcontainers) en local y en CI.
- **CA-03** `pnpm typecheck`, `pnpm lint` y un comando de test unificado incluyen el backend.
- **CA-04** `ruff check`, `ruff format --check` y el type checker de Python en verde.
- **CA-05** Los tipos generados incluyen los errores 404/409 de los endpoints.
- **CA-06** `pnpm --filter web test` ejecuta tests de componentes.
- **CA-07** README describe cómo levantar todo el proyecto desde cero.

## Preguntas abiertas

- **PA-01** Para RF-01: ¿mover `buttonVariants` a un fichero propio o desactivar la regla en `@workspace/ui` (patrón habitual de shadcn)?
- **PA-02** Para RF-02: ¿testcontainers o reutilizar el Docker Compose de desarrollo con una base de datos de tests?
- **PA-03** Para RF-04: ¿mypy o pyright?
