#!/bin/sh

set -ux

if [ -z "${DATABASE_PATH:-}" ]; then
    echo "DATABSE_PATH is not set. Exiting..."
    exit 1
fi

if [ -z "${GUNICORN_PORT:-}" ]; then
    echo "DATABSE_PATH is not set. Exiting..."
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
.venv/bin/gunicorn -b "0.0.0.0:${GUNICORN_PORT}" wsgi:app
