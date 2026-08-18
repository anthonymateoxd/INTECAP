from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CHAR,
    CheckConstraint,
    Computed,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.modules.commissions.model import Commission
from app.modules.users.model import User


class Trip(Base):
    __tablename__ = "trips"

    __table_args__ = (
        UniqueConstraint(
            "commission_id",
            "sequence_number",
            name="uq_trips_commission_sequence",
        ),
        CheckConstraint(
            "sequence_number > 0",
            name="ck_trips_sequence",
        ),
        CheckConstraint(
            "odometer_start_km >= 0",
            name="ck_trips_odometer_start",
        ),
        CheckConstraint(
            "odometer_end_km >= odometer_start_km",
            name="ck_trips_odometer_order",
        ),
        CheckConstraint(
            (
                "tank_balance_percent IS NULL "
                "OR tank_balance_percent BETWEEN 0 AND 100"
            ),
            name="ck_trips_tank_balance",
        ),
        CheckConstraint(
            "road_type IN ('A', 'T')",
            name="ck_trips_road_type",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    commission_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "commissions.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_trips_commission",
        ),
        nullable=False,
    )

    driver_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_trips_driver",
        ),
        nullable=False,
    )

    sequence_number: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    trip_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    origin: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    destination: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    odometer_start_km: Mapped[Decimal] = mapped_column(
        Numeric(12, 1),
        nullable=False,
    )

    odometer_end_km: Mapped[Decimal] = mapped_column(
        Numeric(12, 1),
        nullable=False,
    )

    distance_km: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 1),
        Computed(
            "odometer_end_km - odometer_start_km",
            persisted=True,
        ),
        nullable=True,
    )

    tank_balance_percent: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment=(
            "Porcentaje estimado de combustible restante. "
            "La equivalencia exacta del valor E del formato "
            "actual sigue pendiente de confirmación."
        ),
    )

    road_type: Mapped[str] = mapped_column(
        CHAR(1),
        nullable=False,
        comment="A = Asfalto, T = Tierra.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    deleted_by_user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_trips_deleted_by",
        ),
        nullable=True,
    )


Index(
    "idx_trips_commission",
    Trip.commission_id,
)

Index(
    "idx_trips_driver",
    Trip.driver_user_id,
)

Index(
    "idx_trips_date",
    Trip.trip_date,
)
