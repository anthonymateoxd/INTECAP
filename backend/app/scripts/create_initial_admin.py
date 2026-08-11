from getpass import getpass

from pydantic import ValidationError

from app.core.constants import ROLE_ADMINISTRATION
from app.core.exceptions import EmailAlreadyRegisteredError
from app.database.session import SessionLocal
from app.modules.users.repository import get_role_by_code
from app.modules.users.schemas import UserCreate
from app.modules.users.service import create_user


def main() -> None:
    db = SessionLocal()

    try:
        admin_role = get_role_by_code(
            db,
            ROLE_ADMINISTRATION,
        )

        if admin_role is None:
            print(
                "ERROR: No existe el rol ADMINISTRATION "
                "en la base de datos."
            )
            return

        print("=== Creación del administrador inicial ===")

        full_name = input("Nombre completo: ").strip()
        institutional_email = input(
            "Correo institucional: "
        ).strip()
        password = getpass("Contraseña: ")
        position = input("Puesto: ").strip()
        area_department = input(
            "Área / departamento: "
        ).strip()
        phone = input("Teléfono: ").strip()

        user_data = UserCreate(
            role_id=admin_role.id,
            full_name=full_name,
            institutional_email=institutional_email,
            password=password,
            position=position,
            area_department=area_department,
            phone=phone,
        )

        user = create_user(
            db,
            user_data,
        )

        print()
        print("Administrador creado correctamente.")
        print(f"ID: {user.id}")
        print(f"Nombre: {user.full_name}")
        print(f"Correo: {user.institutional_email}")
        print(f"Rol: {admin_role.code}")

    except EmailAlreadyRegisteredError:
        print(
            "ERROR: Ya existe un usuario "
            "con ese correo institucional."
        )

    except ValidationError as exc:
        print("ERROR: Los datos ingresados no son válidos.")
        print(exc)

    except Exception as exc:
        print(f"ERROR inesperado: {exc}")

    finally:
        db.close()


if __name__ == "__main__":
    main()