from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.utils.database import Base
from app.models.onboardusermodel import OnboardUser,Role,Department
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(Integer, ForeignKey(OnboardUser.emp_id), nullable=False)
    department_id = Column(Integer, ForeignKey(Department.department_id), nullable=True)  # Fix here
    role_id = Column(Integer, ForeignKey(Role.role_id), nullable=True)  # Fix here
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    dob = Column(String, nullable=False)
    is_deleted = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    auth = Column(Boolean, default=False)
    otp = Column(String(10), nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    notes = Column(String, nullable=True)
    password = Column(String, nullable=False)
