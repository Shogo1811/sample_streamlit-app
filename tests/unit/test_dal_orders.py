"""発注DALテスト"""

import json
from unittest.mock import patch

from tests.conftest import MockRow, make_mock_df


class TestGetProposals:
    def test_no_filter(self, mock_session):
        from src.dal.orders import get_proposals

        mock_df = make_mock_df(
            [
                {
                    "PROPOSAL_ID": 1,
                    "INGREDIENT_NAME": "麺",
                    "CATEGORY": "主食材",
                    "RECOMMENDED_QUANTITY": 100,
                    "REASON": "在庫不足",
                    "STATUS": "確認中",
                    "CREATED_AT": "2026-04-23",
                }
            ]
        )
        mock_session.table.return_value = mock_df

        result = get_proposals(mock_session)
        assert len(result) == 1
        assert result[0]["PROPOSAL_ID"] == 1

    def test_with_status_filter(self, mock_session):
        from src.dal.orders import get_proposals

        mock_df = make_mock_df(
            [
                {
                    "PROPOSAL_ID": 2,
                    "INGREDIENT_NAME": "チャーシュー",
                    "CATEGORY": "トッピング",
                    "RECOMMENDED_QUANTITY": 50,
                    "REASON": "定期発注",
                    "STATUS": "承認",
                    "CREATED_AT": "2026-04-23",
                }
            ]
        )
        mock_session.table.return_value = mock_df

        result = get_proposals(mock_session, status_filter="承認")
        assert len(result) == 1
        mock_df.filter.assert_called()


class TestApproveProposal:
    @patch("src.dal.orders.st")
    def test_success_json_string(self, mock_st, mock_session):
        """SP戻り値がJSON文字列の場合にパースされること"""
        from src.dal.orders import approve_proposal

        sp_result = json.dumps({"success": True, "message": "承認しました"})
        mock_session.sql.return_value.collect.return_value = [MockRow({"result": sp_result})]

        result = approve_proposal(mock_session, 1, 100, "TANAKA")
        assert result == {"success": True, "message": "承認しました"}

    @patch("src.dal.orders.st")
    def test_empty_result(self, mock_st, mock_session):
        from src.dal.orders import approve_proposal

        mock_session.sql.return_value.collect.return_value = []

        result = approve_proposal(mock_session, 1, 100, "TANAKA")
        assert result == {"success": False, "message": "SP呼出エラー"}


class TestRejectProposal:
    @patch("src.dal.orders.st")
    def test_success(self, mock_st, mock_session):
        from src.dal.orders import reject_proposal

        sp_result = json.dumps({"success": True, "message": "却下しました"})
        mock_session.sql.return_value.collect.return_value = [MockRow({"result": sp_result})]

        result = reject_proposal(mock_session, 1, "TANAKA")
        assert result == {"success": True, "message": "却下しました"}

    @patch("src.dal.orders.st")
    def test_empty_result(self, mock_st, mock_session):
        from src.dal.orders import reject_proposal

        mock_session.sql.return_value.collect.return_value = []

        result = reject_proposal(mock_session, 1, "TANAKA")
        assert result == {"success": False, "message": "SP呼出エラー"}


class TestGetOrderPlans:
    def test_returns_plans(self, mock_session):
        from src.dal.orders import get_order_plans

        mock_df = make_mock_df(
            [
                {
                    "PLAN_ID": 1,
                    "INGREDIENT_NAME": "麺",
                    "QUANTITY": 100,
                    "APPROVED_BY": "TANAKA",
                    "APPROVED_AT": "2026-04-23",
                }
            ]
        )
        mock_session.table.return_value = mock_df

        result = get_order_plans(mock_session)
        assert len(result) == 1
        assert result[0]["APPROVED_BY"] == "TANAKA"
