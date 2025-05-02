from pydantic import BaseModel
from enum import Enum

class RoleEnum(str, Enum):
    admin = "admin"
    employe = "employe"
    visiteur = "visiteur"

class UserCreate(BaseModel):
    email: str
    password: str
    role: RoleEnum = RoleEnum.visiteur
    username: str  

class UserResponse(BaseModel):
    id: int
    email: str
    role: RoleEnum

    class Config:
        from_attributes = True  

class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str