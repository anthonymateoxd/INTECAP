from getpass import getpass
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.database.session import SessionLocal
from app.main import app
from app.modules.maintenance.models import (
    MaintenanceEvent,
    MaintenancePart,
    ServiceType,
    maintenance_event_services,
)


ADMIN_DEFAULT = "grabriel1@miumg.edu.gt"
COLLAB_DEFAULT = "prueba@intecap.edu.gt"

admin_email = input(
    f"Email ADMIN [{ADMIN_DEFAULT}]: "
).strip() or ADMIN_DEFAULT
admin_password = getpass("Password ADMIN: ")

collab_email = input(
    f"Email COLLABORATOR [{COLLAB_DEFAULT}]: "
).strip() or COLLAB_DEFAULT
collab_password = getpass("Password COLLABORATOR: ")

suffix = uuid4().hex[:8]

service1_id = None
service2_id = None
event_id = None


def login(client, email, password, label):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "institutional_email": email,
            "password": password,
        },
    )

    print(f"LOGIN {label}:", response.status_code)

    if response.status_code != 200:
        print(response.json())
        raise RuntimeError(f"Login {label} falló.")

    return response.json()["access_token"]


try:
    with TestClient(app) as client:
        admin_token = login(
            client,
            admin_email,
            admin_password,
            "ADMIN",
        )

        collab_token = login(
            client,
            collab_email,
            collab_password,
            "COLLABORATOR",
        )

        admin_headers = {
            "Authorization": f"Bearer {admin_token}",
        }

        collab_headers = {
            "Authorization": f"Bearer {collab_token}",
        }

        # Servicio inicial.
        response = client.post(
            "/api/v1/maintenance/service-types",
            headers=admin_headers,
            json={
                "name": f"Aceite PATCH {suffix}",
                "interval_km": 5000.0,
                "interval_days": 180,
            },
        )

        print("CREATE SERVICE 1:", response.status_code)
        service1_id = response.json()["id"]

        # Servicio que utilizaremos después de editar.
        response = client.post(
            "/api/v1/maintenance/service-types",
            headers=admin_headers,
            json={
                "name": f"Frenos PATCH {suffix}",
                "interval_km": 20000.0,
                "interval_days": 365,
            },
        )

        print("CREATE SERVICE 2:", response.status_code)
        service2_id = response.json()["id"]

        # Crear mantenimiento inicial.
        response = client.post(
            "/api/v1/maintenance/events",
            headers=admin_headers,
            json={
                "vehicle_id": 19,
                "maintenance_type": "PREVENTIVO",
                "maintenance_date": "2026-08-14",
                "odometer_km": 10000.0,
                "workshop": "Taller original HTTP",
                "cost_q": 500.00,
                "description": "Evento para probar PATCH y DELETE",
                "service_type_ids": [
                    service1_id,
                ],
                "parts": [
                    {
                        "part_name": "Filtro original",
                        "quantity": 1,
                    },
                ],
            },
        )

        print("CREATE EVENT:", response.status_code)

        if response.status_code != 201:
            print(response.json())
            raise RuntimeError(
                "No fue posible crear el mantenimiento."
            )

        event_id = response.json()["id"]

        print(
            "INITIAL NEXT:",
            response.json()["next_maintenance_date"],
            response.json()["next_maintenance_odometer_km"],
        )

        # Colaborador no puede editar.
        response = client.patch(
            f"/api/v1/maintenance/events/{event_id}",
            headers=collab_headers,
            json={
                "workshop": "Intento colaborador",
            },
        )

        print(
            "PATCH COLLABORATOR:",
            response.status_code,
        )

        # Administración cambia fecha, km, servicio y piezas.
        response = client.patch(
            f"/api/v1/maintenance/events/{event_id}",
            headers=admin_headers,
            json={
                "maintenance_date": "2026-09-01",
                "odometer_km": 12000.0,
                "workshop": "Taller actualizado HTTP",
                "cost_q": 1200.00,
                "service_type_ids": [
                    service2_id,
                ],
                "parts": [
                    {
                        "part_name": "Pastillas de freno",
                        "quantity": 2,
                    },
                    {
                        "part_name": "Liquido de frenos",
                        "quantity": 1,
                    },
                ],
            },
        )

        print("PATCH ADMIN:", response.status_code)

        if response.status_code == 200:
            data = response.json()

            print(
                "RECALCULATED NEXT:",
                data["next_maintenance_date"],
                data["next_maintenance_odometer_km"],
            )

            print(
                "UPDATED SERVICES:",
                [x["name"] for x in data["services"]],
            )

            print(
                "UPDATED PARTS:",
                [
                    (x["part_name"], x["quantity"])
                    for x in data["parts"]
                ],
            )
        else:
            print(response.json())

        # Sobrescritura manual del próximo mantenimiento.
        response = client.patch(
            f"/api/v1/maintenance/events/{event_id}",
            headers=admin_headers,
            json={
                "next_maintenance_date": "2027-03-01",
                "next_maintenance_odometer_km": 18000.0,
            },
        )

        print(
            "PATCH MANUAL NEXT:",
            response.status_code,
        )

        if response.status_code == 200:
            print(
                "MANUAL NEXT:",
                response.json()["next_maintenance_date"],
                response.json()["next_maintenance_odometer_km"],
            )

        # Colaborador no puede eliminar.
        response = client.delete(
            f"/api/v1/maintenance/events/{event_id}",
            headers=collab_headers,
        )

        print(
            "DELETE COLLABORATOR:",
            response.status_code,
        )

        # Administración elimina lógicamente.
        response = client.delete(
            f"/api/v1/maintenance/events/{event_id}",
            headers=admin_headers,
        )

        print(
            "DELETE ADMIN:",
            response.status_code,
        )

        # Ya no debe aparecer en historial normal.
        response = client.get(
            "/api/v1/maintenance/vehicles/19/history",
            headers=admin_headers,
        )

        print(
            "HISTORY ADMIN AFTER DELETE:",
            response.status_code,
            [x["id"] for x in response.json()]
            if response.status_code == 200
            else response.text,
        )

        response = client.get(
            "/api/v1/maintenance/vehicles/19/history",
            headers=collab_headers,
        )

        print(
            "HISTORY COLLAB AFTER DELETE:",
            response.status_code,
            [x["id"] for x in response.json()]
            if response.status_code == 200
            else response.text,
        )

        # Segundo intento de eliminación.
        response = client.delete(
            f"/api/v1/maintenance/events/{event_id}",
            headers=admin_headers,
        )

        print(
            "DELETE SECOND ATTEMPT:",
            response.status_code,
        )

finally:
    db = SessionLocal()

    try:
        if event_id is not None:
            db.execute(
                delete(
                    maintenance_event_services
                ).where(
                    maintenance_event_services.c.maintenance_event_id
                    == event_id
                )
            )

            db.execute(
                delete(MaintenancePart).where(
                    MaintenancePart.maintenance_event_id
                    == event_id
                )
            )

            db.execute(
                delete(MaintenanceEvent).where(
                    MaintenanceEvent.id == event_id
                )
            )

        ids = [
            value
            for value in (
                service1_id,
                service2_id,
            )
            if value is not None
        ]

        if ids:
            db.execute(
                delete(ServiceType).where(
                    ServiceType.id.in_(ids)
                )
            )

        db.commit()

        print(
            "CLEANUP PATCH DELETE HTTP: OK"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
