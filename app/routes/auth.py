from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.utils.auth import create_access_token, create_refresh_token, verify_password,verify_token, hash_password
from app.utils.database import get_db
from app.models.usermodel import User
from fastapi.responses import JSONResponse
from app.schemas.userschema import LoginSchema,Authschema
import anyio
from app.utils.email import send_email
router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/login")
def log(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        return JSONResponse(status_code=201, content={"success": False, "auth": 0, "message": "Invalid credentials"})

    if not user.is_verified:
        return JSONResponse(status_code=201, content={"success": False, "auth": 1, "message": "User is not verified"})

    token_data = {"sub": user.email, "role": user.role_id,'emp_id':user.emp_id}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "success": True,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
@router.post("/logins", status_code=status.HTTP_200_OK)
def login(payload: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    
    if not user or not verify_password(payload.password, user.password):
        return JSONResponse(status_code=201, content={"success": False, "auth": 0, "message": "Invalid credentials"})

    if not user.is_verified:
        return JSONResponse(status_code=201, content={"success": False, "auth": 1, "message": "User is not verified"})
    token_data = {"sub": user.email, "role": user.role_id}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "success": True,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/validate")
def validate_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not verified")

    user_data = user.__dict__.copy()
    user_data.pop("password", None)

    return user_data

@router.post("/refresh")
def refresh_token(refresh_token: str):
    payload = verify_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    new_access_token = create_access_token({"sub": payload["sub"]})
    return {"access_token": new_access_token, "token_type": "bearer"}
