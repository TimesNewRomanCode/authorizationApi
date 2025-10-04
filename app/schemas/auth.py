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

class SuccessResponse(BaseModel):
    message: str