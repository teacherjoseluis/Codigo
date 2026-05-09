# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

Django 1.8 restaurant management system ("Sistema de Restaurante") on Python 3.5. Single Django app (`restaurante`) with a Repository/Factory pattern layer on top of auto-generated (unmanaged) PostgreSQL models.

### Python environment

A conda environment `django18` provides Python 3.5.6 with Django 1.8.19 and psycopg2-binary 2.7.7. Activate it before any Django command:

```bash
export PATH="$HOME/miniconda3/bin:$PATH"
eval "$(conda shell.bash hook)"
conda activate django18
```

### Critical: DJANGO_SETTINGS_MODULE

`manage.py` and `wsgi.py` reference a non-existent `restaurante.settings0` module. Always set the env var before running Django commands:

```bash
export DJANGO_SETTINGS_MODULE=restaurante.settings
```

### Lib.abc shim

`Ubicacion_repository.py` uses `from Lib.abc import ABCMeta` (Windows-style import). A shim package is installed in the conda environment's site-packages to make this work on Linux.

### Database

PostgreSQL 16 runs on localhost:5432. Credentials are hardcoded in `settings.py`: user `postgres`, password `80ligomA`, database `restaurant`. All business models have `managed = False`; their tables are created via a one-time setup script, not Django migrations.

### Running the dev server

```bash
DJANGO_SETTINGS_MODULE=restaurante.settings python manage.py runserver 0.0.0.0:8000
```

Admin is at `/admin/` (superuser: `admin` / `admin123`).

### Running tests

```bash
DJANGO_SETTINGS_MODULE=restaurante.settings python manage.py test restaurante.tests
```

Known pre-existing issues (not caused by the environment):
- 7 test errors due to tests expecting pre-populated fixture data (records with specific IDs).
- 1 test failure (`test_regmas_ped_many_rm`) — assertion logic issue.
- Teardown crash: `test_settings.py` uses MySQL syntax (`SHOW TABLES`) on PostgreSQL.

### Linting

No linter is configured in the project. The codebase targets Python 3.4/3.5; static analysis tools that require Python 3.6+ will not parse the code correctly.

### Key gotchas

- The only `managed = True` model is `ClaveFolio`; all others need tables created externally.
- PostgreSQL sequences (e.g., `"Tabla_ID_seq"`) must exist for models that use `pgSQL_Utils.prefetch_id()`.
- `restaurante/admin.py` registers `ClaveFolio` in Django admin for development visibility.
