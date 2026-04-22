#!/bin/sh
set -e
cd /app
if [ -n "${DATABASE_URL:-}" ]; then
  alembic upgrade head
fi
exec uvicorn linguaboost.app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
