"""UIコンポーネントテスト"""

from unittest.mock import MagicMock, patch


class TestShowLowStockAlerts:
    @patch("src.components.alerts.st")
    def test_with_items(self, mock_st):
        from src.components.alerts import show_low_stock_alerts

        items = [
            {
                "INGREDIENT_NAME": "麺",
                "CATEGORY": "主食材",
                "CURRENT_QUANTITY": 10,
                "THRESHOLD": 20,
                "UNIT": "kg",
            }
        ]
        show_low_stock_alerts(items)
        mock_st.warning.assert_called_once()
        mock_st.markdown.assert_called_once()

    @patch("src.components.alerts.st")
    def test_empty_items(self, mock_st):
        from src.components.alerts import show_low_stock_alerts

        show_low_stock_alerts([])
        mock_st.warning.assert_not_called()

    @patch("src.components.alerts.st")
    def test_multiple_items(self, mock_st):
        from src.components.alerts import show_low_stock_alerts

        items = [
            {"INGREDIENT_NAME": "麺", "CATEGORY": "主食材", "CURRENT_QUANTITY": 10, "THRESHOLD": 20, "UNIT": "kg"},
            {"INGREDIENT_NAME": "ネギ", "CATEGORY": "トッピング", "CURRENT_QUANTITY": 3, "THRESHOLD": 5, "UNIT": "kg"},
        ]
        show_low_stock_alerts(items)
        assert mock_st.markdown.call_count == 2


class TestInventoryBarChart:
    @patch("src.components.charts.st")
    def test_with_data(self, mock_st):
        from src.components.charts import inventory_bar_chart

        data = [
            {"INGREDIENT_NAME": "麺", "CURRENT_QUANTITY": 50, "THRESHOLD": 20, "UNIT": "kg", "CATEGORY": "主食材"},
        ]
        inventory_bar_chart(data)
        mock_st.altair_chart.assert_called_once()

    @patch("src.components.charts.st")
    def test_empty_data(self, mock_st):
        from src.components.charts import inventory_bar_chart

        inventory_bar_chart([])
        mock_st.altair_chart.assert_not_called()


class TestInventoryTrendChart:
    @patch("src.components.charts.st")
    def test_with_data(self, mock_st):
        from src.components.charts import inventory_trend_chart

        data = [
            {"INGREDIENT_NAME": "麺", "CURRENT_QUANTITY": 50, "UPDATED_AT": "2026-04-23"},
        ]
        inventory_trend_chart(data)
        mock_st.altair_chart.assert_called_once()

    @patch("src.components.charts.st")
    def test_empty_data(self, mock_st):
        from src.components.charts import inventory_trend_chart

        inventory_trend_chart([])
        mock_st.altair_chart.assert_not_called()


class TestCommonComponents:
    @patch("src.components.common.st")
    def test_show_loading(self, mock_st):
        from src.components.common import show_loading

        show_loading("読み込み中...")
        mock_st.spinner.assert_called_once_with("読み込み中...")

    @patch("src.components.common.st")
    def test_show_loading_default(self, mock_st):
        from src.components.common import show_loading

        show_loading()
        mock_st.spinner.assert_called_once_with("データを読み込んでいます...")

    @patch("src.components.common.st")
    def test_show_empty_state(self, mock_st):
        from src.components.common import show_empty_state

        show_empty_state("データなし")
        mock_st.info.assert_called_once_with("データなし")

    @patch("src.components.common.st")
    def test_show_error_connection(self, mock_st):
        from src.components.common import show_error_connection

        mock_st.button.return_value = False
        show_error_connection()
        mock_st.error.assert_called_once()

    @patch("src.components.common.st")
    def test_show_error_connection_retry(self, mock_st):
        from src.components.common import show_error_connection

        mock_st.button.return_value = True
        show_error_connection()
        mock_st.rerun.assert_called_once()

    @patch("src.components.common.st")
    def test_show_error_timeout(self, mock_st):
        from src.components.common import show_error_timeout

        show_error_timeout()
        mock_st.warning.assert_called_once()

    @patch("src.components.common.st")
    def test_show_error_permission(self, mock_st):
        from src.components.common import show_error_permission

        show_error_permission()
        mock_st.error.assert_called_once()

    @patch("src.components.common.st")
    def test_show_error_write_no_retry(self, mock_st):
        from src.components.common import show_error_write

        show_error_write()
        mock_st.error.assert_called_once()

    @patch("src.components.common.st")
    def test_show_error_write_with_retry(self, mock_st):
        from src.components.common import show_error_write

        mock_st.button.return_value = True
        callback = MagicMock()
        show_error_write(retry_callback=callback)
        callback.assert_called_once()
