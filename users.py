import uuid
from typing import Optional
from pydantic import BaseModel, Field

class User(BaseModel):
    """User model along with all enforced fields

    Args:
        BaseModel (_type_): https://pydantic-docs.helpmanual.io/usage/models/
    """
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    first_name: str = Field(...)
    last_name: str = Field(...)
    username: str = Field(...)
    password: str = Field(...)
    role: Optional[str]
    class Config:
        """Swagger config examples
        """
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "first_name": "Liam",
                "last_name": "McLaughlin",
                "username": "lm9",
                "password": "password"
            }
        }
class Basic_User(BaseModel):
    """Basic user model used with enforcement of fields not considered "valuable information"

    Args:
        BaseModel (_type_): https://pydantic-docs.helpmanual.io/usage/models/
    """
    first_name: str = Field(...)
    last_name: str = Field(...)
    username: str = Field(...)
    role: str = Field(...)
    class Config:
        """Swagger config examples
        """
        schema_extra = {
            "example": {
                "first_name": "Liam",
                "last_name": "McLaughlin",
                "username": "lm9",
            }
        }    
class UserAuth(BaseModel):
    """User login data enforcement

    Args:
        BaseModel (_type_): https://pydantic-docs.helpmanual.io/usage/models/
    """
    username: str = Field(...)
    password: str = Field(...)
    
    class Config:
        """Swagger docs
        """
        schema_extra = {
            "example": {
                "username": "lm9",
                "password": "password"
            }
        }        

class Token(BaseModel):
    """Access token used to enforce validation

    Args:
        BaseModel (_type_): https://pydantic-docs.helpmanual.io/usage/models/
    """
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
    """Used to enforce only username from token sub

    Args:
        BaseModel (_type_): https://pydantic-docs.helpmanual.io/usage/models/
    """
    username: str | None = None
    
class UserUpdate(BaseModel):
    """User can edit their own account changing the following fields

    Args:
        BaseModel (_type_): https://pydantic-docs.helpmanual.io/usage/models/
    """
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    password: Optional[str]
    
    class Config:
        """Swagger docs
        """
        schema_extra = {
            "example": {
                "first_name": "Liam",
                "last_name": "McLaughlin",
                "username": "liam9",
                "password": "password"
            }
        }
