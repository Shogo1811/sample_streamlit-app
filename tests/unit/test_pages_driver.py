"""ドライバー配送ページテスト"""

from unittest.mock import MagicMock, patch


class TestShowDriverPage:
    @patch("src.pages.driver_delivery.show_empty_state")
    @patch("src.pages.driver_delivery.get_driver_deliveries", return_value=[])
    @patch("src.pages.driver_delivery.show_loading")
    @patch("src.pages.driver_delivery.st")
    def test_empty(self, mock_st, mock_loading, mock_get, mock_empty):
        from src.pages.driver_delivery import show_driver_page

        mock_loading.return_value.__enter__ = MagicMock()
        mock_loading.return_value.__exit__ = MagicMock(return_value=False)

        show_driver_page(MagicMock(), "SATO", "佐藤")
        mock_empty.assert_called_once()

    @patch(
        "src.pages.driver_delivery.get_driver_deliveries",
        return_value=[
            {"DELIVERY_ID": 1, "STORE_NAME": "ラーメン〇〇店", "STATUS": "配送完了", "SCHEDULED_AT": "10:00"},
            {"DELIVERY_ID": 2, "STORE_NAME": "ラーメン△△店", "STATUS": "配送中", "SCHEDULED_AT": "14:00"},
            {"DELIVERY_ID": 3, "STORE_NAME": "ラーメン□□店", "STATUS": "未配送", "SCHEDULED_AT": "16:00"},
        ],
    )
    @patch("src.pages.driver_delivery.show_loading")
    @patch("src.pages.driver_delivery.st")
    def test_mixed_statuses(self, mock_st, mock_loading, mock_get):
        from src.pages.driver_delivery import show_driver_page

        mock_loading.return_value.__enter__ = MagicMock()
        mock_loading.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.container.return_value.__enter__ = MagicMock()
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.button.return_value = False

        show_driver_page(MagicMock(), "SATO", "佐藤")
        mock_st.title.assert_called_once()


class TestHandleComplete:
    @patch("src.pages.driver_delivery.st")
    def test_phase1_sets_flag_and_reruns(self, mock_st):
        """Phase 1: 確認フラグをセットしてst.rerunを呼ぶ"""
        from src.pages.driver_delivery import _handle_complete

        mock_st.session_state = {}
        _handle_complete(MagicMock(), 1, "SATO")
        assert "confirm_complete_1" in mock_st.session_state
        mock_st.rerun.assert_called_once()

    @patch("src.pages.driver_delivery.complete_delivery", return_value={"success": True})
    @patch("src.pages.driver_delivery.st")
    def test_phase2_confirm_success(self, mock_st, mock_complete):
        """Phase 2: 確認→完了成功"""
        from src.pages.driver_delivery import _handle_complete

        mock_st.session_state = {"confirm_complete_1": True}
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.button.side_effect = [True, False]

        _handle_complete(MagicMock(), 1, "SATO")
        mock_complete.assert_called_once()
        mock_st.success.assert_called()

    @patch("src.pages.driver_delivery.show_error_write")
    @patch("src.pages.driver_delivery.complete_delivery", return_value={"success": False})
    @patch("src.pages.driver_delivery.st")
    def test_phase2_confirm_failure(self, mock_st, mock_complete, mock_error):
        """Phase 2: 確認→完了失敗"""
        from src.pages.driver_delivery import _handle_complete

        mock_st.session_state = {"confirm_complete_1": True}
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.button.side_effect = [True, False]

        _handle_complete(MagicMock(), 1, "SATO")
        mock_error.assert_called_once()

    @patch("src.pages.driver_delivery.st")
    def test_phase2_cancel(self, mock_st):
        """Phase 2: キャンセル"""
        from src.pages.driver_delivery import _handle_complete

        mock_st.session_state = {"confirm_complete_1": True}
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.button.side_effect = [False, True]

        _handle_complete(MagicMock(), 1, "SATO")
        mock_st.rerun.assert_called_once()
