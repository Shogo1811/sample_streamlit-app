"""SiS環境診断モード"""

import os
import sys

import streamlit as st

st.set_page_config(page_title="SiS診断", layout="wide")
st.title("SiS環境診断")

st.subheader("環境情報")
st.code(f"__file__: {__file__}")
st.code(f"cwd: {os.getcwd()}")
st.code(f"sys.path: {sys.path[:5]}")

st.subheader("ファイル構成")
try:
    cwd_files = os.listdir(".")
    st.write("カレントディレクトリ:", cwd_files)
except Exception as e:
    st.error(f"listdir error: {e}")

for d in ["src", "src/dal", "src/utils", "src/components", "dal", "utils", "components"]:
    try:
        files = os.listdir(d)
        st.success(f"{d}/: {files}")
    except Exception:
        st.warning(f"{d}/ — 見つかりません")

st.subheader("インポートテスト")
modules = [
    "src.utils.constants",
    "src.dal.session",
    "src.dal.auth",
    "src.components.common",
]
for mod in modules:
    try:
        __import__(mod)
        st.success(f"import {mod} — OK")
    except Exception as e:
        st.error(f"import {mod} — {type(e).__name__}: {e}")
