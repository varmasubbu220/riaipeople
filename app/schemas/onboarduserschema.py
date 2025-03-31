from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Schema for creating a new onboard user
class OnboardUserCreate(BaseModel):
    emp_name: str
    role_id: int
    department_id: int
    email: EmailStr
    notes: Optional[str] = None

# Schema for response
class OnboardUserResponse(BaseModel):
    emp_id: int
    emp_name: str
    role_id: int
    department_id: int
    email: EmailStr
    notes: Optional[str] = None
    created_on: datetime
    is_deleted: bool
    is_allowed: bool

    class Config:
        from_attributes = True  # Allows ORM serialization

# Schema for updating an onboard user
class OnboardUserUpdate(BaseModel):
    emp_name: Optional[str] = None
    role_id: Optional[int] = None
    department_id: Optional[int] = None
    email: Optional[EmailStr] = None
    notes: Optional[str] = None
    is_deleted: Optional[bool] = None
    is_allowed: Optional[bool] = None
