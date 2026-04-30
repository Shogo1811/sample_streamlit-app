"""配送エンドポイント"""

from typing import Literal

from backend.app.auth import CurrentUser
from backend.app.dependencies import get_db_session, require_role
from backend.app.schemas import DeliveryResponse, DriverDeliveryResponse, SPResultResponse
from fastapi import APIRouter, Depends, HTTPException
from snowflake.snowpark import Session
from src.dal.delivery import complete_delivery, get_deliveries, get_driver_deliveries
from src.utils.constants import ROLE_DRIVER, ROLE_MANAGER

router = APIRouter(prefix="/api/deliveries", tags=["配送"])

DeliveryStatus = Literal["未配送", "配送中", "配送完了"]


@router.get("", response_model=list[DeliveryResponse])
async def list_deliveries(
    status: DeliveryStatus | None = None,
    user: CurrentUser = Depends(require_role(ROLE_MANAGER)),
    session: Session = Depends(get_db_session),
):
    """配送一覧取得（店長向け）"""
    if user.store_id is None:
        raise HTTPException(status_code=403, detail="店舗が割り当てられていません")
    return get_deliveries(session, store_id=user.store_id, status_filter=status)


@router.get("/mine", response_model=list[DriverDeliveryResponse])
async def list_my_deliveries(
    user: CurrentUser = Depends(require_role(ROLE_DRIVER)),
    session: Session = Depends(get_db_session),
):
    """自分の配送一覧取得（ドライバー向け）"""
    if user.driver_id is None:
        raise HTTPException(status_code=403, detail="ドライバーが割り当てられていません")
    return get_driver_deliveries(session, driver_id=user.driver_id)


@router.post("/{delivery_id}/complete", response_model=SPResultResponse)
async def post_complete_delivery(
    delivery_id: int,
    user: CurrentUser = Depends(require_role(ROLE_DRIVER)),
    session: Session = Depends(get_db_session),
):
    """配送完了報告"""
    if user.driver_id is None:
        raise HTTPException(status_code=403, detail="ドライバーが割り当てられていません")
    result = complete_delivery(session, delivery_id, user.user_id)
    return SPResultResponse(**result)
