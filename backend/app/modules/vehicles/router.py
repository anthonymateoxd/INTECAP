from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import (
    InventoryCodeAlreadyRegisteredError,
    LicensePlateAlreadyRegisteredError,
    VehicleNotFoundError,
)
from app.database.dependencies import get_db
from app.modules.auth.dependencies import (
    get_current_user,
    require_administration,
)
from app.modules.users.model import User
from app.modules.vehicles import service
from app.modules.vehicles.schemas import (
    VehicleCreate,
    VehicleResponse,
    VehicleStatusUpdate,
    VehicleUpdate,
)


router = APIRouter(
    prefix="/vehicles",
    tags=["Vehicles"],
)


@router.get(
    "",
    response_model=list[VehicleResponse],
)
def get_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.list_vehicles(db)


@router.get(
    "/{vehicle_id}",
    response_model=VehicleResponse,
)
def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vehicle = service.get_vehicle(
        db,
        vehicle_id,
    )

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado.",
        )

    return vehicle


@router.post(
    "",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
)


def create_vehicle(
    vehicle_data: VehicleCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_administration),
):
    try:
        return service.create_vehicle(
            db,
            vehicle_data,
        )

    except InventoryCodeAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un vehículo con ese código de inventario.",
        ) from None

    except LicensePlateAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un vehículo con esa placa.",
        ) from None
        
        
        
@router.patch(
    "/{vehicle_id}",
    response_model=VehicleResponse,
)
def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_administration),
):
    try:
        return service.update_vehicle(
            db,
            vehicle_id,
            vehicle_data,
        )

    except VehicleNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado.",
        ) from None

    except InventoryCodeAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un vehículo con ese código de inventario.",
        ) from None

    except LicensePlateAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un vehículo con esa placa.",
        ) from None
        
@router.patch(
    "/{vehicle_id}/status",
    response_model=VehicleResponse,
)
def update_vehicle_status(
    vehicle_id: int,
    status_data: VehicleStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_administration),
):
    try:
        return service.update_vehicle_status(
            db,
            vehicle_id,
            status_data,
        )

    except VehicleNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado.",
        ) from None