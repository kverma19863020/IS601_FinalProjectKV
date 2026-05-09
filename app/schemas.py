"""
Pydantic schemas for Calculation World.
Handles request validation and response serialization (CLO12).
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for registering a new user."""
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    """Schema for returning user data (excludes password)."""
    id: int
    username: str
    email: str
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CalculationCreate(BaseModel):
    """Schema for saving a new calculation to the database."""
    user_id: int
    operand_a: float
    operand_b: float
    operation: str
    result: float


class CalculationIn(BaseModel):
    """Schema for the REST API POST /api/calculate request body."""
    operand_a: float
    operand_b: float
    operation: str


class CalculationOut(BaseModel):
    """Schema for returning a calculation from the API."""
    id: int
    user_id: int
    operand_a: float
    operand_b: float
    operation: str
    result: float
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CalculationUpdate(BaseModel):
    """Schema for editing an existing calculation."""
    operand_a: float
    operand_b: float
    operation: str
