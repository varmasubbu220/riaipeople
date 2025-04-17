from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Enum, JSON, Text, ForeignKey
from sqlalchemy.sql import func
from app.utils.database import Base
from app.models.usermodel import User
from sqlalchemy.orm import relationship

class Attendance(Base):
    __tablename__ = "attendance"

    attendance_id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(BigInteger, ForeignKey(User.emp_id), nullable=False)
    shift = Column(String(50), default='General')
    check_in = Column(DateTime, nullable=False)
    check_out = Column(DateTime, nullable=True)
    checkin_location = Column(String(100), nullable=False)
    device_info = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(Enum('active', 'inactive', name='status_enum'), default='active')
    info = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # New column: signout_by (foreign key to User.emp_id)
    signout_by = Column(BigInteger, ForeignKey(User.emp_id), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[emp_id], backref="attendances")
    signout_user = relationship("User", foreign_keys=[signout_by], backref="signout_attendances")
