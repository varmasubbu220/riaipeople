from fastapi import APIRouter, Depends, HTTPException,Body
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models.attendancemodel import Attendance
from app.models.usermodel import User
from app.schemas.attendenceschemas import AttendanceCreate, AttendanceOut,SuccessResponse
from datetime import datetime
from fastapi import Request
from sqlalchemy import func
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
router = APIRouter(prefix="/attendance", tags=["Attendance"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
# Create Attendance
@router.post("/", response_model=AttendanceOut)
def create_attendance(request: Request, data: AttendanceCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    data_dict = data.dict()
    today = datetime.utcnow().date()

    emp_id = getattr(request.state, "emp_id", None)
    if not emp_id:
        raise HTTPException(status_code=400, detail="Employee ID not found in request state.")

    # Check if today's attendance already exists
    existing_attendance = db.query(Attendance).filter(
        Attendance.emp_id == emp_id,
        func.date(Attendance.check_in) == today
    ).first()
    if existing_attendance:
        # Always update if existing record found
        existing_attendance.status = "active"
        existing_attendance.signout_by = None
        existing_attendance.check_out = None
        existing_attendance.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(existing_attendance)
        return existing_attendance

    # New record logic
    if data_dict.get("signout_by") == 0:
        data_dict["signout_by"] = None

    attendance = Attendance(**data_dict, emp_id=emp_id, check_in=datetime.utcnow())
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance




# Get Attendance by ID
@router.get("/get", response_model=SuccessResponse)
def get_attendance( request: Request,token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Get today's date at the start of the day
    today = datetime.utcnow().date()
    emp_id = getattr(request.state, "emp_id", None)
    # Query for the attendance record for today and matching emp_id from the path parameter
    attendance = db.query(Attendance).filter(
        Attendance.emp_id == emp_id,
        func.date(Attendance.check_in) == today  # Filter for today's date
    ).first()

    if not attendance:
       return JSONResponse(status_code=201, content={"success": False,  "message": "not found"})

    # Map the Attendance model to AttendanceOut schema
    attendance_out = AttendanceOut(
        attendance_id=attendance.attendance_id,
        emp_id=attendance.emp_id,
        shift=attendance.shift,
        checkin_location=attendance.checkin_location,
        device_info=attendance.device_info,
        ip_address=attendance.ip_address,
        notes=attendance.notes,
        status=attendance.status,
        info=attendance.info,
        signout_by=attendance.signout_by,
        created_at=attendance.created_at,
        updated_at=attendance.updated_at,
        check_in=attendance.check_in,
        check_out=attendance.check_out
    )

    # Return a structured response with success and status
    return {
        "success": True,
        "status": 200,
        "data": attendance_out
    }

@router.get("/checkout", response_model=SuccessResponse)
def checkout_attendance(
    request: Request,
    token: str = Depends(oauth2_scheme),  
    db: Session = Depends(get_db)
):
    emp_id = getattr(request.state, "emp_id", None)
    print(emp_id,'emp')
    # Find the latest active attendance for the employee
    attendance = db.query(Attendance).filter(
        Attendance.emp_id == emp_id,
        Attendance.status == "active",
        Attendance.check_out == None  # Ensure not already signed out
    ).order_by(Attendance.check_in.desc()).first()

    if not attendance:
        return JSONResponse(
            status_code=201,
            content={"success": False, "message": "No active check-in found for this employee"}
        )

    # Update the attendance record
    attendance.check_out = datetime.utcnow()
    attendance.signout_by = emp_id
    attendance.status = "inactive"
    attendance.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(attendance)

    return {
        "success": True,
        "status": 200,
        "message": "Employee checked out successfully",
        "data": {
            "attendance_id": attendance.attendance_id,
            "check_out": attendance.check_out,
            "status": attendance.status
        }
    }
