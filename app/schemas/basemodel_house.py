from pydantic import BaseModel
from typing import Optional, Literal

# เพิ่มข้อมูลบ้านใหม่
class HouseCreate(BaseModel):
    village_id: int
    user_id: int
    house_no: str
    address: str
    status: Literal["ACTIVE", "INACTIVE"] = "ACTIVE"

# อัปเดตเฉพาะ user_id กับ status ได้
class HouseUpdate(BaseModel):
    user_id: Optional[int] = None
    status: Optional[Literal["ACTIVE", "INACTIVE"]] = None