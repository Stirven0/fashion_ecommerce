# AGENTS.md

## Project Overview

**fashion_store** — Tienda de moda online construida con Cookiecutter Django.

| Tool | Version |
|---|---|
| Django | 6.0.3 |
| Python | 3.14 |
| Package Manager | `uv` |

---

## Setup

```bash
cd /home/fashion_store
uv sync          # installs deps into .venv/
```

---

## Developer Commands

All commands must be prefixed with `uv run` (or activate `.venv` first):

```bash
uv run python manage.py runserver        # dev server (uses config.settings.local)
uv run python manage.py migrate          # run migrations
uv run python manage.py createsuperuser  # create admin user
```

---

## Settings Structure

Multi-file settings in `config/settings/`:
- **`local.py`** — default for `manage.py` (DEBUG=True, locmem cache, console email)
- **`test.py`** — used by pytest (MD5 passwords, locmem email, fast runner)
- **`production.py`** — production config
- **`base.py`** — shared base

Default `DJANGO_SETTINGS_MODULE` is `config.settings.local` (set in `manage.py`).

---

## Testing

```bash
uv run pytest                              # run all tests
uv run pytest fashion_store/users/tests/   # run tests for a specific app
uv run coverage run -m pytest && uv run coverage html  # coverage report
```

- Test settings: `config.settings.test` (passed via `--ds` in `pyproject.toml`)
- Uses `pytest-django`, `factory-boy`, `pytest-sugar`
- Fixtures in `fashion_store/conftest.py` (`user` fixture available)
- User factory at `fashion_store/users/tests/factories.py`
- Tests live **inside** the app dir (`fashion_store/users/tests/`) plus root `tests/`

---

## Lint / Format / Typecheck

```bash
uv run ruff check .      # lint (auto-fix: ruff check --fix .)
uv run ruff format .     # format
uv run mypy fashion_store  # type check
uv run djlint .          # template lint
```

Pre-commit runs: ruff (check + format), djlint, django-upgrade (target 6.0), pyproject-fmt.

---

## Key Conventions

- **Single-line isort** enforced (`force-single-line = true` in ruff config)
- **Ruff rules**: extensive set including Django-specific (`DJ`), flake8-bugbear (`B`), pylint (`PL`), and more
- **Ignored Ruff rules**: `RUF012` (mutable class attrs), `S101` (assert), `SIM102` (nested ifs)
- **Timezone**: `America/Bogota`
- **Language**: `en-us` (README/docs in Spanish)
- **Env loading**: uses `django-environ`; `.env` only read if `DJANGO_READ_DOT_ENV_FILE=True`
- Env files live in `.envs/.local/` and `.envs/.production/`
- **Database**: PostgreSQL by default (env var `DATABASE_URL`); test uses SQLite via env override
- **Cache**: locmem in local/test, Redis in production

---

## Directory Ownership

- `config/` — Django settings, URLs, WSGI
- `fashion_store/` — main Django app package (users, templates, static, contrib)
- `fashion_store/users/` — custom user model + auth (allauth integration)
- `tests/` — root-level tests (currently only `test_merge_production_dotenvs_in_dotenv.py`)
- `docs/` — Sphinx documentation
- `locale/` — i18n translations

---

## Rules for Agents

1. **Package manager**: Always use `uv`, not `pip`.
2. **Lint before commit**: Run `uv run ruff check --fix . && uv run ruff format .`
3. **Migrations**: Excluded from ruff linting and mypy — do not lint them manually.
4. **Python version**: Requires Python 3.14 exactly.
5. **Working directory**: Project root is `/home/fashion_store/`.
