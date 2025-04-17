from fastapi import FastAPI
from app.routes import users,onboarduser,auth,roles,attendence
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.authmiddleware import AuthMiddleware
load_dotenv()
app = FastAPI()
# CORS settings
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "DELETE"],
    allow_headers=[
        "Content-Type",
        "Access-Control-Allow-Headers",
        "Authorization",
        "X-Requested-With"],
)

app.add_middleware(AuthMiddleware)
app.include_router(onboarduser.router)
app.include_router(users.router) 
app.include_router(auth.router)
app.include_router(roles.router)
app.include_router(attendence.router)
@app.get("/")
def read_root():
    return {"message": "RIAI People Server is Running 🚀"}
