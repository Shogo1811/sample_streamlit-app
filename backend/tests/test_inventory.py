"""在庫APIテスト"""

from unittest.mock import patch


class TestInventoryEndpoints:
    """在庫エンドポイントテスト"""

    def test_list_inventory(self, client, mock_session):
        mock_data = [
            {
                "STORE_ID": 1,
                "INGREDIENT_NAME": "豚骨",
                "CATEGORY": "スープ素材",
                "CURRENT_QUANTITY": 50,
                "THRESHOLD": 10,
                "UNIT": "kg",
                "UPDATED_AT": "2026-04-28T10:00:00",
            }
        ]
        with patch("backend.app.routers.inventory_router.get_inventory", return_value=mock_data):
            resp = client().get("/api/inventory")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["ingredient_name"] == "豚骨"

    def test_list_low_stock(self, client, mock_session):
        mock_data = [
            {
                "INGREDIENT_NAME": "メンマ",
                "CATEGORY": "トッピング",
                "CURRENT_QUANTITY": 3,
                "THRESHOLD": 5,
                "UNIT": "kg",
            }
        ]
        with patch("backend.app.routers.inventory_router.get_low_stock_items", return_value=mock_data):
            resp = client().get("/api/inventory/low-stock")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["current_quantity"] < data[0]["threshold"]

    def test_list_ingredients(self, client, mock_session):
        mock_data = [
            {
                "INGREDIENT_ID": 1,
                "INGREDIENT_NAME": "豚骨",
                "CATEGORY": "スープ素材",
                "UNIT": "kg",
                "THRESHOLD": 10,
            }
        ]
        with patch("backend.app.routers.inventory_router.get_ingredients", return_value=mock_data):
            resp = client().get("/api/ingredients")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_categories(self, client, mock_session):
        with patch(
            "backend.app.routers.inventory_router.get_categories",
            return_value=["スープ素材", "トッピング", "麺"],
        ):
            resp = client().get("/api/ingredients/categories")
        assert resp.status_code == 200
        assert "スープ素材" in resp.json()
