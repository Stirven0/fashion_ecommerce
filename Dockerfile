FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev --no-editable

FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.production

EXPOSE 8000

RUN groupadd -r django && useradd -r -g django django

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY . .

RUN mkdir -p /app/media /app/staticfiles && \
    chown -R django:django /app/media /app/staticfiles

USER django

ENTRYPOINT ["/app/compose/production/django/entrypoint.sh"]
CMD ["/app/compose/production/django/start.sh"]
