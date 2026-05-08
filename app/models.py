from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    username        = Column(String(50),  unique=True, index=True, nullable=False)
    email           = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    calculations = relationship(
        "Calculation", back_populates="owner", cascade="all, delete-orphan"
    )


class Calculation(Base):
    __tablename__ = "calculations"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    operand_a  = Column(Float, nullable=False)
    operand_b  = Column(Float, nullable=False)
    operation  = Column(String(20), nullable=False)
    result     = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="calculations")
