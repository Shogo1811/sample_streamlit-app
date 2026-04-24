"""Snowparkセッション管理（SiS環境対応）"""

import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session


@st.cache_resource
def get_session() -> Session:
    """SiS環境のアクティブセッションを取得しキャッシュする"""
    return get_active_session()
