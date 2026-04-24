"""認証・ロール判定モジュール"""

import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

from src.utils.constants import CACHE_TTL_AUTH, ROLE_DRIVER, ROLE_MANAGER


@st.cache_data(ttl=CACHE_TTL_AUTH)
def get_current_user(_session: Session) -> str:
    """現在のログインユーザー名を取得"""
    result = _session.sql("SELECT CURRENT_USER()").collect()
    return result[0][0]


@st.cache_data(ttl=CACHE_TTL_AUTH)
def get_user_roles(_session: Session, user_id: str) -> list[dict]:
    """ユーザーの全ロールを取得（複数ロール対応）"""
    tbl = _session.table("APP.USER_ROLE_MAPPING")
    rows = tbl.filter(col("USER_ID") == user_id).collect()
    return [
        {
            "user_id": row["USER_ID"],
            "role_type": row["ROLE_TYPE"],
            "related_id": row["RELATED_ID"],
        }
        for row in rows
    ]


def is_manager(roles: list[dict]) -> bool:
    """店長ロールを持っているか"""
    return any(r["role_type"] == ROLE_MANAGER for r in roles)


def is_driver(roles: list[dict]) -> bool:
    """ドライバーロールを持っているか"""
    return any(r["role_type"] == ROLE_DRIVER for r in roles)


def check_consent(_session: Session, user_id: str, policy_version: str) -> bool:
    """最新の同意レコードを確認（REVOKE考慮・ポリシーバージョン照合）"""
    tbl = _session.table("AUDIT.CONSENT_RECORDS")
    df = (
        tbl.filter((col("USER_ID") == user_id) & (col("POLICY_VERSION") == policy_version))
        .sort(col("CONSENTED_AT").desc())
        .limit(1)
    )
    rows = df.collect()
    if not rows:
        return False
    return rows[0]["CONSENT_TYPE"] == "GRANT"


def record_consent(_session: Session, user_id: str, policy_version: str) -> None:
    """プライバシーポリシー同意を記録"""
    _session.sql(
        "INSERT INTO AUDIT.CONSENT_RECORDS (user_id, consent_type, policy_version) SELECT ?, 'GRANT', ?",
        params=[user_id, policy_version],
    ).collect()
