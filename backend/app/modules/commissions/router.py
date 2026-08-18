from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.core.exceptions import (
    CommissionCancellationNotAllowedError,
    CommissionNotFoundError,
    CommissionScheduleConflictError,
    CommissionStatusNotFoundError,
    VehicleInactiveError,
    VehicleNotFoundError,
)
from app.database.dependencies import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.commissions import service
from app.modules.commissions.schemas import (
    CommissionCreate,
    CommissionResponse,
)
from app.modules.users.model import User
from app.modules.auth.dependencies import (
    get_current_user,
    require_administration,
)

router = APIRouter(
    prefix="/commissions",
    tags=["Commissions"],
)


@router.post(
    "",
    response_model=CommissionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_commission(
    commission_data: CommissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.create_commission(
            db,
            requester_user_id=current_user.id,
            commission_data=commission_data,
        )

    except VehicleNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado.",
        ) from None

    except VehicleInactiveError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El vehículo se encuentra desactivado.",
        ) from None

    except CommissionStatusNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se encuentra configurado el estado inicial de la comisión.",
        ) from None



@router.get(
    "",
    response_model=list[CommissionResponse],
)
def get_commissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.list_commissions_for_user(
        db,
        current_user,
    )



@router.get(
    "/{commission_id}",
    response_model=CommissionResponse,
)
def get_commission(
    commission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    commission = service.get_commission_for_user(
        db,
        commission_id,
        current_user,
    )

    if commission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comisión no encontrada.",
        )

    return commission

@router.patch(
    "/{commission_id}/approve",
    response_model=CommissionResponse,
)
def approve_commission(
    commission_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_administration),
):
    try:
        return service.approve_commission(
            db,
            commission_id,
            current_admin.id,
        )

    except CommissionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comisión no encontrada.",
        ) from None

    except VehicleNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado.",
        ) from None

    except VehicleInactiveError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El vehículo se encuentra desactivado "
                "y la comisión no puede ser aprobada."
            ),
        ) from None

    except CommissionScheduleConflictError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El vehículo ya está asignado a otra "
                "comisión aprobada dentro del horario solicitado."
            ),
        ) from None

    except CommissionStatusNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "No se encuentra configurado el estado "
                "de aprobación de la comisión."
            ),
        ) from None


@router.patch(
    "/{commission_id}/reject",
    response_model=CommissionResponse,
)
def reject_commission(
    commission_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_administration),
):
    try:
        return service.reject_commission(
            db,
            commission_id,
            current_admin.id,
        )

    except CommissionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comisión no encontrada.",
        ) from None

    except CommissionStatusNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "No se encuentra configurado el estado "
                "de rechazo de la comisión."
            ),
        ) from None



@router.patch(
    "/{commission_id}/cancel",
    response_model=CommissionResponse,
)
def cancel_commission(
    commission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.cancel_commission(
            db,
            commission_id,
            current_user,
        )

    except CommissionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comisión no encontrada.",
        ) from None

    except CommissionCancellationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "La comisión no puede cancelarse "
                "en su estado actual."
            ),
        ) from None

    except CommissionStatusNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "No se encuentra configurado el estado "
                "de cancelación de la comisión."
            ),
        ) from None
