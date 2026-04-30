"""認証テスト"""

from unittest.mock import patch

from backend.app.auth import CurrentUser, _map_groups_to_roles
from src.utils.constants import ROLE_DRIVER, ROLE_MANAGER


class TestGroupToRoleMapping:
    """Azure AD グループ → ロールマッピング"""

    @patch("backend.app.auth.settings")
    def test_manager_group(self, mock_settings):
        mock_settings.azure_ad_manager_group_id = "mgr-group-id"
        mock_settings.azure_ad_driver_group_id = "drv-group-id"
        roles = _map_groups_to_roles(["mgr-group-id"])
        assert roles == [ROLE_MANAGER]

    @patch("backend.app.auth.settings")
    def test_driver_group(self, mock_settings):
        mock_settings.azure_ad_manager_group_id = "mgr-group-id"
        mock_settings.azure_ad_driver_group_id = "drv-group-id"
        roles = _map_groups_to_roles(["drv-group-id"])
        assert roles == [ROLE_DRIVER]

    @patch("backend.app.auth.settings")
    def test_dual_role(self, mock_settings):
        mock_settings.azure_ad_manager_group_id = "mgr-group-id"
        mock_settings.azure_ad_driver_group_id = "drv-group-id"
        roles = _map_groups_to_roles(["mgr-group-id", "drv-group-id"])
        assert ROLE_MANAGER in roles
        assert ROLE_DRIVER in roles

    @patch("backend.app.auth.settings")
    def test_no_matching_group(self, mock_settings):
        mock_settings.azure_ad_manager_group_id = "mgr-group-id"
        mock_settings.azure_ad_driver_group_id = "drv-group-id"
        roles = _map_groups_to_roles(["unknown-group"])
        assert roles == []

    @patch("backend.app.auth.settings")
    def test_empty_groups(self, mock_settings):
        mock_settings.azure_ad_manager_group_id = "mgr-group-id"
        mock_settings.azure_ad_driver_group_id = "drv-group-id"
        roles = _map_groups_to_roles([])
        assert roles == []


class TestCurrentUser:
    """CurrentUser データクラス"""

    def test_manager_user(self):
        user = CurrentUser(user_id="oid-1", roles=[ROLE_MANAGER], store_id=1)
        assert user.user_id == "oid-1"
        assert user.store_id == 1
        assert user.driver_id is None

    def test_driver_user(self):
        user = CurrentUser(user_id="oid-2", roles=[ROLE_DRIVER], driver_id=5)
        assert user.driver_id == 5
        assert user.store_id is None


class TestAuthRouterEndpoints:
    """auth_router エンドポイントテスト"""

    def test_get_me_manager(self, client, manager_user):
        with patch("backend.app.routers.auth_router.get_current_user", return_value=manager_user):
            resp = client().get("/api/auth/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_id"] == "manager-oid-001"
        assert ROLE_MANAGER in data["roles"]

    def test_get_consent_status(self, client, mock_session):
        with patch("backend.app.routers.auth_router.check_consent", return_value=True):
            resp = client().get("/api/auth/consent")
        assert resp.status_code == 200
        assert resp.json()["consented"] is True

    def test_post_consent(self, client, mock_session):
        with patch("backend.app.routers.auth_router.record_consent"):
            resp = client().post("/api/auth/consent", json={"policy_version": "1.0.0"})
        assert resp.status_code == 200
        assert resp.json()["consented"] is True

    def test_post_consent_wrong_version(self, client, mock_session):
        resp = client().post("/api/auth/consent", json={"policy_version": "999.0.0"})
        assert resp.status_code == 400

    def test_delete_consent(self, client, mock_session):
        with patch("backend.app.routers.auth_router.revoke_consent"):
            resp = client().delete("/api/auth/consent")
        assert resp.status_code == 200
        assert resp.json()["consented"] is False


class TestRBACAuthorization:
    """ロールベースアクセス制御テスト"""

    def test_driver_cannot_access_inventory(self, client, driver_user, mock_session):
        with patch("backend.app.routers.inventory_router.get_inventory", return_value=[]):
            resp = client(user=driver_user).get("/api/inventory")
        assert resp.status_code == 403

    def test_driver_cannot_access_orders(self, client, driver_user, mock_session):
        with patch("backend.app.routers.orders_router.get_proposals", return_value=[]):
            resp = client(user=driver_user).get("/api/orders/proposals")
        assert resp.status_code == 403

    def test_manager_cannot_access_driver_deliveries(self, client, manager_user, mock_session):
        with patch("backend.app.routers.delivery_router.get_driver_deliveries", return_value=[]):
            resp = client(user=manager_user).get("/api/deliveries/mine")
        assert resp.status_code == 403

    def test_dual_role_can_access_both(self, client, dual_role_user, mock_session):
        with patch("backend.app.routers.inventory_router.get_inventory", return_value=[]):
            resp = client(user=dual_role_user).get("/api/inventory")
        assert resp.status_code == 200
        with patch("backend.app.routers.delivery_router.get_driver_deliveries", return_value=[]):
            resp2 = client(user=dual_role_user).get("/api/deliveries/mine")
        assert resp2.status_code == 200
