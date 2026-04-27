"""発注提案データアクセスモジュール"""

import json

import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import lit

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
    op = _session.table("APP.ORDER_PROPOSALS")
    ing = _session.table("APP.INGREDIENTS")
    df = op.join(ing, on="INGREDIENT_ID").select(
        op["PROPOSAL_ID"],
        ing["INGREDIENT_NAME"],
        ing["CATEGORY"],
        op["RECOMMENDED_QUANTITY"],
        op["REASON"],
        op["STATUS"],
        op["CREATED_AT"],
    )
    if status_filter:
        df = df.filter(op["STATUS"] == lit(status_filter))
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
    op = _session.table("APP.ORDER_PLANS")
    pr = _session.table("APP.ORDER_PROPOSALS")
    ing = _session.table("APP.INGREDIENTS")
    df = (
        op.join(pr, on="PROPOSAL_ID")
        .join(ing, on="INGREDIENT_ID")
        .select(
            op["PLAN_ID"],
            ing["INGREDIENT_NAME"],
            op["QUANTITY"],
            op["APPROVED_BY"],
            op["APPROVED_AT"],
        )
    )
    return [row.as_dict() for row in df.collect()]
