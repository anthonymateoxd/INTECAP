from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    FetchedValue,
    Index,
    Numeric,
    SmallInteger,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base




class Vehicle(Base):
    __tablename__ = "vehicles"

    __table_args__ = (
        CheckConstraint(
            "year >= 1900",
            name="ck_vehicles_year",
        ),
        CheckConstraint(
            "current_odometer_km >= 0",
            name="ck_vehicles_odometer",
        ),
        CheckConstraint(
            "tank_capacity_gal IS NULL OR tank_capacity_gal > 0",
            name="ck_vehicles_tank_capacity",
        ),
        {
            "comment": (
                "Cilindraje/C.C. no se agregan todavía porque "
                "falta confirmar si representan el mismo dato "
                "o datos diferentes."
            ),
        },
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    inventory_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    license_plate: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    brand: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    model: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    year: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    vehicle_type: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    fuel_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    current_odometer_km: Mapped[Decimal] = mapped_column(
        Numeric(12, 1),
        nullable=False,
        server_default="0",
    )

    tank_capacity_gal: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 3),
        nullable=True,
        comment=(
            "PENDIENTE DE CONFIRMACIÓN: capacidad del tanque "
            "en galones. Se deja nullable para soportar el "
            "cálculo futuro de combustible restante sin "
            "inventar valores."
        ),
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
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
    "uq_vehicles_inventory_code_ci",
    func.lower(Vehicle.inventory_code),
    unique=True,
)

Index(
    "uq_vehicles_license_plate_ci",
    func.lower(Vehicle.license_plate),
    unique=True,
)
