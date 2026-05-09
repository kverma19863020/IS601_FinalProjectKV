"""
CRUD operations for Calculation World (CLO11).
Implements full BREAD: Browse, Read, Edit, Add, Delete for calculations.
All database interactions are encapsulated here — routes stay thin.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas, auth


def get_user_by_username(db: Session, username: str):
    """Fetch a user by their username. Returns None if not found."""
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    """Fetch a user by their email address. Returns None if not found."""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, data: schemas.UserCreate):
    """
    Create a new user account.
    Password is hashed with bcrypt before storage — never stored in plain text.
    """
    user = models.User(
        username=data.username,
        email=data.email,
        hashed_password=auth.hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str):
    """
    Verify username and password.
    Returns the User object on success, None on failure.
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not auth.verify_password(password, user.hashed_password):
        return None
    return user


def update_email(db: Session, user: models.User, new_email: str):
    """Update a user's email address."""
    user.email = new_email
    db.commit()
    db.refresh(user)
    return user


def update_password(db: Session, user: models.User, new_password: str):
    """Hash and update a user's password."""
    user.hashed_password = auth.hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user


def create_calculation(db: Session, data: schemas.CalculationCreate):
    """ADD — Save a new calculation result to the database."""
    calc = models.Calculation(**data.model_dump())
    db.add(calc)
    db.commit()
    db.refresh(calc)
    return calc


def get_history(db: Session, user_id: int, limit: int = 500):
    """BROWSE — Return all calculations for a user, newest first."""
    return (
        db.query(models.Calculation)
        .filter(models.Calculation.user_id == user_id)
        .order_by(models.Calculation.created_at.desc())
        .limit(limit)
        .all()
    )


def get_calculation_by_id(db: Session, calc_id: int, user_id: int):
    """READ — Fetch a single calculation by ID, scoped to user."""
    return (
        db.query(models.Calculation)
        .filter(
            models.Calculation.id == calc_id,
            models.Calculation.user_id == user_id,
        )
        .first()
    )


def update_calculation(
    db: Session,
    calc: models.Calculation,
    operand_a: float,
    operand_b: float,
    operation: str,
    result: float,
):
    """EDIT — Update an existing calculation with new values and recalculated result."""
    calc.operand_a = operand_a
    calc.operand_b = operand_b
    calc.operation = operation
    calc.result    = result
    db.commit()
    db.refresh(calc)
    return calc


def delete_calculation(db: Session, calc: models.Calculation):
    """DELETE — Permanently remove a calculation from the database."""
    db.delete(calc)
    db.commit()


def get_stats(db: Session, user_id: int) -> dict:
    """Return aggregate statistics for a user's calculation history."""
    total = (
        db.query(func.count(models.Calculation.id))
        .filter(models.Calculation.user_id == user_id)
        .scalar() or 0
    )
    avg = (
        db.query(func.avg(models.Calculation.result))
        .filter(models.Calculation.user_id == user_id)
        .scalar()
    )
    most_used = (
        db.query(
            models.Calculation.operation,
            func.count(models.Calculation.operation).label("cnt"),
        )
        .filter(models.Calculation.user_id == user_id)
        .group_by(models.Calculation.operation)
        .order_by(func.count(models.Calculation.operation).desc())
        .first()
    )
    return {
        "total":        total,
        "avg_result":   round(avg, 4) if avg is not None else None,
        "most_used_op": most_used[0] if most_used else None,
    }
