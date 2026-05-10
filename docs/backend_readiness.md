# Backend readiness before APIs

This project intentionally keeps the legacy restaurant business schema outside
Django migrations. Before adding HTTP APIs, keep these backend contracts stable.

## Schema bootstrap

Run Django's built-in migrations for contrib apps, then create any missing
legacy unmanaged tables and `*_ID_seq` sequences from the model metadata:

```bash
python3 manage.py migrate
python3 manage.py bootstrap_legacy_schema
```

Preview the bootstrap work without changing the database:

```bash
python3 manage.py bootstrap_legacy_schema --dry-run
```

Do not add a `restaurante/migrations/` directory unless the unmanaged legacy
schema strategy changes.

## Auth and permissions

Use `django.contrib.auth` as the source of truth for users, sessions, groups,
and permissions. The legacy `AuthUser_UbicacionFisica` and
`AuthUser_Sucursal` models are scoped-access mapping tables only. Do not expose
or mutate mirrored Django core tables such as `auth_user` or
`django_content_type` through new APIs.

## API boundary

Keep repository/factory classes as the domain boundary for now. API views should
translate request data into repository/factory calls, wrap writes in
transactions where a workflow spans multiple tables, and map domain exceptions
to HTTP responses consistently:

- `ObjectDoesNotExist` -> 404 or 400, depending on whether the missing object is
  the requested resource or invalid input.
- `ValueError` -> 400 validation error.
- `IntegrityError` -> 409 conflict when caused by duplicate state; otherwise
  log and return a generic server error.

Use Django settings for environment-specific behavior: set
`DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, database variables,
and `DJANGO_LOG_LEVEL` explicitly outside local development.
