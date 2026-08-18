from datetime import date

from sqlalchemy import Date, cast, select
from sqlalchemy.orm import Session

from app.modules.vehicles.model import Vehicle
from sqlalchemy.orm import aliased, selectinload
from app.modules.maintenance.models import MaintenanceEvent
from app.modules.commissions.model import (
    Commission,
    CommissionStatus,
)
from app.modules.fuel.model import FuelLoad
from app.modules.users.model import User
from app.modules.trips.model import Trip

def get_vehicles_report(
    db: Session,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    is_active: bool | None = None,
) -> list[Vehicle]:
    statement = select(Vehicle)

    if start_date is not None:
        statement = statement.where(
            cast(Vehicle.created_at, Date) >= start_date
        )

    if end_date is not None:
        statement = statement.where(
            cast(Vehicle.created_at, Date) <= end_date
        )

    if is_active is not None:
        statement = statement.where(
            Vehicle.is_active.is_(is_active)
        )

    statement = statement.order_by(
        Vehicle.created_at,
        Vehicle.id,
    )

    return list(
        db.scalars(statement).all()
    )


def get_commissions_report(
    db: Session,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    requester_user_id: int | None = None,
):
    requester = aliased(User)
    reviewer = aliased(User)

    statement = (
        select(
            Commission,
            requester.full_name.label("requester_name"),
            reviewer.full_name.label("reviewer_name"),
            Vehicle,
            CommissionStatus,
        )
        .join(
            requester,
            requester.id == Commission.requester_user_id,
        )
        .outerjoin(
            reviewer,
            reviewer.id == Commission.reviewed_by_user_id,
        )
        .outerjoin(
            Vehicle,
            Vehicle.id == Commission.vehicle_id,
        )
        .join(
            CommissionStatus,
            CommissionStatus.id == Commission.status_id,
        )
    )

    if start_date is not None:
        statement = statement.where(
            cast(Commission.scheduled_start_at, Date)
            >= start_date
        )

    if end_date is not None:
        statement = statement.where(
            cast(Commission.scheduled_start_at, Date)
            <= end_date
        )

    if requester_user_id is not None:
        statement = statement.where(
            Commission.requester_user_id
            == requester_user_id
        )

    statement = statement.order_by(
        Commission.scheduled_start_at,
        Commission.id,
    )

    return list(
        db.execute(statement).all()
    )
def get_trips_report(
    db: Session,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    requester_user_id: int | None = None,
):
    driver = aliased(User)

    statement = (
        select(
            Trip,
            Vehicle,
            driver.full_name.label("driver_name"),
            Commission,
        )
        .join(
            Commission,
            Commission.id == Trip.commission_id,
        )
        .outerjoin(
            Vehicle,
            Vehicle.id == Commission.vehicle_id,
        )
        .join(
            driver,
            driver.id == Trip.driver_user_id,
        )
        .where(
            Trip.is_deleted.is_(False)
        )
    )

    if start_date is not None:
        statement = statement.where(
            Trip.trip_date >= start_date
        )

    if end_date is not None:
        statement = statement.where(
            Trip.trip_date <= end_date
        )

    if requester_user_id is not None:
        statement = statement.where(
            Commission.requester_user_id
            == requester_user_id
        )

    statement = statement.order_by(
        Trip.trip_date,
        Trip.commission_id,
        Trip.sequence_number,
        Trip.id,
    )

    return list(
        db.execute(statement).all()
    )






def get_fuel_loads_report(
    db: Session,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
):
    requester = aliased(User)

    statement = (
        select(
            FuelLoad,
            requester.full_name.label("requester_name"),
            Vehicle,
        )
        .join(
            Commission,
            Commission.id == FuelLoad.commission_id,
        )
        .join(
            requester,
            requester.id == Commission.requester_user_id,
        )
        .outerjoin(
            Vehicle,
            Vehicle.id == Commission.vehicle_id,
        )
    )

    if start_date is not None:
        statement = statement.where(
            cast(FuelLoad.loaded_at, Date) >= start_date
        )

    if end_date is not None:
        statement = statement.where(
            cast(FuelLoad.loaded_at, Date) <= end_date
        )

    statement = statement.order_by(
        FuelLoad.loaded_at,
        FuelLoad.id,
    )

    return list(
        db.execute(statement).all()
    )


def get_maintenance_report(
    db: Session,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
):
    statement = (
        select(
            MaintenanceEvent,
            Vehicle,
        )
        .join(
            Vehicle,
            Vehicle.id == MaintenanceEvent.vehicle_id,
        )
        .options(
            selectinload(MaintenanceEvent.services),
            selectinload(MaintenanceEvent.parts),
        )
        .where(
            MaintenanceEvent.is_deleted.is_(False)
        )
    )

    if start_date is not None:
        statement = statement.where(
            MaintenanceEvent.maintenance_date >= start_date
        )

    if end_date is not None:
        statement = statement.where(
            MaintenanceEvent.maintenance_date <= end_date
        )

    statement = statement.order_by(
        MaintenanceEvent.maintenance_date,
        MaintenanceEvent.id,
    )

    return list(
        db.execute(statement).all()
    )
