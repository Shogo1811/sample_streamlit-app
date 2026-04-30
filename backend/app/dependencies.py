"""FastAPI 依存性注入"""

import logging

from backend.app.auth import CurrentUser, verify_token
from backend.app.config import settings
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from snowflake.snowpark import Session
from src.dal.auth import get_driver_id, get_store_id, get_user_roles
from src.dal.session import get_session

logger = logging.getLogger("ramen-logistics")

security = HTTPBearer(auto_error=not settings.debug)


def get_db_session() -> Session:
    """Snowpark セッションを取得"""
    return get_session()


def _get_spcs_user(request: Request, session: Session) -> str:
    """SPCS環境: ingressヘッダーからログインユーザーを取得、なければCURRENT_USER()"""
    # SPCSのingressは Sf-Context-Current-User ヘッダーでユーザー名を渡す
    sf_user = request.headers.get("Sf-Context-Current-User", "")
    if sf_user:
        return sf_user
    # フォールバック: CURRENT_USER()
    return session.sql("SELECT CURRENT_USER()").collect()[0][0]


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    session: Session = Depends(get_db_session),
) -> CurrentUser:
    """認証済みユーザーを取得し、DB からロール情報を補完"""
    # DEBUGモード: Azure AD 未設定時はSnowflakeユーザーで認証バイパス
    if settings.debug and (credentials is None or credentials.credentials == ""):
        sf_user = _get_spcs_user(request, session)
        logger.warning("DEBUG: 認証バイパス — ユーザー: %s", sf_user)
        db_roles = get_user_roles(session, sf_user)
        return CurrentUser(
            user_id=sf_user,
            roles=[r["role_type"] for r in db_roles],
            store_id=get_store_id(db_roles),
            driver_id=get_driver_id(db_roles),
        )

    if credentials is None:
        raise HTTPException(status_code=401, detail="認証トークンが必要です")

    user = await verify_token(credentials)

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
