# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

Django 5.2 restaurant management system ("Sistema de Restaurante") on Python 3.12. Single Django app (`restaurante`) with a Repository/Factory pattern layer on top of unmanaged PostgreSQL models.

### Python environment

Uses system Python 3.12 with pip. Dependencies are in `requirements.txt` (Django 5.2, psycopg with binary). Install with:

```bash
pip install -r requirements.txt
```

### Database

PostgreSQL 16 runs on localhost:5432. Credentials are in `settings.py` (overridable via env vars): user `postgres`, password `80ligomA`, database `restaurant`. Start PostgreSQL before running the app:

```bash
sudo pg_ctlcluster 16 main start
```

All business models have `managed = False`; their tables must be created externally (see setup below). The `restaurante` app intentionally has **no migrations directory** — the custom test runner (`ManagedModelTestRunner`) handles table creation for tests via syncdb.

### Running the dev server

```bash
python3 manage.py runserver 0.0.0.0:8000
```

Admin is at `/admin/` (superuser: `admin` / `admin123`).

### Running tests

```bash
python3 manage.py test restaurante.tests
```

Known pre-existing issues (not caused by the environment):
- 7 test errors due to tests expecting pre-populated fixture data (records with specific IDs like `a.get(1)`).
- 1 test failure (`test_regmas_ped_many_rm`) — assertion logic issue.

These are code-level issues, not environment issues. 15/23 tests pass successfully.

### Linting

No linter is configured in the project.

### Key gotchas

- The `restaurante` app must NOT have a `migrations/` directory. The custom `ManagedModelTestRunner` in `test_settings.py` temporarily marks unmanaged models as managed so Django's syncdb creates tables in the test database.
- PostgreSQL sequences (`"TableName_ID_seq"`) must exist for models using `pgSQL_Utils.prefetch_id()`.
- The unmanaged business tables and sequences for the dev database are created via a one-time Python setup script (not Django migrations).
- `restaurante/admin.py` registers only `ClaveFolio` in Django admin.
- `manage.py` correctly sets `DJANGO_SETTINGS_MODULE=restaurante.settings`.
