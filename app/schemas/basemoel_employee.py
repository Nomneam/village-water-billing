from pydantic import BaseModel, EmailStr
from typing import Optional


class EmployeeCreateRequest(BaseModel):
    username: str
    password: str   
    full_name: str
    role: Optional[str] = "STAFF"

    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    profile_image: Optional[str] = None