from sqlalchemy.orm import Session
from app.modules.reports.excel import (
    build_commissions_excel,
    build_fuel_excel,
    build_maintenance_excel,
    build_trips_excel,
    build_vehicles_excel,
)

from app.modules.reports.pdf import (
    build_commissions_pdf,
    build_fuel_pdf,
    build_maintenance_pdf,
    build_trips_pdf,
    build_vehicles_pdf,
)
from app.core.constants import ROLE_ADMINISTRATION
from app.core.exceptions import ReportOperationNotAllowedError
from app.modules.reports import repository
from app.modules.reports.schemas import (
    CommissionReportFilters,
    CommissionReportRow,
    FuelReportFilters,
    FuelReportRow,
    MaintenanceReportFilters,
    MaintenanceReportRow,
    TripReportFilters,
    TripReportRow,
    VehicleReportFilters,
    VehicleReportRow,
)
from app.modules.users.model import User
from app.modules.vehicles.model import Vehicle


def get_vehicles_report(
    db: Session,
    *,
    current_user: User,
    filters: VehicleReportFilters,
) -> list[Vehicle]:
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise ReportOperationNotAllowedError()

    is_active: bool | None = None

    if filters.status == "ACTIVE":
        is_active = True

    elif filters.status == "INACTIVE":
        is_active = False

    return repository.get_vehicles_report(
        db,
        start_date=filters.start_date,
        end_date=filters.end_date,
        is_active=is_active,
    )


def build_vehicle_report_rows(
    vehicles: list[Vehicle],
) -> list[VehicleReportRow]:
    return [
        VehicleReportRow(
            inventory_code=vehicle.inventory_code,
            license_plate=vehicle.license_plate,
            brand=vehicle.brand,
            model=vehicle.model,
            year=vehicle.year,
            vehicle_type=vehicle.vehicle_type,
            fuel_type=vehicle.fuel_type,
            current_odometer_km=vehicle.current_odometer_km,
            tank_capacity_gal=vehicle.tank_capacity_gal,
            status=(
                "Activo"
                if vehicle.is_active
                else "Inactivo"
            ),
            created_at=vehicle.created_at,
        )
        for vehicle in vehicles
    ]



def generate_vehicles_excel(
    db: Session,
    *,
    current_user: User,
    filters: VehicleReportFilters,
) -> bytes:
    vehicles = get_vehicles_report(
        db,
        current_user=current_user,
        filters=filters,
    )

    rows = build_vehicle_report_rows(
        vehicles,
    )

    return build_vehicles_excel(
        rows=rows,
        filters=filters,
    )


def generate_vehicles_pdf(
    db: Session,
    *,
    current_user: User,
    filters: VehicleReportFilters,
) -> bytes:
    vehicles = get_vehicles_report(
        db,
        current_user=current_user,
        filters=filters,
    )

    rows = build_vehicle_report_rows(
        vehicles,
    )

    return build_vehicles_pdf(
        rows=rows,
        filters=filters,
    )



def get_commissions_report(
    db: Session,
    *,
    current_user: User,
    filters: CommissionReportFilters,
) -> list:
    requester_user_id: int | None = None

    if current_user.role.code != ROLE_ADMINISTRATION:
        requester_user_id = current_user.id

    return repository.get_commissions_report(
        db,
        start_date=filters.start_date,
        end_date=filters.end_date,
        requester_user_id=requester_user_id,
    )


def build_commission_report_rows(
    report_data: list,
) -> list[CommissionReportRow]:
    rows: list[CommissionReportRow] = []

    for item in report_data:
        commission = item[0]
        requester_name = item[1]
        reviewer_name = item[2]
        vehicle = item[3]
        commission_status = item[4]

        vehicle_text = (
            f"{vehicle.brand} {vehicle.model} / "
            f"{vehicle.license_plate}"
            if vehicle is not None
            else "Sin vehículo"
        )

        rows.append(
            CommissionReportRow(
                requester_name=requester_name,
                vehicle=vehicle_text,
                status=commission_status.name,
                scheduled_start_at=(
                    commission.scheduled_start_at
                ),
                scheduled_end_at=(
                    commission.scheduled_end_at
                ),
                reviewer_name=reviewer_name,
                reviewed_at=commission.reviewed_at,
                created_at=commission.created_at,
            )
        )

    return rows


def generate_commissions_excel(
    db: Session,
    *,
    current_user: User,
    filters: CommissionReportFilters,
) -> bytes:
    report_data = get_commissions_report(
        db,
        current_user=current_user,
        filters=filters,
    )

    rows = build_commission_report_rows(
        report_data,
    )

    return build_commissions_excel(
        rows=rows,
        filters=filters,
    )


def generate_commissions_pdf(
    db: Session,
    *,
    current_user: User,
    filters: CommissionReportFilters,
) -> bytes:
    report_data = get_commissions_report(
        db,
        current_user=current_user,
        filters=filters,
    )

    rows = build_commission_report_rows(
        report_data,
    )

    return build_commissions_pdf(
        rows=rows,
        filters=filters,
    )




def get_trips_report(
    db: Session,
    *,
    current_user: User,
    filters: TripReportFilters,
) -> list:
    requester_user_id: int | None = None

    if current_user.role.code != ROLE_ADMINISTRATION:
        requester_user_id = current_user.id

    return repository.get_trips_report(
        db,
        start_date=filters.start_date,
        end_date=filters.end_date,
        requester_user_id=requester_user_id,
    )


def build_trip_report_rows(
    report_data: list,
) -> list[TripReportRow]:
    rows: list[TripReportRow] = []

    for item in report_data:
        trip = item[0]
        vehicle = item[1]
        driver_name = item[2]

        vehicle_text = (
            f"{vehicle.brand} {vehicle.model} / "
            f"{vehicle.license_plate}"
            if vehicle is not None
            else "Sin vehículo"
        )

        rows.append(
            TripReportRow(
                trip_date=trip.trip_date,
                vehicle=vehicle_text,
                driver_name=driver_name,
                sequence_number=trip.sequence_number,
                origin=trip.origin,
                destination=trip.destination,
                odometer_start_km=trip.odometer_start_km,
                odometer_end_km=trip.odometer_end_km,
                distance_km=trip.distance_km,
                tank_balance_percent=trip.tank_balance_percent,
                road_type={
                    "A": "Asfalto",
                    "T": "Terracería",
                }.get(
                    trip.road_type,
                    trip.road_type,
                ),
            )
        )

    return rows


def generate_trips_excel(
    db: Session,
    *,
    current_user: User,
    filters: TripReportFilters,
) -> bytes:
    report_data = get_trips_report(
        db,
        current_user=current_user,
        filters=filters,
    )

    rows = build_trip_report_rows(
        report_data,
    )

    return build_trips_excel(
        rows=rows,
        filters=filters,
    )


def generate_trips_pdf(
    db: Session,
    *,
    current_user: User,
    filters: TripReportFilters,
) -> bytes:
    report_data = get_trips_report(
        db,
        current_user=current_user,
        filters=filters,
    )

    rows = build_trip_report_rows(
        report_data,
    )

    return build_trips_pdf(
        rows=rows,
        filters=filters,
    )


def get_fuel_report(
    db: Session,
    *,
    current_user: User,
    filters: FuelReportFilters,
) -> list:
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise ReportOperationNotAllowedError()

    return repository.get_fuel_loads_report(
        db,
        start_date=filters.start_date,
        end_date=filters.end_date,
    )


def build_fuel_report_rows(
    report_data: list,
) -> list[FuelReportRow]:
    rows: list[FuelReportRow] = []

    for item in report_data:
        fuel_load = item[0]
        requester_name = item[1]
        vehicle = item[2]

        vehicle_text = (
            f"{vehicle.brand} {vehicle.model} / "
            f"{vehicle.license_plate}"
            if vehicle is not None
            else "Sin vehículo"
        )

        rows.append(
            FuelReportRow(
                loaded_at=fuel_load.loaded_at,
                requester_name=requester_name,
                vehicle=vehicle_text,
                gas_station=fuel_load.gas_station,
                gallons=fuel_load.gallons,
                amount_q=fuel_load.amount_q,
            )
        )

    return rows


def generate_fuel_excel(
    db: Session,
    *,
    current_user: User,
    filters: FuelReportFilters,
) -> bytes:
    report_data = get_fuel_report(
        db,
        current_user=current_user,
        filters=filters,
    )

    rows = build_fuel_report_rows(
        report_data,
    )

    return build_fuel_excel(
        rows=rows,
        filters=filters,
    )


def generate_fuel_pdf(
    db: Session,
    *,
    current_user: User,
    filters: FuelReportFilters,
) -> bytes:
    report_data = get_fuel_report(
        db,
        current_user=current_user,
        filters=filters,
    )

    rows = build_fuel_report_rows(
        report_data,
    )

    return build_fuel_pdf(
        rows=rows,
        filters=filters,
    )


def get_maintenance_report(
    db: Session,
    *,
    current_user: User,
    filters: MaintenanceReportFilters,
) -> list:
    if current_user.role.code != ROLE_ADMINISTRATION:
        raise ReportOperationNotAllowedError()

    return repository.get_maintenance_report(
        db,
        start_date=filters.start_date,
        end_date=filters.end_date,
    )


def build_maintenance_report_rows(
    report_data: list,
) -> list[MaintenanceReportRow]:
    rows: list[MaintenanceReportRow] = []

    for item in report_data:
        event = item[0]
        vehicle = item[1]

        vehicle_text = (
            f"{vehicle.brand} {vehicle.model} / "
            f"{vehicle.license_plate}"
        )

        services_text = ", ".join(
            sorted(
                service.name
                for service in event.services
            )
        ) or "-"

        parts_text = ", ".join(
            f"{part.part_name} ({part.quantity})"
            for part in sorted(
                event.parts,
                key=lambda part: part.id,
            )
        ) or "-"

        maintenance_type = {
            "PREVENTIVO": "Preventivo",
            "CORRECTIVO": "Correctivo",
        }.get(
            event.maintenance_type,
            event.maintenance_type,
        )

        rows.append(
            MaintenanceReportRow(
                maintenance_date=event.maintenance_date,
                vehicle=vehicle_text,
                maintenance_type=maintenance_type,
                odometer_km=event.odometer_km,
                workshop=event.workshop,
                cost_q=event.cost_q,
                invoice_number=event.invoice_number,
                description=event.description,
                services=services_text,
                parts=parts_text,
                next_maintenance_date=(
                    event.next_maintenance_date
                ),
                next_maintenance_odometer_km=(
                    event.next_maintenance_odometer_km
                ),
            )
        )

    return rows


def generate_maintenance_excel(
    db: Session,
    *,
    current_user: User,
    filters: MaintenanceReportFilters,
) -> bytes:
    report_data = get_maintenance_report(
        db,
        current_user=current_user,
        filters=filters,
    )

    rows = build_maintenance_report_rows(
        report_data,
    )

    return build_maintenance_excel(
        rows=rows,
        filters=filters,
    )


def generate_maintenance_pdf(
    db: Session,
    *,
    current_user: User,
    filters: MaintenanceReportFilters,
) -> bytes:
    report_data = get_maintenance_report(
        db,
        current_user=current_user,
        filters=filters,
    )

    rows = build_maintenance_report_rows(
        report_data,
    )

    return build_maintenance_pdf(
        rows=rows,
        filters=filters,
    )
