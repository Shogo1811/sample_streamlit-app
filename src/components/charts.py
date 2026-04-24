"""グラフ・チャートコンポーネント（Altair使用 — SiS標準対応）"""

import altair as alt
import pandas as pd
import streamlit as st

# CUD推奨カラーパレット（色覚多様性配慮 — NFR-03a）
COLOR_PALETTE = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00"]


def inventory_bar_chart(data: list[dict]) -> None:
    """在庫状況棒グラフ（FR-01）"""
    if not data:
        return
    df = pd.DataFrame(data)
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("INGREDIENT_NAME:N", title="食材"),
            y=alt.Y("CURRENT_QUANTITY:Q", title="在庫数"),
            color=alt.Color(
                "CATEGORY:N",
                title="カテゴリ",
                scale=alt.Scale(range=COLOR_PALETTE),
            ),
            tooltip=["INGREDIENT_NAME", "CURRENT_QUANTITY", "THRESHOLD", "UNIT"],
        )
        .properties(height=400)
    )
    st.altair_chart(chart, use_container_width=True)


def inventory_trend_chart(data: list[dict]) -> None:
    """在庫推移時系列グラフ（FR-02）"""
    if not data:
        return
    df = pd.DataFrame(data)
    chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X("UPDATED_AT:T", title="日時"),
            y=alt.Y("CURRENT_QUANTITY:Q", title="在庫数"),
            color=alt.Color(
                "INGREDIENT_NAME:N",
                title="食材",
                scale=alt.Scale(range=COLOR_PALETTE),
            ),
            tooltip=["INGREDIENT_NAME", "CURRENT_QUANTITY", "UPDATED_AT"],
        )
        .properties(height=400)
    )
    st.altair_chart(chart, use_container_width=True)
