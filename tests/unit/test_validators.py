"""バリデーションテスト（BVA含む — NFR-09, NFR-23準拠）"""

import pytest

from src.utils.constants import (
    DELIVERY_STATUS_COMPLETED,
    DELIVERY_STATUS_IN_TRANSIT,
    DELIVERY_STATUS_PENDING,
    PROPOSAL_STATUS_APPROVED,
    PROPOSAL_STATUS_GENERATED,
    PROPOSAL_STATUS_REJECTED,
    PROPOSAL_STATUS_REVIEWING,
)
from src.utils.validators import (
    ValidationError,
    validate_delivery_transition,
    validate_order_quantity,
    validate_proposal_transition,
)

# ============================================================
# 発注数量バリデーション（BVA: 0/1/10000/10001/-1/null/小数/文字列）
# ============================================================


class TestValidateOrderQuantity:
    """NFR-09: 発注数量は1以上10,000以下の整数"""

    def test_valid_minimum(self):
        assert validate_order_quantity(1) == 1

    def test_valid_maximum(self):
        assert validate_order_quantity(10000) == 10000

    def test_valid_middle(self):
        assert validate_order_quantity(500) == 500

    def test_invalid_zero(self):
        with pytest.raises(ValidationError, match="1以上"):
            validate_order_quantity(0)

    def test_invalid_over_max(self):
        with pytest.raises(ValidationError, match="10000以下"):
            validate_order_quantity(10001)

    def test_invalid_negative(self):
        with pytest.raises(ValidationError, match="1以上"):
            validate_order_quantity(-1)

    def test_invalid_none(self):
        with pytest.raises(ValidationError, match="入力してください"):
            validate_order_quantity(None)

    def test_invalid_float(self):
        with pytest.raises(ValidationError, match="整数"):
            validate_order_quantity(1.5)

    def test_valid_float_integer(self):
        """整数値のfloat（例: 5.0）は許容"""
        assert validate_order_quantity(5.0) == 5

    def test_invalid_string(self):
        with pytest.raises(ValidationError, match="整数"):
            validate_order_quantity("abc")

    def test_invalid_empty_string(self):
        with pytest.raises(ValidationError, match="整数"):
            validate_order_quantity("")


# ============================================================
# 発注提案ステータス遷移（逆遷移不可）
# ============================================================


class TestValidateProposalTransition:
    """状態遷移: 生成→確認中→承認/却下（逆遷移不可）"""

    def test_generated_to_reviewing(self):
        result = validate_proposal_transition(PROPOSAL_STATUS_GENERATED, PROPOSAL_STATUS_REVIEWING)
        assert result == PROPOSAL_STATUS_REVIEWING

    def test_reviewing_to_approved(self):
        result = validate_proposal_transition(PROPOSAL_STATUS_REVIEWING, PROPOSAL_STATUS_APPROVED)
        assert result == PROPOSAL_STATUS_APPROVED

    def test_reviewing_to_rejected(self):
        result = validate_proposal_transition(PROPOSAL_STATUS_REVIEWING, PROPOSAL_STATUS_REJECTED)
        assert result == PROPOSAL_STATUS_REJECTED

    def test_invalid_approved_to_reviewing(self):
        """逆遷移不可: 承認→確認中"""
        with pytest.raises(ValidationError, match="変更することはできません"):
            validate_proposal_transition(PROPOSAL_STATUS_APPROVED, PROPOSAL_STATUS_REVIEWING)

    def test_invalid_rejected_to_approved(self):
        """逆遷移不可: 却下→承認"""
        with pytest.raises(ValidationError, match="変更することはできません"):
            validate_proposal_transition(PROPOSAL_STATUS_REJECTED, PROPOSAL_STATUS_APPROVED)

    def test_invalid_generated_to_approved(self):
        """スキップ不可: 生成→承認"""
        with pytest.raises(ValidationError, match="変更することはできません"):
            validate_proposal_transition(PROPOSAL_STATUS_GENERATED, PROPOSAL_STATUS_APPROVED)

    def test_invalid_approved_to_generated(self):
        """逆遷移不可: 承認→生成"""
        with pytest.raises(ValidationError, match="変更することはできません"):
            validate_proposal_transition(PROPOSAL_STATUS_APPROVED, PROPOSAL_STATUS_GENERATED)


# ============================================================
# 配送ステータス遷移（逆遷移不可）
# ============================================================


class TestValidateDeliveryTransition:
    """状態遷移: 未配送→配送中→配送完了（逆遷移不可）"""

    def test_pending_to_in_transit(self):
        result = validate_delivery_transition(DELIVERY_STATUS_PENDING, DELIVERY_STATUS_IN_TRANSIT)
        assert result == DELIVERY_STATUS_IN_TRANSIT

    def test_in_transit_to_completed(self):
        result = validate_delivery_transition(DELIVERY_STATUS_IN_TRANSIT, DELIVERY_STATUS_COMPLETED)
        assert result == DELIVERY_STATUS_COMPLETED

    def test_invalid_completed_to_in_transit(self):
        """逆遷移不可: 配送完了→配送中"""
        with pytest.raises(ValidationError, match="変更することはできません"):
            validate_delivery_transition(DELIVERY_STATUS_COMPLETED, DELIVERY_STATUS_IN_TRANSIT)

    def test_invalid_completed_to_pending(self):
        """逆遷移不可: 配送完了→未配送"""
        with pytest.raises(ValidationError, match="変更することはできません"):
            validate_delivery_transition(DELIVERY_STATUS_COMPLETED, DELIVERY_STATUS_PENDING)

    def test_invalid_in_transit_to_pending(self):
        """逆遷移不可: 配送中→未配送"""
        with pytest.raises(ValidationError, match="変更することはできません"):
            validate_delivery_transition(DELIVERY_STATUS_IN_TRANSIT, DELIVERY_STATUS_PENDING)

    def test_invalid_pending_to_completed(self):
        """スキップ不可: 未配送→配送完了"""
        with pytest.raises(ValidationError, match="変更することはできません"):
            validate_delivery_transition(DELIVERY_STATUS_PENDING, DELIVERY_STATUS_COMPLETED)
