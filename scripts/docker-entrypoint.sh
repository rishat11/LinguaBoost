#!/bin/sh
set -e
cd /app
mkdir -p /app/data
alembic upgrade head
exec uvicorn linguaboost.app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
