from datetime import date
from typing import Literal

from pydantic import BaseModel, model_validator

from datetime import datetime
from decimal import Decimal


class VehicleReportRow(BaseModel):
    inventory_code: str
    license_plate: str
    brand: str
    model: str
    year: int
    vehicle_type: str
    fuel_type: str
    current_odometer_km: Decimal
    tank_capacity_gal: Decimal | None
    status: str
    created_at: datetime

class VehicleReportFilters(BaseModel):
    start_date: date | None = None
    end_date: date | None = None

    status: Literal[
        "ALL",
        "ACTIVE",
        "INACTIVE",
    ] = "ALL"

    @model_validator(mode="after")
    def validate_date_range(self):
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.start_date > self.end_date
        ):
            raise ValueError(
                "La fecha inicial no puede ser posterior a la fecha final."
            )

        return self


class CommissionReportFilters(BaseModel):
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_date_range(self):
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.start_date > self.end_date
        ):
            raise ValueError(
                "La fecha inicial no puede ser posterior a la fecha final."
            )

        return self


class CommissionReportRow(BaseModel):
    requester_name: str
    vehicle: str
    status: str
    scheduled_start_at: datetime
    scheduled_end_at: datetime
    reviewer_name: str | None
    reviewed_at: datetime | None
    created_at: datetime



class TripReportFilters(BaseModel):
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_date_range(self):
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.start_date > self.end_date
        ):
            raise ValueError(
                "La fecha inicial no puede ser posterior a la fecha final."
            )

        return self


class TripReportRow(BaseModel):
    trip_date: date
    vehicle: str
    driver_name: str
    sequence_number: int
    origin: str
    destination: str
    odometer_start_km: Decimal
    odometer_end_km: Decimal
    distance_km: Decimal
    tank_balance_percent: Decimal | None
    road_type: str


class FuelReportFilters(BaseModel):
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_date_range(self):
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.start_date > self.end_date
        ):
            raise ValueError(
                "La fecha inicial no puede ser posterior a la fecha final."
            )

        return self


class FuelReportRow(BaseModel):
    loaded_at: datetime
    requester_name: str
    vehicle: str
    gas_station: str
    gallons: Decimal
    amount_q: Decimal


class MaintenanceReportFilters(BaseModel):
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_date_range(self):
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.start_date > self.end_date
        ):
            raise ValueError(
                "La fecha inicial no puede ser posterior a la fecha final."
            )

        return self


class MaintenanceReportRow(BaseModel):
    maintenance_date: date
    vehicle: str
    maintenance_type: str
    odometer_km: Decimal | None
    workshop: str | None
    cost_q: Decimal | None
    invoice_number: str | None
    description: str | None
    services: str
    parts: str
    next_maintenance_date: date | None
    next_maintenance_odometer_km: Decimal | None
