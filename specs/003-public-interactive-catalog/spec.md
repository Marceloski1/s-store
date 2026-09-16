# 003 · Catálogo público interactivo

- **Estado:** Borrador
- **Prioridad:** P2
- **Depende de:** [001](../001-sneaker-catalog/spec.md)

## Contexto

El objetivo original del proyecto es un catálogo interactivo de sneakers para clientes. Hoy solo existe una UI de pruebas para gestionar marcas y categorías.

## Historias de usuario

1. **Como cliente** quiero ver un listado de sneakers publicados con imagen, marca y precio.
2. **Como cliente** quiero filtrar por marca, categoría, género, talla y rango de precio, y buscar por texto, sin recargar la página.
3. **Como cliente** quiero compartir un enlace con mis filtros aplicados y que el botón atrás funcione.
4. **Como cliente** quiero ver la ficha de un sneaker con galería, selector de color y tallas disponibles.
5. **Como negocio** quiero que las páginas de listado y ficha sean indexables por buscadores.

## Requisitos funcionales

- **RF-01** Página de listado `/sneakers` renderizada en servidor con los sneakers `active`.
- **RF-02** Filtros, búsqueda, ordenación y paginación sincronizados con la URL (query string).
- **RF-03** Islas React para filtros y resultados; el resto de la página en Astro.
- **RF-04** Ficha `/sneakers/[slug]` con galería ordenada (imagen principal primero), selector de colorway, precio efectivo y tallas con stock.
- **RF-05** Tallas sin stock visibles pero deshabilitadas.
- **RF-06** Estados de carga, vacío y error en todas las vistas.
- **RF-07** Metadatos SEO por página (title, description, Open Graph con la imagen principal).
- **RF-08** Imágenes responsive con transformaciones de Cloudinary y `loading="lazy"` fuera del primer viewport.
- **RF-09** La UI de gestión se mueve a una ruta separada (p. ej. `/admin`), protegida cuando exista [007](../007-admin-auth/spec.md).

## Criterios de aceptación

- **CA-01** Abrir `/sneakers?brand=nike&size=42` muestra el mismo resultado que aplicar esos filtros desde la UI.
- **CA-02** Un sneaker `draft` o `archived` no aparece en el listado y su ficha responde 404.
- **CA-03** La ficha muestra solo las imágenes del sneaker y el precio del colorway seleccionado.
- **CA-04** Funciona a 400 px de ancho y cumple accesibilidad básica (navegación por teclado, etiquetas, contraste).
- **CA-05** Lighthouse: rendimiento y SEO ≥ 90 en la ficha y en el listado.

## Fuera de alcance

- Carrito, checkout, favoritos y cuentas de cliente.
- Internacionalización.

## Preguntas abiertas

- **PA-01** ¿Modo de salida de Astro: SSR con adaptador (¿cuál? Vercel/Node) o estático con revalidación?
- **PA-02** ¿Diseño visual de referencia o se usa el tema actual de `@workspace/ui`?
- **PA-03** ¿Cambio de colorway en la ficha también cambia la galería? (requiere `colorway_id` opcional en `Image`, ver 001).
