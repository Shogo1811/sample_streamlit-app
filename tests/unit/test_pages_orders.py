"""店長発注提案ページテスト"""

from unittest.mock import MagicMock, patch


class TestShowOrders:
    @patch("src.pages.manager_orders._show_plans")
    @patch("src.pages.manager_orders._show_proposals")
    @patch("src.pages.manager_orders.st")
    def test_renders_tabs(self, mock_st, mock_proposals, mock_plans):
        from src.pages.manager_orders import show_orders

        mock_st.tabs.return_value = [MagicMock(), MagicMock()]
        show_orders(MagicMock(), "TANAKA")
        mock_st.tabs.assert_called_once()


class TestShowProposals:
    @patch("src.pages.manager_orders.show_empty_state")
    @patch("src.pages.manager_orders.get_proposals", return_value=[])
    @patch("src.pages.manager_orders.show_loading")
    @patch("src.pages.manager_orders.st")
    def test_empty(self, mock_st, mock_loading, mock_get, mock_empty):
        from src.pages.manager_orders import _show_proposals

        mock_loading.return_value.__enter__ = MagicMock()
        mock_loading.return_value.__exit__ = MagicMock(return_value=False)

        _show_proposals(MagicMock(), "TANAKA")
        mock_empty.assert_called_once()

    @patch(
        "src.pages.manager_orders.get_proposals",
        return_value=[
            {
                "PROPOSAL_ID": 1,
                "INGREDIENT_NAME": "麺",
                "CATEGORY": "主食材",
                "RECOMMENDED_QUANTITY": 100,
                "REASON": "在庫不足",
                "STATUS": "確認中",
            }
        ],
    )
    @patch("src.pages.manager_orders.show_loading")
    @patch("src.pages.manager_orders.st")
    def test_with_proposals(self, mock_st, mock_loading, mock_get):
        from src.pages.manager_orders import _show_proposals

        mock_loading.return_value.__enter__ = MagicMock()
        mock_loading.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.container.return_value.__enter__ = MagicMock()
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.button.return_value = False

        _show_proposals(MagicMock(), "TANAKA")
        mock_st.number_input.assert_called_once()


class TestShowPlans:
    @patch("src.pages.manager_orders.show_empty_state")
    @patch("src.pages.manager_orders.get_order_plans", return_value=[])
    @patch("src.pages.manager_orders.show_loading")
    @patch("src.pages.manager_orders.st")
    def test_empty(self, mock_st, mock_loading, mock_get, mock_empty):
        from src.pages.manager_orders import _show_plans

        mock_loading.return_value.__enter__ = MagicMock()
        mock_loading.return_value.__exit__ = MagicMock(return_value=False)

        _show_plans(MagicMock())
        mock_empty.assert_called_once()

    @patch(
        "src.pages.manager_orders.get_order_plans",
        return_value=[
            {
                "INGREDIENT_NAME": "麺",
                "QUANTITY": 100,
                "APPROVED_BY": "TANAKA",
                "APPROVED_AT": "2026-04-23",
            }
        ],
    )
    @patch("src.pages.manager_orders.show_loading")
    @patch("src.pages.manager_orders.st")
    def test_with_plans(self, mock_st, mock_loading, mock_get):
        from src.pages.manager_orders import _show_plans

        mock_loading.return_value.__enter__ = MagicMock()
        mock_loading.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.container.return_value.__enter__ = MagicMock()
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)

        _show_plans(MagicMock())
        mock_st.markdown.assert_called()


class TestHandleApprove:
    @patch("src.pages.manager_orders.st")
    def test_invalid_quantity(self, mock_st):
        from src.pages.manager_orders import _handle_approve

        _handle_approve(MagicMock(), 1, 0, "TANAKA")
        mock_st.error.assert_called_once()

    @patch("src.pages.manager_orders.st")
    def test_phase1_sets_flag_and_reruns(self, mock_st):
        """Phase 1: 確認フラグをセットしてst.rerunを呼ぶ"""
        from src.pages.manager_orders import _handle_approve

        mock_st.session_state = {}
        _handle_approve(MagicMock(), 1, 100, "TANAKA")
        assert "confirm_approve_1" in mock_st.session_state
        mock_st.rerun.assert_called_once()

    @patch("src.pages.manager_orders.approve_proposal", return_value={"success": True})
    @patch("src.pages.manager_orders.st")
    def test_phase2_confirm(self, mock_st, mock_approve):
        """Phase 2: 確認済みフラグがある場合に確認UIを表示"""
        from src.pages.manager_orders import _handle_approve

        mock_st.session_state = {"confirm_approve_1": True, "confirm_qty_1": 100}
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.button.side_effect = [True, False]

        _handle_approve(MagicMock(), 1, 100, "TANAKA")
        mock_approve.assert_called_once()
        mock_st.success.assert_called_once()


class TestHandleReject:
    @patch("src.pages.manager_orders.reject_proposal", return_value={"success": True})
    @patch("src.pages.manager_orders.st")
    def test_success(self, mock_st, mock_reject):
        from src.pages.manager_orders import _handle_reject

        _handle_reject(MagicMock(), 1, "TANAKA")
        mock_st.success.assert_called_once()
        mock_st.rerun.assert_called_once()

    @patch("src.pages.manager_orders.show_error_write")
    @patch("src.pages.manager_orders.reject_proposal", return_value={"success": False})
    @patch("src.pages.manager_orders.st")
    def test_failure(self, mock_st, mock_reject, mock_error):
        from src.pages.manager_orders import _handle_reject

        _handle_reject(MagicMock(), 1, "TANAKA")
        mock_error.assert_called_once()
