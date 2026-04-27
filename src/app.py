"""ラーメンチェーン食材自動発注システム — メインエントリーポイント"""

import streamlit as st

from src.components.common import show_error_connection, show_error_permission
from src.dal.auth import check_consent, get_current_user, get_user_roles, is_driver, is_manager
from src.dal.session import get_session
from src.pages.driver_delivery import show_driver_page
from src.pages.manager_dashboard import show_dashboard
from src.pages.manager_delivery import show_delivery_status
from src.pages.manager_orders import show_orders
from src.pages.privacy_consent import show_consent_page
from src.utils.constants import CURRENT_POLICY_VERSION

st.set_page_config(
    page_title="食材物流管理システム",
    page_icon="🍜",
    layout="wide",
)


def main():
    """アプリケーションメイン処理"""
    try:
        session = get_session()
        user_id = get_current_user(session)
    except Exception:
        show_error_connection()
        return

    # プライバシーポリシー同意チェック（ポリシーバージョン照合・REVOKE考慮）
    if not check_consent(session, user_id, CURRENT_POLICY_VERSION):
        show_consent_page(session, user_id)
        return

    # ロール判定
    roles = get_user_roles(session, user_id)
    if not roles:
        show_error_permission()
        return

    # ロール別画面ルーティング
    if is_manager(roles) and is_driver(roles):
        # 複数ロール: タブで切替
        tab_manager, tab_driver = st.tabs(["店長画面", "ドライバー画面"])
        with tab_manager:
            _show_manager_ui(session, user_id)
        with tab_driver:
            driver_name = _get_driver_name(roles)
            show_driver_page(session, user_id, driver_name)
    elif is_manager(roles):
        _show_manager_ui(session, user_id)
    elif is_driver(roles):
        driver_name = _get_driver_name(roles)
        show_driver_page(session, user_id, driver_name)
    else:
        show_error_permission()


def _show_manager_ui(session, user_id: str):
    """店長画面のサイドバーナビゲーション"""
    with st.sidebar:
        st.title("食材物流管理")
        page = st.radio(
            "メニュー",
            options=["ダッシュボード", "発注提案", "配送状況"],
            label_visibility="collapsed",
        )

    if page == "ダッシュボード":
        show_dashboard(session)
    elif page == "発注提案":
        show_orders(session, user_id)
    elif page == "配送状況":
        show_delivery_status(session)


def _get_driver_name(roles: list[dict]) -> str:
    """ドライバー名を取得（表示用）"""
    for r in roles:
        if r["role_type"] == "DRIVER":
            return r.get("user_id", "ドライバー")
    return "ドライバー"


if __name__ == "__main__":
    main()
