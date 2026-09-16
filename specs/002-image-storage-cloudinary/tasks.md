# 002 · Tareas · Cloudinary

- [ ] T001 Obtener credenciales de Cloudinary para desarrollo y producción (PA-01)
- [ ] T002 Añadir variables `CLOUDINARY_*` a settings, `.env.development`, `.env.production` y `.env.example`
- [ ] T010 Definir puerto `ImageStorage` y `StoredImage`
- [ ] T011 Fake `InMemoryImageStorage` para tests
- [x] T012 Añadir dependencia `cloudinary` al backend con `uv add`
- [ ] T013 Implementar `CloudinaryImageStorage` (subida, borrado, transformaciones de entrega, ejecución en hilo)
- [ ] T014 Validación de tipo y tamaño en la capa HTTP (RF-04)
- [ ] T015 Dependencia `get_image_storage` y override en tests de integración
- [ ] T016 Tests de compensación (RF-06) y borrado tolerante (RF-07)
- [ ] T017 Prueba manual de subida y borrado reales en desarrollo (CA-02, CA-03)
- [ ] T018 Commits (solo asunto) y marcar la spec como `Hecha`
