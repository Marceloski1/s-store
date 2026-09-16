# 004 · Preparación para producción

- **Estado:** Borrador
- **Prioridad:** P2
- **Depende de:** [007](../007-admin-auth/spec.md) — no se despliegan endpoints de escritura sin autenticación

## Contexto

Hoy todo funciona en local (Postgres en Docker, `.env.development`). Los `.env.production` contienen valores de ejemplo, el CORS acepta cualquier método y cabecera (marcado con `TODO(cors)`) y no hay pipeline de despliegue.

## Requisitos funcionales

- **RF-01** Base de datos en **Neon** con la connection string *pooled* configurada en `apps/saury-backend/.env.production` (o en el gestor de secretos del hosting).
- **RF-02** Verificar el funcionamiento de asyncpg con el pooler de Neon (PgBouncer en modo transacción y sentencias preparadas); si falla, desactivar la caché de sentencias (`statement_cache_size=0` / `prepared_statement_cache_size=0`).
- **RF-03** Migraciones Alembic aplicadas contra Neon como paso explícito del despliegue, usando la conexión directa (no pooled).
- **RF-04** CORS restringido: `allow_origins` con el dominio real, `allow_methods` y `allow_headers` explícitos; eliminar `TODO(cors)` en `main.py`.
- **RF-05** `PUBLIC_API_URL` real en `apps/web/.env.production` y `CORS_ORIGINS` coherente con el dominio del frontend.
- **RF-06** Documentación de la API (`/docs`, `/openapi.json`) deshabilitada o protegida en producción.
- **RF-07** Logging estructurado y `DATABASE_ECHO=false` en producción.
- **RF-08** Endpoint de salud (`/health`) que compruebe la conexión a base de datos.
- **RF-09** Pipeline CI: tests Python, typecheck, lint y build del frontend en cada push.
- **RF-10** Despliegue del backend y del frontend en la plataforma elegida.

## Criterios de aceptación

- **CA-01** `APP_ENV=production` arranca con Neon, aplica migraciones y responde en `/health`.
- **CA-02** Una petición desde un origen no permitido es rechazada por CORS.
- **CA-03** `/docs` no es accesible públicamente en producción.
- **CA-04** El pipeline CI falla si falla cualquier test, typecheck, lint o build.
- **CA-05** Ningún secreto está versionado en git.

## Preguntas abiertas

- **PA-01** ¿Plataforma de hosting para backend y frontend (Vercel, Fly.io, Railway, Render…)?
- **PA-02** ¿Dominio final del frontend y de la API?
- **PA-03** ¿CI en GitHub Actions o GitLab CI?
- **PA-04** ¿Proyecto/rama de Neon separado para staging?
