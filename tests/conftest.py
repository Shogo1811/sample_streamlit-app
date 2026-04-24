"""pytestフィクスチャ定義"""

from unittest.mock import MagicMock

import pytest


def pytest_collection_modifyitems(items):
    """ディレクトリベースの自動マーカー付与"""
    for item in items:
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


class MockRow:
    """Snowpark Rowのモック（dict/index両アクセス対応）"""

    def __init__(self, data: dict):
        self._data = data
        self._values = list(data.values())

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._values[key]
        return self._data[key]

    def as_dict(self):
        return dict(self._data)


def make_mock_df(rows: list[dict]):
    """チェーン可能なモックDataFrameを作成"""
    mock_df = MagicMock()
    mock_rows = [MockRow(r) for r in rows]
    mock_df.filter.return_value = mock_df
    mock_df.select.return_value = mock_df
    mock_df.join.return_value = mock_df
    mock_df.sort.return_value = mock_df
    mock_df.distinct.return_value = mock_df
    mock_df.limit.return_value = mock_df
    mock_df.collect.return_value = mock_rows
    return mock_df


@pytest.fixture(autouse=True)
def _clear_st_cache():
    """テスト間でStreamlitキャッシュをクリア"""
    yield
    try:
        import streamlit as st

        st.cache_data.clear()
    except Exception:  # noqa: S110
        pass


@pytest.fixture
def mock_session():
    """Snowpark Sessionのモック"""
    return MagicMock()
