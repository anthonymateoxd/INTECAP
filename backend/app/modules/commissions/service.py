from sqlalchemy.orm import Session

from app.core.exceptions import (
    CommissionCancellationNotAllowedError,
    CommissionNotFoundError,
    CommissionScheduleConflictError,
    CommissionStatusNotFoundError,
    VehicleInactiveError,
    VehicleNotFoundError,
)
from app.modules.commissions import repository
from app.modules.commissions.model import Commission
from app.modules.commissions.schemas import CommissionCreate
from app.modules.vehicles.repository import get_vehicle_by_id
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from app.core.exceptions import (
    CommissionNotFoundError,
    CommissionScheduleConflictError,
    CommissionStatusNotFoundError,
    VehicleInactiveError,
    VehicleNotFoundError,
)
from app.core.constants import ROLE_ADMINISTRATION
from app.modules.users.model import User

def list_commission_statuses(
    db: Session,
):
    return repository.get_commission_statuses(db)


def list_commissions(
    db: Session,
) -> list[Commission]:
    return repository.get_commissions(db)


def get_commission(
    db: Session,
    commission_id: int,
) -> Commission | None:
    return repository.get_commission_by_id(
        db,
        commission_id,
    )


def create_commission(
    db: Session,
    requester_user_id: int,
    commission_data: CommissionCreate,
) -> Commission:
    vehicle = get_vehicle_by_id(
        db,
        commission_data.vehicle_id,
    )

    if vehicle is None:
        raise VehicleNotFoundError()

    if not vehicle.is_active:
        raise VehicleInactiveError()

    pending_status = (
        repository.get_commission_status_by_code(
            db,
            "PENDING",
        )
    )

    if pending_status is None:
        raise CommissionStatusNotFoundError()

    try:
        commission = repository.create_commission(
            db,
            requester_user_id=requester_user_id,
            vehicle_id=commission_data.vehicle_id,
            status_id=pending_status.id,
            scheduled_start_at=commission_data.scheduled_start_at,
            scheduled_end_at=commission_data.scheduled_end_at,
        )

        db.commit()
        db.refresh(commission)

        return commission

    except Exception:
        db.rollback()
        raise


def list_commissions_for_user(
    db: Session,
    current_user: User,
) -> list[Commission]:
    if current_user.role.code == ROLE_ADMINISTRATION:
        return repository.get_commissions(db)

    return repository.get_commissions_by_requester(
        db,
        current_user.id,
    )


def get_commission_for_user(
    db: Session,
    commission_id: int,
    current_user: User,
) -> Commission | None:
    commission = repository.get_commission_by_id(
        db,
        commission_id,
    )

    if commission is None:
        return None

    if current_user.role.code == ROLE_ADMINISTRATION:
        return commission

    if commission.requester_user_id != current_user.id:
        return None

    return commission


def approve_commission(
    db: Session,
    commission_id: int,
    reviewed_by_user_id: int,
) -> Commission:
    commission = repository.get_commission_by_id(
        db,
        commission_id,
    )

    if commission is None:
        raise CommissionNotFoundError()

    vehicle = get_vehicle_by_id(
        db,
        commission.vehicle_id,
    )

    if vehicle is None:
        raise VehicleNotFoundError()

    if not vehicle.is_active:
        raise VehicleInactiveError()

    approved_status = (
        repository.get_commission_status_by_code(
            db,
            "APPROVED",
        )
    )

    if approved_status is None:
        raise CommissionStatusNotFoundError()

    try:
        updated_commission = (
            repository.update_commission_review(
                db,
                commission,
                status_id=approved_status.id,
                reviewed_by_user_id=reviewed_by_user_id,
                reviewed_at=datetime.now(timezone.utc),
            )
        )

        db.commit()
        db.refresh(updated_commission)

        return updated_commission

    except IntegrityError as exc:
        db.rollback()

        sqlstate = getattr(
            exc.orig,
            "sqlstate",
            None,
        )

        if sqlstate == "23P01":
            raise CommissionScheduleConflictError() from None

        raise

    except Exception:
        db.rollback()
        raise



def reject_commission(
    db: Session,
    commission_id: int,
    reviewed_by_user_id: int,
) -> Commission:
    commission = repository.get_commission_by_id(
        db,
        commission_id,
    )

    if commission is None:
        raise CommissionNotFoundError()

    rejected_status = (
        repository.get_commission_status_by_code(
            db,
            "REJECTED",
        )
    )

    if rejected_status is None:
        raise CommissionStatusNotFoundError()

    try:
        updated_commission = (
            repository.update_commission_review(
                db,
                commission,
                status_id=rejected_status.id,
                reviewed_by_user_id=reviewed_by_user_id,
                reviewed_at=datetime.now(timezone.utc),
            )
        )

        db.commit()
        db.refresh(updated_commission)

        return updated_commission

    except Exception:
        db.rollback()
        raise


def cancel_commission(
    db: Session,
    commission_id: int,
    current_user: User,
) -> Commission:
    commission = repository.get_commission_by_id(
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

    current_status = (
        repository.get_commission_status_by_id(
            db,
            commission.status_id,
        )
    )

    if (
        current_status is None
        or current_status.code not in {"PENDING", "APPROVED"}
    ):
        raise CommissionCancellationNotAllowedError()

    cancelled_status = (
        repository.get_commission_status_by_code(
            db,
            "CANCELLED",
        )
    )

    if cancelled_status is None:
        raise CommissionStatusNotFoundError()

    try:
        updated_commission = (
            repository.update_commission_status(
                db,
                commission,
                status_id=cancelled_status.id,
            )
        )

        db.commit()
        db.refresh(updated_commission)

        return updated_commission

    except Exception:
        db.rollback()
        raise
