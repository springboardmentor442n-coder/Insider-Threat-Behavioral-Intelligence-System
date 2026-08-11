from pydantic import BaseModel


class UserRegister(BaseModel):
    username: str
    password: str
    role: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    username: str
    role: str


class TokenData(BaseModel):
    username: str | None = None
