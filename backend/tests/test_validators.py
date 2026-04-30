"""バリデーションユニットテスト"""

import pytest
from src.utils.validators import (
    ValidationError,
    validate_delivery_status,
    validate_delivery_transition,
    validate_order_quantity,
    validate_proposal_status,
    validate_proposal_transition,
)


class TestValidateOrderQuantity:
    """発注数量バリデーション"""

    def test_valid_min(self):
        assert validate_order_quantity(1) == 1

    def test_valid_max(self):
        assert validate_order_quantity(10000) == 10000

    def test_valid_mid(self):
        assert validate_order_quantity(500) == 500

    def test_below_min(self):
        with pytest.raises(ValidationError):
            validate_order_quantity(0)

    def test_above_max(self):
        with pytest.raises(ValidationError):
            validate_order_quantity(10001)

    def test_negative(self):
        with pytest.raises(ValidationError):
            validate_order_quantity(-1)

    def test_none(self):
        with pytest.raises(ValidationError):
            validate_order_quantity(None)

    def test_string(self):
        with pytest.raises(ValidationError):
            validate_order_quantity("abc")

    def test_float_integer(self):
        assert validate_order_quantity(5.0) == 5

    def test_float_non_integer(self):
        with pytest.raises(ValidationError):
            validate_order_quantity(5.5)


class TestValidateProposalStatus:
    """発注提案ステータスバリデーション"""

    def test_valid_statuses(self):
        for s in ["生成", "確認中", "承認", "却下"]:
            assert validate_proposal_status(s) == s

    def test_invalid_status(self):
        with pytest.raises(ValidationError):
            validate_proposal_status("不明")


class TestValidateDeliveryStatus:
    """配送ステータスバリデーション"""

    def test_valid_statuses(self):
        for s in ["未配送", "配送中", "配送完了"]:
            assert validate_delivery_status(s) == s

    def test_invalid_status(self):
        with pytest.raises(ValidationError):
            validate_delivery_status("不明")


class TestValidateProposalTransition:
    """発注提案ステータス遷移"""

    def test_valid_transitions(self):
        assert validate_proposal_transition("生成", "確認中") == "確認中"
        assert validate_proposal_transition("確認中", "承認") == "承認"
        assert validate_proposal_transition("確認中", "却下") == "却下"

    def test_invalid_reverse(self):
        with pytest.raises(ValidationError):
            validate_proposal_transition("承認", "確認中")

    def test_invalid_skip(self):
        with pytest.raises(ValidationError):
            validate_proposal_transition("生成", "承認")


class TestValidateDeliveryTransition:
    """配送ステータス遷移"""

    def test_valid_transitions(self):
        assert validate_delivery_transition("未配送", "配送中") == "配送中"
        assert validate_delivery_transition("配送中", "配送完了") == "配送完了"

    def test_invalid_reverse(self):
        with pytest.raises(ValidationError):
            validate_delivery_transition("配送完了", "配送中")
