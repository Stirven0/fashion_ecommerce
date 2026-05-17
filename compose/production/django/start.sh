#!/usr/bin/env sh
set -e

exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-4}" \
  --timeout "${GUNICORN_TIMEOUT:-120}" \
  --log-level "${GUNICORN_LOG_LEVEL:-info}" \
  --access-logfile - \
  --error-logfile -
