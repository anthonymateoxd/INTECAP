from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.trips.model import Trip
from datetime import datetime

def get_trips_by_commission(
    db: Session,
    commission_id: int,
) -> list[Trip]:
    statement = (
        select(Trip)
        .where(
            Trip.commission_id == commission_id,
            Trip.is_deleted.is_(False),
        )
        .order_by(Trip.sequence_number)
    )

    return list(
        db.scalars(statement).all()
    )

def get_trip_by_id(
    db: Session,
    trip_id: int,
) -> Trip | None:
    statement = select(Trip).where(
        Trip.id == trip_id,
        Trip.is_deleted.is_(False),
    )

    return db.scalars(statement).first()


def get_next_sequence_number(
    db: Session,
    commission_id: int,
) -> int:
    statement = select(
        func.coalesce(
            func.max(Trip.sequence_number),
            0,
        )
    ).where(
        Trip.commission_id == commission_id
    )

    current_max = db.scalar(statement)

    return int(current_max) + 1


def create_trip(
    db: Session,
    *,
    commission_id: int,
    driver_user_id: int,
    trip_date: date,
    origin: str,
    destination: str,
    odometer_start_km: Decimal,
    odometer_end_km: Decimal,
    tank_balance_percent: Decimal | None,
    road_type: str,
) -> Trip:
    sequence_number = get_next_sequence_number(
        db,
        commission_id,
    )

    trip = Trip(
        commission_id=commission_id,
        driver_user_id=driver_user_id,
        sequence_number=sequence_number,
        trip_date=trip_date,
        origin=origin,
        destination=destination,
        odometer_start_km=odometer_start_km,
        odometer_end_km=odometer_end_km,
        tank_balance_percent=tank_balance_percent,
        road_type=road_type,
    )

    db.add(trip)
    db.flush()
    db.refresh(trip)

    return trip




def update_trip(
    db: Session,
    trip: Trip,
    *,
    values: dict,
) -> Trip:
    for field_name, value in values.items():
        setattr(
            trip,
            field_name,
            value,
        )

    db.flush()
    db.refresh(trip)

    return trip


def get_deleted_trips_by_commission(
    db: Session,
    commission_id: int,
) -> list[Trip]:
    statement = (
        select(Trip)
        .where(
            Trip.commission_id == commission_id,
            Trip.is_deleted.is_(True),
        )
        .order_by(Trip.sequence_number)
    )

    return list(
        db.scalars(statement).all()
    )


def get_trip_by_id_including_deleted(
    db: Session,
    trip_id: int,
) -> Trip | None:
    statement = select(Trip).where(
        Trip.id == trip_id
    )

    return db.scalars(statement).first()



def soft_delete_trip(
    db: Session,
    trip: Trip,
    *,
    deleted_by_user_id: int,
    deleted_at: datetime,
) -> Trip:
    trip.is_deleted = True
    trip.deleted_by_user_id = deleted_by_user_id
    trip.deleted_at = deleted_at

    db.flush()
    db.refresh(trip)

    return trip
