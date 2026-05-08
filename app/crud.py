from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas, auth


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, data: schemas.UserCreate):
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
    user = get_user_by_username(db, username)
    if not user or not auth.verify_password(password, user.hashed_password):
        return None
    return user


def update_email(db: Session, user: models.User, new_email: str):
    user.email = new_email
    db.commit()
    db.refresh(user)
    return user


def update_password(db: Session, user: models.User, new_password: str):
    user.hashed_password = auth.hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user


def create_calculation(db: Session, data: schemas.CalculationCreate):
    calc = models.Calculation(**data.model_dump())
    db.add(calc)
    db.commit()
    db.refresh(calc)
    return calc


def get_history(db: Session, user_id: int, limit: int = 500):
    return (
        db.query(models.Calculation)
        .filter(models.Calculation.user_id == user_id)
        .order_by(models.Calculation.created_at.desc())
        .limit(limit)
        .all()
    )


def get_stats(db: Session, user_id: int) -> dict:
    total = db.query(func.count(models.Calculation.id)).filter(
        models.Calculation.user_id == user_id
    ).scalar() or 0

    avg = db.query(func.avg(models.Calculation.result)).filter(
        models.Calculation.user_id == user_id
    ).scalar()

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
