#!/bin/sh
set -e

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"

echo "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT}..."
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; do
  sleep 2
done
echo "PostgreSQL is ready."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

WORKERS="${GUNICORN_WORKERS:-3}"
TIMEOUT="${GUNICORN_TIMEOUT:-60}"

if [ "$1" = "gunicorn" ]; then
  set -- gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "$WORKERS" \
    --timeout "$TIMEOUT"
fi

exec "$@"
