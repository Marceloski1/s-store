# 003 · Plan técnico · Catálogo público

## Decisiones

| Decisión | Elección | Motivo |
|---|---|---|
| Renderizado | Páginas Astro con datos del backend en servidor + islas React para interactividad | SEO y rendimiento (RF-01, RF-07) |
| Estado de filtros | Fuente de verdad en la URL; la isla lee y escribe `URLSearchParams` | Enlaces compartibles y botón atrás (RF-02) |
| Datos en cliente | Mismo cliente tipado `openapi-fetch`; valorar TanStack Query si aparecen cachés o reintentos | Evitar dependencias hasta que haga falta |
| Endpoint público | Filtro `status=active` forzado por el backend en rutas públicas (p. ej. `GET /catalog/sneakers`) | No depender de que el frontend filtre |
| Estructura | `apps/web/src/features/storefront/{api,hooks,components}` separado de `features/catalog` (gestión) | Screaming architecture |
| Componentes UI | Nuevos componentes shadcn en `@workspace/ui` (select, checkbox, slider, badge, skeleton, carousel) | Reutilizables |
| Adaptador Astro | Pendiente PA-01 | — |

## Tests

- Tests de componentes presentacionales (Vitest + Testing Library) — requiere añadir tooling de tests al frontend (005).
- Validación en navegador con Playwright de CA-01…CA-04.
- Lighthouse en build de producción (CA-05).
