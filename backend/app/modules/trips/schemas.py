from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class TripCreate(BaseModel):
    driver_user_id: int = Field(
        gt=0,
    )

    trip_date: date

    origin: str = Field(
        max_length=200,
    )

    destination: str = Field(
        max_length=200,
    )

    odometer_start_km: Decimal | None = Field(
    default=None,
    ge=0,
    decimal_places=1,
    )

    odometer_end_km: Decimal = Field(
        ge=0,
        decimal_places=1,
    )

    tank_balance_percent: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        decimal_places=2,
    )

    road_type: Literal["A", "T"]

    @model_validator(mode="after")
    def validate_odometer(self) -> Self:
        if (
            self.odometer_start_km is not None
            and self.odometer_end_km < self.odometer_start_km
        ):
            raise ValueError(
                "El odómetro final no puede ser menor "
                "que el odómetro inicial."
            )

        return self

class TripUpdate(BaseModel):
    driver_user_id: int | None = Field(
        default=None,
        gt=0,
    )

    trip_date: date | None = None

    origin: str | None = Field(
        default=None,
        max_length=200,
    )

    destination: str | None = Field(
        default=None,
        max_length=200,
    )

    odometer_start_km: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=1,
    )

    odometer_end_km: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=1,
    )

    tank_balance_percent: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        decimal_places=2,
    )

    road_type: Literal["A", "T"] | None = None

    @model_validator(mode="after")
    def validate_update(self) -> Self:
        if not self.model_fields_set:
            raise ValueError(
                "Debe proporcionar al menos un campo para actualizar."
            )

        fields_that_cannot_be_null = {
            "driver_user_id",
            "trip_date",
            "origin",
            "destination",
            "odometer_start_km",
            "odometer_end_km",
            "road_type",
        }

        for field_name in fields_that_cannot_be_null:
            if (
                field_name in self.model_fields_set
                and getattr(self, field_name) is None
            ):
                raise ValueError(
                    f"El campo '{field_name}' no puede ser nulo."
                )

        if (
            "odometer_start_km" in self.model_fields_set
            and "odometer_end_km" in self.model_fields_set
            and self.odometer_start_km is not None
            and self.odometer_end_km is not None
            and self.odometer_end_km < self.odometer_start_km
        ):
            raise ValueError(
                "El odómetro final no puede ser menor "
                "que el odómetro inicial."
            )

        return self

class TripResponse(BaseModel):
    id: int
    commission_id: int
    driver_user_id: int
    sequence_number: int
    trip_date: date
    origin: str
    destination: str
    odometer_start_km: Decimal
    odometer_end_km: Decimal
    distance_km: Decimal | None
    tank_balance_percent: Decimal | None
    road_type: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class DeletedTripResponse(TripResponse):
    is_deleted: bool
    deleted_at: datetime | None
    deleted_by_user_id: int | None
