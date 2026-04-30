"""アプリメインテスト（Streamlit版 — React移行により無効化）"""

from unittest.mock import MagicMock, patch  # noqa: E402

import pytest

pytestmark = pytest.mark.skip(reason="Streamlit版テスト — React+FastAPIに移行済み")


class TestGetDriverName:
    def test_with_driver_role(self):
        with patch("streamlit.set_page_config"):
            from src.app import _get_driver_name

        roles = [{"role_type": "DRIVER", "user_id": "SATO", "related_id": "D001"}]
        assert _get_driver_name(roles) == "SATO"

    def test_without_driver_role(self):
        with patch("streamlit.set_page_config"):
            from src.app import _get_driver_name

        roles = [{"role_type": "MANAGER", "user_id": "TANAKA", "related_id": "S001"}]
        assert _get_driver_name(roles) == "ドライバー"

    def test_empty_roles(self):
        with patch("streamlit.set_page_config"):
            from src.app import _get_driver_name

        assert _get_driver_name([]) == "ドライバー"

    def test_driver_without_user_id(self):
        with patch("streamlit.set_page_config"):
            from src.app import _get_driver_name

        roles = [{"role_type": "DRIVER", "related_id": "D001"}]
        assert _get_driver_name(roles) == "ドライバー"


class TestMain:
    @patch("src.app.show_error_connection")
    @patch("src.app.get_current_user", side_effect=Exception("Connection error"))
    @patch("src.app.get_session")
    @patch("streamlit.set_page_config")
    def test_connection_error(self, mock_config, mock_get_session, mock_get_user, mock_show_error):
        from src.app import main

        main()
        mock_show_error.assert_called_once()

    @patch("src.app.show_consent_page")
    @patch("src.app.check_consent", return_value=False)
    @patch("src.app.get_current_user", return_value="TANAKA")
    @patch("src.app.get_session")
    @patch("streamlit.set_page_config")
    def test_consent_not_granted(self, mock_config, mock_session, mock_user, mock_consent, mock_show_consent):
        from src.app import main

        main()
        mock_show_consent.assert_called_once()

    @patch("src.app.show_error_permission")
    @patch("src.app.get_user_roles", return_value=[])
    @patch("src.app.check_consent", return_value=True)
    @patch("src.app.get_current_user", return_value="NOBODY")
    @patch("src.app.get_session")
    @patch("streamlit.set_page_config")
    def test_no_roles(self, mock_config, mock_session, mock_user, mock_consent, mock_roles, mock_error):
        from src.app import main

        main()
        mock_error.assert_called_once()

    @patch("src.app._show_manager_ui")
    @patch("src.app.is_driver", return_value=False)
    @patch("src.app.is_manager", return_value=True)
    @patch("src.app.get_user_roles", return_value=[{"role_type": "MANAGER"}])
    @patch("src.app.check_consent", return_value=True)
    @patch("src.app.get_current_user", return_value="TANAKA")
    @patch("src.app.get_session")
    @patch("streamlit.set_page_config")
    def test_manager_only(self, _cfg, _sess, _user, _consent, _roles, _mgr, _drv, mock_show_mgr):
        from src.app import main

        main()
        mock_show_mgr.assert_called_once()

    @patch("src.app.show_driver_page")
    @patch("src.app._get_driver_name", return_value="佐藤")
    @patch("src.app.is_driver", return_value=True)
    @patch("src.app.is_manager", return_value=False)
    @patch("src.app.get_user_roles", return_value=[{"role_type": "DRIVER"}])
    @patch("src.app.check_consent", return_value=True)
    @patch("src.app.get_current_user", return_value="SATO")
    @patch("src.app.get_session")
    @patch("streamlit.set_page_config")
    def test_driver_only(self, _cfg, _sess, _user, _consent, _roles, _mgr, _drv, _name, mock_show_drv):
        from src.app import main

        main()
        mock_show_drv.assert_called_once()

    @patch("src.app.show_error_permission")
    @patch("src.app.is_driver", return_value=False)
    @patch("src.app.is_manager", return_value=False)
    @patch("src.app.get_user_roles", return_value=[{"role_type": "UNKNOWN"}])
    @patch("src.app.check_consent", return_value=True)
    @patch("src.app.get_current_user", return_value="GUEST")
    @patch("src.app.get_session")
    @patch("streamlit.set_page_config")
    def test_unknown_role(self, _cfg, _sess, _user, _consent, _roles, _mgr, _drv, mock_error):
        from src.app import main

        main()
        mock_error.assert_called_once()

    @patch("src.app.show_driver_page")
    @patch("src.app._show_manager_ui")
    @patch("src.app._get_driver_name", return_value="佐藤")
    @patch("src.app.st")
    @patch("src.app.is_driver", return_value=True)
    @patch("src.app.is_manager", return_value=True)
    @patch("src.app.get_user_roles", return_value=[{"role_type": "MANAGER"}, {"role_type": "DRIVER"}])
    @patch("src.app.check_consent", return_value=True)
    @patch("src.app.get_current_user", return_value="SATO")
    @patch("src.app.get_session")
    @patch("streamlit.set_page_config")
    def test_dual_role(
        self,
        _cfg,
        _sess,
        _user,
        _consent,
        _roles,
        _mgr,
        _drv,
        mock_st,
        _name,
        _show_mgr,
        _show_drv,
    ):
        from src.app import main

        mock_st.tabs.return_value = [MagicMock(), MagicMock()]
        main()
        mock_st.tabs.assert_called_once()


class TestShowManagerUI:
    @patch("src.app.show_dashboard")
    @patch("src.app.st")
    @patch("streamlit.set_page_config")
    def test_dashboard(self, mock_config, mock_st, mock_show):
        from src.app import _show_manager_ui

        mock_st.sidebar.__enter__ = MagicMock(return_value=None)
        mock_st.sidebar.__exit__ = MagicMock(return_value=False)
        mock_st.radio.return_value = "ダッシュボード"
        session = MagicMock()
        _show_manager_ui(session, "TANAKA")
        mock_show.assert_called_once_with(session)

    @patch("src.app.show_orders")
    @patch("src.app.st")
    @patch("streamlit.set_page_config")
    def test_orders(self, mock_config, mock_st, mock_show):
        from src.app import _show_manager_ui

        mock_st.sidebar.__enter__ = MagicMock(return_value=None)
        mock_st.sidebar.__exit__ = MagicMock(return_value=False)
        mock_st.radio.return_value = "発注提案"
        session = MagicMock()
        _show_manager_ui(session, "TANAKA")
        mock_show.assert_called_once_with(session, "TANAKA")

    @patch("src.app.show_delivery_status")
    @patch("src.app.st")
    @patch("streamlit.set_page_config")
    def test_delivery(self, mock_config, mock_st, mock_show):
        from src.app import _show_manager_ui

        mock_st.sidebar.__enter__ = MagicMock(return_value=None)
        mock_st.sidebar.__exit__ = MagicMock(return_value=False)
        mock_st.radio.return_value = "配送状況"
        session = MagicMock()
        _show_manager_ui(session, "TANAKA")
        mock_show.assert_called_once_with(session)
