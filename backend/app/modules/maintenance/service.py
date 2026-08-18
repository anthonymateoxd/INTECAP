from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.constants import ROLE_ADMINISTRATION
from app.modules.commissions import repository as commission_repository
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from app.modules.maintenance import repository
from app.modules.maintenance.models import (
    MaintenanceEvent,
    ServiceType,
)
from app.modules.users.model import User
from app.core.exceptions import (
    MaintenanceEventNotFoundError,
    MaintenanceOperationNotAllowedError,
    ServiceTypeInactiveError,
    ServiceTypeNameAlreadyExistsError,
    ServiceTypeNotFoundError,
    VehicleNotFoundError,
    MaintenanceEventAlreadyDeletedError,
)
from app.modules.maintenance.schemas import (
    MaintenanceEventCreate,
    MaintenanceEventUpdate,
    ServiceTypeCreate,
    ServiceTypeUpdate,
)
from app.modules.vehicles import repository as vehicle_repository

def list_service_types(
    db: Session,
    *,
    current_user: User,
    only_active: bool = False,
) -> list[ServiceType]:
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise MaintenanceOperationNotAllowedError()

    return repository.get_service_types(
        db,
        only_active=only_active,
    )


def get_service_type(
    db: Session,
    *,
    service_type_id: int,
    current_user: User,
) -> ServiceType:
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise MaintenanceOperationNotAllowedError()

    service_type = repository.get_service_type_by_id(
        db,
        service_type_id,
    )

    if service_type is None:
        raise ServiceTypeNotFoundError()

    return service_type



def create_service_type(
    db: Session,
    *,
    current_user: User,
    service_type_data: ServiceTypeCreate,
) -> ServiceType:
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise MaintenanceOperationNotAllowedError()

    existing_service_type = (
        repository.get_service_type_by_name(
            db,
            service_type_data.name,
        )
    )

    if existing_service_type is not None:
        raise ServiceTypeNameAlreadyExistsError()

    try:
        service_type = repository.create_service_type(
            db,
            service_type_data,
        )

        db.commit()
        db.refresh(service_type)

        return service_type

    except IntegrityError as exc:
        db.rollback()

        if getattr(exc.orig, "sqlstate", None) == "23505":
            raise ServiceTypeNameAlreadyExistsError() from exc

        raise

    except Exception:
        db.rollback()
        raise

def update_service_type(
    db: Session,
    *,
    service_type_id: int,
    current_user: User,
    service_type_data: ServiceTypeUpdate,
) -> ServiceType:
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise MaintenanceOperationNotAllowedError()

    service_type = repository.get_service_type_by_id(
        db,
        service_type_id,
    )

    if service_type is None:
        raise ServiceTypeNotFoundError()

    if (
        "name" in service_type_data.model_fields_set
        and service_type_data.name is not None
    ):
        existing_service_type = (
            repository.get_service_type_by_name(
                db,
                service_type_data.name,
            )
        )

        if (
            existing_service_type is not None
            and existing_service_type.id != service_type.id
        ):
            raise ServiceTypeNameAlreadyExistsError()

    try:
        service_type = repository.update_service_type(
            db,
            service_type=service_type,
            service_type_data=service_type_data,
        )

        db.commit()
        db.refresh(service_type)

        return service_type

    except IntegrityError as exc:
        db.rollback()

        if getattr(exc.orig, "sqlstate", None) == "23505":
            raise ServiceTypeNameAlreadyExistsError() from exc

        raise

    except Exception:
        db.rollback()
        raise


def deactivate_service_type(
    db: Session,
    *,
    service_type_id: int,
    current_user: User,
) -> ServiceType:
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise MaintenanceOperationNotAllowedError()

    service_type = repository.get_service_type_by_id(
        db,
        service_type_id,
    )

    if service_type is None:
        raise ServiceTypeNotFoundError()

    try:
        service_type = repository.deactivate_service_type(
            db,
            service_type=service_type,
        )

        db.commit()
        db.refresh(service_type)

        return service_type

    except Exception:
        db.rollback()
        raise


def calculate_next_maintenance(
    *,
    maintenance_date: date,
    odometer_km: Decimal | None,
    service_types: list[ServiceType],
    manual_next_date: date | None = None,
    manual_next_odometer_km: Decimal | None = None,
) -> tuple[date | None, Decimal | None]:
    next_date: date | None = None
    next_odometer_km: Decimal | None = None

    day_intervals = [
        service.interval_days
        for service in service_types
        if service.interval_days is not None
    ]

    km_intervals = [
        service.interval_km
        for service in service_types
        if service.interval_km is not None
    ]

    if day_intervals:
        next_date = maintenance_date + timedelta(
            days=min(day_intervals)
        )

    if odometer_km is not None and km_intervals:
        next_odometer_km = (
            odometer_km
            + min(km_intervals)
        )

    if manual_next_date is not None:
        next_date = manual_next_date

    if manual_next_odometer_km is not None:
        next_odometer_km = manual_next_odometer_km

    return next_date, next_odometer_km


def create_maintenance_event(
    db: Session,
    *,
    current_user: User,
    maintenance_data: MaintenanceEventCreate,
) -> MaintenanceEvent:
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise MaintenanceOperationNotAllowedError()

    vehicle = vehicle_repository.get_vehicle_by_id(
        db,
        maintenance_data.vehicle_id,
    )

    if vehicle is None:
        raise VehicleNotFoundError()

    service_types: list[ServiceType] = []

    # Evita repetir el mismo servicio dentro del mismo mantenimiento.
    service_type_ids = list(
        dict.fromkeys(
            maintenance_data.service_type_ids
        )
    )

    for service_type_id in service_type_ids:
        service_type = repository.get_service_type_by_id(
            db,
            service_type_id,
        )

        if service_type is None:
            raise ServiceTypeNotFoundError()

        if not service_type.is_active:
            raise ServiceTypeInactiveError()

        service_types.append(service_type)

    next_date, next_odometer_km = calculate_next_maintenance(
        maintenance_date=maintenance_data.maintenance_date,
        odometer_km=maintenance_data.odometer_km,
        service_types=service_types,
        manual_next_date=maintenance_data.next_maintenance_date,
        manual_next_odometer_km=(
            maintenance_data.next_maintenance_odometer_km
        ),
    )

    try:
        event = repository.create_maintenance_event(
            db,
            vehicle_id=maintenance_data.vehicle_id,
            maintenance_type=maintenance_data.maintenance_type,
            maintenance_date=maintenance_data.maintenance_date,
            odometer_km=maintenance_data.odometer_km,
            workshop=maintenance_data.workshop,
            cost_q=maintenance_data.cost_q,
            invoice_number=maintenance_data.invoice_number,
            description=maintenance_data.description,
            next_maintenance_date=next_date,
            next_maintenance_odometer_km=next_odometer_km,
        )

        for service_type in service_types:
            repository.add_service_to_maintenance_event(
                db,
                event=event,
                service_type=service_type,
            )

        for part_data in maintenance_data.parts:
            repository.create_maintenance_part(
                db,
                maintenance_event_id=event.id,
                part_name=part_data.part_name,
                quantity=part_data.quantity,
            )

        db.commit()
        db.refresh(event)

        return event

    except Exception:
        db.rollback()
        raise



def can_view_vehicle_maintenance_history(
    db: Session,
    *,
    current_user: User,
    vehicle_id: int,
) -> bool:
    if current_user.role.code == ROLE_ADMINISTRATION:
        return True

    approved_status = (
        commission_repository.get_commission_status_by_code(
            db,
            "APPROVED",
        )
    )

    if approved_status is None:
        return False

    commissions = (
        commission_repository.get_commissions_by_requester(
            db,
            current_user.id,
        )
    )

    return any(
        commission.vehicle_id == vehicle_id
        and commission.status_id == approved_status.id
        for commission in commissions
    )


def list_vehicle_maintenance_history(
    db: Session,
    *,
    current_user: User,
    vehicle_id: int,
) -> list[MaintenanceEvent]:
    vehicle = vehicle_repository.get_vehicle_by_id(
        db,
        vehicle_id,
    )

    if vehicle is None:
        raise VehicleNotFoundError()

    if not can_view_vehicle_maintenance_history(
        db,
        current_user=current_user,
        vehicle_id=vehicle_id,
    ):
        raise MaintenanceOperationNotAllowedError()

    return repository.get_maintenance_events_by_vehicle(
        db,
        vehicle_id,
    )

def update_maintenance_event(
    db: Session,
    *,
    maintenance_event_id: int,
    current_user: User,
    maintenance_data: MaintenanceEventUpdate,
) -> MaintenanceEvent:
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise MaintenanceOperationNotAllowedError()

    event = repository.get_maintenance_event_by_id(
        db,
        maintenance_event_id,
    )

    if event is None:
        raise MaintenanceEventNotFoundError()

    # Si cambia el vehículo, únicamente comprobamos que exista.
    # Puede estar activo o desactivado.
    if (
        "vehicle_id" in maintenance_data.model_fields_set
        and maintenance_data.vehicle_id is not None
    ):
        vehicle = vehicle_repository.get_vehicle_by_id(
            db,
            maintenance_data.vehicle_id,
        )

        if vehicle is None:
            raise VehicleNotFoundError()

    # Servicios finales del mantenimiento.
    service_types = list(event.services)

    if (
        "service_type_ids" in maintenance_data.model_fields_set
        and maintenance_data.service_type_ids is not None
    ):
        service_types = []

        service_type_ids = list(
            dict.fromkeys(
                maintenance_data.service_type_ids
            )
        )

        for service_type_id in service_type_ids:
            service_type = repository.get_service_type_by_id(
                db,
                service_type_id,
            )

            if service_type is None:
                raise ServiceTypeNotFoundError()

            if not service_type.is_active:
                raise ServiceTypeInactiveError()

            service_types.append(service_type)

    try:
        # Campos normales, excluyendo relaciones y próximo mantenimiento,
        # porque este último se recalcula después.
        update_data = maintenance_data.model_dump(
            exclude_unset=True,
            exclude={
                "service_type_ids",
                "parts",
                "next_maintenance_date",
                "next_maintenance_odometer_km",
            },
        )

        if update_data:
            repository.update_maintenance_event(
                db,
                event=event,
                update_data=update_data,
            )

        # Si service_type_ids fue enviado, reemplazamos la selección.
        if (
            "service_type_ids"
            in maintenance_data.model_fields_set
            and maintenance_data.service_type_ids is not None
        ):
            repository.replace_maintenance_event_services(
                db,
                event=event,
                service_types=service_types,
            )

        # Si parts fue enviado, reemplazamos las piezas.
        if (
            "parts" in maintenance_data.model_fields_set
            and maintenance_data.parts is not None
        ):
            repository.replace_maintenance_event_parts(
                db,
                event=event,
                parts=maintenance_data.parts,
            )

        # Siempre se recalcula en una edición.
        manual_next_date = None
        manual_next_odometer_km = None

        if (
            "next_maintenance_date"
            in maintenance_data.model_fields_set
        ):
            manual_next_date = (
                maintenance_data.next_maintenance_date
            )

        if (
            "next_maintenance_odometer_km"
            in maintenance_data.model_fields_set
        ):
            manual_next_odometer_km = (
                maintenance_data.next_maintenance_odometer_km
            )

        next_date, next_odometer_km = (
            calculate_next_maintenance(
                maintenance_date=event.maintenance_date,
                odometer_km=event.odometer_km,
                service_types=service_types,
                manual_next_date=manual_next_date,
                manual_next_odometer_km=(
                    manual_next_odometer_km
                ),
            )
        )

        repository.update_maintenance_event(
            db,
            event=event,
            update_data={
                "next_maintenance_date": next_date,
                "next_maintenance_odometer_km": (
                    next_odometer_km
                ),
            },
        )

        db.commit()
        db.refresh(event)

        return event

    except Exception:
        db.rollback()
        raise


def delete_maintenance_event(
    db: Session,
    *,
    maintenance_event_id: int,
    current_user: User,
) -> MaintenanceEvent:
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise MaintenanceOperationNotAllowedError()

    event = (
        repository.get_maintenance_event_by_id_including_deleted(
            db,
            maintenance_event_id,
        )
    )

    if event is None:
        raise MaintenanceEventNotFoundError()

    if event.is_deleted:
        raise MaintenanceEventAlreadyDeletedError()

    try:
        deleted_event = repository.soft_delete_maintenance_event(
            db,
            event=event,
            deleted_by_user_id=current_user.id,
            deleted_at=datetime.now(timezone.utc),
        )

        db.commit()
        db.refresh(deleted_event)

        return deleted_event

    except Exception:
        db.rollback()
        raise
