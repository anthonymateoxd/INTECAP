from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MaintenancePartCreate(BaseModel):
    part_name: str = Field(
        min_length=1,
        max_length=150,
    )

    quantity: int = Field(
        default=1,
        gt=0,
    )


class MaintenancePartResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    maintenance_event_id: int
    part_name: str
    quantity: int
    created_at: datetime


class ServiceTypeCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
    )

    interval_km: Decimal | None = Field(
        default=None,
        gt=0,
        decimal_places=1,
    )

    interval_days: int | None = Field(
        default=None,
        gt=0,
    )


class ServiceTypeResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    name: str
    interval_km: Decimal | None
    interval_days: int | None
    is_active: bool
    created_at: datetime


class MaintenanceEventCreate(BaseModel):
    vehicle_id: int = Field(
        gt=0,
    )

    maintenance_type: Literal[
        "PREVENTIVO",
        "CORRECTIVO",
    ]

    maintenance_date: date

    odometer_km: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=1,
    )

    workshop: str | None = Field(
        default=None,
        max_length=150,
    )

    cost_q: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=2,
    )

    invoice_number: str | None = Field(
        default=None,
        max_length=100,
    )

    description: str | None = None

    next_maintenance_date: date | None = None

    next_maintenance_odometer_km: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=1,
    )

    service_type_ids: list[int] = Field(
        default_factory=list,
    )

    parts: list[MaintenancePartCreate] = Field(
        default_factory=list,
    )


class MaintenanceEventResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    vehicle_id: int
    maintenance_type: str
    maintenance_date: date
    odometer_km: Decimal | None

    workshop: str | None
    cost_q: Decimal | None
    invoice_number: str | None
    description: str | None

    next_maintenance_date: date | None
    next_maintenance_odometer_km: Decimal | None

    created_at: datetime

    services: list[ServiceTypeResponse] = Field(
        default_factory=list,
    )

    parts: list[MaintenancePartResponse] = Field(
        default_factory=list,
    )

from pydantic import model_validator


class ServiceTypeUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    interval_km: Decimal | None = Field(
        default=None,
        gt=0,
        decimal_places=1,
    )

    interval_days: int | None = Field(
        default=None,
        gt=0,
    )

    @model_validator(mode="after")
    def validate_not_empty(self):
        if not self.model_fields_set:
            raise ValueError(
                "Debe proporcionar al menos un campo para actualizar."
            )

        if "name" in self.model_fields_set and self.name is None:
            raise ValueError(
                "El nombre no puede ser nulo."
            )

        return self


class MaintenanceEventUpdate(BaseModel):
    vehicle_id: int | None = Field(
        default=None,
        gt=0,
    )

    maintenance_type: Literal[
        "PREVENTIVO",
        "CORRECTIVO",
    ] | None = None

    maintenance_date: date | None = None

    odometer_km: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=1,
    )

    workshop: str | None = Field(
        default=None,
        max_length=150,
    )

    cost_q: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=2,
    )

    invoice_number: str | None = Field(
        default=None,
        max_length=100,
    )

    description: str | None = None

    next_maintenance_date: date | None = None

    next_maintenance_odometer_km: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=1,
    )

    service_type_ids: list[int] | None = None

    parts: list[MaintenancePartCreate] | None = None

    @model_validator(mode="after")
    def validate_update(self):
        if not self.model_fields_set:
            raise ValueError(
                "Debe proporcionar al menos un campo para actualizar."
            )

        required_fields = {
            "vehicle_id",
            "maintenance_type",
            "maintenance_date",
        }

        for field_name in required_fields:
            if (
                field_name in self.model_fields_set
                and getattr(self, field_name) is None
            ):
                raise ValueError(
                    f"{field_name} no puede ser nulo."
                )

        if self.service_type_ids is not None:
            if any(
                service_type_id <= 0
                for service_type_id in self.service_type_ids
            ):
                raise ValueError(
                    "Los identificadores de servicios deben ser mayores que cero."
                )

        return self
