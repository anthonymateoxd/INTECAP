from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import (
    MaintenanceEventAlreadyDeletedError,
    MaintenanceEventNotFoundError,
    MaintenanceOperationNotAllowedError,
    ServiceTypeInactiveError,
    ServiceTypeNameAlreadyExistsError,
    ServiceTypeNotFoundError,
    VehicleNotFoundError,
)
from app.database.dependencies import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.maintenance import service
from app.modules.maintenance.schemas import (
    MaintenanceEventCreate,
    MaintenanceEventResponse,
    MaintenanceEventUpdate,
    ServiceTypeCreate,
    ServiceTypeResponse,
    ServiceTypeUpdate,
)
from app.modules.users.model import User


router = APIRouter(
    prefix="/maintenance",
    tags=["Maintenance"],
)


@router.get(
    "/service-types",
    response_model=list[ServiceTypeResponse],
)
def list_service_types(
    only_active: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.list_service_types(
            db,
            current_user=current_user,
            only_active=only_active,
        )

    except MaintenanceOperationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta operación.",
        ) from None


@router.get(
    "/service-types/{service_type_id}",
    response_model=ServiceTypeResponse,
)
def get_service_type(
    service_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.get_service_type(
            db,
            service_type_id=service_type_id,
            current_user=current_user,
        )

    except MaintenanceOperationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta operación.",
        ) from None

    except ServiceTypeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de servicio no encontrado.",
        ) from None


@router.post(
    "/service-types",
    response_model=ServiceTypeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_service_type(
    service_type_data: ServiceTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.create_service_type(
            db,
            current_user=current_user,
            service_type_data=service_type_data,
        )

    except MaintenanceOperationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta operación.",
        ) from None

    except ServiceTypeNameAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un tipo de servicio con ese nombre.",
        ) from None


@router.patch(
    "/service-types/{service_type_id}",
    response_model=ServiceTypeResponse,
)
def update_service_type(
    service_type_id: int,
    service_type_data: ServiceTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.update_service_type(
            db,
            service_type_id=service_type_id,
            current_user=current_user,
            service_type_data=service_type_data,
        )

    except MaintenanceOperationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta operación.",
        ) from None

    except ServiceTypeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de servicio no encontrado.",
        ) from None

    except ServiceTypeNameAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un tipo de servicio con ese nombre.",
        ) from None


@router.patch(
    "/service-types/{service_type_id}/deactivate",
    response_model=ServiceTypeResponse,
)
def deactivate_service_type(
    service_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.deactivate_service_type(
            db,
            service_type_id=service_type_id,
            current_user=current_user,
        )

    except MaintenanceOperationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta operación.",
        ) from None

    except ServiceTypeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de servicio no encontrado.",
        ) from None


@router.post(
    "/events",
    response_model=MaintenanceEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_maintenance_event(
    maintenance_data: MaintenanceEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.create_maintenance_event(
            db,
            current_user=current_user,
            maintenance_data=maintenance_data,
        )

    except MaintenanceOperationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta operación.",
        ) from None

    except VehicleNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado.",
        ) from None

    except ServiceTypeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de servicio no encontrado.",
        ) from None

    except ServiceTypeInactiveError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No se puede utilizar un tipo de servicio "
                "desactivado en un mantenimiento nuevo."
            ),
        ) from None


@router.get(
    "/vehicles/{vehicle_id}/history",
    response_model=list[MaintenanceEventResponse],
)
def get_vehicle_maintenance_history(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.list_vehicle_maintenance_history(
            db,
            current_user=current_user,
            vehicle_id=vehicle_id,
        )

    except VehicleNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado.",
        ) from None

    except MaintenanceOperationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "No tiene permisos para consultar "
                "el historial de mantenimiento de este vehículo."
            ),
        ) from None



@router.patch(
    "/events/{maintenance_event_id}",
    response_model=MaintenanceEventResponse,
)
def update_maintenance_event(
    maintenance_event_id: int,
    maintenance_data: MaintenanceEventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.update_maintenance_event(
            db,
            maintenance_event_id=maintenance_event_id,
            current_user=current_user,
            maintenance_data=maintenance_data,
        )

    except MaintenanceOperationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta operación.",
        ) from None

    except MaintenanceEventNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mantenimiento no encontrado.",
        ) from None

    except VehicleNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado.",
        ) from None

    except ServiceTypeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de servicio no encontrado.",
        ) from None

    except ServiceTypeInactiveError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No se puede asignar un tipo de servicio "
                "desactivado al mantenimiento."
            ),
        ) from None


@router.delete(
    "/events/{maintenance_event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_maintenance_event(
    maintenance_event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        service.delete_maintenance_event(
            db,
            maintenance_event_id=maintenance_event_id,
            current_user=current_user,
        )

    except MaintenanceOperationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta operación.",
        ) from None

    except MaintenanceEventNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mantenimiento no encontrado.",
        ) from None

    except MaintenanceEventAlreadyDeletedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El mantenimiento ya fue eliminado.",
        ) from None
