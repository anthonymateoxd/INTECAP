from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.modules.users.schemas import RoleResponse, UserResponse
from app.modules.users import service




from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    RoleNotFoundError,
)
from app.modules.auth.dependencies import require_administration
from app.modules.users.model import User
from app.modules.users.schemas import (
    RoleResponse,
    UserCreate,
    UserResponse,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/roles",
    response_model=list[RoleResponse],
)
def get_roles(
    db: Session = Depends(get_db),
):
    return service.list_roles(db)


@router.get(
    "",
    response_model=list[UserResponse],
)
def get_users(
    db: Session = Depends(get_db),
):
    return service.list_users(db)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_administration),
):
    try:
        return service.create_user(
            db,
            user_data,
        )

    except RoleNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado.",
        ) from None

    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese correo institucional.",
        ) from None

@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = service.get_user(
        db,
        user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )

    return user