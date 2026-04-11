from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with expenses
    expenses = relationship("Expense", back_populates="owner", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(email='{self.email}')>"


class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    merchant = Column(String, index=True)
    category = Column(String, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    description = Column(String, nullable=True)
    receipt_image_path = Column(String, nullable=True)
    ocr_confidence = Column(Float, nullable=True)  # Store OCR confidence score
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key to user (optional for MVP)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship("User", back_populates="expenses")
    
    def __repr__(self):
        return f"<Expense(merchant='{self.merchant}', amount={self.amount})>"
    
    def to_dict(self):
        """Convert expense to dictionary"""
        return {
            "id": self.id,
            "amount": self.amount,
            "merchant": self.merchant,
            "category": self.category,
            "date": self.date.isoformat() if self.date else None,
            "description": self.description,
            "ocr_confidence": self.ocr_confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
