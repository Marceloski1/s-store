# 003 · Plan técnico · Catálogo público

## Decisiones

| Decisión | Elección | Motivo |
|---|---|---|
| Renderizado | Páginas Astro con datos del backend en servidor + islas React para interactividad | SEO y rendimiento (RF-01, RF-07) |
| Estado de filtros | Fuente de verdad en la URL; la isla lee y escribe `URLSearchParams` | Enlaces compartibles y botón atrás (RF-02) |
| Datos en cliente | Mismo cliente tipado `openapi-fetch`; valorar TanStack Query si aparecen cachés o reintentos | Evitar dependencias hasta que haga falta |
| Endpoint público | `GET /catalog/sneakers`, `GET /catalog/sneakers/{slug}` y `GET /catalog/facets` fuerzan `status=active` en el backend | No depender de que el frontend filtre |
| Estructura | `apps/web/src/features/storefront/{api,hooks,components}` separado de `features/catalog` (gestión) | Screaming architecture |
| Componentes UI | Nuevos componentes shadcn en `@workspace/ui` (select, checkbox, slider, badge, skeleton, carousel) | Reutilizables |
| Adaptador Astro | `@astrojs/node` standalone con `output: "server"` | Hosting aún sin decidir (004 PA-01) |
| Marca y categoría | El frontend cruza `brand_id`/`category_id` con los listados de marcas y categorías | Evita un read model en el backend mientras el catálogo sea pequeño |

## Tests

- Tests de componentes presentacionales (Vitest + Testing Library) — requiere añadir tooling de tests al frontend (005).
- Validación en navegador con Playwright de CA-01…CA-04.
- Lighthouse en build de producción (CA-05).
