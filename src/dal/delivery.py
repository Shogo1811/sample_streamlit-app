"""配送データアクセスモジュール

キャッシュ方針: 配送データはリアルタイム性が重要なため、意図的にキャッシュを適用しない。
"""

from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, lit

from src.dal.utils import parse_sp_result


def get_deliveries(
    session: Session,
    store_id: int | None = None,
    status_filter: str | None = None,
) -> list[dict]:
    """配送一覧取得（店長向け）

    store_id: 指定時はその店舗のみ（RLS代替）
    """
    dl = session.table("APP.DELIVERIES")
    st_tbl = session.table("APP.STORES")
    dr = session.table("APP.DRIVERS")
    if store_id is not None:
        dl = dl.filter(col("STORE_ID") == store_id)
    if status_filter:
        dl = dl.filter(col("STATUS") == lit(status_filter))
    df = (
        dl.join(st_tbl, on="STORE_ID")
        .join(dr, on="DRIVER_ID")
        .select(
            dl["DELIVERY_ID"],
            st_tbl["STORE_NAME"],
            dr["DRIVER_NAME"],
            dl["STATUS"],
            dl["SCHEDULED_AT"],
            dl["COMPLETED_AT"],
        )
    )
    return [row.as_dict() for row in df.collect()]


def get_driver_deliveries(session: Session, driver_id: int | None = None) -> list[dict]:
    """ドライバー向け配送リスト取得

    driver_id: 指定時はそのドライバーのみ（RLS代替）
    """
    dl = session.table("APP.DELIVERIES")
    st_tbl = session.table("APP.STORES")
    if driver_id is not None:
        dl = dl.filter(col("DRIVER_ID") == driver_id)
    df = (
        dl.join(st_tbl, on="STORE_ID")
        .select(
            dl["DELIVERY_ID"],
            st_tbl["STORE_NAME"],
            dl["STATUS"],
            dl["SCHEDULED_AT"],
        )
        .sort(dl["SCHEDULED_AT"])
    )
    return [row.as_dict() for row in df.collect()]


def complete_delivery(session: Session, delivery_id: int, user_id: str) -> dict:
    """配送完了報告（SP経由）"""
    result = session.sql(
        "CALL APP.SP_COMPLETE_DELIVERY(?, ?)",
        params=[delivery_id, user_id],
    ).collect()
    return parse_sp_result(result)
