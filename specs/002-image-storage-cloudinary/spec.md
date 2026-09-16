# 002 · Almacenamiento de imágenes con Cloudinary

- **Estado:** Borrador
- **Prioridad:** P1
- **Bloqueante para:** [001](../001-sneaker-catalog/spec.md) (RF-06, RN-05, RN-07)

## Contexto

Las imágenes de los sneakers se guardan en Cloudinary. El backend debe subirlas, guardar su referencia (`public_id` + `url`) y borrarlas, sin que el dominio dependa del SDK.

## Historias de usuario

1. **Como gestor** quiero subir imágenes desde el panel y verlas inmediatamente en el sneaker.
2. **Como gestor** quiero que al borrar una imagen o un sneaker no queden ficheros huérfanos en Cloudinary.
3. **Como desarrollador** quiero probar el flujo sin credenciales reales ni llamadas de red en los tests.

## Requisitos funcionales

- **RF-01** Puerto `ImageStorage` con operaciones `upload(content, filename, folder) -> StoredImage(public_id, url)` y `delete(public_id)`.
- **RF-02** Adaptador `CloudinaryImageStorage` con el SDK oficial `cloudinary`.
- **RF-03** Configuración vía settings: `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`, `CLOUDINARY_FOLDER` (distinta por entorno).
- **RF-04** Validación de tipo (`image/jpeg`, `image/png`, `image/webp`) y tamaño máximo antes de subir.
- **RF-05** URLs servidas por HTTPS y con transformaciones de entrega (`f_auto,q_auto`).
- **RF-06** Si la subida funciona pero falla la transacción en BD, se intenta borrar la imagen subida (compensación).
- **RF-07** Si falla el borrado en Cloudinary tras borrar en BD, se registra el `public_id` para reintento y la operación no falla para el usuario.

## Criterios de aceptación

- **CA-01** Subir un fichero no permitido responde 422 sin llamar a Cloudinary.
- **CA-02** Subir una imagen válida persiste `public_id` y `url` y la imagen es accesible por HTTPS.
- **CA-03** Borrar la imagen elimina el recurso de Cloudinary (verificado en entorno de desarrollo).
- **CA-04** Los tests usan un fake de `ImageStorage`; ningún test hace llamadas de red.
- **CA-05** `.env.example` documenta las variables nuevas; los secretos no se versionan.

## Fuera de alcance

- Subida directa desde el navegador con firma (signed uploads). Se valorará si el tamaño de las imágenes lo exige.
- Gestión de avatares o logos de marcas.

## Preguntas abiertas

- **PA-01** Credenciales de Cloudinary para desarrollo y producción (¿cuentas o carpetas separadas?).
- **PA-02** Tamaño máximo por imagen y número máximo por sneaker (compartida con 001-PA-03).
- **PA-03** ¿Mecanismo de reintento para borrados fallidos (tabla de pendientes, job periódico o solo log)?
