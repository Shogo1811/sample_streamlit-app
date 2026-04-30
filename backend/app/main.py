"""FastAPI メインアプリケーション"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from backend.app.config import settings
from backend.app.routers import auth_router, delivery_router, inventory_router, orders_router
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.dal.session import close_session, get_session
from src.utils.validators import ValidationError

logger = logging.getLogger("ramen-logistics")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """アプリケーションライフサイクル管理"""
    # 起動時: セッション初期化（get_session内で遅延作成）
    get_session()
    yield
    close_session()


app = FastAPI(
    title="ラーメン物流管理API",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# ValidationError ハンドラ
@app.exception_handler(ValidationError)
async def validation_error_handler(_request: Request, exc: ValidationError) -> JSONResponse:
    """バリデーションエラーを 422 で返す"""
    return JSONResponse(status_code=422, content={"detail": exc.message})


# 汎用例外ハンドラ（本番用）
@app.exception_handler(Exception)
async def generic_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """未処理例外を 500 で返す（スタックトレースは非公開）"""
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


# ルーター登録
app.include_router(auth_router.router)
app.include_router(inventory_router.router)
app.include_router(orders_router.router)
app.include_router(delivery_router.router)


@app.get("/health")
async def health_check():
    """ヘルスチェック（DB接続確認含む）"""
    try:
        get_session()
        return {"status": "ok"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "unhealthy"})
