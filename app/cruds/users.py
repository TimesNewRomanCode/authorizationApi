from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users import Users

class UsersCRUD:
    def __init__(self):
        pass

    async def create_users(self, users: Users, session: AsyncSession):
        session.add(users)
        await session.commit()
        await session.refresh(users)

    async def get_all_users(self, session: AsyncSession):
        result = await session.execute(select(Users))
        return result.scalars().all()

    async def get_users_by_id(self, sid, session: AsyncSession):
        result = await session.execute(select(Users).where(Users.sid == sid))
        return result.scalars().one()

    async def get_users_by_username(self, username, session: AsyncSession):
        result = await session.execute(select(Users).where(Users.username == username))
        return result.scalars().one()

    async def get_users_by_email(self, email: str, session: AsyncSession):
        result = await session.execute(select(Users).where(Users.email == email))
        return result.scalars().first()

    async def delete_users(self, sid, session: AsyncSession):
        result = await session.execute(delete(Users).where(Users.sid == sid))
        return result

