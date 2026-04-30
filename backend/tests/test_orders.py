"""発注APIテスト"""

from unittest.mock import patch


class TestOrderEndpoints:
    """発注エンドポイントテスト"""

    def test_list_proposals(self, client, mock_session):
        mock_data = [
            {
                "PROPOSAL_ID": 1,
                "INGREDIENT_NAME": "豚骨",
                "CATEGORY": "スープ素材",
                "RECOMMENDED_QUANTITY": 100,
                "REASON": "在庫が閾値以下",
                "STATUS": "確認中",
                "CREATED_AT": "2026-04-28T09:00:00",
            }
        ]
        with patch("backend.app.routers.orders_router.get_proposals", return_value=mock_data):
            resp = client().get("/api/orders/proposals")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["status"] == "確認中"

    def test_list_proposals_with_status_filter(self, client, mock_session):
        with patch("backend.app.routers.orders_router.get_proposals", return_value=[]) as mock_get:
            resp = client().get("/api/orders/proposals?status=承認")
        assert resp.status_code == 200
        mock_get.assert_called_once()

    def test_approve_proposal(self, client, mock_session):
        sp_result = {"success": True, "message": "承認しました"}
        with patch("backend.app.routers.orders_router.approve_proposal", return_value=sp_result):
            resp = client().post(
                "/api/orders/proposals/1/approve",
                json={"quantity": 100},
            )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_approve_proposal_invalid_quantity(self, client, mock_session):
        resp = client().post(
            "/api/orders/proposals/1/approve",
            json={"quantity": 0},
        )
        assert resp.status_code == 422

    def test_approve_proposal_exceeds_max(self, client, mock_session):
        resp = client().post(
            "/api/orders/proposals/1/approve",
            json={"quantity": 10001},
        )
        assert resp.status_code == 422

    def test_reject_proposal(self, client, mock_session):
        sp_result = {"success": True, "message": "却下しました"}
        with patch("backend.app.routers.orders_router.reject_proposal", return_value=sp_result):
            resp = client().post("/api/orders/proposals/1/reject")
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_list_order_plans(self, client, mock_session):
        mock_data = [
            {
                "PLAN_ID": 1,
                "INGREDIENT_NAME": "豚骨",
                "QUANTITY": 100,
                "APPROVED_BY": "manager-001",
                "APPROVED_AT": "2026-04-28T10:00:00",
            }
        ]
        with patch("backend.app.routers.orders_router.get_order_plans", return_value=mock_data):
            resp = client().get("/api/orders/plans")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
