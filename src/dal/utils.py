"""DAL共通ユーティリティ"""

import json


def parse_sp_result(result) -> dict:
    """SP戻り値をパース（VARIANT型のJSON文字列対応）"""
    if not result:
        return {"success": False, "message": "SP呼出エラー"}
    raw = result[0][0]
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"success": False, "message": f"SP結果のパースに失敗: {raw[:100]}"}
    return raw
