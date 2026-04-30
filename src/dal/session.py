"""Snowparkセッション管理（Container Services / ローカル両対応）"""

import os
import threading

from snowflake.snowpark import Session

_lock = threading.Lock()
_session: Session | None = None


def _is_spcs() -> bool:
    """Snowflake Container Services 環境かどうかを判定"""
    return os.path.exists("/snowflake/session/token")


def _create_spcs_session() -> Session:
    """SPCS環境: OAuth トークンファイルで接続"""
    from backend.app.config import settings

    return Session.builder.configs(
        {
            "host": os.environ.get("SNOWFLAKE_HOST", ""),
            "account": os.environ.get("SNOWFLAKE_ACCOUNT", ""),
            "authenticator": "oauth",
            "token": open("/snowflake/session/token").read(),  # noqa: SIM115
            "database": settings.snowflake_database,
            "schema": settings.snowflake_schema,
            "warehouse": settings.snowflake_warehouse,
        }
    ).create()


def _create_local_session() -> Session:
    """ローカル環境: パスワード or キーペア認証で接続"""
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
    return Session.builder.configs(params).create()


def create_session() -> Session:
    """Snowparkセッションを作成（環境自動判定）"""
    if _is_spcs():
        return _create_spcs_session()
    return _create_local_session()


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
