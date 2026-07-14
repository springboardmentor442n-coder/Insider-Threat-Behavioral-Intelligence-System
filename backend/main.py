from fastapi import Depends
from sqlalchemy.orm import Session
from routes.prediction import router as prediction_router

from config import get_db
from crud import (
    create_user,
    get_users,
    get_user,
    update_user,
    delete_user,
    login_user
)
from schemas import UserCreate, UserLogin
from fastapi import FastAPI
from config import engine, Base
from routes import auth
from models import Prediction
from sqlalchemy.orm import Session
from routes.employee import router as employee_router
from routes.dashboard import router as dashboard_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(prediction_router)
app.include_router(employee_router)
app.include_router(dashboard_router)
Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    try:
        connection = engine.connect()
        connection.close()
        return {
            "message": "Hello Sristi! Backend is running.",
            "database": "Connected successfully!"
        }
    except Exception as e:
        return {
            "message": "Backend is running.",
            "database": str(e)
        }

@app.post("/users")
def add_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = create_user(
        db,
        user.username,
        user.email,
        user.department,
        user.password
    )

    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "department": new_user.department
    }

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    return login_user(
        db,
        user.username,
        user.password
    )
    
@app.get("/users")
def read_users(db: Session = Depends(get_db)):
    return get_users(db)
@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    return get_user(db, user_id)
@app.put("/users/{user_id}")
def edit_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    updated_user = update_user(
        db,
        user_id,
        user.username,
        user.email,
        user.department
    )

    if not updated_user:
        return {"message": "User not found"}

    return updated_user
@app.delete("/users/{user_id}")
def remove_user(user_id: int, db: Session = Depends(get_db)):
    deleted_user = delete_user(db, user_id)

    if not deleted_user:
        return {"message": "User not found"}

    return {"message": "User deleted successfully"}
    
@app.get("/predictions")
def read_predictions(db: Session = Depends(get_db)):
    return db.query(Prediction).all()