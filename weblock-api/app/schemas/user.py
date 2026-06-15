from pydantic import BaseModel
from pydantic import EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str