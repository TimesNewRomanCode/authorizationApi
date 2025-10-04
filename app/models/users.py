import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, func, Enum
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class Users(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_activated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_active: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
