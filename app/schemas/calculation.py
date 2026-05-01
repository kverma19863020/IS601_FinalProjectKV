from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

VALID_OPERATIONS = {"add", "subtract", "multiply", "divide"}

class CalculationBase(BaseModel):
    operation: str
    operand1: float
    operand2: float

    @field_validator("operation")
    @classmethod
    def validate_operation(cls, v):
        if v not in VALID_OPERATIONS:
            raise ValueError(f"operation must be one of {VALID_OPERATIONS}")
        return v

    @field_validator("operand2")
    @classmethod
    def no_divide_by_zero(cls, v, info):
        if info.data.get("operation") == "divide" and v == 0:
            raise ValueError("Cannot divide by zero")
        return v

class CalculationCreate(CalculationBase):
    pass

class CalculationUpdate(BaseModel):
    operation: Optional[str] = None
    operand1: Optional[float] = None
    operand2: Optional[float] = None

    @field_validator("operation")
    @classmethod
    def validate_operation(cls, v):
        if v is not None and v not in VALID_OPERATIONS:
            raise ValueError(f"operation must be one of {VALID_OPERATIONS}")
        return v

class CalculationResponse(CalculationBase):
    id: int
    result: float
    owner_id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
