"""Pydantic スキーマ定義"""

from datetime import datetime

from pydantic import BaseModel, Field
from src.utils.constants import ORDER_QUANTITY_MAX, ORDER_QUANTITY_MIN

# --- リクエスト ---


class ApproveProposalRequest(BaseModel):
    quantity: int = Field(ge=ORDER_QUANTITY_MIN, le=ORDER_QUANTITY_MAX)


class ConsentRequest(BaseModel):
    policy_version: str


# --- レスポンス ---


class UserResponse(BaseModel):
    user_id: str
    roles: list[str]
    store_id: int | None = None
    driver_id: int | None = None


class ConsentStatusResponse(BaseModel):
    consented: bool
    policy_version: str


class IngredientResponse(BaseModel):
    ingredient_id: int = Field(validation_alias="INGREDIENT_ID")
    ingredient_name: str = Field(validation_alias="INGREDIENT_NAME")
    category: str = Field(validation_alias="CATEGORY")
    unit: str = Field(validation_alias="UNIT")
    threshold: int = Field(validation_alias="THRESHOLD")


class InventoryResponse(BaseModel):
    store_id: int = Field(validation_alias="STORE_ID")
    ingredient_name: str = Field(validation_alias="INGREDIENT_NAME")
    category: str = Field(validation_alias="CATEGORY")
    current_quantity: int = Field(validation_alias="CURRENT_QUANTITY")
    threshold: int = Field(validation_alias="THRESHOLD")
    unit: str = Field(validation_alias="UNIT")
    updated_at: datetime = Field(validation_alias="UPDATED_AT")


class LowStockResponse(BaseModel):
    ingredient_name: str = Field(validation_alias="INGREDIENT_NAME")
    category: str = Field(validation_alias="CATEGORY")
    current_quantity: int = Field(validation_alias="CURRENT_QUANTITY")
    threshold: int = Field(validation_alias="THRESHOLD")
    unit: str = Field(validation_alias="UNIT")


class ProposalResponse(BaseModel):
    proposal_id: int = Field(validation_alias="PROPOSAL_ID")
    ingredient_name: str = Field(validation_alias="INGREDIENT_NAME")
    category: str = Field(validation_alias="CATEGORY")
    recommended_quantity: int = Field(validation_alias="RECOMMENDED_QUANTITY")
    reason: str = Field(validation_alias="REASON")
    status: str = Field(validation_alias="STATUS")
    created_at: datetime = Field(validation_alias="CREATED_AT")


class OrderPlanResponse(BaseModel):
    plan_id: int = Field(validation_alias="PLAN_ID")
    ingredient_name: str = Field(validation_alias="INGREDIENT_NAME")
    quantity: int = Field(validation_alias="QUANTITY")
    approved_by: str = Field(validation_alias="APPROVED_BY")
    approved_at: datetime = Field(validation_alias="APPROVED_AT")
    status: str = Field(validation_alias="STATUS")
    executed_by: str | None = Field(default=None, validation_alias="EXECUTED_BY")
    executed_at: datetime | None = Field(default=None, validation_alias="EXECUTED_AT")


class DeliveryResponse(BaseModel):
    delivery_id: int = Field(validation_alias="DELIVERY_ID")
    store_name: str = Field(validation_alias="STORE_NAME")
    driver_name: str = Field(validation_alias="DRIVER_NAME")
    status: str = Field(validation_alias="STATUS")
    scheduled_at: datetime = Field(validation_alias="SCHEDULED_AT")
    completed_at: datetime | None = Field(default=None, validation_alias="COMPLETED_AT")


class DriverDeliveryResponse(BaseModel):
    delivery_id: int = Field(validation_alias="DELIVERY_ID")
    store_name: str = Field(validation_alias="STORE_NAME")
    status: str = Field(validation_alias="STATUS")
    scheduled_at: datetime = Field(validation_alias="SCHEDULED_AT")


class SPResultResponse(BaseModel):
    success: bool
    message: str
