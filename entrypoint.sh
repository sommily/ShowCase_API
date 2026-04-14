#!/bin/bash
set -e

echo "[INFO] 收集静态文件..."
python manage.py collectstatic --noinput

echo "[INFO] 启动 Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
