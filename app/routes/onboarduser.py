from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.onboardusermodel import OnboardUser
from app.schemas.onboarduserschema import OnboardUserCreate, OnboardUserResponse, OnboardUserUpdate
from app.utils.database import get_db
from fastapi.responses import JSONResponse
import anyio
from fastapi import Request
from app.utils.email import send_email
router = APIRouter(prefix="/onboardusers", tags=["Onboard Users"])


# Create a new onboard user
@router.post("/", response_model=OnboardUserResponse)
def create_onboard_user(user: OnboardUserCreate, request: Request, db: Session = Depends(get_db)):
    try:
        # Check if the email already exists
        if getattr(request.state, "role", None) != 1:
            
            return JSONResponse(status_code=201, content={"success": False, "detail": "Only Admin can onboard"})

        db_user = db.query(OnboardUser).filter(OnboardUser.email == user.email).first()
        if db_user:
            return JSONResponse(status_code=201, content={"success": False, "detail": "Email already exists"})

        # Create a new user
        new_user = OnboardUser(
            emp_name=user.emp_name,
            role_id=user.role_id,
            department_id=user.department_id,
            email=user.email,
            notes=user.notes,
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        anyio.from_thread.run(
            send_email,
            user.email,
            "🎉 Welcome to RIAI Solution – You’re Successfully Onboarded!",
            "Greetings from RIAI Solution! Your onboarding was successful, and you can now sign up for the RIAI People App.",
            """
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <h2 style="color: #2C3E50;">🎉 Greetings from RIAI Solution! 🎉</h2>
    <p>Dear User,</p>
    <p>We are thrilled to welcome you to the <b>RIAI Solution family</b>! 🎊</p>

    <p>Your onboarding was successful, and you can now <b>sign up for the RIAI People App</b> to start your journey with us. 🚀  
       Experience our innovative platform designed to make your interactions seamless and efficient.</p>

    <h3 style="color: #16A085;">What’s Next?</h3>
    <ul>
      <li>Complete your signup by clicking the button below.</li>
      <li>Fill in your details to personalize your experience.</li>
      <li>Explore our platform and discover all its powerful features.</li>
    </ul>

    <p style="text-align: center;">
      <a href="https://localhost:3000/signup" 
         style="background-color: #2980B9; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px; font-size: 16px;">
        🔹 Sign Up Now
      </a>
    </p>

    <p>Should you have any questions, feel free to reach out to our support team. We’re here to assist you every step of the way.</p>

    <p>Welcome aboard, and let's create something amazing together! 🚀</p>

    <p>Best Regards,</p>
    <p><b>RIAI Solution Team</b></p>

    <hr>
    <p style="font-size: 12px; color: #7F8C8D;">This is an automated message. Please do not reply to this email.</p>
  </body>
</html>

            """
        )
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "User onboarded successfully",
                
            }
        )

    except HTTPException as e:
        raise e  # Re-raise HTTP exceptions for proper handling

    except Exception as e:
        db.rollback()  # Rollback in case of unexpected errors
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")



# Get all onboard users
@router.get("/", response_model=list[OnboardUserResponse])
def get_all_onboard_users(db: Session = Depends(get_db)):
    return db.query(OnboardUser).all()


# Get a specific onboard user by ID
@router.get("/{emp_id}", response_model=OnboardUserResponse)
def get_onboard_user(emp_id: int, db: Session = Depends(get_db)):
    user = db.query(OnboardUser).filter(OnboardUser.emp_id == emp_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Onboard user not found")
    return user


# Update an onboard user
@router.put("/{emp_id}", response_model=OnboardUserResponse)
def update_onboard_user(emp_id: int, user_update: OnboardUserUpdate, db: Session = Depends(get_db)):
    user = db.query(OnboardUser).filter(OnboardUser.emp_id == emp_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Onboard user not found")

    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


# Delete an onboard user (soft delete)
@router.delete("/{emp_id}")
def delete_onboard_user(emp_id: int, db: Session = Depends(get_db)):
    user = db.query(OnboardUser).filter(OnboardUser.emp_id == emp_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Onboard user not found")

    user.is_deleted = True  # Soft delete by setting is_deleted to True
    db.commit()
    return {"message": "Onboard user deleted successfully"}
