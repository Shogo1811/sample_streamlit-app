# Backend コード生成計画

## 生成ファイル一覧

### 1. DAL層の移行（src/dal/ の修正）
- [x] `src/dal/session.py` — サービスアカウント接続（環境変数ベース）
- [x] `src/dal/auth.py` — Azure AD oid ベースに変更、st依存除去
- [x] `src/dal/inventory.py` — st.cache_data 除去
- [x] `src/dal/orders.py` — st.cache_data 除去
- [x] `src/dal/delivery.py` — st依存除去

### 2. FastAPI アプリケーション（backend/ 新規）
- [x] `backend/app/__init__.py`
- [x] `backend/app/main.py` — FastAPI エントリポイント、CORS、lifespan
- [x] `backend/app/config.py` — 環境変数設定（pydantic-settings）
- [x] `backend/app/schemas.py` — Pydantic レスポンス/リクエストモデル
- [x] `backend/app/dependencies.py` — DI（セッション、現在ユーザー）
- [x] `backend/app/auth.py` — Azure AD JWT 検証、ロールマッピング
- [x] `backend/app/routers/__init__.py`
- [x] `backend/app/routers/auth_router.py` — 認証エンドポイント
- [x] `backend/app/routers/inventory_router.py` — 在庫エンドポイント
- [x] `backend/app/routers/orders_router.py` — 発注エンドポイント
- [x] `backend/app/routers/delivery_router.py` — 配送エンドポイント

### 3. テスト（backend/tests/ 新規）
- [x] `backend/tests/__init__.py`
- [x] `backend/tests/conftest.py` — テストフィクスチャ
- [x] `backend/tests/test_auth.py` — 認証テスト
- [x] `backend/tests/test_inventory.py` — 在庫APIテスト
- [x] `backend/tests/test_orders.py` — 発注APIテスト
- [x] `backend/tests/test_delivery.py` — 配送APIテスト

### 4. 設定ファイル
- [x] `backend/requirements.txt` — Python 依存関係
- [x] `backend/pyproject.toml` — リンター・テスト設定
