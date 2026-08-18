from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.maintenance.models import (
    MaintenanceEvent,
    MaintenancePart,
    ServiceType,
)
from app.modules.maintenance.schemas import (
    ServiceTypeCreate,
    ServiceTypeUpdate,
)
from sqlalchemy import delete, select
def get_service_types(
    db: Session,
    *,
    only_active: bool = False,
) -> list[ServiceType]:
    statement = (
        select(ServiceType)
        .order_by(
            ServiceType.name,
            ServiceType.id,
        )
    )

    if only_active:
        statement = statement.where(
            ServiceType.is_active.is_(True)
        )

    return list(
        db.scalars(statement).all()
    )


def get_service_type_by_id(
    db: Session,
    service_type_id: int,
) -> ServiceType | None:
    statement = select(ServiceType).where(
        ServiceType.id == service_type_id
    )

    return db.scalars(statement).first()


def get_service_type_by_name(
    db: Session,
    name: str,
) -> ServiceType | None:
    statement = select(ServiceType).where(
        ServiceType.name == name
    )

    return db.scalars(statement).first()


def create_service_type(
    db: Session,
    service_type_data: ServiceTypeCreate,
) -> ServiceType:
    service_type = ServiceType(
        **service_type_data.model_dump(),
    )

    db.add(service_type)
    db.flush()
    db.refresh(service_type)

    return service_type


def get_maintenance_events(
    db: Session,
) -> list[MaintenanceEvent]:
    statement = (
        select(MaintenanceEvent)
        .where(
            MaintenanceEvent.is_deleted.is_(False),
        )
        .order_by(
            MaintenanceEvent.maintenance_date,
            MaintenanceEvent.id,
        )
    )

    return list(
        db.scalars(statement).all()
    )

def get_maintenance_events_by_vehicle(
    db: Session,
    vehicle_id: int,
) -> list[MaintenanceEvent]:
    statement = (
        select(MaintenanceEvent)
        .where(
            MaintenanceEvent.vehicle_id == vehicle_id,
            MaintenanceEvent.is_deleted.is_(False),
        )
        .order_by(
            MaintenanceEvent.maintenance_date,
            MaintenanceEvent.id,
        )
    )

    return list(
        db.scalars(statement).all()
    )

def get_maintenance_event_by_id(
    db: Session,
    maintenance_event_id: int,
) -> MaintenanceEvent | None:
    statement = select(MaintenanceEvent).where(
        MaintenanceEvent.id == maintenance_event_id,
        MaintenanceEvent.is_deleted.is_(False),
    )

    return db.scalars(statement).first()



def create_maintenance_event(
    db: Session,
    *,
    vehicle_id: int,
    maintenance_type: str,
    maintenance_date,
    odometer_km=None,
    workshop=None,
    cost_q=None,
    invoice_number=None,
    description=None,
    next_maintenance_date=None,
    next_maintenance_odometer_km=None,
) -> MaintenanceEvent:
    event = MaintenanceEvent(
        vehicle_id=vehicle_id,
        maintenance_type=maintenance_type,
        maintenance_date=maintenance_date,
        odometer_km=odometer_km,
        workshop=workshop,
        cost_q=cost_q,
        invoice_number=invoice_number,
        description=description,
        next_maintenance_date=next_maintenance_date,
        next_maintenance_odometer_km=(
            next_maintenance_odometer_km
        ),
    )

    db.add(event)
    db.flush()
    db.refresh(event)

    return event


def add_service_to_maintenance_event(
    db: Session,
    *,
    event: MaintenanceEvent,
    service_type: ServiceType,
) -> MaintenanceEvent:
    event.services.append(service_type)

    db.flush()
    db.refresh(event)

    return event


def create_maintenance_part(
    db: Session,
    *,
    maintenance_event_id: int,
    part_name: str,
    quantity: int = 1,
) -> MaintenancePart:
    part = MaintenancePart(
        maintenance_event_id=maintenance_event_id,
        part_name=part_name,
        quantity=quantity,
    )

    db.add(part)
    db.flush()
    db.refresh(part)

    return part


def get_maintenance_parts_by_event(
    db: Session,
    maintenance_event_id: int,
) -> list[MaintenancePart]:
    statement = (
        select(MaintenancePart)
        .where(
            MaintenancePart.maintenance_event_id
            == maintenance_event_id
        )
        .order_by(
            MaintenancePart.id,
        )
    )

    return list(
        db.scalars(statement).all()
    )

def update_service_type(
    db: Session,
    *,
    service_type: ServiceType,
    service_type_data: ServiceTypeUpdate,
) -> ServiceType:
    values = service_type_data.model_dump(
        exclude_unset=True,
    )

    for field, value in values.items():
        setattr(
            service_type,
            field,
            value,
        )

    db.flush()
    db.refresh(service_type)

    return service_type


def deactivate_service_type(
    db: Session,
    *,
    service_type: ServiceType,
) -> ServiceType:
    service_type.is_active = False

    db.flush()
    db.refresh(service_type)

    return service_type

def update_maintenance_event(
    db: Session,
    *,
    event: MaintenanceEvent,
    update_data: dict,
) -> MaintenanceEvent:
    for field, value in update_data.items():
        setattr(
            event,
            field,
            value,
        )

    db.flush()
    db.refresh(event)

    return event


def replace_maintenance_event_services(
    db: Session,
    *,
    event: MaintenanceEvent,
    service_types: list[ServiceType],
) -> MaintenanceEvent:
    event.services[:] = service_types

    db.flush()
    db.expire(
        event,
        ["services"],
    )

    return event


def replace_maintenance_event_parts(
    db: Session,
    *,
    event: MaintenanceEvent,
    parts: list,
) -> MaintenanceEvent:
    db.execute(
        delete(MaintenancePart).where(
            MaintenancePart.maintenance_event_id
            == event.id
        )
    )

    db.flush()

    for part_data in parts:
        create_maintenance_part(
            db,
            maintenance_event_id=event.id,
            part_name=part_data.part_name,
            quantity=part_data.quantity,
        )

    db.flush()
    db.expire(
        event,
        ["parts"],
    )

    return event


def get_maintenance_event_by_id_including_deleted(
    db: Session,
    maintenance_event_id: int,
) -> MaintenanceEvent | None:
    statement = select(MaintenanceEvent).where(
        MaintenanceEvent.id == maintenance_event_id,
    )

    return db.scalars(statement).first()


def soft_delete_maintenance_event(
    db: Session,
    *,
    event: MaintenanceEvent,
    deleted_by_user_id: int,
    deleted_at,
) -> MaintenanceEvent:
    event.is_deleted = True
    event.deleted_by_user_id = deleted_by_user_id
    event.deleted_at = deleted_at

    db.flush()
    db.refresh(event)

    return event
