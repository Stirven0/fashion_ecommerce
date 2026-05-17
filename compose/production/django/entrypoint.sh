#!/usr/bin/env sh
set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" >/dev/null 2>&1; do
  sleep 1
done
echo "PostgreSQL ready."

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear --ignore *.scss

exec "$@"
