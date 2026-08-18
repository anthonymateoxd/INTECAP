from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime
from app.modules.commissions.model import (
    Commission,
    CommissionStatus,
)

from datetime import datetime
def get_commission_statuses(
    db: Session,
) -> list[CommissionStatus]:
    statement = (
        select(CommissionStatus)
        .order_by(CommissionStatus.id)
    )

    return list(
        db.scalars(statement).all()
    )


def get_commission_status_by_id(
    db: Session,
    status_id: int,
) -> CommissionStatus | None:
    statement = select(CommissionStatus).where(
        CommissionStatus.id == status_id
    )

    return db.scalars(statement).first()


def get_commission_status_by_code(
    db: Session,
    code: str,
) -> CommissionStatus | None:
    statement = select(CommissionStatus).where(
        CommissionStatus.code == code
    )

    return db.scalars(statement).first()


def get_commissions(
    db: Session,
) -> list[Commission]:
    statement = (
        select(Commission)
        .order_by(Commission.id)
    )

    return list(
        db.scalars(statement).all()
    )


def get_commission_by_id(
    db: Session,
    commission_id: int,
) -> Commission | None:
    statement = select(Commission).where(
        Commission.id == commission_id
    )

    return db.scalars(statement).first()


def create_commission(
    db: Session,
    *,
    requester_user_id: int,
    vehicle_id: int,
    status_id: int,
    scheduled_start_at: datetime,
    scheduled_end_at: datetime,
) -> Commission:
    commission = Commission(
        requester_user_id=requester_user_id,
        vehicle_id=vehicle_id,
        status_id=status_id,
        scheduled_start_at=scheduled_start_at,
        scheduled_end_at=scheduled_end_at,
    )

    db.add(commission)
    db.flush()
    db.refresh(commission)

    return commission




def get_commissions_by_requester(
    db: Session,
    requester_user_id: int,
) -> list[Commission]:
    statement = (
        select(Commission)
        .where(
            Commission.requester_user_id
            == requester_user_id
        )
        .order_by(Commission.id)
    )

    return list(
        db.scalars(statement).all()
    )



def update_commission_review(
    db: Session,
    commission: Commission,
    *,
    status_id: int,
    reviewed_by_user_id: int,
    reviewed_at: datetime,
) -> Commission:
    commission.status_id = status_id
    commission.reviewed_by_user_id = reviewed_by_user_id
    commission.reviewed_at = reviewed_at

    db.flush()
    db.refresh(commission)

    return commission



def update_commission_status(
    db: Session,
    commission: Commission,
    *,
    status_id: int,
) -> Commission:
    commission.status_id = status_id

    db.flush()
    db.refresh(commission)

    return commission
