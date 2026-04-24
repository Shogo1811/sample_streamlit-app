"""配送データアクセスモジュール

キャッシュ方針: 配送データはリアルタイム性が重要なため、意図的にキャッシュを適用しない。
配送完了等の書き込み操作後は他モジュールのキャッシュをクリアして整合性を保つ。
"""

import json

import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, lit


def _parse_sp_result(result) -> dict:
    """SP戻り値をパース（VARIANT型のJSON文字列対応）"""
    if not result:
        return {"success": False, "message": "SP呼出エラー"}
    raw = result[0][0]
    if isinstance(raw, str):
        return json.loads(raw)
    return raw


def get_deliveries(session: Session, status_filter: str | None = None) -> list[dict]:
    """配送一覧取得（RAPにより自動フィルタ）"""
    df = (
        session.table("APP.DELIVERIES")
        .join(session.table("APP.STORES"), on="STORE_ID")
        .join(session.table("APP.DRIVERS"), on="DRIVER_ID")
        .select(
            col("DELIVERY_ID"),
            col("STORE_NAME"),
            col("DRIVER_NAME"),
            col("DELIVERIES.STATUS"),
            col("SCHEDULED_AT"),
            col("COMPLETED_AT"),
        )
    )
    if status_filter:
        df = df.filter(col("DELIVERIES.STATUS") == lit(status_filter))
    return [row.as_dict() for row in df.collect()]


def get_driver_deliveries(session: Session) -> list[dict]:
    """ドライバー向け配送リスト取得（RAPにより自分の担当のみ）"""
    df = (
        session.table("APP.DELIVERIES")
        .join(session.table("APP.STORES"), on="STORE_ID")
        .select(
            col("DELIVERY_ID"),
            col("STORE_NAME"),
            col("DELIVERIES.STATUS"),
            col("SCHEDULED_AT"),
        )
        .sort(col("SCHEDULED_AT"))
    )
    return [row.as_dict() for row in df.collect()]


def complete_delivery(session: Session, delivery_id: int, user_id: str) -> dict:
    """配送完了報告（SP経由）"""
    result = session.sql(
        "CALL APP.SP_COMPLETE_DELIVERY(?, ?)",
        params=[delivery_id, user_id],
    ).collect()
    st.cache_data.clear()
    return _parse_sp_result(result)
