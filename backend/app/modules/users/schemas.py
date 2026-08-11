from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
)

from pydantic import BaseModel, ConfigDict


class RoleResponse(BaseModel):
    id: int
    code: str
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    role_id: int
    full_name: str
    institutional_email: str
    position: str
    area_department: str
    phone: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
class UserCreate(BaseModel):
    role_id: int

    full_name: str = Field(
        max_length=150,
    )

    institutional_email: EmailStr

    password: SecretStr

    position: str = Field(
        max_length=100,
    )

    area_department: str = Field(
        max_length=150,
    )

    phone: str = Field(
        max_length=30,
    )