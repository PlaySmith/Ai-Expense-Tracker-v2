from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    merchant = Column(String(255), nullable=False)
    category = Column(String(100))
    date = Column(DateTime)
    description = Column(Text)
    receipt_image_path = Column(String(500))
    ocr_confidence = Column(Float)  # 0-1.0
    requires_review = Column(Boolean, default=False)
    extracted_raw = Column(Text)  # JSON-str for raw OCR data
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    

    owner_id = Column(Integer, nullable=True)  # Guest mode, no users table needed


