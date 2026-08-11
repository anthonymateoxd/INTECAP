from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.users.model import Role, User


def get_roles(db: Session) -> list[Role]:
    statement = select(Role).order_by(Role.id)

    return list(db.scalars(statement).all())


def get_role_by_id(
    db: Session,
    role_id: int,
) -> Role | None:
    statement = select(Role).where(Role.id == role_id)

    return db.scalars(statement).first()


def get_users(db: Session) -> list[User]:
    statement = select(User).order_by(User.id)

    return list(db.scalars(statement).all())


def get_user_by_id(
    db: Session,
    user_id: int,
) -> User | None:
    statement = select(User).where(User.id == user_id)

    return db.scalars(statement).first()


def get_user_by_email(
    db: Session,
    institutional_email: str,
) -> User | None:
    statement = select(User).where(
        func.lower(User.institutional_email)
        == institutional_email.lower()
    )

    return db.scalars(statement).first()

def create_user(
    db: Session,
    *,
    role_id: int,
    full_name: str,
    institutional_email: str,
    password_hash: str,
    position: str,
    area_department: str,
    phone: str,
) -> User:
    user = User(
        role_id=role_id,
        full_name=full_name,
        institutional_email=institutional_email,
        password_hash=password_hash,
        position=position,
        area_department=area_department,
        phone=phone,
    )

    db.add(user)
    db.flush()
    db.refresh(user)

    return user


def get_role_by_code(
    db: Session,
    code: str,
) -> Role | None:
    statement = select(Role).where(
        Role.code == code
    )

    return db.scalars(statement).first()