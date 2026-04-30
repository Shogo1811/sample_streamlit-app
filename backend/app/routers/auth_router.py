"""認証・ユーザー情報エンドポイント"""

from backend.app.auth import CurrentUser
from backend.app.dependencies import get_current_user, get_db_session
from backend.app.schemas import ConsentRequest, ConsentStatusResponse, UserResponse
from fastapi import APIRouter, Depends, HTTPException
from snowflake.snowpark import Session
from src.dal.auth import check_consent, record_consent, revoke_consent
from src.utils.constants import CURRENT_POLICY_VERSION

router = APIRouter(prefix="/api/auth", tags=["認証"])


@router.get("/me", response_model=UserResponse)
async def get_me(user: CurrentUser = Depends(get_current_user)):
    """現在のユーザー情報を取得"""
    return UserResponse(
        user_id=user.user_id,
        roles=user.roles,
        store_id=user.store_id,
        driver_id=user.driver_id,
    )


@router.get("/consent", response_model=ConsentStatusResponse)
async def get_consent_status(
    user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    """同意ステータスを確認"""
    consented = check_consent(session, user.user_id, CURRENT_POLICY_VERSION)
    return ConsentStatusResponse(
        consented=consented,
        policy_version=CURRENT_POLICY_VERSION,
    )


@router.post("/consent", response_model=ConsentStatusResponse)
async def post_consent(
    body: ConsentRequest,
    user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    """プライバシーポリシー同意を記録"""
    if body.policy_version != CURRENT_POLICY_VERSION:
        raise HTTPException(
            status_code=400,
            detail=f"無効なポリシーバージョンです。現在のバージョン: {CURRENT_POLICY_VERSION}",
        )
    record_consent(session, user.user_id, body.policy_version)
    return ConsentStatusResponse(consented=True, policy_version=body.policy_version)


@router.delete("/consent", response_model=ConsentStatusResponse)
async def delete_consent(
    user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_db_session),
):
    """プライバシーポリシー同意を撤回"""
    revoke_consent(session, user.user_id, CURRENT_POLICY_VERSION)
    return ConsentStatusResponse(consented=False, policy_version=CURRENT_POLICY_VERSION)
