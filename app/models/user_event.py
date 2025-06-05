from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class UserEvent(Base):
    __tablename__ = "user_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(String, nullable=False)  # view, cart_add, purchase, etc.
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    session_id = Column(String, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    metadata = Column(JSON)  # Additional event data
    
    # Relationships
    user = relationship("User")
    product = relationship("Product")