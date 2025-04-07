from fastapi import APIRouter, Depends, HTTPException,status,Request
from sqlalchemy.orm import Session
from app.models.usermodel import User
from app.models.onboardusermodel import OnboardUser
from app.schemas.userschema import UserCreate, UserResponse, UserUpdate
from app.utils.database import get_db
from app.utils.auth import hash_password,generate_verification_token,SECRET_KEY,ALGORITHM,create_access_token,create_refresh_token
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
import anyio
import random
import jwt
from fastapi.encoders import jsonable_encoder
from app.utils.email import send_email
router = APIRouter(prefix="/users", tags=["Users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Create a new user
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        onboarded_user = db.query(OnboardUser).filter(OnboardUser.email == user.email).first()
        if not onboarded_user:
            return JSONResponse(
                status_code=201,
                content={"success": False, "message": "User not onboarded"},
            )

        db_user = db.query(User).filter(User.email == user.email).first()

        if db_user:
            if db_user.is_verified:
                return JSONResponse(
                    status_code=201,
                    content={"success": False, "message": "Email already registered, try login"},
                )
            else:
                # Update existing user's details
                db_user.first_name = user.first_name
                db_user.last_name = user.last_name
                # db_user.dob = user.dob
                db_user.notes = user.notes
                db_user.password = hash_password(user.password)  # Update password
                db_user.department_id = onboarded_user.department_id
                db_user.role_id = onboarded_user.role_id

                db.commit()
                db.refresh(db_user)

                # Resend verification email
                token = generate_verification_token(user.email)
                verification_link = f"https://yourdomain.com/verify?token={token}"
                anyio.from_thread.run(
                    send_email,
                    user.email,
                    "✅ RIAI Solution – Verify Your Email",
                    f"Click the link below to verify your email and complete signup:\n\n{verification_link}",
                    f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <h2 style="color: #2C3E50;">✅ Verify Your Email</h2>
    <p>Dear User,</p>
    <p>Welcome to <b>RIAI Solution</b>! Please verify your email by clicking the link below:</p>

    <p style="text-align: center;">
      <a href="{verification_link}" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a>
    </p>

    <p>If you didn’t request this, please ignore this email.</p>

    <p>Best Regards,</p>
    <p><b>RIAI Solution Team</b></p>

    <hr>
    <p style="font-size: 12px; color: #7F8C8D;">This is an automated message. Please do not reply to this email.</p>
  </body>
</html>
                    """
                )
                return JSONResponse(
                    status_code=201,
                    content={"success": True, "message": " Verification email sent"},
                )

        # Create a new user if not found
        hashed_pwd = hash_password(user.password)
        new_user = User(
            emp_id=onboarded_user.emp_id,
            first_name=user.first_name,
            last_name=user.last_name,
            # dob=user.dob,
            email=user.email,
            notes=user.notes,
            password=hashed_pwd,
            department_id=onboarded_user.department_id,
            role_id=onboarded_user.role_id,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Send verification email
        token = generate_verification_token(user.email)
        verification_link = f"https://yourdomain.com/verify?token={token}"
        anyio.from_thread.run(
            send_email,
            user.email,
            "✅ RIAI Solution – Verify Your Email",
            f"Click the link below to verify your email and complete signup:\n\n{verification_link}",
            f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <h2 style="color: #2C3E50;">✅ Verify Your Email</h2>
    <p>Dear User,</p>
    <p>Welcome to <b>RIAI Solution</b>! Please verify your email by clicking the link below:</p>

    <p style="text-align: center;">
      <a href="{verification_link}" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a>
    </p>

    <p>If you didn’t request this, please ignore this email.</p>

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
                "message": "User created successfully. Verification email sent.",
                "data": {
                    "emp_id": new_user.emp_id,
                    "first_name": new_user.first_name,
                    "last_name": new_user.last_name,
                    # "dob": str(new_user.dob),
                    "email": new_user.email,
                    "notes": new_user.notes,
                    "department_id": new_user.department_id,
                    "role_id": new_user.role_id,
                },
            },
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Internal server error", "error": str(e)},
        )


@router.get("/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload["email"]

        user = db.query(User).filter(User.email == email).first()
        if not user:
              return JSONResponse(status_code=201,content={"success": False, "message":"Invalid token or user not found"},)

        if user.is_verified:
            return JSONResponse(
                status_code=200,
                content={"success": True, "message": "Email already verified"},
            )

        user.is_verified = True
        db.commit()
        
        access_token = create_access_token({"sub": user.email})
        refresh_token = create_refresh_token({"sub": user.email})
        return JSONResponse(
            status_code=200,
            content={"success": True,"access_token":access_token,"refresh_token":refresh_token, "message": "Email verified successfully"},
        )

    except jwt.ExpiredSignatureError:
        return JSONResponse(status_code=201,content={"success": False, "message":"Verification link expired"},)
 

    except jwt.InvalidTokenError:
        return JSONResponse(status_code=201,content={"success": False, "message":"Invalidtoken"},)

# Get all users (excluding soft deleted)
@router.get("/", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return db.query(User).filter(User.is_deleted == False).all()



@router.get("/config", response_model=UserResponse)
def get_user_config(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token: email missing")

        user = db.query(User).filter(User.email == email, User.is_deleted == False).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return UserResponse(**jsonable_encoder(user))  # ✅ Convert ORM to dict then Pydantic model

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Get a specific user by ID
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = db.query(User).filter(User.user_id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
# Update a user
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = db.query(User).filter(User.user_id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user

# Delete a user (soft delete)
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = db.query(User).filter(User.user_id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_deleted = True
    db.commit()
    return {"message": "User deleted successfully"}
