from sqlalchemy.orm import Session

from app.core.exceptions import InvalidCredentialsError
from app.core.security import (
    create_access_token,
    verify_password,
)
from app.modules.auth.schemas import (
    LoginRequest,
    TokenResponse,
)
from app.modules.users.repository import get_user_by_email


def authenticate_user(
    db: Session,
    credentials: LoginRequest,
) -> TokenResponse:
    user = get_user_by_email(
        db,
        str(credentials.institutional_email),
    )

    if user is None:
        raise InvalidCredentialsError()

    if not verify_password(
        credentials.password.get_secret_value(),
        user.password_hash,
    ):
        raise InvalidCredentialsError()

    access_token = create_access_token(
        subject=str(user.id),
    )

    return TokenResponse(
        access_token=access_token,
    )