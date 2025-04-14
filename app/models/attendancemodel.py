from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Enum, JSON, Text,ForeignKey
from sqlalchemy.sql import func
from app.utils.database import Base
from app.models.usermodel import User
from sqlalchemy.orm import relationship
class Attendance(Base):
    __tablename__ = "attendance"

    attendance_id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(BigInteger, ForeignKey(User.emp_id), nullable=False)  # Foreign key to the users table
    shift = Column(String(50), default='General')  # Default value is 'General'
    check_in = Column(DateTime, nullable=False)  # check_in is required
    check_out = Column(DateTime, nullable=True)  # Optional, can be NULL
    checkin_location = Column(String(100), nullable=False)  # checkin_location is required
    device_info = Column(String(255), nullable=True)  # Optional, can be NULL
    ip_address = Column(String(45), nullable=False)  # ip_address is required
    notes = Column(Text, nullable=True)  # Optional, can be NULL
    status = Column(Enum('active', 'inactive', name='status_enum'), default='active')  # Default value is 'active'
    info = Column(JSON, nullable=True)  # JSON column for additional information
    created_at = Column(DateTime, default=func.current_timestamp())  # Default timestamp
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())  # Updated timestamp

    # Foreign key relationship to OnboardUser (if needed)
    Users = relationship("Users", back_populates="attendances") 
