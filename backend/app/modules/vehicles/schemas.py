from datetime import datetime
from decimal import Decimal

from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

class VehicleCreate(BaseModel):
    inventory_code: str = Field(
        max_length=50,
    )

    license_plate: str = Field(
        max_length=20,
    )

    brand: str = Field(
        max_length=80,
    )

    model: str = Field(
        max_length=80,
    )

    year: int = Field(
        ge=1900,
    )

    vehicle_type: str = Field(
        max_length=80,
    )

    fuel_type: str = Field(
        max_length=30,
    )

    current_odometer_km: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        decimal_places=1,
    )

    tank_capacity_gal: Decimal | None = Field(
        default=None,
        gt=0,
        decimal_places=3,
    )

class VehicleUpdate(BaseModel):
    inventory_code: str | None = Field(
        default=None,
        max_length=50,
    )

    license_plate: str | None = Field(
        default=None,
        max_length=20,
    )

    brand: str | None = Field(
        default=None,
        max_length=80,
    )

    model: str | None = Field(
        default=None,
        max_length=80,
    )

    year: int | None = Field(
        default=None,
        ge=1900,
    )

    vehicle_type: str | None = Field(
        default=None,
        max_length=80,
    )

    fuel_type: str | None = Field(
        default=None,
        max_length=30,
    )

    current_odometer_km: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=1,
    )

    tank_capacity_gal: Decimal | None = Field(
        default=None,
        gt=0,
        decimal_places=3,
    )


    @model_validator(mode="after")
    def validate_update(self) -> Self:
        if not self.model_fields_set:
            raise ValueError(
                "Debe enviar al menos un campo para actualizar."
            )

        nullable_fields = {
            "tank_capacity_gal",
        }

        for field_name in self.model_fields_set:
            if (
                field_name not in nullable_fields
                and getattr(self, field_name) is None
            ):
                raise ValueError(
                    f"El campo '{field_name}' no puede ser null."
                )

        return self
    
    
    
    # @model_validator(mode="after")
    # def validate_update(self) -> Self:
    #     if not self.model_fields_set:
    #         raise ValueError(
    #             "Debe enviar al menos un campo para actualizar."
    #         )

    #     nullable_fields = {
    #         "tank_capacity_gal",
    #     }

    #     for field_name in self.model_fields_set:
    #         if (
    #             field_name not in nullable_fields
    #             and getattr(self, field_name) is None
    #         ):
    #             raise ValueError(
    #                 f"El campo '{field_name}' no puede ser null."
    #             )

    #     return self
    
    
class VehicleStatusUpdate(BaseModel):
    is_active: bool 
    
class VehicleResponse(BaseModel):
    id: int
    inventory_code: str
    license_plate: str
    brand: str
    model: str
    year: int
    vehicle_type: str
    fuel_type: str
    current_odometer_km: Decimal
    tank_capacity_gal: Decimal | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )