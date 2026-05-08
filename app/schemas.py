from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CalculationCreate(BaseModel):
    user_id: int
    operand_a: float
    operand_b: float
    operation: str
    result: float


class CalculationIn(BaseModel):
    operand_a: float
    operand_b: float
    operation: str


class CalculationOut(BaseModel):
    id: int
    user_id: int
    operand_a: float
    operand_b: float
    operation: str
    result: float
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}
