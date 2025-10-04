from asyncpg.pgproto.pgproto import timedelta
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.cruds.users import UsersCRUD
from app.models.users import Users
from app.schemas.auth import RegistrationScheme, LoginScheme
from app.utils.hashing import Hasher
from app.utils.security import create_access_token


class AuthService:
    def __init__(self):
        self.user_crud = UsersCRUD()

    async def registration(self, data: RegistrationScheme, session: AsyncSession):
        existing_player = await self.user_crud.get_users_by_email(data.email, session)
        if existing_player:
            return None

        new_player = Users(
            username=data.username,
            email=data.email,
            hashed_password=Hasher.get_password_hash(data.password),
        )

        return await self.user_crud.create_users(new_player, session)

    async def login(self, data: LoginScheme, session: AsyncSession):
        user = await self.user_crud.get_users_by_email(data.email, session)
        if not user:
            return None
        if not Hasher.verify_password(data.password, user.hashed_password):
            return None

        return user

    async def login_for_access_token(self, form_data: OAuth2PasswordRequestForm, session: AsyncSession):
        login_data = LoginScheme(email=form_data.username, password=form_data.password)
        user = await self.login(login_data, session)
        if not user:
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        access_token_expires = timedelta(milliseconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
