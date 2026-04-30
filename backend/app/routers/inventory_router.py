"""在庫エンドポイント"""

from backend.app.auth import CurrentUser
from backend.app.dependencies import get_db_session, require_role
from backend.app.schemas import IngredientResponse, InventoryResponse, LowStockResponse
from fastapi import APIRouter, Depends, HTTPException
from snowflake.snowpark import Session
from src.dal.inventory import get_categories, get_ingredients, get_inventory, get_low_stock_items
from src.utils.constants import ROLE_MANAGER

router = APIRouter(prefix="/api", tags=["在庫"])


def _require_store_id(user: CurrentUser) -> int:
    """store_id が設定されていることを保証"""
    if user.store_id is None:
        raise HTTPException(status_code=403, detail="店舗が割り当てられていません")
    return user.store_id


@router.get("/inventory", response_model=list[InventoryResponse])
async def list_inventory(
    user: CurrentUser = Depends(require_role(ROLE_MANAGER)),
    session: Session = Depends(get_db_session),
):
    """在庫一覧取得（自店舗のみ）"""
    store_id = _require_store_id(user)
    return get_inventory(session, store_id=store_id)


@router.get("/inventory/low-stock", response_model=list[LowStockResponse])
async def list_low_stock(
    user: CurrentUser = Depends(require_role(ROLE_MANAGER)),
    session: Session = Depends(get_db_session),
):
    """低在庫アイテム取得"""
    store_id = _require_store_id(user)
    return get_low_stock_items(session, store_id=store_id)


@router.get("/ingredients", response_model=list[IngredientResponse])
async def list_ingredients(
    _user: CurrentUser = Depends(require_role(ROLE_MANAGER)),
    session: Session = Depends(get_db_session),
):
    """食材マスタ取得"""
    return get_ingredients(session)


@router.get("/ingredients/categories", response_model=list[str])
async def list_categories(
    _user: CurrentUser = Depends(require_role(ROLE_MANAGER)),
    session: Session = Depends(get_db_session),
):
    """カテゴリ一覧取得"""
    return get_categories(session)
