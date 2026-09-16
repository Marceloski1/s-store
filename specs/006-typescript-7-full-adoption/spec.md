# 006 · Adopción completa de TypeScript 7

- **Estado:** Diferida (bloqueada por upstream)
- **Prioridad:** P3

## Contexto

El proyecto usa TypeScript 7.0.2 para `tsc`, pero mantiene el alias `typescript` → `npm:@typescript/typescript6@^6.0.2` porque TypeScript 7.0 no expone API programática y estas herramientas la necesitan:

| Herramienta | Versión actual | Rango de TypeScript | Estado upstream (14-09-2026) |
|---|---|---|---|
| `@astrojs/check` / language server | 0.9.10 / 2.16.16 | `^5 \|\| ^6` | Bloqueado: [withastro/astro#17268](https://github.com/withastro/astro/issues/17268) ("unable to fix"), [roadmap#1321](https://github.com/withastro/roadmap/discussions/1321) |
| `typescript-eslint` | 8.70.0 | `>=4.8.4 <6.1.0` | Sin soporte: [typescript-eslint#12518](https://github.com/typescript-eslint/typescript-eslint/issues/12518) cerrado como "not planned" |
| `openapi-typescript` | 7.13.0 | `^5.x` (permitido 6 vía `peerDependencyRules`) | [openapi-typescript#2841](https://github.com/openapi-ts/openapi-typescript/issues/2841); PR [#2868](https://github.com/openapi-ts/openapi-typescript/pull/2868) sin publicar |

Según el [anuncio de TypeScript 7.0](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/), la API estable llegará en 7.1.

## Requisitos

- **RF-01** Eliminar el alias `typescript` → `@typescript/typescript6` de la raíz, `apps/web` y `packages/node/ui` cuando todas las herramientas soporten TypeScript 7.
- **RF-02** Eliminar `peerDependencyRules` de `openapi-typescript` en `pnpm-workspace.yaml`.
- **RF-03** Unificar el typecheck de `apps/web` (hoy `astro check && tsc --noEmit`) si `astro check` pasa a usar TypeScript 7.

## Riesgo vigente

`tsc --noEmit` con TypeScript 7 en `apps/web` no reconoce módulos `.astro`. Funciona hoy porque ningún `.ts`/`.tsx` importa `.astro`; si eso cambia, excluir esos ficheros del check con TS 7 o volver a solo `astro check`.

## Criterios de aceptación

- **CA-01** `pnpm why typescript` solo muestra 7.x.
- **CA-02** `pnpm typecheck`, `pnpm lint`, `pnpm --filter web build` y `pnpm --filter web api:types` en verde sin alias ni reglas de peers.

## Disparadores para reabrir

- Publicación de TypeScript 7.1 con API estable.
- Nueva versión de `@astrojs/check` con TypeScript 7 en `peerDependencies`.
- `typescript-eslint` con rango que incluya 7.x.
- `openapi-typescript` sin dependencia de TypeScript o con soporte de 7.
