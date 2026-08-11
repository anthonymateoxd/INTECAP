from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.vehicles.model import Vehicle
from decimal import Decimal


def get_vehicles(
    db: Session,
) -> list[Vehicle]:
    statement = (
        select(Vehicle)
        .order_by(Vehicle.id)
    )

    return list(
        db.scalars(statement).all()
    )


def get_vehicle_by_id(
    db: Session,
    vehicle_id: int,
) -> Vehicle | None:
    statement = (
        select(Vehicle)
        .where(Vehicle.id == vehicle_id)
    )

    return db.scalars(statement).first()


def get_vehicle_by_inventory_code(
    db: Session,
    inventory_code: str,
) -> Vehicle | None:
    statement = (
        select(Vehicle)
        .where(
            func.lower(Vehicle.inventory_code)
            == inventory_code.lower()
        )
    )

    return db.scalars(statement).first()


def get_vehicle_by_license_plate(
    db: Session,
    license_plate: str,
) -> Vehicle | None:
    statement = (
        select(Vehicle)
        .where(
            func.lower(Vehicle.license_plate)
            == license_plate.lower()
        )
    )

    return db.scalars(statement).first()


def create_vehicle(
    db: Session,
    *,
    inventory_code: str,
    license_plate: str,
    brand: str,
    model: str,
    year: int,
    vehicle_type: str,
    fuel_type: str,
    current_odometer_km: Decimal,
    tank_capacity_gal: Decimal | None,
) -> Vehicle:
    vehicle = Vehicle(
        inventory_code=inventory_code,
        license_plate=license_plate,
        brand=brand,
        model=model,
        year=year,
        vehicle_type=vehicle_type,
        fuel_type=fuel_type,
        current_odometer_km=current_odometer_km,
        tank_capacity_gal=tank_capacity_gal,
    )

    db.add(vehicle)
    db.flush()
    db.refresh(vehicle)

    return vehicle



def update_vehicle(
    db: Session,
    vehicle: Vehicle,
    update_data: dict,
) -> Vehicle:
    for field, value in update_data.items():
        setattr(
            vehicle,
            field,
            value,
        )

    db.flush()
    db.refresh(vehicle)

    return vehicle