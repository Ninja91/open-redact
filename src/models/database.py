from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime
import enum

Base = declarative_base()

class RequestStatus(enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    address_line_1 = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    country = Column(String, default="US")
    
    # Encrypted PII would go here in a production app
    extra_data = Column(JSON, default={}) 
    
    requests = relationship("RemovalRequest", back_populates="user")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class RemovalRequest(Base):
    __tablename__ = "removal_requests"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    broker_name = Column(String, nullable=False)
    status = Column(RequestStatus, default=RequestStatus.PENDING)
    external_id = Column(String) # ID provided by the broker if any
    logs = Column(JSON, default=[])
    
    user = relationship("User", back_populates="requests")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
