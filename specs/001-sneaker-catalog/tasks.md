# 001 · Tareas · Catálogo de sneakers

> Resolver PA-01…PA-04 de la spec antes de empezar la fase 1.

## Fase 0 · Preparación

- [x] T001 Resolver preguntas abiertas de la spec y actualizar `spec.md` / `plan.md`
- [x] T002 Añadir `Money` a `shared.domain` con tests (suma, comparación, validación de negativos y moneda)

## Fase 1 · Dominio

- [x] T010 Value objects `Gender` y `SneakerStatus`
- [x] T011 Entidades `SizeVariant`, `Colorway` (precio efectivo RF-08) e `Image`
- [x] T012 Agregado `Sneaker`: creación, actualización, gestión de colorways/tallas/imágenes y transiciones de estado
- [x] T013 Errores de dominio (`SneakerNotFound`, `SneakerSlugAlreadyExists`, `SkuAlreadyExists`, `SneakerNotPublishable`, `BrandInUse`, `CategoryInUse`, …)
- [x] T014 Puerto `SneakerRepository` y `SneakerFilters`
- [x] T015 Tests unitarios del agregado para RN-01…RN-04 y RF-07

## Fase 2 · Aplicación

- [x] T020 DTOs y comandos de sneaker, colorway, talla e imagen
- [x] T021 Casos de uso CRUD de sneaker (valida existencia de `Brand` y `Category`)
- [x] T022 Casos de uso de colorways y tallas (unicidad de `sku`, stock ≥ 0)
- [x] T023 Casos de uso de publicación (`Publish`, `Archive`, `Unarchive`)
- [x] T024 Casos de uso de imágenes usando el puerto `ImageStorage` (depende de 002-T010)
- [x] T025 Impedir borrar `Brand`/`Category` en uso (RN-06) actualizando sus casos de uso
- [x] T026 Fakes en memoria y tests unitarios de todos los casos de uso

## Fase 3 · Infraestructura

- [x] T030 Modelos SQLAlchemy y mappers entidad ↔ modelo
- [x] T031 `SqlAlchemySneakerRepository` con carga del agregado (`selectinload`) y filtros RF-03
- [x] T032 Migración Alembic (tablas, FKs, índices, CHECKs); quitar comentarios autogenerados
- [x] T033 Validar `upgrade`/`downgrade` en Postgres local (Docker Compose)

## Fase 4 · Presentación

- [x] T040 Schemas Pydantic de request/response
- [x] T041 Routers `sneakers`, `colorways`, `images` y dependencias
- [x] T042 Declarar respuestas 404/409 en OpenAPI
- [x] T043 Tests de integración de API (CRUD, filtros, publicación, errores CA-01…CA-05)

## Fase 5 · UI de pruebas

- [x] T050 Regenerar tipos (`pnpm --filter web api:types`)
- [x] T051 Gateway y hooks de sneakers en `features/admin`
- [x] T052 Formularios y tablas de sneakers, colorways, tallas e imágenes (contenedor/presentacional)
- [ ] T053 Validación en navegador del flujo completo (CA-06) — validado todo salvo la subida de imágenes, pendiente de credenciales de Cloudinary en desarrollo (002-T001)

## Cierre

- [ ] T060 `uv run pytest`, `pnpm typecheck`, `pnpm lint`, `pnpm --filter web build` en verde
- [ ] T061 Commits por capa (solo asunto) y marcar la spec como `Hecha`
