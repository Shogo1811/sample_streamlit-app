"""Snowparkセッション管理（Container Services / ローカル両対応）"""

import threading

from snowflake.snowpark import Session

_lock = threading.Lock()
_session: Session | None = None


def _get_connection_params() -> dict:
    """設定から接続パラメータを取得"""
    from backend.app.config import settings

    account = settings.snowflake_account
    user = settings.snowflake_user
    password = settings.snowflake_password
    private_key_path = settings.snowflake_private_key_path
    database = settings.snowflake_database
    warehouse = settings.snowflake_warehouse

    if not account or not user or not database or not warehouse:
        msg = "SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_DATABASE, SNOWFLAKE_WAREHOUSE は必須です"
        raise ValueError(msg)
    if not password and not private_key_path:
        msg = "SNOWFLAKE_PASSWORD または SNOWFLAKE_PRIVATE_KEY_PATH のいずれかを設定してください"
        raise ValueError(msg)

    params = {
        "account": account,
        "user": user,
        "database": database,
        "schema": settings.snowflake_schema,
        "warehouse": warehouse,
    }
    if private_key_path:
        params["private_key_path"] = private_key_path
    else:
        params["password"] = password
    return params


def create_session() -> Session:
    """Snowparkセッションを作成"""
    return Session.builder.configs(_get_connection_params()).create()


def get_session() -> Session:
    """現在のセッションを返す（スレッドセーフ、接続切断時は再作成）"""
    global _session  # noqa: PLW0603
    with _lock:
        if _session is not None:
            try:
                _session.sql("SELECT 1").collect()
            except Exception:
                _session = None
        if _session is None:
            _session = create_session()
        return _session


def close_session() -> None:
    """セッションをクローズ"""
    global _session  # noqa: PLW0603
    with _lock:
        if _session is not None:
            _session.close()
            _session = None
