from fastapi import APIRouter, Depends, HTTPException,Body
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models.attendancemodel import Attendance
from app.models.usermodel import User
from app.schemas.attendenceschemas import AttendanceCreate, AttendanceOut,SuccessResponse,AttendanceActionUpdate
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
    print(getattr(request.state, "role", None))
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
       return JSONResponse(status_code=201, content={"success": False,  "message": "Attandance not found"})

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


@router.put("/update", response_model=SuccessResponse)
def update_attendance(
    request: Request,
    data: AttendanceActionUpdate,  # Note: Now getting emp_id from body
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    emp_id = data.emp_id
    if not emp_id:
        raise HTTPException(status_code=400, detail="Employee ID is required in the payload.")
    if getattr(request.state, "role", None) not in (1, 2):
        return JSONResponse(
            status_code=201,
            content={"success": False, "detail": "Only Admin can access data"}
        )
    today = datetime.utcnow().date()

    # Find today's attendance record
    attendance = db.query(Attendance).filter(
        Attendance.emp_id == emp_id,
        func.date(Attendance.check_in) == today
    ).first()

    if not attendance:
        return JSONResponse(
            status_code=201,
            content={"success": False, "message": "Attendance record not found for today"}
        )

    # Perform action based on is_reset or is_checkout
    if data.is_reset:
        attendance.check_out = None
        attendance.check_in = None
        attendance.status = "inactive"
        attendance.signout_by = None
    elif data.is_checkout:
        attendance.check_out = datetime.utcnow()
        attendance.status = "inactive"
        attendance.signout_by = emp_id
    else:
        raise HTTPException(status_code=400, detail="Either is_reset or is_checkout must be true.")

    attendance.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(attendance)

    return {
        "success": True,
        "status": 200,
        "message": "Updated successfully",
        "data": {
            "attendance_id": attendance.attendance_id,
            "action": "reset" if data.is_reset else "checkout"
        }
    }

@router.get("/today", response_model=SuccessResponse)
def get_today_attendance(
     request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    if getattr(request.state, "role", None) not in (1, 2,4):
        return JSONResponse(
            status_code=201,
            content={"success": False, "detail": "Only Admin can access data"}
        )
    today = datetime.utcnow().date()

    # Fetch all records where check_in is today
    attendances = db.query(Attendance).filter(
        func.date(Attendance.check_in) == today
    ).all()

    if not attendances:
        return JSONResponse(
            status_code=201,
            content={"success": False, "message": "No attendance records found for today"}
        )
    
    # Prepare list of attendance out
    attendance_list = [
        AttendanceOut(
            attendance_id=record.attendance_id,
            emp_id=record.emp_id,
            emp_name=record.emp_name,
            shift=record.shift,
            checkin_location=record.checkin_location,
            device_info=record.device_info,
            ip_address=record.ip_address,
            notes=record.notes,
            status=record.status,
            info=record.info,
            signout_by=record.signout_by,
            created_at=record.created_at,
            updated_at=record.updated_at,
            check_in=record.check_in,
            check_out=record.check_out
        )
        for record in attendances
    ]

    return {
        "success": True,
        "status": 200,
        "data": attendance_list
    }
