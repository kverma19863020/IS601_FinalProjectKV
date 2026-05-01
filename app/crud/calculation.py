from sqlalchemy.orm import Session
from app.models.calculation import Calculation
from app.schemas.calculation import CalculationCreate, CalculationUpdate

def compute(operation: str, a: float, b: float) -> float:
    if operation == "add":        return a + b
    if operation == "subtract":   return a - b
    if operation == "multiply":   return a * b
    if operation == "divide":     return a / b
    raise ValueError("Invalid operation")

def get_calculations(db: Session, user_id: int):
    return db.query(Calculation).filter(Calculation.owner_id == user_id).all()

def get_calculation(db: Session, calc_id: int, user_id: int):
    return db.query(Calculation).filter(
        Calculation.id == calc_id,
        Calculation.owner_id == user_id
    ).first()

def create_calculation(db: Session, data: CalculationCreate, user_id: int):
    result = compute(data.operation, data.operand1, data.operand2)
    calc = Calculation(**data.model_dump(), result=result, owner_id=user_id)
    db.add(calc)
    db.commit()
    db.refresh(calc)
    return calc

def update_calculation(db: Session, calc_id: int, data: CalculationUpdate, user_id: int):
    calc = get_calculation(db, calc_id, user_id)
    if not calc:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(calc, k, v)
    # recompute result
    calc.result = compute(calc.operation, calc.operand1, calc.operand2)
    db.commit()
    db.refresh(calc)
    return calc

def delete_calculation(db: Session, calc_id: int, user_id: int):
    calc = get_calculation(db, calc_id, user_id)
    if not calc:
        return False
    db.delete(calc)
    db.commit()
    return True
