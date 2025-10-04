import uuid

from sqlalchemy import func
from sqlalchemy.dialects.postgresql.base import UUID
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)


class SidMixin:
    sid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, unique=True,
    nullable=False, )


class Base(DeclarativeBase, SidMixin):
    pass
