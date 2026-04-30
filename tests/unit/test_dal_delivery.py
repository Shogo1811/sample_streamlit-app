"""配送DALテスト"""

import json

from src.dal.delivery import complete_delivery, get_deliveries, get_driver_deliveries
from tests.conftest import MockRow, make_mock_df


class TestGetDeliveries:
    def test_no_filter(self, mock_session):
        mock_df = make_mock_df(
            [
                {
                    "DELIVERY_ID": 1,
                    "STORE_NAME": "ラーメン〇〇店",
                    "DRIVER_NAME": "佐藤",
                    "STATUS": "配送中",
                    "SCHEDULED_AT": "2026-04-23 10:00",
                    "COMPLETED_AT": None,
                }
            ]
        )
        mock_session.table.return_value = mock_df

        result = get_deliveries(mock_session)
        assert len(result) == 1
        assert result[0]["STORE_NAME"] == "ラーメン〇〇店"

    def test_with_status_filter(self, mock_session):
        mock_df = make_mock_df(
            [
                {
                    "DELIVERY_ID": 2,
                    "STORE_NAME": "ラーメン△△店",
                    "DRIVER_NAME": "佐藤",
                    "STATUS": "配送完了",
                    "SCHEDULED_AT": "2026-04-23 14:00",
                    "COMPLETED_AT": "2026-04-23 14:30",
                }
            ]
        )
        mock_session.table.return_value = mock_df

        result = get_deliveries(mock_session, status_filter="配送完了")
        assert len(result) == 1
        mock_df.filter.assert_called()


class TestGetDriverDeliveries:
    def test_returns_sorted_list(self, mock_session):
        mock_df = make_mock_df(
            [
                {"DELIVERY_ID": 1, "STORE_NAME": "ラーメン〇〇店", "STATUS": "配送中", "SCHEDULED_AT": "10:00"},
                {"DELIVERY_ID": 2, "STORE_NAME": "ラーメン△△店", "STATUS": "未配送", "SCHEDULED_AT": "14:00"},
            ]
        )
        mock_session.table.return_value = mock_df

        result = get_driver_deliveries(mock_session)
        assert len(result) == 2
        mock_df.sort.assert_called_once()


class TestCompleteDelivery:
    def test_success(self, mock_session):
        sp_result = json.dumps({"success": True, "message": "配送完了"})
        mock_session.sql.return_value.collect.return_value = [MockRow({"result": sp_result})]

        result = complete_delivery(mock_session, 1, "SATO")
        assert result == {"success": True, "message": "配送完了"}

    def test_empty_result(self, mock_session):
        mock_session.sql.return_value.collect.return_value = []

        result = complete_delivery(mock_session, 1, "SATO")
        assert result == {"success": False, "message": "SP呼出エラー"}
