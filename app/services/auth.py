from datetime import timedelta
from fastapi import HTTPException, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.config import settings
from app.core.redis import get_redis
from app.cruds.users import UsersCRUD
from app.models.users import Users
from app.schemas.auth import RegistrationScheme, LoginScheme
from app.utils.hashing import Hasher
from app.utils.security import create_access_token, create_refresh_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class AuthService:
    def __init__(self):
        self.user_crud = UsersCRUD()
        self.oauth2_scheme = oauth2_scheme

    async def _store_tokens_in_redis(self, user_sid: str, access_token: str, refresh_token: str):
        redis_client = await get_redis()

        await redis_client.setex(
            f"access_token:{user_sid}",
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            access_token
        )

        await redis_client.setex(
            f"refresh_token:{user_sid}",
            timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            refresh_token
        )

    async def _is_token_valid(self, user_sid: str, token_type: str) -> bool:
        redis_client = await get_redis()
        stored_token = await redis_client.get(f"{token_type}_token:{user_sid}")
        return stored_token is not None

    async def _revoke_tokens(self, user_sid: str):
        redis_client = await get_redis()
        await redis_client.delete(f"access_token:{user_sid}")
        await redis_client.delete(f"refresh_token:{user_sid}")

    async def registration(self, data: RegistrationScheme, session: AsyncSession):
        existing_player = await self.user_crud.get_users_by_email(data.email, session)
        if existing_player:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists"
            )

        new_player = Users(
            username=data.username,
            email=data.email,
            hashed_password=Hasher.get_password_hash(data.password),
        )

        user = await self.user_crud.create_users(new_player, session)

        return {"message": "User registered successfully"}

    async def login(self, data: LoginScheme, session: AsyncSession):
        user = await self.user_crud.get_users_by_email(data.email, session)
        if not user:
            return None
        if not Hasher.verify_password(data.password, user.hashed_password):
            return None
        return user

    async def login_for_access_token(
            self,
            form_data: OAuth2PasswordRequestForm,
            session: AsyncSession,
            response: Response = None
    ):
        login_data = LoginScheme(email=form_data.username, password=form_data.password)
        user = await self.login(login_data, session)

        if not user:
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": str(user.sid)}
        )

        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = create_refresh_token(
            data={"sub": user.email, "user_id": str(user.sid)}
        )

        await self._store_tokens_in_redis(str(user.sid), access_token, refresh_token)

        if response:
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=False,
                samesite="lax",
                max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                path="/"

            )

            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=False,
                samesite="lax",
                max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
                path="/"
            )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": str(user.sid),
            "email": user.email
        }

    async def refresh_access_token(
            self,
            refresh_token: str,
            response: Response,
            session: AsyncSession
    ):
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Refresh token required")

        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            email: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            token_type: str = payload.get("type")

            if not email or not user_id or token_type != "refresh":
                raise HTTPException(status_code=401, detail="Invalid refresh token")

            if not await self._is_token_valid(user_id, "refresh"):
                raise HTTPException(status_code=401, detail="Refresh token revoked")

            user = await self.user_crud.get_users_by_email(email, session)
            if not user:
                raise HTTPException(status_code=401, detail="User not found")

            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            new_access_token = create_access_token(
                data={"sub": user.email, "user_id": str(user.sid)}
            )

            redis_client = await get_redis()
            await redis_client.setex(
                f"access_token:{user.sid}",
                timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
                new_access_token
            )

            # Обновляем cookie
            response.set_cookie(
                key="access_token",
                value=new_access_token,
                httponly=True,
                secure=False,
                samesite="lax",
                max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )

            return {
                "access_token": new_access_token,
                "token_type": "bearer"
            }

        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    async def logout(self, user_sid: uuid.UUID, response: Response):
        await self._revoke_tokens(str(user_sid))

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return {"message": "Successfully logged out"}

    async def get_current_user_from_token(
            self,
            token: str = Depends(oauth2_scheme),
            session: AsyncSession = None
    ):
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
        )

        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            email: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            token_type: str = payload.get("type")

            if not email or not user_id or token_type != "access":
                raise credentials_exception

            if not await self._is_token_valid(user_id, "access"):
                raise credentials_exception

        except JWTError:
            raise credentials_exception

        user = await self.user_crud.get_users_by_email(email, session)
        if user is None:
            raise credentials_exception

        return user