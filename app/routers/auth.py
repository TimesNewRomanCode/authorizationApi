from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.schemas.auth import (
    RegistrationScheme,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/reregistration")
async def registration(
    data: RegistrationScheme,
    session: AsyncSession = Depends(get_session),
    service: AuthService = Depends(AuthService),
):
    return await service.registration(data, session)


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
    service: AuthService = Depends(AuthService),
):
    return await service.login_for_access_token(form_data, session)

