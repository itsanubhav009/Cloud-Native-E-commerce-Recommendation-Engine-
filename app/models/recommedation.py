from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    score = Column(Float, nullable=False)  # Recommendation score/confidence
    algorithm = Column(String, nullable=False)  # Which algorithm generated this recommendation
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User")
    product = relationship("Product")