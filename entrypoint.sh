#!/bin/sh

set -ux

if [ -z "${DATABASE_PATH:-}" ]; then
    echo "DATABASE_PATH is not set. Exiting..."
    exit 1
fi

if [ -z "${GUNICORN_HOST:-}" ]; then
    echo "GUNICORN_HOST is not set. Exiting..."
    exit 1
fi

if [ -z "${GUNICORN_PORT:-}" ]; then
    echo "GUNICORN_PORT is not set. Exiting..."
    exit 1
fi

db_dir=$(dirname "$DATABASE_PATH")
if [ ! -d "${db_dir}" ]; then
    echo "Creating ${db_dir}..."
    mkdir -p "${db_dir}"
fi

echo "running migrations..."
.venv/bin/flask --app src db upgrade -d src/migrations
echo "starting..."
.venv/bin/gunicorn -b "${GUNICORN_HOST}:${GUNICORN_PORT}" wsgi:app
