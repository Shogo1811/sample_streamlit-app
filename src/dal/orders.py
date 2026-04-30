"""発注提案データアクセスモジュール"""

from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, lit

from src.dal.utils import parse_sp_result


def get_proposals(
    session: Session,
    store_id: int | None = None,
    status_filter: str | None = None,
) -> list[dict]:
    """発注提案リスト取得

    store_id: 指定時はその店舗のみ（RLS代替）
    """
    op = session.table("APP.ORDER_PROPOSALS")
    ing = session.table("APP.INGREDIENTS")
    if store_id is not None:
        op = op.filter(col("STORE_ID") == store_id)
    if status_filter:
        op = op.filter(col("STATUS") == lit(status_filter))
    df = op.join(ing, on="INGREDIENT_ID").select(
        op["PROPOSAL_ID"],
        ing["INGREDIENT_NAME"],
        ing["CATEGORY"],
        op["RECOMMENDED_QUANTITY"],
        op["REASON"],
        op["STATUS"],
        op["CREATED_AT"],
    )
    return [row.as_dict() for row in df.collect()]


def approve_proposal(session: Session, proposal_id: int, quantity: int, user_id: str) -> dict:
    """発注提案の承認（SP経由）"""
    result = session.sql(
        "CALL APP.SP_APPROVE_ORDER_PROPOSAL(?, ?, ?)",
        params=[proposal_id, quantity, user_id],
    ).collect()
    return parse_sp_result(result)


def reject_proposal(session: Session, proposal_id: int, user_id: str) -> dict:
    """発注提案の却下（SP経由）"""
    result = session.sql(
        "CALL APP.SP_REJECT_ORDER_PROPOSAL(?, ?)",
        params=[proposal_id, user_id],
    ).collect()
    return parse_sp_result(result)


def execute_order_plan(session: Session, plan_id: int, user_id: str) -> dict:
    """発注予定の発注実行（SP経由）"""
    result = session.sql(
        "CALL APP.SP_EXECUTE_ORDER_PLAN(?, ?)",
        params=[plan_id, user_id],
    ).collect()
    return parse_sp_result(result)


def get_order_plans(session: Session, store_id: int | None = None) -> list[dict]:
    """承認済み発注予定リスト取得"""
    op = session.table("APP.ORDER_PLANS")
    pr = session.table("APP.ORDER_PROPOSALS")
    ing = session.table("APP.INGREDIENTS")
    if store_id is not None:
        pr = pr.filter(col("STORE_ID") == store_id)
    df = (
        op.join(pr, on="PROPOSAL_ID")
        .join(ing, pr["INGREDIENT_ID"] == ing["INGREDIENT_ID"])
        .select(
            op["PLAN_ID"],
            ing["INGREDIENT_NAME"],
            op["QUANTITY"],
            op["APPROVED_BY"],
            op["APPROVED_AT"],
            op["STATUS"].alias("STATUS"),
            op["EXECUTED_BY"],
            op["EXECUTED_AT"],
        )
    )
    return [row.as_dict() for row in df.collect()]
