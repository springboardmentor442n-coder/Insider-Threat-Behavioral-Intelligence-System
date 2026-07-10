from backend.security import hash_password, verify_password, create_access_token
from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.models import User

def create_user(db: Session,username: str,email: str,department: str,password: str):

    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )
    print("Password:", password)
    print("Type:", type(password))
    user = User(
        username=username,
        email=email,
        department=department,
        password=hash_password(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def get_users(db: Session):
    return db.query(User).all()

def get_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

def update_user(db: Session, user_id: int, username: str, email: str, department: str):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.username = username
    user.email = email
    user.department = department

    db.commit()
    db.refresh(user)

    return user

def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}

def login_user(db: Session, username: str, password: str):

    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(
        {"sub": user.username}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }