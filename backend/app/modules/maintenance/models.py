from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    text,
)
from app.modules.users.model import User
from sqlalchemy.orm import relationship
from app.modules.vehicles.model import Vehicle

from app.database.base import Base


maintenance_event_services = Table(
    "maintenance_event_services",
    Base.metadata,
    Column(
        "maintenance_event_id",
        BigInteger,
        ForeignKey(
            "maintenance_events.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        primary_key=True,
    ),
    Column(
        "service_type_id",
        BigInteger,
        ForeignKey(
            "service_types.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        primary_key=True,
    ),
)

Index(
    "idx_maintenance_event_services_service",
    maintenance_event_services.c.service_type_id,
)

class MaintenanceEvent(Base):
    __tablename__ = "maintenance_events"

    __table_args__ = (
        CheckConstraint(
            "maintenance_type IN ('PREVENTIVO', 'CORRECTIVO')",
            name="ck_maintenance_events_type",
        ),
        CheckConstraint(
            "odometer_km IS NULL OR odometer_km >= 0",
            name="ck_maintenance_events_odometer",
        ),
        Index(
            "idx_maintenance_events_vehicle_date",
            "vehicle_id",
            "maintenance_date",
        ),
    )

    id = Column(
        BigInteger,
        primary_key=True,
    )

    vehicle_id = Column(
        BigInteger,
        ForeignKey(
            "vehicles.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    maintenance_type = Column(
        String(20),
        nullable=False,
    )

    maintenance_date = Column(
        Date,
        nullable=False,
    )

    odometer_km = Column(
        Numeric(12, 1),
        nullable=True,
    )

    workshop = Column(
        String(150),
        nullable=True,
    )

    cost_q = Column(
        Numeric(12, 2),
        nullable=True,
    )

    invoice_number = Column(
        String(100),
        nullable=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    next_maintenance_date = Column(
        Date,
        nullable=True,
    )

    next_maintenance_odometer_km = Column(
        Numeric(12, 1),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    services = relationship(
        "ServiceType",
        secondary=maintenance_event_services,
        back_populates="maintenance_events",
    )

    parts = relationship(
        "MaintenancePart",
        back_populates="maintenance_event",
    )

    is_deleted = Column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    deleted_by_user_id = Column(
        BigInteger,
        ForeignKey(
            "users.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
            name="fk_maintenance_events_deleted_by",
        ),
        nullable=True,
    )


class ServiceType(Base):
    __tablename__ = "service_types"

    __table_args__ = (
        CheckConstraint(
            "interval_km IS NULL OR interval_km > 0",
            name="ck_service_types_interval_km",
        ),
        CheckConstraint(
            "interval_days IS NULL OR interval_days > 0",
            name="ck_service_types_interval_days",
        ),
        {
            "comment": (
                "PENDIENTE DE CONFIRMACIÓN: determinar si la "
                "periodicidad de servicios se controla por "
                "kilometraje, tiempo o ambos. La V1 soporta "
                "las tres posibilidades sin obligar ninguna."
            ),
        },
    )

    id = Column(
        BigInteger,
        primary_key=True,
    )

    name = Column(
        String(150),
        nullable=False,
        unique=True,
    )

    interval_km = Column(
        Numeric(12, 1),
        nullable=True,
    )

    interval_days = Column(
        Integer,
        nullable=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    maintenance_events = relationship(
        "MaintenanceEvent",
        secondary=maintenance_event_services,
        back_populates="services",
    )


class MaintenancePart(Base):
    __tablename__ = "maintenance_parts"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_maintenance_parts_quantity",
        ),
        Index(
            "idx_maintenance_parts_event",
            "maintenance_event_id",
        ),
    )

    id = Column(
        BigInteger,
        primary_key=True,
    )

    maintenance_event_id = Column(
        BigInteger,
        ForeignKey(
            "maintenance_events.id",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    part_name = Column(
        String(150),
        nullable=False,
    )

    quantity = Column(
        Integer,
        nullable=False,
        server_default=text("1"),
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    maintenance_event = relationship(
        "MaintenanceEvent",
        back_populates="parts",
    )
