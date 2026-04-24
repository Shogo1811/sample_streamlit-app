"""ステータスバリデーションテスト（validators.pyカバレッジ補完）"""

import pytest

from src.utils.constants import (
    DELIVERY_STATUS_COMPLETED,
    DELIVERY_STATUS_IN_TRANSIT,
    DELIVERY_STATUS_PENDING,
    DELIVERY_TRANSITIONS,
    PROPOSAL_STATUS_APPROVED,
    PROPOSAL_STATUS_GENERATED,
    PROPOSAL_STATUS_REVIEWING,
    PROPOSAL_TRANSITIONS,
)
from src.utils.validators import (
    ValidationError,
    validate_delivery_status,
    validate_proposal_status,
    validate_status_transition,
)


class TestValidateProposalStatus:
    """ホワイトリスト方式のステータス検証"""

    def test_valid_generated(self):
        assert validate_proposal_status(PROPOSAL_STATUS_GENERATED) == PROPOSAL_STATUS_GENERATED

    def test_valid_reviewing(self):
        assert validate_proposal_status(PROPOSAL_STATUS_REVIEWING) == PROPOSAL_STATUS_REVIEWING

    def test_valid_approved(self):
        assert validate_proposal_status(PROPOSAL_STATUS_APPROVED) == PROPOSAL_STATUS_APPROVED

    def test_invalid_status(self):
        with pytest.raises(ValidationError, match="無効なステータスです"):
            validate_proposal_status("不正な値")


class TestValidateDeliveryStatus:
    """ホワイトリスト方式の配送ステータス検証"""

    def test_valid_pending(self):
        assert validate_delivery_status(DELIVERY_STATUS_PENDING) == DELIVERY_STATUS_PENDING

    def test_valid_in_transit(self):
        assert validate_delivery_status(DELIVERY_STATUS_IN_TRANSIT) == DELIVERY_STATUS_IN_TRANSIT

    def test_valid_completed(self):
        assert validate_delivery_status(DELIVERY_STATUS_COMPLETED) == DELIVERY_STATUS_COMPLETED

    def test_invalid_status(self):
        with pytest.raises(ValidationError, match="無効な配送ステータスです"):
            validate_delivery_status("不正な値")


class TestValidateStatusTransition:
    """汎用ステータス遷移バリデーション直接テスト"""

    def test_valid_transition(self):
        result = validate_status_transition(PROPOSAL_STATUS_GENERATED, PROPOSAL_STATUS_REVIEWING, PROPOSAL_TRANSITIONS)
        assert result == PROPOSAL_STATUS_REVIEWING

    def test_invalid_transition(self):
        with pytest.raises(ValidationError, match="変更することはできません"):
            validate_status_transition(DELIVERY_STATUS_COMPLETED, DELIVERY_STATUS_PENDING, DELIVERY_TRANSITIONS)

    def test_unknown_current_status(self):
        with pytest.raises(ValidationError, match="変更することはできません"):
            validate_status_transition("不明", PROPOSAL_STATUS_REVIEWING, PROPOSAL_TRANSITIONS)
