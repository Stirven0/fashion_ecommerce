---
name: qa-testing
description: |
  Run and interpret tests: pytest, ruff linting/formatting,
  mypy type checking, and djlint template validation.
license: MIT
compatibility: opencode
metadata:
  audience: developer
  workflow: testing
---

## Overview

Use this skill when the user asks to run tests, check code quality,
fix lint errors, or verify that changes don't break anything.

## Commands (prefix with `uv run`)

### Tests

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_qa.py -v

# Filter by test name
pytest tests/test_qa.py -k "Wishlist"

# Verbose output
pytest -v
```

Pytest is configured in `pyproject.toml` with:
- `--ds=config.settings.test` (Django settings)
- `--reuse-db` (keep test DB between runs)
- `--import-mode=importlib`

### Code Quality

```bash
# Lint + format check
ruff check . && ruff format .

# Auto-fix lint issues
ruff check --fix .

# Format in place
ruff format .
```

Ruff config in `pyproject.toml`:
- `force-single-line = true` (one import per line)
- Ignores: `RUF012`, `S101`, `SIM102`
- Excludes: `*/migrations/*.py`, `staticfiles/*`

### Type Checking

```bash
mypy fashion_store
```

Configured in `pyproject.toml`: Python 3.14, Django plugin, migrations excluded.

### Template Lint

```bash
djlint .
```

Configured in `pyproject.toml`: profile `django`, indent 2, max line 119,
ignores `H006`, `H030`, `H031`, `T002`.

## Test Structure

| File | What it tests |
|---|---|
| `tests/test_qa.py` | 50 QA tests (functional + non-functional) |
| `fashion_store/products/tests/` | Producst specific tests |

Test factories in `fashion_store/products/tests/factories.py` and
`fashion_store/users/tests/factories.py`.

Global fixture in `fashion_store/conftest.py`:
- `user` — creates a test user
- `_media_storage` (autouse) — sets MEDIA_ROOT to tmpdir

## QA Tests (tests/test_qa.py)

### Functional (5 classes)
| Test | Description |
|---|---|
| TestFunctionalCart | Add/remove/update cart items |
| TestFunctionalCheckout | Complete checkout flow order creation |
| TestFunctionalProduct | Product listing and filtering |
| TestFunctionalWishlist | Add/remove/view wishlist items |

### Non-Functional (5 classes)
| Test | Description |
|---|---|
| TestNonFunctionalPerformance | Page load times under 500ms |
| TestNonFunctionalQueryCount | Query count limits (≤15) |
| TestNonFunctionalSecurity | Auth protection, 404s, staff-only |
| TestNonFunctionalDataIntegrity | Unique constraints, defaults |
| TestNonFunctionalTemplateRendering | Page renders, nav links, store name |
