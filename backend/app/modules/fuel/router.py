from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import (
    CommissionNotFoundError,
    FuelCommissionNotApprovedError,
    FuelCouponAlreadyAssignedError,
    FuelCouponNotFoundError,
    FuelCouponNumberAlreadyExistsError,
    FuelOperationNotAllowedError,
    CommissionCouponNotFoundError,
    FuelCouponStateConflictError,
    FuelCommissionNotApprovedError,
    InsufficientFuelCouponsError,
    FuelLoadNotFoundError,
)
from app.database.dependencies import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.fuel import service
from app.modules.fuel.schemas import (
    CommissionCouponAssign,
    CommissionCouponResponse,
    FuelCouponCreate,
    FuelCouponResponse,
    FuelLoadCreate,
    FuelLoadResponse,
)
from app.modules.users.model import User


router = APIRouter(
    prefix="/fuel",
    tags=["Fuel"],
)


@router.post(
    "/coupons",
    response_model=FuelCouponResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_fuel_coupon(
    coupon_data: FuelCouponCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.create_fuel_coupon(
            db,
            current_user=current_user,
            coupon_data=coupon_data,
        )

    except FuelOperationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta operación.",
        ) from None

    except FuelCouponNumberAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un cupón con ese número.",
        ) from None



@router.post(
    "/commissions/{commission_id}/coupons",
    response_model=CommissionCouponResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_commission_coupon(
    commission_id: int,
    assignment_data: CommissionCouponAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.assign_commission_coupon(
            db,
            commission_id=commission_id,
            current_user=current_user,
            coupon_id=assignment_data.coupon_id,
        )

    except FuelOperationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta operación.",
        ) from None

    except CommissionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comisión no encontrada.",
        ) from None

    except FuelCommissionNotApprovedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Los cupones solo pueden asignarse "
                "a una comisión aprobada."
            ),
        ) from None

    except FuelCouponNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cupón no encontrado.",
        ) from None

    except FuelCouponAlreadyAssignedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El cupón ya se encuentra asignado.",
        ) from None




@router.patch(
    "/commissions/{commission_id}/coupons/{assignment_id}/return",
    response_model=CommissionCouponResponse,
)
def return_commission_coupon(
    commission_id: int,
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.return_commission_coupon(
            db,
            commission_id=commission_id,
            assignment_id=assignment_id,
            current_user=current_user,
        )

    except CommissionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comisión no encontrada.",
        ) from None

    except CommissionCouponNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignación de cupón no encontrada.",
        ) from None

    except FuelOperationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El cupón no puede devolverse porque "
                "ya fue usado o ya fue devuelto."
            ),
        ) from None

@router.patch(
    "/commissions/{commission_id}/coupons/{assignment_id}/used",
    response_model=CommissionCouponResponse,
)
def mark_commission_coupon_used(
    commission_id: int,
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.mark_commission_coupon_used(
            db,
            commission_id=commission_id,
            assignment_id=assignment_id,
            current_user=current_user,
        )

    except FuelOperationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta operación.",
        ) from None

    except CommissionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comisión no encontrada.",
        ) from None

    except CommissionCouponNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignación de cupón no encontrada.",
        ) from None

    except FuelCouponStateConflictError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El cupón no puede marcarse como usado porque "
                "ya fue usado o fue devuelto."
            ),
        ) from None

@router.post(
    "/commissions/{commission_id}/loads",
    response_model=FuelLoadResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_fuel_load(
    commission_id: int,
    fuel_load_data: FuelLoadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.create_fuel_load(
            db,
            commission_id=commission_id,
            current_user=current_user,
            fuel_load_data=fuel_load_data,
        )

    except CommissionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comisión no encontrada.",
        ) from None

    except FuelCommissionNotApprovedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Solo se pueden registrar cargas de combustible "
                "en una comisión aprobada."
            ),
        ) from None

    except InsufficientFuelCouponsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "La comisión no tiene suficientes cupones "
                "disponibles para registrar esta carga."
            ),
        ) from None


@router.get(
    "/coupons",
    response_model=list[FuelCouponResponse],
)
def get_fuel_coupons(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.list_fuel_coupons(
            db,
            current_user=current_user,
        )

    except FuelOperationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta operación.",
        ) from None


@router.get(
    "/coupons/available",
    response_model=list[FuelCouponResponse],
)
def get_available_fuel_coupons(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.list_available_fuel_coupons(
            db,
            current_user=current_user,
        )

    except FuelOperationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta operación.",
        ) from None


@router.get(
    "/commissions/{commission_id}/coupons",
    response_model=list[CommissionCouponResponse],
)
def get_commission_coupons(
    commission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.list_commission_coupons(
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
    "/commissions/{commission_id}/loads",
    response_model=list[FuelLoadResponse],
)
def get_fuel_loads(
    commission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.list_fuel_loads(
            db,
            commission_id=commission_id,
            current_user=current_user,
        )

    except FuelOperationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta operación.",
        ) from None

    except CommissionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comisión no encontrada.",
        ) from None



@router.get(
    "/loads",
    response_model=list[FuelLoadResponse],
)
def get_all_fuel_loads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.list_all_fuel_loads(
            db,
            current_user=current_user,
        )

    except FuelOperationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta operación.",
        ) from None



@router.get(
    "/loads/{fuel_load_id}",
    response_model=FuelLoadResponse,
)
def get_fuel_load(
    fuel_load_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.get_fuel_load(
            db,
            fuel_load_id=fuel_load_id,
            current_user=current_user,
        )

    except FuelOperationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta operación.",
        ) from None

    except FuelLoadNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carga de combustible no encontrada.",
        ) from None


@router.get(
    "/coupons/{coupon_id}",
    response_model=FuelCouponResponse,
)
def get_fuel_coupon(
    coupon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.get_fuel_coupon(
            db,
            coupon_id=coupon_id,
            current_user=current_user,
        )

    except FuelOperationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta operación.",
        ) from None

    except FuelCouponNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cupón no encontrado.",
        ) from None
@router.get(
    "/commissions/{commission_id}/coupons/{assignment_id}",
    response_model=CommissionCouponResponse,
)
def get_commission_coupon(
    commission_id: int,
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return service.get_commission_coupon(
            db,
            commission_id=commission_id,
            assignment_id=assignment_id,
            current_user=current_user,
        )

    except CommissionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comisión no encontrada.",
        ) from None

    except CommissionCouponNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignación de cupón no encontrada.",
        ) from None
