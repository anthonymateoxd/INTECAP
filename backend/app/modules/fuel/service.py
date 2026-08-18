from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.modules.commissions import repository as commissions_repository

from app.core.exceptions import (
    CommissionCouponNotFoundError,
    InsufficientFuelCouponsError,
    FuelOperationNotAllowedError,
    CommissionNotFoundError,
    FuelCouponNotFoundError,
    FuelCouponNumberAlreadyExistsError,
    FuelLoadNotFoundError,
    FuelCouponAlreadyAssignedError,
    FuelCommissionNotApprovedError,
    FuelCouponStateConflictError,
)
from datetime import datetime, timezone
from app.core.constants import ROLE_ADMINISTRATION
from app.modules.users.model import User
from app.modules.fuel import repository
from app.modules.fuel.model import (
    CommissionCoupon,
    FuelCoupon,
    FuelLoad,
)
from decimal import Decimal
from app.modules.fuel.schemas import (
    FuelCouponCreate,
    FuelLoadCreate,
)

def list_fuel_coupons(
    db: Session,
    *,
    current_user: User,
) -> list[FuelCoupon]:
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise FuelOperationNotAllowedError()

    return repository.get_fuel_coupons(db)


def get_fuel_coupon(
    db: Session,
    *,
    coupon_id: int,
    current_user: User,
) -> FuelCoupon:
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise FuelOperationNotAllowedError()

    coupon = repository.get_fuel_coupon_by_id(
        db,
        coupon_id,
    )

    if coupon is None:
        raise FuelCouponNotFoundError()

    return coupon


def create_fuel_coupon(
    db: Session,
    *,
    current_user: User,
    coupon_data: FuelCouponCreate,
) -> FuelCoupon:
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise FuelOperationNotAllowedError()

    existing_coupon = (
        repository.get_fuel_coupon_by_number(
            db,
            coupon_data.coupon_number,
        )
    )

    if existing_coupon is not None:
        raise FuelCouponNumberAlreadyExistsError()

    try:
        coupon = repository.create_fuel_coupon(
            db,
            coupon_data,
        )

        db.commit()
        db.refresh(coupon)

        return coupon

    except IntegrityError as exc:
        db.rollback()

        sqlstate = getattr(
            exc.orig,
            "sqlstate",
            None,
        )

        if sqlstate == "23505":
            raise FuelCouponNumberAlreadyExistsError() from None

        raise

    except Exception:
        db.rollback()
        raise


def list_fuel_loads(
    db: Session,
    *,
    commission_id: int,
    current_user: User,
) -> list[FuelLoad]:
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise FuelOperationNotAllowedError()

    commission = commissions_repository.get_commission_by_id(
        db,
        commission_id,
    )

    if commission is None:
        raise CommissionNotFoundError()

    return repository.get_fuel_loads_by_commission(
        db,
        commission_id,
    )


def get_fuel_load(
    db: Session,
    *,
    fuel_load_id: int,
    current_user: User,
) -> FuelLoad:
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise FuelOperationNotAllowedError()

    fuel_load = repository.get_fuel_load_by_id(
        db,
        fuel_load_id,
    )

    if fuel_load is None:
        raise FuelLoadNotFoundError()

    return fuel_load


def create_fuel_load(
    db: Session,
    *,
    commission_id: int,
    current_user: User,
    fuel_load_data: FuelLoadCreate,
) -> FuelLoad:
    commission = commissions_repository.get_commission_by_id(
        db,
        commission_id,
    )

    if commission is None:
        raise CommissionNotFoundError()

    if (
        current_user.role.code != ROLE_ADMINISTRATION
        and commission.requester_user_id != current_user.id
    ):
        raise CommissionNotFoundError()

    commission_status = (
        commissions_repository.get_commission_status_by_id(
            db,
            commission.status_id,
        )
    )

    if (
        commission_status is None
        or commission_status.code != "APPROVED"
    ):
        raise FuelCommissionNotApprovedError()

    coupons_required = int(
        fuel_load_data.amount_q
        / Decimal("100.00")
    )

    assignments = (
        repository.get_unused_commission_coupons(
            db,
            commission_id,
            limit=coupons_required,
        )
    )

    if len(assignments) < coupons_required:
        raise InsufficientFuelCouponsError()

    try:
        fuel_load = repository.create_fuel_load(
            db,
            commission_id=commission_id,
            loaded_at=fuel_load_data.loaded_at,
            gas_station=fuel_load_data.gas_station,
            gallons=fuel_load_data.gallons,
            amount_q=fuel_load_data.amount_q,
        )

        for assignment in assignments:
            repository.mark_commission_coupon_used(
                db,
                assignment,
                used_at=fuel_load_data.loaded_at,
            )

        db.commit()
        db.refresh(fuel_load)

        return fuel_load

    except Exception:
        db.rollback()
        raise


def list_commission_coupons(
    db: Session,
    *,
    commission_id: int,
    current_user: User,
) -> list[CommissionCoupon]:
    commission = commissions_repository.get_commission_by_id(
        db,
        commission_id,
    )

    if commission is None:
        raise CommissionNotFoundError()

    if (
        current_user.role.code != ROLE_ADMINISTRATION
        and commission.requester_user_id != current_user.id
    ):
        raise CommissionNotFoundError()

    return repository.get_commission_coupons(
        db,
        commission_id,
    )


def get_commission_coupon(
    db: Session,
    *,
    commission_id: int,
    assignment_id: int,
    current_user: User,
) -> CommissionCoupon:
    commission = commissions_repository.get_commission_by_id(
        db,
        commission_id,
    )

    if commission is None:
        raise CommissionNotFoundError()

    if (
        current_user.role.code != ROLE_ADMINISTRATION
        and commission.requester_user_id != current_user.id
    ):
        raise CommissionNotFoundError()

    assignment = repository.get_commission_coupon_by_id(
        db,
        assignment_id,
    )

    if (
        assignment is None
        or assignment.commission_id != commission_id
    ):
        raise CommissionCouponNotFoundError()

    return assignment

def list_available_fuel_coupons(
    db: Session,
    *,
    current_user: User,
) -> list[FuelCoupon]:
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise FuelOperationNotAllowedError()

    return repository.get_available_fuel_coupons(db)



def assign_commission_coupon(
    db: Session,
    *,
    commission_id: int,
    current_user: User,
    coupon_id: int,
) -> CommissionCoupon:
    # Solo Administración puede asignar cupones.
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise FuelOperationNotAllowedError()

    commission = commissions_repository.get_commission_by_id(
        db,
        commission_id,
    )

    if commission is None:
        raise CommissionNotFoundError()

    commission_status = (
        commissions_repository.get_commission_status_by_id(
            db,
            commission.status_id,
        )
    )

    if (
        commission_status is None
        or commission_status.code != "APPROVED"
    ):
        raise FuelCommissionNotApprovedError()

    coupon = repository.get_fuel_coupon_by_id(
        db,
        coupon_id,
    )

    if coupon is None:
        raise FuelCouponNotFoundError()

    active_assignment = (
        repository.get_active_assignment_by_coupon(
            db,
            coupon_id,
        )
    )

    if active_assignment is not None:
        raise FuelCouponAlreadyAssignedError()

    try:
        assignment = (
            repository.create_commission_coupon_assignment(
                db,
                commission_id=commission_id,
                coupon_id=coupon_id,
            )
        )

        db.commit()
        db.refresh(assignment)

        return assignment

    except IntegrityError as exc:
        db.rollback()

        if getattr(exc.orig, "sqlstate", None) == "23505":
            raise FuelCouponAlreadyAssignedError() from exc

        raise


def return_commission_coupon(
    db: Session,
    *,
    commission_id: int,
    assignment_id: int,
    current_user: User,
) -> CommissionCoupon:
    commission = commissions_repository.get_commission_by_id(
        db,
        commission_id,
    )

    if commission is None:
        raise CommissionNotFoundError()

    # Administración puede devolver cualquier cupón.
    # El colaborador solamente puede hacerlo en su propia comisión.
    if (
        current_user.role.code != ROLE_ADMINISTRATION
        and commission.requester_user_id != current_user.id
    ):
        raise CommissionNotFoundError()

    assignment = repository.get_commission_coupon_by_id(
        db,
        assignment_id,
    )

    if (
        assignment is None
        or assignment.commission_id != commission_id
    ):
        raise CommissionCouponNotFoundError()

    # Un cupón usado ya no puede devolverse.
    if assignment.used_at is not None:
        raise FuelOperationNotAllowedError()

    # Una devolución no puede registrarse dos veces.
    if assignment.returned_at is not None:
        raise FuelOperationNotAllowedError()

    try:
        assignment = repository.mark_commission_coupon_returned(
            db,
            assignment,
            returned_at=datetime.now(timezone.utc),
        )

        db.commit()
        db.refresh(assignment)

        return assignment

    except Exception:
        db.rollback()
        raise



def mark_commission_coupon_used(
    db: Session,
    *,
    commission_id: int,
    assignment_id: int,
    current_user: User,
) -> CommissionCoupon:
    # Solo Administración puede marcar un cupón como usado.
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise FuelOperationNotAllowedError()

    commission = commissions_repository.get_commission_by_id(
        db,
        commission_id,
    )

    if commission is None:
        raise CommissionNotFoundError()

    assignment = repository.get_commission_coupon_by_id(
        db,
        assignment_id,
    )

    if (
        assignment is None
        or assignment.commission_id != commission_id
    ):
        raise CommissionCouponNotFoundError()

    # Un cupón devuelto ya no puede marcarse como usado
    # desde esta asignación.
    if assignment.returned_at is not None:
        raise FuelCouponStateConflictError()

    if assignment.used_at is not None:
        raise FuelCouponStateConflictError()

    try:
        assignment = repository.mark_commission_coupon_used(
            db,
            assignment,
            used_at=datetime.now(timezone.utc),
        )

        db.commit()
        db.refresh(assignment)

        return assignment

    except Exception:
        db.rollback()
        raise


def list_all_fuel_loads(
    db: Session,
    *,
    current_user: User,
) -> list[FuelLoad]:
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise FuelOperationNotAllowedError()

    return repository.get_all_fuel_loads(db)
