"""入力バリデーションモジュール（NFR-09準拠）"""

from src.utils.constants import (
    DELIVERY_STATUSES,
    DELIVERY_TRANSITIONS,
    ORDER_QUANTITY_MAX,
    ORDER_QUANTITY_MIN,
    PROPOSAL_STATUSES,
    PROPOSAL_TRANSITIONS,
)


class ValidationError(Exception):
    """バリデーションエラー"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


def validate_order_quantity(quantity: object) -> int:
    """発注数量のバリデーション（NFR-09: 1以上10,000以下の整数）"""
    if quantity is None:
        raise ValidationError("発注数量を入力してください。")
    if isinstance(quantity, float) and not quantity.is_integer():
        raise ValidationError("発注数量は整数で入力してください。")
    try:
        qty = int(quantity)
    except (ValueError, TypeError) as err:
        raise ValidationError("発注数量は整数で入力してください。") from err
    if qty < ORDER_QUANTITY_MIN:
        raise ValidationError(f"発注数量は{ORDER_QUANTITY_MIN}以上で入力してください。")
    if qty > ORDER_QUANTITY_MAX:
        raise ValidationError(f"発注数量は{ORDER_QUANTITY_MAX}以下で入力してください。")
    return qty


def validate_proposal_status(status: str) -> str:
    """発注提案ステータスのバリデーション（ホワイトリスト方式）"""
    if status not in PROPOSAL_STATUSES:
        raise ValidationError(f"無効なステータスです: {status}")
    return status


def validate_delivery_status(status: str) -> str:
    """配送ステータスのバリデーション（ホワイトリスト方式）"""
    if status not in DELIVERY_STATUSES:
        raise ValidationError(f"無効な配送ステータスです: {status}")
    return status


def validate_status_transition(
    current_status: str,
    new_status: str,
    transitions: dict[str, list[str]],
) -> str:
    """ステータス遷移のバリデーション（逆遷移不可）"""
    allowed = transitions.get(current_status, [])
    if new_status not in allowed:
        raise ValidationError(f"ステータスを「{current_status}」から「{new_status}」に変更することはできません。")
    return new_status


def validate_proposal_transition(current: str, new: str) -> str:
    """発注提案ステータス遷移バリデーション"""
    return validate_status_transition(current, new, PROPOSAL_TRANSITIONS)


def validate_delivery_transition(current: str, new: str) -> str:
    """配送ステータス遷移バリデーション"""
    return validate_status_transition(current, new, DELIVERY_TRANSITIONS)
