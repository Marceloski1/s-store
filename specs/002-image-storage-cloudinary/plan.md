# 002 · Plan técnico · Cloudinary

## Decisiones

| Decisión | Elección | Motivo |
|---|---|---|
| Ubicación del puerto | `catalog/application/ports/image_storage.py` | Lo consumen casos de uso; si otra feature lo necesita se mueve a `shared.application` |
| Adaptador | `catalog/infrastructure/storage/cloudinary_image_storage.py` | Única capa que importa `cloudinary` |
| SDK síncrono | Ejecutar llamadas con `anyio.to_thread.run_sync` | El SDK de Cloudinary es bloqueante y no debe bloquear el event loop |
| Settings | Nuevo bloque `cloudinary_*` en `Settings`, opcional en tests | Los tests inyectan el fake |
| Inyección | `get_image_storage` en `presentation/http/dependencies.py`, sobreescribible con `dependency_overrides` | Mismo patrón que los repositorios |
| Compensación | El caso de uso sube → guarda → `commit`; si `commit` falla, llama a `delete` y relanza | RF-06 sin transacciones distribuidas |

## Contrato del puerto

```python
class StoredImage(Protocol):
    public_id: str
    url: str


class ImageStorage(Protocol):
    async def upload(self, content: bytes, filename: str, folder: str) -> StoredImage: ...

    async def delete(self, public_id: str) -> None: ...
```

## Tests

- Fake en memoria `InMemoryImageStorage` con registro de subidas y borrados.
- Tests unitarios de la compensación (RF-06) y del borrado tolerante a fallos (RF-07).
- Test manual (no automatizado) contra Cloudinary en desarrollo para CA-02 y CA-03.
