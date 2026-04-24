"""配送ステータスページテスト"""

from unittest.mock import MagicMock, patch


class TestShowDeliveryStatus:
    @patch("src.pages.manager_delivery._show_deliveries")
    @patch("src.pages.manager_delivery.st")
    def test_renders_tabs(self, mock_st, mock_show):
        from src.pages.manager_delivery import show_delivery_status

        mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock()]
        show_delivery_status(MagicMock())
        assert mock_show.call_count == 3


class TestShowDeliveries:
    @patch("src.pages.manager_delivery.show_empty_state")
    @patch("src.pages.manager_delivery.get_deliveries", return_value=[])
    @patch("src.pages.manager_delivery.show_loading")
    @patch("src.pages.manager_delivery.st")
    def test_empty(self, mock_st, mock_loading, mock_get, mock_empty):
        from src.pages.manager_delivery import _show_deliveries

        mock_loading.return_value.__enter__ = MagicMock()
        mock_loading.return_value.__exit__ = MagicMock(return_value=False)

        _show_deliveries(MagicMock(), "未配送")
        mock_empty.assert_called_once()

    @patch(
        "src.pages.manager_delivery.get_deliveries",
        return_value=[
            {
                "DELIVERY_ID": 1,
                "STORE_NAME": "ラーメン〇〇店",
                "DRIVER_NAME": "佐藤",
                "SCHEDULED_AT": "10:00",
            }
        ],
    )
    @patch("src.pages.manager_delivery.show_loading")
    @patch("src.pages.manager_delivery.st")
    def test_pending_deliveries(self, mock_st, mock_loading, mock_get):
        from src.pages.manager_delivery import _show_deliveries

        mock_loading.return_value.__enter__ = MagicMock()
        mock_loading.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.container.return_value.__enter__ = MagicMock()
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        _show_deliveries(MagicMock(), "未配送")
        mock_st.warning.assert_called_once_with("未配送", icon="📦")

    @patch(
        "src.pages.manager_delivery.get_deliveries",
        return_value=[
            {
                "DELIVERY_ID": 2,
                "STORE_NAME": "ラーメン△△店",
                "DRIVER_NAME": "佐藤",
                "SCHEDULED_AT": "14:00",
            }
        ],
    )
    @patch("src.pages.manager_delivery.show_loading")
    @patch("src.pages.manager_delivery.st")
    def test_in_transit_deliveries(self, mock_st, mock_loading, mock_get):
        from src.pages.manager_delivery import _show_deliveries

        mock_loading.return_value.__enter__ = MagicMock()
        mock_loading.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.container.return_value.__enter__ = MagicMock()
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        _show_deliveries(MagicMock(), "配送中")
        mock_st.info.assert_called_once_with("配送中", icon="🚚")

    @patch(
        "src.pages.manager_delivery.get_deliveries",
        return_value=[
            {
                "DELIVERY_ID": 3,
                "STORE_NAME": "ラーメン□□店",
                "DRIVER_NAME": "田中",
                "SCHEDULED_AT": "16:00",
            }
        ],
    )
    @patch("src.pages.manager_delivery.show_loading")
    @patch("src.pages.manager_delivery.st")
    def test_completed_deliveries(self, mock_st, mock_loading, mock_get):
        from src.pages.manager_delivery import _show_deliveries

        mock_loading.return_value.__enter__ = MagicMock()
        mock_loading.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.container.return_value.__enter__ = MagicMock()
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        _show_deliveries(MagicMock(), "配送完了")
        mock_st.success.assert_called_once_with("完了", icon="✅")
