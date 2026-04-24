"""店長画面: 配送状況確認（FR-14）"""

import streamlit as st
from snowflake.snowpark import Session

from src.components.common import show_empty_state, show_loading
from src.dal.delivery import get_deliveries
from src.utils.constants import (
    DELIVERY_STATUS_COMPLETED,
    DELIVERY_STATUS_IN_TRANSIT,
    DELIVERY_STATUS_PENDING,
)


def show_delivery_status(session: Session) -> None:
    """配送状況ページ"""
    st.header("配送状況")

    tab_pending, tab_transit, tab_done = st.tabs(["未配送", "配送中", "配送完了"])

    with tab_pending:
        _show_deliveries(session, DELIVERY_STATUS_PENDING)

    with tab_transit:
        _show_deliveries(session, DELIVERY_STATUS_IN_TRANSIT)

    with tab_done:
        _show_deliveries(session, DELIVERY_STATUS_COMPLETED)


def _show_deliveries(session: Session, status: str) -> None:
    """ステータス別配送一覧"""
    with show_loading():
        deliveries = get_deliveries(session, status_filter=status)

    if not deliveries:
        show_empty_state(f"「{status}」の配送はありません。")
        return

    for d in deliveries:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**配送 #{d['DELIVERY_ID']}** → {d['STORE_NAME']}")
                st.caption(f"ドライバー: {d['DRIVER_NAME']} / 予定: {d.get('SCHEDULED_AT', '-')}")
            with col2:
                if status == DELIVERY_STATUS_COMPLETED:
                    st.success("完了", icon="✅")
                elif status == DELIVERY_STATUS_IN_TRANSIT:
                    st.info("配送中", icon="🚚")
                else:
                    st.warning("未配送", icon="📦")
