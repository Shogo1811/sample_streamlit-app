"""在庫データアクセスモジュール"""

import streamlit as st
from snowflake.snowpark import Session

from src.utils.constants import CACHE_TTL_DASHBOARD, CACHE_TTL_MASTER


@st.cache_data(ttl=CACHE_TTL_MASTER)
def get_ingredients(_session: Session) -> list[dict]:
    """食材マスタ取得"""
    df = _session.table("APP.INGREDIENTS").select("INGREDIENT_ID", "INGREDIENT_NAME", "CATEGORY", "UNIT", "THRESHOLD")
    return [row.as_dict() for row in df.collect()]


@st.cache_data(ttl=CACHE_TTL_MASTER)
def get_categories(_session: Session) -> list[str]:
    """食材カテゴリ一覧取得（フィルタ用）"""
    df = _session.table("APP.INGREDIENTS").select("CATEGORY").distinct()
    return [row["CATEGORY"] for row in df.collect()]


@st.cache_data(ttl=CACHE_TTL_DASHBOARD)
def get_inventory(_session: Session) -> list[dict]:
    """在庫データ取得（RAPにより自店舗のみ自動フィルタ）"""
    inv = _session.table("APP.INVENTORY")
    ing = _session.table("APP.INGREDIENTS")
    df = inv.join(ing, on="INGREDIENT_ID").select(
        inv["STORE_ID"],
        ing["INGREDIENT_NAME"],
        ing["CATEGORY"],
        inv["CURRENT_QUANTITY"],
        ing["THRESHOLD"],
        ing["UNIT"],
        inv["UPDATED_AT"],
    )
    return [row.as_dict() for row in df.collect()]


@st.cache_data(ttl=CACHE_TTL_DASHBOARD)
def get_low_stock_items(_session: Session) -> list[dict]:
    """閾値以下の食材取得（アラート用）"""
    inv = _session.table("APP.INVENTORY")
    ing = _session.table("APP.INGREDIENTS")
    df = (
        inv.join(ing, on="INGREDIENT_ID")
        .filter(inv["CURRENT_QUANTITY"] <= ing["THRESHOLD"])
        .select(
            ing["INGREDIENT_NAME"],
            ing["CATEGORY"],
            inv["CURRENT_QUANTITY"],
            ing["THRESHOLD"],
            ing["UNIT"],
        )
    )
    return [row.as_dict() for row in df.collect()]
