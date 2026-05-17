#!/usr/bin/env sh
set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" >/dev/null 2>&1; do
  sleep 1
done
echo "PostgreSQL ready."

exec "$@"
