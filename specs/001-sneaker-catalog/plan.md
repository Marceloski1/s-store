# 001 · Plan técnico · Catálogo de sneakers

## Decisiones

| Decisión | Elección | Motivo |
|---|---|---|
| Agregado | `Sneaker` es raíz de agregado con `images`, `colorways` y sus `size_variants` | Las reglas RN-01…RN-04 cruzan esas entidades; se garantizan dentro del agregado |
| Repositorio | Un único `SneakerRepository` (carga/guarda el agregado completo) + consultas de listado con filtros | Menos puertos; consistencia transaccional |
| Money | Value object `Money(amount: Decimal, currency: str)` en `shared.domain`; persistido como `NUMERIC(10,2)` + `CHAR(3)`. Operaciones y comparaciones solo entre la misma moneda | Evitar `float`; multi-moneda (PA-01) |
| Tallas | `size` como `Decimal` EU persistido en `NUMERIC(3,1)` | PA-02; admite medias tallas |
| Unicidad `slug`/`sku` | Comprobación en caso de uso + `UNIQUE` en BD (mapeado a 409 por `SqlAlchemyUnitOfWork`) | Mismo patrón que `Brand` |
| Imágenes | Puerto `ImageStorage` en `catalog/application/ports` (ver 002) | El dominio no conoce Cloudinary |
| Borrado de marcas/categorías en uso | FK `ON DELETE RESTRICT` + error de dominio `BrandInUse` / `CategoryInUse` | RN-06 con mensaje claro |
| Búsqueda `q` | `ILIKE` sobre `name` y `description` | Suficiente para MVP; full-text en el futuro |

## Capas afectadas

```
catalog/
├── domain/
│   ├── entities/            sneaker.py, colorway.py, size_variant.py, image.py
│   ├── value_objects/       gender.py, sneaker_status.py
│   ├── repositories/        sneaker_repository.py (+ SneakerFilters)
│   └── errors.py            SneakerNotFound, SkuAlreadyExists, SneakerNotPublishable, BrandInUse, …
├── application/
│   ├── ports/               image_storage.py
│   ├── dtos/                sneaker.py, colorway.py, image.py
│   └── use_cases/           sneaker.py, colorway.py, size_variant.py, image.py, publication.py
├── infrastructure/
│   └── persistence/         models.py (+ tablas), sneaker_repository.py
└── presentation/http/
    ├── schemas.py           Sneaker*/Colorway*/SizeVariant*/Image*
    ├── sneakers.py, colorways.py, images.py
    └── dependencies.py

packages/python/shared/src/shared/domain/money.py
```

## Contrato HTTP

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/sneakers` | Crear (estado `draft`) |
| `GET` | `/sneakers` | Listado con filtros RF-03 |
| `GET` | `/sneakers/{sneaker_id}` | Detalle con colorways, tallas e imágenes |
| `PUT` | `/sneakers/{sneaker_id}` | Actualizar datos base |
| `DELETE` | `/sneakers/{sneaker_id}` | Borrar agregado (RN-07) |
| `POST` | `/sneakers/{sneaker_id}/publish` · `/archive` · `/unarchive` | Transiciones RF-07 |
| `POST` | `/sneakers/{sneaker_id}/colorways` | Crear colorway |
| `PUT` / `DELETE` | `/sneakers/{sneaker_id}/colorways/{colorway_id}` | Editar / borrar colorway |
| `PUT` | `/sneakers/{sneaker_id}/colorways/{colorway_id}/sizes/{size}` | Alta o ajuste de stock |
| `DELETE` | `/sneakers/{sneaker_id}/colorways/{colorway_id}/sizes/{size}` | Baja de talla |
| `POST` | `/sneakers/{sneaker_id}/images` | Subida multipart |
| `PUT` | `/sneakers/{sneaker_id}/images/order` | Reordenar (lista de ids) |
| `POST` | `/sneakers/{sneaker_id}/images/{image_id}/primary` | Marcar principal |
| `DELETE` | `/sneakers/{sneaker_id}/images/{image_id}` | Borrar imagen |

Las respuestas 404/409 se declaran en OpenAPI para tipar errores en el frontend (ver 005).

## Base de datos

- Tablas `sneakers`, `sneaker_images`, `colorways`, `size_variants`.
- FKs: `sneakers.brand_id` / `category_id` → `RESTRICT`; hijos del agregado → `CASCADE`.
- Índices: `sneakers(slug)` único, `colorways(sku)` único, `size_variants(colorway_id, size)` único, `sneakers(brand_id)`, `sneakers(category_id)`, `sneakers(status)`.
- `CHECK (stock >= 0)`, `CHECK (base_price >= 0)`, `CHECK (price_override >= 0)` y `CHECK (size > 0)`.
- `sneakers(currency, base_price)` para ordenación y filtros de precio (RF-09).
- Una migración Alembic autogenerada y revisada, validada con `upgrade`/`downgrade` en Postgres local.

## Estrategia de tests

- **Unit (dominio):** invariantes del agregado (RN-01…RN-04, RF-07, RF-08).
- **Unit (casos de uso):** fakes en memoria para `SneakerRepository`, `ImageStorage` y `UnitOfWork`.
- **Integración API:** `TestClient` con fake de `ImageStorage` inyectado vía `dependency_overrides`.
- **Filtros:** tests de integración del repositorio. Los filtros con `ILIKE` y `NUMERIC` requieren Postgres real → depende de la tarea de 005 (tests contra Postgres).
- **UI:** validación manual en navegador con Playwright.

## Riesgos

- Filtros por talla/stock pueden generar N+1 → usar `selectinload` y subconsultas `EXISTS`.
- Subidas grandes → límite de 5 MB en la capa HTTP (002-T014).
