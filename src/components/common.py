"""共通UIコンポーネント（ローディング、空状態、エラー表示）"""

import streamlit as st


def show_loading(message: str = "データを読み込んでいます..."):
    """ローディング表示（NFR-01: コールドスタート時st.spinner）"""
    return st.spinner(message)


def show_empty_state(message: str = "データがありません。"):
    """空状態表示"""
    st.info(message)


def show_error_connection():
    """Snowflake接続エラー（NFR-19）"""
    st.error("サーバーへの接続に失敗しました。しばらく待ってから再試行してください。")
    if st.button("再試行", key="retry_connection"):
        st.rerun()


def show_error_timeout():
    """クエリタイムアウト（NFR-20）"""
    st.warning("データ取得に時間がかかっています。フィルタ条件を絞り込んでお試しください。")


def show_error_permission():
    """権限不足（NFR-21）"""
    st.error("この操作を行う権限がありません。管理者にお問い合わせください。")


def show_error_write(retry_callback=None):
    """データ書き込み失敗（NFR-22: session_state一時保存+リトライ）"""
    st.error("データの保存に失敗しました。")
    if retry_callback and st.button("再試行", key="retry_write"):
        retry_callback()
