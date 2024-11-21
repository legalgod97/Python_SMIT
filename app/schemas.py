from pydantic import BaseModel, Field, validator
from datetime import date
from typing import Optional

class TariffSchema(BaseModel):
    cargo_type: str = Field(...)
    rate: float = Field(...)
    date: date = Field(...)

    @validator('rate')
    def rate_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Ставка должна быть положительной")
        return v


class InsuranceRequest(BaseModel):
    cargo_type: str = Field(...)
    declared_value: float = Field(..., gt=0) # Объявленная стоимость должна быть больше 0
    date: date = Field(...)

class InsuranceResponse(BaseModel):
    insurance_cost: float = Field(...)