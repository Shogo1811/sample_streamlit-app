"""在庫データアクセスモジュール"""

import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

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
    df = (
        _session.table("APP.INVENTORY")
        .join(
            _session.table("APP.INGREDIENTS"),
            on="INGREDIENT_ID",
        )
        .select(
            col("INVENTORY.STORE_ID"),
            col("INGREDIENT_NAME"),
            col("CATEGORY"),
            col("CURRENT_QUANTITY"),
            col("THRESHOLD"),
            col("UNIT"),
            col("INVENTORY.UPDATED_AT"),
        )
    )
    return [row.as_dict() for row in df.collect()]


@st.cache_data(ttl=CACHE_TTL_DASHBOARD)
def get_low_stock_items(_session: Session) -> list[dict]:
    """閾値以下の食材取得（アラート用）"""
    df = (
        _session.table("APP.INVENTORY")
        .join(_session.table("APP.INGREDIENTS"), on="INGREDIENT_ID")
        .filter(col("CURRENT_QUANTITY") <= col("THRESHOLD"))
        .select(
            col("INGREDIENT_NAME"),
            col("CATEGORY"),
            col("CURRENT_QUANTITY"),
            col("THRESHOLD"),
            col("UNIT"),
        )
    )
    return [row.as_dict() for row in df.collect()]
