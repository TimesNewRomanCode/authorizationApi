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


    async def get_users_by_email(self, email: str, session: AsyncSession):
        result = await session.execute(select(Users).where(Users.email == email))
        return result.scalars().first()

