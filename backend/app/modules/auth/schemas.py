from pydantic import BaseModel, EmailStr, SecretStr


class LoginRequest(BaseModel):
    institutional_email: EmailStr
    password: SecretStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"