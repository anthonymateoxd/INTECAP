from sqlalchemy.orm import Session

from app.core.exceptions import (
    InventoryCodeAlreadyRegisteredError,
    LicensePlateAlreadyRegisteredError,
    VehicleNotFoundError,
)
from app.modules.vehicles import repository
from app.modules.vehicles.model import Vehicle
from app.modules.vehicles.schemas import (
    VehicleCreate,
    VehicleStatusUpdate,
    VehicleUpdate,
)

def list_vehicles(
    db: Session,
) -> list[Vehicle]:
    return repository.get_vehicles(db)


def get_vehicle(
    db: Session,
    vehicle_id: int,
) -> Vehicle | None:
    return repository.get_vehicle_by_id(
        db,
        vehicle_id,
    )


def create_vehicle(
    db: Session,
    vehicle_data: VehicleCreate,
) -> Vehicle:
    existing_inventory_code = (
        repository.get_vehicle_by_inventory_code(
            db,
            vehicle_data.inventory_code,
        )
    )

    if existing_inventory_code is not None:
        raise InventoryCodeAlreadyRegisteredError()

    existing_license_plate = (
        repository.get_vehicle_by_license_plate(
            db,
            vehicle_data.license_plate,
        )
    )

    if existing_license_plate is not None:
        raise LicensePlateAlreadyRegisteredError()

    try:
        vehicle = repository.create_vehicle(
            db,
            inventory_code=vehicle_data.inventory_code,
            license_plate=vehicle_data.license_plate,
            brand=vehicle_data.brand,
            model=vehicle_data.model,
            year=vehicle_data.year,
            vehicle_type=vehicle_data.vehicle_type,
            fuel_type=vehicle_data.fuel_type,
            current_odometer_km=vehicle_data.current_odometer_km,
            tank_capacity_gal=vehicle_data.tank_capacity_gal,
        )

        db.commit()
        db.refresh(vehicle)

        return vehicle

    except Exception:
        db.rollback()
        raise


def update_vehicle(
    db: Session,
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
) -> Vehicle:
    vehicle = repository.get_vehicle_by_id(
        db,
        vehicle_id,
    )

    if vehicle is None:
        raise VehicleNotFoundError()

    update_data = vehicle_data.model_dump(
        exclude_unset=True,
    )

    if "inventory_code" in update_data:
        existing_vehicle = (
            repository.get_vehicle_by_inventory_code(
                db,
                update_data["inventory_code"],
            )
        )

        if (
            existing_vehicle is not None
            and existing_vehicle.id != vehicle.id
        ):
            raise InventoryCodeAlreadyRegisteredError()

    if "license_plate" in update_data:
        existing_vehicle = (
            repository.get_vehicle_by_license_plate(
                db,
                update_data["license_plate"],
            )
        )

        if (
            existing_vehicle is not None
            and existing_vehicle.id != vehicle.id
        ):
            raise LicensePlateAlreadyRegisteredError()

    try:
        updated_vehicle = repository.update_vehicle(
            db,
            vehicle,
            update_data,
        )

        db.commit()
        db.refresh(updated_vehicle)

        return updated_vehicle

    except Exception:
        db.rollback()
        raise
    
    
def update_vehicle_status(
    db: Session,
    vehicle_id: int,
    status_data: VehicleStatusUpdate,
) -> Vehicle:
    vehicle = repository.get_vehicle_by_id(
        db,
        vehicle_id,
    )

    if vehicle is None:
        raise VehicleNotFoundError()

    try:
        updated_vehicle = repository.update_vehicle(
            db,
            vehicle,
            {
                "is_active": status_data.is_active,
            },
        )

        db.commit()
        db.refresh(updated_vehicle)

        return updated_vehicle

    except Exception:
        db.rollback()
        raise