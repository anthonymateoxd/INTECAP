from datetime import datetime
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

class CommissionStatusResponse(BaseModel):
    id: int
    code: str
    name: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class CommissionCreate(BaseModel):
    vehicle_id: int = Field(
        gt=0,
    )

    scheduled_start_at: datetime
    scheduled_end_at: datetime

    @model_validator(mode="after")
    def validate_schedule(self) -> Self:
        if self.scheduled_end_at <= self.scheduled_start_at:
            raise ValueError(
                "La fecha y hora de fin debe ser posterior "
                "a la fecha y hora de inicio."
            )

        return self

class CommissionResponse(BaseModel):
    id: int
    requester_user_id: int
    vehicle_id: int | None
    status_id: int
    scheduled_start_at: datetime
    scheduled_end_at: datetime
    reviewed_by_user_id: int | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
