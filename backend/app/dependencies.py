"""FastAPI 依存性注入"""

from backend.app.auth import CurrentUser, verify_token
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from snowflake.snowpark import Session
from src.dal.auth import get_driver_id, get_store_id, get_user_roles
from src.dal.session import get_session

security = HTTPBearer()


def get_db_session() -> Session:
    """Snowpark セッションを取得"""
    return get_session()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_db_session),
) -> CurrentUser:
    """認証済みユーザーを取得し、DB からロール情報を補完"""
    user = await verify_token(credentials)

    # DB の USER_ROLE_MAPPING からロール + related_id を取得
    db_roles = get_user_roles(session, user.user_id)
    if db_roles:
        user.store_id = get_store_id(db_roles)
        user.driver_id = get_driver_id(db_roles)

    return user


def require_role(*required_roles: str):
    """指定ロールを持っているか検証する依存関数を返す"""

    async def check_role(
        user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if not any(role in user.roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="この操作に必要なロールがありません",
            )
        return user

    return check_role
