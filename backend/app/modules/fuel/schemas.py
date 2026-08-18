from datetime import date, datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class FuelCouponCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    coupon_number: str = Field(
        min_length=1,
        max_length=50,
    )

    coupon_date: date | None = None

    gas_station: str | None = Field(
        default=None,
        max_length=150,
    )


class FuelCouponResponse(BaseModel):
    id: int
    coupon_number: str
    face_value_q: Decimal
    coupon_date: date | None
    gas_station: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class CommissionCouponAssign(BaseModel):
    coupon_id: int = Field(
        gt=0,
    )


class CommissionCouponResponse(BaseModel):
    id: int
    commission_id: int
    coupon_id: int
    assigned_at: datetime
    used_at: datetime | None
    returned_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True,
    )


class FuelLoadCreate(BaseModel):
    loaded_at: datetime

    gas_station: str = Field(
        min_length=1,
        max_length=150,
    )

    gallons: Decimal = Field(
        gt=0,
        decimal_places=3,
    )

    amount_q: Decimal = Field(
        gt=0,
        multiple_of=Decimal("100.00"),
        decimal_places=2,
    )

class FuelLoadResponse(BaseModel):
    id: int
    commission_id: int
    loaded_at: datetime
    gas_station: str
    gallons: Decimal
    amount_q: Decimal
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
