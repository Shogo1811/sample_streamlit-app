"""在庫DALテスト"""

from tests.conftest import make_mock_df


class TestGetIngredients:
    def test_returns_list(self, mock_session):
        from src.dal.inventory import get_ingredients

        mock_df = make_mock_df(
            [
                {"INGREDIENT_ID": 1, "INGREDIENT_NAME": "麺", "CATEGORY": "主食材", "UNIT": "kg", "THRESHOLD": 20},
                {
                    "INGREDIENT_ID": 2,
                    "INGREDIENT_NAME": "チャーシュー",
                    "CATEGORY": "トッピング",
                    "UNIT": "kg",
                    "THRESHOLD": 10,
                },
            ]
        )
        mock_session.table.return_value = mock_df

        result = get_ingredients(mock_session)
        assert len(result) == 2
        assert result[0]["INGREDIENT_NAME"] == "麺"
        assert result[1]["CATEGORY"] == "トッピング"


class TestGetCategories:
    def test_returns_category_list(self, mock_session):
        from src.dal.inventory import get_categories

        mock_df = make_mock_df([{"CATEGORY": "主食材"}, {"CATEGORY": "トッピング"}])
        mock_session.table.return_value = mock_df

        result = get_categories(mock_session)
        assert result == ["主食材", "トッピング"]


class TestGetInventory:
    def test_returns_joined_data(self, mock_session):
        from src.dal.inventory import get_inventory

        mock_df = make_mock_df(
            [
                {
                    "STORE_ID": "S001",
                    "INGREDIENT_NAME": "麺",
                    "CATEGORY": "主食材",
                    "CURRENT_QUANTITY": 50,
                    "THRESHOLD": 20,
                    "UNIT": "kg",
                    "UPDATED_AT": "2026-04-23",
                }
            ]
        )
        mock_session.table.return_value = mock_df

        result = get_inventory(mock_session)
        assert len(result) == 1
        assert result[0]["CURRENT_QUANTITY"] == 50


class TestGetLowStockItems:
    def test_returns_low_stock(self, mock_session):
        from src.dal.inventory import get_low_stock_items

        mock_df = make_mock_df(
            [
                {
                    "INGREDIENT_NAME": "チャーシュー",
                    "CATEGORY": "トッピング",
                    "CURRENT_QUANTITY": 5,
                    "THRESHOLD": 10,
                    "UNIT": "kg",
                }
            ]
        )
        mock_session.table.return_value = mock_df

        result = get_low_stock_items(mock_session)
        assert len(result) == 1
        assert result[0]["CURRENT_QUANTITY"] == 5

    def test_returns_empty_when_no_alerts(self, mock_session):
        from src.dal.inventory import get_low_stock_items

        mock_df = make_mock_df([])
        mock_session.table.return_value = mock_df

        result = get_low_stock_items(mock_session)
        assert result == []
