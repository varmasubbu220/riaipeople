from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Department Table
class Department(Base):
    __tablename__ = 'department'
    department_id = Column(BigInteger, primary_key=True, autoincrement=True)
    department_name = Column(String(100), nullable=False)

# Role Table
class Role(Base):
    __tablename__ = 'roles'
    role_id = Column(BigInteger, primary_key=True, autoincrement=True)
    role_name = Column(String(100), nullable=False)
   