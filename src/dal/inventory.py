"""在庫データアクセスモジュール"""

from snowflake.snowpark import Session
from snowflake.snowpark.functions import col


def get_ingredients(session: Session) -> list[dict]:
    """食材マスタ取得"""
    df = session.table("APP.INGREDIENTS").select("INGREDIENT_ID", "INGREDIENT_NAME", "CATEGORY", "UNIT", "THRESHOLD")
    return [row.as_dict() for row in df.collect()]


def get_categories(session: Session) -> list[str]:
    """食材カテゴリ一覧取得（フィルタ用）"""
    df = session.table("APP.INGREDIENTS").select("CATEGORY").distinct()
    return [row["CATEGORY"] for row in df.collect()]


def get_inventory(session: Session, store_id: int | None = None) -> list[dict]:
    """在庫データ取得

    store_id: 指定時はその店舗のみ（RLS代替）
    """
    inv = session.table("APP.INVENTORY")
    ing = session.table("APP.INGREDIENTS")
    if store_id is not None:
        inv = inv.filter(col("STORE_ID") == store_id)
    df = inv.join(ing, on="INGREDIENT_ID").select(
        inv["STORE_ID"],
        ing["INGREDIENT_NAME"],
        ing["CATEGORY"],
        inv["CURRENT_QUANTITY"],
        ing["THRESHOLD"],
        ing["UNIT"],
        inv["UPDATED_AT"],
    )
    return [row.as_dict() for row in df.collect()]


def get_low_stock_items(session: Session, store_id: int | None = None) -> list[dict]:
    """閾値以下の食材取得（アラート用）"""
    inv = session.table("APP.INVENTORY")
    ing = session.table("APP.INGREDIENTS")
    if store_id is not None:
        inv = inv.filter(col("STORE_ID") == store_id)
    df = (
        inv.join(ing, on="INGREDIENT_ID")
        .filter(inv["CURRENT_QUANTITY"] <= ing["THRESHOLD"])
        .select(
            ing["INGREDIENT_NAME"],
            ing["CATEGORY"],
            inv["CURRENT_QUANTITY"],
            ing["THRESHOLD"],
            ing["UNIT"],
        )
    )
    return [row.as_dict() for row in df.collect()]
