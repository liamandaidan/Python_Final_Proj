import uuid
from typing import Optional
from pydantic import BaseModel, Field

class User(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    first_name: str = Field(...)
    last_name: str = Field(...)
    username: str = Field(...)
    password: str = Field(...)
    role: Optional[str]
    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                #"_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "first_name": "Liam",
                "last_name": "McLaughlin",
                "username": "lm9",
                "password": "password"
            }
        }
class Basic_User(BaseModel):
    first_name: str = Field(...)
    last_name: str = Field(...)
    username: str = Field(...)
    role: str = Field(...)
    class Config:
            schema_extra = {
            "example": {
                "first_name": "Liam",
                "last_name": "McLaughlin",
                "username": "lm9",
            }
        }    
class UserAuth(BaseModel):
    username: str = Field(...)
    password: str = Field(...)
    
    class Config:
        schema_extra = {
            "example": {
                "username": "lm9",
                "password": "password"
            }
        }        

class Token(BaseModel):
    access_token: str
    token_type: str
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJsaWFtMSIsImV4cCI6MTY2NjkxNjMwNH0.PFM8BJwdRrx3bh5rCuJfqp4GW3p_VrJVrC1uFBlGu-E",
                "token_type": "bearer"
            }
        }

class TokenData(BaseModel):
    username: str | None = None
    
class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    password: Optional[str]
    
    class Config:
        schema_extra = {
            "example": {
                "first_name": "Liam",
                "last_name": "McLaughlin",
                "username": "liam9",
                "password": "password"
            }
        }
