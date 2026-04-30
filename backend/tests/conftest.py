"""テストフィクスチャ"""

from unittest.mock import MagicMock

import pytest
from backend.app.auth import CurrentUser
from backend.app.dependencies import get_current_user, get_db_session
from backend.app.main import app
from fastapi.testclient import TestClient
from src.utils.constants import ROLE_DRIVER, ROLE_MANAGER


@pytest.fixture
def mock_session():
    """モック Snowpark Session"""
    return MagicMock()


@pytest.fixture
def manager_user():
    """店長ユーザー"""
    return CurrentUser(
        user_id="manager-oid-001",
        roles=[ROLE_MANAGER],
        store_id=1,
        driver_id=None,
    )


@pytest.fixture
def driver_user():
    """ドライバーユーザー"""
    return CurrentUser(
        user_id="driver-oid-001",
        roles=[ROLE_DRIVER],
        store_id=None,
        driver_id=1,
    )


@pytest.fixture
def dual_role_user():
    """店長+ドライバー兼任ユーザー"""
    return CurrentUser(
        user_id="dual-oid-001",
        roles=[ROLE_MANAGER, ROLE_DRIVER],
        store_id=1,
        driver_id=2,
    )


@pytest.fixture
def client(mock_session, manager_user):
    """テストクライアント（dependency_overrides で認証バイパス）"""

    def _make_client(user=None):
        active_user = user or manager_user

        app.dependency_overrides[get_current_user] = lambda: active_user
        app.dependency_overrides[get_db_session] = lambda: mock_session

        return TestClient(app)

    yield _make_client

    app.dependency_overrides.clear()
