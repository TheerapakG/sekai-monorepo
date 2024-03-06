import enum
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import BigInteger


class ChannelIntentEnum(enum.Enum):
    ANNOUNCE = 1
    MUSIC_LEAK = 2
    VOCAL_LEAK = 3
    CARD_LEAK = 4


class Base(AsyncAttrs, DeclarativeBase):
    pass


class ChannelIntent(Base):
    __tablename__ = "channel_intent"

    guild: Mapped[int] = mapped_column(primary_key=True, type_=BigInteger)
    channel: Mapped[int] = mapped_column(primary_key=True, type_=BigInteger)
    intent: Mapped[ChannelIntentEnum]
