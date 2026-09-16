# 001 · Catálogo de sneakers

- **Estado:** Borrador
- **Prioridad:** P1
- **Depende de:** [002 · Cloudinary](../002-image-storage-cloudinary/spec.md) para las imágenes

## Contexto

La tienda vende zapatillas (sneakers). Ya existen `Brand` y `Category` con CRUD completo. Falta el núcleo del catálogo: el modelo de zapatilla con sus colores, tallas, stock e imágenes, gestionable mediante CRUD desde la API y la UI de pruebas.

## Historias de usuario

1. **Como gestor del catálogo** quiero crear, editar, listar y borrar sneakers para mantener la oferta actualizada.
2. **Como gestor** quiero añadir colorways a un sneaker, cada uno con su SKU y precio opcional, para vender el mismo modelo en varios colores.
3. **Como gestor** quiero definir las tallas disponibles por colorway y ajustar su stock.
4. **Como gestor** quiero subir, ordenar, marcar como principal y borrar las imágenes de un sneaker.
5. **Como gestor** quiero preparar sneakers en borrador y publicarlos solo cuando estén completos.
6. **Como gestor** quiero filtrar y buscar sneakers para encontrarlos rápido.

## Modelo de dominio

```
Brand 1───* Sneaker *───1 Category
            │     │
            1     1
            │     │
            *     *
        Image   Colorway 1───* SizeVariant
```

| Entidad | Campos |
|---|---|
| **Sneaker** | `id`, `name`, `slug`, `description`, `brand_id`, `category_id`, `gender` (`men`/`women`/`unisex`/`kids`), `base_price` (Money), `status` (`draft`/`active`/`archived`), `release_date?`, `created_at`, `updated_at` |
| **Image** | `id`, `sneaker_id`, `public_id` (Cloudinary), `url`, `alt`, `position`, `is_primary` |
| **Colorway** | `id`, `sneaker_id`, `name`, `color_code`, `sku`, `price_override?` |
| **SizeVariant** | `id`, `colorway_id`, `size`, `stock` |

## Requisitos funcionales

- **RF-01** CRUD de sneakers con validación de nombre, slug, descripción, precio y referencias a `Brand` y `Category` existentes.
- **RF-02** El slug se genera a partir del nombre si no se envía y es único.
- **RF-03** Listado paginado con filtros combinables: `brand`, `category`, `gender`, `status`, `size`, `min_price`, `max_price`, `in_stock`, búsqueda por texto (`q`) y ordenación (`name`, `price`, `release_date`, `created_at`).
- **RF-04** CRUD de colorways dentro de un sneaker; el `sku` es único globalmente.
- **RF-05** Alta, baja y ajuste de stock de tallas por colorway; talla única por colorway.
- **RF-06** Gestión de imágenes del sneaker: subir (multipart), reordenar, marcar principal y borrar.
- **RF-07** Transiciones de estado: `draft → active`, `active → archived`, `archived → draft`.
- **RF-08** El precio efectivo de un colorway es `price_override` si existe, si no `base_price`.

## Reglas de negocio

- **RN-01** Un sneaker solo puede pasar a `active` si tiene al menos una imagen principal y al menos un colorway con una talla.
- **RN-02** Como máximo una imagen `is_primary` por sneaker; marcar otra desmarca la anterior.
- **RN-03** Las posiciones de imagen son consecutivas y empiezan en 0.
- **RN-04** El stock nunca es negativo.
- **RN-05** Borrar una imagen la elimina también de Cloudinary.
- **RN-06** No se puede borrar una `Brand` o `Category` con sneakers asociados (409).
- **RN-07** Borrar un sneaker elimina sus colorways, tallas e imágenes (incluidas las de Cloudinary).

## Criterios de aceptación

- **CA-01** `POST /sneakers` con marca inexistente responde 404; con slug duplicado, 409; con precio negativo, 422.
- **CA-02** `POST /sneakers/{id}/publish` sin imagen principal responde 409 con un mensaje que explica la regla incumplida.
- **CA-03** `GET /sneakers?brand=nike&size=42&in_stock=true` devuelve solo sneakers de esa marca con stock en talla 42.
- **CA-04** Ajustar stock por debajo de 0 responde 422 y no modifica datos.
- **CA-05** Borrar una marca con sneakers responde 409.
- **CA-06** La UI de pruebas permite ejecutar el CRUD completo de sneakers, colorways, tallas e imágenes.
- **CA-07** Tests unitarios, de integración y la migración Alembic en verde; migración validada contra Postgres local.

## Fuera de alcance

- Catálogo público y SEO → [003](../003-public-interactive-catalog/spec.md).
- Autenticación → [007](../007-admin-auth/spec.md).
- Carrito, pedidos, reseñas, tags y materiales.
- Imágenes por colorway (se podrá añadir `colorway_id` opcional en `Image` sin romper el modelo).

## Preguntas abiertas

- **PA-01** ¿Moneda única (EUR/USD) o multi-moneda? Afecta al value object `Money`.
- **PA-02** ¿Sistema de tallas: EU, US, UK o varios con conversión?
- ~~**PA-03**~~ Resuelta en 002-PA-02: máximo 8 imágenes por sneaker, 5 MB por imagen, formatos JPEG, PNG y WebP.
- **PA-04** ¿`archived` oculta el sneaker también en la UI de gestión o solo en el catálogo público?
