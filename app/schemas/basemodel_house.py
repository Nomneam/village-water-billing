from pydantic import BaseModel
from typing import Optional, Literal


class HouseCreate(BaseModel):
    village_id: int
    user_id: int
    house_no: str
    address: str
    status: Literal["ACTIVE", "INACTIVE"] = "ACTIVE"