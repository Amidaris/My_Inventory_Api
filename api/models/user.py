from pydantic import BaseModel, EmailStr, model_validator, StringConstraints
from fastapi import HTTPException
from typing import Annotated


class User(BaseModel):
    id: int
    username: str
    email: str | None = None
    full_name: str | None = None
    role: str | None = None
    disabled: bool | None = None

    model_config = { 
        "from_attributes": True # for ORM → Pydantic 
        }


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8)]
    confirm_password: str

    @model_validator(mode="after") # confirm password
    def passwords_match(self):
        if self.password != self.confirm_password: 
            raise HTTPException( 
                status_code=400, 
                detail="Passwords do not match" 
            )
        return self


class RegisterResponse(BaseModel):
    id: int
    email: EmailStr
    role: str

