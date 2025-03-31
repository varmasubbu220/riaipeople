from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.rolemodel import Department, Role
from app.utils.database import get_db

router = APIRouter(prefix="/data", tags=["Departments and Roles"])

# Get all departments
@router.get("/departments")
def get_all_departments(db: Session = Depends(get_db)):
    return db.query(Department).all()

# Get all roles
@router.get("/roles")
def get_all_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()