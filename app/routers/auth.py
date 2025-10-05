from fastapi import APIRouter, Depends, Response, Cookie, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import RegistrationScheme, TokenResponse, RefreshTokenResponse
from app.services.auth import AuthService, oauth2_scheme

router = APIRouter(prefix="/auth", tags=["auth"])

auth_service = AuthService()


@router.post("/registration")
async def registration(data: RegistrationScheme):
    from app.core.database import get_session
    async for session in get_session():
        return await auth_service.registration(data, session)


@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        response: Response = Response(),
):
    from app.core.database import get_session
    async for session in get_session():
        result = await auth_service.login_for_access_token(form_data, session, response)
        return result


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(response: Response, refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token required")

    from app.core.database import get_session
    async for session in get_session():
        return await auth_service.refresh_access_token(refresh_token, response, session)

@router.post("/logout")
async def logout(response: Response, request: Request):
    from app.core.database import get_session

    # Получаем токен из cookies
    access_token = request.cookies.get("access_token")

    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    async for session in get_session():
        try:
            current_user = await auth_service.get_current_user_from_token(access_token, session)
            return await auth_service.logout(current_user.sid, response)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/me")
async def get_current_user(request: Request):
    from app.core.database import get_session

    access_token = request.cookies.get("access_token")

    if not access_token:
        try:
            access_token = await oauth2_scheme(request)
        except:
            raise HTTPException(status_code=401, detail="Not authenticated")

    async for session in get_session():
        current_user = await auth_service.get_current_user_from_token(access_token, session)
        return {
            "sid": current_user.sid,
            "username": current_user.username,
            "email": current_user.email
        }