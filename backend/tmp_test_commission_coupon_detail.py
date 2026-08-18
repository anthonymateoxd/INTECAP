from getpass import getpass
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.database.session import SessionLocal
from app.modules.fuel.model import (
    FuelCoupon,
    CommissionCoupon,
)


ADMIN_EMAIL = "grabriel1@miumg.edu.gt"
OWNER_EMAIL = "prueba@intecap.edu.gt"

COMMISSION_ID = 2
FOREIGN_COMMISSION_ID = 5

client = TestClient(app)

admin_password = getpass("Password ADMINISTRATION: ")
owner_password = getpass("Password COLLABORATOR propietario: ")

coupon_id = None

try:
    # LOGIN ADMIN
    admin_login = client.post(
        "/api/v1/auth/login",
        json={
            "institutional_email": ADMIN_EMAIL,
            "password": admin_password,
        },
    )

    print("ADMIN login:", admin_login.status_code)

    if admin_login.status_code != 200:
        raise SystemExit("Login ADMIN incorrecto.")

    admin_headers = {
        "Authorization": (
            f"Bearer {admin_login.json()['access_token']}"
        )
    }

    # LOGIN PROPIETARIO
    owner_login = client.post(
        "/api/v1/auth/login",
        json={
            "institutional_email": OWNER_EMAIL,
            "password": owner_password,
        },
    )

    print("PROPIETARIO login:", owner_login.status_code)

    if owner_login.status_code != 200:
        raise SystemExit("Login PROPIETARIO incorrecto.")

    owner_headers = {
        "Authorization": (
            f"Bearer {owner_login.json()['access_token']}"
        )
    }

    # CREAR CUPÓN TEMPORAL
    coupon_response = client.post(
        "/api/v1/fuel/coupons",
        headers=admin_headers,
        json={
            "coupon_number": (
                f"DETAIL-API-{uuid4().hex[:8].upper()}"
            )
        },
    )

    print(
        "Crear cupón:",
        coupon_response.status_code,
    )

    coupon_id = coupon_response.json()["id"]

    # ASIGNAR A COMISIÓN 2
    assignment_response = client.post(
        f"/api/v1/fuel/commissions/"
        f"{COMMISSION_ID}/coupons",
        headers=admin_headers,
        json={
            "coupon_id": coupon_id,
        },
    )

    print(
        "Asignar cupón:",
        assignment_response.status_code,
    )

    assignment_id = assignment_response.json()["id"]

    # ADMIN CONSULTA DETALLE
    admin_detail = client.get(
        f"/api/v1/fuel/commissions/"
        f"{COMMISSION_ID}/coupons/"
        f"{assignment_id}",
        headers=admin_headers,
    )

    print(
        "ADMIN detalle:",
        admin_detail.status_code,
    )

    # PROPIETARIO CONSULTA DETALLE
    owner_detail = client.get(
        f"/api/v1/fuel/commissions/"
        f"{COMMISSION_ID}/coupons/"
        f"{assignment_id}",
        headers=owner_headers,
    )

    print(
        "PROPIETARIO detalle:",
        owner_detail.status_code,
    )

    # PROPIETARIO INTENTA CONSULTARLO DESDE COMISIÓN AJENA
    foreign_detail = client.get(
        f"/api/v1/fuel/commissions/"
        f"{FOREIGN_COMMISSION_ID}/coupons/"
        f"{assignment_id}",
        headers=owner_headers,
    )

    print(
        "PROPIETARIO comisión ajena:",
        foreign_detail.status_code,
    )

    # ASIGNACIÓN INEXISTENTE EN SU PROPIA COMISIÓN
    nonexistent_detail = client.get(
        f"/api/v1/fuel/commissions/"
        f"{COMMISSION_ID}/coupons/999999",
        headers=owner_headers,
    )

    print(
        "Asignación inexistente:",
        nonexistent_detail.status_code,
    )

finally:
    db = SessionLocal()

    try:
        if coupon_id is not None:
            db.query(CommissionCoupon).filter(
                CommissionCoupon.coupon_id == coupon_id
            ).delete(
                synchronize_session=False,
            )

            db.query(FuelCoupon).filter(
                FuelCoupon.id == coupon_id
            ).delete(
                synchronize_session=False,
            )

            db.commit()

    finally:
        db.close()

    print("Limpieza terminada.")
