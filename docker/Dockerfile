# ============================================
# Stage 1: Frontend ビルド
# ============================================
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ============================================
# Stage 2: Backend + Nginx
# ============================================
FROM python:3.11-slim

LABEL maintainer="forgevision" \
      version="2.0.0" \
      description="Ramen Logistics Management System"

# Nginx + curl (ヘルスチェック用) インストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx curl && \
    rm -rf /var/lib/apt/lists/*

# 非rootユーザー作成
RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

# Python 依存関係
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# アプリケーションコード
COPY backend/ ./backend/
COPY src/ ./src/

# Frontend ビルド成果物
COPY --from=frontend-build /app/frontend/dist /usr/share/nginx/html

# Nginx 設定
COPY docker/nginx.conf /etc/nginx/nginx.conf

# ログ・PID ディレクトリの権限調整
RUN mkdir -p /var/log/nginx /var/lib/nginx /tmp/nginx && \
    chown -R app:app /var/log/nginx /var/lib/nginx /tmp/nginx /usr/share/nginx/html && \
    chown app:app /var/run

# 起動スクリプト
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER app

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
