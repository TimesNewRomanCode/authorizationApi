import uuid

from pydantic import BaseModel, Field

class RegistrationScheme(BaseModel):
    username: str = Field(
        ...,
        min_length=5,
        max_length=50,
        description="email address",
    )
    email: str = Field(
        ...,
        min_length=5,
        max_length=50,
        description="email address",
        pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password from 8 characters"
    )

class LoginScheme(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user_id: uuid.UUID
    email: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str
