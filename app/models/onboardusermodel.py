from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Department(Base):
    __tablename__ = "department"

    department_id = Column(Integer, primary_key=True, autoincrement=True)
    department_name = Column(String(100), nullable=False, unique=True)
    users = relationship("OnboardUser", back_populates="department")


class OnboardUser(Base):
    __tablename__ = "onboardusers"

    emp_id = Column(Integer, primary_key=True, index=True)
    emp_name = Column(String(50), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.role_id'), nullable=False)
    department_id = Column(Integer, ForeignKey('department.department_id'), nullable=False)
    notes = Column(Text, nullable=True)
    created_on = Column(TIMESTAMP, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    email = Column(String(255), nullable=False, unique=True)
    is_allowed = Column(Boolean, default=True)

    role = relationship("Role", back_populates="users")
    department = relationship("Department", back_populates="users")


class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(50), nullable=False, unique=True)
    users = relationship("OnboardUser", back_populates="role")
