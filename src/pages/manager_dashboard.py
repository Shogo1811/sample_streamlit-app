"""店長画面: ダッシュボード（FR-01〜FR-05）"""

import streamlit as st
from snowflake.snowpark import Session

from src.components.alerts import show_low_stock_alerts
from src.components.charts import inventory_bar_chart, inventory_trend_chart
from src.components.common import show_empty_state, show_loading
from src.dal.inventory import get_categories, get_inventory, get_low_stock_items


def show_dashboard(session: Session) -> None:
    """ダッシュボードページ"""
    st.header("在庫ダッシュボード")

    # サイドバー: フィルタ（FR-04）
    with st.sidebar:
        st.subheader("フィルタ")
        categories = get_categories(session)
        selected_category = st.selectbox(
            "食材カテゴリ",
            options=["すべて"] + categories,
            help="表示する食材カテゴリを選択してください",
        )

    # メインエリア
    with show_loading():
        inventory_data = get_inventory(session)
        low_stock = get_low_stock_items(session)

    # カテゴリフィルタ適用
    if selected_category != "すべて":
        inventory_data = [item for item in inventory_data if item.get("CATEGORY") == selected_category]

    # 在庫アラート（FR-05）
    if low_stock:
        show_low_stock_alerts(low_stock)

    # 在庫状況グラフ（FR-01）
    st.subheader("在庫状況")
    if inventory_data:
        inventory_bar_chart(inventory_data)
    else:
        show_empty_state("在庫データがありません。")

    # 在庫推移グラフ（FR-02 — 履歴データ蓄積後にトレンド表示）
    st.subheader("在庫推移")
    if inventory_data:
        inventory_trend_chart(inventory_data)
    else:
        show_empty_state("在庫推移データがありません。")
