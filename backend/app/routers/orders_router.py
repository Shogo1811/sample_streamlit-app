"""発注エンドポイント"""

from typing import Literal

from backend.app.auth import CurrentUser
from backend.app.dependencies import get_db_session, require_role
from backend.app.schemas import (
    ApproveProposalRequest,
    OrderPlanResponse,
    ProposalResponse,
    SPResultResponse,
)
from fastapi import APIRouter, Depends, HTTPException
from snowflake.snowpark import Session
from src.dal.orders import approve_proposal, execute_order_plan, get_order_plans, get_proposals, reject_proposal
from src.utils.constants import ROLE_MANAGER

router = APIRouter(prefix="/api/orders", tags=["発注"])

ProposalStatus = Literal["生成", "確認中", "承認", "却下"]


def _require_store_id(user: CurrentUser) -> int:
    if user.store_id is None:
        raise HTTPException(status_code=403, detail="店舗が割り当てられていません")
    return user.store_id


@router.get("/proposals", response_model=list[ProposalResponse])
async def list_proposals(
    status: ProposalStatus | None = None,
    user: CurrentUser = Depends(require_role(ROLE_MANAGER)),
    session: Session = Depends(get_db_session),
):
    """発注提案一覧取得"""
    store_id = _require_store_id(user)
    return get_proposals(session, store_id=store_id, status_filter=status)


@router.post("/proposals/{proposal_id}/approve", response_model=SPResultResponse)
async def post_approve_proposal(
    proposal_id: int,
    body: ApproveProposalRequest,
    user: CurrentUser = Depends(require_role(ROLE_MANAGER)),
    session: Session = Depends(get_db_session),
):
    """発注提案を承認"""
    result = approve_proposal(session, proposal_id, body.quantity, user.user_id)
    return SPResultResponse(**result)


@router.post("/proposals/{proposal_id}/reject", response_model=SPResultResponse)
async def post_reject_proposal(
    proposal_id: int,
    user: CurrentUser = Depends(require_role(ROLE_MANAGER)),
    session: Session = Depends(get_db_session),
):
    """発注提案を却下"""
    result = reject_proposal(session, proposal_id, user.user_id)
    return SPResultResponse(**result)


@router.get("/plans", response_model=list[OrderPlanResponse])
async def list_order_plans(
    user: CurrentUser = Depends(require_role(ROLE_MANAGER)),
    session: Session = Depends(get_db_session),
):
    """承認済み発注予定一覧取得"""
    store_id = _require_store_id(user)
    return get_order_plans(session, store_id=store_id)


@router.post("/plans/{plan_id}/execute", response_model=SPResultResponse)
async def post_execute_order_plan(
    plan_id: int,
    user: CurrentUser = Depends(require_role(ROLE_MANAGER)),
    session: Session = Depends(get_db_session),
):
    """発注予定を発注実行"""
    result = execute_order_plan(session, plan_id, user.user_id)
    return SPResultResponse(**result)
