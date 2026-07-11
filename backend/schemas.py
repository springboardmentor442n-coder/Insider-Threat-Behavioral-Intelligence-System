from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    department: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

from pydantic import BaseModel

class PredictionRequest(BaseModel):
    login_count: int
    unique_pc_count: int
    is_weekend: int
    hour: int


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class EmployeeCreate(BaseModel):
    employee_id: str
    name: str
    department: str
    designation: str
    email: str