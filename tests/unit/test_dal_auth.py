"""認証DALテスト"""

from src.dal.auth import (
    check_consent,
    get_current_user,
    get_user_roles,
    is_driver,
    is_manager,
    record_consent,
)
from tests.conftest import MockRow, make_mock_df


class TestGetCurrentUser:
    def test_returns_username(self, mock_session):
        mock_session.sql.return_value.collect.return_value = [MockRow({"CURRENT_USER()": "TANAKA"})]
        assert get_current_user(mock_session) == "TANAKA"
        mock_session.sql.assert_called_once_with("SELECT CURRENT_USER()")


class TestGetUserRoles:
    def test_multiple_roles(self, mock_session):
        mock_df = make_mock_df(
            [
                {"USER_ID": "SATO", "ROLE_TYPE": "MANAGER", "RELATED_ID": "STORE_001"},
                {"USER_ID": "SATO", "ROLE_TYPE": "DRIVER", "RELATED_ID": "DRIVER_001"},
            ]
        )
        mock_session.table.return_value = mock_df

        result = get_user_roles(mock_session, "SATO")
        assert len(result) == 2
        assert result[0]["role_type"] == "MANAGER"
        assert result[1]["role_type"] == "DRIVER"

    def test_empty(self, mock_session):
        mock_df = make_mock_df([])
        mock_session.table.return_value = mock_df

        result = get_user_roles(mock_session, "NOBODY")
        assert result == []


class TestIsManager:
    def test_true(self):
        roles = [{"role_type": "MANAGER", "user_id": "T", "related_id": "S"}]
        assert is_manager(roles) is True

    def test_false(self):
        roles = [{"role_type": "DRIVER", "user_id": "S", "related_id": "D"}]
        assert is_manager(roles) is False

    def test_empty(self):
        assert is_manager([]) is False


class TestIsDriver:
    def test_true(self):
        roles = [{"role_type": "DRIVER", "user_id": "S", "related_id": "D"}]
        assert is_driver(roles) is True

    def test_false(self):
        roles = [{"role_type": "MANAGER", "user_id": "T", "related_id": "S"}]
        assert is_driver(roles) is False


class TestCheckConsent:
    def test_granted(self, mock_session):
        mock_df = make_mock_df([{"USER_ID": "TANAKA", "CONSENT_TYPE": "GRANT", "POLICY_VERSION": "1.0.0"}])
        mock_session.table.return_value = mock_df

        assert check_consent(mock_session, "TANAKA", "1.0.0") is True

    def test_not_granted(self, mock_session):
        mock_df = make_mock_df([])
        mock_session.table.return_value = mock_df

        assert check_consent(mock_session, "NEW_USER", "1.0.0") is False

    def test_revoked(self, mock_session):
        """同意撤回後はFalseを返す"""
        mock_df = make_mock_df([{"USER_ID": "TANAKA", "CONSENT_TYPE": "REVOKE", "POLICY_VERSION": "1.0.0"}])
        mock_session.table.return_value = mock_df

        assert check_consent(mock_session, "TANAKA", "1.0.0") is False


class TestRecordConsent:
    def test_inserts_with_params(self, mock_session):
        record_consent(mock_session, "TANAKA", "v1.0")
        mock_session.sql.assert_called_once()
        call_args = mock_session.sql.call_args
        assert call_args.kwargs.get("params") == ["TANAKA", "v1.0"]
