"""発注提案データアクセスモジュール"""

import json

import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, lit

from src.utils.constants import CACHE_TTL_DASHBOARD


def _parse_sp_result(result) -> dict:
    """SP戻り値をパース（VARIANT型のJSON文字列対応）"""
    if not result:
        return {"success": False, "message": "SP呼出エラー"}
    raw = result[0][0]
    if isinstance(raw, str):
        return json.loads(raw)
    return raw


@st.cache_data(ttl=CACHE_TTL_DASHBOARD)
def get_proposals(_session: Session, status_filter: str | None = None) -> list[dict]:
    """発注提案リスト取得（RAPにより自店舗のみ）"""
    df = (
        _session.table("APP.ORDER_PROPOSALS")
        .join(_session.table("APP.INGREDIENTS"), on="INGREDIENT_ID")
        .select(
            col("PROPOSAL_ID"),
            col("INGREDIENT_NAME"),
            col("CATEGORY"),
            col("RECOMMENDED_QUANTITY"),
            col("REASON"),
            col("ORDER_PROPOSALS.STATUS"),
            col("ORDER_PROPOSALS.CREATED_AT"),
        )
    )
    if status_filter:
        df = df.filter(col("ORDER_PROPOSALS.STATUS") == lit(status_filter))
    return [row.as_dict() for row in df.collect()]


def approve_proposal(session: Session, proposal_id: int, quantity: int, user_id: str) -> dict:
    """発注提案の承認（SP経由）"""
    result = session.sql(
        "CALL APP.SP_APPROVE_ORDER_PROPOSAL(?, ?, ?)",
        params=[proposal_id, quantity, user_id],
    ).collect()
    st.cache_data.clear()
    return _parse_sp_result(result)


def reject_proposal(session: Session, proposal_id: int, user_id: str) -> dict:
    """発注提案の却下（SP経由）"""
    result = session.sql(
        "CALL APP.SP_REJECT_ORDER_PROPOSAL(?, ?)",
        params=[proposal_id, user_id],
    ).collect()
    st.cache_data.clear()
    return _parse_sp_result(result)


@st.cache_data(ttl=CACHE_TTL_DASHBOARD)
def get_order_plans(_session: Session) -> list[dict]:
    """承認済み発注予定リスト取得"""
    df = (
        _session.table("APP.ORDER_PLANS")
        .join(_session.table("APP.ORDER_PROPOSALS"), on="PROPOSAL_ID")
        .join(_session.table("APP.INGREDIENTS"), on="INGREDIENT_ID")
        .select(
            col("PLAN_ID"),
            col("INGREDIENT_NAME"),
            col("ORDER_PLANS.QUANTITY"),
            col("APPROVED_BY"),
            col("APPROVED_AT"),
        )
    )
    return [row.as_dict() for row in df.collect()]
