from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.usermodel import User
from app.schemas.userschema import UserCreate, UserResponse, UserUpdate
from app.utils.database import get_db
from app.utils.auth import hash_password
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/users", tags=["Users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Create a new user
@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash_password(user.password)
    new_user = User(
        emp_id=user.emp_id,
        first_name=user.first_name,
        last_name=user.last_name,
        dob=user.dob,
        email=user.email,
        notes=user.notes,
        password=hashed_pwd,
        department_id=user.department_id,
        role_id=user.role_id,        
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

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