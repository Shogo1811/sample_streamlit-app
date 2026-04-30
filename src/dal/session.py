"""Snowparkセッション管理（Container Services / ローカル両対応）"""

import os
import threading

from snowflake.snowpark import Session

_lock = threading.Lock()
_session: Session | None = None


def _get_connection_params() -> dict:
    """環境変数から接続パラメータを取得"""
    account = os.environ.get("SNOWFLAKE_ACCOUNT", "")
    user = os.environ.get("SNOWFLAKE_USER", "")
    password = os.environ.get("SNOWFLAKE_PASSWORD", "")
    private_key_path = os.environ.get("SNOWFLAKE_PRIVATE_KEY_PATH", "")
    database = os.environ.get("SNOWFLAKE_DATABASE", "")
    warehouse = os.environ.get("SNOWFLAKE_WAREHOUSE", "")

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
        "schema": os.environ.get("SNOWFLAKE_SCHEMA", "APP"),
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
