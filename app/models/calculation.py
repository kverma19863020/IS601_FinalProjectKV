from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Calculation(Base):
    __tablename__ = "calculations"
    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String, nullable=False)   # add, subtract, multiply, divide
    operand1 = Column(Float, nullable=False)
    operand2 = Column(Float, nullable=False)
    result = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="calculations")
