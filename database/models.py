from sqlalchemy import Column, Integer, String, Float
from database.config import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    department = Column(String)
    password = Column(String, nullable=False)

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String)
    login_count = Column(Integer)
    unique_pc_count = Column(Integer)
    is_weekend = Column(Integer)
    hour = Column(Integer)

    prediction = Column(Integer)
    risk_level = Column(String)
    confidence = Column(Float)

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True)
    name = Column(String)
    department = Column(String)
    designation = Column(String)
    email = Column(String, unique=True)