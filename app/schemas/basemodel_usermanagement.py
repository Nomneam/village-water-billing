# app/schemas/user.py

from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# เพิ่มข้อมูลผู้ใช้งานใหม่
class UserCreate(BaseModel):
    citizen_id: str = Field(..., min_length=13, max_length=13)
    line_user_id: str | None = None
    full_name: str
    phone: str | None = None
    email: EmailStr | None = None

    @field_validator("citizen_id")
    @classmethod
    def validate_citizen_id(cls, value: str):
        if not value.isdigit():
            raise ValueError("Citizen ID must contain only digits")

        if len(value) != 13:
            raise ValueError("Citizen ID must be 13 digits")

        return value
# แก้ไขข้อมูลผู้ใช้งาน
class UserUpdate(BaseModel):
    citizen_id: Optional[str] = None
    line_user_id: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

    @field_validator("citizen_id")
    @classmethod
    def validate_citizen_id(cls, value: Optional[str]):
        if value is None:
            return value
        if not value.isdigit():
            raise ValueError(
                "Citizen ID must contain only digits"
            )
        if len(value) != 13:
            raise ValueError(
                "Citizen ID must be 13 digits"
            )
        return value


class UserResponse(BaseModel):
    user_id: int
    citizen_id: str | None = None
    line_user_id: str | None = None
    full_name: str
    phone: str | None = None
    email: str | None = None


class UserListResponse(BaseModel):
    users: list[UserResponse]

class UserPaginationResponse(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    users: list[UserResponse]

