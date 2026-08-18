from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

# Import necesario para resolver la FK commissions.id
from app.modules.commissions.model import Commission


class FuelCoupon(Base):
    __tablename__ = "fuel_coupons"


    __table_args__ = (
        CheckConstraint(
            "face_value_q > 0",
            name="ck_fuel_coupons_face_value",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    coupon_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    face_value_q: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        server_default=text("100.00"),
        comment=(
            "Actualmente los cupones son de Q100. "
            "No se restringe a exactamente Q100 para no "
            "bloquear un cambio institucional futuro."
        ),
    )

    coupon_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    gas_station: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class CommissionCoupon(Base):
    __tablename__ = "commission_coupons"

    __table_args__ = (
        CheckConstraint(
            "NOT (used_at IS NOT NULL AND returned_at IS NOT NULL)",
            name="ck_commission_coupons_not_used_and_returned",
        ),
        CheckConstraint(
            "used_at IS NULL OR used_at >= assigned_at",
            name="ck_commission_coupons_used_after_assignment",
        ),
        CheckConstraint(
            "returned_at IS NULL OR returned_at >= assigned_at",
            name="ck_commission_coupons_returned_after_assignment",
        ),
        {
            "comment": (
                "Cuando un cupón se devuelve, la relación histórica "
                "se conserva con returned_at, aunque funcionalmente "
                "deje de mostrarse como asignado a la comisión."
            ),
        },
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
            name="fk_commission_coupons_commission",
        ),
        nullable=False,
    )

    coupon_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "fuel_coupons.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_commission_coupons_coupon",
        ),
        nullable=False,
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    returned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class FuelLoad(Base):
    __tablename__ = "fuel_loads"

    __table_args__ = (
        CheckConstraint(
            "gallons > 0",
            name="ck_fuel_loads_gallons",
        ),
        CheckConstraint(
            "amount_q > 0",
            name="ck_fuel_loads_amount",
        ),
        {
            "comment": (
                "Separa el dinero/cupones asignados del combustible "
                "realmente cargado. Permite calcular galones y gasto "
                "para el dashboard."
            ),
        },
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
            name="fk_fuel_loads_commission",
        ),
        nullable=False,
    )

    loaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    gas_station: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    gallons: Mapped[Decimal] = mapped_column(
        Numeric(10, 3),
        nullable=False,
    )

    amount_q: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )




Index(
    "idx_commission_coupons_commission",
    CommissionCoupon.commission_id,
)

Index(
    "idx_commission_coupons_coupon",
    CommissionCoupon.coupon_id,
)

Index(
    "uq_commission_coupons_active_coupon",
    CommissionCoupon.coupon_id,
    unique=True,
    postgresql_where=CommissionCoupon.returned_at.is_(None),
)

Index(
    "idx_fuel_loads_commission",
    FuelLoad.commission_id,
)

Index(
    "idx_fuel_loads_loaded_at",
    FuelLoad.loaded_at,
)
