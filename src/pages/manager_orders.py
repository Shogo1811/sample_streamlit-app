"""店長画面: 発注提案・承認（FR-06〜FR-10）"""

import streamlit as st
from snowflake.snowpark import Session

from src.components.common import show_empty_state, show_error_write, show_loading
from src.dal.orders import approve_proposal, get_order_plans, get_proposals, reject_proposal
from src.utils.constants import PROPOSAL_STATUS_REVIEWING
from src.utils.validators import ValidationError, validate_order_quantity


def show_orders(session: Session, user_id: str) -> None:
    """発注提案・承認ページ"""
    st.header("発注提案")

    tab_proposals, tab_plans = st.tabs(["発注提案リスト", "承認済み発注予定"])

    with tab_proposals:
        _show_proposals(session, user_id)

    with tab_plans:
        _show_plans(session)


def _show_proposals(session: Session, user_id: str) -> None:
    """発注提案リスト（FR-06〜FR-09）"""
    with show_loading():
        proposals = get_proposals(session, status_filter=PROPOSAL_STATUS_REVIEWING)

    if not proposals:
        show_empty_state("確認待ちの発注提案はありません。")
        return

    for proposal in proposals:
        pid = proposal["PROPOSAL_ID"]
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{proposal['INGREDIENT_NAME']}**（{proposal['CATEGORY']}）")
                st.caption(f"発注理由: {proposal.get('REASON', '-')}")
            with col2:
                st.metric("推奨数量", proposal["RECOMMENDED_QUANTITY"])

            # 数量入力 + 承認/却下ボタン
            quantity = st.number_input(
                "発注数量",
                min_value=1,
                max_value=10000,
                value=int(proposal["RECOMMENDED_QUANTITY"]),
                key=f"qty_{pid}",
                help="1〜10,000の整数で入力してください",
            )

            col_approve, col_reject = st.columns(2)
            with col_approve:
                if st.button("承認", key=f"approve_{pid}", use_container_width=True):
                    _handle_approve(session, pid, quantity, user_id)
            with col_reject:
                if st.button("却下", key=f"reject_{pid}", use_container_width=True):
                    _handle_reject(session, pid, user_id)


def _handle_approve(session: Session, proposal_id: int, quantity: int, user_id: str) -> None:
    """承認処理（2段階確認 — Streamlit再実行モデル対応）"""
    try:
        qty = validate_order_quantity(quantity)
    except ValidationError as e:
        st.error(e.message)
        return

    confirm_key = f"confirm_approve_{proposal_id}"
    qty_key = f"confirm_qty_{proposal_id}"

    if confirm_key not in st.session_state:
        # Phase 1: 確認フラグをセットして再描画
        st.session_state[confirm_key] = True
        st.session_state[qty_key] = qty
        st.rerun()
    else:
        # Phase 2: 確認UIを表示
        saved_qty = st.session_state.get(qty_key, qty)
        st.warning(f"**{saved_qty}** 個で承認しますか？")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("確定する", key=f"confirm_{proposal_id}", use_container_width=True):
                result = approve_proposal(session, proposal_id, saved_qty, user_id)
                st.session_state.pop(confirm_key, None)
                st.session_state.pop(qty_key, None)
                if result.get("success"):
                    st.success("承認しました。")
                    st.rerun()
                else:
                    show_error_write()
        with col2:
            if st.button("キャンセル", key=f"cancel_approve_{proposal_id}", use_container_width=True):
                st.session_state.pop(confirm_key, None)
                st.session_state.pop(qty_key, None)
                st.rerun()


def _handle_reject(session: Session, proposal_id: int, user_id: str) -> None:
    """却下処理"""
    result = reject_proposal(session, proposal_id, user_id)
    if result.get("success"):
        st.success("却下しました。")
        st.rerun()
    else:
        show_error_write()


def _show_plans(session: Session) -> None:
    """承認済み発注予定リスト（FR-10）"""
    with show_loading():
        plans = get_order_plans(session)

    if not plans:
        show_empty_state("承認済みの発注予定はありません。")
        return

    for plan in plans:
        with st.container(border=True):
            st.markdown(f"**{plan['INGREDIENT_NAME']}** — {plan['QUANTITY']} 個")
            st.caption(f"承認者: {plan['APPROVED_BY']} / {plan['APPROVED_AT']}")
