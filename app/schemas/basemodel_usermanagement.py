# app/schemas/user.py

from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Literal


class UserCreate(BaseModel):
    line_user_id: str
    full_name: str
    phone: str | None = None
    email: str | None = None

class UserResponse(BaseModel):
    user_id: int
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

# เลขที่บ้าน
class HouseResponse(BaseModel):
    house_id: int
    user_id: int
    house_no: str
    address: str | None = None
    status: Literal["ACTIVE", "INACTIVE"]
    created_at: datetime
    updated_at: datetime