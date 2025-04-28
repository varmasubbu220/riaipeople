from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.rolemodel import Department, Role
from app.utils.database import get_db
from fastapi.security import OAuth2PasswordBearer
router = APIRouter(prefix="/data", tags=["Departments and Roles"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # you
# Get all departments
@router.get("/departments")
def get_all_departments(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    return db.query(Department).all()

# Get all roles
@router.get("/roles")
def get_all_roles(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    return db.query(Role).all()