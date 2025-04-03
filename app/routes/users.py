from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from app.models.usermodel import User
from app.models.onboardusermodel import OnboardUser
from app.schemas.userschema import UserCreate, UserResponse, UserUpdate
from app.utils.database import get_db
from app.utils.auth import hash_password
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/users", tags=["Users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Create a new user
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.email == user.email).first()
        onboarded_user = db.query(OnboardUser).filter(OnboardUser.email == user.email).first()
        if not onboarded_user:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "User not onboarded"},
            )
       
        if db_user:
            return JSONResponse(
                status_code=201,
                content={"success": False, "message": "Email already registered"},
            )

        hashed_pwd = hash_password(user.password)
        new_user = User(
            emp_id=onboarded_user.emp_id,
            first_name=user.first_name,
            last_name=user.last_name,
            dob=user.dob,
            email=user.email,
            notes=user.notes,
            password=hashed_pwd,
            department_id=onboarded_user.department_id,
            role_id=onboarded_user.role_id,        
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "message": "User created successfully",
                "data": {
                   
                    "emp_id": new_user.emp_id,
                    "first_name": new_user.first_name,
                    "last_name": new_user.last_name,
                    "dob": str(new_user.dob),
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

# Get all users (excluding soft deleted)
@router.get("/", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return db.query(User).filter(User.is_deleted == False).all()

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