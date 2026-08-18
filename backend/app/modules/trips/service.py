from sqlalchemy.orm import Session

from app.core.constants import ROLE_ADMINISTRATION
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
from datetime import datetime, timezone
from app.modules.commissions import repository as commissions_repository
from app.modules.trips import repository
from app.modules.trips.model import Trip
from app.modules.trips.schemas import TripCreate
from app.modules.users.model import User
from app.modules.users.repository import get_user_by_id
from app.modules.vehicles.repository import get_vehicle_by_id
from app.modules.trips.schemas import TripCreate, TripUpdate

def create_trip(
    db: Session,
    *,
    commission_id: int,
    current_user: User,
    trip_data: TripCreate,
) -> Trip:
    commission = commissions_repository.get_commission_by_id(
        db,
        commission_id,
    )

    if commission is None:
        raise CommissionNotFoundError()

    # Administración puede registrar cualquier comisión.
    # Un colaborador solamente puede registrar la suya.
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
        raise TripCommissionNotApprovedError()

    driver = get_user_by_id(
        db,
        trip_data.driver_user_id,
    )

    if driver is None:
        raise TripDriverNotFoundError()

    start_date = commission.scheduled_start_at.date()
    end_date = commission.scheduled_end_at.date()

    if not (
        start_date
        <= trip_data.trip_date
        <= end_date
    ):
        raise TripDateOutsideCommissionError()

    vehicle = get_vehicle_by_id(
        db,
        commission.vehicle_id,
    )

    if vehicle is None:
        raise CommissionNotFoundError()

    odometer_start_km = trip_data.odometer_start_km

    if odometer_start_km is None:
        odometer_start_km = vehicle.current_odometer_km

    if trip_data.odometer_end_km < odometer_start_km:
        raise TripInvalidOdometerError()

    try:
        trip = repository.create_trip(
            db,
            commission_id=commission.id,
            driver_user_id=trip_data.driver_user_id,
            trip_date=trip_data.trip_date,
            origin=trip_data.origin,
            destination=trip_data.destination,
            odometer_start_km=odometer_start_km,
            odometer_end_km=trip_data.odometer_end_km,
            tank_balance_percent=trip_data.tank_balance_percent,
            road_type=trip_data.road_type,
        )

        vehicle.current_odometer_km = (
            vehicle.current_odometer_km
            + trip.distance_km
        )

        db.flush()

        db.commit()
        db.refresh(trip)

        return trip

    except Exception:
        db.rollback()
        raise



def list_trips_for_commission(
    db: Session,
    *,
    commission_id: int,
    current_user: User,
) -> list[Trip]:
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

    return repository.get_trips_by_commission(
        db,
        commission_id,
    )


def get_trip_for_user(
    db: Session,
    *,
    commission_id: int,
    trip_id: int,
    current_user: User,
) -> Trip:
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

    trip = repository.get_trip_by_id(
        db,
        trip_id,
    )

    if (
        trip is None
        or trip.commission_id != commission.id
    ):
        raise TripNotFoundError()

    return trip


def update_trip(
    db: Session,
    *,
    commission_id: int,
    trip_id: int,
    current_user: User,
    trip_data: TripUpdate,
) -> Trip:
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

    trip = repository.get_trip_by_id(
        db,
        trip_id,
    )

    if (
        trip is None
        or trip.commission_id != commission.id
    ):
        raise TripNotFoundError()

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
        raise TripEditNotAllowedError()

    values = trip_data.model_dump(
        exclude_unset=True,
    )

    if "driver_user_id" in values:
        driver = get_user_by_id(
            db,
            values["driver_user_id"],
        )

        if driver is None:
            raise TripDriverNotFoundError()

    if "trip_date" in values:
        start_date = commission.scheduled_start_at.date()
        end_date = commission.scheduled_end_at.date()

        if not (
            start_date
            <= values["trip_date"]
            <= end_date
        ):
            raise TripDateOutsideCommissionError()

    effective_start = values.get(
        "odometer_start_km",
        trip.odometer_start_km,
    )

    effective_end = values.get(
        "odometer_end_km",
        trip.odometer_end_km,
    )

    if effective_end < effective_start:
        raise TripInvalidOdometerError()

    vehicle = get_vehicle_by_id(
        db,
        commission.vehicle_id,
    )

    if vehicle is None:
        raise CommissionNotFoundError()

    old_distance = trip.distance_km

    try:
        updated_trip = repository.update_trip(
            db,
            trip,
            values=values,
        )

        new_distance = updated_trip.distance_km

        distance_difference = (
            new_distance - old_distance
        )

        vehicle.current_odometer_km = (
            vehicle.current_odometer_km
            + distance_difference
        )

        db.flush()
        db.commit()

        db.refresh(updated_trip)
        db.refresh(vehicle)

        return updated_trip

    except Exception:
        db.rollback()
        raise




def delete_trip(
    db: Session,
    *,
    commission_id: int,
    trip_id: int,
    current_user: User,
) -> Trip:
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise CommissionNotFoundError()

    commission = commissions_repository.get_commission_by_id(
        db,
        commission_id,
    )

    if commission is None:
        raise CommissionNotFoundError()

    trip = repository.get_trip_by_id_including_deleted(
        db,
        trip_id,
    )

    if (
        trip is None
        or trip.commission_id != commission.id
    ):
        raise TripNotFoundError()

    if trip.is_deleted:
        raise TripAlreadyDeletedError()

    vehicle = get_vehicle_by_id(
        db,
        commission.vehicle_id,
    )

    if vehicle is None:
        raise VehicleNotFoundError()

    try:
        vehicle.current_odometer_km = (
            vehicle.current_odometer_km
            - trip.distance_km
        )

        deleted_trip = repository.soft_delete_trip(
            db,
            trip,
            deleted_by_user_id=current_user.id,
            deleted_at=datetime.now(timezone.utc),
        )

        db.flush()
        db.commit()

        db.refresh(deleted_trip)
        db.refresh(vehicle)

        return deleted_trip

    except Exception:
        db.rollback()
        raise



def list_deleted_trips_for_admin(
    db: Session,
    *,
    commission_id: int,
    current_user: User,
) -> list[Trip]:
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise CommissionNotFoundError()

    commission = commissions_repository.get_commission_by_id(
        db,
        commission_id,
    )

    if commission is None:
        raise CommissionNotFoundError()

    return repository.get_deleted_trips_by_commission(
        db,
        commission_id,
    )
