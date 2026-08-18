from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from decimal import Decimal
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

VEHICLE_REPORT_HEADERS = [
    "Código de inventario",
    "Placa",
    "Marca",
    "Modelo",
    "Año",
    "Tipo de vehículo",
    "Combustible",
    "Kilometraje (km)",
    "Tanque (gal)",
    "Estado",
    "Fecha de registro",
]


def build_vehicles_pdf(
    *,
    rows: list[VehicleReportRow],
    filters: VehicleReportFilters,
) -> bytes:
    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title="Reporte de vehículos",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "VehicleReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=19,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    info_style = ParagraphStyle(
        "VehicleReportInfo",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
    )

    header_style = ParagraphStyle(
        "VehicleReportHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=6.5,
        leading=8,
        alignment=TA_CENTER,
    )

    cell_style = ParagraphStyle(
        "VehicleReportCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=6.5,
        leading=8,
        alignment=TA_CENTER,
    )

    start_text = (
        filters.start_date.strftime("%d/%m/%Y")
        if filters.start_date
        else "Sin límite"
    )

    end_text = (
        filters.end_date.strftime("%d/%m/%Y")
        if filters.end_date
        else "Sin límite"
    )

    status_text = {
        "ALL": "Todos",
        "ACTIVE": "Activos",
        "INACTIVE": "Inactivos",
    }[filters.status]

    story = [
        Paragraph(
            "Reporte de vehículos",
            title_style,
        ),
        Paragraph(
            f"<b>Período:</b> {start_text} - {end_text}",
            info_style,
        ),
        Paragraph(
            f"<b>Estado:</b> {status_text}",
            info_style,
        ),
        Paragraph(
            f"<b>Total de vehículos:</b> {len(rows)}",
            info_style,
        ),
        Spacer(1, 8),
    ]

    table_data = [
        [
            Paragraph(header, header_style)
            for header in VEHICLE_REPORT_HEADERS
        ]
    ]

    for row in rows:
        values = [
            row.inventory_code,
            row.license_plate,
            row.brand,
            row.model,
            str(row.year),
            row.vehicle_type,
            row.fuel_type,
            f"{row.current_odometer_km:,.1f}",
            (
                f"{row.tank_capacity_gal:,.3f}"
                if row.tank_capacity_gal is not None
                else "-"
            ),
            row.status,
            row.created_at.strftime(
                "%d/%m/%Y %H:%M"
            ),
        ]

        table_data.append(
            [
                Paragraph(
                    str(value),
                    cell_style,
                )
                for value in values
            ]
        )

    column_widths = [
        27 * mm,
        19 * mm,
        21 * mm,
        23 * mm,
        12 * mm,
        26 * mm,
        23 * mm,
        25 * mm,
        22 * mm,
        18 * mm,
        29 * mm,
    ]

    table = Table(
        table_data,
        colWidths=column_widths,
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
            ]
        )
    )

    story.append(table)

    document.build(story)

    return output.getvalue()


COMMISSION_REPORT_HEADERS = [
    "Solicitante",
    "Vehículo / placa",
    "Estado",
    "Inicio programado",
    "Fin programado",
    "Revisado por",
    "Fecha de revisión",
    "Fecha de creación",
]


def build_commissions_pdf(
    *,
    rows: list[CommissionReportRow],
    filters: CommissionReportFilters,
) -> bytes:
    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title="Reporte de comisiones",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CommissionReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=19,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    info_style = ParagraphStyle(
        "CommissionReportInfo",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
    )

    header_style = ParagraphStyle(
        "CommissionReportHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=8,
        alignment=TA_CENTER,
    )

    cell_style = ParagraphStyle(
        "CommissionReportCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=8,
        alignment=TA_CENTER,
    )

    start_text = (
        filters.start_date.strftime("%d/%m/%Y")
        if filters.start_date
        else "Sin límite"
    )

    end_text = (
        filters.end_date.strftime("%d/%m/%Y")
        if filters.end_date
        else "Sin límite"
    )

    story = [
        Paragraph(
            "Reporte de comisiones",
            title_style,
        ),
        Paragraph(
            f"<b>Período:</b> {start_text} - {end_text}",
            info_style,
        ),
        Paragraph(
            f"<b>Total de comisiones:</b> {len(rows)}",
            info_style,
        ),
        Spacer(1, 8),
    ]

    table_data = [
        [
            Paragraph(header, header_style)
            for header in COMMISSION_REPORT_HEADERS
        ]
    ]

    for row in rows:
        values = [
            row.requester_name,
            row.vehicle,
            row.status,
            row.scheduled_start_at.strftime(
                "%d/%m/%Y %H:%M"
            ),
            row.scheduled_end_at.strftime(
                "%d/%m/%Y %H:%M"
            ),
            row.reviewer_name or "-",
            (
                row.reviewed_at.strftime(
                    "%d/%m/%Y %H:%M"
                )
                if row.reviewed_at is not None
                else "-"
            ),
            row.created_at.strftime(
                "%d/%m/%Y %H:%M"
            ),
        ]

        table_data.append(
            [
                Paragraph(
                    str(value),
                    cell_style,
                )
                for value in values
            ]
        )

    column_widths = [
        31 * mm,
        36 * mm,
        20 * mm,
        31 * mm,
        31 * mm,
        29 * mm,
        31 * mm,
        31 * mm,
    ]

    table = Table(
        table_data,
        colWidths=column_widths,
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
            ]
        )
    )

    story.append(table)

    document.build(story)

    return output.getvalue()



TRIP_REPORT_HEADERS = [
    "Fecha",
    "Vehículo / placa",
    "Piloto",
    "No.",
    "Origen",
    "Destino",
    "Odómetro inicial",
    "Odómetro final",
    "Km recorridos",
    "Tanque (%)",
    "Carretera",
]


def build_trips_pdf(
    *,
    rows: list[TripReportRow],
    filters: TripReportFilters,
) -> bytes:
    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        rightMargin=8 * mm,
        leftMargin=8 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
        title="Reporte de recorridos y kilómetros",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TripReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        alignment=TA_CENTER,
        spaceAfter=7,
    )

    info_style = ParagraphStyle(
        "TripReportInfo",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
    )

    header_style = ParagraphStyle(
        "TripReportHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=6.5,
        leading=7.5,
        alignment=TA_CENTER,
    )

    cell_style = ParagraphStyle(
        "TripReportCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=6.5,
        leading=7.5,
        alignment=TA_CENTER,
    )

    start_text = (
        filters.start_date.strftime("%d/%m/%Y")
        if filters.start_date
        else "Sin límite"
    )

    end_text = (
        filters.end_date.strftime("%d/%m/%Y")
        if filters.end_date
        else "Sin límite"
    )

    total_km = sum(
        (row.distance_km for row in rows),
        Decimal("0"),
    )

    story = [
        Paragraph(
            "Reporte de recorridos y kilómetros",
            title_style,
        ),
        Paragraph(
            f"<b>Período:</b> {start_text} - {end_text}",
            info_style,
        ),
        Paragraph(
            f"<b>Total de recorridos:</b> {len(rows)}",
            info_style,
        ),
        Paragraph(
            f"<b>Kilómetros recorridos:</b> {total_km} km",
            info_style,
        ),
        Spacer(1, 8),
    ]

    table_data = [
        [
            Paragraph(header, header_style)
            for header in TRIP_REPORT_HEADERS
        ]
    ]

    for row in rows:
        values = [
            row.trip_date.strftime("%d/%m/%Y"),
            row.vehicle,
            row.driver_name,
            row.sequence_number,
            row.origin,
            row.destination,
            f"{row.odometer_start_km:.1f}",
            f"{row.odometer_end_km:.1f}",
            f"{row.distance_km:.1f}",
            (
                f"{row.tank_balance_percent:.2f}"
                if row.tank_balance_percent is not None
                else "-"
            ),
            row.road_type,
        ]

        table_data.append(
            [
                Paragraph(
                    str(value),
                    cell_style,
                )
                for value in values
            ]
        )

    column_widths = [
        18 * mm,
        30 * mm,
        24 * mm,
        12 * mm,
        23 * mm,
        23 * mm,
        21 * mm,
        21 * mm,
        19 * mm,
        18 * mm,
        20 * mm,
    ]

    table = Table(
        table_data,
        colWidths=column_widths,
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
            ]
        )
    )

    story.append(table)
    document.build(story)

    return output.getvalue()


FUEL_REPORT_HEADERS = [
    "Fecha y hora de carga",
    "Solicitante",
    "Vehículo / placa",
    "Gasolinera",
    "Galones",
    "Monto (Q)",
]


def build_fuel_pdf(
    *,
    rows: list[FuelReportRow],
    filters: FuelReportFilters,
) -> bytes:
    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title="Reporte de combustible",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "FuelReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=19,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    info_style = ParagraphStyle(
        "FuelReportInfo",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
    )

    header_style = ParagraphStyle(
        "FuelReportHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=9,
        alignment=TA_CENTER,
    )

    cell_style = ParagraphStyle(
        "FuelReportCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=9,
        alignment=TA_CENTER,
    )

    start_text = (
        filters.start_date.strftime("%d/%m/%Y")
        if filters.start_date
        else "Sin límite"
    )

    end_text = (
        filters.end_date.strftime("%d/%m/%Y")
        if filters.end_date
        else "Sin límite"
    )

    story = [
        Paragraph(
            "Reporte de combustible",
            title_style,
        ),
        Paragraph(
            f"<b>Período:</b> {start_text} - {end_text}",
            info_style,
        ),
        Paragraph(
            f"<b>Total de cargas:</b> {len(rows)}",
            info_style,
        ),
        Spacer(1, 8),
    ]

    table_data = [
        [
            Paragraph(header, header_style)
            for header in FUEL_REPORT_HEADERS
        ]
    ]

    for row in rows:
        values = [
            row.loaded_at.strftime(
                "%d/%m/%Y %H:%M"
            ),
            row.requester_name,
            row.vehicle,
            row.gas_station,
            f"{row.gallons:.3f}",
            f"Q {row.amount_q:.2f}",
        ]

        table_data.append(
            [
                Paragraph(
                    str(value),
                    cell_style,
                )
                for value in values
            ]
        )

    column_widths = [
        38 * mm,
        42 * mm,
        48 * mm,
        48 * mm,
        28 * mm,
        30 * mm,
    ]

    table = Table(
        table_data,
        colWidths=column_widths,
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    story.append(table)

    document.build(story)

    return output.getvalue()



MAINTENANCE_REPORT_HEADERS = [
    "Fecha",
    "Vehículo / placa",
    "Tipo",
    "Odómetro",
    "Taller",
    "Costo",
    "Factura",
    "Descripción",
    "Servicios",
    "Repuestos",
    "Próx. fecha",
    "Próx. km",
]


def build_maintenance_pdf(
    *,
    rows: list[MaintenanceReportRow],
    filters: MaintenanceReportFilters,
) -> bytes:
    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        rightMargin=8 * mm,
        leftMargin=8 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
        title="Reporte de mantenimiento",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "MaintenanceReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        alignment=TA_CENTER,
        spaceAfter=7,
    )

    info_style = ParagraphStyle(
        "MaintenanceReportInfo",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
    )

    header_style = ParagraphStyle(
        "MaintenanceReportHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=6,
        leading=7,
        alignment=TA_CENTER,
    )

    cell_style = ParagraphStyle(
        "MaintenanceReportCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=6,
        leading=7,
        alignment=TA_CENTER,
    )

    start_text = (
        filters.start_date.strftime("%d/%m/%Y")
        if filters.start_date
        else "Sin límite"
    )

    end_text = (
        filters.end_date.strftime("%d/%m/%Y")
        if filters.end_date
        else "Sin límite"
    )

    story = [
        Paragraph(
            "Reporte de mantenimiento",
            title_style,
        ),
        Paragraph(
            f"<b>Período:</b> {start_text} - {end_text}",
            info_style,
        ),
        Paragraph(
            f"<b>Total de mantenimientos:</b> {len(rows)}",
            info_style,
        ),
        Spacer(1, 8),
    ]

    table_data = [
        [
            Paragraph(header, header_style)
            for header in MAINTENANCE_REPORT_HEADERS
        ]
    ]

    for row in rows:
        values = [
            row.maintenance_date.strftime("%d/%m/%Y"),
            row.vehicle,
            row.maintenance_type,
            (
                f"{row.odometer_km:.1f} km"
                if row.odometer_km is not None
                else "-"
            ),
            row.workshop or "-",
            (
                f"Q {row.cost_q:.2f}"
                if row.cost_q is not None
                else "-"
            ),
            row.invoice_number or "-",
            row.description or "-",
            row.services,
            row.parts,
            (
                row.next_maintenance_date.strftime(
                    "%d/%m/%Y"
                )
                if row.next_maintenance_date is not None
                else "-"
            ),
            (
                f"{row.next_maintenance_odometer_km:.1f} km"
                if (
                    row.next_maintenance_odometer_km
                    is not None
                )
                else "-"
            ),
        ]

        table_data.append(
            [
                Paragraph(
                    str(value),
                    cell_style,
                )
                for value in values
            ]
        )

    column_widths = [
        17 * mm,
        26 * mm,
        17 * mm,
        19 * mm,
        24 * mm,
        17 * mm,
        19 * mm,
        30 * mm,
        30 * mm,
        30 * mm,
        20 * mm,
        20 * mm,
    ]

    table = Table(
        table_data,
        colWidths=column_widths,
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
            ]
        )
    )

    story.append(table)

    document.build(story)

    return output.getvalue()
