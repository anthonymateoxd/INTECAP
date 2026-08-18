from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.fuel.model import (
    CommissionCoupon,
    FuelCoupon,
    FuelLoad,
)
from app.modules.fuel.schemas import FuelCouponCreate
from decimal import Decimal
from datetime import datetime
def get_fuel_coupons(
    db: Session,
) -> list[FuelCoupon]:
    statement = (
        select(FuelCoupon)
        .order_by(FuelCoupon.id)
    )

    return list(
        db.scalars(statement).all()
    )


def get_fuel_coupon_by_id(
    db: Session,
    coupon_id: int,
) -> FuelCoupon | None:
    statement = select(FuelCoupon).where(
        FuelCoupon.id == coupon_id
    )

    return db.scalars(statement).first()


def get_fuel_coupon_by_number(
    db: Session,
    coupon_number: str,
) -> FuelCoupon | None:
    statement = select(FuelCoupon).where(
        FuelCoupon.coupon_number == coupon_number
    )

    return db.scalars(statement).first()


def create_fuel_coupon(
    db: Session,
    coupon_data: FuelCouponCreate,
) -> FuelCoupon:
    coupon = FuelCoupon(
        **coupon_data.model_dump(),
        face_value_q=Decimal("100.00"),
    )

    db.add(coupon)
    db.flush()
    db.refresh(coupon)

    return coupon


def get_commission_coupons(
    db: Session,
    commission_id: int,
) -> list[CommissionCoupon]:
    statement = (
        select(CommissionCoupon)
        .where(
            CommissionCoupon.commission_id
            == commission_id
        )
        .order_by(CommissionCoupon.id)
    )

    return list(
        db.scalars(statement).all()
    )


def get_fuel_loads_by_commission(
    db: Session,
    commission_id: int,
) -> list[FuelLoad]:
    statement = (
        select(FuelLoad)
        .where(
            FuelLoad.commission_id
            == commission_id
        )
        .order_by(FuelLoad.loaded_at)
    )

    return list(
        db.scalars(statement).all()
    )

def get_all_fuel_loads(
    db: Session,
) -> list[FuelLoad]:
    statement = (
        select(FuelLoad)
        .order_by(
            FuelLoad.loaded_at,
            FuelLoad.id,
        )
    )

    return list(
        db.scalars(statement).all()
    )

def get_active_assignment_by_coupon(
    db: Session,
    coupon_id: int,
) -> CommissionCoupon | None:
    statement = select(CommissionCoupon).where(
        CommissionCoupon.coupon_id == coupon_id,
        CommissionCoupon.returned_at.is_(None),
    )

    return db.scalars(statement).first()


def get_available_fuel_coupons(
    db: Session,
) -> list[FuelCoupon]:
    active_coupon_ids = (
        select(CommissionCoupon.coupon_id)
        .where(
            CommissionCoupon.returned_at.is_(None)
        )
    )

    statement = (
        select(FuelCoupon)
        .where(
            FuelCoupon.id.not_in(active_coupon_ids)
        )
        .order_by(FuelCoupon.id)
    )

    return list(
        db.scalars(statement).all()
    )



def get_commission_coupon_by_id(
    db: Session,
    assignment_id: int,
) -> CommissionCoupon | None:
    statement = select(CommissionCoupon).where(
        CommissionCoupon.id == assignment_id
    )

    return db.scalars(statement).first()


def create_commission_coupon_assignment(
    db: Session,
    *,
    commission_id: int,
    coupon_id: int,
) -> CommissionCoupon:
    assignment = CommissionCoupon(
        commission_id=commission_id,
        coupon_id=coupon_id,
    )

    db.add(assignment)
    db.flush()
    db.refresh(assignment)

    return assignment


def mark_commission_coupon_used(
    db: Session,
    assignment: CommissionCoupon,
    *,
    used_at: datetime,
) -> CommissionCoupon:
    assignment.used_at = used_at

    db.flush()
    db.refresh(assignment)

    return assignment


def mark_commission_coupon_returned(
    db: Session,
    assignment: CommissionCoupon,
    *,
    returned_at: datetime,
) -> CommissionCoupon:
    assignment.returned_at = returned_at

    db.flush()
    db.refresh(assignment)

    return assignment


def get_fuel_load_by_id(
    db: Session,
    fuel_load_id: int,
) -> FuelLoad | None:
    statement = select(FuelLoad).where(
        FuelLoad.id == fuel_load_id
    )

    return db.scalars(statement).first()


def create_fuel_load(
    db: Session,
    *,
    commission_id: int,
    loaded_at: datetime,
    gas_station: str,
    gallons,
    amount_q,
) -> FuelLoad:
    fuel_load = FuelLoad(
        commission_id=commission_id,
        loaded_at=loaded_at,
        gas_station=gas_station,
        gallons=gallons,
        amount_q=amount_q,
    )

    db.add(fuel_load)
    db.flush()
    db.refresh(fuel_load)

    return fuel_load



def get_unused_commission_coupons(
    db: Session,
    commission_id: int,
    *,
    limit: int | None = None,
) -> list[CommissionCoupon]:
    statement = (
        select(CommissionCoupon)
        .where(
            CommissionCoupon.commission_id == commission_id,
            CommissionCoupon.used_at.is_(None),
            CommissionCoupon.returned_at.is_(None),
        )
        .order_by(
            CommissionCoupon.assigned_at,
            CommissionCoupon.id,
        )
    )

    if limit is not None:
        statement = statement.limit(limit)

    return list(
        db.scalars(statement).all()
    )
