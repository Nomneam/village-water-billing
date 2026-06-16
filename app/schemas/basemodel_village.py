from pydantic import BaseModel
from typing import Optional

class VillageCreate(BaseModel):
    village_name: str

class VillageUpdate(BaseModel):
    village_name: Optional[str] = None

class PasswordConfirm(BaseModel):
    password: str