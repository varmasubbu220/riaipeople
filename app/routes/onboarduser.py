from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.onboardusermodel import OnboardUser
from app.schemas.onboarduserschema import OnboardUserCreate, OnboardUserResponse, OnboardUserUpdate
from app.utils.database import get_db

router = APIRouter(prefix="/onboardusers", tags=["Onboard Users"])


# Create a new onboard user
@router.post("/", response_model=OnboardUserResponse)
def create_onboard_user(user: OnboardUserCreate, db: Session = Depends(get_db)):
    db_user = db.query(OnboardUser).filter(OnboardUser.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = OnboardUser(
        emp_name=user.emp_name,
        role_id=user.role_id,
        department_id =user.department_id,
        email=user.email,
        notes=user.notes,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


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
