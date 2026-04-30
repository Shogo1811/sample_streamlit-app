#!/bin/bash
set -e

# FastAPI をバックグラウンドで起動
cd /app
python -m uvicorn backend.app.main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --workers "${UVICORN_WORKERS:-2}" &
UVICORN_PID=$!

# Nginx をバックグラウンドで起動
nginx -g "daemon off;" &
NGINX_PID=$!

# いずれかのプロセスが終了したらコンテナを停止
trap "kill $UVICORN_PID $NGINX_PID 2>/dev/null; exit" INT TERM

wait -n $UVICORN_PID $NGINX_PID 2>/dev/null || true
kill $UVICORN_PID $NGINX_PID 2>/dev/null || true
exit 1
