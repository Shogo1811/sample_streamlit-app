"""在庫アラートコンポーネント（FR-05）"""

import streamlit as st


def show_low_stock_alerts(items: list[dict]) -> None:
    """閾値以下の食材をアラート表示"""
    if not items:
        return
    st.warning(f"在庫が閾値を下回っている食材が {len(items)} 件あります")
    for item in items:
        st.markdown(
            f"- **{item['INGREDIENT_NAME']}**（{item['CATEGORY']}）: "
            f"現在 {item['CURRENT_QUANTITY']}{item['UNIT']} "
            f"/ 閾値 {item['THRESHOLD']}{item['UNIT']}"
        )
