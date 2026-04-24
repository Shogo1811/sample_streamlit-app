"""店長ダッシュボードページテスト"""

from unittest.mock import MagicMock, patch


class TestShowDashboard:
    @patch("src.pages.manager_dashboard.show_low_stock_alerts")
    @patch("src.pages.manager_dashboard.inventory_trend_chart")
    @patch("src.pages.manager_dashboard.inventory_bar_chart")
    @patch("src.pages.manager_dashboard.get_low_stock_items", return_value=[])
    @patch(
        "src.pages.manager_dashboard.get_inventory",
        return_value=[
            {"INGREDIENT_NAME": "麺", "CATEGORY": "主食材", "CURRENT_QUANTITY": 50, "THRESHOLD": 20, "UNIT": "kg"},
        ],
    )
    @patch("src.pages.manager_dashboard.get_categories", return_value=["主食材", "トッピング"])
    @patch("src.pages.manager_dashboard.show_loading")
    @patch("src.pages.manager_dashboard.st")
    def test_with_data_no_filter(
        self, mock_st, mock_loading, mock_cat, mock_inv, mock_low, mock_chart, mock_trend, mock_alerts
    ):
        from src.pages.manager_dashboard import show_dashboard

        mock_st.selectbox.return_value = "すべて"
        mock_loading.return_value.__enter__ = MagicMock()
        mock_loading.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.sidebar.__enter__ = MagicMock()
        mock_st.sidebar.__exit__ = MagicMock(return_value=False)

        show_dashboard(MagicMock())
        mock_chart.assert_called_once()
        mock_alerts.assert_not_called()

    @patch("src.pages.manager_dashboard.show_low_stock_alerts")
    @patch("src.pages.manager_dashboard.inventory_trend_chart")
    @patch("src.pages.manager_dashboard.inventory_bar_chart")
    @patch(
        "src.pages.manager_dashboard.get_low_stock_items",
        return_value=[
            {
                "INGREDIENT_NAME": "チャーシュー",
                "CATEGORY": "トッピング",
                "CURRENT_QUANTITY": 5,
                "THRESHOLD": 10,
                "UNIT": "kg",
            },
        ],
    )
    @patch(
        "src.pages.manager_dashboard.get_inventory",
        return_value=[
            {"INGREDIENT_NAME": "麺", "CATEGORY": "主食材", "CURRENT_QUANTITY": 50},
        ],
    )
    @patch("src.pages.manager_dashboard.get_categories", return_value=["主食材"])
    @patch("src.pages.manager_dashboard.show_loading")
    @patch("src.pages.manager_dashboard.st")
    def test_with_low_stock(
        self, mock_st, mock_loading, mock_cat, mock_inv, mock_low, mock_chart, mock_trend, mock_alerts
    ):
        from src.pages.manager_dashboard import show_dashboard

        mock_st.selectbox.return_value = "すべて"
        mock_loading.return_value.__enter__ = MagicMock()
        mock_loading.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.sidebar.__enter__ = MagicMock()
        mock_st.sidebar.__exit__ = MagicMock(return_value=False)

        show_dashboard(MagicMock())
        mock_alerts.assert_called_once()

    @patch("src.pages.manager_dashboard.inventory_trend_chart")
    @patch("src.pages.manager_dashboard.show_empty_state")
    @patch("src.pages.manager_dashboard.get_low_stock_items", return_value=[])
    @patch(
        "src.pages.manager_dashboard.get_inventory",
        return_value=[
            {"INGREDIENT_NAME": "麺", "CATEGORY": "主食材", "CURRENT_QUANTITY": 50},
        ],
    )
    @patch("src.pages.manager_dashboard.get_categories", return_value=["主食材", "トッピング"])
    @patch("src.pages.manager_dashboard.show_loading")
    @patch("src.pages.manager_dashboard.st")
    def test_category_filter(self, mock_st, mock_loading, mock_cat, mock_inv, mock_low, mock_empty, mock_trend):
        from src.pages.manager_dashboard import show_dashboard

        mock_st.selectbox.return_value = "トッピング"
        mock_loading.return_value.__enter__ = MagicMock()
        mock_loading.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.sidebar.__enter__ = MagicMock()
        mock_st.sidebar.__exit__ = MagicMock(return_value=False)

        show_dashboard(MagicMock())
        assert mock_empty.call_count == 2
