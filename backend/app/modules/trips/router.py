from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import (
    CommissionNotFoundError,
    TripAlreadyDeletedError,
    TripCommissionNotApprovedError,
    TripDateOutsideCommissionError,
    TripDriverNotFoundError,
    TripEditNotAllowedError,
    TripInvalidOdometerError,
    TripNotFoundError,
    VehicleNotFoundError,
)
from app.modules.auth.dependencies import (
    get_current_user,
    require_administration,
)
from app.database.dependencies import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.trips import service
from app.modules.trips.schemas import (
    DeletedTripResponse,
    TripCreate,
    TripResponse,
    TripUpdate,
)
from app.modules.users.model import User


router = APIRouter(
    prefix="/commissions",
    tags=["Trips"],
)


@router.post(
    "/{commission_id}/trips",
    response_model=TripResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_trip(
    commission_id: int,
    trip_data: TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.create_trip(
            db,
            commission_id=commission_id,
            current_user=current_user,
            trip_data=trip_data,
        )

    except CommissionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comisión no encontrada.",
        ) from None

    except TripCommissionNotApprovedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Solo se pueden registrar recorridos "
                "en una comisión aprobada."
            ),
        ) from None

    except TripDriverNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Piloto no encontrado.",
        ) from None

    except TripDateOutsideCommissionError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "La fecha del recorrido debe estar "
                "dentro del período de la comisión."
            ),
        ) from None

    except TripInvalidOdometerError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El odómetro final no puede ser menor "
                "que el odómetro inicial."
            ),
        ) from None




@router.get(
    "/{commission_id}/trips",
    response_model=list[TripResponse],
)
def get_trips(
    commission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.list_trips_for_commission(
            db,
            commission_id=commission_id,
            current_user=current_user,
        )

    except CommissionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comisión no encontrada.",
        ) from None


@router.get(
    "/{commission_id}/trips/{trip_id}",
    response_model=TripResponse,
)
def get_trip(
    commission_id: int,
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.get_trip_for_user(
            db,
            commission_id=commission_id,
            trip_id=trip_id,
            current_user=current_user,
        )

    except CommissionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comisión no encontrada.",
        ) from None

    except TripNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recorrido no encontrado.",
        ) from None


@router.patch(
    "/{commission_id}/trips/{trip_id}",
    response_model=TripResponse,
)
def update_trip(
    commission_id: int,
    trip_id: int,
    trip_data: TripUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.update_trip(
            db,
            commission_id=commission_id,
            trip_id=trip_id,
            current_user=current_user,
            trip_data=trip_data,
        )

    except CommissionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comisión no encontrada.",
        ) from None

    except TripNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recorrido no encontrado.",
        ) from None

    except TripEditNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Los recorridos solo pueden editarse "
                "cuando la comisión está aprobada."
            ),
        ) from None

    except TripDriverNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Piloto no encontrado.",
        ) from None

    except TripDateOutsideCommissionError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "La fecha del recorrido debe estar "
                "dentro del período de la comisión."
            ),
        ) from None

    except TripInvalidOdometerError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El odómetro final no puede ser menor "
                "que el odómetro inicial."
            ),
        ) from None





@router.delete(
    "/{commission_id}/trips/{trip_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_trip(
    commission_id: int,
    trip_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_administration),
):
    try:
        service.delete_trip(
            db,
            commission_id=commission_id,
            trip_id=trip_id,
            current_user=current_admin,
        )

    except CommissionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comisión no encontrada.",
        ) from None

    except TripNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recorrido no encontrado.",
        ) from None

    except TripAlreadyDeletedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El recorrido ya fue eliminado.",
        ) from None

    except VehicleNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado.",
        ) from None



@router.get(
    "/{commission_id}/trips-history",
    response_model=list[DeletedTripResponse],
)
def get_deleted_trips_history(
    commission_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_administration),
):
    try:
        return service.list_deleted_trips_for_admin(
            db,
            commission_id=commission_id,
            current_user=current_admin,
        )

    except CommissionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comisión no encontrada.",
        ) from None
