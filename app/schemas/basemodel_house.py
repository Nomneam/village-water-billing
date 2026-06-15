from pydantic import BaseModel
from typing import Optional, Literal


class HouseCreate(BaseModel):
    user_id: Optional[int] = None
    house_no: str
    meter_number: str
    address: str
    status: Literal["ACTIVE", "INACTIVE"] = "ACTIVE"