"""認証・ロール判定モジュール（Azure AD 対応版）"""

from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

from src.utils.constants import ROLE_DRIVER, ROLE_MANAGER


def get_user_roles(session: Session, user_id: str) -> list[dict]:
    """ユーザーの全ロールを取得（複数ロール対応）

    user_id: Azure AD の oid（Object ID）
    """
    tbl = session.table("APP.USER_ROLE_MAPPING")
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


def get_store_id(roles: list[dict]) -> int | None:
    """店長ロールの store_id を取得"""
    for r in roles:
        if r["role_type"] == ROLE_MANAGER:
            return r["related_id"]
    return None


def get_driver_id(roles: list[dict]) -> int | None:
    """ドライバーロールの driver_id を取得"""
    for r in roles:
        if r["role_type"] == ROLE_DRIVER:
            return r["related_id"]
    return None


def check_consent(session: Session, user_id: str, policy_version: str) -> bool:
    """最新の同意レコードを確認（REVOKE考慮・ポリシーバージョン照合）"""
    tbl = session.table("AUDIT.CONSENT_RECORDS")
    df = (
        tbl.filter((col("USER_ID") == user_id) & (col("POLICY_VERSION") == policy_version))
        .sort(col("CONSENTED_AT").desc())
        .limit(1)
    )
    rows = df.collect()
    if not rows:
        return False
    return rows[0]["CONSENT_TYPE"] == "GRANT"


def record_consent(session: Session, user_id: str, policy_version: str) -> None:
    """プライバシーポリシー同意を記録"""
    session.sql(
        "INSERT INTO AUDIT.CONSENT_RECORDS (user_id, consent_type, policy_version) VALUES (?, 'GRANT', ?)",
        params=[user_id, policy_version],
    ).collect()


def revoke_consent(session: Session, user_id: str, policy_version: str) -> None:
    """プライバシーポリシー同意を撤回"""
    session.sql(
        "INSERT INTO AUDIT.CONSENT_RECORDS (user_id, consent_type, policy_version) VALUES (?, 'REVOKE', ?)",
        params=[user_id, policy_version],
    ).collect()
