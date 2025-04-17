from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
from typing import Any
class AttendanceCreate(BaseModel):
    emp_id: int
    shift: Optional[str] = "General"
    checkin_location: str
    device_info: Optional[str] = None
    ip_address: str
    notes: Optional[str] = None
    status: Optional[str] = "active"
    info: Optional[Dict] = None
    signout_by: Optional[int] = None


class AttendanceOut(AttendanceCreate):
    attendance_id: int
    created_at: datetime
    updated_at: datetime
    check_in: Optional[datetime]
    check_out: Optional[datetime]

    class Config:
        orm_mode = True  # This ensures SQLAlchemy models are handled correctly
        from_attributes = True  # This is necessary for using from_orm
        json_encoders = {
            datetime: lambda v: v.isoformat()  # Ensures datetime fields are serialized correctly to ISO 8601 format
        }
class SuccessResponse(BaseModel):
    success: bool  # Indicates if the request was successful
    status: int     # HTTP status code (200, 404, etc.)
    data: Any 