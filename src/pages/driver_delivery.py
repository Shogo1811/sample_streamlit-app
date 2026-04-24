"""ドライバー画面: 配送リスト・完了報告（FR-11〜FR-13）
スマートフォン最適化: 単一カラム + 大型ボタン
"""

import streamlit as st
from snowflake.snowpark import Session

from src.components.common import show_empty_state, show_error_write, show_loading
from src.dal.delivery import complete_delivery, get_driver_deliveries
from src.utils.constants import DELIVERY_STATUS_COMPLETED, DELIVERY_STATUS_IN_TRANSIT

# スマートフォン最適化CSS（NFR-03c: 最小768px対応）
_MOBILE_CSS = """
<style>
@media (max-width: 768px) {
    .main .block-container { max-width: 100%; padding: 0.5rem 1rem; }
    .stButton > button { min-height: 48px; font-size: 1.1rem; }
}
</style>
"""


def show_driver_page(session: Session, user_id: str, driver_name: str) -> None:
    """ドライバー配送画面"""
    st.markdown(_MOBILE_CSS, unsafe_allow_html=True)
    st.title(f"本日の配送 — {driver_name}さん")

    with show_loading():
        deliveries = get_driver_deliveries(session)

    if not deliveries:
        show_empty_state("本日の配送予定はありません。")
        return

    # 集計
    completed = sum(1 for d in deliveries if d["STATUS"] == DELIVERY_STATUS_COMPLETED)
    remaining = len(deliveries) - completed
    st.markdown(f"完了: **{completed}** 件 / 残り: **{remaining}** 件")
    st.divider()

    # 配送リスト（単一カラム・縦スクロール）
    for d in deliveries:
        delivery_id = d["DELIVERY_ID"]
        is_completed = d["STATUS"] == DELIVERY_STATUS_COMPLETED
        is_in_transit = d["STATUS"] == DELIVERY_STATUS_IN_TRANSIT

        with st.container(border=True):
            st.markdown(f"### {d['STORE_NAME']}")
            st.caption(f"予定: {d.get('SCHEDULED_AT', '-')}")

            if is_completed:
                st.success("配送完了", icon="✅")
            elif is_in_transit:
                # 配送中 → 配送完了ボタン
                if st.button(
                    "配送完了",
                    key=f"complete_{delivery_id}",
                    use_container_width=True,
                    type="primary",
                ):
                    _handle_complete(session, delivery_id, user_id)
            else:
                st.info("未配送", icon="📦")


def _handle_complete(session: Session, delivery_id: int, user_id: str) -> None:
    """配送完了処理（2段階確認 — Streamlit再実行モデル対応）"""
    confirm_key = f"confirm_complete_{delivery_id}"

    if confirm_key not in st.session_state:
        # Phase 1: 確認フラグをセットして再描画
        st.session_state[confirm_key] = True
        st.rerun()
    else:
        # Phase 2: 確認UIを表示
        st.warning("この配送を完了にしますか？")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("はい、完了", key=f"yes_{delivery_id}", use_container_width=True):
                result = complete_delivery(session, delivery_id, user_id)
                st.session_state.pop(confirm_key, None)
                if result.get("success"):
                    st.success("配送完了を報告しました。")
                    st.rerun()
                else:
                    show_error_write()
        with col2:
            if st.button("キャンセル", key=f"cancel_{delivery_id}", use_container_width=True):
                st.session_state.pop(confirm_key, None)
                st.rerun()
