from sqlalchemy.orm import Session

from app.modules.users.model import Role, User
from app.modules.users import repository


from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    RoleNotFoundError,
)
from app.core.security import hash_password
from app.modules.users.schemas import UserCreate

def list_roles(db: Session) -> list[Role]:
    return repository.get_roles(db)


def get_role(
    db: Session,
    role_id: int,
) -> Role | None:
    return repository.get_role_by_id(
        db,
        role_id,
    )


def list_users(db: Session) -> list[User]:
    return repository.get_users(db)


def get_user(
    db: Session,
    user_id: int,
) -> User | None:
    return repository.get_user_by_id(
        db,
        user_id,
    )


def get_user_by_email(
    db: Session,
    institutional_email: str,
) -> User | None:
    return repository.get_user_by_email(
        db,
        institutional_email,
    )
    
    
def create_user(
    db: Session,
    user_data: UserCreate,
) -> User:
    role = repository.get_role_by_id(
        db,
        user_data.role_id,
    )

    if role is None:
        raise RoleNotFoundError()

    existing_user = repository.get_user_by_email(
        db,
        str(user_data.institutional_email),
    )

    if existing_user is not None:
        raise EmailAlreadyRegisteredError()

    hashed_password = hash_password(
        user_data.password.get_secret_value()
    )

    try:
        user = repository.create_user(
            db,
            role_id=user_data.role_id,
            full_name=user_data.full_name,
            institutional_email=str(
                user_data.institutional_email
            ),
            password_hash=hashed_password,
            position=user_data.position,
            area_department=user_data.area_department,
            phone=user_data.phone,
        )

        db.commit()
        db.refresh(user)

        return user

    except Exception:
        db.rollback()
        raise