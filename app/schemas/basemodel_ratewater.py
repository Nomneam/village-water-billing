from pydantic import BaseModel
from decimal import Decimal
from datetime import date

class WaterRateItem(BaseModel):
    min_unit: int
    max_unit: int
    price_per_unit: Decimal

class WaterRateVersionCreate(BaseModel):
    effective_from: date
    rates: list[WaterRateItem]