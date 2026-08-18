from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    FetchedValue,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.modules.users.model import User
from app.modules.vehicles.model import Vehicle

class CommissionStatus(Base):
    __tablename__ = "commission_statuses"

    __table_args__ = (
        UniqueConstraint(
            "code",
            name="commission_statuses_code_key",
        ),
        UniqueConstraint(
            "name",
            name="commission_statuses_name_key",
        ),
    )

    id: Mapped[int] = mapped_column(
        SmallInteger,
        primary_key=True,
        autoincrement=True,
    )

    code: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class Commission(Base):
    __tablename__ = "commissions"

    __table_args__ = (
        CheckConstraint(
            "scheduled_end_at > scheduled_start_at",
            name="ck_commissions_schedule",
        ),
        {
            "comment": (
                "Las comisiones rechazadas o canceladas "
                "permanecen almacenadas. No deben representarse "
                "mediante DELETE físico."
            ),
        },
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    requester_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_commissions_requester",
        ),
        nullable=False,
    )

    vehicle_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "vehicles.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_commissions_vehicle",
        ),
        nullable=True,
    )

    status_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey(
            "commission_statuses.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_commissions_status",
        ),
        nullable=False,
    )

    scheduled_start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    scheduled_end_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    reviewed_by_user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_commissions_reviewer",
        ),
        nullable=True,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        server_onupdate=FetchedValue(),
    )


Index(
    "idx_commissions_requester",
    Commission.requester_user_id,
)

Index(
    "idx_commissions_status",
    Commission.status_id,
)

Index(
    "idx_commissions_vehicle_schedule",
    Commission.vehicle_id,
    Commission.scheduled_start_at,
    Commission.scheduled_end_at,
    postgresql_where=Commission.vehicle_id.is_not(None),
)
