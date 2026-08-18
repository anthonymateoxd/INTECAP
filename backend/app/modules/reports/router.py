from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.exceptions import ReportOperationNotAllowedError
from app.database.dependencies import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.reports import service
from app.modules.reports.schemas import (
    CommissionReportFilters,
    FuelReportFilters,
    MaintenanceReportFilters,
    TripReportFilters,
    VehicleReportFilters,
)
from app.modules.users.model import User


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


def get_vehicle_report_filters(
    start_date: date | None = Query(
        default=None,
    ),
    end_date: date | None = Query(
        default=None,
    ),
    vehicle_status: Literal[
        "ALL",
        "ACTIVE",
        "INACTIVE",
    ] = Query(
        default="ALL",
        alias="status",
    ),
) -> VehicleReportFilters:
    try:
        return VehicleReportFilters(
            start_date=start_date,
            end_date=end_date,
            status=vehicle_status,
        )

    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=exc.errors(
                include_url=False,
                include_context=False,
                include_input=False,
            ),
        ) from None


@router.get(
    "/vehicles/excel",
)
def download_vehicles_excel(
    filters: VehicleReportFilters = Depends(
        get_vehicle_report_filters
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        content = service.generate_vehicles_excel(
            db,
            current_user=current_user,
            filters=filters,
        )

        return Response(
            content=content,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            headers={
                "Content-Disposition": (
                    'attachment; filename="reporte_vehiculos.xlsx"'
                ),
            },
        )

    except ReportOperationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para generar este reporte.",
        ) from None


@router.get(
    "/vehicles/pdf",
)
def download_vehicles_pdf(
    filters: VehicleReportFilters = Depends(
        get_vehicle_report_filters
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        content = service.generate_vehicles_pdf(
            db,
            current_user=current_user,
            filters=filters,
        )

        return Response(
            content=content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    'attachment; filename="reporte_vehiculos.pdf"'
                ),
            },
        )

    except ReportOperationNotAllowedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para generar este reporte.",
        ) from None


def get_commission_report_filters(
    start_date: date | None = Query(
        default=None,
    ),
    end_date: date | None = Query(
        default=None,
    ),
) -> CommissionReportFilters:
    try:
        return CommissionReportFilters(
            start_date=start_date,
            end_date=end_date,
        )

    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=exc.errors(
                include_url=False,
                include_context=False,
                include_input=False,
            ),
        ) from None


@router.get(
    "/commissions/excel",
)
def download_commissions_excel(
    filters: CommissionReportFilters = Depends(
        get_commission_report_filters
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content = service.generate_commissions_excel(
        db,
        current_user=current_user,
        filters=filters,
    )

    return Response(
        content=content,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                'attachment; filename="reporte_comisiones.xlsx"'
            ),
        },
    )


@router.get(
    "/commissions/pdf",
)
def download_commissions_pdf(
    filters: CommissionReportFilters = Depends(
        get_commission_report_filters
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content = service.generate_commissions_pdf(
        db,
        current_user=current_user,
        filters=filters,
    )

    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                'attachment; filename="reporte_comisiones.pdf"'
            ),
        },
    )


def get_trip_report_filters(
    start_date: date | None = Query(
        default=None,
    ),
    end_date: date | None = Query(
        default=None,
    ),
) -> TripReportFilters:
    try:
        return TripReportFilters(
            start_date=start_date,
            end_date=end_date,
        )

    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=exc.errors(
                include_url=False,
                include_context=False,
                include_input=False,
            ),
        ) from None


@router.get(
    "/trips/excel",
)
def download_trips_excel(
    filters: TripReportFilters = Depends(
        get_trip_report_filters
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content = service.generate_trips_excel(
        db,
        current_user=current_user,
        filters=filters,
    )

    return Response(
        content=content,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                'attachment; filename="reporte_recorridos.xlsx"'
            ),
        },
    )


@router.get(
    "/trips/pdf",
)
def download_trips_pdf(
    filters: TripReportFilters = Depends(
        get_trip_report_filters
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content = service.generate_trips_pdf(
        db,
        current_user=current_user,
        filters=filters,
    )

    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                'attachment; filename="reporte_recorridos.pdf"'
            ),
        },
    )


def get_fuel_report_filters(
    start_date: date | None = Query(
        default=None,
    ),
    end_date: date | None = Query(
        default=None,
    ),
) -> FuelReportFilters:
    try:
        return FuelReportFilters(
            start_date=start_date,
            end_date=end_date,
        )

    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=exc.errors(
                include_url=False,
                include_context=False,
                include_input=False,
            ),
        ) from None


@router.get(
    "/fuel/excel",
)
def download_fuel_excel(
    filters: FuelReportFilters = Depends(
        get_fuel_report_filters
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        content = service.generate_fuel_excel(
            db,
            current_user=current_user,
            filters=filters,
        )

    except ReportOperationNotAllowedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from None

    return Response(
        content=content,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                'attachment; filename="reporte_combustible.xlsx"'
            ),
        },
    )


@router.get(
    "/fuel/pdf",
)
def download_fuel_pdf(
    filters: FuelReportFilters = Depends(
        get_fuel_report_filters
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        content = service.generate_fuel_pdf(
            db,
            current_user=current_user,
            filters=filters,
        )

    except ReportOperationNotAllowedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from None

    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                'attachment; filename="reporte_combustible.pdf"'
            ),
        },
    )


def get_maintenance_report_filters(
    start_date: date | None = Query(
        default=None,
    ),
    end_date: date | None = Query(
        default=None,
    ),
) -> MaintenanceReportFilters:
    try:
        return MaintenanceReportFilters(
            start_date=start_date,
            end_date=end_date,
        )

    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=exc.errors(
                include_url=False,
                include_context=False,
                include_input=False,
            ),
        ) from None



@router.get(
    "/maintenance/excel",
)
def download_maintenance_excel(
    filters: MaintenanceReportFilters = Depends(
        get_maintenance_report_filters
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        content = service.generate_maintenance_excel(
            db,
            current_user=current_user,
            filters=filters,
        )

    except ReportOperationNotAllowedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from None

    return Response(
        content=content,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                'attachment; filename="reporte_mantenimiento.xlsx"'
            ),
        },
    )


@router.get(
    "/maintenance/pdf",
)
def download_maintenance_pdf(
    filters: MaintenanceReportFilters = Depends(
        get_maintenance_report_filters
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        content = service.generate_maintenance_pdf(
            db,
            current_user=current_user,
            filters=filters,
        )

    except ReportOperationNotAllowedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from None

    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                'attachment; filename="reporte_mantenimiento.pdf"'
            ),
        },
    )
