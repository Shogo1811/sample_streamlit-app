"""配送APIテスト"""

from unittest.mock import patch


class TestDeliveryEndpoints:
    """配送エンドポイントテスト"""

    def test_list_deliveries_manager(self, client, mock_session):
        mock_data = [
            {
                "DELIVERY_ID": 1,
                "STORE_NAME": "渋谷店",
                "DRIVER_NAME": "佐藤次郎",
                "STATUS": "配送中",
                "SCHEDULED_AT": "2026-04-28T14:00:00",
                "COMPLETED_AT": None,
            }
        ]
        with patch("backend.app.routers.delivery_router.get_deliveries", return_value=mock_data):
            resp = client().get("/api/deliveries")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["status"] == "配送中"

    def test_list_deliveries_with_status_filter(self, client, mock_session):
        with patch("backend.app.routers.delivery_router.get_deliveries", return_value=[]):
            resp = client().get("/api/deliveries?status=未配送")
        assert resp.status_code == 200

    def test_list_my_deliveries_driver(self, client, mock_session, driver_user):
        mock_data = [
            {
                "DELIVERY_ID": 1,
                "STORE_NAME": "渋谷店",
                "STATUS": "配送中",
                "SCHEDULED_AT": "2026-04-28T14:00:00",
            }
        ]
        with patch("backend.app.routers.delivery_router.get_driver_deliveries", return_value=mock_data):
            resp = client(user=driver_user).get("/api/deliveries/mine")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["store_name"] == "渋谷店"

    def test_complete_delivery_driver(self, client, mock_session, driver_user):
        sp_result = {"success": True, "message": "配送完了を記録しました"}
        with patch("backend.app.routers.delivery_router.complete_delivery", return_value=sp_result):
            resp = client(user=driver_user).post("/api/deliveries/1/complete")
        assert resp.status_code == 200
        assert resp.json()["success"] is True
